"""Prepared paired TRAIN launcher, starts only after new R56 nominal RM pass.
New variant on the same8TRAIN seeds as R55; NOT new independent evidence.
No old baseline physics is re-run. Full original DR remains attached once.
"""
from pathlib import Path
import copy,hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;A=R/'MINIHOP_POSITION_TRIGGER_V1/preflight001';D=R/'MINIHOP_POSITION_TRIGGER_V1/paired_train002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base_path=R/'results/r56_position_rm/result.json';br=base_path.read_bytes();r=json.loads(br)
assert r['complete']is True and r['proposed_manual_first_bar_clear_stop_v1']is True and r['config']['nominal']is True
assert r['config']['hop']['position_trigger_enable']is True
review_path=A/'PRE_EXEC_REVIEW.json';review=json.loads(review_path.read_bytes());assert review['ready_for_physics']is True
for x in review['checked_sources']:assert sha(Path(x['path']))==x['SHA'],x['path']
refs=json.loads((A/'SOURCE_PREEXEC.json').read_bytes())['files']
for x in refs:assert sha(Path(x['path']))==x['SHA'],x['path']
base=copy.deepcopy(r['config']);cases=[];paired=[]
position_keys=('position_trigger_enable','position_trigger_distance_m','position_trigger_min_time_s','position_trigger_deadline_s')
def baseline_equivalent(c):
    v=copy.deepcopy(c)
    for k in('case_id','cohort'):v.pop(k,None)
    for k in position_keys:v['hop'].pop(k,None)
    return v
for seed in range(4501,4509):
    name=f'r57_position_RM_DR_{seed}';c=copy.deepcopy(base);c.update(case_id=name,nominal=False,seed=seed,cohort='R57_PAIRED_POSITION_TRAIN_NOT_HOLDOUT')
    op=R/f'results/r55_t195_RM_DR_{seed}/result.json';raw=op.read_bytes();old=json.loads(raw)
    assert baseline_equivalent(c)==baseline_equivalent(old['config'])
    cases.append((name,c));paired.append(dict(seed=seed,baseline_result_path=str(op),baseline_SHA=hashlib.sha256(raw).hexdigest(),baseline_physics_not_rerun=True))
D.mkdir(exist_ok=False)
dump(D/'SOURCE_PREEXEC.json',dict(files=refs,launcher_SHA=sha(Path(__file__)),review_SHA=sha(review_path),nominal_admission_result_SHA=hashlib.sha256(br).hexdigest(),paired_baselines=paired))
p=dict(kind='R57_PAIRED_MANUAL_POSITION_FULLDR_TRAIN',configs=cases,max_workers=4,
    only_control_change='Manual measured relative odometry1.18m schedules nexttick trigger; fixedV3 durations/guards/gains/drivers/gates unchanged',
    same8TRAINseeds_not_16_independent_trials=True,old_R55_results_immutable_no_baseline_replay=True,
    full_original_D0_D7_once=True,original_100Hz_sensor_chain_no_RAW2K=True,no_control_truth_or_DR_parameter_inputs=True,
    robot_failures_preserved_and_continue=True,software_errors_stop_unstarted_waves=True,
    H1_H2_H4_H5_and_Stage1_unchanged=True,PH7_pending=True,
    scope='manual local first6cmbar, not wholeRM/270mm/realboard/independentholdout')
dump(D/'PROTOCOL.json',p)
keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','forward_progress_m','max_abs_world_y_m',
      'maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks','hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
launch(R,'r57_position_paired_DR8','run_manual_position_v4.py',cases,dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),
    source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),launcher_SHA=sha(Path(__file__)),max_physics_CPU=4,PH7_pending=True,
    paired_TRAIN_only_not_independent_holdout=True),keys,max_workers=4)
