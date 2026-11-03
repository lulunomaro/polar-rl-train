"""Reusable closed small-result aggregation, no trajectory reads/physics.
Optional paired baseline is compared without replay; never a HOLDOUT report.
"""
from pathlib import Path
import argparse,hashlib,json
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--batch',required=True);ap.add_argument('--out-prefix',required=True)
ap.add_argument('--title',required=True);ap.add_argument('--baseline-template');ap.add_argument('--change-description',required=True);a=ap.parse_args()
assert Path(a.batch).name==a.batch and Path(a.out_prefix).name==a.out_prefix
b=json.loads((R/'batches'/a.batch/'BATCH_RESULT.json').read_bytes())

def small_result(p):
    p=p.resolve();assert p.is_relative_to(R/'results');raw=p.read_bytes();return json.loads(raw),hashlib.sha256(raw).hexdigest()
def local_gate(r):
    h=r['maximum_main_mesh_clearance_during_full_air_m']
    t=dict(complete=r['complete'],peak_air80mm=h is not None and h>=.08,no_guide=r['guide_contact_physics_ticks']==0,
        no_hard=r['hard_contact_physics_ticks']==0,endstable2s=r['end_stable_s']>=2.,lane0p3m=r['max_abs_world_y_m']<=.3,
        progress0p5m=r['forward_progress_m']>=.5,full_collision_final_behind_bar=r['conservative_final_robot_all_collision_behind_bar'],
        never_nextbar_envelope=r['conservative_front_never_reached_next_bar'])
    ok=all(t.values());assert ok==r['proposed_manual_first_bar_clear_stop_v1'];return ok,[k for k,v in t.items()if not v]
rows=[];software=[]
for item in b['rows']:
    if 'result_path'not in item:
        software.append(dict(case=item['case'],returncode=item['returncode'],actual_saved_error=item.get('software_error')));continue
    r,h=small_result(Path(item['result_path']));ok,fails=local_gate(r);seed=r['config']['seed'];cross=r['first_flight_main_rear_crossing_bar_back_s']
    land=r['first_landing'];v=dict(case=item['case'],seed=seed,result_SHA=h,original_local_gate_pass=ok,failed_predicates=fails,
        complete=r['complete'],controls=r['controls'],physics_steps=r['physics_steps'],guide_ticks=r['guide_contact_physics_ticks'],hard_ticks=r['hard_contact_physics_ticks'],
        first_flight_main_rear_cross_s=cross,local_AND_firstflight=ok and cross is not None,endstable_s=r['end_stable_s'],
        max_pitch_rad=r['max_pitch_rad'],max_roll_rad=r['max_roll_rad'],max_abs_y_m=r['max_abs_world_y_m'],progress_m=r['forward_progress_m'],
        peak_mesh_air_m=r['maximum_main_mesh_clearance_during_full_air_m'],first_landing_stage_s=None if land is None else land['stage_time_s'],
        first_landing_positive_contacts=[]if land is None else [dict(kind=c['kind'],robot=c['robot_geom'],environment=c['environment_geom'],normal_N=c['normal_N'])for c in land['contacts']if c['normal_N']>0.],
        trace_artifact=r['trace_artifact'],physical_artifact=r['physical_artifact'])
    if a.baseline_template:
        name=a.baseline_template.format(seed=seed);assert Path(name).name==name
        old,oh=small_result(R/'results'/name/'result.json');oldok,_=local_gate(old)
        v.update(baseline_case=name,baseline_result_SHA=oh,baseline_local_pass=oldok,baseline_guide_ticks=old['guide_contact_physics_ticks'],
                 baseline_firstflight=old['first_flight_main_rear_crossing_bar_back_s']is not None,baseline_local_AND_firstflight=oldok and old['first_flight_main_rear_crossing_bar_back_s']is not None,
                 DR_receipt_value_equal=r['DR']==old['DR'])
    rows.append(v)
