"""Fixed outcome-selected TRAIN; NO launch without actual nominal admission.
Two source-locked waves: association is checked before the second wave.
No controller/physics import; old helper and baseline trials remain immutable.
"""
from pathlib import Path
import argparse,copy,hashlib,json,math,traceback
from fresh_train_batch_v2 import launch,dump
from candidate_case_evidence_v1 import validate_case,canonical
R=Path(__file__).resolve().parent;D=R/'R63_SPRING_PUSH_ADMISSION_V1';P=R/'R63_SPRING_PUSH_PAIRED_TRAIN_V1'
SEEDS=(4602,4605,4606,4610)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
ap=argparse.ArgumentParser();ap.add_argument('--parent-approval',type=Path,required=True);ap.add_argument('--review',type=Path,required=True);args=ap.parse_args()
apath=(R/args.parent_approval).resolve();rpath=(R/args.review).resolve()
assert apath.is_relative_to(R)and rpath.is_relative_to(R)
a=load(apath);review=load(rpath);source=load(D/'SOURCE_PREEXEC.json');nomplan=load(D/'PROTOCOL.json')
assert a['approved_for_fixed_paired_TRAIN']is True and a['seeds']==list(SEEDS)
assert a['launcher_SHA']==sha(Path(__file__))and a['source_index_SHA']==sha(D/'SOURCE_PREEXEC.json')and a['review_SHA']==sha(rpath)
assert review['ready_for_fixed_paired_TRAIN']is True
approval_sha=sha(apath)
def check_sources():
    for z in source['files']+review['checked_sources']:assert sha(z['path'])==z['SHA'],z['path']
    assert sha(apath)==approval_sha
check_sources()
spec=nomplan['candidate_binding'];runner=spec['entry_path']
nominals={};bindings=[]
for name,cfg in nomplan['configs']:
    bindings.append(validate_case(R,name,cfg,source,spec))
    x=load(R/'results'/name/'result.json');nominals[cfg['scene']]=x
assert canonical(bindings)==canonical(a['nominal_bindings'])
flat=nominals['flat'];rm=nominals['rm']
assert flat['proposed_moving_flat_air80_stop_v1']is True and rm['proposed_manual_first_bar_clear_stop_v1']is True
cross=rm['first_flight_main_rear_crossing_bar_back_s']
assert type(cross)in(int,float)and math.isfinite(cross)and cross>=0.
def profile(c):
    c=copy.deepcopy(c)
    for k in('case_id','cohort','nominal','seed'):c.pop(k,None)
    c['hop'].pop('release_spring_compensation_during_push',None)
    return canonical(c)
cases=[];baseline=[]
for seed in SEEDS:
    bp=R/f'results/r60_tall0_fresh_RM_DR_{seed}/result.json';old=load(bp)
    assert old['complete']is True and old['config']['seed']==seed and old['config']['nominal']is False
    assert profile(old['config'])==profile(rm['config'])
    name=f'r63_spring_release_DR{seed}';cfg=copy.deepcopy(old['config'])
    cfg.update(case_id=name,cohort='R63_FIXED_POST_R60_MECHANISM_TRAIN_NOT_HOLDOUT')
    cfg['hop']['release_spring_compensation_during_push']=True
    assert not(R/'results'/name).exists()
    cases.append((name,cfg));baseline.append(dict(seed=seed,case=old['config']['case_id'],path=str(bp),SHA=sha(bp),
        local_pass=old['proposed_manual_first_bar_clear_stop_v1'],guide=old['guide_contact_physics_ticks'],hard=old['hard_contact_physics_ticks']))
assert sum(z['local_pass']for z in baseline)==2
P.mkdir(exist_ok=False)
protocol=dict(kind='R63_SPRING_RELEASE_FIXED_PAIRED_TRAIN_NOT_HOLDOUT',configs=cases,max_workers=2,waves=2,
    candidate_binding=spec,baseline_small_results=baseline,nominal_bindings=bindings,
    selection='Same predeclared outcome-selected four old TRAIN seeds: not independent generalization evidence.',
    all_original_gates_and_D0_D7_driver_sensor_unchanged=True,inside_batch_retuning=False,post_PH7_cutoff_PH8_pending=True)
dump(P/'PROTOCOL.json',protocol)
dump(P/'SOURCE_PREEXEC.json',dict(files=source['files'],launcher_SHA=sha(Path(__file__)),parent_approval_SHA=approval_sha,review_SHA=sha(rpath)))
keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','forward_progress_m','max_abs_world_y_m',
      'maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks','hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
rows=[];attempted=[];wave_records=[]
def finish(status):
    known={z['case']for z in rows}
    result=dict(kind=protocol['kind'],status=status,scheduled=4,rows=rows,wave_records=wave_records,
        unstarted=[n for n,c in cases if n not in attempted],
        attempted_wave_cases_without_final_batch_row=[n for n in attempted if n not in known],
        executed_from_saved_batch_rows=len(rows),software_failure=status!='COMPLETE_FIXED_TRAIN',
        counts_only_from_actual_saved_artifacts_not_requested_duration=True)
    dump(P/'BATCH_RESULT.json',result);print(json.dumps(result,indent=2,allow_nan=False))
for wave in range(2):
    items=cases[wave*2:wave*2+2];batch=f'r63_spring_release_paired_DR4_wave{wave+1}'
    try:
        check_sources()
        attempted.extend(n for n,c in items)
        b=launch(R,batch,runner,items,dict(kind=protocol['kind'],protocol_SHA=sha(P/'PROTOCOL.json'),
            source_index_SHA=sha(P/'SOURCE_PREEXEC.json'),launcher_SHA=sha(Path(__file__)),parent_approval_SHA=approval_sha,
            independent_review_SHA=sha(rpath),selected_TRAIN_not_holdout=True),keys,max_workers=2)
    except BaseException:
        bp=R/'batches'/batch/'BATCH_RESULT.json'
        if bp.is_file():rows.extend(load(bp)['rows'])
        wave_records.append(dict(wave=wave+1,batch=str(bp),failure=traceback.format_exc()))
        finish('SOFTWARE_ABORT_NO_FUTURE_WAVE');raise
    wave_records.append(dict(wave=wave+1,batch=str(R/'batches'/batch/'BATCH_RESULT.json')))
    failures=[];cfg_by_name=dict(items)
    for oldrow in b['rows']:
        row=copy.deepcopy(oldrow)
        try:row['candidate_binding']=validate_case(R,row['case'],cfg_by_name[row['case']],source,spec)
        except Exception:
            row.update(candidate_binding_failure=True,software_failure=True,binding_exception=traceback.format_exc());failures.append(row['case'])
        rows.append(row)
    if failures:finish('CANDIDATE_BINDING_ABORT_NO_FUTURE_WAVE');raise SystemExit(1)
finish('COMPLETE_FIXED_TRAIN')
