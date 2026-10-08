"""Real SDK proof, not PPO: parameter write, selected reset and CUDA disk state."""
from pathlib import Path
import tempfile,torch
from gas_damping_factor import GasDamping
from gas_damping_sdk_adapter import tensor

def equal_state(a,b):
    if torch.is_tensor(a):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal_state(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal_state(x,y) for x,y in zip(a,b))
    return a==b

class ActualGasDampingProof:
    def __init__(self,env):
        self.env=env;self.adapter=env._gas_damping;self.controls=0
        self.contact_start=env._integrated_contact.tick
        self.initial=self.assignment();self.parent_reset=None;self.isolated_reset=None;self.roundtrip=None
    def assignment(self):
        c=self.adapter.component
        return dict(factor=c.factor.detach().cpu().tolist(),episode=c.episode.detach().cpu().tolist(),
                    actual_damping_Ns_m=c.actual_damping_Ns_per_m().detach().cpu().tolist())
    def before_selected_reset(self,ids):
        c=self.adapter.component;self.before=dict(factor=c.factor.clone(),episode=c.episode.clone(),
            damping=tensor(self.adapter.robot.root_view.get_dof_dampings()).clone(),tick=self.env.common_step_counter)
    def after_selected_reset(self,ids):
        e=self.env;c=self.adapter.component;other=torch.tensor([0,2,3,5,6,8,9],device=e.device)
        assert torch.equal(c.factor[other],self.before['factor'][other])
        assert torch.equal(c.episode[other],self.before['episode'][other])
        assert torch.equal(c.episode[ids],self.before['episode'][ids]+1)
        actual=tensor(self.adapter.robot.root_view.get_dof_dampings())
        assert torch.equal(actual[other],self.before['damping'][other])
        assert e.common_step_counter==self.before['tick'];self.adapter.audit_parameters()
        self.parent_reset=dict(ids=ids.detach().cpu().tolist(),only_selected_D6_rows_changed=True,
            selected_episode_incremented_once=True,global_control_tick_unchanged=True,actual_three_views_exact=True)
    def after_control(self):
        self.controls+=1;e=self.env;a=self.adapter;r=a.robot
        if self.controls==120:
            ids=torch.tensor([1,4,7],device=e.device);other=torch.tensor([0,2,3,5,6,8,9],device=e.device)
            prior=a.state_dict();spring=e._spring_pressure.component.state_dict()
            cpu=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state_all()
            q=tensor(r.data.joint_pos).clone();qd=tensor(r.data.joint_vel).clone()
            tick=e.common_step_counter;contact=e._integrated_contact.tick
            a.reset(ids);now=a.state_dict()
            assert torch.equal(now['factor'][other],prior['factor'][other])
            assert torch.equal(now['episode'][ids],prior['episode'][ids]+1)
            assert torch.equal(now['episode'][other],prior['episode'][other])
            assert equal_state(spring,e._spring_pressure.component.state_dict())
            assert torch.equal(q,tensor(r.data.joint_pos)) and torch.equal(qd,tensor(r.data.joint_vel))
            assert torch.equal(cpu,torch.get_rng_state()) and equal_state(cuda,torch.cuda.get_rng_state_all())
            assert tick==e.common_step_counter and contact==e._integrated_contact.tick
            a.audit_parameters();e._mild_dr.audit();e._spring_pressure.audit()
            self.isolated_reset=dict(ids=[1,4,7],independent_D6_only_selected_reset=True,
                D5_state_and_joint_state_global_CPU_CUDA_RNG_control_physics_clocks_unchanged=True)
        if self.controls==150:
            state=a.state_dict();q=tensor(r.data.joint_pos).clone();qd=tensor(r.data.joint_vel).clone()
            cpu=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state_all();tick=e.common_step_counter
            before=e.observation_manager.compute()['policy'].clone()
            with tempfile.TemporaryDirectory(prefix='mod4_d6_cuda_sdk_') as temp:
                file=Path(temp)/'actual_cuda_state.pt';torch.save(state,file)
                loaded=torch.load(file,map_location='cpu',weights_only=False)
                a.load_state_dict(loaded)
            assert equal_state(a.state_dict(),state)
            x=GasDamping(e.num_envs,e.device,1,a.component.enabled);y=GasDamping(e.num_envs,e.device,2,a.component.enabled)
            x.load_state_dict(loaded);y.load_state_dict(state);ids=torch.tensor([1,4,7],device=e.device)
            x.reset(ids);y.reset(ids);assert equal_state(x.state_dict(),y.state_dict())
            assert torch.equal(q,tensor(r.data.joint_pos)) and torch.equal(qd,tensor(r.data.joint_vel))
            assert torch.equal(cpu,torch.get_rng_state()) and equal_state(cuda,torch.cuda.get_rng_state_all())
            assert tick==e.common_step_counter and torch.equal(before,e.observation_manager.compute()['policy'])
            a.audit_parameters();e._mild_dr.audit();e._spring_pressure.audit()
            self.roundtrip=dict(actual_CUDA_factor_episode_both_private_RNG_disk_roundtrip_exact=True,
                subsequent_selected_private_draw_exact=True,same_tick_actor_joint_state_global_RNG_exact=True,
                actual_damping_three_views_restored_exact=True,not_PhysX_exact_resume=True)
    def finish(self):
        assert self.controls==300 and self.parent_reset and self.isolated_reset and self.roundtrip
        count=self.env._integrated_contact.tick-self.contact_start;assert count==1200
        return dict(controls=self.controls,actual_contact_callbacks=count,
            action_group_callbacks=dict(self.env._physics_action_delay.calls),initial_assignment=self.initial,
            final_assignment=self.assignment(),selected_parent_reset=self.parent_reset,
            isolated_D6_reset=self.isolated_reset,CUDA_disk_roundtrip=self.roundtrip,
            actual_audit=self.adapter.audit(),recipe=self.env.gas_damping_recipe(),
            inherited_D5_damping_unchanged_recipe_is_superseded_by_D6=True,
            learning_optimizer_updates=0,SDK_contract_only_not_skill_graduation=True)
