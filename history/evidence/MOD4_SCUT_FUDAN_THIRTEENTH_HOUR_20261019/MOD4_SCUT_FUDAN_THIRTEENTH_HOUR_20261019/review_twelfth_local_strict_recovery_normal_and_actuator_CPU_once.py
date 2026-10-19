"""Existing new-source raw only: strict events, late recovery residuals and actual local force."""
from pathlib import Path
import json,time,hashlib,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019'
v=json.loads((R/'TWELFTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes());old=json.loads((P/'reports/TENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes());names=list(v['reward_telemetry']['profile']['weights']);rows=[]
def longest(mask):
 best=n=0
 for x in mask:n=n+1 if x else 0;best=max(best,n)
 return best
def point(a,b,c,i):
 dyaw=np.arctan2(np.sin(a[i,36]-a[0,36]),np.cos(a[i,36]-a[0,36]))
 return dict(time_s=float(a[i,0]),control=int(a[i,1]),mode=int(a[i,2]),pitch=float(a[i,35]),roll=float(a[i,34]),yaw_error_rad=float(dyaw),planar_speed_m_s=float(np.linalg.norm(a[i,13:15])),vz_m_s=float(a[i,15]),world_angular_velocity=a[i,10:13].tolist(),body_angular_velocity=b[i,8:11].tolist(),policy_action=a[i,16:22].tolist(),sent_d_ctrl_hip_crank_wheel_left_right=c[i,2:8].tolist(),actual_d_actuator_force_hip_crank_wheel_left_right=c[i,8:14].tolist(),wheel_support_N=a[i,28:30].tolist(),wheel_clear_m=a[i,30:32].tolist(),active=bool(b[i,2]),airborne=bool(b[i,3]),recover_ticks=int(b[i,7]),weighted_rate=dict(zip(names,b[i,14:].tolist())))
def normal_metrics(e):
 a=np.load(e['raw']['path'])['callback'];speed=np.linalg.norm(a[:,13:15],axis=1);yaw=np.arctan2(np.sin(a[-1,36]-a[0,36]),np.cos(a[-1,36]-a[0,36]))
 return dict(source_SHA=e['SHA'],survived15s=e['survived15s'],final_speed_m_s=float(speed[-1]),last_second_mean_speed_m_s=float(speed[a[:,0]>=14].mean()),final_yaw_drift_rad=float(yaw),net_planar_displacement_m=float(np.linalg.norm(a[-1,3:5]-a[0,3:5])),raw=e['raw'])
for e in v['episodes']:
 z=np.load(e['raw']['path']);a=z['callback'];b=z['reward_callback'];c=z['actuator_readback'];assert a.shape[1]==46 and b.shape==(len(a),23) and c.shape==(len(a),14);assert np.array_equal(a[:,0],b[:,0]) and np.array_equal(a[:,0],c[:,0]) and np.array_equal(a[:,22:28],c[:,2:8]);assert all(np.isfinite(q).all() for q in (a,b,c))
 prior=next(x for x in old['episodes'] if x['public4_requested']==e['public4_requested'] and x['yaw']==e['yaw']);events={}
 for name,col in [('takeoff',39),('landing',40),('recovery',41)]:
  inds=np.flatnonzero(a[:,col]);assert len(inds)==e['counts'][name];events[name]=[point(a,b,c,int(i)) for i in inds]
 dyaw=np.arctan2(np.sin(a[:,36]-a[0,36]),np.cos(a[:,36]-a[0,36]));checks=dict(both_wheel_support=(a[:,28:30]>1).all(1),nonwheel_clean=a[:,33]<=1,geometry_clear=a[:,32]>=-.001,vertical_speed=np.abs(a[:,15])<=.03,planar_speed=np.linalg.norm(a[:,13:15],axis=1)<=.03,roll=np.abs(a[:,34])<np.pi/18,pitch=np.abs(a[:,35])<np.pi/18,yaw=np.abs(dyaw)<.2)
 ground=checks['both_wheel_support']&checks['nonwheel_clean']&checks['geometry_clear'];prepared=ground&(np.abs(a[:,15])<=.2)&(np.linalg.norm(a[:,13:15],axis=1)<=.2)&(np.abs(a[:,34:36])<np.pi/12).all(1)&(a[:,1]<100)
 landed=b[:,5]>0;stable=landed.copy()
 for good in checks.values():stable &= good
 segment={}
 for name,mask in dict(public4_attempt=b[:,2]>0,landed_still_public4=landed&(a[:,2]==4),landed_normal=landed&(a[:,2]==0),after_recovery_event=b[:,6]>0,last_second=a[:,0]>=14).items():
  n=int(mask.sum());segment[name]=dict(callbacks=n,failed_original_recovery_conditions={k:int((mask&~q).sum()) for k,q in checks.items()},all_conditions_callbacks=int((mask&stable).sum()),weighted_rate_mean={k:float(b[mask,14+j].mean()) for j,k in enumerate(names)} if n else None)
 assert np.all(b[a[:,2]==0,14:]==0)
 for j,name in enumerate(names):
  if name in ('flight_vz','flight','leg_tuck','takeoff_extend','orientation','angular_velocity_xy'):assert abs(b[:,14+j]).max()<=2.500001
 request=(a[:,1]>=100)&(a[:,1]<180)
 rows.append(dict(source_SHA=e['SHA'],public4_requested=e['public4_requested'],yaw=e['yaw'],ready_before_request=e['ready_before_request'],prepared_longest_callbacks=longest(prepared),strict_counts=e['counts'],event_callback_rows=events,survived15s=e['survived15s'],duration_s=e['simulated_s'],first_failure=e['first_failure'],request_both_wheel_min_peak_m=float(a[request,30:32].min(1).max()),actual_phase_recovery_ticks_max=int(a[:,45].max()),original_required_recovery_callbacks=200,longest_readonly_recovery_condition_callbacks=longest(stable),final_state=point(a,b,c,len(a)-1),segments=segment,actual_local_actuator_force_max_abs=np.abs(c[:,8:14]).max(0).tolist(),command_minus_actual_local_force_max_abs=np.abs(c[:,2:8]-c[:,8:14]).max(0).tolist(),previous_source_SHA=prior['SHA'],previous_strict_counts=prior['counts'],previous_duration_s=prior['simulated_s'],normal_comparison=dict(current=normal_metrics(e),previous=normal_metrics(prior)) if not e['public4_requested'] else None,raw=e['raw']))
p=B/'review_twelfth_reward_hour_new_source_local_behavior_once.py';actual=p.read_bytes();declared=json.loads((R/'TWELFTH_CLOSED_SOURCE_LOCAL_DIAGNOSTIC_PREPARED_CPU_ACTUAL.json').read_bytes())['new_script_SHA'];normalized=hashlib.sha256(p.read_text('utf8').encode()).hexdigest();assert declared==hashlib.sha256(actual).hexdigest()
out=dict(epoch=time.time(),trial_id='twelfth-reward-hour-new-source-local-strict-recovery-review',rows=rows,source_script_actual_bytes=dict(path=str(p),bytes=len(actual),SHA=hashlib.sha256(actual).hexdigest()),prepared_report_SHA_clarification=dict(original_field=declared,field_is_LF_normalized_source_text_SHA=False,field_is_actual_file_bytes_SHA=True,actual_file_byte_SHA=hashlib.sha256(actual).hexdigest(),original_report_and_source_retained=True,no_GPU_or_case_replay=True),actual_local_d_actuator_force_readback=True,original_phase_thresholds_and_external_request_clock_unchanged=True,all_normal_extra_reward_rates_zero=True,Fudan_weighted_rate_clip_verified=True,no_old_case_replay=True,rate_limit='Read-only formula rates on current local MuJoCo states and actual local actuator force; not a PhysX applied_torque or RewardManager/PPO return. Prior command-only telemetry remains retained.',interpretation='Use original phase-event counts and late-condition residuals separately: one recovery event does not prove sustained station keeping, statistical success, PhysX qualification or course graduation. Two yaw variants are deterministic small-sample diagnostics under a different backend without original20kDR.',no_live_player_GPU_optimizer_reward_LR_STD_physics_CAD_guard_or_budget_change=True)
with (R/'TWELFTH_HOUR_LOCAL_STRICT_RECOVERY_NORMAL_AND_ACTUATOR_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(source_file_actual_SHA=out['source_script_actual_bytes']['SHA'],rows=[{k:x[k] for k in ('public4_requested','yaw','strict_counts','ready_before_request','prepared_longest_callbacks','request_both_wheel_min_peak_m','actual_phase_recovery_ticks_max','final_state','normal_comparison')} for x in rows]),indent=2))
