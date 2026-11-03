"""Closed small-result facts only. No raw/asset hashing, no new physics."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;rows=[]
for batch in('r54_takeoff_window_flat','r54_takeoff_window_rm'):
    b=json.loads((R/'batches'/batch/'BATCH_RESULT.json').read_bytes());assert b['executed']==2 and not b['unstarted']
    for item in b['rows']:
        assert item['returncode']==0
        p=Path(item['result_path']);raw=p.read_bytes();r=json.loads(raw);scene=r['config']['scene']
        checks=dict(complete=r['complete'],peak_air80mm=r['maximum_main_mesh_clearance_during_full_air_m']is not None and r['maximum_main_mesh_clearance_during_full_air_m']>=.08,
            no_guide=r['guide_contact_physics_ticks']==0,no_hard=r['hard_contact_physics_ticks']==0,endstable2s=r['end_stable_s']>=2.,lane0p3m=r['max_abs_world_y_m']<=.3,progress0p5m=r['forward_progress_m']>=.5)
        if scene=='rm':checks.update(full_collision_final_behind_bar=r['conservative_final_robot_all_collision_behind_bar'],never_nextbar_envelope=r['conservative_front_never_reached_next_bar'])
        passed=all(checks.values());assert passed==r['proposed_'+('manual_first_bar_clear_stop_v1'if scene=='rm'else'moving_flat_air80_stop_v1')]
        land=r['first_landing'];cross=r['first_flight_main_rear_crossing_bar_back_s']
        if cross is not None:assert land is not None and cross<=land['stage_time_s']
        rows.append(dict(case=item['case'],scene=scene,passed=passed,failed_predicates=[k for k,v in checks.items()if not v],result_SHA=hashlib.sha256(raw).hexdigest(),
            controls=r['controls'],physics_steps=r['physics_steps'],trigger_time_s=r['config']['hop']['trigger_time_s'],
            guide_ticks=r['guide_contact_physics_ticks'],hard_ticks=r['hard_contact_physics_ticks'],peak_mesh_air_m=r['maximum_main_mesh_clearance_during_full_air_m'],
            first_all_world_air_s=r['first_all_world_air_s'],first_flight_rear_cross_s=cross,
            first_landing_stage_s=None if land is None else land['stage_time_s'],
            first_landing_positive_environment_contacts=[]if land is None else [dict(kind=c['kind'],robot=c['robot_geom'],environment=c['environment_geom'],normal_N=c['normal_N'],position_world_m=c['position_world_m'])for c in land['contacts']if c['normal_N']>1.],
            endstable_s=r['end_stable_s'],progress_m=r['forward_progress_m'],max_abs_y_m=r['max_abs_world_y_m'],max_pitch_rad=r['max_pitch_rad'],max_roll_rad=r['max_roll_rad'],
            trace_artifact=r['trace_artifact'],physical_artifact=r['physical_artifact']))
v=dict(kind='R54_NOMINAL_FIRSTFLIGHT6CM_FACTS',nominal_cases=4,flat_passes=sum(x['passed']for x in rows if x['scene']=='flat'),flat_n=2,
    RM_local_passes=sum(x['passed']for x in rows if x['scene']=='rm'),RM_n=2,controls=sum(x['controls']for x in rows),physics_steps=sum(x['physics_steps']for x in rows),rows=rows,
    clean_firstflight_meaning='Main-wheel rear mesh crossed the firstbar back while original all-positive-world-force<=1N qualified-air and before firstlanding. Not all-body instantaneous bbox crossing or hardware contact certainty.',
    full_robot_final_bbox_and_nextbar_rules_unchanged=True,not_fullDR_or_independent_holdout_or_wholeRM_or270_or_hardware=True,
    controllers_Python_not_C_jump_port=True,new_physics_steps_in_analysis=0,no_raw_or_assets_rehash=True,
    archive_membership='R54 excluded from explicitPH6cutoffR53; PH7pending. Original provisional PH6_pending fields are preserved, not rewritten.')
with (R/'reports/R54_FIRST_FLIGHT_6CM_FACTS.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
md=['# R54：首次取得名义6cm首bar的first-flight通过','',
    '全几何与原力阈值/guard/gate保留。4项新名义试验均800controls/16000steps，总64000新物理步；flat **2/2**，RM局部 **1/2**。不是全DR成功率。',
    '| case | gate | guide/hard ticks | first-flight rear-cross s | endstable s | 失败项 |','|---|---|---:|---:|---:|---|']
for x in rows:md.append('|'+x['case']+'|'+str(x['passed'])+'|'+str(x['guide_ticks'])+'/'+str(x['hard_ticks'])+'|'+str(x['first_flight_rear_cross_s'])+'|'+format(x['endstable_s'],'.4f')+'|'+','.join(x['failed_predicates'])+'|')
md+=['',
    '1.95s方案：主轮mesh后沿在2.3825s的qualified operational-air中越过首bar后沿，早于firstlanding；最终全collision保守包络在bar之后，且全程未到下bar包络。guide/hard均0，endstable3.67s。',
    '1.90s方案虽guide/hard0且最终过bar，但nextbar保守包络失败，仍记失败；未仅凭保守包络推断实际nextbar力接触。',
    '这里的clean first-flight限定为上述主轮mesh＋原operational-air定义，非全机瞬间包络、真实零力或硬件冲击认证。峰mesh离地约0.183m，不是270mm。',
    '仅新TRAIN、Python控制路径、手动定时首bar局部；H1/H2/H4/H5和Stage1 V1未改。后续新全DR TRAIN独立保存，不据名义宣称鲁棒毕业。',
    'PH6严格截止R53，R54属于PH7pending；保留执行时旧provisional字段原样。',
    '[结构化事实](<R54_FIRST_FLIGHT_6CM_FACTS.json>)']
with (R/'reports/R54_FIRST_FLIGHT_6CM_FACTS.md').open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
print(json.dumps({k:v[k]for k in('flat_passes','flat_n','RM_local_passes','RM_n','controls','physics_steps')},indent=2))
