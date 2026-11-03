"""Freeze Tall0 candidate before16fresh TRAIN seeds; not an H6 holdout.
Do not keep tuning only the remaining1ms guide event of the original8seeds.
"""
from pathlib import Path
import copy,hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;A=R/'MINIHOP_POSITION_TRIGGER_V1/tall0_profile003';D=R/'MINIHOP_POSITION_TRIGGER_V1/tall0_fresh_train005'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
basep=R/'results/r58_tall0_position_rm/result.json';rb=basep.read_bytes();base_result=json.loads(rb)
assert base_result['complete']is True and base_result['proposed_manual_first_bar_clear_stop_v1']is True
assert base_result['config']['landing_gain']=={'file':'TALL_ROUGH_BANK_V1/gain_delta0.json'}
train=json.loads((R/'batches/r59_tall0_paired_DR8/BATCH_RESULT.json').read_bytes());assert train['executed']==8 and not train['unstarted']
old_results=[]
for z in train['rows']:
    assert z['returncode']==0
    p=Path(z['result_path']);raw=p.read_bytes();r=json.loads(raw)
    old_results.append(dict(case=z['case'],result_SHA=hashlib.sha256(raw).hexdigest(),local_pass=r['proposed_manual_first_bar_clear_stop_v1'],guide_ticks=r['guide_contact_physics_ticks']))
assert sum(x['local_pass']for x in old_results)==7
refs=json.loads((A/'SOURCE_PREEXEC.json').read_bytes())['files']
for x in refs:assert sha(Path(x['path']))==x['SHA'],x['path']
cases=[]
for seed in range(4601,4617):
    name=f'r60_tall0_fresh_RM_DR_{seed}';c=copy.deepcopy(base_result['config']);c.update(case_id=name,nominal=False,seed=seed,cohort='R60_FRESH_TRAIN_NOT_HOLDOUT');cases.append((name,c))
D.mkdir(exist_ok=False)
dump(D/'SOURCE_PREEXEC.json',dict(files=refs,launcher_SHA=sha(Path(__file__)),nominal_admission_SHA=hashlib.sha256(rb).hexdigest(),prior_TRAIN8=old_results))
p=dict(kind='R60_TALL0_FROZEN_CANDIDATE_FRESH16_TRAIN',configs=cases,max_workers=4,
    selection='PostR59TRAIN original local7/8 vsR57local6/8, no local regression relativeR57, same8paired; not a preregistered selection rule before priorTRAIN.',
    fresh_seeds_not_in_previous_batches=True,not_independent_H6_holdout=True,
    candidate_source_gain_and_config_frozen_before_this_batch=True,no_changes_during_or_after_failures_in_this_batch=True,
    original_full_D0_D7_and_driver_and_100Hz_sensors=True,all_original_contact_and_geometry_gates_unchanged=True,
    all_robot_failures_preserved_and_continue=True,software_errors_stop_future_waves_no_replacement=True,
    no_H1_H2_H4_H5_or_Stage1_changes=True,no_truth_or_DR_parameters_used_by_controller=True,
    scope='manual relativeodometry, local known firstSCUT6cmbar, .9mps approach and stop; not wholearena/270mm/hardware',PH7_pending=True)
dump(D/'PROTOCOL.json',p)
keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','forward_progress_m','max_abs_world_y_m',
      'maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks','hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
launch(R,'r60_tall0_fresh_DR16','run_manual_position_v4.py',cases,dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),
    source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),launcher_SHA=sha(Path(__file__)),max_physics_CPU=4,freshTRAIN_not_holdout=True,PH7_pending=True),keys,max_workers=4)
