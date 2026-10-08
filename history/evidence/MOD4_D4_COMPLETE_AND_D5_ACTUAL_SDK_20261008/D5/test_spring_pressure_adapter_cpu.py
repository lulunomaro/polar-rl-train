"""CPU SDK-shaped fixture; actual parameter writes/CUDA proof remain separate."""
import sys,types,torch,hashlib,json
from pathlib import Path
# Read-only conversion helper imports Warp but never creates an Isaac/GPU env.
from spring_pressure_sdk_adapter import SpringPressureSDK
D=Path(__file__).resolve().parent
class Fixture:
    def __init__(self):
        self.num_envs=6;self.device='cpu';self.common_step_counter=100;self._sim_step_counter=400
        r=types.SimpleNamespace(joint_names=['other','left_gas_slide','right_gas_slide'])
        r.data=types.SimpleNamespace(joint_stiffness=torch.tensor([[9.,3500.,3500.]]).repeat(6,1))
        damp=torch.tensor([[1.,3.,3.]]).repeat(6,1);cap=torch.tensor([[5.,2000.,2000.]]).repeat(6,1);arm=torch.ones((6,3))*.002
        r.root_view=types.SimpleNamespace(get_dof_stiffnesses=lambda:r.data.joint_stiffness.clone(),get_dof_dampings=lambda:damp.clone(),get_dof_max_forces=lambda:cap.clone(),get_dof_armatures=lambda:arm.clone())
        actuator=types.SimpleNamespace(joint_indices=[1,2],stiffness=torch.ones((6,2))*3500)
        r.actuators={'gas_springs':actuator}
        def write(*,stiffness,joint_ids,env_ids,full_data):
            assert not full_data and stiffness.shape==(len(env_ids),2)
            r.data.joint_stiffness[env_ids[:,None],torch.tensor(joint_ids)[None,:]]=stiffness
        r.write_joint_stiffness_to_sim_index=write
        self.scene={'robot':r};self.original_resets=[]
        self.cfg=types.SimpleNamespace(events=types.SimpleNamespace(gas_spring_preload=types.SimpleNamespace(params={'joint_names':['left_gas_slide','right_gas_slide']})))
    def _reset_idx(self,ids):self.original_resets.append(torch.as_tensor(ids).tolist())
e=Fixture();global0=torch.random.get_rng_state().clone();a=SpringPressureSDK(e,True,20261002)
assert torch.equal(global0,torch.random.get_rng_state())
assert torch.equal(e.scene['robot'].actuators['gas_springs'].stiffness,e.scene['robot'].data.joint_stiffness[:,1:])
assert bool((e.scene['robot'].data.joint_stiffness[:,0]==9).all())
before=a.state_dict();e._reset_idx(torch.tensor([1,4]));assert e.original_resets==[[1,4]]
assert torch.equal(a.component.factor[[0,2,3,5]],before['factor'][[0,2,3,5]]) and torch.equal(a.component.episode[[1,4]],before['episode'][[1,4]]+1)
saved=a.state_dict();a.reset(torch.tensor([0,3]));a.load_state_dict(saved)
assert torch.equal(a.component.factor,saved['factor']) and torch.equal(e.scene['robot'].actuators['gas_springs'].stiffness,a.component.actual_stiffness(a.nominal))
off=SpringPressureSDK(Fixture(),False,20261002);off.reset(torch.tensor([1,4]));assert torch.equal(off.component.factor,torch.ones((6,2)))
assert not torch.cuda.is_initialized()
value=dict(passed=True,contracts=6,CPU_only=True,actual_SDK=False,actual_CUDA_resume=False,CUDA_initialized=torch.cuda.is_initialized(),
    checks=['PhysX/buffer/implicit model coherent setter fixture','selected reset after original lifecycle','unselected stiffness and non-gas stiffness preserved','global RNG unchanged','restored factor re-applied to drive and model','off exact nominal'],
    source_sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('spring_pressure_sdk_adapter.py','test_spring_pressure_adapter_cpu.py')})
(D/'reports/SPRING_PRESSURE_ADAPTER_CPU_PASSED.json').write_text(json.dumps(value,indent=2));print(json.dumps(value))
