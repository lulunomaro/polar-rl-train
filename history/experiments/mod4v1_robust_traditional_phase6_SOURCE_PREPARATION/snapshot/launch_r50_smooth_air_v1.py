"""Nominal smooth-air moving admission, then at most one real first-bar case."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;D=R/'MINIHOP_AIR_RETRACT_V4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'preflight001/RESULT.json').read_bytes());assert a['status']=='PASS_NEW_SMOOTH_AIR_ZERO_STEP_ADMISSION'and a['integrator_calls']==0
for x in json.loads((D/'preflight001/SOURCE_PREEXEC.json').read_bytes())['files']:assert sha(Path(x['path']))==x['SHA']
p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']];assert len(cases)==2
keys=['complete','stop','controls','physics_steps','proposed_moving_flat_air80_stop_v1','proposed_manual_first_bar_clear_stop_v1',
      'forward_progress_m','max_abs_world_y_m','maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks',
      'hard_contact_physics_ticks','max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar',
      'conservative_front_never_reached_next_bar','some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s']
meta=dict(kind=p['kind'],launcher_SHA=sha(Path(__file__)),protocol_SHA=sha(D/'PROTOCOL.json'),not_whole_RM_or_270mm=True,PH6_pending=True)
f=launch(R,'r50a_smooth_air_flat1','run_manual_air_retract_v2.py',cases[:1],meta,keys,max_workers=1)
if f['rows'][0].get('proposed_moving_flat_air80_stop_v1')is True:
    launch(R,'r50b_smooth_air_first_bar1','run_manual_air_retract_v2.py',cases[1:],meta,keys,max_workers=1)
else:dump(D/'RM_DEFERRED.json',dict(reason='new moving-flat admission not passed',unstarted=[cases[1][0]],no_retuning=True))
