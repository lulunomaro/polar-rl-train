"""Fresh full D0-D7 TRAIN for the ONE R54 nominal local-gate passing profile.
Selection is after R54 TRAIN, not independently preregistered before it.
No H5 or other holdout data; no replaced failures, relaxed gates or old replay.
"""
from pathlib import Path
import copy,hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/t195_DR_train006'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base_path=R/'results/r54_t195_rm/result.json';rb=base_path.read_bytes();r=json.loads(rb)
assert r['complete']is True and r['proposed_manual_first_bar_clear_stop_v1']is True and r['config']['nominal']is True
assert r['first_flight_main_rear_crossing_bar_back_s']is not None
assert r['guide_contact_physics_ticks']==r['hard_contact_physics_ticks']==0
source=json.loads((R/'MANUAL_FIRST_BAR_V1/takeoff_window005/SOURCE_PREEXEC.json').read_bytes())
refs=source['files']+[dict(path=str(R/'fresh_train_batch_v1.py'),SHA=sha(R/'fresh_train_batch_v1.py'))]
for x in refs:assert sha(Path(x['path']))==x['SHA'],x['path']
base=copy.deepcopy(r['config']);assert base['hop']['trigger_time_s']==1.95 and base['hop']['predicted_air_after_push_s']==.25
cases=[]
for seed in range(4501,4509):
    name=f'r55_t195_RM_DR_{seed}';c=copy.deepcopy(base);c.update(case_id=name,nominal=False,seed=seed,cohort='R55_FRESH_FULLDR_TRAIN_NOT_HOLDOUT');cases.append((name,c))
D.mkdir(exist_ok=False)
dump(D/'SOURCE_PREEXEC.json',dict(files=refs,launcher_SHA=sha(Path(__file__)),base_nominal_result_path=str(base_path),base_result_SHA=hashlib.sha256(rb).hexdigest()))
p=dict(kind='R55_FRESH_FULLDR_FIRST6CMBAR_TRAIN',configs=cases,max_workers=4,
    selection_after_R54_TRAIN='Onlyt195 passed original nominalRMlocalgate; t190failed nextbar envelope and retained. No threshold changes.',
    all_actual_full_D0_D7_on_original_driver=True,sensors_original_100Hz_no_RAW2K_enrichment=True,
    controller_and_guards_unchanged=True,first_flight_cross_recorded_not_added_as_new_success_gate=True,
    no_control_truth_or_DR_parameter_inputs=True,not_independent_holdout=True,
    seed_precheck='Parentgrep batches JSON found no used4501..4508 before writing this plan; launch still enforces new IDs.',
    robot_failures_continue_and_preserved=True,software_errors_stop_unstarted_waves=True,
    original_H1_H2_H4_H5_and_Stage1_immutable=True,archive='Excluded from PH6cutoffR53; PH7pending',
    scope='LOCAL first SCUT6cmbar with manualtimer and stop; not whole9mRM/fullrobustqualification/270mm/hardware')
dump(D/'PROTOCOL.json',p)
keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','forward_progress_m','max_abs_world_y_m',
      'maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks','hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
launch(R,'r55_first_bar_DR8','run_manual_capture_v3.py',cases,dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),
    source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),launcher_SHA=sha(Path(__file__)),max_physics_CPU=4,PH7_pending=True,
    TRAIN_only_not_H5_or_new_holdout=True),keys,max_workers=4)
