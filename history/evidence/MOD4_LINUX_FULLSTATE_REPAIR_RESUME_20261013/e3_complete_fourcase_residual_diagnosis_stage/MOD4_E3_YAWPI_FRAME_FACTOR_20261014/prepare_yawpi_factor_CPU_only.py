"""Prepare an independent frozen factor; never SSH, launch SDK, or update PPO."""
from pathlib import Path
import ast, hashlib, json, time, py_compile
D=Path(__file__).resolve().parent; W=D.parent; B=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload'; P=D/'payload'; R=D/'reports'
P.mkdir(exist_ok=True); R.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(name,text):
 p=P/name; assert not p.exists(),str(p); p.write_text(text,encoding='utf8'); py_compile.compile(str(p),doraise=True); return p
def replace_once(s,a,b):
 assert s.count(a)==1,(a,s.count(a)); return s.replace(a,b,1)
component='''"""One reset/frame factor: original full pose first, then legal rotated footprint.
Native3060 ABI is actual xyzw, pinned by the worker installed-backend guard.
No live correction, new RNG draws, q setters, simulation steps, or policy edits.
"""
import numpy as np, torch
from scipy.spatial.transform import Rotation
PROFILE='e3_yaw_pi_body_sign_same_world_fullfootprint_v1'
def tensor(x):
 if isinstance(x,torch.Tensor):return x
 if hasattr(x,'torch'):return x.torch
 import warp as wp
 return wp.to_torch(x)
def pi_xyzw(q):
 assert q.ndim==2 and q.shape[1]==4 and torch.isfinite(q).all()
 assert torch.allclose(q.square().sum(-1),torch.ones(len(q),device=q.device,dtype=q.dtype),atol=1e-6,rtol=0)
 out=torch.stack((-q[:,1],q[:,0],q[:,3],-q[:,2]),-1)
 assert torch.equal(out.square().sum(-1),q.square().sum(-1))
 return out
def body_targets(groups):
 assert torch.equal(groups,torch.arange(80,device=groups.device)%3)
 v=torch.tensor([-.3,.3,0.],device=groups.device)[groups]
 assert torch.equal(v[groups==2],torch.zeros_like(v[groups==2]))
 return v
def full_reset_yawpi_same_world(env,env_ids):
 from e1_full_pose_reset import full_reset,query
 full_reset(env,env_ids)
 ids=torch.arange(env.num_envs,device=env.device) if env_ids is None else env_ids
 if not len(ids):return
 assert env.num_envs==80 and env.physics_dt==.0025 and env.step_dt==.01
 robot=env.scene['robot']; bank=env._rough_probe_bank; ray=query(env)
 before=tensor(robot.data.root_state_w)[ids].clone();q_before=tensor(robot.data.joint_pos)[ids].clone()
 assert q_before.shape==(len(ids),30) and bank['points'].shape==(25200,3)
 assert torch.equal(q_before,env._rough_probe_expected_q[ids])
 assert torch.equal(before[:,7:],torch.zeros_like(before[:,7:]))
 after=before.clone();after[:,3:7]=pi_xyzw(before[:,3:7]);xy=before[:,:2].clone()
 # Exact quaternion permutation; SciPy consumes the verified native xyzw ABI.
 frames=Rotation.from_quat(after[:,3:7].cpu().numpy()).as_matrix()
 rotations=torch.as_tensor(frames,device=env.device,dtype=torch.float32)
 z=torch.empty(len(ids),device=env.device,dtype=before.dtype)
 ceiling=float(ray.geometry.vertices[:,2].max())+2.;minimum=float('inf')
 for first in range(0,len(ids),64):
  last=min(first+64,len(ids)); offsets=torch.einsum('nij,pj->npi',rotations[first:last],bank['points'])
  starts=offsets.clone(); starts[:,:,:2]+=xy[first:last,None,:]; starts[:,:,2]=ceiling
  surface=ray.cast(starts.contiguous(),10.)
  assert surface['hit'].all() and torch.isfinite(surface['height']).all() and torch.isfinite(surface['normal']).all() and (surface['normal'][...,2]>0).all()
  placed=(surface['height']+.002-offsets[:,:,2]).amax(1)
  clear=placed[:,None]+offsets[:,:,2]-surface['height']
  assert torch.isfinite(clear).all() and float(clear.min())>=.002-1e-5
  z[first:last]=placed;minimum=min(minimum,float(clear.min()))
 after[:,2]=z
 assert torch.equal(after[:,:2],before[:,:2]) and torch.equal(after[:,7:],before[:,7:])
 robot.write_root_state_to_sim(after,env_ids=ids)
 assert torch.equal(tensor(robot.data.joint_pos)[ids],q_before)
 assert torch.equal(tensor(robot.data.root_state_w)[ids],after),'Root native setter readback mismatch'
 env._rough_query_tick=None
 receipt=dict(profile=PROFILE,ids=ids.cpu().tolist(),reset_index=getattr(env,'_yawpi_factor_reset_calls',0),original_full_reset_called_once=True,full_collision_points=25200,
  original_root_xyzw=before.cpu().tolist(),factor_root_xyzw=after.cpu().tolist(),root_Z_delta_m=(after[:,2]-before[:,2]).cpu().tolist(),
  full_q30_exact=True,XY_exact=True,zero_velocity_exact=True,quaternion_changed_NOT_root30_byteexact=True,minimum_sampled_clearance_m=minimum,
  original_clearance_m=.002,original_clearance_tolerance_m=1e-5,query_distance_m=10.,extra_physics_steps_forward_render_reset=0,no_rng_draw=True,
  legal_sampled_fullfootprint_not_continuous_collision_certificate=True)
 env._yawpi_factor_reset_calls=receipt['reset_index']+1
 env._yawpi_factor_birth_receipt=receipt
 if not hasattr(env,'_yawpi_factor_birth_receipts'):env._yawpi_factor_birth_receipts=[]
 env._yawpi_factor_birth_receipts.append(receipt)
'''
emit('yawpi_same_world_reset_factor_v1.py',component)
s=(B/'full80_runtime_native_v1.py').read_text(encoding='utf8')
s=replace_once(s,'from e1_full_pose_reset import query','from e1_full_pose_reset import query\nfrom yawpi_same_world_reset_factor_v1 import full_reset_yawpi_same_world, body_targets, PROFILE as FACTOR_PROFILE')
s=replace_once(s,"    torch.manual_seed(args.seed)","    assert args.yaw_pi_body_flip is True and args.body_sign == -1 and args.world_sign == 1 and not args.feedback_current\n    torch.manual_seed(args.seed)")
s=replace_once(s,'    recipe = configure_intro(cfg)','    recipe = configure_intro(cfg)\n    cfg.events.consistent_start.func = full_reset_yawpi_same_world')
s=replace_once(s,"    targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups]","    targets = body_targets(groups)")
s=replace_once(s,"    cap = e._integrated_contact","    save('YAWPI_FACTOR_FIRST_PHYSICS_ACTUAL.json', dict(profile=FACTOR_PROFILE,after_wrapper_reset=True,actual_last_birth=e._yawpi_factor_birth_receipt,all_births_before_physics=e._yawpi_factor_birth_receipts,body_targets_m_s=cpu(targets).tolist(),world_cohort_targets_m_s=[.3,-.3,0.],q30_exact_to_original_reset=True,root30_NOT_baseline_byteexact=True,no_live_correction=True,no_PPO=True))\n    cap = e._integrated_contact")
s=replace_once(s,"for i, label in enumerate(('forward', 'reverse', 'stand')):","for i, label in enumerate(('WORLD_forward_BODY_reverse', 'WORLD_reverse_BODY_forward', 'stand')):")
s=replace_once(s,"target = float((0.3, -0.3, 0.0)[i])","target = float((-0.3, 0.3, 0.0)[i])")
s=replace_once(s,"protocol='approved_E1_G4_derived50mm_worldmesh_actualray_approach040_fullroute_behavior_v2'","protocol='diagnostic_E3_yawpi_bodyflip_same_world_full80_original_physical_v1'")
s=replace_once(s,"    output.write_text(json.dumps(result, indent=2))","    result['yawpi_frame_factor']=dict(profile=FACTOR_PROFILE,all_actual_births=e._yawpi_factor_birth_receipts,world_cohort_group_ids=data['group_ids'].tolist(),body_command_sign_reversed=True,root30_NOT_baseline_byteexact=True,full_footprint_Z_delta_disclosed=True,no_live_heading_or_position_correction=True,no_PPO=True)\n    output.write_text(json.dumps(result, indent=2))")
emit('full80_yawpi_same_world_runtime_v1.py',s)
s=(B/'paired_full80_parameter_bound_v2.py').read_text(encoding='utf8')
s=replace_once(s,"p.add_argument('--feedback-current',action='store_true');", "p.add_argument('--yaw-pi-body-flip',action='store_true');p.add_argument('--feedback-current',action='store_true');")
s=replace_once(s,"assert a.steps in (120,1500) and a.num_envs==80 and a.seed==20260928","assert a.steps in (120,1500) and a.num_envs==80 and a.seed==20260928\nassert a.yaw_pi_body_flip and a.body_sign==-1 and a.world_sign==1 and not a.feedback_current")
s=s.replace('MOD4_3060_LEFT_SECOND_FULL80_20261014','MOD4_E3_YAWPI_FRAME_FACTOR_20261014').replace('full80_runtime_native_v1','full80_yawpi_same_world_runtime_v1')
s=replace_once(s,"('steps','num_envs','seed','body_sign','world_sign','feedback_current','headless','device')","('steps','num_envs','seed','body_sign','world_sign','yaw_pi_body_flip','feedback_current','headless','device')")
s=replace_once(s,"assert lease['case_parameters']==case","assert lease['case_parameters']==case\nfor row in lease['new_factor_components']:assert H(D/row['relative'])==row['sha256']\nassert len(lease['new_factor_components'])>=4")
emit('paired_full80_yawpi_same_world_v1.py',s)
s=(B/'run_full80_parameter_bound_parent_v2.py').read_text(encoding='utf8').replace('paired_full80_parameter_bound_v2.py','paired_full80_yawpi_same_world_v1.py').replace('full80_runtime_native_v1.py','full80_yawpi_same_world_runtime_v1.py')
emit('run_full80_yawpi_same_world_parent_v1.py',s)
paths=list(P.glob('*.py'));source=[dict(path=str(p),relative=p.name,bytes=p.stat().st_size,sha256=H(p)) for p in paths]
report=dict(epoch=time.time(),CPU_prepared_only=True,source_E3='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c',baseline_namespace='MOD4_3060_LEFT_SECOND_FULL80_20261014',new_namespace=D.name,components=source,
 original_sources=[dict(path=str(B/n),bytes=(B/n).stat().st_size,sha256=H(B/n)) for n in ('full80_runtime_native_v1.py','paired_full80_parameter_bound_v2.py','run_full80_parameter_bound_parent_v2.py','runtime/isaac/mod4/e1_full_pose_reset.py')],
 shared_original_payload_copy_required=True,new_target_GPU_lease_required=True,steps_native120_then_full1500_each_once=True,all_original_physical_query_contact_COMhardware_guards_retained=True,
 target_materialization_CPU_pending=True,GPU_native_fullfootprint_resetZ_readback_pending=True,GPU_full1500_behavior_pending=True,no_SSH_GPU_PPO_budget_or_checkpoint_mutation=True,Git_pending_root_archive=True,
 discovery_read_errors_preserved=['initial generic rg had access-denied unrelated rmuc2026_work directory','guessed full80_worker_v1.py and native_sdk_compat_v1.py did not exist; actual paired parameter-bound worker read instead'])
out=R/'YAWPI_FACTOR_CPU_SOURCE_PREPARED.json';assert not out.exists();out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),files=len(paths),no_GPU=True)))
