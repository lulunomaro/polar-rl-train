"""Read-only actual paired residual analysis; no CUDA, SSH, draws or setters.

Input control phase is explicit: action is requested before vec.step, processed
targets/COM/root are captured before reset. policy_obs is copied after vec.step
and may share an updated observation buffer, so it is never used for actor replay.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
from pathlib import Path
import json, hashlib, time, traceback
import numpy as np
import torch

W=Path(r'C:/Users/lulu/Desktop/claude/mjcf')
D=Path(__file__).resolve().parent
R=D/'reports';R.mkdir(exist_ok=True)
NEW=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014'
OLD=W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014'
OUT=R/'PAIRED_FULL80_RESIDUAL_ACTUAL_CPU_DIAGNOSIS.json'
assert not OUT.exists(), 'Preserve original analysis; no overwrite'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def witness(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def angles(q):
 x,y,z,w=np.moveaxis(q,-1,0)
 return np.stack((np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y)),np.arcsin(np.clip(2*(w*y-z*x),-1,1)),np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))),-1)
def quant(a):return dict(min=float(np.min(a)),median=float(np.median(a)),mean=float(np.mean(a)),max=float(np.max(a)))
def triangular_heights(tri,xy):
 """Independent float64 barycentric downward surface from actual f32 mesh."""
 t=np.asarray(tri,dtype=np.float64);a=t[:,0];b=t[:,1]-a;c=t[:,2]-a
 det=b[:,0]*c[:,1]-b[:,1]*c[:,0];assert (np.abs(det)>1e-12).all()
 h=[]
 for p in np.asarray(xy,dtype=np.float64):
  dx=p[0]-a[:,0];dy=p[1]-a[:,1]
  u=(dx*c[:,1]-dy*c[:,0])/det;v=(b[:,0]*dy-b[:,1]*dx)/det
  ok=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
  assert ok.any(), 'Residual wheel COM outside authored tile'
  h.append(np.max((a[:,2]+u*b[:,2]+v*c[:,2])[ok]))
 return np.asarray(h)
def load(folder):
 revpath=folder/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json'
 rev=json.loads(revpath.read_bytes());assert rev['passed'] and rev['ordinary']==0 and rev['truncation_unique']==0
 raw=Path(rev['raw']['local_path']);assert sha(raw)==rev['raw']['sha256']
 report=json.loads(Path(rev['original_report']['local_path']).read_bytes())
 keys=['before_root','root','action','processed_action','guarded_leg_targets','COM_link_pos','COM_link_vel','physical_wheel_force_N','episode','terminated','truncated','group_ids','command','ground','normal','closure','mimic','physical_hardware_actual_applied_effort','physical_hardware_cached_pre_actuator_velocity','physical_hardware_torque_speed_lower','physical_hardware_torque_speed_upper']
 with np.load(raw) as z:d={k:z[k].copy() for k in keys}
 assert not d['terminated'].any() and not d['truncated'].any() and (d['episode']==0).all()
 assert np.array_equal(d['before_root'][1:],d['root'][:-1]),'Nonreset same-episode root continuity'
 assert np.array_equal(d['processed_action'],np.clip(d['action'],-6,6))
 proc=torch.from_numpy(d['action'][:,:,:4]).clip(-6,6)*.5
 for c,h in [(0,1),(2,3)]:
  proc[:,:,c]=torch.maximum(proc[:,:,c],proc[:,:,h]-1.0843)
  proc[:,:,c]=torch.minimum(proc[:,:,c],proc[:,:,h]+.85)
 assert torch.equal(proc,torch.from_numpy(d['guarded_leg_targets'])),'Original CAD processor all120k byteexact'
 assert not torch.cuda.is_initialized()
 return rev,report,d,revpath
def summarize(rev,report,d,env):
 g=int(d['group_ids'][env]);s=1 if g==0 else -1
 centers=np.asarray(report['route_scope']['tile_centers'],dtype=np.float64)
 half=float(report['route_scope']['wave_x_halfspan_m']);goal=half+.2
 wheels=[report['body_names'].index(x) for x in ('left_wheel','right_wheel')]
 pos=d['COM_link_pos'][:,env][:,wheels].astype(np.float64)
 x=(pos[...,0]-centers[env,0])*s; y=pos[...,1]-centers[env,1]
 roots=d['root'][:,env].astype(np.float64);before=d['before_root'][:,env].astype(np.float64)
 eul=angles(before[:,3:7]);yaw=np.unwrap(eul[:,2]);delta=roots[:,:2]-before[:,:2]
 world=delta[:,0]*s/.01;body=(delta[:,0]*np.cos(yaw)+delta[:,1]*np.sin(yaw))*s/.01
 crossbody=(-delta[:,0]*np.sin(yaw)+delta[:,1]*np.cos(yaw))/.01
 forces=np.maximum(d['physical_wheel_force_N'].reshape(1500,4,80,2,3)[:,:,env,:,2],0)
 loadN=forces.sum(1)*np.float32(.0025)/np.float32(.01)
 double=loadN.min(1)>1.
 left=d['action'][:,env,0];hip=d['action'][:,env,1];right=d['action'][:,env,2];rhip=d['action'][:,env,3]
 targets=d['guarded_leg_targets'][:,env]
 preleft=.5*(np.clip(left,-6,6)-np.clip(hip,-6,6))
 preright=.5*(np.clip(right,-6,6)-np.clip(rhip,-6,6))
 guard=(np.abs(targets[:,0]-targets[:,1]+1.0843)<=2e-6)
 upper=(np.abs(targets[:,0]-targets[:,1]-.85)<=2e-6)
 actual=np.array([r for r in rev['rows'] if r['env']==env])[0]
 bins=[]
 for st,en in [(0,300),(300,600),(600,900),(900,1200),(1200,1500)]:
  bins.append(dict(seconds=[st*.01,en*.01],mean_signed_world_vx_m_s=float(world[st:en].mean()),mean_signed_body_along_m_s=float(body[st:en].mean()),signed_min_wheel_end_x_m=float(x[en-1].min()),min_wheel_closest_to_goal_x_m=float(x[st:en].min(1).max()),end_root_cross_m=float(roots[en-1,1]-centers[env,1]),max_abs_yaw_deg=float(np.rad2deg(np.abs(yaw[st:en])).max()),double_1N_fraction=float(double[st:en].mean()),left_CAD_lower_projection_fraction=float((preleft[st:en]<-1.0843).mean()),left_lower_target_fraction=float(guard[st:en].mean()),raw_left_clip_lower_fraction=float((left[st:en]<=-6).mean())))
 closest=int(x.min(1).argmax());bothafter=(x.min(1)>goal)
 tau=d['physical_hardware_actual_applied_effort'][:,env].astype(np.float64)
 lo=d['physical_hardware_torque_speed_lower'][:,env].astype(np.float64);hi=d['physical_hardware_torque_speed_upper'][:,env].astype(np.float64)
 return dict(env=env,group=g,complete_original_contact=actual['contact_complete'],all_valid_episode_controls=1500,no_resets=True,signed_route_goal_minwheel_m=goal,
  signed_min_wheel_last_x_m=float(x[-1].min()),signed_min_wheel_closest_x_m=float(x[closest].min()),closest_control=closest,closest_deficit_to_original_after_goal_m=float(goal-x[closest].min()),last_deficit_to_original_after_goal_m=float(goal-x[-1].min()),
  root_start_signed_x_m=float((before[0,0]-centers[env,0])*s),root_end_signed_x_m=float((roots[-1,0]-centers[env,0])*s),signed_world_total_dx_m=float(delta[:,0].sum()*s),signed_world_vx_m_s=quant(world),signed_body_along_v_m_s=quant(body),mean_cos_yaw=float(np.cos(yaw).mean()),mean_abs_body_cross_v_m_s=float(np.abs(crossbody).mean()),last3s_signed_world_vx_m_s=float(world[-300:].mean()),
  root_abs_cross_max_m=float(np.abs(roots[:,1]-centers[env,1]).max()),root_cross_last_m=float(roots[-1,1]-centers[env,1]),yaw_abs_max_deg=float(np.rad2deg(np.abs(yaw)).max()),yaw_last_deg=float(np.rad2deg(yaw[-1])),roll_abs_max_deg=float(np.rad2deg(np.abs(eul[:,0])).max()),pitch_abs_max_deg=float(np.rad2deg(np.abs(eul[:,1])).max()),
  perwheel_mean_load_N=loadN.mean(0).tolist(),double_1N_fraction=float(double.mean()),one_or_no_1N_fraction=float((~double).mean()),perwheel_under_1N_fraction=(loadN<=1).mean(0).tolist(),
  both_wheels_after_goal_controls=np.flatnonzero(bothafter).tolist(),after_goal_with_insufficient_contact_only=bool(bothafter.any() and not (bothafter&double).any()),
  actual_wheel_signed_velocity_mean_m_s=(d['COM_link_vel'][:,env][:,wheels,0]*s).mean(0).tolist(),signed_left_minus_right_x_m=quant(x[:,0]-x[:,1]),
  raw_left_range=quant(left),raw_hip_range=quant(hip),raw_right_range=quant(right),raw_rhip_range=quant(rhip),raw_left_clip_lower_fraction=float((left<=-6).mean()),raw_left_clip_upper_fraction=float((left>=6).mean()),raw_hip_clip_fraction=float((np.abs(hip)>=6).mean()),
  actual_left_pre_guard_input_difference_rad=quant(preleft),actual_right_pre_guard_input_difference_rad=quant(preright),left_CAD_lower_projection_fraction=float((preleft<-1.0843).mean()),right_CAD_lower_projection_fraction=float((preright<-1.0843).mean()),left_lower_target_fraction=float(guard.mean()),left_upper_target_fraction=float(upper.mean()),left_guarded_input_difference_rad=quant(targets[:,0]-targets[:,1]),right_guarded_input_difference_rad=quant(targets[:,2]-targets[:,3]),
  actual_per_motor_effort_mean_Nm=tau.mean(0).tolist(),actual_per_motor_effort_abs_mean_Nm=np.abs(tau).mean(0).tolist(),actual_per_motor_bound_fraction=(np.isclose(tau,lo,atol=1e-5,rtol=0)|np.isclose(tau,hi,atol=1e-5,rtol=0)).mean(0).tolist(),
  saved_ground_four_query_channels_min_max_m=[float(d['ground'][:,env].min()),float(d['ground'][:,env].max())],closure_max_m=float(d['closure'][:,env].max()),mimic_max_rad=float(d['mimic'][:,env].max()),three_second_bins=bins)

try:
 old,orp,od,op=load(OLD);new,nrp,nd,npth=load(NEW)
 pairp=NEW/'reports/LEFT_REPAIR_DIRECT_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json';pair=json.loads(pairp.read_bytes());assert pair['passed'] and pair['actual_all_initial_root_q30_physical_parameters_recipes_assignments_captured_RNG_and_queue_values_exact']
 assert np.array_equal(od['group_ids'],nd['group_ids']) and np.array_equal(od['before_root'][0],nd['before_root'][0])
 failed=[r['env'] for r in new['rows'] if r['group']!=2 and not r['contact_complete']];assert failed==[6,15,21,67,69,70,72]
 moving=[i for i in range(80) if int(nd['group_ids'][i])!=2]
 allpaired=[dict(env=i,old=summarize(old,orp,od,i),new=summarize(new,nrp,nd,i)) for i in moving]
 adm=json.loads((NEW/'reports/FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json').read_bytes());query=Path(adm['query']['local_path']);assert sha(query)==adm['query']['sha256']
 with np.load(query) as z:tri=z['world_triangles'].copy()
 whe=[nrp['body_names'].index('left_wheel'),nrp['body_names'].index('right_wheel')]
 for row in allpaired:
  if row['env'] not in failed:continue
  i=row['env'];p=nd['COM_link_pos'][:,i][:,whe].astype(np.float64)
  ground=triangular_heights(tri[i],p[...,:2].reshape(-1,2)).reshape(1500,2)
  row['new']['independent_actual_float32_triangle_ground_at_wheel_COM_XY_m']=[float(ground.min()),float(ground.max())]
  row['new']['wheel_COM_z_minus_triangle_surface_m']=[quant(p[:,k,2]-ground[:,k]) for k in range(2)]
  row['new']['wheel_COM_ground_last_m']=ground[-1].tolist()
  row['new']['wheel_COM_z_minus_ground_last_m']=(p[-1,:,2]-ground[-1]).tolist()
  row['new']['triangle_ground_at_COM_not_wheel_contact_or_radius_certificate']=True
 out=dict(epoch=time.time(),passed=True,scope='CPU-only full80 paired actual residual characterization',source_old=old['source_SHA'],source_new=new['source_SHA'],input_reports=[witness(op),witness(npth),witness(pairp)],raw_original_index=old['raw'],raw_new_index=new['raw'],query_index=adm['query'],source_math=witness(NEW/'payload/runtime/isaac/mod4/mod4_task.py'),source_loop=witness(NEW/'payload/full80_runtime_native_v1.py'),
  all120000_processed_requests_and_original_CAD_targets_byteexact_both=True,all1500_nonreset_root_continuity_and_full_prefix_exact=True,actual_all_initial_parameters_and_captured_RNG_pair_exact=True,
  old_forward=7,new_forward=22,old_reverse=27,new_reverse=25,ordinary_old=0,ordinary_new=0,failed_new=failed,
  action_phase='Saved raw action generated before vec.step. processed and guarded targets are captured in termination compute before reset; root/q/COM are actual pre-reset control endpoint.',
  policy_obs_phase='cpu(obs[policy]) occurs after vec.step; potential shared buffer update unresolved, excluded from same-control actor input replay and all probability reconstructions.',
  CAD_math='float32 clamp raw each leg to [-6,6], multiply .5, then crank=max(crank,hip-1.0843), min(crank,hip+.85). No q mechanical limits substituted.',
  motor_phase='Torque-speed limits use saved actual substep cached-pre-actuator velocities and exact applied effort; current endpoint joint velocity is separate.',
  all54_paired=allpaired,residual7_paired=[x for x in allpaired if x['env'] in failed],
  no_CUDA_initialized=not torch.cuda.is_initialized(),no_SSH_GPU_RNGdraw_train_mutation_budget=True,original_15s_040approach_1N_200mmafter_query_contact_COM_thresholds_unchanged=True,sole_cause_or_qualification_not_claimed=True,Git_archive_pending_root_owner=True,
  source_read_warning_preserved='Initial rg reader assumed g4_worldmesh_query_contract.py under runtime and used Windows wildcard literal; paths absent/glob invalid. Subsequent rg --files resolved actual payload CPU module. No production/source or raw mutation.')
 OUT.write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(OUT),residual=[dict(env=x['env'],deficit=x['new']['closest_deficit_to_original_after_goal_m'],worldspeed=x['new']['signed_world_vx_m_s']['mean'],last3speed=x['new']['last3s_signed_world_vx_m_s'],yaw=x['new']['yaw_abs_max_deg'],cross=x['new']['root_abs_cross_max_m'],lower=x['new']['left_CAD_lower_projection_fraction'],oldlower=x['old']['left_CAD_lower_projection_fraction']) for x in out['residual7_paired']],no_CUDA=True)))
except Exception:
 p=R/f'CPU_READER_ERROR_{time.time_ns()}.json'
 p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source=witness(__file__),no_GPU=True,original_false_retained=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8')
 raise
