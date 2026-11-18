"""Success-gated E1 mixture of true zeroDR and the unchanged full SCUT ranges."""
from collections import deque
import math,torch
from .scut_flat_env import tensor

FRACTIONS=(0.,0.,.1,.25,.5,.75,1.)
class E1DRMixture:
    def __init__(self,env):
        self.env=env;dr=env.full_dr;self.target_stage=0
        self.original_nominal=env.reference_nominal_env_mask.clone()
        self.raw={name:getattr(dr,name).clone()for name in ['body_mass_scale','total_mass_scale','startup_com_delta','startup_materials','startup_joint_friction']}
        self.nominal_friction=dr.startup_joint_friction.clone()
        ids=env.continuous_stair_mask.nonzero().flatten()
        self.nominal_friction[ids,:,0]=dr.static_friction_default[ids]
        self.nominal_friction[ids,:,1]=(dr.dynamic_friction_default if dr.dynamic_friction_default is not None else dr.static_friction_default)[ids]
        self.nominal_friction[ids,:,2]=0. if dr.viscous_friction_default is None else dr.viscous_friction_default[ids]
        self.stage=torch.full((env.num_envs,),-1,dtype=torch.long,device=env.device)
        self.actual_full_dr=torch.zeros(env.num_envs,dtype=torch.bool,device=env.device)
        selected=(env.continuous_stair_mask&(~self.original_nominal)).nonzero().flatten()
        gen=torch.Generator(device=env.device).manual_seed(int(env.cfg.seed)+3701)
        order=selected[torch.randperm(len(selected),device=env.device,generator=gen)]
        self.rank=torch.full((env.num_envs,),len(selected)+1,dtype=torch.long,device=env.device);self.rank[order]=torch.arange(len(order),device=env.device)
        self.full_count=len(selected)
        self.attempts=torch.zeros(7,2,5,dtype=torch.long,device=env.device)
        self.completions=torch.zeros_like(self.attempts)
        self.recent=[deque(maxlen=128 if i==0 else 256)for i in range(7)]
        self.promotions=[]
    def finish(self,ids):
        e=self.env
        if not e.course_accounting or e.snapshots is None:return
        ids=ids[e.continuous_stair_mask[ids]&(e.episode_length_buf[ids]>0)]
        if not len(ids):return
        ok=e.course_success[ids]&(~e.reset_terminated[ids])
        for env_id,success in zip(ids.tolist(),ok.tolist()):
            stage=int(self.stage[env_id]);group=int(self.actual_full_dr[env_id]);offset=int(e.actual_start_offset_index[env_id])
            if stage<0:continue
            self.attempts[stage,group,offset]+=1;self.completions[stage,group,offset]+=int(success)
            if stage<2 or group==1:self.recent[stage].append(int(success))
        stage=self.target_stage
        if stage>=len(FRACTIONS)-1:return
        recent=self.recent[stage]
        if stage==0:ready=len(recent)>=128 and sum(recent)/len(recent)>=.7 and int(self.completions[0].sum())>=64
        elif stage==1:ready=len(recent)>=256 and sum(recent)/len(recent)>=.7 and bool((self.completions[1].sum(0)>=16).all())
        else:ready=len(recent)>=128 and sum(recent)/len(recent)>=.6 and int(self.completions[stage,1].sum())>=32 and bool((self.completions[stage,1]>=3).all())
        if ready:
            self.target_stage+=1;self.promotions.append(dict(global_policy_step=int(e._sim_step_counter)//8,from_stage=stage,to_stage=self.target_stage,actual_completion_count=int(self.completions[stage].sum()),recent_success_rate=sum(recent)/len(recent)))
    def prepare(self,ids):
        e=self.env;dr=e.full_dr;ids=ids[e.continuous_stair_mask[ids]]
        if not len(ids):return
        stage=self.target_stage;self.stage[ids]=stage
        new_full=(~self.original_nominal[ids])&(self.rank[ids]<math.ceil(FRACTIONS[stage]*self.full_count))
        activated=ids[new_full&(~self.actual_full_dr[ids])]
        self.actual_full_dr[ids]=new_full;dr.nominal_env_mask[ids]=~new_full
        e.actual_start_offset_index[ids]=torch.where(self.stage[ids]==0,torch.full_like(self.stage[ids],2),e.start_offset_index[ids])
        full=ids[new_full];zero=ids[~new_full]
        for name in ['body_mass_scale','total_mass_scale']:
            getattr(dr,name)[full]=self.raw[name][full];getattr(dr,name)[zero]=1.
        dr.startup_com_delta[full]=self.raw['startup_com_delta'][full];dr.startup_com_delta[zero]=0.
        dr.startup_materials[full.cpu()]=self.raw['startup_materials'][full.cpu()];dr.startup_materials[zero.cpu()]=dr.materials[zero.cpu()]
        dr.startup_joint_friction[full]=self.raw['startup_joint_friction'][full];dr.startup_joint_friction[zero]=self.nominal_friction[zero]
        fr=dr.startup_joint_friction
        e.robot.write_joint_friction_coefficient_to_sim(joint_friction_coeff=fr[ids,:,0],joint_dynamic_friction_coeff=fr[ids,:,1],joint_viscous_friction_coeff=fr[ids,:,2],joint_ids=dr.joint_ids,env_ids=ids)
        dr._write_body_mass_inertia(ids);dr._write_startup_materials(ids)
        if len(activated):dr.gain_count[activated]=0;dr.effort_sample_count[activated]=0
    def summary(self):
        e=self.env;mask=e.continuous_stair_mask
        return dict(method='success-gated mixture fraction; enabled DR always uses original full ranges',target_stage=self.target_stage,fullDR_fraction_of_reference_DR_group=FRACTIONS[self.target_stage],stage_population=torch.bincount(self.stage[mask].clamp_min(0),minlength=7).tolist(),actual_fullDR_population=int(self.actual_full_dr[mask].sum()),zeroDR_population=int((~self.actual_full_dr[mask]).sum()),attempts_stage_actualDR_offset=self.attempts.tolist(),completions_stage_actualDR_offset=self.completions.tolist(),offsets_mm=[-60,-30,0,30,60],recent_success_rates=[sum(q)/len(q)if q else None for q in self.recent],promotions=self.promotions,zeroDR_results_are_not_fullDR_graduation=True)
    def checkpoint(self):
        return dict(target_stage=self.target_stage,stage=self.stage.clone(),actual_full_dr=self.actual_full_dr.clone(),rank=self.rank.clone(),raw=self.raw,nominal_friction=self.nominal_friction,attempts=self.attempts.clone(),completions=self.completions.clone(),recent=[list(q)for q in self.recent],promotions=self.promotions)
