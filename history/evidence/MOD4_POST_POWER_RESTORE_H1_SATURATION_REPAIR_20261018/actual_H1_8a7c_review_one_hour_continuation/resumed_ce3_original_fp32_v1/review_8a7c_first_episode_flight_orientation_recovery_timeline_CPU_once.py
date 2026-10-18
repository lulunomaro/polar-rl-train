"""Readonly original first-episode temporal residuals; no new gate or GPU experiment."""
from pathlib import Path
import os,json,time,hashlib,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'frozen_ce3_original_fp32_continued_final_linux_v1/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def longest(mask):
 current=maximum=0
 for value in mask:
  current=current+1 if value else 0;maximum=max(maximum,current)
 return int(maximum)

def event_before_failure(values,end):
 ids=np.flatnonzero(values[:end]);return int(ids[0]) if len(ids) else None

def summary(values):
 return [float(np.min(values)),float(np.median(values)),float(np.max(values))] if len(values) else None

def main():
 collection=R/'LINUX_GPU1_CR3FINAL_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json';j=json.loads(collection.read_bytes());cpu=R/'H1_CR3FINAL_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json';audit=json.loads(cpu.read_bytes());assert audit['passed_complete_data_and_source_CPU'] and audit['source_SHA']=='8a7c730d97acf9db8e4ab2f89390fd9302bdf4b9186eee3c92ae287d2a199bc2'
 raw=next(x for x in j['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'));probe=json.loads(Path(next(x['local_path'] for x in j['files'] if x['relative'].endswith('/probe.json'))).read_bytes());names=probe['native_readonly_witness']['reason_names'];assert raw['twohost_complete_SHA']
 needed=['terminated','truncated','reasons','H1_public_request','H1_phase_yaw_reference','H1_phase_landed','H1_phase_recover_ticks','substep_H1_takeoff','substep_H1_landing','substep_H1_recovery','substep_H1_root13','substep_H1_roll','substep_H1_pitch','substep_H1_wheel_norm_N','substep_H1_nonwheel_max','substep_H1_all34_clearance','substep_H1_wheel_clearance','processed_action','substep_actual_applied_effort','substep_torque_speed_lower','substep_torque_speed_upper']
 with np.load(raw['local_path'],allow_pickle=False) as z:a={k:z[k] for k in needed}
 done=a['terminated']|a['truncated'];S,N=done.shape;assert (S,N)==(1500,80);first=np.where(done.any(0),done.argmax(0),S);root=a['substep_H1_root13'].astype(np.float64);x,y,z,w=np.moveaxis(root[...,3:7],-1,0)
 roll=np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y));pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1));yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z));yawref=np.repeat(a['H1_phase_yaw_reference'],4,axis=0);dyaw=np.arctan2(np.sin(yaw-yawref),np.cos(yaw-yawref));quatnorm=float(abs((root[...,3:7]**2).sum(-1)-1).max());assert quatnorm<1e-5
 valid=np.arange(S)[:,None]<first[None,:];pv=np.repeat(valid,4,axis=0);roll_error=float(abs(roll[pv]-a['substep_H1_roll'][pv]).max());pitch_error=float(abs(pitch[pv]-a['substep_H1_pitch'][pv]).max());assert max(roll_error,pitch_error)<1e-6
 tree=ast.parse((Q/'h1_public_request_phase_v1.py').read_text('utf8'));node=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROFILE' for t in n.targets));assert isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='dict' and not node.args and all(k.arg is not None for k in node.keywords);profile={k.arg:ast.literal_eval(k.value) for k in node.keywords}
 assert profile['recovery_ticks']==200 and profile['recovery_speed_m_s']==.03 and profile['recovery_tilt_rad']==.17453292519943295 and profile['recovery_yaw_rad']==.2
 ground=(a['substep_H1_wheel_norm_N']>1).all(-1)&(a['substep_H1_nonwheel_max']<=1)&(a['substep_H1_all34_clearance'].min(-1)>=-.001)
 factors=dict(ground=ground,root_vz_abs_at_most03=abs(root[...,9])<=.03,planar_speed_at_most03=np.linalg.norm(root[...,7:9],axis=-1)<=.03,roll_abs_under10deg=abs(roll)<profile['recovery_tilt_rad'],pitch_abs_under10deg=abs(pitch)<profile['recovery_tilt_rad'],yaw_from_original_anchor_under02=abs(dyaw)<.2)
 rows=[];groups={'takeoff_then_orientation_before_landing':[],'takeoff_landing_then_orientation':[],'takeoff_no_first_orientation_failure':[],'orientation_without_takeoff':[],'other':[]};landedrows=[]
 for env,endcontrol in enumerate(first):
  end=int(endcontrol)*4;take=event_before_failure(a['substep_H1_takeoff'][:,env],end);land=event_before_failure(a['substep_H1_landing'][:,env],end);recover=event_before_failure(a['substep_H1_recovery'][:,env],end);reasons=[n for i,n in enumerate(names) if endcontrol<S and a['reasons'][endcontrol,env,i]];bad='bad_orientation' in reasons
  group=('takeoff_landing_then_orientation' if land is not None else 'takeoff_then_orientation_before_landing') if take is not None and bad else ('takeoff_no_first_orientation_failure' if take is not None else ('orientation_without_takeoff' if bad else 'other'));groups[group].append(env)
  checkpoints={}
  for label,k in [('pre_takeoff20ms',take-8 if take is not None and take>=8 else None),('takeoff',take),('takeoff_plus40ms',take+16 if take is not None and take+16<end else None),('landing',land),('last_valid_callback',end-1 if end else None)]:
   if k is None:continue
   checkpoints[label]=dict(callback=int(k),time_s=float((k+1)*.0025),roll_rad=float(roll[k,env]),pitch_rad=float(pitch[k,env]),root_angular_speed_world_norm=float(np.linalg.norm(root[k,env,10:13])),root_planar_speed=float(np.linalg.norm(root[k,env,7:9])),root_vz=float(root[k,env,9]),wheel_force_N=a['substep_H1_wheel_norm_N'][k,env].tolist(),wheel_clearance_m=a['substep_H1_wheel_clearance'][k,env].tolist(),actual_clipped_action=a['processed_action'][k//4,env].tolist(),actual_applied_effort=a['substep_actual_applied_effort'][k,env].tolist())
  failureshape=None
  if endcontrol<S:
   k=int(endcontrol)*4+3;failureshape=dict(roll_rad=float(roll[k,env]),pitch_rad=float(pitch[k,env]),dominant_Euler_axis='pitch' if abs(pitch[k,env])>=abs(roll[k,env]) else 'roll',world_angular_speed_norm=float(np.linalg.norm(root[k,env,10:13])),not_actual_loaded_SDK_termination_formula_proof=True)
  recovery_diag=None
  if land is not None:
   start=land;mask=np.arange(4*S)>=start;mask&=np.arange(4*S)<end;allgood=np.logical_and.reduce([v[:,env] for v in factors.values()]);runs={name:longest(v[:,env]&mask) for name,v in factors.items()};failcounts={name:int((mask&~v[:,env]).sum()) for name,v in factors.items()};recovery_diag=dict(valid_callbacks_after_landing=int(mask.sum()),all_original_stable_factors_longest_run=longest(allgood&mask),original_saved_recover_ticks_max=int(a['H1_phase_recover_ticks'][:endcontrol,env].max()) if endcontrol else 0,factor_individual_longest_runs=runs,factor_failed_callback_counts=failcounts,none_of_these_single_factor_counts_waives_any_original_gate=True);landedrows.append(dict(environment=env,**recovery_diag))
  rows.append(dict(environment=env,valid_first_episode_controls=int(endcontrol),takeoff_callback=take,landing_callback=land,recovery_callback=recover,first_failure_reasons=reasons,group=group,time_from_takeoff_to_first_failure_s=float(endcontrol*.01-(take+1)*.0025) if take is not None and endcontrol<S else None,checkpoints=checkpoints,failed_control_pose=failureshape,recovery_diagnostic=recovery_diag))
 take_rows=[r for r in rows if r['takeoff_callback'] is not None];badrows=[r for r in rows if 'bad_orientation' in r['first_failure_reasons']];axis={k:sum(r['failed_control_pose']['dominant_Euler_axis']==k for r in badrows) for k in ('roll','pitch')}
 assert len(rows)==80 and len(take_rows)==audit['first_episode_before_failed_control_events']['takeoff'] and len(landedrows)==audit['first_episode_before_failed_control_events']['landing'] and sum(r['recovery_callback'] is not None for r in rows)==audit['first_episode_before_failed_control_events']['recovery']
 # Valid-prefix fixtures: events on or after a failed control are never accepted.
 fixture=np.array([False,False,True,True]);assert event_before_failure(fixture,2) is None and event_before_failure(fixture,3)==2 and longest([True,True,False,True])==2
 summary_out=dict(group_counts={k:len(v) for k,v in groups.items()},orientation_first_failure_dominant_Euler_axis_counts=axis,takeoff_root_angular_speed_norm_min_median_max=summary([r['checkpoints']['takeoff']['root_angular_speed_world_norm'] for r in take_rows]),takeoff_pitch_abs_min_median_max_rad=summary([abs(r['checkpoints']['takeoff']['pitch_rad']) for r in take_rows]),orientation_failure_time_after_takeoff_min_median_max_s=summary([r['time_from_takeoff_to_first_failure_s'] for r in take_rows if r['time_from_takeoff_to_first_failure_s'] is not None]),landed_recovery_allfactor_longest_runs=[r['all_original_stable_factors_longest_run'] for r in landedrows],landed_recovery_factor_failure_callbacks_total={k:sum(r['factor_failed_callback_counts'][k] for r in landedrows) for k in factors})
 out=dict(epoch=time.time(),trial_id='h1-8a7c-firstepisode-flight-orientation-recovery-timeline-cpu-20261018',source_SHA=audit['source_SHA'],actual_full_raw_index=raw,whole_data_reference_CPU_proof=str(cpu),whole_data_reference_CPU_proof_SHA=H(cpu),original_actor_reference_FP32_fixed120000_same1e4=True,prior_ce3_FP32_false_and_FP64_separate_reports_retained=True,source_physics_observer=dict(path=str(Q/'frozen_shared/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py'),SHA=H(Q/'frozen_shared/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py')),source_phase=dict(path=str(Q/'h1_public_request_phase_v1.py'),SHA=H(Q/'h1_public_request_phase_v1.py'),profile=profile),independent_XYZW_root_Euler_valid_prefix_maxabs=dict(roll=roll_error,pitch=pitch_error,unit_quaternion_norm=quatnorm),summary=summary_out,per_group_environment_ids=groups,per_environment=rows,original_valid_prefix_and_stable200_conditions_unchanged=True,no_angular_velocity_condition_in_original_H1_recovery_gate_angular_speed_is_diagnostic_only=True,no_single_cause_or_closedloop_counterfactual_or_new_skill_PASS=True,no_GPU_RNG_optimizer_new_paid_window_or_source_change=True,initial_lookup_missing_top_level_environment_path_corrected_to_manifest_runtime_path=True)
 with (R/'H1_8A7C_FIRST_EPISODE_FLIGHT_ORIENTATION_RECOVERY_TIMELINE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(summary_out))

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_8A7C_TIMELINE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_trajectory_replay=True),f,indent=2)
  raise
