"""Low-speed one-step course. Collision bank is built once; each env moves on reset."""
import math,torch
from .legacy_continuous_stair_env import _OriginalContinuousStairEnv
from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env
from .stair_training_repair import ContinuousStairRepairMixin,wheel_center_ground
from .scut_flat_env import tensor
from .single_step_math import SPEC,COURSE,advance,supported_upper,stable_completion,first_landings
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.math_ops import euler_xyz_from_quat,wrap_to_pi

class ContinuousStairEnv(ContinuousStairRepairMixin,_OriginalContinuousStairEnv):
    # User2026-11-09/10:2mm is diagnostic only; inherited >1m catastrophe reset remains.
    enforce_closure_reset=False
    def __init__(self,cfg,meta,bank):
        self._course_ready=False
        super().__init__(cfg,meta,bank)
        n=self.num_envs;dev=self.device
        self.course_mastered=torch.zeros(n,dtype=torch.long,device=dev)
        self.course_level=torch.zeros_like(self.course_mastered)
        self.course_fail_streak=torch.zeros_like(self.course_mastered)
        self.course_attempts=torch.zeros(2,len(SPEC.heights),dtype=torch.long,device=dev)
        self.course_successes=torch.zeros_like(self.course_attempts)
        self.course_promotions=torch.zeros_like(self.course_attempts)
        self.course_demotions=torch.zeros_like(self.course_attempts)
        self.course_speed_rejections=torch.zeros_like(self.course_attempts)
        self.course_failure_causes=torch.zeros(2,len(SPEC.heights),3,dtype=torch.long,device=dev)
        self.course_entry_speed=torch.zeros(n,device=dev)
        self.course_speed_max=torch.zeros_like(self.course_entry_speed)
        self.course_hold=torch.zeros_like(self.course_entry_speed)
        self.course_lift_best=torch.zeros(n,2,device=dev)
        self.course_lift_reference=torch.zeros_like(self.course_lift_best)
        self.course_landed=torch.zeros(n,2,dtype=torch.bool,device=dev)
        self.course_lift_armed=torch.zeros(n,dtype=torch.bool,device=dev)
        self.course_entry_seen=torch.zeros(n,dtype=torch.bool,device=dev)
        self.course_success=torch.zeros_like(self.course_entry_seen)
        self.course_progress=torch.zeros(n,device=dev)
        self.course_event_reward=torch.zeros(n,device=dev)
        self.course_reward_sums=torch.zeros(4,device=dev)
        self.course_accounting=False;self.course_evaluation=False
        self._course_ready=True

    def _set_origins(self,ids):
        ScutUnifiedRoughV1Env._set_origins(self,ids)
        special=getattr(self.terrain,'r1_continuous_stair_mask',None)
        if special is not None:
            selected=ids[special[ids]]
            # The bank's origin is the lower ground, while its center ray hits the top.
            lower=self.terrain.terrain_origins[self.terrain.terrain_levels[selected],self.terrain.terrain_types[selected],2]
            self.terrain.env_origins[selected,2]=lower
            self.scene.env_origins[selected,2]=lower

    def _course_scatter(self,buffer,ids,values):
        if ids.numel():
            index=self.full_dr.nominal_env_mask[ids].long()*len(SPEC.heights)+self.course_level[ids]
            buffer.view(-1).scatter_add_(0,index,values.long())

    def _finish_course_episodes(self,ids):
        if not self.course_accounting or self.snapshots is None:return
        picked=ids[self.continuous_stair_mask[ids]&(self.episode_length_buf[ids]>0)]
        if not picked.numel():return
        ok=self.course_success[picked]&(~self.reset_terminated[picked])
        attempted=torch.ones_like(ok)
        new,streak,up,down=advance(self.course_mastered[picked],self.course_level[picked],self.course_fail_streak[picked],ok,attempted)
        self._course_scatter(self.course_attempts,picked,attempted)
        self._course_scatter(self.course_successes,picked,ok)
        self._course_scatter(self.course_speed_rejections,picked,self.course_entry_seen[picked]&((self.course_entry_speed[picked]>SPEC.maximum_speed)|(self.course_speed_max[picked]>SPEC.maximum_speed)))
        if not self.course_evaluation:
            self._course_scatter(self.course_promotions,picked,up)
            self._course_scatter(self.course_demotions,picked,down)
            self.course_mastered[picked]=new;self.course_fail_streak[picked]=streak
        group=self.full_dr.nominal_env_mask[picked].long();level=self.course_level[picked]
        for k,mask in enumerate((self.reset_terminated[picked],~self.course_landed[picked].all(1),self.course_landed[picked].all(1)&~ok)):
            self.course_failure_causes[:,:,k].index_put_((group,level),mask.long(),accumulate=True)

    def _reset_idx(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        ready=getattr(self,'_course_ready',False)
        if ready:
            self._finish_course_episodes(ids)
            picked=ids[self.continuous_stair_mask[ids]]
            if not self.course_evaluation:
                level=self.course_mastered[picked].clone()
                review=(level>0)&(torch.rand(len(picked),device=self.device,generator=self.reset_generator)<SPEC.review_fraction)
                level[review]=(torch.rand(int(review.sum()),device=self.device,generator=self.reset_generator)*level[review]).long()
                self.course_level[picked]=level
            self.terrain.terrain_levels[picked]=self.course_level[picked]
        # Keep the native full-DR/rough/air reset implementation and bypass the old 200mm reset.
        ScutUnifiedRoughV1Env._reset_idx(self,ids)
        if not ready:return
        self._flat_preservation_commands(ids)
        for cause in ('contact','orientation','other'):
            for suffix in ('_counter','_raw_buf'):
                value=getattr(self.reward,'_stair_'+cause+suffix,None)
                if value is not None:value[ids]=0
        for name in ('_stair_guide_allowed','_stair_contact_raw','_stair_suppressed_guide_raw'):
            value=getattr(self.reward,name,None)
            if value is not None:value[ids]=False
        for buf in (self.course_entry_seen,self.course_success,self.course_landed,self.course_lift_armed):buf[ids]=False
        for buf in (self.course_entry_speed,self.course_speed_max,self.course_hold,self.course_lift_best,self.course_progress,self.course_event_reward):buf[ids]=0
        picked=ids[self.continuous_stair_mask[ids]]
        self.stair_up[ids]=False;self.stair_mid[ids]=False;self.stair_goal_hold[ids]=0.;self.stair_stage[ids]=0
        if not picked.numel():return
        n=len(picked);gen=self.reset_generator;center=self._center()[picked]
        choices=((self._bank_h>=.24)&(self._bank_h<=.272)).nonzero().flatten()
        sample=choices[torch.randint(len(choices),(n,),device=self.device,generator=gen)]
        q=self._bank_q[sample][:,self._bank_ids].clone();root=tensor(self.robot.data.default_root_state)[picked].clone()
        side=torch.where(torch.rand(n,device=self.device,generator=gen)<.5,-1.,1.)
        distance=torch.empty(n,device=self.device).uniform_(SPEC.edge+.65,SPEC.edge+1.05,generator=gen)
        root[:,:3]=center;root[:,0]+=side*distance;root[:,1]+=torch.empty(n,device=self.device).uniform_(-.15,.15,generator=gen)
        root[:,2]+=self._bank_h[sample]+.01
        yaw=torch.where(side<0,0.,math.pi);root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw);root[:,7:]=0.
        self.robot.write_root_state_to_sim(root,env_ids=picked);self.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=picked)
        self.stair_up[picked]=True;self.stair_side[picked]=side;self.stair_start[picked]=distance
        h=self.command.new_tensor(SPEC.heights)[self.course_level[picked]]
        self.stair_height[picked]=(.28+.4*h).clamp_max(.38)
        self.stair_speed[picked]=torch.empty(n,device=self.device).uniform_(.3,.5,generator=gen)
        self.height[picked]=.28;self.command[picked]=0.;self.heading_env[picked]=False;self.standing_env[picked]=True
        self.actions[picked]=0.;self.torque[picked]=0.;self.zero_torque_remaining[picked]=0;self._ground_command_until[picked]=0;self.r2_air_reset[picked]=False
        self.course_lift_reference[picked]=.25
        self.reward.ground_z_est[picked]=center[:,2];self.reward._invalidate_step_caches()
        self._course_commands()

    def _sample_command(self,ids):
        ScutUnifiedRoughV1Env._sample_command(self,ids)
        if getattr(self,'_course_ready',False):
            self._flat_preservation_commands(ids);self._course_commands()

    def _course_commands(self):
        if not getattr(self,'_course_ready',False):return
        picked=self.continuous_stair_mask.nonzero().flatten()
        age=self.episode_length_buf[picked]*self.step_dt
        self.height[picked]=torch.minimum(self.stair_height[picked],.28+.06*age)
        self.command[picked]=0.;self.command[picked,0]=torch.where(age>=SPEC.settle_seconds,self.stair_speed[picked],0.)
        self.command_timer[picked]=1e9;self.heading_env[picked]=False;self.standing_env[picked]=age<SPEC.settle_seconds
        self._ground_original_command[picked]=self.command[picked];self._ground_original_heading[picked]=False
        self.reward.command[picked]=self.command[picked];self.reward.height_cmd[picked]=self.height[picked];self.reward._invalidate_step_caches()

    def _get_observations(self):
        self._course_commands()
        return ScutUnifiedRoughV1Env._get_observations(self)

    def _pre_physics_step(self,actions):
        self._course_commands()
        ScutUnifiedRoughV1Env._pre_physics_step(self,actions)
        self._course_commands()

    def prepare_endpoint(self):
        ScutUnifiedRoughV1Env.prepare_endpoint(self)
        if not getattr(self,'_course_ready',False):return
        r=self.reward;wheels=self.view.data.body_pos_w[:,self.stair_wheel_idx]
        ground=torch.stack([wheel_center_ground(tensor(self.scene[name].data.ray_hits_w),wheels[:,side,:2],r.ground_wheels[:,side])for side,name in enumerate(('ground_left','ground_right'))],1)
        mask=self.continuous_stair_mask
        self.stair_original_root_ground=r.ground_z_est.clone();self.stair_wheel_ground=ground
        r.ground_z_est=torch.where(mask,ground.amin(1),r.ground_z_est)
        r.ground_wheels=torch.where(mask[:,None],ground,r.ground_wheels);r._invalidate_step_caches()
        x=(wheels[:,:,0]-self._center()[:,None,0])*self.stair_side[:,None]
        r._stair_course_mask=mask
        r._stair_guide_allowed=mask&(~self.course_success)&((x-SPEC.edge).abs().amin(1)<.45)

    def _update_course_events(self,term):
        self.course_event_reward.zero_()
        center=self._center();d=self.view.data;wheel=d.body_pos_w[:,self.stair_wheel_idx]
        forces=tensor(self.scene['contacts'].data.net_forces_w)[:,self.wheel_sensor_ids]
        x=(wheel[:,:,0]-center[:,None,0])*self.stair_side[:,None];y=wheel[:,:,1]-center[:,None,1];z=wheel[:,:,2]-center[:,None,2]
        h=self.command.new_tensor(SPEC.heights)[self.course_level]
        active=self.continuous_stair_mask&(~term)&(self.episode_length_buf*self.step_dt>=SPEC.settle_seconds)
        near=(x-SPEC.edge).abs().amin(1)<.45
        speed=tensor(self.robot.data.root_lin_vel_w)[:,:2].norm(dim=-1)
        entering=active&(~self.course_entry_seen)&(x.amin(1)<SPEC.edge+.20)
        self.course_entry_speed[entering]=speed[entering];self.course_entry_seen|=entering
        self.course_speed_max=torch.where(active&(near|self.course_entry_seen),torch.maximum(self.course_speed_max,speed),self.course_speed_max)
        upper=supported_upper(x,y,z,forces[:,:,2],h)
        gained,self.course_landed=first_landings(self.course_landed,upper,active)
        body_x=(d.root_pos_w[:,0]-center[:,0])*self.stair_side
        roll,pitch,_=euler_xyz_from_quat(self.robot.data.root_quat_w)
        stable=stable_completion(upper,body_x,wrap_to_pi(pitch),wrap_to_pi(roll),d.root_ang_vel_b[:,:2].norm(dim=-1),tensor(self.robot.data.root_lin_vel_w)[:,2],self.course_entry_speed,self.course_speed_max,self.course_entry_seen,term|self.reward._stair_contact_raw,active)
        self.course_hold=torch.where(stable,self.course_hold+self.step_dt,torch.zeros_like(self.course_hold))
        completed=(self.course_hold>=SPEC.hold_seconds-1e-7)&(~self.course_success)
        self.course_success|=completed;self.stair_goal_hold.copy_(self.course_hold)
        # Credit increases only, near the real edge with measured support and actual wheel lift.
        supported=(forces[:,:,2]>SPEC.support_force).any(1)
        interaction=active&near&supported
        arm=interaction&(~self.course_lift_armed)
        self.course_lift_reference[arm]=self.reward.length[arm];self.course_lift_armed|=arm
        lift=((z-SPEC.radius)/h[:,None]).clamp(0,1)
        retract=((self.course_lift_reference-self.reward.length)/.08).clamp(0,1)
        score=lift*retract
        lift_gain=(score-self.course_lift_best).clamp_min(0).mean(1)*interaction
        self.course_lift_best=torch.where(interaction[:,None],torch.maximum(self.course_lift_best,score),self.course_lift_best)
        progress=(self.stair_start-body_x).clamp(0,1.5)
        advance=(progress-self.course_progress).clamp(0,.02)*interaction
        self.course_progress=torch.where(interaction,torch.maximum(self.course_progress,progress),self.course_progress)
        parts=torch.stack((.25*lift_gain,.15*advance,.2*gained.sum(1),2.*completed.float()),1)
        self.course_event_reward.copy_(parts.sum(1));self.course_reward_sums+=parts.sum(0)
        self.stair_stage=torch.where(self.course_landed.all(1),1,0)

    def _get_dones(self):
        term,timeout=ScutUnifiedRoughV1Env._get_dones(self)
        if getattr(self,'_course_ready',False):
            self._update_course_events(term)
            timeout|=self.course_success&(~term)
        return term,timeout

    def _get_rewards(self):
        base=ScutUnifiedRoughV1Env._get_rewards(self)
        return base+self.course_event_reward if getattr(self,'_course_ready',False)else base

    def terrain_summary(self):
        out=ScutUnifiedRoughV1Env.terrain_summary(self)
        if not getattr(self,'_course_ready',False):return out
        mask=self.continuous_stair_mask
        out['course_groups']=dict(continuous_stairs=int(mask.sum()),retained_rough=int(self.terrain.r1_retained_rough_mask.sum()),flat=int(self.flat_terrain_mask.sum()))
        out['single_step_curriculum']=dict(course=COURSE,heights_m=list(SPEC.heights),mastered_population=torch.bincount(self.course_mastered[mask],minlength=9).tolist(),episode_population=torch.bincount(self.course_level[mask],minlength=9).tolist(),attempts_DR_then_nominal=self.course_attempts.tolist(),successes_DR_then_nominal=self.course_successes.tolist(),promotions_DR_then_nominal=self.course_promotions.tolist(),demotions_DR_then_nominal=self.course_demotions.tolist(),entry_speed_rejections_DR_then_nominal=self.course_speed_rejections.tolist(),failure_causes=self.course_failure_causes.tolist(),failure_columns=['terminated','both_wheels_never_landed','landing_without_qualified_hold'],reward_sums=self.course_reward_sums.tolist(),reward_columns=['incremental_supported_lift','incremental_edge_progress','each_wheel_first_landing','qualified_stable_completion'],review_fraction=SPEC.review_fraction,failures_before_demotion=SPEC.failures_to_demote,maximum_actual_entry_speed=SPEC.maximum_speed,hold_s=SPEC.hold_seconds,per_env_reset_only=True,evaluation_only=self.course_evaluation,scope='stochastic training episode totals; not a frozen evaluation')
        return out

    def terrain_checkpoint_state(self):
        state=ScutUnifiedRoughV1Env.terrain_checkpoint_state(self)
        state.update(course=COURSE,heights_m=SPEC.heights)
        for name in ('course_mastered','course_level','course_fail_streak','course_attempts','course_successes','course_promotions','course_demotions','course_speed_rejections','course_failure_causes','course_reward_sums'):
            state[name]=getattr(self,name).clone()
        return state

    def restore_terrain_curriculum(self,state):
        same=state.get('course')==COURSE
        self.course_accounting=False
        if same:
            assert tuple(state['heights_m'])==SPEC.heights
            for name in ('course_mastered','course_level','course_fail_streak','course_attempts','course_successes','course_promotions','course_demotions','course_speed_rejections','course_failure_causes','course_reward_sums'):
                target=getattr(self,name);value=state[name].to(target)
                if value.shape!=target.shape:raise ValueError('Course resume shape differs: '+name)
                target.copy_(value)
        self.parent_terrain_state=state;self.snapshots=None;self.reset()
        return dict(new_course=not same,course=COURSE,counters_restored=same,old_terrain_not_relabelled=True,fresh_physical_episodes=True)

    def begin_training_counts(self):
        self.course_accounting=True
