"""Two predeclared bar-specific nominal timing TRAIN cases, no hardware."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent;D=R/'MANUAL_BAR_CAPTURE_TIMING_V1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'RESULT.json').read_bytes());assert a['status']=='PASS_ZERO_STEP_BAR_CAPTURE_TIMING'and a['integrator_calls']==0
for x in json.loads((D/'SOURCE_PREEXEC.json').read_bytes())['files']:assert sha(Path(x['path']))==x['SHA']
p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']];assert len(cases)==2 and all(c['nominal']is True and c['scene']=='rm'for n,c in cases)
keys=['complete','stop','controls','physics_steps','proposed_manual_first_bar_clear_stop_v1','forward_progress_m','max_abs_world_y_m',
      'maximum_main_mesh_clearance_during_full_air_m','end_stable_s','guide_contact_physics_ticks','hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s']
launch(R,'r51_bar_capture_nominal2','run_manual_capture_v3.py',cases,dict(kind=p['kind'],launcher_SHA=sha(Path(__file__)),
       frozen_profile_SHA=sha(D/'PROTOCOL.json'),bar_specific_manual_not_contact_FSM=True,H5_unchanged=True,PH6_pending=True),keys,max_workers=2)
