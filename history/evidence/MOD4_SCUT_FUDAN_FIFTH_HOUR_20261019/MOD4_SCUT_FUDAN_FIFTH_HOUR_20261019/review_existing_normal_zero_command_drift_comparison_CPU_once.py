"""Existing raw only: survival does not establish unchanged normal zero-command behavior."""
from pathlib import Path
import json,time,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'
new=json.loads((R/'FOURTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes());old=json.loads((P/'reports/THIRD_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
def metrics(e):
 a=np.load(e['raw']['path'])['callback'];assert a.shape[1]==46 and np.isfinite(a).all();speed=np.linalg.norm(a[:,13:15],axis=1);dyaw=np.arctan2(np.sin(a[:,36]-a[0,36]),np.cos(a[:,36]-a[0,36]))
 return dict(source_SHA=e['SHA'],survived15s=e['survived15s'],duration_s=e['simulated_s'],final_speed_m_s=float(speed[-1]),last_second_mean_speed_m_s=float(speed[a[:,0]>=14].mean()),final_yaw_drift_rad=float(dyaw[-1]),net_planar_displacement_m=float(np.linalg.norm(a[-1,3:5]-a[0,3:5])),planar_path_length_m=float(np.linalg.norm(np.diff(a[:,3:5],axis=0),axis=1).sum()),raw=e['raw'])
rows=[]
for e in new['episodes']:
 if e['public4_requested']:continue
 prior=next(x for x in old['episodes'] if not x['public4_requested'] and x['yaw']==e['yaw']);n=metrics(e);p=metrics(prior)
 rows.append(dict(yaw=e['yaw'],new=n,previous=p,final_speed_increase_m_s=n['final_speed_m_s']-p['final_speed_m_s']))
out=dict(epoch=time.time(),rows=rows,only_existing_local_raw_read_no_case_replay=True,interpretation='Both normal traces still survive15s, but zero-command final planar speed increases from about.014 to.054m/s. This is a local residual/regression in stopping, alongside yaw drift in both generations. Do not describe these survival results as complete normal nonregression. No statistical, PhysX or unique causal claim.',no_new_threshold_or_training_player_GPU_account_change=True)
with (R/'FOURTH_HOUR_NORMAL_ZERO_COMMAND_DRIFT_COMPARISON_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
