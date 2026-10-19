"""Original-condition timing on already-saved trajectories; no rerun or causal attribution."""
from pathlib import Path
import json,time,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'MOD4_SCUT_FUDAN_FIFTEENTH_HOUR_20261019'
current=json.loads((R/'FIFTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
previous=json.loads((P/'reports/FOURTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
def inspect(e):
 with np.load(e['raw']['path']) as z:a=z['callback'];b=z['reward_callback']
 rec=np.flatnonzero(a[:,41]);assert len(rec)==1;end=int(rec[0]);start=end-199;assert start>=0
 dyaw=np.arctan2(np.sin(a[:,36]-a[0,36]),np.cos(a[:,36]-a[0,36]))
 checks=dict(both_wheel_support=(a[:,28:30]>1).all(1),nonwheel_clean=a[:,33]<=1,geometry_clear=a[:,32]>=-.001,vertical_speed=np.abs(a[:,15])<=.03,planar_speed=np.linalg.norm(a[:,13:15],axis=1)<=.03,roll=np.abs(a[:,34])<np.pi/18,pitch=np.abs(a[:,35])<np.pi/18,yaw=np.abs(dyaw)<.2)
 landed=b[:,5]>0;stable=landed.copy()
 for x in checks.values():stable &= x
 assert stable[start:end+1].all() and end-start+1==200
 before=landed & (np.arange(len(a))<start);last={}
 for name,mask in checks.items():
  bad=np.flatnonzero(before & ~mask);last[name]=float(a[bad[-1],0]) if len(bad) else None
 nonyaw=landed.copy()
 for name,mask in checks.items():
  if name!='yaw':nonyaw &= mask
 yaw_only=landed & nonyaw & ~checks['yaw'] & (np.arange(len(a))<end)
 first=np.flatnonzero(yaw_only);nonbad=np.flatnonzero(landed & ~nonyaw & (np.arange(len(a))<start))
 return dict(source_SHA=e['SHA'],raw=e['raw'],recovery_event_s=float(a[end,0]),original_200_callback_window=dict(first_s=float(a[start,0]),last_s=float(a[end,0]),callbacks=200,all_original_conditions_true=True),last_failed_original_condition_before_window_s=last,last_non_yaw_failure_before_window_s=float(a[nonbad[-1],0]) if len(nonbad) else None,only_yaw_failed_while_other_conditions_passed_before_event=dict(callbacks=int(yaw_only.sum()),first_s=float(a[first[0],0]) if len(first) else None,last_s=float(a[first[-1],0]) if len(first) else None,callback_count_times_2p5ms_s=float(yaw_only.sum()*.0025)),yaw_error_at_window_start_rad=float(dyaw[start]),yaw_error_at_recovery_rad=float(dyaw[end]))
rows=[]
for e in current['episodes']:
 if not e['public4_requested']:continue
 prior=next(x for x in previous['episodes'] if x['public4_requested'] and x['yaw']==e['yaw'])
 rows.append(dict(yaw=e['yaw'],current=inspect(e),previous=inspect(prior)))
out=dict(epoch=time.time(),rows=rows,interpretation='The last failed condition before the observed original200-callback recovery window is a temporal readout of these trajectories. It does not identify which reward, action or backend difference caused that condition. No request clock, actor input, force, physics or threshold was changed. These are two deterministic local MuJoCo yaws without production20kDR, not PhysX skill qualification or statistical evidence.',read_only_already_saved_raw_no_case_or_GPU_or_player_replay=True,original_sticky_recovered_flag_not_permanent_holding=True)
with (R/'FIFTEENTH_HOUR_DELAYED_RECOVERY_CONDITION_TIMING_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(out,stream,indent=2)
print(json.dumps(dict(rows=rows),indent=2))
