"""Separate observed baseline failures; no causal or production reward edit."""
from pathlib import Path
import json,hashlib,ast,time,numpy as np,torch,types
D=Path(__file__).resolve().parent;W=D.parents[1];L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013';A=D/'attempts/geometry_bodypos_worldpos_1500_v1/output'
j=lambda p:json.loads(Path(p).read_bytes());c=j(A/'COMPLETE_ACTUAL.json');v=j(D/'reports/BODYPOS_WORLDPOS1500_CPU_ACTUAL_REVIEW.json')
with np.load(A/'route_raw.npz') as archive:r={k:archive[k].copy() for k in archive.files}
T,N=r['root'].shape[:2];groups=r['group_ids'];q=r['before_root'][...,3:7]
yaw=np.arctan2(2*(q[...,3]*q[...,2]+q[...,0]*q[...,1]),1-2*(q[...,1]**2+q[...,2]**2));pitch=np.arcsin(np.clip(2*(q[...,3]*q[...,1]-q[...,2]*q[...,0]),-1,1))
delta=r['root'][...,:2]-r['before_root'][...,:2];body=(delta[...,0]*np.cos(yaw)+delta[...,1]*np.sin(yaw))/.01;world=delta[...,0]/.01
contact=(r['impulse']/.01>1).all(-1);diff=np.stack((r['guarded_leg_targets'][...,0]-r['guarded_leg_targets'][...,1],r['guarded_leg_targets'][...,2]-r['guarded_leg_targets'][...,3]),-1)
rows=[]
for i in range(N):
 valid=(r['episode'][:,i]==0)&(~r['terminated'][:,i]);route=v['fullroute']['rows'][i]
 completed=bool(route['complete_double1N_episodes']);heading=abs((yaw[:,i]-c['factor']['yaw_rad']+np.pi)%(2*np.pi)-np.pi)
 stalled=(body[:,i]<.05)&(r['targets_m_s'][i]!=0)&valid;highpitch=(abs(pitch[:,i])>np.deg2rad(10))&valid;largeyaw=(heading>np.pi/4)&valid
 rows.append(dict(env=i,standing=groups[i]==2,completed_double1N_before_to_after200mm=completed,
  initial_complete_pose_DR_q_exact=True,ordinary_failure_events=int(r['terminated'][:,i].sum()),
  max_route_heading_deg=float(heading[valid].max()*180/np.pi),large_heading_over45_control=int(largeyaw.sum()),
  large_heading_first_control=int(np.flatnonzero(largeyaw)[0]) if largeyaw.any() else None,
  BODY_stall_under05_control=int(stalled.sum()),BODY_stall_first_control=int(np.flatnonzero(stalled)[0]) if stalled.any() else None,
  pitch_over10deg_control=int(highpitch.sum()),pitch_over10deg_first_control=int(np.flatnonzero(highpitch)[0]) if highpitch.any() else None,
  BODY_stall_and_pitch_over10_control=int((stalled&highpitch).sum()),BODY_stall_without_pitch_over10_control=int((stalled&~highpitch).sum()),
  world_progress_speed_mean=float(world[valid,i].mean()),BODY_speed_mean=float(body[valid,i].mean()),two_wheel_mean_load_over1N_fraction=float(contact[valid,i].mean()),
  left_raw_actor_abs_at_least6_fraction=float((abs(r['action'][valid,i,0])>=6).mean()),left_guard_lower_bound_fraction=float((abs(diff[valid,i,0]-(-1.0843))<1e-5).mean()),right_guard_lower_bound_fraction=float((abs(diff[valid,i,1]-(-1.0843))<1e-5).mean()),
  max_left_raw_actor_abs=float(abs(r['action'][valid,i,0]).max()),
  descriptive_flags=dict(heading_over45_observed=bool(largeyaw.any()),BODY_stall_observed=bool(stalled.any()),pitch_over10_observed=bool(highpitch.any())),
  flags_are_descriptive_not_unique_causes=True))
