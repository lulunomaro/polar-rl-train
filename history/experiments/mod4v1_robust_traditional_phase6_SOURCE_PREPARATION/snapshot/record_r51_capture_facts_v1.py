"""Aggregate only closed R51 small results. No raw reads/new physics/H5."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
b=json.loads((R/'batches/r51_bar_capture_nominal2/BATCH_RESULT.json').read_bytes());assert b['executed']==2 and not b['unstarted']
rows=[]
for v in b['rows']:
    assert v['returncode']==0
    p=Path(v['result_path']);raw=p.read_bytes();r=json.loads(raw)
    failures=[]
    for label,ok in [('complete',r['complete']),('peak_air_80mm',r['maximum_main_mesh_clearance_during_full_air_m']is not None and r['maximum_main_mesh_clearance_during_full_air_m']>=.08),
        ('no_guide',r['guide_contact_physics_ticks']==0),('no_hard',r['hard_contact_physics_ticks']==0),('endstable_2s',r['end_stable_s']>=2.),
        ('lane_0p3m',r['max_abs_world_y_m']<=.3),('progress_0p5m',r['forward_progress_m']>=.5),
        ('full_collision_behind_firstbar',r['conservative_final_robot_all_collision_behind_bar']),('never_reached_nextbar_envelope',r['conservative_front_never_reached_next_bar'])]:
        if not ok:failures.append(label)
    assert (len(failures)==0)==r['proposed_manual_first_bar_clear_stop_v1']
    rows.append(dict(case=v['case'],result_path=str(p),result_SHA=hashlib.sha256(raw).hexdigest(),passed=not failures,failed_predicates=failures,
        controls=r['controls'],physics_steps=r['physics_steps'],complete=r['complete'],predicted_air_after_push_s=r['config']['hop']['predicted_air_after_push_s'],
        guide_physics_ticks=r['guide_contact_physics_ticks'],hard_physics_ticks=r['hard_contact_physics_ticks'],
        end_stable_s=r['end_stable_s'],max_pitch_rad=r['max_pitch_rad'],max_abs_world_y_m=r['max_abs_world_y_m'],progress_m=r['forward_progress_m'],
        first_flight_rear_cross_s=r['first_flight_main_rear_crossing_bar_back_s'],any_later_operational_air_rear_cross_s=r['some_operational_air_main_rear_crossing_s'],
        trace_artifact=r['trace_artifact'],physical_artifact=r['physical_artifact']))
result=dict(kind='R51_NOMINAL_BAR_CAPTURE_FACTS',closed_cases=2,completed=sum(x['complete']for x in rows),local_passes=sum(x['passed']for x in rows),
    controls=sum(x['controls']for x in rows),physics_steps=sum(x['physics_steps']for x in rows),rows=rows,
    causal_boundary='Earlier capture changes alone did not remove guide-contact or satisfy original local gate. No unique mechanism inferred. R49 firstbar edge before fullair is a separate TRAIN observation.',
    next_bar_force_identity='not_read_here; failed conservative envelope is not alone proof of actual contact',
    first_flight_cross_is_diagnostic_not_newly_added_success_gate=True,new_physics_steps_in_analysis=0,no_raw_rehash_for_archive=True,
    H5_unchanged=True,PH6_pending=True)
for name,value in [('reports/R51_BAR_CAPTURE_FACTS.json',result)]:
    with (R/name).open('x',encoding='utf-8')as f:json.dump(value,f,indent=2,allow_nan=False)
md=['# R51：提前定时capture的两项名义TRAIN','',
    '两项均完成800 controls / 16000 physics，总32000新物理步，原局部gate **0/2**；未改门槛。',
    '| case | air后定时 s | guide ticks | endstable s | peak pitch rad | 原gate失败项 |',
    '|---|---:|---:|---:|---:|---|']
for x in rows:md.append('|'+x['case']+'|'+str(x['predicted_air_after_push_s'])+'|'+str(x['guide_physics_ticks'])+'|'+format(x['end_stable_s'],'.6f')+'|'+format(x['max_pitch_rad'],'.6f')+'|'+', '.join(x['failed_predicates'])+'|')
md+=['','两案first-flight-only rear-cross均null；这是独立诊断字段，不回溯增添原成功门槛。any-later-air另列，不能称clean firstflight。',
     'nextbar包络失败不单独证明真实力接触，本汇总没有读取R51 physics raw确认身份。',
     '提前capture单项未消除guide。R49已观察push中先碰首bar前上棱、之后才fullair；后续可在新TRAIN研究提前离地，仍保留旧失败，不读取H5调参。',
     '本脚本只读小batch/result，0新物理步、无大raw重hash；PH6pending。','[结构化事实](<R51_BAR_CAPTURE_FACTS.json>)']
with (R/'reports/R51_BAR_CAPTURE_FACTS.md').open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
print(json.dumps(dict(closed_cases=2,complete=2,local_passes=0,controls=result['controls'],physics_steps=result['physics_steps']),indent=2))
