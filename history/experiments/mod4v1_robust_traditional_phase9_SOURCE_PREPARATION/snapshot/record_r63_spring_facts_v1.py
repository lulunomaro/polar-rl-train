"""One saved-small-result R63 reconciliation; never replays or opens raw/assets."""
from pathlib import Path
import copy,hashlib,json,math
R=Path(__file__).resolve().parent;D=R/'R63_SPRING_PUSH_ADMISSION_V1';P=R/'R63_SPRING_PUSH_PAIRED_TRAIN_V1'
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def gates(x):
    peak=x['maximum_main_mesh_clearance_during_full_air_m']
    tests=dict(complete=x['complete']is True,mesh_air80=finite(peak)and peak>=.08,
        no_guide=x['guide_contact_physics_ticks']==0,no_hard=x['hard_contact_physics_ticks']==0,
        end_stable2=x['end_stable_s']>=2.,lane=x['max_abs_world_y_m']<=.3,progress=x['forward_progress_m']>=.5)
    main=all(tests.values());scene=x['config']['scene']
    local=bool(scene=='rm'and main and x['conservative_final_robot_all_collision_behind_bar']and x['conservative_front_never_reached_next_bar'])
    assert x['proposed_moving_flat_air80_stop_v1']==bool(scene=='flat'and main)
    assert x['proposed_manual_first_bar_clear_stop_v1']==local
    if scene=='rm':tests.update(final_behind=x['conservative_final_robot_all_collision_behind_bar']is True,
                                never_next=x['conservative_front_never_reached_next_bar']is True)
    return dict(original_pass=bool(main if scene=='flat'else local),failed=[k for k,v in tests.items()if not v],
                main_rear_firstflight=finite(x['first_flight_main_rear_crossing_bar_back_s']))
def profile(c):
    c=copy.deepcopy(c)
    for k in('case_id','cohort'):c.pop(k,None)
    c['hop'].pop('release_spring_compensation_during_push',None)
    return json.dumps(c,sort_keys=True,allow_nan=False)
rows=[];known_controls=known_steps=0;unknown_errors=[]
plans=[('nominal',D/'PROTOCOL.json')]
if(P/'PROTOCOL.json').is_file():plans.append(('selected_TRAIN',P/'PROTOCOL.json'))
for cohort,pp in plans:
    for name,cfg in load(pp)['configs']:
        rp=R/'results'/name/'result.json';ep=rp.parent/'ERROR.json'
        row=dict(case=name,cohort=cohort,seed=cfg['seed'],scene=cfg['scene'])
        if ep.is_file():
            e=load(ep);row.update(status='SOFTWARE_ERROR_SAVED_PREFIX',error_path=str(ep),error_SHA=sha(ep))
            if type(e.get('controls'))is int and type(e.get('physics_steps'))is int:
                row.update(controls=e['controls'],physics_steps=e['physics_steps']);known_controls+=e['controls'];known_steps+=e['physics_steps']
            else:unknown_errors.append(name)
        elif rp.is_file():
            x=load(rp);assert profile(x['config'])==profile(cfg);g=gates(x)
            assert x['kind']=='NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN'and x['spring_release_enabled']is True
            assert x['physics_steps']==20*x['controls']and x['controller_truth_inputs']is False
            assert x['root_assist_forces']==x['root_state_overwrites_after_initialization']==0
            baseline_name=('r58_tall0_position_'+cfg['scene'])if cohort=='nominal'else f"r60_tall0_fresh_RM_DR_{cfg['seed']}"
            bp=R/'results'/baseline_name/'result.json';old=load(bp);assert profile(old['config'])==profile(cfg)
            oldg=gates(old)
            row.update(status='PHYSICAL_RESULT',controls=x['controls'],physics_steps=x['physics_steps'],complete=x['complete'],stop=x['stop'],
                **g,baseline_original_pass=oldg['original_pass'],DR_receipt_value_equal=x['DR']==old['DR'],
                peak_main_mesh_air_m=x['maximum_main_mesh_clearance_during_full_air_m'],baseline_peak_main_mesh_air_m=old['maximum_main_mesh_clearance_during_full_air_m'],
                guide=x['guide_contact_physics_ticks'],hard=x['hard_contact_physics_ticks'],end_stable_s=x['end_stable_s'],
                max_pitch_rad=x['max_pitch_rad'],world_y_max_m=x['max_abs_world_y_m'],progress_m=x['forward_progress_m'],
                peak_positive_mechanical_power_W=x['peak_positive_mechanical_power_W'],
                firstflight_cross_s=x['first_flight_main_rear_crossing_bar_back_s'],result_SHA=sha(rp),baseline_small_result_SHA=sha(bp),
                raw_producer_metadata_only=[x['trace_artifact'],x['physical_artifact']])
            known_controls+=x['controls'];known_steps+=x['physics_steps']
        else:row.update(status='UNSTARTED_OR_NOT_ADMITTED',actual_counts=None)
        rows.append(row)
