"""Read new R40 TRAIN traces for control/observer failure diagnosis, 0 steps.
No raw SHA rehash, no acceptance rewriting, no old physics replay.
"""
from pathlib import Path
import hashlib,json,math
import numpy as np
R=Path(__file__).resolve().parent
batch=json.loads((R/'batches/r40_world_leg4/BATCH_RESULT.json').read_bytes());cases=[]
for row in batch['rows']:
    name=row['case'];result=json.loads((R/'results'/name/'result.json').read_bytes())
    trace=R/'results'/name/'trace.jsonl';data=[]
    with trace.open(encoding='utf-8')as f:
        for line in f:data.append(json.loads(line))
    assert len(data)==result['controls']
    tail=[r for r in data if r['time']>=max(1.,result['config']['duration_s']-2.)]or data
    pitch_err=np.array([r['estimated14'][2]-r['ground_truth_before']['pitch_true']for r in tail])
    velocity_err=np.array([r['estimated14'][7]-r['ground_truth_before']['body_velocity'][0]for r in tail])
    truep=np.array([r['ground_truth']['pitch_true']for r in tail]);estp=np.array([r['estimated14'][2]for r in tail])
    roll=np.array([r['ground_truth']['roll_true']for r in tail]);wref=np.array([r['shaped'][1]for r in tail])
    failures=[]
    if not result['complete']:failures.append('incomplete_'+result['stop_reason'])
    if not np.all(abs(truep)<math.radians(10)):failures.append('tail_pitch_gt10deg')
    if not np.all(abs(roll)<math.radians(10)):failures.append('tail_roll_gt10deg')
    if not result['tail_v_tracking_RMSE']<.15:failures.append('tail_v_RMSE_ge0p15')
    if not result['tail_w_tracking_RMSE']<.1*max(1.,float(abs(wref).max())):failures.append('tail_yaw_RMSE')
    if not result['impulse_support_gate']:failures.append('tail_wheel_impulse_support')
    if result['physics_nonwheel_contact_ticks']!=0:failures.append('nonwheel_contact')
    if result['rough_progress_m']<6.5:failures.append('progress_lt6p5')
    if result['rough_max_y_m']>.3:failures.append('lateral_gt0p3')
    if data[-1]['ground_truth']['xyz'][0]>=8.8:failures.append('finite_ground_exit')
    if result['max_closure']>.01 or result['max_mimic']>.01:failures.append('closure_or_mimic')
    assert bool(not failures)==result['rough_case_pass'],(name,failures)
    delta=result['config']['gain_file'].split('gain_delta')[-1].split('.')[0]
    height=round(result['scene']['actual_bar_height_m']*1000)
    base=f'r22_height{delta}bar{height}'
    old=json.loads((R/'results'/base/'result.json').read_bytes())
    last=data[-1]
    cases.append(dict(case=name,existing_baseline=base,new_physics_steps=result['physics_callbacks'],complete=result['complete'],passed=result['rough_case_pass'],unchanged_gate_failures=failures,
        baseline_progress_m=old['rough_progress_m'],new_progress_m=result['rough_progress_m'],baseline_nonwheel=old['physics_nonwheel_contact_ticks'],new_nonwheel=result['physics_nonwheel_contact_ticks'],
        tail_pitch_true_range_rad=[float(truep.min()),float(truep.max())],tail_pitch_est_range_rad=[float(estp.min()),float(estp.max())],
        tail_pitch_error_RMS_rad=float(np.sqrt(np.mean(pitch_err*pitch_err))),tail_pitch_error_mean_rad=float(pitch_err.mean()),
        tail_forward_error_RMS_m_s=float(np.sqrt(np.mean(velocity_err*velocity_err))),
        final=dict(time=last['time'],true_pitch=last['ground_truth']['pitch_true'],estimated_pitch=last['estimated14'][2],true_v=last['ground_truth']['body_velocity'][0],estimated_v=last['estimated14'][7],world_reference=last['world_leg_reference'],gyro_mean=last['raw_gyro'],proper_mean=last['raw_accel'],wheel_rate_mean=last['wheel_rate2'],joint_rate_mean=last['encoder_rate4']),
        raw_reference=result['trace_artifact'],raw_read_for_new_diagnosis_not_archive_rehash=True))
report=dict(kind='R40_WORLDLEG_NEW_TRAIN_FACTS_AND_OBSERVER_DIAGNOSTIC',source_analysis_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    executed_cases=len(cases),completed=sum(r['complete']for r in cases),original_screen_pass=sum(r['passed']for r in cases),
    actual_new_physics_steps_already_executed=sum(r['new_physics_steps']for r in cases),new_physics_steps_during_analysis=0,all_once_preserved=True,cases=cases)
with(R/'reports/R40_WORLDLEG_FACTS.json').open('x',encoding='utf-8')as f:json.dump(report,f,indent=2,allow_nan=False)
print(json.dumps(report,indent=2))
