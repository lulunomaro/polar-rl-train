"""Real chassis-only COM setter/cache/reset/CUDA-state proof; no PPO."""
from pathlib import Path
import tempfile,torch
from chassis_com_component import ChassisCOM
from chassis_com_pose_roundtrip_sdk_adapter import verify_rotation_preserved
from gas_damping_sdk_adapter import tensor
from chassis_pd_nominal_readback import quat_rotate_xyzw
def equal(a,b):
    if torch.is_tensor(a):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b
class ActualChassisCOMProof:
    def __init__(self,env):
        self.env=env;self.adapter=env._chassis_com;self.controls=0;self.contact_start=env._integrated_contact.tick
        self.initial=self.assignment();self.parent_reset=None;self.isolated=None;self.roundtrip=None
        self.mass_weighted_formula_max_error=0.;self.world_frame_max_error=0.
    def assignment(self):
        c=self.adapter.component;return dict(delta_m=c.delta_m.cpu().tolist(),episode=c.episode.cpu().tolist())
    def snapshot(self):
        a=self.adapter;r=a.robot;e=self.env
        return dict(state=a.state_dict(),local=tensor(r.root_view.get_coms()).clone().to(e.device),
                    mass=tensor(r.root_view.get_masses()).clone().to(e.device),inertia=tensor(r.root_view.get_inertias()).clone().to(e.device),
                    q=tensor(r.data.joint_pos).clone(),qd=tensor(r.data.joint_vel).clone(),
                    tick=e.common_step_counter,contact=e._integrated_contact.tick)
    def before_selected_reset(self,ids):self.before=self.snapshot()
    def after_selected_reset(self,ids):
        e=self.env;a=self.adapter;c=a.component;other=torch.tensor([0,2,3,5,6,8,9],device=e.device)
        assert torch.equal(c.episode[ids],self.before['state']['episode'][ids]+1)
        assert torch.equal(c.episode[other],self.before['state']['episode'][other])
        assert torch.equal(c.delta_m[other],self.before['state']['delta_m'][other])
        now=tensor(a.robot.root_view.get_coms()).to(e.device)
        assert torch.equal(now[other],self.before['local'][other])
        assert e.common_step_counter==self.before['tick'] and e._integrated_contact.tick==self.before['contact']
        a.audit_parameters();e._mild_dr.audit()
        self.parent_reset=dict(ids=[1,4,7],selected_episode_once=True,other_COM_rows_and_private_state_exact=True,
                               D0_selected_mass_inertia_orientation_changes_are_separately_audited=True,global_control_physics_tick_unchanged=True)
    def whole_COM(self):
        r=self.adapter.robot;pos=tensor(r.data.body_com_pos_w).double();mass=tensor(r.root_view.get_masses()).to(pos.device).double()
        return (pos*mass[...,None]).sum(1)/mass.sum(1)[:,None]
    def frame_audit(self):
        r=self.adapter.robot;local=tensor(r.root_view.get_coms()).to(self.env.device)
        link=tensor(r.data.body_link_pose_w)
        predicted=link[...,:3].double()+quat_rotate_xyzw(link[...,3:].double(),local[...,:3].double())
        error=float((predicted-tensor(r.data.body_com_pos_w).double()).abs().max())
        assert error<1e-5,error;self.world_frame_max_error=max(self.world_frame_max_error,error)
    def after_control(self):
        self.controls+=1;e=self.env;a=self.adapter;r=a.robot
        self.frame_audit()
        if self.controls==120:
            ids=torch.tensor([1,4,7],device=e.device);other=torch.tensor([0,2,3,5,6,8,9],device=e.device)
            before=self.snapshot();whole=self.whole_COM().clone();link=tensor(r.data.body_link_pose_w).clone()
            old_groups=dict(spring=e._spring_pressure.state_dict(),gas=e._gas_damping.state_dict())
            cpu=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state_all()
            a.reset(ids);after=self.snapshot()
            for key in ('mass','inertia','q','qd'):assert torch.equal(before[key],after[key]),key
            assert before['tick']==after['tick'] and before['contact']==after['contact']
            assert equal(old_groups,dict(spring=e._spring_pressure.state_dict(),gas=e._gas_damping.state_dict()))
            assert torch.equal(cpu,torch.get_rng_state()) and equal(cuda,torch.cuda.get_rng_state_all())
            rotations=verify_rotation_preserved(before['local'][...,3:],after['local'][...,3:])
            assert torch.equal(after['local'][other],before['local'][other])
            assert torch.equal(link,tensor(r.data.body_link_pose_w))
            delta=a.component.delta_m-before['state']['delta_m'];mass=after['mass'].double()
            predicted=quat_rotate_xyzw(link[:,a.body_id,3:].double(),delta.double())*(mass[:,a.body_id]/mass.sum(1))[:,None]
            error=float((self.whole_COM()-whole-predicted).abs().max());assert error<1e-5,error
            self.mass_weighted_formula_max_error=error;a.audit_parameters();e._mild_dr.audit()
            self.isolated=dict(selected_ids=[1,4,7],only_chassis_translation_changes=True,current_all_body_quaternions_exact=rotations['raw_quaternion_bytes_exact'],physical_rotations_preserved_float32_roundtrip=rotations,
                               mass_inertia_joint_state_D5_D6_and_global_RNG_unchanged=True,
                               global_control_physics_ticks_unchanged=True,whole_robot_COM_mass_weighted_formula_max_error_m=error)
        if self.controls==150:
            state=a.state_dict();before=self.snapshot();actor=e.observation_manager.compute()['policy'].clone()
            cpu=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state_all()
            with tempfile.TemporaryDirectory(prefix='mod4_d7_com_cuda_sdk_') as temp:
                path=Path(temp)/'actual_cuda_state.pt';torch.save(state,path);loaded=torch.load(path,map_location='cpu',weights_only=False);a.load_state_dict(loaded)
            assert equal(a.state_dict(),state)
            x=ChassisCOM(e.num_envs,e.device,1,a.component.enabled);y=ChassisCOM(e.num_envs,e.device,2,a.component.enabled)
            x.load_state_dict(loaded);y.load_state_dict(state);ids=torch.tensor([1,4,7],device=e.device);x.reset(ids);y.reset(ids);assert equal(x.state_dict(),y.state_dict())
            after=self.snapshot()
            for key in ('mass','inertia','q','qd'):assert torch.equal(before[key],after[key]),key
            assert torch.equal(before['local'][...,:3],after['local'][...,:3])
            rotations=verify_rotation_preserved(before['local'][...,3:],after['local'][...,3:])
            assert before['tick']==after['tick'] and before['contact']==after['contact']
            assert torch.equal(cpu,torch.get_rng_state()) and equal(cuda,torch.cuda.get_rng_state_all())
            assert torch.equal(actor,e.observation_manager.compute()['policy']);a.audit_parameters();e._mild_dr.audit()
            self.roundtrip=dict(actual_CUDA_delta_episode_three_private_RNG_disk_roundtrip_exact=True,
                                subsequent_selected_private_draw_exact=True,same_tick_actor_COM_translation_joint_state_exact=True,physical_rotations_preserved_float32_roundtrip=rotations,
                                global_CPU_CUDA_RNG_control_physics_tick_unchanged=True,not_PhysX_exact_resume=True)
    def finish(self):
        assert self.controls==300 and self.parent_reset and self.isolated and self.roundtrip
        count=self.env._integrated_contact.tick-self.contact_start;assert count==1200
        return dict(controls=300,actual_contact_callbacks=count,action_group_callbacks=dict(self.env._physics_action_delay.calls),
                    initial_assignment=self.initial,final_assignment=self.assignment(),selected_parent_reset=self.parent_reset,
                    isolated_COM_reset=self.isolated,CUDA_disk_roundtrip=self.roundtrip,actual_audit=self.adapter.audit(),
                    recipe=self.env.chassis_com_recipe(),world_COM_frame_formula_max_error_m=self.world_frame_max_error,
                    learning_optimizer_updates=0,SDK_only_not_skill_or_hardware_graduation=True)
