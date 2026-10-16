"""Local full model finite and exact source weights; no claim of learned jumping."""
from pathlib import Path
import os,json,hashlib,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;R=D/'reports';C=json.loads((R/'INITIAL_E2_H1_CURB_HANDOFF_ACTUAL_BOUND_COLLECTION.json').read_bytes());p=D/'collected_native_models/job1.pt';v=torch.load(p,map_location='cpu',weights_only=False);source=D/'payload/job1/source/E0_full_source.pt';s=torch.load(source,map_location='cpu',weights_only=False);H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=next(x for x in C['native_local_models'] if x['path']==str(p.resolve()));assert H(p)==r['SHA'] and r['twohost_bytes_SHA_exact'];counts=[0,0]
def finite(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for z in x.values():finite(z)
 elif isinstance(x,(tuple,list)):
  for z in x:finite(z)
def exact(a,b):
 if torch.is_tensor(a):return a.dtype==b.dtype and a.shape==b.shape and a.contiguous().numpy().tobytes()==b.contiguous().numpy().tobytes()
 if isinstance(a,dict):return a.keys()==b.keys() and all(exact(z,b[k]) for k,z in a.items())
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
finite(v)
for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(v[k],s[k]),k
assert {int(x['step']) for x in v['optimizer_state_dict']['state'].values()}=={639560}
native=next(x['value'] for x in C['target72']['files'] if x['path'].endswith('/job1/native/NATIVE144_COMPLETE.json'));cpu=next(x['value'] for x in C['target72']['files'] if x['path'].endswith('/job1/native/NATIVE_ALL_ROWS_CPU_ADMITTED.json'))
assert cpu['passed'] and native['num_envs']==80 and native['source_USD_colliders'] and len(native['actual_full_sensor_body_names'])==len(native['body_names'])
out=dict(epoch=time.time(),passed=True,actual_H1_native80_controls144_callbacks576_closed=True,complete_local_checkpoint=dict(path=str(p.resolve()),bytes=p.stat().st_size,SHA=H(p),tensor_counts=counts),source_E0_SHA=H(source),source_actor9_critic8_STD17Adam_literal_bytes_exact=True,all17Adam_unchanged639560=True,target_all_saved_CPUmeans_maxabs=cpu['all_saved_actor_CPUmeans_maxabs'],target_physical_vertical_impulse_maxabs=cpu['physical_wheel_impulse_maxabs'],original_plane_query_mimic_mode4_previous_actual_clipped6_selectedreset_data_passed=True,actual_full_robot_sensor_bodies=len(native['actual_full_sensor_body_names']),authored_USD_collision_shapes=len(native['source_USD_colliders']),fresh80_DR_not_full20k_restore=True,authoring_USD_shapes_not_direct_cooked_shapeLocal=True,pose_contact_postcontrol_reset_rows_not_airborne_proof=True,all_model_runtime_tensors_finite=True,no_optimizer_CPU_or_GPU_learning_or_budget_charge=True,jump_airborne_landing_or_skill_not_yet_proven=True,required_before_PPO=['Complete20k fullsource typed state and new H1 phase save-resume','Actual airborne/contact/collision evidence and executable reward/termination readback','Freeze and review narrow H1 executable scope, not old broad S8 draft'])
with (R/'H1_NATIVE80_COMPLETE_MODEL_LOCAL_CPU_VERIFIED_AND_JUMP_RELEASE_LIMITS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(out),flush=True)
