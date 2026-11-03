"""Once-only B control diagnosis; no robot imports/raw hashes/physics reads."""
from pathlib import Path
import datetime,hashlib,json,math,traceback
D=Path(__file__).resolve().parent;T=D.parents[1];CASE='startup_front065_tracking_v3b_nominal1';B=T/'results'/CASE
COUNTS={'trace_open_count':0,'control_rows':0,'physics_or_old_A_raw_opens':0,'raw_hashes':0,'new_model_FK_PHY_QA_Git_agents':0}
SELECTED=[]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def num(x):
    assert type(x)in(int,float)and math.isfinite(x),'Missing/nonfinite required saved scalar'
    return float(x)
def vector(x,n):
    assert isinstance(x,list)and len(x)==n,'Saved vector shape';return [num(v)for v in x]
def main():
    assert not(D/'SOURCE_PREEXEC.json').exists(),'Once consumed: inspect partial evidence; no replay'
    v=load(B/'result.json');assert v['config']['case_id']==CASE and v['config']['nominal']is True
    assert(v['controls'],v['physics_steps'])==(298,5960)and v['complete']is False and v['startup_stand_original_v1_gate']is False
    raw=B/'trace.jsonl';producer=v['trace_artifact'];assert Path(producer['path']).resolve()==raw.resolve()and raw.stat().st_size==producer['bytes']
    inputs=[D/'METHOD.json',Path(__file__),B/'result.json'];before=[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))for p in inputs]
    new(D/'SOURCE_PREEXEC.json',dict(status='METHOD_SMALLSOURCE_LOCK_BEFORE_ONE_CONTROL_TRACE_READ',sources=before,producer_trace=producer,archive_raw_SHA_recomputed=False,limits=dict(opens=1,rows=298,events=12),UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PH10pending=True))
    rows=[];COUNTS['trace_open_count']+=1
    with raw.open('rb')as f:
        for b in f:
            COUNTS['control_rows']+=1;assert COUNTS['control_rows']<=298,'Stop at declared row budget'
            rows.append(json.loads(b))
    assert len(rows)==298
    for k,r in enumerate(rows):assert abs(num(r['command_time_s'])-k*.01)<1e-8
    def phase(i):return rows[i]['phase']
    def first(pred):return next((i for i,r in enumerate(rows)if pred(i,r)),None)
    eligible=first(lambda i,r:phase(i).get('alignment_candidate_eligible_this_command')is True)
    latched=first(lambda i,r:phase(i).get('alignment_latched')is True)
    soft=first(lambda i,r:any(phase(i).get('alignment_soft_overspeed_limited2',[])))
    def braking(i,r):
        if phase(i).get('alignment_latched')is not True:return False
        flags=phase(i).get('alignment_soft_overspeed_limited2');w=r['wheel_rate_mean2'];u=r['requested_tau6']
        return flags is not None and any(num(w[j])*num(u[a]) < 0. and flags[j] is False for j,a in enumerate((2,5)))
    brake=first(braking)
    selectors={'initial':0,'first_SHAPE':first(lambda i,r:phase(i)['phase']=='SHAPE_TO_STAND'),'pre_first_eligible':None if eligible is None or eligible==0 else eligible-1,'first_eligible':eligible,'first_alignment_latch':latched,'first_logged_soft_overspeed_replacement':soft,'first_aligned_already_braking_request_not_replaced':brake,'first_proxy_ge_0p10':first(lambda i,r:phase(i).get('recovery_encoder_travel_m',-1.)>=.10),'first_proxy_ge_0p25':first(lambda i,r:phase(i).get('recovery_encoder_travel_m',-1.)>=.25),'first_proxy_gt_0p50':first(lambda i,r:phase(i).get('recovery_encoder_travel_m',-1.)>.50),'penultimate':len(rows)-2,'terminal':len(rows)-1}
    labels={}
    for name,i in selectors.items():
        if i is not None:labels.setdefault(i,[]).append(name)
    assert len(labels)<=12
    initial=vector(v['actual_initial_xyz_m'],3)
    def xy(g):
        a=vector(g['xyz'],3);return math.hypot(a[0]-initial[0],a[1]-initial[1])
    def truepose(g):
        w=vector(g['gyro_true'],3);roll=num(g['roll_true'])
        return dict(root_pose_velocity_time_s=g.get('root_pose_velocity_time_s'),cache_time_s=g.get('collision_site_cache_time_s'),pitch_rad=num(g['pitch_true']),roll_rad=roll,gyro_BODY_rad_s3=w,derived_Euler_pitch_rate_rad_s=w[1]*math.cos(roll)-w[2]*math.sin(roll),xyz_m=g['xyz'],XY_net_displacement_from_initial_m=xy(g),body_velocity_m_s3=g.get('body_velocity'),upright_cos=g.get('upright_cos'))
    lastrefs={};lastref=None
    for i,r in enumerate(rows):
        if 'reference_q4'in phase(i):lastref=dict(command_time_s=r['command_time_s'],reference_q4=phase(i)['reference_q4'],reference_qd4=phase(i).get('reference_qd4'))
        lastrefs[i]=lastref
    for i in sorted(labels):
        r=rows[i];p=phase(i);q=vector(r['encoder_q4'],4);qd=vector(r['encoder_qd4'],4);ref=p.get('reference_q4');last=lastrefs[i];w=vector(r['wheel_rate_mean2'],2);tau=vector(r['requested_tau6'],6);x=vector(r['estimated14'],14)
        e=dict(control_index=i,labels=labels[i],command_time_s=r['command_time_s'],sensor_time_s=r['sensor_time_s'],sensor_age_s=r['sensor_age_s'],root_POST_s=r['root_post_s'],phase=p['phase'],fault=p.get('fault'),recovery_subphase=p.get('recovery_subphase'),eligibility_current=p.get('alignment_candidate_eligible_this_command'),eligibility_ever=p.get('alignment_candidate_eligible_ever'),alignment_latched=p.get('alignment_latched'),first_eligible_s=p.get('alignment_first_eligible_s'),encoder_travel_m=p.get('recovery_encoder_travel_m'),estimated_pitch_rad=x[2],estimated_pitch_rate_rad_s=x[9],estimated_roll_rad=r['estimated_roll'],true_PRE=truepose(r['grade_before']),true_POST=truepose(r['grade_after']),packet_wheel_mean_rate2_rad_s=w,requested_tau6_Nm=tau,actual_substep_tau_or_speed='UNKNOWN_PHYSICS_NOT_OPENED',alignment_common_before_damping_Nm=p.get('alignment_pose_common_before_damping_Nm'),soft_overspeed_replaced2=p.get('alignment_soft_overspeed_limited2'),current_reference_q4=ref,current_reference_qd4=p.get('reference_qd4'),packet_encoder_q4=q,packet_encoder_qd4=qd,max_packet_reference_error_rad=None if ref is None else max(abs(a-b)for a,b in zip(q,vector(ref,4))),max_abs_packet_qd_rad_s=max(map(abs,qd)),last_published_reference=last,last_published_reference_packet_error_rad=None if last is None else max(abs(a-b)for a,b in zip(q,vector(last['reference_q4'],4))),private_POST_true_joint_target_error_rad=r.get('private_true_joint_error_rad'),main_mean_N2=r['main_contact_mean_N2'],main_min_N2=r['main_contact_min_N2'],both_support_every_2k_sample=r['both_support_every_2k_sample'],no_other_contact_in_control=r['no_other_contact_in_control'],end_stable_s=r['end_stable_s'],all_recorded_phase_fields=p)
        SELECTED.append(e)
    aligned=[]if latched is None else rows[latched:]
    s=dict(complete=v['complete'],stop=v['stop'],controller_fault=v['controller_fault_reason'],original_gate=v['startup_stand_original_v1_gate'],controls=v['controls'],physics_steps=v['physics_steps'],first_BALANCE_command_s=v['first_BALANCE_command_s'],max_true_XY_net_m=v['max_root_xy_displacement_m'],body_height_gain_m=v['body_height_gain_m'],final_POST_pitch_rad=v['final_grade']['pitch_true'],final_POST_xyz_m=v['final_grade']['xyz'],guide_ticks_whole_episode=v['guide_contact_ticks_whole_episode'],hard_ticks_whole_episode=v['hard_contact_ticks_whole_episode'],phase_counts={name:sum(r['phase']['phase']==name for r in rows)for name in sorted({r['phase']['phase']for r in rows})},first_eligible_control_s=None if eligible is None else rows[eligible]['command_time_s'],first_alignment_control_s=None if latched is None else rows[latched]['command_time_s'],first_logged_softlimit_control_s=None if soft is None else rows[soft]['command_time_s'],aligned_row_count=len(aligned),aligned_min_abs_POST_pitch_rad=None if not aligned else min(abs(r['grade_after']['pitch_true'])for r in aligned),aligned_max_abs_POST_pitch_rad=None if not aligned else max(abs(r['grade_after']['pitch_true'])for r in aligned),aligned_POST_abs_pitch_lt_0p15_rows=sum(abs(r['grade_after']['pitch_true'])<.15 for r in aligned),aligned_double_support_bins=sum(r['both_support_every_2k_sample']for r in aligned),aligned_noOther_bins=sum(r['no_other_contact_in_control']for r in aligned),terminal_proxy_m=phase(len(rows)-1).get('recovery_encoder_travel_m'),terminal_PRE_true_XY_net_m=xy(rows[-1]['grade_before']),terminal_POST_true_XY_net_m=xy(rows[-1]['grade_after']),max_abs_packet_wheel_rate_rad_s=max(abs(a)for r in rows for a in r['wheel_rate_mean2']))
    new(D/'READ_COUNTS.json',dict(status='ONE_B_CONTROL_TRACE_CONSUMED_NO_PHYSICS_OR_OLD_RAW',counts=COUNTS,selected_event_count=len(SELECTED),selector_indices=selectors,trace_producer=producer,PH10pending=True))
    new(D/'EVENTS.json',dict(status='BOUNDED_B_CONTROL_EVENTS_NOT_UNIQUE_MECHANISM_OR_PHYSICAL_STANDUP',summary=s,events=SELECTED,selector_indices=selectors,recorded_top_keys=sorted(rows[0]),counts=COUNTS,requested_NOT_actual=True,phase_telemetry_is_control_epoch_and_true_POST_is_later=True,unknowns=['2k instantaneous wheel torque/speed and actual contact identities','Slip fraction, friction/clip unique causal attribution','Physical continuous-time support between samples'],PH10pending=True))
    # Minimal derived evidence is durable before narrative/assertion closure.
    assert abs(s['max_true_XY_net_m']-max(xy(r['grade_after'])for r in rows))<1e-12
    assert phase(len(rows)-1)['phase']=='INHIBIT'and s['terminal_proxy_m']>.50 and rows[-1]['requested_tau6']==[0.]*6
    assert all(sha(Path(x['path']))==x['SHA']for x in before)
    lines=['# V3B单次控制trace事实诊断（非起立成功）',f"原完整case状态complete={s['complete']}, stop={s['stop']}, fault={s['controller_fault']}; {s['controls']}controls/{s['physics_steps']}PHY，originalgateFalse，未重跑。",f"首次eligible/对准control={s['first_eligible_control_s']}/{s['first_alignment_control_s']}s；首次logged软限速替换={s['first_logged_softlimit_control_s']}s；BALANCE={s['first_BALANCE_command_s']}。",'|control s/事件|phase|est pitch/rate|POST true pitch/rate|proxy m / PRE XY m|packet wheel rad/s|requested wheel Nm|q-ref max rad|support minN2 / noOther|','|---|---|---|---|---|---|---|---|---|']
    for e in SELECTED:
        def fmt(z):return 'UNKNOWN'if z is None else f'{z:.6g}'
        lines.append(f"|{e['command_time_s']:.2f} / {','.join(e['labels'])}|{e['phase']}|{e['estimated_pitch_rad']:.6g}/{e['estimated_pitch_rate_rad_s']:.6g}|{e['true_POST']['pitch_rad']:.6g}/{e['true_POST']['derived_Euler_pitch_rate_rad_s']:.6g}|{fmt(e['encoder_travel_m'])}/{e['true_PRE']['XY_net_displacement_from_initial_m']:.6g}|{e['packet_wheel_mean_rate2_rad_s']}|{[e['requested_tau6_Nm'][j]for j in(2,5)]}|{fmt(e['max_packet_reference_error_rad'])}|{e['main_min_N2']} / {e['no_other_contact_in_control']}|")
    lines.extend([f"对准起至终段POST true |pitch|min/max={s['aligned_min_abs_POST_pitch_rad']}/{s['aligned_max_abs_POST_pitch_rad']}rad；<.15rad rows={s['aligned_POST_abs_pitch_lt_0p15_rows']}；仍未BLEND/BALANCE。末Z={s['final_POST_xyz_m'][2]}m，gain={s['body_height_gain_m']}m，不等于直立。",f"原proxy strict>.50触发，末proxy={s['terminal_proxy_m']}m，PRE true XY净位移={s['terminal_PRE_true_XY_net_m']}m，POST/max净位移={s['max_true_XY_net_m']}m<.5；绝对轮转代理与真XY净位移/历程非同量，epoch亦不同，不据此证明打滑或真实越界。",'软限速事件来自控制日志；already-braking是请求对packet轮速反向且无soft replacement，不是实际driver力矩。只报告requested，2k实际τ/速度未读、UNKNOWN；不唯一归因摩擦/clip。','current_reference缺失的INHIBIT保留UNKNOWN；last_published_reference另标时刻，private POST joint-target error是不同量。main mean/min和noOther系原writer的20×2k采样统计，未重建contact identity；POST pitchrate仅由记录gyro/roll代数换算。',f"本脚本一open/{COUNTS['control_rows']}rows、事件{len(SELECTED)}<=12；physics/旧Araw/rawhash/model/FK/PHY/旧QA/Git/agent0。原源码/guard/gate/score不改，计数不声称全会话别人未读。",'[READ_COUNTS](<READ_COUNTS.json>) · [EVENTS](<EVENTS.json>) · [METHOD](<METHOD.json>)；V4另提最小方法，不调参、不执行。PH10pending。'])
    assert len(lines)<=45
    with(D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(lines)+'\n')
    rec=dict(status='COMPLETE_ONE_B_TRACE_BOUNDED_DIAGNOSIS_NOT_NEW_TRIAL',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_small_before_after_equal=True,sources=before,counts=COUNTS,events=len(SELECTED),report_lines=len(lines),report_SHA=sha(D/'REPORT.md'),events_SHA=sha(D/'EVENTS.json'),counts_SHA=sha(D/'READ_COUNTS.json'),result_unchanged=True,new_proof_or_PHY_or_approval=False,PH10pending=True)
    new(D/'RECEIPT.json',rec)
    print(json.dumps(dict(status=rec['status'],counts=COUNTS,selected_events=len(SELECTED),summary=s,report_SHA=rec['report_SHA'],receipt_SHA=sha(D/'RECEIPT.json')),ensure_ascii=True))
if __name__=='__main__':
    try:main()
    except BaseException:
        e=traceback.format_exc();print(e)
        if not(D/'FAILURE.txt').exists():(D/'FAILURE.txt').write_text(e,encoding='utf-8')
        if not(D/'FAILURE_SOURCE.py').exists():(D/'FAILURE_SOURCE.py').write_bytes(Path(__file__).read_bytes())
        if not(D/'FAILURE_RECEIPT.json').exists():new(D/'FAILURE_RECEIPT.json',dict(status='STOP_NO_AUTOMATIC_TRACE_REOPEN',counts=COUNTS,partial_selected_events=SELECTED,PH10pending=True))
        raise
