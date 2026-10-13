"""CPU-only source/case/footprint/static worker contract preparation."""
from pathlib import Path
import ast,json,hashlib,time,torch,numpy as np
from scipy.spatial.transform import Rotation
D=Path(__file__).resolve().parent;W=D.parents[1];L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
P=L/'attempts/same128_continue_second7200_v1/output/model_32396.pt'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(P)=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
ck=torch.load(P,map_location='cpu',weights_only=False);count=0
def finite(x):
 global count
 if isinstance(x,torch.Tensor) and (x.is_floating_point() or x.is_complex()):assert torch.isfinite(x).all();count+=1
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,(tuple,list)):
  for v in x:finite(v)
finite(ck);assert count==107
profile=json.loads((L/'runtime/isaac/mod4/g4_cad_profile.json').read_bytes());assert profile['derived_peak_to_trough_m']==.05
with np.load(L/'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz') as bank:
 index=int(np.argmin(abs(bank['root_height']-.25)));points=bank['points_root'][index].copy();q=bank['q'][index].copy()
cases=[]
for world in (1,-1):
 for body in (1,-1):
  yaw=0. if world==body else np.pi
  rot=Rotation.from_euler('z',yaw).as_matrix();offset=points@rot.T;start=np.array([-world*(profile['span_m']*.5+.4),0.])
  # Every sampled collider point remains on the initial planar side.
  clearance=-(offset[:,0]+start[0])*world-profile['span_m']*.5
  assert clearance.min()>0
  assert (abs(offset[:,1])<4.5).all() and q.shape==(30,)
  cases.append(dict(case_id=f'body_{body:+d}_world_{world:+d}_pose0',body_sign=body,world_sign=world,yaw_rad=yaw,pitch_deg=0.,roll_deg=0.,height_m=.25,root_approach_m=.4,
   complete_sampled_footprint_flat_front_clearance_m=float(clearance.min()),quaternion_wxyz=Rotation.from_matrix(rot).as_quat()[[3,0,1,2]].tolist()))
sources=[]
for p in D.glob('*.py'):
 ast.parse(p.read_text(encoding='utf8'));compile(p.read_text(encoding='utf8'),str(p),'exec');sources.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)))
result=dict(epoch=time.time(),CPU_prepared=True,GPU_executed=False,source=dict(path=str(P),bytes=P.stat().st_size,sha256=H(P),floating_tensors=count,actor=dict((k,list(v.shape)) for k,v in ck['actor_state_dict'].items())),
 case_interface=cases,num_envs=8,seed=20260928,first_GUARD_prefix_controls=120,full_route_controls=1500,fullroute_seconds=15.,original_ground_tolerance_m=1e-6,
 callback_per_control=4,physics_dt=.0025,solver=[32,4],stand_cohort=1,moving_cohort=7,all_case_initial_parameter_SHA_must_exact_match_for_paired_inference=True,
 isolated_scene_process_per_case=True,no_optimizer_or_PPO=True,no_GPU_before_root_lease_native_lock=True,source_files=sources,
 original_readonly_search_errors_preserved=['Missing optional guessed mild_physical_dr.py, chassis_pd_runtime.py, sensor_mild_runtime.py, retention_assignment.py; observed real module filenames and interfaces instead.','rg workspace search encountered access denied in unrelated rmuc2026_work/unpack_verify_4zomhj13. No mutation.'],
 guard_lease_schema=dict(case_id='actual case id',checkpoint_sha256=H(P),GPU_lease_granted_by_root=True,owned_training_actual_exit_and_shared_lock_free_verified=True),
 expected_wall_time_not_measured=True,short_prefix_speed_and_health_must_actual_pass_before_full_gpu_cases=True,qualification_claimed=False)
R=D/'reports/GEOMETRY_POSE_CPU_PREPARED_ACTUAL.json';assert not R.exists();R.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(R),CPU_passed=True,GPU_executed=False,source_SHA=H(P),cases=cases),ensure_ascii=False))
