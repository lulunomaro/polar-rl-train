from pathlib import Path
import json,sys,os,time,traceback,hashlib
D=Path(__file__).resolve().parent;F=D.parent;T=F.parent.parent
S=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1/source'

def put(name,value):
 with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)

def main():
 put('FLAT_ADDED_ANGULAR_STABILITY_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),no_PT_SDK_model_forward_GPU_physics_or_remote=True))
 os.environ['CUDA_VISIBLE_DEVICES']=''
 import torch
 torch.set_num_threads(2);sys.path[:0]=[str(D),str(F),str(S),str(S/'sm_deps')]
 from native_flat_jump_adapter_v1 import OwnFlatJumpReference,OwnFlatJumpMdp,encode_frame
 from supermimic_wheel_leg_v3.geometry import unflatten_state
 doc=json.loads((D/'OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json').read_bytes())
 fixture=json.loads((D/'NEUTRAL127_XI31_SOURCE_CPU_FIXTURE.json').read_bytes())
 provider=OwnFlatJumpReference(doc,order_scope='source_CPU_fixture')
 mdp=OwnFlatJumpMdp(provider,json.loads((S.parent/'job0/assets/import_contract.json').read_bytes()),json.loads((S/'OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json').read_bytes()))
 state=unflatten_state(torch.tensor([fixture['neutral127']]))
 f=encode_frame(torch.tensor([300]),torch.tensor([0]));a=torch.zeros(1,6)
 stationary=(*state[:3],torch.zeros_like(state[3]),*state[4:])
 low=mdp.objective_terms(stationary,f,a,a)
 omega=torch.tensor([[0.,0.,1.]],requires_grad=True)
 spin=(*state[:3],omega,*state[4:]);high=mdp.objective_terms(spin,f,a,a)
 gradient,=torch.autograd.grad(high['total'].sum(),omega)
 assert high['angular_stability_cost'].item()>0 and high['total'].item()<low['total'].item() and gradient[0,2]<0
 theta=torch.tensor(.3,requires_grad=True);c,s=theta.cos(),theta.sin();z=c*0;one=z+1
 R=torch.stack((c,-s,z,s,c,z,z,z,one)).reshape(1,3,3)
 turn=(state[0],R,*stationary[2:]);turned=mdp.objective_terms(turn,f,a,a)
 gy,=torch.autograd.grad(turned['total'].sum(),theta)
 assert turned['heading_stability_cost'].item()>0 and gy<0
 assert torch.isfinite(gradient).all() and torch.isfinite(gy)
 put('FLAT_ADDED_ANGULAR_STABILITY_SOURCE_CPU_ACTUAL.json',dict(passed=True,source_only=True,
  source_SHA=hashlib.sha256((D/'native_flat_jump_adapter_v1.py').read_bytes()).hexdigest(),
  only_added_ground_angular_heading_costs_tested=True,old_phase_shape_FK_fixture_not_rerun=True,
  stationary_score=low['total'].item(),spin_score=high['total'].item(),heading_offset_score=turned['total'].item(),
  d_reward_d_positive_yaw_rate=gradient[0,2].item(),d_reward_d_positive_heading=gy.item(),
  no_PT_SDK_model_forward_GPU_physics_or_remote=True,actual_flat_training_started=False))
 print('added flat ground angular/heading cost gradients passed; source only')

if __name__=='__main__':
 try:main()
 except BaseException:
  put('FLAT_ADDED_ANGULAR_STABILITY_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc()));raise
