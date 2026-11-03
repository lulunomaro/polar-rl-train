"""Closed small-artifact facts only. No trajectory/asset reads or model calls.
R62 four TRAIN pairs were outcome-selected from R60, not an unbiased holdout.
"""
from pathlib import Path
import hashlib,json,copy
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def original_gate(r):
    peak=r['maximum_main_mesh_clearance_during_full_air_m']
    flags=dict(complete=r['complete'],mesh_air80mm=peak is not None and peak>=.08,guide0=r['guide_contact_physics_ticks']==0,
        hard0=r['hard_contact_physics_ticks']==0,endstable2s=r['end_stable_s']>=2.,lane0p3=r['max_abs_world_y_m']<=.3,progress0p5=r['forward_progress_m']>=.5)
    main=all(flags.values())
    if r['config']['scene']=='rm':
        flags.update(full_collision_final_behind_bar=r['conservative_final_robot_all_collision_behind_bar'],never_nextbar_envelope=r['conservative_front_never_reached_next_bar'])
        good=all(flags.values());assert good==r['proposed_manual_first_bar_clear_stop_v1']
    else:
        good=main;assert good==r['proposed_moving_flat_air80_stop_v1']
    return good,[k for k,v in flags.items()if not v]
def key(c):
    c=copy.deepcopy(c)
    for k in('case_id','cohort'):c.pop(k,None)
    c['hop'].pop('air_pitch_ref_enable',None);return c
batches=['r62_airref002_nominal_v2_flat','r62_airref002_nominal_v2_rm','r62_airref002_paired_DR4'];rows=[];software=[];unstarted=[]
for name in batches:
    b=load(R/'batches'/name/'BATCH_RESULT.json');unstarted+=b['unstarted']
    for item in b['rows']:
        if item['software_failure']:software.append(dict(case=item['case'],reasons=item['software_failure_reasons'],saved_error=item.get('software_error')))
        rp=R/'results'/item['case']/'result.json'
        if not rp.exists():continue
        r=load(rp);ok,fail=original_gate(r)
        assert r['controller_truth_inputs']is False and r['root_assist_forces']==r['root_state_overwrites_after_initialization']==0
        assert r['physics_steps']==20*r['controls']
        v=dict(case=item['case'],scene=r['config']['scene'],seed=r['config']['seed'],nominal=r['config']['nominal'],
               software_failure=item['software_failure'],valid_robot_result=not item['software_failure'],result_path=str(rp),result_SHA=sha(rp),
               complete=r['complete'],controls=r['controls'],physics_steps=r['physics_steps'],original_gate_pass=ok,failed_predicates=fail,
               firstflight_main_rear_cross_s=r['first_flight_main_rear_crossing_bar_back_s'],
               original_gate_AND_mainfirstflight=ok and r['first_flight_main_rear_crossing_bar_back_s']is not None,
               guide_ticks=r['guide_contact_physics_ticks'],hard_ticks=r['hard_contact_physics_ticks'],endstable_s=r['end_stable_s'],
               peak_mesh_air_m=r['maximum_main_mesh_clearance_during_full_air_m'],max_pitch_rad=r['max_pitch_rad'],max_abs_y_m=r['max_abs_world_y_m'],
               trace_artifact=r['trace_artifact'],physical_artifact=r['physical_artifact'])
        if not v['nominal']:
            op=R/f"results/r60_tall0_fresh_RM_DR_{v['seed']}/result.json";old=load(op);oldok,_=original_gate(old)
            assert key(r['config'])==key(old['config'])
            v.update(baseline_case=old['config']['case_id'],baseline_result_SHA=sha(op),baseline_original_gate_pass=oldok,
                     baseline_guide_ticks=old['guide_contact_physics_ticks'],baseline_hard_ticks=old['hard_contact_physics_ticks'],
                     baseline_firstflight=old['first_flight_main_rear_crossing_bar_back_s']is not None,DR_receipt_value_equal=r['DR']==old['DR'])
        rows.append(v)
