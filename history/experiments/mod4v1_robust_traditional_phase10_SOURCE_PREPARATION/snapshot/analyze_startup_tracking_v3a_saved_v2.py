"""ONE read of fresh V3A saved control stream, 0physics/model/old traces.
Records physical outcome separately from sensor-only future-B eligibility.
"""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parent;case='startup_front065_tracking_v3a_nominal1'
P=R/'results'/case;D=R/'STARTUP_STAND_V3/front_A_saved_analysis001'
def dump(p,x):
    with p.open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
result=json.loads((P/'result.json').read_bytes());assert result['config']['case_id']==case
assert result['config']['controller']==dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=False)
g=json.loads((R/'TALL_ROUGH_BANK_V1/gain_delta0.json').read_bytes())['gain']['q'];target=[g[3],g[3]+g[4],g[5],g[5]+g[6]]
D.mkdir(exist_ok=False);dump(D/'PLAN.json',dict(case_id=case,max_new_control_stream_reads=1,old_raw_physics_model_FK_or_replay=0,
    source_result_SHA=hashlib.sha256((P/'result.json').read_bytes()).hexdigest(),source_trace_producer=result['trace_artifact'],raw_SHA_recomputed=False))
count=0;eligible_times=[];phasecounts={};peaks=[0.]*6;wheelmax=[0.,0.];events=[];lastphase=None;last=None;maxverifyerr=0.;lastverify=None
with (P/'trace.jsonl').open(encoding='utf-8')as f:
    for line in f:
        row=json.loads(line);count+=1;ph=row['phase'];phase=ph['phase'];t=row['command_time_s'];phasecounts[phase]=phasecounts.get(phase,0)+1
        q=row['encoder_q4'];qd=row['encoder_qd4'];err=max(abs(a-b)for a,b in zip(q,target))
        expected=bool(phase=='VERIFY'and err<=.08 and max(abs(v)for v in qd)<=.40)
        actual=ph.get('alignment_candidate_eligible_this_command',False);assert type(actual)is bool and actual==expected,(t,actual,expected)
        if actual:eligible_times.append(t)
        if phase=='VERIFY':maxverifyerr=max(maxverifyerr,err);lastverify=dict(time_s=t,q4=q,q_error_max_rad=err,pitch_est_rad=row['estimated14'][2],wheel_rate2=row['wheel_rate_mean2'])
        for i,v in enumerate(row['requested_tau6']):assert math.isfinite(v);peaks[i]=max(peaks[i],abs(v))
        for i,v in enumerate(row['wheel_rate_mean2']):wheelmax[i]=max(wheelmax[i],abs(v))
        if phase!=lastphase:
            events.append(dict(time_s=t,phase=phase,pitch_est_rad=row['estimated14'][2],pitch_true_POST_rad=row['grade_after']['pitch_true'],rootXYZ_POST=row['grade_after']['xyz'],q4=q,
                final_target_error_max_rad=err,encoder_travel_proxy_m=ph.get('recovery_encoder_travel_m'),eligible=actual))
            lastphase=phase
        last=row
assert count==result['controls']and count>0
assert (last['phase'].get('alignment_candidate_eligible_ever',False))==bool(eligible_times)
passed=result['startup_stand_original_v1_gate'];assert type(passed)is bool
out=dict(status='NEW_PHYSICAL_V3A_SAVED_CONTROL_FACTS_NOT_ANOTHER_TRIAL',case_id=case,complete=result['complete'],stop=result['stop'],
    controls=count,physics_steps=result['physics_steps'],original_gate=passed,controller_fault_reason=result['controller_fault_reason'],
    first_BALANCE_command_s=result['first_BALANCE_command_s'],end_stable_s=result['end_stable_s'],max_stable_s=result['max_stable_s'],
    max_root_xy_displacement_m=result['max_root_xy_displacement_m'],body_height_gain_m=result['body_height_gain_m'],
    final_true_pitch_POST_rad=result['final_grade']['pitch_true'],final_rootXYZ_POST=result['final_grade']['xyz'],phase_counts=phasecounts,events=events,
    max_abs_requested_tau6_Nm=peaks,max_abs_wheel_rate2_rad_s=wheelmax,maximum_VERIFY_final_target_error_rad=maxverifyerr,last_VERIFY=lastverify,
    actual_A_sensor_alignment_eligible_count=len(eligible_times),actual_A_first_sensor_alignment_eligible_s=eligible_times[0]if eligible_times else None,
    future_B_condition_available_but_NOT_launch_permission=bool(not passed and eligible_times),
    future_B_still_requires_separate_freshID_freeze_review_parentapproval=True,
    actual_control_stream_open_count=1,actual_control_rows_read=count,actual_physics_stream_or_old_raw_open_count=0,
    code_or_simulator_execution_or_model_FK_count=0,raw_SHA_recomputed=False,source_trace_producer=result['trace_artifact'])
dump(D/'RESULT.json',out)
md='# Startup V3A — 实际单案结果\n\n'
md+=f"- complete={out['complete']}，stop={out['stop']}，原门={passed}；{count} controls / {out['physics_steps']} physics。\n"
md+=f"- firstBALANCE={out['first_BALANCE_command_s']}s；末稳定={out['end_stable_s']}s；XY最大={out['max_root_xy_displacement_m']:.6f}m；高度增量={out['body_height_gain_m']:.6f}m。\n"
md+=f"- 实际A传感器alignment eligible={len(eligible_times)}帧，首次={out['actual_A_first_sensor_alignment_eligible_s']}s；仅供后续B另行准入，不是接触置信度或自动启动许可。\n"
md+='- 仅此新control stream一次读取；0physics/旧raw读取/大rawhash/模型或重物理。保持原验收门，单nominal TRAIN不是fullDR或可靠性证明。\n'
with (D/'REPORT.md').open('x',encoding='utf-8')as f:f.write(md)
print(json.dumps(out,indent=2,allow_nan=False))