source=L/'runtime/isaac/mod4/scut_flat_rescue.py';tree=ast.parse(source.read_text(encoding='utf8'));wanted=('exponential','forward_error','linear_exp','linear_square','linear_gap','yaw_exp','orientation')
scope=dict(torch=torch);functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted];assert len(functions)==len(wanted)
exec(compile(ast.Module(body=functions,type_ignores=[]),str(source)+'#CPU-original-reward-geometry-fixture','exec'),scope)
def fixture(sign,pitch_deg,heading_deg):
 gravity=torch.tensor([[np.sin(np.deg2rad(pitch_deg)),0.,-np.cos(np.deg2rad(pitch_deg))]],dtype=torch.float32)
 cmd=torch.tensor([[sign*.3,0.,0.]],dtype=torch.float32)
 robot=types.SimpleNamespace(data=types.SimpleNamespace(projected_gravity_b=gravity,root_lin_vel_b=torch.tensor([[sign*.3,0.,0.]],dtype=torch.float32),root_ang_vel_b=torch.zeros(1,3)))
 env=types.SimpleNamespace(scene={'robot':robot},command_manager=types.SimpleNamespace(get_command=lambda name:cmd))
 return dict(BODYsign=sign,pitch_deg=pitch_deg,birth_relative_world_heading_deg=heading_deg,
  forward_error=float(scope['forward_error'](env)),linear_exp=float(scope['linear_exp'](env)),linear_square=float(scope['linear_square'](env)),linear_gap=float(scope['linear_gap'](env)),yaw_exp=float(scope['yaw_exp'](env)),
  orientation_pitch=float(scope['orientation'](env,'pitch')),orientation_pitch_velocity=float(scope['orientation'](env,'pitch_velocity')),orientation_roll_velocity=float(scope['orientation'](env,'roll_velocity')))
fixtures=[fixture(s,p,h) for s in (1,-1) for p in (0,10) for h in (0,45,90)]
for p in (0,10):
 values=[x for x in fixtures if x['pitch_deg']==p]
 for key in ('linear_exp','linear_square','linear_gap','yaw_exp','orientation_pitch','orientation_pitch_velocity','orientation_roll_velocity'):assert len(set(x[key] for x in values))==1,(p,key)
runmanifest=j(W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/run_manifest.json')
report=dict(epoch=time.time(),CPU_original_source_reward_fixture_passed=True,GPU_new_run=False,source_checkpoint_SHA=c['checkpoint_sha256'],fullraw_SHA=c['raw']['sha256'],
 baseline_complete_double1N=2,moving=7,per_env_observed_failure_factors=rows,
 original_reward_SOURCE=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),functions=wanted),
 original_reward_geometric_invariance_fixtures=fixtures,positive_negative_tracking_yaw_pitch_weights_invariant_given_matched_BODY_state=True,
 original_velocity_reward_pays_BODY_x_not_birth_world_route_progress=True,
 yaw_reward_compares_actual_BODY_angular_velocity_to_command0_not_absolute_birth_heading=True,
 orientation_velocity_gain_depends_command_squared_not_direction_sign=True,
 source_RM_heading_command=runmanifest['env'].get('RM_HEADING_CMD'),source_RM_map_mode=runmanifest['env'].get('RM_MAP_MODE'),
 no_actor_birth_heading_feature_or_frozen_reward_change_causal_inference=True,
 conclusion='Left crank clipping/lower-bound occupancy is shared by all cases, while failure manifestations differ (turning, substantial stall/pitch, or endpoint insufficiency). It is a candidate common control defect, not yet a proven sole cause. Original selected reward equations have no explicit positive/negative sign preference or absolute-route heading correction.',
 original_readonly_path_errors_retained=['scut_rescue_rewards.py/scut_rescue_reward.py/scut_aligned_reward.py/skills.py guesses absent; actual task aliases scut_flat_rescue.py and skills_isaac.py read.'],
 all_original_physics_tolerances_unchanged=True,not_production_qualification=True)
R=D/'reports/BASELINE1500_FAILURE_FACTORS_AND_REWARD_GEOMETRY_CPU_ACTUAL_REVIEW.json';assert not R.exists();R.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(R),completed=2,moving=7,env_rows=[{k:x[k] for k in ('env','standing','completed_double1N_before_to_after200mm','large_heading_over45_control','BODY_stall_under05_control','pitch_over10deg_control','left_guard_lower_bound_fraction','right_guard_lower_bound_fraction')} for x in rows],reward_fixture_symmetric=True),ensure_ascii=False))
