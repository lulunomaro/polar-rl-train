"""R53 parent-admitted TRAIN, flat first then only matching passed RM config."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/early_landing004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'RESULT.json').read_bytes());assert a['status']=='PASS_ZERO_STEP_R53_TIMING'and a['integrator_calls']==0
s=json.loads((D/'SOURCE_PREEXEC.json').read_bytes())
for x in s['files']:assert sha(Path(x['path']))==x['SHA'],x['path']
p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']]
assert len(cases)==4 and all(c['nominal']is True and c['forward_m_s']==.9 and c['hop']['trigger_time_s']==2. and c['hop']['max_trigger_speed_m_s']==1.2 for n,c in cases)
flat=[(n,c)for n,c in cases if c['scene']=='flat'];rm=[(n,c)for n,c in cases if c['scene']=='rm']
keys=['complete','stop','controls','physics_steps','proposed_moving_flat_air80_stop_v1','proposed_manual_first_bar_clear_stop_v1',
      'forward_progress_m','max_abs_world_y_m','maximum_main_mesh_clearance_during_full_air_m','end_stable_s',
      'guide_contact_physics_ticks','hard_contact_physics_ticks','max_pitch_rad','max_roll_rad',
      'conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
meta=dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),launcher_SHA=sha(Path(__file__)),
          parent_preexec_admission=True,no_claim_of_new_independent_R53_review=True,
          controller_and_guards_unchanged=True,nominal_only=True,not_whole_RM_qualification=True,H5_unchanged=True,PH6_pending=True)
f=launch(R,'r53a_earlier_capture_flat2','run_manual_capture_v3.py',flat,meta,keys,max_workers=2)
passed={row['case']for row in f['rows']if row.get('proposed_moving_flat_air80_stop_v1')is True}
ready={c['hop']['predicted_air_after_push_s']for n,c in flat if n in passed}
admitted=[(n,c)for n,c in rm if c['hop']['predicted_air_after_push_s']in ready]
dump(D/'RM_ADMISSION_DECISION.json',dict(flat_passed_cases=sorted(passed),admitted_RM=[n for n,c in admitted],
    unstarted_deferred_RM=[n for n,c in rm if c['hop']['predicted_air_after_push_s']not in ready],success_gate_not_relaxed=True))
if admitted:
    for x in s['files']:assert sha(Path(x['path']))==x['SHA'],x['path']
    launch(R,'r53b_earlier_capture_rm','run_manual_capture_v3.py',admitted,meta,keys,max_workers=2)
