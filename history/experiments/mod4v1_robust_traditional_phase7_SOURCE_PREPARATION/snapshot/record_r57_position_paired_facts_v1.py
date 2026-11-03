"""Paired TRAIN small-result comparison plus bounded new-trigger trace read.
No old baseline trajectory replay/read, no raw SHA recalculation or physics.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;bp=R/'batches/r57_position_paired_DR8/BATCH_RESULT.json';batch=json.loads(bp.read_bytes())
def latch_data(result):
    p=Path(result['trace_artifact']['path']);assert p.resolve().is_relative_to(R/'results')
    seen=0;decision=None;push=None;last=None
    with p.open(encoding='utf-8')as f:
        for line in f:
            row=json.loads(line);seen+=1;ph=row['phase'];last=ph
            if decision is None and ph.get('position_decision_time_s')is not None:
                decision=dict(time_s=ph['position_decision_time_s'],latched_push_s=ph['position_latched_push_time_s'],
                    relative_estimate_m=ph['position_relative_estimate_m'],origin_estimate_m=ph['position_origin_estimate_m'])
            if ph['phase']=='timed_push':push=row['command_time_s'];break
            if ph['phase']=='INHIBIT'or row['command_time_s']>2.61:break
    return dict(decision=decision,first_logged_push_s=push,rows_examined=seen,last_phase=last['phase']if last else None,
                last_reason=last.get('reason')if last else None)
def strict_local(r):
    p=r['maximum_main_mesh_clearance_during_full_air_m']
    tests=dict(complete=r['complete'],peak_air80mm=p is not None and p>=.08,no_guide=r['guide_contact_physics_ticks']==0,
        no_hard=r['hard_contact_physics_ticks']==0,endstable2s=r['end_stable_s']>=2.,lane0p3m=r['max_abs_world_y_m']<=.3,
        progress0p5m=r['forward_progress_m']>=.5,full_collision_final_behind_bar=r['conservative_final_robot_all_collision_behind_bar'],
        never_nextbar_envelope=r['conservative_front_never_reached_next_bar'])
    passed=all(tests.values());assert passed==r['proposed_manual_first_bar_clear_stop_v1'];return passed,[k for k,v in tests.items()if not v]
rows=[];software=[]
for item in batch['rows']:
    if 'result_path'not in item:
        software.append(dict(case=item['case'],returncode=item['returncode'],actual_saved_error=item.get('software_error')));continue
    np=Path(item['result_path']);raw=np.read_bytes();new=json.loads(raw);seed=new['config']['seed']
    op=R/f'results/r55_t195_RM_DR_{seed}/result.json';oldraw=op.read_bytes();old=json.loads(oldraw)
    passed,fails=strict_local(new);oldpassed,_=strict_local(old);cross=new['first_flight_main_rear_crossing_bar_back_s']
    rows.append(dict(case=item['case'],seed=seed,new_result_SHA=hashlib.sha256(raw).hexdigest(),baseline_result_SHA=hashlib.sha256(oldraw).hexdigest(),
        baseline_local_pass=oldpassed,new_local_pass=passed,new_failed_predicates=fails,
        baseline_guide_ticks=old['guide_contact_physics_ticks'],new_guide_ticks=new['guide_contact_physics_ticks'],new_hard_ticks=new['hard_contact_physics_ticks'],
        first_flight_main_rear_cross_s=cross,local_AND_firstflight=passed and cross is not None,endstable_s=new['end_stable_s'],
        max_pitch_rad=new['max_pitch_rad'],max_abs_y_m=new['max_abs_world_y_m'],complete=new['complete'],controls=new['controls'],physics_steps=new['physics_steps'],
        DR_receipt_value_equal=new['DR']==old['DR'],new_trigger=latch_data(new),trace_artifact=new['trace_artifact'],physical_artifact=new['physical_artifact']))
full=len(rows)==8 and not software and not batch['unstarted'];paired_match=all(r['DR_receipt_value_equal']for r in rows)
v=dict(kind='R57_POSITION_TRIGGER_PAIRED_TRAIN_FACTS',scheduled=8,result_count=len(rows),software_error_count=len(software),unstarted=batch['unstarted'],full8=full,
    completed=sum(r['complete']for r in rows),baseline_local_passes_in_matched_results=sum(r['baseline_local_pass']for r in rows),new_local_passes=sum(r['new_local_pass']for r in rows),
    new_firstflight_cross_n=sum(r['first_flight_main_rear_cross_s']is not None for r in rows),new_local_AND_firstflight_n=sum(r['local_AND_firstflight']for r in rows),
    gained=[r['seed']for r in rows if not r['baseline_local_pass']and r['new_local_pass']],regressed=[r['seed']for r in rows if r['baseline_local_pass']and not r['new_local_pass']],
    DR_receipts_equal_on_all_matched_results=paired_match,controls=sum(r['controls']for r in rows),physics_steps=sum(r['physics_steps']for r in rows),
    rows=rows,software=software,TRAINS_same8_not16independent_or_holdout=True,baseline_R55_unchanged_no_baseline_physics_or_raw_reread=True,
    new_physics_steps_in_analysis=0,raw_SHA_recomputed=False,scope='manual local first6cmbar, approach.9mps and stop, not wholeRM/270mm/hardware',PH7_pending=True)
with(R/'reports/R57_POSITION_PAIRED_TRAIN_FACTS.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
md=['# R57：手动里程next-tick触发，paired TRAIN','',
    f"实际物理result {len(rows)}/8，完整 {v['completed']}，软件错误 {len(software)}，未启动 {len(batch['unstarted'])}。原局部gate配对baseline {v['baseline_local_passes_in_matched_results']}/{len(rows)} → 新候选 {v['new_local_passes']}/{len(rows)}。",
    '同8个TRAIN种子，不是16个独立样本、不是新holdout，也没有重跑旧baseline。',
    f"DR receipt逐值一致：{paired_match}；仅用作事后配对核验，未把参数输入控制或消除扰动。",'',
    '| seed | baseline/new gate | guide旧→新 | decision→push s | firstflight cross s | 失败项 |',
    '|---|---|---:|---|---:|---|']
for r in rows:
    a=r['new_trigger'];d=a['decision'];schedule='None'if d is None else str(d['time_s'])+'→'+str(a['first_logged_push_s'])
    md.append('|'+str(r['seed'])+'|'+str(r['baseline_local_pass'])+'/'+str(r['new_local_pass'])+'|'+str(r['baseline_guide_ticks'])+'→'+str(r['new_guide_ticks'])+'|'+schedule+'|'+str(r['first_flight_main_rear_cross_s'])+'|'+','.join(r['new_failed_predicates'])+'|')
md+=['',f"首次operational-air内main-rear cross {v['new_firstflight_cross_n']}/{len(rows)}；同时原局部gate通过 {v['new_local_AND_firstflight_n']}/{len(rows)}。三个计数不混用。",
    f"改善seed={v['gained']}，退化seed={v['regressed']}；全部原失败保留，不挑最好片段或改阈值。",
    '当前只是手动相对估计里程调度；不是真位置/障碍/接触许可，无新增RAW2K输入。实际float-grid phase以日志为准。',
    '尚非全9m/其他地形/270mm/2mps越障/C跳跃/Power/实机或WCET资格。所有旧H1/H2/H4/H5冻结。PH7pending。',
    '[结构化事实](<R57_POSITION_PAIRED_TRAIN_FACTS.json>)']
with(R/'reports/R57_POSITION_PAIRED_TRAIN_FACTS.md').open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
print(json.dumps({k:v[k]for k in('full8','completed','new_local_passes','new_firstflight_cross_n','new_local_AND_firstflight_n','gained','regressed','DR_receipts_equal_on_all_matched_results','controls','physics_steps')},indent=2))