nom=[r for r in rows if r['nominal']and r['valid_robot_result']];pairs=[r for r in rows if not r['nominal']and r['valid_robot_result']]
v=dict(kind='R62_CLOSED_NOMINAL_AND_OUTCOME_SELECTED_TRAIN_PAIRS',scheduled_nominal=2,scheduled_pairs=4,
       valid_nominal_results=len(nom),valid_paired_results=len(pairs),software_errors=software,unstarted=unstarted,
       nominal_original_gate_passes=sum(r['original_gate_pass']for r in nom),paired_original_gate_passes=sum(r['original_gate_pass']for r in pairs),
       paired_mainfirstflight=sum(r['firstflight_main_rear_cross_s']is not None for r in pairs),paired_joint_gate=sum(r['original_gate_AND_mainfirstflight']for r in pairs),
       baseline_original_gate_passes_on_these_pairs=sum(r['baseline_original_gate_pass']for r in pairs),
       gained=[r['seed']for r in pairs if not r['baseline_original_gate_pass']and r['original_gate_pass']],
       regressed=[r['seed']for r in pairs if r['baseline_original_gate_pass']and not r['original_gate_pass']],
       DR_receipts_equal_on_all_observed_pairs=all(r['DR_receipt_value_equal']for r in pairs),
       observed_saved_result_controls=sum(r['controls']for r in rows),observed_saved_result_physics_steps=sum(r['physics_steps']for r in rows),
       rows=rows,old_baseline_replayed=False,old_scores_or_gates_changed=False,raw_or_asset_reads_or_rehash=False,new_physics_in_analysis=0,
       selection='Two previous R60 passes4602/4610 plus guide4605 and guide+hard4606 selected after old outcomes. Not holdout; no unbiased reliability claim.',
       scope='Moving approach plus one6cmSCUTbar and stop, not270mm/wholeRM/auto-contact/MCU/electrical/WCET qualification.',PH8_pending=True)
out=R/'reports/R62_AIRREF_NOMINAL_AND_PAIRED_FACTS'
with out.with_suffix('.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
md=['# R62空中俯仰参考：名义及固定TRAIN配对事实','',
    f"名义原gate {v['nominal_original_gate_passes']}/{len(nom)}；固定TRAIN配对原gate {v['paired_original_gate_passes']}/{len(pairs)}，baseline同seed {v['baseline_original_gate_passes_on_these_pairs']}/{len(pairs)}。",
    f"配对firstflight main-rear {v['paired_mainfirstflight']}/{len(pairs)}；与原local gate联合 {v['paired_joint_gate']}/{len(pairs)}。改善{v['gained']}，退化{v['regressed']}；DR receipts一致={v['DR_receipts_equal_on_all_observed_pairs']}。",
    f"已保存物理result消耗 {v['observed_saved_result_controls']} controls / {v['observed_saved_result_physics_steps']} integrator steps；软件错误{len(software)}，未启动{len(unstarted)}。未知软件prefix另看原ERROR，不由duration推算。",'',
    '| case | 原gate | guide/hard ticks | mainfirstflight s | endstable s | maxpitch rad | 失败项 |','|---|---|---:|---:|---:|---:|---|']
for r in rows:md.append(f"|{r['case']}|{r['original_gate_pass']}|{r['guide_ticks']}/{r['hard_ticks']}|{r['firstflight_main_rear_cross_s']}|{r['endstable_s']:.4f}|{r['max_pitch_rad']:.5f}|{','.join(r['failed_predicates'])}|")
md+=['','配对是看过旧R60 TRAIN结局后的机制对照；不是独立holdout或可靠率证明，未重跑baseline。',
     '保留原FullDR、传感器boxcar→D1→D3、D4/PD/gain/signedDC、闭链和所有contact；未改失败/阈值或扩大main-rear净空为整机净空。',
     '旧H1/H2/H4/H5与Stage1不变；本结果不是270mm、完整RM、自主接触许可、目标板或实机验收。PH8pending。',
     '[结构化逐例事实](<R62_AIRREF_NOMINAL_AND_PAIRED_FACTS.json>)']
with out.with_suffix('.md').open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
print(json.dumps({k:v[k]for k in('valid_nominal_results','valid_paired_results','nominal_original_gate_passes','paired_original_gate_passes','baseline_original_gate_passes_on_these_pairs','paired_mainfirstflight','paired_joint_gate','gained','regressed','observed_saved_result_controls','observed_saved_result_physics_steps')},indent=2))
