"""Analyse NEW R61 traces once for realised gate/strict-screen evidence.
Reads OLD small results only, never old trajectories; no physics/regrading.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
R=Path(__file__).resolve().parent
rows=[]
for seed in(0,201,202):
    name='r61_decelgate_spin_'+('nominal'if seed==0 else 'DR_'+str(seed))
    rp=R/'results'/name/'result.json';raw=rp.read_bytes();r=json.loads(raw)
    oldp=R/'results'/('r26_spin_cycle_'+str(seed))/'result.json';oldraw=oldp.read_bytes();old=json.loads(oldraw)
    cfg=json.loads(json.dumps(r['config']));cfg['case_id']=old['config']['case_id'];del cfg['controller']['center_through_yaw_decel'];assert cfg==old['config']
    # Keep only small tail arrays and realised gate intervals, not a second raw.
    v=[];w=[];ref=[];pitch=[];roll=[];intervals=[];active_interval=None;new_raw_rows=0
    with Path(r['trace_artifact']['path']).open('r',encoding='utf-8')as f:
        for line in f:
            q=json.loads(line);i=new_raw_rows;new_raw_rows+=1;c=q['spin_center'];ret=c['gate_retained_from_previous_active']
            if ret:
                assert q['request'][1]==0. and c['gate_previous_shaped_w_rad_s']!=0. and c['active']
                t=q['estimate_time']
                if active_interval is None:active_interval=dict(first_control_pre_s=t,last_control_pre_s=t,count=0,last_current_shaper_w=None,last_previous_shaper_w=None)
                active_interval.update(last_control_pre_s=t,count=active_interval['count']+1,last_current_shaper_w=c['gate_current_shaped_w_rad_s'],last_previous_shaper_w=c['gate_previous_shaped_w_rad_s'])
            elif active_interval is not None:
                active_interval.update(next_control_pre_s=q['estimate_time'],next_active=c['active'],next_previous_shaper_w=c['gate_previous_shaped_w_rad_s']);intervals.append(active_interval);active_interval=None
            if q['time']>=max(1.,r['config']['duration_s']-2.):
                g=q['ground_truth'];a=g['gyro_true'];p=g['pitch_true'];rr=g['roll_true']
                v.append(g['body_velocity'][0]);w.append((a[1]*math.sin(rr)+a[2]*math.cos(rr))/max(math.cos(p),.15));ref.append(q['shaped']);pitch.append(p);roll.append(rr)
    if active_interval is not None:intervals.append(active_interval)
    assert new_raw_rows==r['controls']==2600
    vv=np.array(v);ww=np.array(w);refs=np.array(ref);v_rms=float(np.sqrt(np.mean((vv-refs[:,0])**2)));w_rms=float(np.sqrt(np.mean((ww-refs[:,1])**2)))
    assert v_rms==r['tail_v_tracking_RMSE']and w_rms==r['tail_w_tracking_RMSE']
    gates=dict(complete=r['complete'],upright_all_tail=bool(np.all(np.abs(roll)<math.radians(10))and np.all(np.abs(pitch)<math.radians(10))),
        v_tracking_RMS_lt_0p15=v_rms<.15,w_tracking_RMS_strict=w_rms<.1*max(1.,float(np.abs(refs[:,1]).max())),
        closure_le_0p01=r['max_closure']<=.01,mimic_le_0p01=r['max_mimic']<=.01,impulse_support=r['impulse_support_gate'],zero_nonwheel_physics=r['physics_nonwheel_contact_ticks']==0)
    assert all(gates.values())==r['proposed_gate_passed']
    rows.append(dict(case=name,seed=seed,nominal=r['nominal'],complete=r['complete'],controls=r['controls'],physics_steps=r['physics_callbacks'],
        original_wholecase_screen=r['proposed_gate_passed'],original_composite=r['transition_proposed_pass'],failed_wholecase_predicates=[k for k,v in gates.items()if not v],
        tail_v_tracking_RMS=v_rms,tail_w_tracking_RMS=w_rms,tail_w_threshold=.1*max(1.,float(np.abs(refs[:,1]).max())),
        final_XY_m=r['xy_displacement_m'],phase_metrics=r['phase_metrics'],realised_retained_gate_intervals=intervals,
        actual_fullDR_receipt_equal_to_old=r['DR']==old['DR'],before_first_stop_positive_phase_metrics_equal=r['phase_metrics'][0]==old['phase_metrics'][0],
        baseline_composite=old['transition_proposed_pass'],baseline_XY_m=old['xy_displacement_m'],baseline_final_stop_v_RMS=old['phase_metrics'][-1]['tail_v_RMS'],
        baseline_first_stop_s=old['phase_metrics'][1]['stop_after_command_s'],baseline_final_stop_s=old['phase_metrics'][-1]['stop_after_command_s'],
        result_SHA=hashlib.sha256(raw).hexdigest(),baseline_small_result_SHA=hashlib.sha256(oldraw).hexdigest(),new_trace_producer_artifact=r['trace_artifact'],new_trace_open_count=1))
summary=dict(kind='R61_STOP_ONLY_GATE_NEW_TRAIN_FACTS',complete=sum(r['complete']for r in rows),n=3,paired_DR_n=2,
    composite_passes=sum(r['original_composite']for r in rows),paired_DR_composite_passes=sum(r['original_composite']for r in rows if not r['nominal']),
    controls=sum(r['controls']for r in rows),physics_steps=sum(r['physics_steps']for r in rows),rows=rows,
    all_frozen_thresholds_retained=True,new_physics_steps_in_analysis=0,old_raw_trajectories_read=False,raw_hash_recomputed=False,
    realised_gate_not_measured_spin_or_contact=True,H1_H2_H4_H5_Stage1_unchanged=True,no_inside_batch_retune=True,no_MCU_or_robust_qualification=True,PH7_pending=True)
with(R/'reports/R61_SPIN_DECEL_GATE_FACTS.json').open('x',encoding='utf-8')as f:json.dump(summary,f,indent=2,allow_nan=False)
md=['# R61：自转停止门控的单因素TRAIN结果','',
    '真实新实验3/3完整（1名义+2配对DR），7800controls/156000物理步；**原composite仍0/3（全DR0/2）**。没有把完成执行或部分相位改善当技能通过。',
    '只保持centering至previous commanded shaper归零，旧K/observer/roll/torque cap/driver与所有评价窗不变；旧baseline未重跑，只读小result比较。',
    '','|seed|old→new最终XY m|old→new final-stop v RMS|新first/final stop s|原wholecase失败项|','|---|---:|---:|---|---|']
for r in rows:
    p=r['phase_metrics'];md.append(f"|{r['seed']}|{r['baseline_XY_m']:.6f}→{r['final_XY_m']:.6f}|{r['baseline_final_stop_v_RMS']:.6f}→{p[-1]['tail_v_RMS']:.6f}|{p[1]['stop_after_command_s']} / {p[-1]['stop_after_command_s']}|{','.join(r['failed_wholecase_predicates'])}|")
md +=['','名义first_stop最长0.49s<0.50s，继续记失败；201虽然两个stop相位均取得>=0.5s hold，仍未过原wholecase screen；202最后停止未取得hold且XY>.3m。没有删除wholecase gate或放宽yaw跟踪阈值。',
    '两DR首次stop前positive phase保存指标与旧值精确相同='+str(all(r['before_first_stop_positive_phase_metrics_equal']for r in rows if not r['nominal']))+'；DR receipt逐值相同='+str(all(r['actual_fullDR_receipt_equal_to_old']for r in rows if not r['nominal']))+'。不是逐2k物理state位证明；旧heldout未作选择/改分。',
    '实际centering保留区间/previous-current shaper与严格wholecase失败项详JSON；这些是command状态，不是测得已停止/触地。新trace各单pass、无旧raw/资产归档重hash、0新分析物理步。',
    '结论：门控可改善部分停止指标，但该单因素不足完成停启换向；201/202是旧TRAIN配对，不是新的独立鲁棒性样本。新候选保持实验默认off，PH7pending。',
    '[结构化证据](<R61_SPIN_DECEL_GATE_FACTS.json>)']
with(R/'reports/R61_SPIN_DECEL_GATE_FACTS.md').open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
print(json.dumps({k:summary[k]for k in('n','complete','composite_passes','controls','physics_steps')},indent=2));print('\n'.join(md[6:10]))
