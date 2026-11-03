"""New nominal TRAIN launcher: source-locked nested relative entry is supported.
V1/V2/V3/V4 immutable. V5 additionally binds actual candidate artifacts before RM admission. No execution until an actual zero-step result, protocol, full
source lock, independent ready-for-physics review and explicit parent approval.
No controller/plant/model/gate changes here.
"""
from pathlib import Path
import argparse,copy,hashlib,json
from fresh_train_batch_v2 import launch,dump
from candidate_case_evidence_v1 import validate_case
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--plan-dir',type=Path,required=True);ap.add_argument('--expected-status',required=True)
ap.add_argument('--preparer',type=Path,required=True);ap.add_argument('--runner',required=True);ap.add_argument('--batch-prefix',required=True)
ap.add_argument('--review',type=Path,required=True);ap.add_argument('--parent-approval',type=Path,required=True);args=ap.parse_args()
D=(R/args.plan_dir).resolve();prep=(R/args.preparer).resolve();runner=(R/args.runner).resolve()
assert all(p.is_relative_to(R)for p in(D,prep,runner))
rp=Path(args.runner)
assert not rp.is_absolute() and '..' not in rp.parts and rp.suffix=='.py' and runner.is_file()
assert Path(args.batch_prefix).name==args.batch_prefix and args.batch_prefix not in('.','..')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'RESULT.json').read_bytes());assert a['status']==args.expected_status and a['integrator_calls']==0 and a['new_physics_steps']==0
s=json.loads((D/'SOURCE_PREEXEC.json').read_bytes())
source_by_path={Path(x['path']).resolve():x['SHA']for x in s['files']}
assert runner in source_by_path and sha(runner)==source_by_path[runner]
expected_prep=s.get('preparer_SHA',source_by_path.get(prep));assert expected_prep is not None and sha(prep)==expected_prep

def check_sources():
    for x in s['files']:assert sha(Path(x['path']))==x['SHA'],x['path']
check_sources()
review_path=(R/args.review).resolve();approval_path=(R/args.parent_approval).resolve()
assert review_path.is_relative_to(R) and approval_path.is_relative_to(R)
review=json.loads(review_path.read_bytes());assert review['ready_for_physics']is True
for x in review['checked_sources']:assert sha(Path(x['path']))==x['SHA'],x['path']
approval=json.loads(approval_path.read_bytes())
assert approval['approved_for_this_nominal_plan']is True
assert approval['protocol_SHA']==sha(D/'PROTOCOL.json') and approval['source_index_SHA']==sha(D/'SOURCE_PREEXEC.json')
assert approval['review_SHA']==sha(review_path) and approval['launcher_SHA']==sha(Path(__file__))
p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']]
binding=p['candidate_binding']
assert binding['entry_path']==args.runner
def bind_cases(items):
    return [validate_case(R,n,c,s,binding) for n,c in items]
assert 0<len(cases)<=8 and all(c['nominal']is True and c['case_id']==n for n,c in cases)
workers=p.get('max_workers',1);assert type(workers)is int and 1<=workers<=4

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
          sources_SHA=sha(D/'SOURCE_PREEXEC.json'),preparer_SHA=sha(prep),entry_SHA=sha(runner),launcher_SHA=sha(Path(__file__)),
          independent_review_present=True,review_SHA=sha(review_path),parent_approval_SHA=sha(approval_path),
          parent_preexec_admission=True,nominal_only=True,H5_unchanged=True,post_PH7_cutoff_pending=True)
try:
    f=launch(R,args.batch_prefix+'_flat',args.runner,flat,meta,keys,max_workers=workers)
    flat_bindings=bind_cases(flat)
    dump(D/'FLAT_RUNTIME_BINDING.json',dict(status='MATCHES_LOCKED_CANDIDATE',cases=flat_bindings,dynamic_qualification=False))
except BaseException:
    # Do not infer a successful RM admission from a software-aborted flat wave.
    dump(D/'RM_ADMISSION_DECISION.json',dict(status='FLAT_SOFTWARE_OR_CANDIDATE_BINDING_ABORT_NO_RM_LAUNCH',
        unstarted_deferred_RM=[n for n,c in rm],flat_batch_evidence=str(R/'batches'/(args.batch_prefix+'_flat')/'BATCH_RESULT.json'),
        actual_counts_only_from_saved_artifacts_not_duration=True))
    raise
passed={z['case']for z in f['rows']if z.get('proposed_moving_flat_air80_stop_v1')is True}
ready={control_key(c)for n,c in flat if n in passed};admitted=[(n,c)for n,c in rm if control_key(c)in ready]
dump(D/'RM_ADMISSION_DECISION.json',dict(flat_passed_cases=sorted(passed),admitted_RM=[n for n,c in admitted],
    unstarted_deferred_RM=[n for n,c in rm if control_key(c)not in ready],exact_control_profile_match_excluding_scene_terrain_labels=True,success_gate_not_relaxed=True))
if admitted:
    check_sources();assert sha(prep)==expected_prep
    for x in review['checked_sources']:assert sha(Path(x['path']))==x['SHA'],x['path']
    assert sha(approval_path)==meta['parent_approval_SHA']
    launch(R,args.batch_prefix+'_rm',args.runner,admitted,meta,keys,max_workers=workers)
    rm_bindings=bind_cases(admitted)
    dump(D/'RM_RUNTIME_BINDING.json',dict(status='MATCHES_LOCKED_CANDIDATE',cases=rm_bindings,dynamic_qualification=False))
