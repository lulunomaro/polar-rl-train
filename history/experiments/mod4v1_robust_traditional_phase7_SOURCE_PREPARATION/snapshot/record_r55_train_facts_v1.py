"""Read only closed R55 small results/configs, preserve strict gates and failures."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;b=json.loads((R/'batches/r55_first_bar_DR8/BATCH_RESULT.json').read_bytes())
assert b['executed']==8 and b['scheduled']==8 and b['unstarted']==[]
rows=[]
for item in b['rows']:
    assert item['returncode']==0
    p=Path(item['result_path']);raw=p.read_bytes();r=json.loads(raw);c=r['config']
    assert c['nominal']is False and c['seed']in range(4501,4509)and c['hop']['trigger_time_s']==1.95 and c['hop']['predicted_air_after_push_s']==.25
    tests=dict(complete=r['complete'],peak_air80mm=r['maximum_main_mesh_clearance_during_full_air_m']is not None and r['maximum_main_mesh_clearance_during_full_air_m']>=.08,
        no_guide=r['guide_contact_physics_ticks']==0,no_hard=r['hard_contact_physics_ticks']==0,endstable2s=r['end_stable_s']>=2.,
        lane0p3m=r['max_abs_world_y_m']<=.3,progress0p5m=r['forward_progress_m']>=.5,
        full_collision_final_behind_bar=r['conservative_final_robot_all_collision_behind_bar'],never_nextbar_envelope=r['conservative_front_never_reached_next_bar'])
    passed=all(tests.values());assert passed==r['proposed_manual_first_bar_clear_stop_v1']
    cross=r['first_flight_main_rear_crossing_bar_back_s'];land=r['first_landing']
    if cross is not None:assert land is not None and cross<=land['stage_time_s']
    rows.append(dict(case=item['case'],seed=c['seed'],result_path=str(p),result_SHA=hashlib.sha256(raw).hexdigest(),
        original_local_gate_pass=passed,failed_predicates=[k for k,v in tests.items()if not v],complete=r['complete'],controls=r['controls'],physics_steps=r['physics_steps'],
        first_flight_main_rear_cross_s=cross,original_local_pass_AND_first_flight_cross=passed and cross is not None,
        guide_ticks=r['guide_contact_physics_ticks'],hard_ticks=r['hard_contact_physics_ticks'],endstable_s=r['end_stable_s'],
        max_pitch_rad=r['max_pitch_rad'],max_roll_rad=r['max_roll_rad'],max_abs_y_m=r['max_abs_world_y_m'],progress_m=r['forward_progress_m'],
        peak_mesh_air_m=r['maximum_main_mesh_clearance_during_full_air_m'],trace_artifact=r['trace_artifact'],physical_artifact=r['physical_artifact']))
assert len({x['seed']for x in rows})==8
v=dict(kind='R55_FRESH_FULLDR_LOCAL_FIRST6CMBAR_TRAIN_FACTS',scheduled=8,valid_physical_results=8,software_errors=0,unstarted=0,
    complete=sum(x['complete']for x in rows),original_local_gate_passes=sum(x['original_local_gate_pass']for x in rows),
    first_flight_main_rear_cross_n=sum(x['first_flight_main_rear_cross_s']is not None for x in rows),
    original_local_pass_AND_first_flight_cross_n=sum(x['original_local_pass_AND_first_flight_cross']for x in rows),
    controls=sum(x['controls']for x in rows),physics_steps=sum(x['physics_steps']for x in rows),rows=rows,
    full_D0_D7_original_100Hz_sensor_driver_path=True,no_RAW2K_enrichment_or_truth_inputs=True,
    TRAIN_not_independent_holdout=True,scope='manual timer1.95; approach command.9m/s; local first6cmbar then stop, not whole9mgrid/other10families/270mm/2mps/hardware',
    no_new_or_relaxed_success_gate=True,first_flight_cross_separate_diagnostic_not_substituted_for_local_gate=True,
    H1_H2_H4_H5_immutable=True,new_physics_steps_in_analysis=0,no_large_raw_or_asset_hash_for_archive=True,archive='PH7pending after explicitPH6cutoffR53')
with (R/'reports/R55_FULLDR_FIRST_BAR_TRAIN_FACTS.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
md=['# R55：6cm首bar，新全DR TRAIN','',
    '固定R54唯一名义局部门槛通过的1.95s方案后，再执行8个未用TRAIN种子4501–4508。原D0–D7、100Hz传感链、2kHz物理与力/几何门槛均保留。',
    '', '**结果：8/8完整运行，原局部gate 6/8。** 不是独立holdout，也不是全场鲁棒毕业。',
    '', '| seed | 原局部gate | guide/hard ticks | first-flight主轮rear-cross s | endstable s | 失败项 |',
    '|---|---|---:|---:|---:|---|']
for x in rows:md.append('|'+str(x['seed'])+'|'+str(x['original_local_gate_pass'])+'|'+str(x['guide_ticks'])+'/'+str(x['hard_ticks'])+'|'+str(x['first_flight_main_rear_cross_s'])+'|'+format(x['endstable_s'],'.4f')+'|'+','.join(x['failed_predicates'])+'|')
md+=['','## 必须分开的三个计数','',
    '- 原首bar局部gate：**6/8**。4503和4505分别有33、3个guide>1N物理采样，仍严格失败；3个采样也未舍入忽略。',
    '- 首次qualified operational-air内主轮mesh后沿越过bar后沿：**4/8**。不是把landing后rebound充首次飞越。',
    '- 同时原gate通过且有上述first-flight cross：**3/8**（4501、4507、4508）。因此6/8不能写成6/8 clean first-flight。',
    '', '全部8案hard>1N采样0、endstable≥2s、最终全collision包络在首bar后且没有到下bar保守包络。最高mesh离地范围约0.1916–0.2464m，仍非270mm。100Hz endstable不等于每个2k采样连续主轮支撑。',
    '', '指令接近速度0.9m/s、手动定时起跳、已知局部首bar后停车；不是2m/s越障、自动接触FSM、全9m格栅/其他10类地形或硬件资格。控制为Python V3，不称C跳跃或已接入Power。',
    '', '原H1/H2/H4/H5及Stage1 V1保持原样；本次8个TRAIN失败均保留，无替换种子或放宽门槛。6400controls/128000新物理步；分析只读小结果，0新步/无大raw重hash。PH7pending。',
    '', '[结构化事实](<R55_FULLDR_FIRST_BAR_TRAIN_FACTS.json>) · [名义首次飞越事实](<R54_FIRST_FLIGHT_6CM_FACTS.md>)']
with (R/'reports/R55_FULLDR_FIRST_BAR_TRAIN_FACTS.md').open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
print(json.dumps({k:v[k]for k in('complete','original_local_gate_passes','first_flight_main_rear_cross_n','original_local_pass_AND_first_flight_cross_n','controls','physics_steps')},indent=2))