full=len(rows)==b['scheduled']and not software and not b['unstarted']
v=dict(kind='CLOSED_LOCAL_FIRST_BAR_TRAIN_FACTS',batch=a.batch,title=a.title,change_description=a.change_description,
    scheduled=b['scheduled'],valid_physical_results=len(rows),software_error_count=len(software),unstarted=b['unstarted'],full=full,
    complete=sum(r['complete']for r in rows),local_passes=sum(r['original_local_gate_pass']for r in rows),
    firstflight_cross_n=sum(r['first_flight_main_rear_cross_s']is not None for r in rows),local_AND_firstflight_n=sum(r['local_AND_firstflight']for r in rows),
    guide_failed_seeds=[r['seed']for r in rows if r['guide_ticks']>0],hard_failed_seeds=[r['seed']for r in rows if r['hard_ticks']>0],
    controls=sum(r['controls']for r in rows),physics_steps=sum(r['physics_steps']for r in rows),rows=rows,software=software,
    TRAIN_not_independent_holdout=True,no_heldout_or_old_score_mutation=True,new_physics_steps_in_analysis=0,raw_or_asset_hash_recomputed=False,raw_trajectories_read=False,
    scope='manual local first6cmbar after.9mps approach, not wholeRM/270mm/realboard',PH7_pending=True)
if a.baseline_template:
    v.update(baseline_local_passes=sum(r['baseline_local_pass']for r in rows),baseline_firstflight_cross_n=sum(r['baseline_firstflight']for r in rows),
        baseline_local_AND_firstflight_n=sum(r['baseline_local_AND_firstflight']for r in rows),
        gained=[r['seed']for r in rows if not r['baseline_local_pass']and r['original_local_gate_pass']],
        regressed=[r['seed']for r in rows if r['baseline_local_pass']and not r['original_local_gate_pass']],
        DR_receipts_equal_on_all_pairs=all(r['DR_receipt_value_equal']for r in rows),paired_same_seeds_not_new_independent_samples=True,baseline_not_replayed=True)
with (R/'reports'/(a.out_prefix+'.json')).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
md=['# '+a.title,'',a.change_description,'',
    f"实际result {len(rows)}/{b['scheduled']}，完整{v['complete']}，软件错误{len(software)}，未启动{len(b['unstarted'])}；原局部gate **{v['local_passes']}/{len(rows)}**。",
    f"first-flight main-rear cross **{v['firstflight_cross_n']}/{len(rows)}**；同时原gate通过 **{v['local_AND_firstflight_n']}/{len(rows)}**。三个计数不混用。"]
if a.baseline_template:
    md +=[f"配对baseline原gate {v['baseline_local_passes']}/{len(rows)}、联合{v['baseline_local_AND_firstflight_n']}/{len(rows)}；改善{v['gained']}、退化{v['regressed']}。同seed DR receipts一致={v['DR_receipts_equal_on_all_pairs']}。不是新的独立样本，未重跑旧baseline。"]
md +=['','| seed | 原局部gate | guide/hard ticks | firstflight cross s | endstable s | 失败项 |','|---|---|---:|---:|---:|---|']
for r in rows:md.append('|'+str(r['seed'])+'|'+str(r['original_local_gate_pass'])+'|'+str(r['guide_ticks'])+'/'+str(r['hard_ticks'])+'|'+str(r['first_flight_main_rear_cross_s'])+'|'+format(r['endstable_s'],'.4f')+'|'+','.join(r['failed_predicates'])+'|')
md +=['','全部guide/hard失败原样保留，即使最后恢复稳定；未替换seed或改变阈值。本报告只聚合小result，raw仅producer metadata，0新物理步。',
    '原力阈值/geometry/driver/D0–D7/100Hz sensor链不改；仍是TRAIN、手动相对里程/单bar停车，不是自动接触许可、整场地、270mm或硬件资格。旧H1/H2/H4/H5与Stage1保持。PH7pending。',
    '[结构化事实](<'+a.out_prefix+'.json>)']
with (R/'reports'/(a.out_prefix+'.md')).open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
print(json.dumps({k:v[k]for k in('scheduled','valid_physical_results','complete','local_passes','firstflight_cross_n','local_AND_firstflight_n','guide_failed_seeds','hard_failed_seeds','controls','physics_steps')},indent=2))
