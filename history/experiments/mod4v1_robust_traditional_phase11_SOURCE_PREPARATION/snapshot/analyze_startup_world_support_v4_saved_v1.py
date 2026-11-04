"""One fresh V4 control-stream read; no physics stream, model, solver, replay or raw hashing."""
from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parent;CASE='startup_front065_world_support_v4_nominal1'
P=R/'results'/CASE;D=R/'STARTUP_STAND_V4/front_saved_analysis001'
def dump(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
result_bytes=(P/'result.json').read_bytes();res=json.loads(result_bytes)
assert res['config']['case_id']==CASE and res['controls']==193 and res['physics_steps']==3860
assert res['config']['controller']['support_geometry_enable'] is True
assert res['startup_stand_original_v1_gate'] is False and res['complete'] is False
D.mkdir(exist_ok=False)
dump(D/'PLAN.json',dict(one_NEW_control_stream_open_limit=1,maximum_rows=193,old_raw_physics_stream_model_FK_QA_replay=0,
    no_raw_SHA=True,case_id=CASE,source_result_SHA=hashlib.sha256(result_bytes).hexdigest(),source_trace_producer=res['trace_artifact']))
N=0;events={};seen=set();phases={};peaks=[0.]*6;wmax=[0.,0.];pmax=0.;emax=0.;both=quiet=joint=0;previous=None;last=None
def event(row,tag):
    t=row['command_time_s']
    if t not in events:
        events[t]=dict(time_PRE_s=t,time_POST_s=row['root_post_s'],tags=[],phase=row['phase']['phase'],
            pitch_est_rad=row['estimated14'][2],pitch_rate_est_rad_s=row['estimated14'][9],pitch_true_POST_rad=row['grade_after']['pitch_true'],
            rootXYZ_POST_m=row['grade_after']['xyz'],body_velocity_POST=row['grade_after']['body_velocity'],
            q4=row['encoder_q4'],qd4=row['encoder_qd4'],wheel_rate2=row['wheel_rate_mean2'],
            requested_tau6=row['requested_tau6'],actual_applied_tau='NOT_IN_THIS_CONTROL_STREAM_DO_NOT_INFER_CLIPPING',
            main_mean_N2=row['main_contact_mean_N2'],main_min_N2=row['main_contact_min_N2'],
            both_main_every20=row['both_support_every_2k_sample'],no_other_every20=row['no_other_contact_in_control'],
            sensor_time_s=row['sensor_time_s'],sensor_age_s=row['sensor_age_s'],controller_log=row['phase'])
    events[t]['tags'].append(tag)
with (P/'trace.jsonl').open(encoding='utf-8')as f:
    for line in f:
        row=json.loads(line);N+=1;assert N<=193
        t=row['command_time_s'];ph=row['phase']['phase'];g=row['grade_after'];last=row
        assert abs(t-(N-1)*.01)<1e-9
        phases[ph]=phases.get(ph,0)+1
        b=row['both_support_every_2k_sample'];q=row['no_other_contact_in_control'];assert type(b)is type(q)is bool
        both+=b;quiet+=q;joint+=b and q
        for i,x in enumerate(row['requested_tau6']):assert math.isfinite(x);peaks[i]=max(peaks[i],abs(x))
        for i,x in enumerate(row['wheel_rate_mean2']):wmax[i]=max(wmax[i],abs(x))
        pmax=max(pmax,abs(g['pitch_true']));emax=max(emax,abs(row['estimated14'][2]-g['pitch_true']))
        if ph!=previous:event(row,'phase_transition');previous=ph
        tests=[('first_both_main_all20',b),('first_no_guide_or_hard_all20',q),('first_both_and_no_other_all20',b and q)]
        tests += [(f'first_true_abs_pitch_ge_{thr}',abs(g['pitch_true'])>=thr)for thr in(.6,.8,.95)]
        for tag,condition in tests:
            if condition and tag not in seen:seen.add(tag);event(row,tag)
assert N==res['controls'];event(last,'last_command');assert len(events)<=12
# Persist the bounded numeric record before any report formatting.
out=dict(status='SAVED_NEW_V4_PHYSICAL_FACTS_NOT_ANOTHER_TRIAL',case_id=CASE,controls=N,physics_steps=res['physics_steps'],phase_counts=phases,
    complete=res['complete'],stop=res['stop'],fault=res['controller_fault_reason'],original_gate=False,
    max_true_abs_pitch_POST_rad=pmax,max_abs_estimate_minus_POST_pitch_rad=emax,
    max_requested_tau6_Nm=peaks,max_wheel_rate2_rad_s=wmax,
    bins_both_main_all20=both,bins_no_guide_or_hard_all20=quiet,bins_both_and_no_other_all20=joint,
    physical_support_interval_statement='20 discrete2kHz samples per 100Hz bin; this is private grading, not a controller support detector or continuous contact proof',
    first_BALANCE_command_s=res['first_BALANCE_command_s'],capture_eligible_ever=res['support_capture_eligible_ever'],
    final_true_pitch_POST_rad=res['final_grade']['pitch_true'],final_rootXYZ_POST_m=res['final_grade']['xyz'],
    body_height_gain_m=res['body_height_gain_m'],max_root_xy_displacement_m=res['max_root_xy_displacement_m'],
    guide_ticks_whole=res['guide_contact_ticks_whole_episode'],hard_ticks_whole=res['hard_contact_ticks_whole_episode'],
    events=list(events.values()),read_counts=dict(new_control_stream_opens=1,new_control_rows=N,old_raw_opens=0,physics_stream_opens=0,raw_SHA=0,model_FK_PHY_QA_compile_Git=0),
    source_result_SHA=hashlib.sha256(result_bytes).hexdigest(),source_trace_producer=res['trace_artifact'],
    no_causal_uniqueness_or_actual_torque_or_slip_or_force_identity_claim=True)
dump(D/'RESULT_MIN.json',out)
md='# V4 首案：实际起立失效，单次已存传感流诊断\n\n'
md+=f'- {N} controls / {res["physics_steps"]} physics；complete=False，原门=False；{out["fault"]}。\n'
md+=f'- phase={phases}；未到CAPTURE/RETURN/VERIFY/BLEND/BALANCE；sensor capture eligible={out["capture_eligible_ever"]}。\n'
md+=f'- 末真实pitch={out["final_true_pitch_POST_rad"]:.9f}rad；rootZ={out["final_rootXYZ_POST_m"][2]:.9f}m，高度增量={out["body_height_gain_m"]:.9f}m；最大XY={out["max_root_xy_displacement_m"]:.9f}m。抬高不是站稳。\n'
md+=f'- 193个控制bin中：双主轮全部20采样承重={both}；guide/hard全部20采样≤1N={quiet}；两者同时={joint}。whole guide={out["guide_ticks_whole"]}，hard={out["hard_ticks_whole"]}，仅原private grader。\n'
md+=f'- request峰值Nm={peaks}；wheel-rate峰值rad/s={wmax}；不从request推断actual/DC clipping，不从encoder proxy推断真实路程。\n'
md+='- PRE sensor/command vs POST root以及.5ms collision缓存按原日志时标保留。一次新control读取193行，0physics/旧raw/模型/FK/重仿真/原始流hash。\n'
md+='- 既有静态支撑几何只是构型可行性，尚未成为动态起立策略；本案按原阈值停，门/旧冻结结果不改。本诊断不证明唯一失效原因，也不自动批准后续增益或病例。\n'
with (D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(md)
print(json.dumps({k:v for k,v in out.items()if k not in('events','source_trace_producer')},indent=2))
