"""R52 reviewed TRAIN: flat first, same predeclared profile RM only if passed."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1/early_takeoff003'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'RESULT.json').read_bytes());assert a['status']=='PASS_ZERO_STEP_R52_PROFILE'and a['integrator_calls']==0
review_path=D/'PRE_EXEC_REVIEW.json';review=json.loads(review_path.read_bytes());assert review['ready_for_physics']is True
for x in review['checked_sources']:assert sha(Path(x['path']))==x['SHA'],x['path']
s=json.loads((D/'SOURCE_PREEXEC.json').read_bytes())
for x in s['files']+s['additional_old_admitted_files']:assert sha(Path(x['path']))==x['SHA'],x['path']
p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']]
assert len(cases)==2 and all(c['nominal']is True and c['forward_m_s']==.9 and c['hop']['trigger_time_s']==2. and c['hop']['max_trigger_speed_m_s']==1.2 for n,c in cases)
flat=[(n,c)for n,c in cases if c['scene']=='flat'];rm=[(n,c)for n,c in cases if c['scene']=='rm'];assert len(flat)==len(rm)==1
keys=['complete','stop','controls','physics_steps','proposed_moving_flat_air80_stop_v1','proposed_manual_first_bar_clear_stop_v1',
      'forward_progress_m','max_abs_world_y_m','maximum_main_mesh_clearance_during_full_air_m','end_stable_s',
      'guide_contact_physics_ticks','hard_contact_physics_ticks','max_pitch_rad','max_roll_rad',
      'conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s','first_landing']
meta=dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),review_SHA=sha(review_path),launcher_SHA=sha(Path(__file__)),
          controller_and_guards_unchanged=True,nominal_only=True,not_whole_RM_qualification=True,H5_unchanged=True,PH6_pending=True)
f=launch(R,'r52a_early_takeoff_flat1','run_manual_capture_v3.py',flat,meta,keys,max_workers=1)
ready=len(f['rows'])==1 and f['rows'][0].get('proposed_moving_flat_air80_stop_v1')is True
dump(D/'RM_ADMISSION_DECISION.json',dict(flat_case=f['rows'][0]['case'],passed_original_flat_gate=ready,
    admitted_RM=[n for n,c in rm]if ready else [],unstarted_deferred_RM=[]if ready else [n for n,c in rm],success_gate_not_relaxed=True))
if ready:
    for x in s['files']+s['additional_old_admitted_files']:assert sha(Path(x['path']))==x['SHA'],x['path']
    launch(R,'r52b_early_takeoff_rm1','run_manual_capture_v3.py',rm,meta,keys,max_workers=1)