physical=[r for r in rows if r['status']=='PHYSICAL_RESULT'];dr=[r for r in physical if r['cohort']=='selected_TRAIN']
facts=dict(kind='R63_CLOSED_SAVED_SMALL_RESULTS_NO_REPLAY',rows=rows,
    actual_physical_result_count=len(physical),actual_complete_count=sum(r['complete']for r in physical),
    saved_software_error_count=sum(r['status']=='SOFTWARE_ERROR_SAVED_PREFIX'for r in rows),known_consumed_controls=known_controls,
    known_consumed_physics_steps=known_steps,software_prefix_counts_unknown_cases=unknown_errors,
    selected_TRAIN_executed=len(dr),selected_TRAIN_pass=sum(r['original_pass']for r in dr),
    same_executed_TRAIN_baseline_pass=sum(r['baseline_original_pass']for r in dr),
    main_rear_firstflight_TRAIN=sum(r['main_rear_firstflight']for r in dr),
    paired_not_executed=not(P/'PROTOCOL.json').is_file(),
    claims=dict(unbiased_holdout=False,wholebody_clearance_from_main_marker=False,step270_qualified=False,hardware_or_buspower_qualified=False),
    no_new_controller_model_physics_raw_asset_or_QA_executed=True,H1_H2_H4_H5_stage1_unchanged=True,post_PH7_cutoff_pending=True)
dump(R/'reports/R63_SPRING_PUSH_FACTS.json',facts)
lines=['# R63：仅push阶段撤名义弹簧抵消的实际结果','',
       f"新物理结果 {len(physical)}，完整 {facts['actual_complete_count']}；已知实际消耗 {known_controls} controls / {known_steps} physics steps。软件prefix未知项：{unknown_errors}。",
       '', '|case|原门|旧baseline|轮mesh空中峰值 m|guide/hard ticks|终态稳定 s|失败项|','|---|---|---|---:|---:|---:|---|']
for r in rows:
    if r['status']=='PHYSICAL_RESULT':lines.append(f"|{r['case']}|{r['original_pass']}|{r['baseline_original_pass']}|{r['peak_main_mesh_air_m']}|{r['guide']}/{r['hard']}|{r['end_stable_s']}|{','.join(r['failed'])}|")
    else:lines.append(f"|{r['case']}|{r['status']}|—|—|—|—|—|")
lines+=['',f"所选机制TRAIN：{facts['selected_TRAIN_pass']}/{len(dr)}；同一已执行seed旧baseline {facts['same_executed_TRAIN_baseline_pass']}/{len(dr)}。"if dr else '配对TRAIN尚未执行或未被名义准入；不报0/4机器人通过率。',
        '只改变名义弹性端点FF加回，机械spring/PD/driver/原接触及所有原门保持。端点混合不是任意q(t)精确模型。',
        '原标准逐项重算一致；main轮rear-cross不等整机空中净跨，保守包络失败不自动等实际碰撞。',
        '队列是已按旧TRAIN结果选择的机制对照，不是独立holdout。空中mesh峰值、6cm局部跨障不构成270mm台阶/全RM/硬件或母线功率资格。',
        '本统计只读小result/config；大raw只引用producer SHA/size，没有物理/旧QA重放或为归档重hash。']
with(R/'reports/R63_SPRING_PUSH_FACTS.md').open('x',encoding='utf-8')as f:f.write('\n'.join(lines)+'\n')
print(json.dumps({k:v for k,v in facts.items()if k!='rows'},indent=2))
