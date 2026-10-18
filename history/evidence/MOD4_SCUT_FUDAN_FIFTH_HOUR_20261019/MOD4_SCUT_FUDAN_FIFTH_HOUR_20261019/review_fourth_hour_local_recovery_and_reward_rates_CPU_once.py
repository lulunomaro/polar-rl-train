"""Read existing new-source trajectories; inspect recovery blockers and measured rates."""
from pathlib import Path
import json,time,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'
v=json.loads((R/'FOURTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
prior=json.loads((P/'reports/THIRD_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
names=list(v['reward_telemetry']['profile']['weights']);rows=[]
def longest(mask):
 best=n=0
 for x in mask:n=n+1 if x else 0;best=max(best,n)
 return best
def snapshot(a,b,i):
 return dict(time_s=float(a[i,0]),control=int(a[i,1]),mode=int(a[i,2]),pitch=float(a[i,35]),roll=float(a[i,34]),planar_speed=float(np.linalg.norm(a[i,13:15])),vz=float(a[i,15]),world_angular_velocity=a[i,10:13].tolist(),body_angular_velocity=b[i,8:11].tolist(),policy_action=a[i,16:22].tolist(),actuator_torque_hip_crank_wheel_left_right=a[i,22:28].tolist(),wheel_support_N=a[i,28:30].tolist(),wheel_clearance=a[i,30:32].tolist(),active=bool(b[i,2]),airborne=bool(b[i,3]),recovery_ticks=int(b[i,7]),weighted_rate=dict(zip(names,b[i,14:].tolist())))
for e in v['episodes']:
 z=np.load(e['raw']['path']);a=z['callback'];b=z['reward_callback'];assert a.shape[1]==46 and b.shape==(len(a),14+len(names)) and np.array_equal(a[:,0],b[:,0]) and np.isfinite(a).all() and np.isfinite(b).all()
 old=next(x for x in prior['episodes'] if x['public4_requested']==e['public4_requested'] and x['yaw']==e['yaw'])
 ev={name:[snapshot(a,b,int(i)) for i in np.flatnonzero(a[:,col])] for name,col in [('takeoff',39),('landing',40),('recovery',41)]}
 ground=(a[:,28:30]>1).all(1)&(a[:,33]<=1)&(a[:,32]>=-.001)
 prepared=ground&(np.abs(a[:,15])<=.2)&(np.linalg.norm(a[:,13:15],axis=1)<=.2)&(np.abs(a[:,34:36])<np.pi/12).all(1)&(a[:,1]<100)
 dyaw=np.arctan2(np.sin(a[:,36]-a[0,36]),np.cos(a[:,36]-a[0,36]))
 checks=dict(both_wheel_support=(a[:,28:30]>1).all(1),nonwheel_clean=a[:,33]<=1,geometry_clear=a[:,32]>=-.001,vertical_speed=np.abs(a[:,15])<=.03,planar_speed=np.linalg.norm(a[:,13:15],axis=1)<=.03,roll=np.abs(a[:,34])<np.pi/18,pitch=np.abs(a[:,35])<np.pi/18,yaw=np.abs(dyaw)<.2)
 landed=b[:,5]>0;stable=landed.copy()
 for good in checks.values():stable &= good
 segments={}
 for label,mask in dict(public4_attempt=(b[:,2]>0),landed_still_public4=landed&(a[:,2]==4),landed_normal=landed&(a[:,2]==0),last_second=a[:,0]>=14).items():
  n=int(mask.sum())
  segments[label]=dict(callbacks=n,failed_recovery_condition_callbacks={k:int((mask&~ok).sum()) for k,ok in checks.items()},all_recovery_conditions_callbacks=int((mask&stable).sum()),pitch_range=[float(a[mask,35].min()),float(a[mask,35].max())] if n else None,planar_speed_max=float(np.linalg.norm(a[mask,13:15],axis=1).max()) if n else None,weighted_rate_mean={name:float(b[mask,14+j].mean()) for j,name in enumerate(names)} if n else None)
 request=(a[:,1]>=100)&(a[:,1]<180);indices={}
 for label,target in [('request_start',1.),('request_end',1.8),('one_second_after_request',2.8),('final',a[-1,0])]:indices[label]=snapshot(a,b,int(np.argmin(np.abs(a[:,0]-target))))
 # Actual phase counter retains all original conditions, including its exact yaw anchor.
 normal=a[:,2]==0;assert np.all(b[normal,14:]==0)
 for j,n in enumerate(names):
  if n in ('flight_vz','flight','leg_tuck','takeoff_extend','orientation','angular_velocity_xy'):assert np.abs(b[:,14+j]).max()<=2.500001
 rows.append(dict(source_SHA=e['SHA'],public4_requested=e['public4_requested'],yaw=e['yaw'],ready_before_request=e['ready_before_request'],prepared_longest_callbacks=longest(prepared),strict_counts=e['counts'],event_callback_rows=ev,survived15s=e['survived15s'],duration_s=e['simulated_s'],first_failure=e['first_failure'],request_both_wheel_min_peak_m=float(a[request,30:32].min(1).max()),actual_phase_recovery_ticks_max=int(a[:,45].max()),original_required_recovery_callbacks=200,longest_readonly_recovery_condition_callbacks=longest(stable),segments=segments,samples=indices,previous_source_SHA=old['SHA'],previous_counts=old['counts'],previous_duration_s=old['simulated_s'],previous_first_failure=old['first_failure'],raw=e['raw']))
out=dict(epoch=time.time(),trial_id='fourth-reward-hour-new-source-local-recovery-and-rate-diagnostic',rows=rows,original_thresholds_and_external_request_clock_unchanged=True,all_normal_rows_new_reward_terms_zero=True,weighted_Fudan_rate_limit_verified=True,rate_evidence='Read-only evaluation of installed formula on current local MuJoCo callback state; not an actual PhysX RewardManager/PPO reward readback. Callback rates are not summed as training return.',no_old_case_replay=True,not_PhysX_or_statistical_or_unique_causal_result=True,no_live_player_GPU_reward_LR_STD_physics_or_budget_change=True)
with (R/'FOURTH_HOUR_LOCAL_RECOVERY_AND_REWARD_RATES_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(jump=[{k:r[k] for k in ('source_SHA','strict_counts','ready_before_request','prepared_longest_callbacks','survived15s','duration_s','request_both_wheel_min_peak_m','actual_phase_recovery_ticks_max','segments')} for r in rows if r['public4_requested']]),indent=2))
