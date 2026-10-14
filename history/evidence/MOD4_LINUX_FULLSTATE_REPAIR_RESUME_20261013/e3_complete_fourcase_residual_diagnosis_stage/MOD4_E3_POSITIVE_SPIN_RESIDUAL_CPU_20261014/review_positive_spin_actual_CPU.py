"""Read retained complete raw only. No SDK import, transport, candidate or PPO."""
from pathlib import Path
import numpy as np,json,hashlib,time,traceback,math
W=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent;R=D/'reports'
def read(p):return json.loads(p.read_bytes())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def index(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def find(root,name):
 ps=list(root.rglob(name));assert len(ps)==1,(root,name,len(ps));return ps[0]
def load(kind):
 parent=W/('MOD4_3060_LEFT_SECOND_RETENTION_20261014' if kind=='e3' else 'MOD4_3060_LEFT_REPAIR_RETENTION_20261014')
 case='retention_second_e3_spin_1500_v8' if kind=='e3' else 'retention_repair2b_spin_1500_v8'
 raw=find(parent/'actual_collections'/case,'retention_full_control_substep_actual.npz');p=read(raw.with_name('probe.json'));c=read(raw.with_name('COMPLETE_ACTUAL.json'))
 assert raw.stat().st_size==c['raw']['bytes'] and sha(raw)==c['raw']['sha256']
 with np.load(raw,allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
 assert a['root'].shape==(1500,88,13) and a['substep_actual_applied_effort'].shape==(6000,88,6)
 assert all(np.isfinite(x).all() for x in a.values() if x.dtype.kind in 'fc')
 assert np.array_equal(np.clip(a['raw_actor_action'],-6,6),a['vec_clipped_action'])
 assert np.array_equal(a['processed_action'],a['vec_clipped_action'])
 assert np.max(a['substep_COM_frame_error_m'])<1e-5
 lo=a['substep_torque_speed_lower'];hi=a['substep_torque_speed_upper'];tau=a['substep_actual_applied_effort'];assert np.array_equal(tau,np.clip(tau,lo,hi))
 f=a['substep_force'];calc=np.maximum(f[...,2].reshape(1500,4,88,2),0).astype(np.float64).sum(1)*.0025
 assert np.max(abs(calc-a['impulse']))/.01<=.1
 names=p['native_readonly_witness']['reason_names'];done=a['terminated']|a['truncated'];assert np.array_equal(a['episode'][1:]-a['episode'][:-1],done[:-1].astype(np.int64))
 def one(i):
  fs=np.flatnonzero(done[:,i]);stop=int(fs[0]) if len(fs) else 1500;ids=np.arange(50,stop);ss=np.arange(200,stop*4);yaw=a['root'][ids,i,12]
  assert stop>=50
  old=float(p['per_environment']['yaw_rate'][i]);mean=float(yaw.mean());assert abs(old-mean)<2e-5,(i,old,mean)
  force=a['impulse'][ids,i]/.01;eff=tau[ss,i];low=lo[ss,i];high=hi[ss,i];vel=a['substep_cached_pre_actuator_velocity'][ss,i]
  quat=a['root'][ids,i,3:7].astype(float);tilt=np.degrees(np.arccos(np.clip(1-2*(quat[:,0]**2+quat[:,1]**2),-1,1)))
  rows=[]
  for s in fs:
   rows.append(dict(control=int(s),physical_endpoint_s=float((s+1)*.01),reason=[n for j,n in enumerate(names) if a['reasons'][s,i,j]],yaw_pre_reset=float(a['root'][s,i,12]),root_z_m=float(a['root'][s,i,2]),after_reset_z_m=float(a['after_reset_root'][s,i,2])))
  def window(t0,t1):
   ix=np.arange(max(50,int(t0*100)),min(stop,int(t1*100)));return dict(start_s=t0,end_s=min(stop*.01,t1),controls=len(ix),mean_yaw=float(a['root'][ix,i,12].mean()) if len(ix) else None)
  return dict(env_id=i,group_id=int(p['group_ids'][i]),sample_index=i//11,command_yaw=float(a['command'][0,i,2]),first_failure_control=stop,valid_prefix_controls=stop,scored_controls=len(ids),scored_duration_s=len(ids)*.01,first_failure_and_later_resets=rows,yaw_mean_original=old,yaw_mean_raw_pre_reset=mean,yaw_error_absolute_mean=float(np.abs(yaw-a['command'][ids,i,2]).mean()),yaw_std=float(yaw.std()),yaw_min=float(yaw.min()),yaw_max=float(yaw.max()),yaw_windows=[window(.5,2),window(2,5),window(5,10),window(10,15)],both_wheels_original_1N_pct=float(np.mean((force>=1).all(-1))*100),wheel_mean_support_N=force.mean(0).tolist(),max_tilt_deg=float(tilt.max()),root_z_min_m=float(a['root'][ids,i,2].min()),max_closure_m=float(a['closure'][:stop,i].max()),actual_cached_motor_velocity_mean_rad_s=vel.mean(0).tolist(),actual_cached_wheel_velocity_abs_peak_rad_s=np.abs(vel[:,4:]).max(0).tolist(),actual_motor_effort_mean_Nm=eff.mean(0).tolist(),actual_motor_effort_abs_peak_Nm=np.abs(eff).max(0).tolist(),actual_motor_exact_lower_bound_pct=np.mean(eff==low,0).tolist(),actual_motor_exact_upper_bound_pct=np.mean(eff==high,0).tolist(),actual_motor_near_bound_1e6_pct=np.mean((abs(eff-low)<=1e-6)|(abs(eff-high)<=1e-6),0).tolist(),raw_actor_mean=a['raw_actor_action'][ids,i].mean(0).tolist(),raw_actor_clip_pct=(np.mean(np.abs(a['raw_actor_action'][ids,i])>=6,0)*100).tolist(),processed_actor_mean=a['processed_action'][ids,i].mean(0).tolist(),guarded_leg_target_mean_rad=a['guarded_leg_targets'][ids,i].mean(0).tolist(),guarded_crank_minus_hip_range_rad=[[float((a['guarded_leg_targets'][ids,i,j]-a['guarded_leg_targets'][ids,i,j+1]).min()),float((a['guarded_leg_targets'][ids,i,j]-a['guarded_leg_targets'][ids,i,j+1]).max())] for j in (0,2)],wheel_link_COM_velocity_finite=True,all_post_first_failure_samples_excluded=True,requested_pre_motor_torque_not_captured_cannot_infer_saturation_reason=True)
 purepos=[i for i,g in enumerate(p['group_ids']) if g==7];pureneg=[i for i,g in enumerate(p['group_ids']) if g==8]
 assert purepos==[7,18,29,40,51,62,73,84] and pureneg==[8,19,30,41,52,63,74,85]
 allfails=[dict(env_id=i,group_id=p['group_ids'][i],control=int(s),reason=[n for j,n in enumerate(names) if a['reasons'][s,i,j]]) for s,i in np.argwhere(done)]
 return dict(source=kind,checkpoint_sha256=c['checkpoint_sha256'],raw=index(raw),probe=index(raw.with_name('probe.json')),all_resets=allfails,positive=[one(i) for i in purepos],negative=[one(i) for i in pureneg],initial=p['native_readonly_witness']['first_physics_initial'],ordinary=int(a['terminated'].sum()),truncation=int(a['truncated'].sum()))
def main():
 out=R/'E3_POSITIVE_4PI_ALL_PREFIX_MOTOR_CONTACT_ACTUAL_CPU_REVIEW.json';assert not out.exists()
 b=load('2b');e=load('e3')
 assert b['checkpoint_sha256']=='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971';assert e['checkpoint_sha256']=='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
 for k in ('root','q30','physical_parameters','phase'):assert b['initial'][k]==e['initial'][k]
 b.pop('initial');e.pop('initial')
 comparisons=[]
 for sign in ('positive','negative'):
  for old,new in zip(b[sign],e[sign]):
   assert old['env_id']==new['env_id']
   comparisons.append(dict(sign=sign,env_id=old['env_id'],sample_index=old['sample_index'],mean_yaw_old=old['yaw_mean_original'],mean_yaw_new=new['yaw_mean_original'],absolute_error_of_mean_change=abs(new['yaw_mean_original']-new['command_yaw'])-abs(old['yaw_mean_original']-old['command_yaw']),mean_absolute_tracking_error_change=new['yaw_error_absolute_mean']-old['yaw_error_absolute_mean'],old_valid_controls=old['valid_prefix_controls'],new_valid_controls=new['valid_prefix_controls'],reset_truncated_comparison=old['valid_prefix_controls']!=new['valid_prefix_controls']))
 training=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/TARGET_SOURCE_AND_ADMISSION_SNAPSHOTS/runtime/isaac/mod4/retained_flat_command_math.py'
 state=training.with_name('retention_command_state.py');body=training.read_text(encoding='utf8');assert 'yaw=signed*(1+u[:,2])' in body and 'No pure high-rate spin' in body
 manifest=read(W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/left_second_ownsave_actual_1791963199228502100/14_LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json')
 matches=[x for x in manifest['source_freeze'] if x['path'].endswith('/retained_flat_command_math.py')];assert len(matches)==1 and matches[0]['sha256']==sha(training)
 report=dict(epoch=time.time(),trial_id='E3_POSITIVE_4PI_ALL_PREFIX_MOTOR_CONTACT_CPU_20261014',passed_readonly_diagnostic=True,no_SSH_GPU_PPO_budget_candidate_or_production_change=True,baseline=b,candidate=e,paired_changes=comparisons,training_command_source=dict(file=index(training),actual_frozen_manifest_match=matches[0],state_schema=index(state),profile='E1_G3_verified_plane_signed_straight_world05_yaw12_v1',plane_nonstanding_half_signed_straight_abs_vx_1_to1p5_half_world_body_projection_yaw_abs_1_to2=True,plane_world_vx_cos_heading_minus_world_direction_not_pure_spin=True,pure_4pi_training_command_not_in_this_profile=True,complete_all_training_episode_exposure_NOT_proven=True),original_signed_yaw_tolerance_rad_s=.2,thresholds_unmodified=True,legacy_false_and_all_failed_prefix_preserved=True,unique_causality_not_claimed=True)
 out.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(output=str(out),comparisons=comparisons,old_resets=b['all_resets'],new_resets=e['all_resets']),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  f=R/('ORIGINAL_CPU_READER_ERROR_'+str(time.time_ns())+'.json');f.write_text(json.dumps(dict(error=traceback.format_exc(),no_SSH_GPU_PPO=True),indent=2),encoding='utf8');raise
