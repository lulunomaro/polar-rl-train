"""Conditional four-case TRAIN, selected before new nominal physics.
No baseline replay, hidden retuning, or launch without independent review and
an explicit parent approval binding this exact script and the source index.
"""
from pathlib import Path
import argparse,copy,hashlib,json,math
from fresh_train_batch_v2 import launch,dump
from r62_nominal_evidence_v1 import validate_enabled_nominals
R=Path(__file__).resolve().parent;D=R/'R62_AIRREF_ADMISSION_V2';P=R/'R62_AIRREF_PAIRED_TRAIN_V2'
SEEDS=(4602,4605,4606,4610)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
ap=argparse.ArgumentParser();ap.add_argument('--parent-approval',type=Path,required=True);ap.add_argument('--review',type=Path,required=True);args=ap.parse_args()
approval_path=(R/args.parent_approval).resolve();review_path=(R/args.review).resolve()
assert approval_path.is_relative_to(R) and review_path.is_relative_to(R)
approval=load(approval_path);review=load(review_path)
assert approval['approved_for_fixed_paired_TRAIN']is True and approval['seeds']==list(SEEDS)
assert approval['launcher_SHA']==sha(Path(__file__)) and approval['source_index_SHA']==sha(D/'SOURCE_PREEXEC.json') and approval['review_SHA']==sha(review_path)
assert review['ready_for_fixed_paired_TRAIN']is True
for z in review['checked_sources']:assert sha(z['path'])==z['SHA'],z['path']
sources=load(D/'SOURCE_PREEXEC.json')['files']
for z in sources:assert sha(z['path'])==z['SHA'],z['path']
flatp=R/'results/r62_airref002_nominal_flat/result.json';rmp=R/'results/r62_airref002_nominal_rm/result.json'
flat=load(flatp);rm=load(rmp)
assert approval['flat_result_SHA']==sha(flatp) and approval['RM_result_SHA']==sha(rmp)
fm=flatp.parent/'SOURCE_MANIFEST.json';mm=rmp.parent/'SOURCE_MANIFEST.json'
assert approval['flat_manifest_SHA']==sha(fm) and approval['RM_manifest_SHA']==sha(mm)
nominal_binding=validate_enabled_nominals(R,load(D/'PROTOCOL.json'),sources,flat,rm,load(fm),load(mm))
runner='MINIHOP_AIR_PITCH_REF_V1/attempt002/run_manual_air_pitch_ref_v1.py'
assert any(Path(z['path']).resolve()==R/runner and sha(R/runner)==z['SHA']for z in sources)
cases=[];baseline=[]
def key(c):
    c=copy.deepcopy(c)
    for k in('case_id','cohort','nominal','seed'):c.pop(k,None)
    c['hop'].pop('air_pitch_ref_enable',None)
    return c
for seed in SEEDS:
    bp=R/f'results/r60_tall0_fresh_RM_DR_{seed}/result.json';old=load(bp)
    assert old['complete']is True and old['config']['seed']==seed and old['config']['nominal']is False
    assert key(old['config'])==key(rm['config'])
    name=f'r62_airref002_paired_RM_DR_{seed}';c=copy.deepcopy(old['config'])
    c.update(case_id=name,cohort='R62_POST_R60_OUTCOME_BALANCED_PAIRED_TRAIN_NOT_HOLDOUT')
    c['hop']['air_pitch_ref_enable']=True
    assert not(R/'results'/name).exists()
    cases.append((name,c));baseline.append(dict(seed=seed,case=old['config']['case_id'],path=str(bp),SHA=sha(bp),
        local_pass=old['proposed_manual_first_bar_clear_stop_v1'],guide=old['guide_contact_physics_ticks'],hard=old['hard_contact_physics_ticks']))
assert sum(z['local_pass']for z in baseline)==2
P.mkdir(exist_ok=False)
protocol=dict(kind='R62_AIRREF002_FOUR_PAIRED_TRAIN_CONDITIONAL',configs=cases,max_workers=2,
    selection='After old R60 TRAIN outcomes but before this candidate physics:two baselinepassed4602/4610,guide4605,hard4606. Selected mechanism cohort, NOT independent holdout.',
    baseline_small_results=baseline,nominal_admission_result_SHA=dict(flat=sha(flatp),rm=sha(rmp)),
    extra_nominal_mainfirstflight_admission_not_original_score_rewrite=True,all_old_gates_and_D0_D7_driver_sensor_unchanged=True,
    no_insidebatch_changes_or_seed_replacements=True,robot_failures_continue_planned_cases_software_errors_stop_waves=True,
    no_old_raw_or_baseline_replay=True,actual_nominal_binding=nominal_binding,PH8_pending=True)
dump(P/'PROTOCOL.json',protocol)
dump(P/'SOURCE_PREEXEC.json',dict(files=sources,launcher_SHA=sha(Path(__file__)),parent_approval_SHA=sha(approval_path),review_SHA=sha(review_path)))
keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','forward_progress_m','max_abs_world_y_m',
      'maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks','hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
launch(R,'r62_airref002_paired_DR4',runner,cases,dict(kind=protocol['kind'],protocol_SHA=sha(P/'PROTOCOL.json'),
    source_index_SHA=sha(P/'SOURCE_PREEXEC.json'),launcher_SHA=sha(Path(__file__)),parent_approval_SHA=sha(approval_path),
    independent_review_SHA=sha(review_path),max_physics_CPU=2,selected_TRAIN_not_holdout=True,PH8_pending=True),keys,max_workers=2)
