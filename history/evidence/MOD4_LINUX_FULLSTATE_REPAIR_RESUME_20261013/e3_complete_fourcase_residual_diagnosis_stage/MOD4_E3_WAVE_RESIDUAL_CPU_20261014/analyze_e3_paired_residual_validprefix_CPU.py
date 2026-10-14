"""Existing saved e3/2b raw only; CPU, no SDK import/SSH/GPU/draw/mutation.

Original episode validity is applied before every position/contact/speed metric.
Names for measured q are deliberately not inferred from USD ordering.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import time,json,hashlib,traceback
import numpy as np
import torch
W=Path(r'C:/Users/lulu/Desktop/claude/mjcf');D=Path(__file__).resolve().parent
R=D/'reports';R.mkdir(parents=True,exist_ok=True)
OUT=R/'E3_VS2B_REMAINING_FOUR_FULL_VALIDPREFIX_CPU_ACTUAL.json'
assert not OUT.exists(),'Append-only report; never overwrite original'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def index(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def j(p):return json.loads(Path(p).read_bytes())
def quant(x):
 x=np.asarray(x,dtype=np.float64)
 return dict(min=float(x.min()),mean=float(x.mean()),median=float(np.median(x)),max=float(x.max()))
def euler(q):
 x,y,z,w=np.moveaxis(q,-1,0)
 return np.stack((np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y)),np.arcsin(np.clip(2*(w*y-z*x),-1,1)),np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))),-1)
def load(folder):
 rp=folder/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json';rev=j(rp);assert rev['passed']
 ap=folder/'reports/FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json';ad=j(ap);assert ad['passed']
 raw=Path(rev['raw']['local_path']);assert sha(raw)==rev['raw']['sha256']
 pr=Path(rev['original_report']['local_path']);report=j(pr);assert sha(pr)==rev['original_report']['sha256']
 with np.load(raw) as z:d={k:z[k].copy() for k in z.files}
 assert d['action'].shape==(1500,80,6) and d['q'].shape==(1500,80,30)
 assert np.array_equal(d['processed_action'],np.clip(d['action'],-6,6))
 p=torch.from_numpy(d['processed_action'][...,:4]).clone()*.5
 for c,h in [(0,1),(2,3)]:
  p[...,c]=torch.maximum(p[...,c],p[...,h]-1.0843)
  p[...,c]=torch.minimum(p[...,c],p[...,h]+.85)
 assert torch.equal(p,torch.from_numpy(d['guarded_leg_targets']))
 for k,a in d.items():assert np.isfinite(a).all(),k
 reset=d['terminated']|d['truncated'];assert np.array_equal(d['episode'][1:]-d['episode'][:-1],reset[:-1])
 assert np.array_equal(d['before_root'][1:][~reset[:-1]],d['root'][:-1][~reset[:-1]])
 loadN=np.maximum(d['physical_wheel_force_N'].reshape(1500,4,80,2,3)[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01)
 assert np.max(np.abs(loadN-d['impulse']/.01))<=.1
 return dict(rev=rev,ad=ad,report=report,d=d,load=loadN,input=[index(rp),index(ap)],raw=rev['raw'])
def episode_summary(v,i,ids,ep,end_event):
 d=v['d'];p=v['report'];g=int(d['group_ids'][i]);s=1 if g==0 else -1
 centers=np.asarray(p['route_scope']['tile_centers']);half=p['route_scope']['wave_x_halfspan_m'];goal=half+.2
 wi=[p['body_names'].index(n) for n in ['left_wheel','right_wheel']]
 pos=d['COM_link_pos'][ids,i][:,wi].astype(np.float64)
 x=(pos[...,0]-centers[i,0])*s;y=pos[...,1]-centers[i,1]
 before=d['before_root'][ids,i].astype(np.float64);root=d['root'][ids,i].astype(np.float64)
 ang=euler(before[:,3:7]);yaw=np.unwrap(ang[:,2]);afteryaw=np.unwrap(euler(root[:,3:7])[:,2])
 delta=root[:,:2]-before[:,:2];vx=delta[:,0]*s/.01
 body=(delta[:,0]*np.cos(yaw)+delta[:,1]*np.sin(yaw))*s/.01
 cross=(-delta[:,0]*np.sin(yaw)+delta[:,1]*np.cos(yaw))/.01
 loads=v['load'][ids,i];double=loads.min(1)>1.;req=d['action'][ids,i];clip=d['processed_action'][ids,i];gt=d['guarded_leg_targets'][ids,i]
 prediff=.5*(clip[:,[0,2]]-clip[:,[1,3]]);targetdiff=gt[:,[0,2]]-gt[:,[1,3]]
 sub=(ids[:,None]*4+np.arange(4)).reshape(-1)
 tau=d['physical_hardware_actual_applied_effort'][sub,i];lo=d['physical_hardware_torque_speed_lower'][sub,i];hi=d['physical_hardware_torque_speed_upper'][sub,i];vel=d['physical_hardware_cached_pre_actuator_velocity'][sub,i]
 assert (tau>=lo-1e-6).all() and (tau<=hi+1e-6).all()
 closest=int(x.min(1).argmax());initialbefore=(x.max(1)<-half-.2)&double;after=(x.min(1)>goal)&double
 def first(mask):return int(ids[np.flatnonzero(mask)[0]]) if mask.any() else None
 bins=[]
 for st,en in [(0,300),(300,600),(600,900),(900,1200),(1200,1500)]:
  z=(ids>=st)&(ids<en)
  if not z.any():continue
  rows=np.flatnonzero(z);sb=(rows[:,None]*4+np.arange(4)).reshape(-1)
  bins.append(dict(global_controls=[int(ids[rows[0]]),int(ids[rows[-1]])],seconds=[float(ids[rows[0]]*.01),float((ids[rows[-1]]+1)*.01)],controls=int(z.sum()),signed_world_vx_mean=float(vx[z].mean()),signed_body_along_mean=float(body[z].mean()),mean_abs_body_cross_v=float(np.abs(cross[z]).mean()),yaw_last_deg=float(np.rad2deg(afteryaw[rows[-1]])),yaw_change_deg=float(np.rad2deg(afteryaw[rows[-1]]-yaw[rows[0]])),root_cross_last_m=float(root[rows[-1],1]-centers[i,1]),minwheel_signed_last_x_m=float(x[rows[-1]].min()),minwheel_beyond_wave_end_last_m=float(x[rows[-1]].min()-half),double1N_fraction=float(double[z].mean()),raw6_mean=req[z].mean(0).tolist(),clipped6_mean=clip[z].mean(0).tolist(),guarded4_mean=gt[z].mean(0).tolist(),actual_wheel_pre_actuator_velocity_mean=vel[sb,4:].mean(0).tolist(),actual_wheel_applied_effort_mean=tau[sb,4:].mean(0).tolist()))
 wave=[]
 for n,(a,b) in enumerate(zip(np.linspace(-half,half,11)[:-1],np.linspace(-half,half,11)[1:])):
  perwheel=[]
  for k in range(2):
   z=(x[:,k]>=a)&(x[:,k]<=b)
   perwheel.append(dict(wheel=['left','right'][k],controls_in_signed_X_interval=int(z.sum()),first_control_in_interval=first(z),first_control_beyond_interval_end=first(x[:,k]>b),mean_load_N=float(loads[z,k].mean()) if z.any() else None,under_or_equal1N_fraction=float((loads[z,k]<=1).mean()) if z.any() else None,cross_y_m=quant(y[z,k]) if z.any() else None))
  both=(x.min(1)>b)&double
  wave.append(dict(interval=n+1,signed_x_edges_m=[float(a),float(b)],first_both_wheel_COM_beyond_with_double1N_control=first(both),perwheel=perwheel))
 tail=ids>=max(int(ids[0]),int(ids[-1])-299)
 q=d['q'][ids,i]
 return dict(env=i,group=g,episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),valid_controls=len(ids),ending_event=end_event,original_complete=bool(initialbefore.any() and after.any() and first(initialbefore)<int(ids[np.flatnonzero(after)[-1]])),no_sameepisode_reset_credit=True,
  signed_minwheel_best_x_m=float(x[closest].min()),best_control=int(ids[closest]),best_minwheel_beyond_wave_end_m=float(x[closest].min()-half),best_deficit_to_original_after200mm_m=float(goal-x[closest].min()),last_minwheel_beyond_wave_end_m=float(x[-1].min()-half),last_deficit_to_after200mm_m=float(goal-x[-1].min()),first_before_double1N_control=first(initialbefore),first_after_double1N_control=first(after),first_leadingwheel_wave_entry_control=first(x.max(1)>=-half),first_bothwheels_wave_end_control=first(x.min(1)>half),
  signed_world_vx=quant(vx),signed_body_along=quant(body),mean_abs_body_cross_v_m_s=float(np.abs(cross).mean()),last_valid3s_signed_world_vx_m_s=float(vx[tail].mean()),world_signed_dx_m=float(delta[:,0].sum()*s),root_cross_max_abs_m=float(np.abs(root[:,1]-centers[i,1]).max()),root_cross_last_m=float(root[-1,1]-centers[i,1]),yaw_abs_max_deg=float(np.rad2deg(np.abs(yaw)).max()),yaw_final_deg=float(np.rad2deg(afteryaw[-1])),yaw_last_valid3s_change_deg=float(np.rad2deg(afteryaw[-1]-yaw[np.flatnonzero(tail)[0]])),actual_world_omega_z_mean=float(root[:,12].mean()),roll_abs_max_deg=float(np.rad2deg(np.abs(ang[:,0])).max()),pitch_abs_max_deg=float(np.rad2deg(np.abs(ang[:,1])).max()),
  double1N_fraction=float(double.mean()),perwheel_mean_load_N=loads.mean(0).tolist(),perwheel_under_or_equal1N_fraction=(loads<=1).mean(0).tolist(),perwheel_load_quant=[quant(loads[:,k]) for k in range(2)],signed_left_minus_right_x_m=quant(x[:,0]-x[:,1]),
  raw6_quant=[quant(req[:,k]) for k in range(6)],raw6_clip_lower_fraction=(req<=-6).mean(0).tolist(),raw6_clip_upper_fraction=(req>=6).mean(0).tolist(),clipped6_quant=[quant(clip[:,k]) for k in range(6)],guarded4_quant=[quant(gt[:,k]) for k in range(4)],actual_requested_crank_minus_hip_rad=[quant(prediff[:,k]) for k in range(2)],actual_guarded_crank_minus_hip_rad=[quant(targetdiff[:,k]) for k in range(2)],CAD_lower_projection_fraction=(prediff<-1.0843).mean(0).tolist(),CAD_upper_projection_fraction=(prediff>.85).mean(0).tolist(),CAD_target_lower_fraction=(np.abs(targetdiff+1.0843)<=2e-6).mean(0).tolist(),CAD_target_upper_fraction=(np.abs(targetdiff-.85)<=2e-6).mean(0).tolist(),
  actual_per_motor_applied_effort_quant=[quant(tau[:,k]) for k in range(6)],actual_per_motor_bound_lower_fraction=(np.abs(tau-lo)<=1e-5).mean(0).tolist(),actual_per_motor_bound_upper_fraction=(np.abs(tau-hi)<=1e-5).mean(0).tolist(),actual_per_motor_pre_actuator_velocity_quant=[quant(vel[:,k]) for k in range(6)],q30_indexed_min=q.min(0).tolist(),q30_indexed_max=q.max(0).tolist(),q30_indexed_last=q[-1].tolist(),q30_name_mapping_not_saved_NOT_inferred=True,
  closure_max_m=float(d['closure'][ids,i].max()),mimic_max_rad=float(d['mimic'][ids,i].max()),three_second_bins=bins,ten_section_spatial_interval_tables=wave,intervals_are_authored_section_X_partition_NOT_contact_point_or_actual_peak_events=True)
def summary(v,i):
 d=v['d'];es=[]
 for ep in np.unique(d['episode'][:,i]):
  ids=np.flatnonzero(d['episode'][:,i]==ep);event=ids[(d['terminated']|d['truncated'])[ids,i]]
  ending=None
  if len(event):
   c=int(event[0]);ending=dict(control=c,ordinary=bool(d['terminated'][c,i]),truncation=bool(d['truncated'][c,i]),reason_names=[v['report']['reason_names'][k] for k in np.flatnonzero(d['reasons'][c,i])]);ids=ids[ids<c]
  if len(ids):es.append(episode_summary(v,i,ids,ep,ending))
 return dict(env=i,original_contact_complete=next(r for r in v['rev']['rows'] if r['env']==i)['contact_complete'],all_valid_episodes=es)
try:
 old=load(W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014');new=load(W/'MOD4_3060_LEFT_SECOND_FULL80_20261014')
 pairp=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/LEFT_REPAIR_DIRECT_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json';pair=j(pairp);assert pair['passed'] and pair['actual_all_initial_root_q30_physical_parameters_recipes_assignments_captured_RNG_and_queue_values_exact']
 assert np.array_equal(old['d']['before_root'][0],new['d']['before_root'][0])
 remaining=[r['env'] for r in new['rev']['rows'] if r['group']!=2 and not r['contact_complete']];assert remaining==[6,15,67,69]
 allrows=[dict(env=i,old=summary(old,i),new=summary(new,i)) for i in range(80) if int(new['d']['group_ids'][i])!=2]
 events=[]
 for c,i in np.argwhere(new['d']['terminated']|new['d']['truncated']):
  c=int(c);i=int(i);events.append(dict(control=c,env=i,episode=int(new['d']['episode'][c,i]),ordinary=bool(new['d']['terminated'][c,i]),truncated=bool(new['d']['truncated'][c,i]),names=[new['report']['reason_names'][k] for k in np.flatnonzero(new['d']['reasons'][c,i])],event_sample_root=new['d']['root'][c,i].tolist(),event_sample_closure_m=float(new['d']['closure'][c,i]),event_sample_mimic_rad=float(new['d']['mimic'][c,i]),event_sample_q30=new['d']['q'][c,i].tolist(),event_samples_excluded_from_valid_transit_prefix=True))
 out=dict(epoch=time.time(),passed=True,scope='Existing fullraw CPU characterization, not cause or qualification',source_old=old['rev']['source_SHA'],source_new=new['rev']['source_SHA'],old_new_contact_counts=[[old['rev']['forward_complete'],old['rev']['reverse_complete']],[new['rev']['forward_complete'],new['rev']['reverse_complete']]],raw_indexes=[old['raw'],new['raw']],input_reports=old['input']+new['input']+[index(pairp)],source=index(__file__),actual_channel_schema={k:dict(shape=list(a.shape),dtype=str(a.dtype)) for k,a in new['d'].items()},all_actual_raw_processed_CAD_requests_byteexact=True,all_actual_nonreset_root_and_episode_coverage_exact=True,all_actual_effort_within_saved_original_torque_speed_limits=True,ordinary_and_truncation_events=events,remaining=remaining,remaining4_paired=[r for r in allrows if r['env'] in remaining],improved21_72_70_paired=[r for r in allrows if r['env'] in [21,72,70]],all54_paired=allrows,
  limitations=dict(policy_obs='Copied after vec.step may alias updated actor buffer; no same-control actor replay',physical_delayed_applied_target='Delay queue row traces are empty; raw wheel request is not delayed applied target',q='All30 measured positions saved, exact perjoint name mapping absent here; indexedq is not commanded CAD input bounds',contact='Saved wheel body net force/integral is actual support witness; individual contact point/normal/friction impulse not saved',massCOM='Actual substep mass-weightedCOM saved and prior independentCOM1e-5 admission passed; no hardware calibration',base_contact='Boolean termination captured; exact chassis/guide contact point and force not saved',causal='Sameinitial paired rollouts differ afterpolicy update; residual correlations do not prove unique causation'),
  physical_contract_preserved=dict(approach_m=.4,seconds=15,contact_N=1.,after_margin_m=.2,ground_query_tolerance_m=1e-6),no_CUDA_initialized=not torch.cuda.is_initialized(),no_new_RNG_GPU_PPO_SSH_candidate_or_budget=True,Git_archive_pending_root_owner=True,
  reader_output_error_retained='Initial schema exploration printed route_scope containing large arrays and tool truncated output; no source/raw mutation or GPU activity. Compact reader thereafter.')
 assert out['no_CUDA_initialized'];OUT.write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(OUT),bytes=OUT.stat().st_size,remaining=[dict(env=r['env'],new=[dict(prefix=e['valid_controls'],deficit=e['best_deficit_to_original_after200mm_m'],yaw=e['yaw_final_deg'],cross=e['root_cross_last_m'],double1N=e['double1N_fraction'],end_event=e['ending_event']) for e in r['new']['all_valid_episodes']]) for r in out['remaining4_paired']],events=events)))
except Exception:
 err=R/f'ORIGINAL_CPU_READER_ERROR_{time.time_ns()}.json';err.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source=index(__file__),no_GPU_or_SSH=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8');raise
