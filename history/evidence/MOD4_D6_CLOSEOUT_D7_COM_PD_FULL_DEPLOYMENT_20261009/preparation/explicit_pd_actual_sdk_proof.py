"""Real explicit motor coefficients, reset and private CUDA state; no learning."""
from pathlib import Path
import tempfile,torch
from explicit_pd_component import ExplicitPD
from gas_damping_sdk_adapter import tensor
def equal(a,b):
    if torch.is_tensor(a):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b
class ActualExplicitPDProof:
    def __init__(self,env):
        self.env=env;self.adapter=env._explicit_pd;self.controls=0;self.contact_start=env._integrated_contact.tick
        self.initial=self.assignment();self.parent_reset=None;self.isolated=None;self.roundtrip=None
    def assignment(self):
        c=self.adapter.component
        return dict(factors={k:v.cpu().tolist() for k,v in c.factor.items()},episode=c.episode.cpu().tolist())
    def snapshot(self):
        e=self.env;r=self.adapter.robot
        return dict(state=self.adapter.state_dict(),mass=tensor(r.root_view.get_masses()).clone(),inertia=tensor(r.root_view.get_inertias()).clone(),
                    com=tensor(r.root_view.get_coms()).clone(),drive_k=tensor(r.root_view.get_dof_stiffnesses()).clone(),drive_d=tensor(r.root_view.get_dof_dampings()).clone(),
                    q=tensor(r.data.joint_pos).clone(),qd=tensor(r.data.joint_vel).clone(),tick=e.common_step_counter,contact=e._integrated_contact.tick,
                    spring=e._spring_pressure.state_dict(),gas=e._gas_damping.state_dict())
    def before_selected_reset(self,ids):self.before=self.snapshot()
    def after_selected_reset(self,ids):
        e=self.env;a=self.adapter;c=a.component;other=torch.tensor([0,2,3,5,6,8,9],device=e.device)
        assert torch.equal(c.episode[ids],self.before['state']['episode'][ids]+1)
        assert torch.equal(c.episode[other],self.before['state']['episode'][other])
        assert all(torch.equal(v[other],self.before['state']['factor'][k][other]) for k,v in c.factor.items())
        assert e.common_step_counter==self.before['tick'] and e._integrated_contact.tick==self.before['contact']
        a.audit_parameters();e._mild_dr.audit()
        self.parent_reset=dict(ids=[1,4,7],selected_episode_once=True,other_PD_rows_exact=True,global_control_physical_ticks_unchanged=True)
    def after_control(self):
        self.controls+=1;e=self.env;a=self.adapter;c=a.component
        a.audit_parameters()
        if self.controls==120:
            before=self.snapshot();cpu=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state_all();ids=torch.tensor([1,4,7],device=e.device);other=torch.tensor([0,2,3,5,6,8,9],device=e.device)
            a.reset(ids);after=self.snapshot()
            for k in ('mass','inertia','com','drive_k','drive_d','q','qd','spring','gas'):assert equal(before[k],after[k]),k
            assert before['tick']==after['tick'] and before['contact']==after['contact']
            assert all(torch.equal(v[other],before['state']['factor'][k][other]) for k,v in c.factor.items())
            assert torch.equal(cpu,torch.get_rng_state()) and equal(cuda,torch.cuda.get_rng_state_all());e._mild_dr.audit()
            self.isolated=dict(selected_ids=[1,4,7],only_explicit_motor_coefficient_group_changes=True,mass_inertia_COM_implicit_drives_joint_state_spring_gas_exact=True,
                               output_gain_and_hardware_envelope_unchanged=True,global_CPU_CUDA_RNG_control_physical_ticks_exact=True)
        if self.controls==150:
            state=a.state_dict();before=self.snapshot();actor=e.observation_manager.compute()['policy'].clone();cpu=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state_all()
            with tempfile.TemporaryDirectory(prefix='mod4_d7_pd_cuda_') as temp:
                path=Path(temp)/'state.pt';torch.save(state,path);loaded=torch.load(path,map_location='cpu',weights_only=False);a.load_state_dict(loaded)
            assert equal(a.state_dict(),state)
            x=ExplicitPD(e.num_envs,e.device,1,c.enabled);y=ExplicitPD(e.num_envs,e.device,2,c.enabled);x.load_state_dict(loaded);y.load_state_dict(state)
            ids=torch.tensor([1,4,7],device=e.device);x.reset(ids);y.reset(ids);assert equal(x.state_dict(),y.state_dict())
            after=self.snapshot()
            for k in ('mass','inertia','com','drive_k','drive_d','q','qd','spring','gas'):assert equal(before[k],after[k]),k
            assert before['tick']==after['tick'] and before['contact']==after['contact']
            assert torch.equal(cpu,torch.get_rng_state()) and equal(cuda,torch.cuda.get_rng_state_all());assert torch.equal(actor,e.observation_manager.compute()['policy']);e._mild_dr.audit()
            self.roundtrip=dict(actual_CUDA_factor_episode_three_private_RNG_disk_roundtrip_exact=True,next_selected_private_draw_exact=True,
                                same_tick_actor_joint_state_model_coefficients_exact=True,global_CPU_CUDA_RNG_and_ticks_exact=True,not_PhysX_exact_resume=True)
    def finish(self):
        assert self.controls==300 and self.parent_reset and self.isolated and self.roundtrip
        count=self.env._integrated_contact.tick-self.contact_start;assert count==1200
        assert all(v==1200 for v in self.env._physics_action_delay.calls.values())
        return dict(controls=300,actual_contact_callbacks=count,action_group_callbacks=dict(self.env._physics_action_delay.calls),initial_assignment=self.initial,
                    final_assignment=self.assignment(),selected_parent_reset=self.parent_reset,isolated_PD_reset=self.isolated,CUDA_disk_roundtrip=self.roundtrip,
                    actual_audit=self.adapter.audit(),recipe=self.env.explicit_pd_recipe(),actor35_cleancritic38_no_teacher=True,
                    learning_optimizer_updates=0,SDK_only_not_skill_or_hardware_graduation=True)
