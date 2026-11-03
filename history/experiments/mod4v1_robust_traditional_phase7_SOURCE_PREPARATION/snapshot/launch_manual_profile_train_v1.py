"""Reusable parent-admitted nominal TRAIN: flat first, exact-control-matched RM.
Not an independent-HOLDOUT launcher. No control/physics algorithm changes.
"""
from pathlib import Path
import argparse,copy,hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--plan-dir',type=Path,required=True);ap.add_argument('--expected-status',required=True)
ap.add_argument('--preparer',type=Path,required=True);ap.add_argument('--batch-prefix',required=True);args=ap.parse_args()
D=(R/args.plan_dir).resolve();assert D.is_relative_to(R)and Path(args.batch_prefix).name==args.batch_prefix
prep=(R/args.preparer).resolve();assert prep.is_relative_to(R)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'RESULT.json').read_bytes());assert a['status']==args.expected_status and a['integrator_calls']==0 and a['new_physics_steps']==0
s=json.loads((D/'SOURCE_PREEXEC.json').read_bytes());assert sha(prep)==s['preparer_SHA']
def check_sources():
    for x in s['files']:assert sha(Path(x['path']))==x['SHA'],x['path']
check_sources();p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']]
assert 0<len(cases)<=8 and all(c['nominal']is True and c['case_id']==n for n,c in cases)
def control_key(c):
    v=copy.deepcopy(c)
    for k in('scene','case_id','cohort','terrain_seed','terrain_difficulty'):v.pop(k,None)
    return json.dumps(v,sort_keys=True,allow_nan=False,separators=(',',':'))
flat=[(n,c)for n,c in cases if c['scene']=='flat'];rm=[(n,c)for n,c in cases if c['scene']=='rm']
assert flat and rm and len(flat)==len(rm) and len(flat)+len(rm)==len(cases)
assert len({control_key(c)for n,c in flat})==len(flat)
assert {control_key(c)for n,c in flat}=={control_key(c)for n,c in rm}
keys=['complete','stop','controls','physics_steps','proposed_moving_flat_air80_stop_v1','proposed_manual_first_bar_clear_stop_v1',
      'forward_progress_m','max_abs_world_y_m','maximum_main_mesh_clearance_during_full_air_m','end_stable_s',
      'guide_contact_physics_ticks','hard_contact_physics_ticks','max_pitch_rad','max_roll_rad',
      'conservative_final_robot_all_collision_behind_bar','conservative_front_never_reached_next_bar',
      'some_operational_air_main_rear_crossing_s','first_flight_main_rear_crossing_bar_back_s','first_all_world_air_s']
meta=dict(kind=p['kind'],protocol_SHA=sha(D/'PROTOCOL.json'),preexec_result_SHA=sha(D/'RESULT.json'),
          sources_SHA=sha(D/'SOURCE_PREEXEC.json'),preparer_SHA=sha(prep),launcher_SHA=sha(Path(__file__)),
          parent_preexec_admission_only=True,no_new_independent_review_claim=True,nominal_only=True,H5_unchanged=True,PH6_pending=True)
f=launch(R,args.batch_prefix+'_flat','run_manual_capture_v3.py',flat,meta,keys,max_workers=2)
passed={z['case']for z in f['rows']if z.get('proposed_moving_flat_air80_stop_v1')is True}
ready={control_key(c)for n,c in flat if n in passed};admitted=[(n,c)for n,c in rm if control_key(c)in ready]
dump(D/'RM_ADMISSION_DECISION.json',dict(flat_passed_cases=sorted(passed),admitted_RM=[n for n,c in admitted],
    unstarted_deferred_RM=[n for n,c in rm if control_key(c)not in ready],exact_control_profile_match_excluding_scene_terrain_labels=True,success_gate_not_relaxed=True))
if admitted:
    check_sources();assert sha(prep)==s['preparer_SHA']
    launch(R,args.batch_prefix+'_rm','run_manual_capture_v3.py',admitted,meta,keys,max_workers=2)
