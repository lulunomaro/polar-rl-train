"""CPU contracts for setter/auditor/reset semantics. Not an actual SDK proof."""
from types import SimpleNamespace as NS
import torch,json,hashlib
from pathlib import Path
from gas_damping_sdk_adapter import GasDampingSDK
from gas_damping_factor import PROFILE
from spring_pressure_component import SpringPressure
D=Path(__file__).resolve().parent
class Root:
    def __init__(self,n):
        self.d=torch.full((n,6),.02);self.d[:,[2,5]]=3.
        self.k=torch.zeros((n,6));self.cap=torch.full((n,6),2000.);self.arm=torch.full((n,6),.002)
    def get_dof_dampings(self):return self.d
    def get_dof_stiffnesses(self):return self.k
    def get_dof_max_forces(self):return self.cap
    def get_dof_armatures(self):return self.arm
class Robot:
    def __init__(self,n):
        self.root_view=Root(n);self.joint_names=['a','b','left_gas_slide','c','d','right_gas_slide']
        self.data=NS(joint_damping=self.root_view.d.clone(),joint_stiffness=self.root_view.k.clone())
        self.actuators={'gas_springs':NS(joint_indices=torch.tensor([2,5]),stiffness=torch.zeros(n,2),damping=torch.full((n,2),3.))}
    def write_joint_damping_to_sim_index(self,*,damping,joint_ids,env_ids,full_data):
        assert not full_data and damping.shape==(len(env_ids),2)
        self.root_view.d[env_ids[:,None],joint_ids]=damping
        self.data.joint_damping[env_ids[:,None],joint_ids]=damping
class Pressure:
    def __init__(self,robot,n):
        self.component=SpringPressure(n,'cpu',112,True);self.component.reset(torch.arange(n))
        self.nominal=torch.tensor([3500.,3500.]);self.actuator=robot.actuators['gas_springs'];self.robot=robot
        k=self.component.actual_stiffness(self.nominal)
        robot.root_view.k[:,[2,5]]=k;robot.data.joint_stiffness[:,[2,5]]=k;self.actuator.stiffness[:]=k
        self.initial_other={'damping':robot.root_view.d.clone()}
    def audit(self):
        assert torch.equal(self.initial_other['damping'],self.robot.root_view.d)
        return dict(preload_damping_force_limit_armature_unchanged=True)
class Mild:
    def __init__(self,robot):
        self.robot=robot;self.gains={'gas_springs':{'damping':torch.full((len(robot.root_view.d),2),3.)}}
        self.fail=False
    def audit(self):
        assert torch.equal(self.gains['gas_springs']['damping'],self.robot.actuators['gas_springs'].damping)
        if self.fail:raise RuntimeError('injected unrelated observer failure')
        return dict(actual_parameters_pass=True)
def env(n=10):
    r=Robot(n);pressure=Pressure(r,n)
    return NS(scene={'robot':r},num_envs=n,device='cpu',cfg=NS(events=NS(gas_spring_preload=NS(params={'joint_names':['left_gas_slide','right_gas_slide']}))),
              _spring_pressure=pressure,_mild_dr=Mild(r),_reset_idx=lambda ids:None,common_step_counter=5,_sim_step_counter=20)
def equal(a,b):
    if torch.is_tensor(a):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b
def main():
    checks=[];e=env();rng=torch.random.get_rng_state().clone();a=GasDampingSDK(e,True,9)
    assert torch.equal(rng,torch.random.get_rng_state());checks.append('private_RNG_does_not_advance_global')
    audit=a.audit();assert 2.7<=audit['actual_damping_range_Ns_m'][0]<=audit['actual_damping_range_Ns_m'][1]<=3.3
    checks.append('SI_and_three_actual_parameter_views_exact')
    before=a.state_dict();params=e.scene['robot'].root_view.d.clone();ids=torch.tensor([1,4,7]);e._reset_idx(ids)
    mask=torch.ones(10,dtype=torch.bool);mask[ids]=False
    assert torch.equal(a.component.factor[mask],before['factor'][mask]) and torch.equal(a.component.episode[mask],before['episode'][mask])
    assert torch.equal(e.scene['robot'].root_view.d[mask],params[mask]);checks.append('selected_reset_and_unselected_parameters_exact')
    assert torch.equal(a.component.episode[ids],before['episode'][ids]+1);checks.append('selected_episode_increments_once')
    assert (e.common_step_counter,e._sim_step_counter)==(5,20);checks.append('physical_and_control_clock_unchanged')
    saved=a.state_dict();b=GasDampingSDK(env(),True,99);b.load_state_dict(saved);assert equal(saved,b.state_dict())
    checks.append('factor_episode_two_RNG_complete_roundtrip')
    a.reset(ids);b.reset(ids);assert equal(a.state_dict(),b.state_dict());checks.append('next_selected_draw_exact')
    original=e._mild_dr.gains['gas_springs']['damping'];assert e._mild_dr.audit()['actual_parameters_pass']
    assert e._mild_dr.gains['gas_springs']['damping'] is original;checks.append('D0_expected_audit_nominal_reference_restored')
    e._mild_dr.fail=True
    try:e._mild_dr.audit();raise AssertionError('failure masked')
    except RuntimeError:pass
    assert e._mild_dr.gains['gas_springs']['damping'] is original;e._mild_dr.fail=False
    checks.append('unrelated_audit_failure_preserved_finally_restored')
    spring_reference=e._spring_pressure.initial_other['damping'];assert e._spring_pressure.audit()['D6_gas_damping_varies_separately']
    assert e._spring_pressure.initial_other['damping'] is spring_reference;checks.append('D5_audit_only_damping_expected_value_superseded')
    robot=e.scene['robot'];old=robot.actuators['gas_springs'].damping.clone();robot.actuators['gas_springs'].damping[0,0]+=1
    try:a.audit();raise RuntimeError('mismatched actuator model accepted')
    except AssertionError:pass
    robot.actuators['gas_springs'].damping[:]=old;checks.append('actual_model_damping_mismatch_rejected')
    wrong=dict(saved,physical_parameter='D5_stiffness')
    try:b.load_state_dict(wrong);raise RuntimeError('wrong parameter accepted')
    except ValueError:pass
    checks.append('wrong_parameter_namespace_rejected')
    off=GasDampingSDK(env(),False,11);states=[g.get_state().clone() for g in off.component.rng]
    off.reset(ids);assert all(torch.equal(x,g.get_state()) for x,g in zip(states,off.component.rng)) and off.audit()['actual_damping_range_Ns_m']==[3.,3.]
    checks.append('off_exact_nominal_no_random_draw')
    row=dict(passed=True,count=len(checks),checks=checks,CPU_only=True,CUDA_initialized=torch.cuda.is_initialized(),Torch=torch.__version__,
             source_sha256={n:hashlib.sha256((D/n if n.startswith('test_') else D/'isaac/mod4'/n).read_bytes()).hexdigest() for n in ['gas_damping_factor.py','spring_pressure_component.py','gas_damping_sdk_adapter.py','gas_damping_training_env.py','test_gas_damping_adapter_cpu.py']})
    assert not row['CUDA_initialized'];print(json.dumps(row))
if __name__=='__main__':main()
