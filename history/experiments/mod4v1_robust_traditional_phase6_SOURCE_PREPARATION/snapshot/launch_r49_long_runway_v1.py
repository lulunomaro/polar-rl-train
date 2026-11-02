"""Later manual timers; keep .15rad and1.2m/s trigger guards unchanged."""
from pathlib import Path
import json,hashlib
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/long_runway002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'RESULT.json').read_bytes());assert a['status']=='PASS_ZERO_STEP_LONG_RUNWAY_ADMISSION'and a['integrator_calls']==0
source=json.loads((D/'SOURCE_PREEXEC.json').read_bytes())
for x in source['old_admitted_sources']:assert sha(Path(x['path']))==x['SHA']
p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']]
flat=[(n,c)for n,c in cases if c['scene']=='flat'];rm=[(n,c)for n,c in cases if c['scene']=='rm']
assert len(flat)==len(rm)==2
keys=['complete','stop','controls','physics_steps','proposed_moving_flat_air80_stop_v1','proposed_manual_first_bar_clear_stop_v1',
      'forward_progress_m','max_abs_world_y_m','maximum_main_mesh_clearance_during_full_air_m','end_stable_s',
      'guide_contact_physics_ticks','hard_contact_physics_ticks','max_pitch_rad','max_roll_rad',
      'conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar','clean_air_both_main_rear_crossing_bar_back_s']
meta=dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),launcher_SHA=sha(Path(__file__)),nominal_only=True,guards_unchanged=True,
          not_whole_RM_qualification=True,H5_unchanged=True,PH6_pending=True)
f=launch(R,'r49a_long_flat2','run_manual_first_bar_v1.py',flat,meta,keys,max_workers=2)
passed={row['case']for row in f['rows']if row.get('proposed_moving_flat_air80_stop_v1')is True}
ready={c['hop']['trigger_time_s']for n,c in flat if n in passed}
admitted=[(n,c)for n,c in rm if c['hop']['trigger_time_s']in ready]
deferred=[n for n,c in rm if c['hop']['trigger_time_s']not in ready]
dump(D/'RM_ADMISSION_DECISION.json',dict(physically_passed_flat_cases=sorted(passed),admitted_RM=[n for n,c in admitted],
    unstarted_deferred_RM=deferred,gate_not_relaxed=True,no_timing_retune=True))
if admitted:launch(R,'r49b_long_first_bar','run_manual_first_bar_v1.py',admitted,meta,keys,max_workers=2)
