"""Fresh nominal admissions only; a failed flat admission defers RM, not retunes it."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'preflight001/RESULT.json').read_bytes());assert a['status']=='PASS_ZERO_INTEGRATOR_ADMISSION'and a['integrator_calls']==0
sources=json.loads((D/'preflight001/SOURCE_PREEXEC.json').read_bytes())
for row in sources['files']:assert digest(Path(row['path']))==row['SHA'],row['path']
p=json.loads((D/'PROTOCOL.json').read_bytes());configs=[(n,c)for n,c in p['configs']]
assert len(configs)==3 and all(c['nominal']is True for n,c in configs)
dump(D/'LAUNCH_SOURCE_PREEXEC.json',dict(launcher_SHA=digest(Path(__file__)),protocol_SHA=digest(D/'PROTOCOL.json'),
    preflight_result_SHA=digest(D/'preflight001/RESULT.json'),all_admitted_sources_unchanged=True,new_cases_only=True,
    nominal_only=True,no_hardware_actuation=True,PH6_pending=True))
keys=['complete','stop','controls','physics_steps','proposed_moving_flat_air80_stop_v1','proposed_manual_first_bar_clear_stop_v1',
      'forward_progress_m','max_abs_world_y_m','maximum_main_mesh_clearance_during_full_air_m','end_stable_s',
      'guide_contact_physics_ticks','hard_contact_physics_ticks','max_pitch_rad','max_roll_rad',
      'conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'clean_air_both_main_rear_crossing_bar_back_s']
meta=dict(kind=p['kind'],protocol_SHA=digest(D/'PROTOCOL.json'),manual_not_contact_FSM=True,not_whole_RM_qualification=True,PH6_pending=True)
first=launch(R,'r48a_moving_flat1','run_manual_first_bar_v1.py',configs[:1],meta,keys,max_workers=1)
if first['rows'][0].get('proposed_moving_flat_air80_stop_v1')is not True:
    dump(D/'RM_DEFERRED_AFTER_FLAT_ADMISSION.json',dict(reason='new moving-flat engineering gate did not pass; frozen RM timings not consumed',
        actual_flat_case=configs[0][0],unstarted_RM=[n for n,c in configs[1:]],no_retuning=True))
else:
    launch(R,'r48b_first_bar_nominal2','run_manual_first_bar_v1.py',configs[1:],meta,keys,max_workers=2)
