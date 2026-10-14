"""Actual saved root/q and complete bank, synthetic plane; no Isaac imports."""
from pathlib import Path
import json,sys,types,hashlib,ast,time
import numpy as np,torch
from scipy.spatial.transform import Rotation
D=Path(__file__).resolve().parent;W=D.parent;B=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload';P=D/'payload';R=D/'reports'
sys.path.insert(0,str(P));import yawpi_same_world_reset_factor_v1 as f
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rv=json.loads((W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json').read_bytes())
probe_path=Path(rv['original_full_report']['local_path']);assert H(probe_path)==rv['original_full_report']['sha256'];probe=json.loads(probe_path.read_bytes())
initial=probe['initial'];root=torch.tensor(initial['root'],dtype=torch.float32);q=torch.tensor(initial['q'],dtype=torch.float32)
assert root.shape==(80,13) and q.shape==(80,30) and torch.equal(root[:,7:],torch.zeros_like(root[:,7:]))
with np.load(B/'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz') as z:
 pick=int(np.argmin(abs(z['root_height']-.25)));points=torch.tensor(z['points_root'][pick],dtype=torch.float32)
assert points.shape==(25200,3)
class Robot:
 def __init__(self):self.data=types.SimpleNamespace(root_state_w=root.clone(),joint_pos=q.clone());self.writes=[]
 def write_root_state_to_sim(self,state,env_ids):self.data.root_state_w[env_ids]=state;self.writes.append(state.clone())
class Ray:
 def __init__(self):self.geometry=types.SimpleNamespace(vertices=np.array([[0.,0.,0.]],dtype=np.float32));self.mode='valid';self.calls=[]
 def cast(self,starts,distance):
  self.calls.append((starts.shape,distance));shape=starts.shape[:-1];height=torch.zeros(shape);hit=torch.ones(shape,dtype=torch.bool);normal=torch.zeros((*shape,3));normal[...,2]=1
  if self.mode=='miss':hit[0,0]=False
  if self.mode=='nan':height[0,0]=float('nan')
  if self.mode=='down':normal[0,0,2]=-1
  return dict(hit=hit,height=height,normal=normal)
robot=Robot();ray=Ray();env=types.SimpleNamespace(num_envs=80,device='cpu',physics_dt=.0025,step_dt=.01,scene={'robot':robot},_rough_probe_bank={'points':points},_rough_probe_expected_q=q.clone(),original_calls=0)
def original(e,ids):
 ids=torch.arange(80) if ids is None else ids;e.original_calls+=1;robot.data.root_state_w[ids]=root[ids];robot.data.joint_pos[ids]=q[ids]
fake=types.ModuleType('e1_full_pose_reset');fake.full_reset=original;fake.query=lambda e:ray
sys.modules['e1_full_pose_reset']=fake
rng=torch.get_rng_state().clone();f.full_reset_yawpi_same_world(env,None);after=robot.data.root_state_w.clone()
assert env.original_calls==1 and len(robot.writes)==1 and len(ray.calls)==2 and sum(x[0][0]*x[0][1] for x in ray.calls)==80*25200
assert torch.equal(after[:,:2],root[:,:2]) and torch.equal(robot.data.joint_pos,q) and torch.equal(torch.get_rng_state(),rng)
expectedq=torch.stack((-root[:,4],root[:,3],root[:,6],-root[:,5]),-1);assert torch.equal(after[:,3:7],expectedq)
groups=torch.arange(80)%3;body=f.body_targets(groups);origbody=torch.tensor([.3,-.3,0.])[groups]
def heading(r):
 x,y,z,w=r[:,3:7].T;return torch.stack((1-2*(y*y+z*z),2*(x*y+w*z)),-1)
err=float((heading(root)*origbody[:,None]-heading(after)*body[:,None]).abs().max());assert err<=1e-7
assert env._yawpi_factor_birth_receipt['minimum_sampled_clearance_m']>=.002-1e-5
selected=torch.tensor([0,17,79]);f.full_reset_yawpi_same_world(env,selected);assert env.original_calls==2 and env._yawpi_factor_reset_calls==2
assert torch.equal(robot.data.root_state_w[selected,3:7],expectedq[selected]),'Repeated reset must not double-flip previous factor state'
neg=0
for mode in ('miss','nan','down'):
 ray.mode=mode
 try:f.full_reset_yawpi_same_world(env,selected)
 except AssertionError:neg+=1
 else:raise AssertionError('Bad footprint admitted '+mode)
ray.mode='valid'
for bad in (torch.zeros(80,dtype=torch.long),torch.arange(80)%2):
 try:f.body_targets(bad)
 except AssertionError:neg+=1
 else:raise AssertionError('Bad cohort admitted')
for bad in (torch.zeros(80,4),torch.zeros(80,3)):
 try:f.pi_xyzw(bad)
 except AssertionError:neg+=1
 else:raise AssertionError('Bad quaternion admitted')
origast=ast.parse((B/'full80_runtime_native_v1.py').read_text(encoding='utf8'));newast=ast.parse((P/'full80_yawpi_same_world_runtime_v1.py').read_text(encoding='utf8'))
def loop(t):return next(n for n in ast.walk(t) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='step')
assert ast.dump(loop(origast),include_attributes=False)==ast.dump(loop(newast),include_attributes=False)
def fn(t,name):return next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==name)
assert ast.dump(fn(origast,'measured_capture'),include_attributes=False)==ast.dump(fn(newast,'measured_capture'),include_attributes=False)
assert ast.dump(fn(origast,'before_reset'),include_attributes=False)==ast.dump(fn(newast,'before_reset'),include_attributes=False)
reset_ast=ast.parse((P/'yawpi_same_world_reset_factor_v1.py').read_text())
for n in ast.walk(reset_ast):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):
  assert n.func.attr not in ('step','forward','render','reset','write_joint_state_to_sim','manual_seed','rand','randn','random')
out=R/'YAWPI_FACTOR_FULLBANK_ACTUAL_SOURCE_CPU_FIXTURE_PASSED.json';assert not out.exists()
report=dict(epoch=time.time(),passed_CPU_fixture_only=True,actual_source_probe=dict(path=str(probe_path),bytes=probe_path.stat().st_size,sha256=H(probe_path)),actual_collision_bank=dict(path=str(B/'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'),sha256=H(B/'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'),points_per_pose=25200),actual80_rootq_fixture=True,
 source_E3=rv['source_SHA'],synthetic_flat_query_only=True,all25200_each80_collision_points_used=True,global_CPU_RNG_unchanged=True,world_heading_command_product_error_m_s=err,
 selected_reset_cannot_doubleflip=True,strict_negative_inputs=neg,original_control_loop_measured_capture_before_reset_ASTexact=True,
 joint30_XY_velocity_exact=True,quaternion_factor_only_plus_safe_Z_recalculation=True,physical_reset_Z_and_native_ABI_still_PENDING=True,
 GPU_native120_scope_PENDING=True,full1500_frozen_behavior_PENDING=True,no_SSH_GPU_PPO_budget=True,components=[dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)) for p in P.glob('*.py')],Git_pending_root_archive=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),negative_inputs=neg,world_error=err,GPU_pass=False)))
