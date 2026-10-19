"""Read only new and already-saved prior local trajectories; do not replay a case."""
from pathlib import Path
import json,time,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';K=B.parent/'MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019'
new=json.loads((R/'TWELFTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
old=json.loads((K/'reports/TENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())
def read(e):
 with np.load(e['raw']['path']) as z:a=z['callback'];b=z['reward_callback'];c=z['actuator_readback']
 assert a.shape[1]==46 and b.shape==(len(a),23) and c.shape==(len(a),14)
 tail=a[:,0]>=14;assert tail.any() and np.array_equal(a[:,0],b[:,0]) and np.array_equal(a[:,0],c[:,0])
 assert np.all(np.isfinite(a)) and np.all(np.isfinite(b)) and np.all(np.isfinite(c))
 dyaw=np.arctan2(np.sin(a[:,36]-a[0,36]),np.cos(a[:,36]-a[0,36]))
 return dict(source_SHA=e['SHA'],raw=e['raw'],survived15s=e['survived15s'],strict_counts=e['counts'],last_second=dict(callbacks=int(tail.sum()),yaw_growth_rad=float(dyaw[-1]-dyaw[np.flatnonzero(tail)[0]]),mean_world_yaw_rate_rad_s=float(a[tail,12].mean()),mean_body_yaw_rate_rad_s=float(b[tail,10].mean()),mean_planar_speed_m_s=float(np.linalg.norm(a[tail,13:15],axis=1).mean()),mean_policy_action6=a[tail,16:22].mean(0).tolist(),action_at_abs_clip6_fraction_per_channel=(np.abs(a[tail,16:22])>=6-1e-7).mean(0).tolist(),actual_wheel_actuator_force_mean_indices2_5=c[tail][:,[10,13]].mean(0).tolist(),actual_wheel_actuator_force_RMS_indices2_5=np.sqrt(np.square(c[tail][:,[10,13]]).mean(0)).tolist(),extra_nine_formula_rates_zero=bool(np.all(b[tail,14:]==0))),actual_ctrl_force_max_abs_difference=float(np.abs(c[:,2:8]-c[:,8:14]).max()))
rows=[]
for e in new['episodes']:
 previous=next(x for x in old['episodes'] if x['yaw']==e['yaw'] and x['public4_requested']==e['public4_requested'])
 rows.append(dict(public4_requested=e['public4_requested'],yaw=e['yaw'],current=read(e),previous=read(previous)))
out=dict(epoch=time.time(),rows=rows,normal_and_post_request_extra_terms_zero_is_expected_original_scope=True,actuator_order='Local MuJoCo hip/crank/wheel per side; actual d.actuator_force wheel channels2,5. Signed values retain original joint-axis convention, not a world yaw moment.',read_only_original_raw_comparison_no_case_replay=True,retained_yaw_rate_vs_accumulated_heading_source_audit=str(B.parent/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/reports/NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json'),interpretation='Late local yaw growth and clipped actor channels are observations. Their coexistence does not establish which reward, actuator or backend difference caused drift. Rates are local formula diagnostics, not production RewardManager/PPO returns or PhysX torque readback. Two yaw variants without production20kDR do not establish statistical significance, PhysX skill qualification or complete normal nonregression.',no_live_player_remote_GPU_reward_LR_STD_physics_threshold_or_budget_change=True)
with (R/'TWELFTH_HOUR_LATE_YAW_ACTION_ACTUATOR_RESIDUAL_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(out,stream,indent=2)
print(json.dumps(dict(rows=[dict(requested=x['public4_requested'],yaw=x['yaw'],current_tail=x['current']['last_second'],previous_tail=x['previous']['last_second']) for x in rows]),indent=2))
