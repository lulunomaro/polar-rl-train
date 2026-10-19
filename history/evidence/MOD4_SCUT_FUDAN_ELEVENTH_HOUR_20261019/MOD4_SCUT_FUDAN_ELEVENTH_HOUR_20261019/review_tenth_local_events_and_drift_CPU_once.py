"""Summarize newly produced raw trajectories; old raw is read only for comparison."""
from pathlib import Path
import json,time,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019'
v=json.loads((R/'TENTH_HOUR_LOCAL_STRICT_RECOVERY_NORMAL_AND_ACTUATOR_CPU_ACTUAL.json').read_bytes())
old=json.loads((P/'reports/NINTH_HOUR_LOCAL_EVENTS_AND_DRIFT_CPU_ACTUAL.json').read_bytes())
rows=[]
for x in v['rows']:
    a=np.load(x['raw']['path'])['callback'];dyaw=np.arctan2(np.sin(a[:,36]-a[0,36]),np.cos(a[:,36]-a[0,36]))
    events={k:[z['time_s'] for z in values] for k,values in x['event_callback_rows'].items()}
    rec=events['recovery'];late=np.flatnonzero((a[:,0]>=rec[0])&(np.abs(dyaw)>=.2)) if rec else []
    prior=next(z for z in old['rows'] if z['public4_requested']==x['public4_requested'] and z['yaw']==x['yaw'])
    rows.append(dict(source_SHA=x['source_SHA'],public4_requested=x['public4_requested'],yaw=x['yaw'],
        strict_counts=x['strict_counts'],event_times_s=events,survived15s=x['survived15s'],duration_s=x['duration_s'],first_failure=x['first_failure'],
        peak_both_wheel_min_clearance_m=x['request_both_wheel_min_peak_m'],prepared_longest_callbacks=x['prepared_longest_callbacks'],
        actual_phase_recovery_ticks_max=x['actual_phase_recovery_ticks_max'],first_after_recovery_yaw_condition_breach_s=float(a[late[0],0]) if len(late) else None,
        previous_after_recovery_yaw_condition_breach_s=prior['first_after_recovery_yaw_condition_breach_s'],
        final_yaw_error_rad=float(dyaw[-1]),previous_final_yaw_error_rad=prior['final_yaw_error_rad'],
        final_planar_speed_m_s=x['final_state']['planar_speed_m_s'],previous_final_planar_speed_m_s=prior['final_planar_speed_m_s'],
        command_actual_force_max_abs_difference=x['command_minus_actual_local_force_max_abs'],normal_comparison=x['normal_comparison'],raw=x['raw']))
out=dict(epoch=time.time(),rows=rows,interpretation='Compare each observed event, duration, clearance and late yaw/speed/displacement separately. A sticky recovery event does not establish continuous holding. These are four deterministic local MuJoCo trajectories under a different backend without the production20kDR, not PhysX qualification, statistical significance, unique reward causality or complete normal nonregression.',original_physics_control_request_clock_and_thresholds_unchanged=True,no_old_case_replay_or_live_player_GPU_account_change=True,retained_original_yaw_objective_source_audit=str(B.parent/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/reports/NORMAL_YAW_RATE_SOURCE_OBJECTIVE_CPU_ACTUAL.json'))
with (R/'TENTH_HOUR_LOCAL_EVENTS_AND_DRIFT_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(out,stream,indent=2)
print(json.dumps(dict(rows=[{k:x[k] for k in ('public4_requested','yaw','strict_counts','event_times_s','survived15s','first_failure','peak_both_wheel_min_clearance_m','actual_phase_recovery_ticks_max','first_after_recovery_yaw_condition_breach_s','final_yaw_error_rad','final_planar_speed_m_s','normal_comparison')} for x in rows]),indent=2))
