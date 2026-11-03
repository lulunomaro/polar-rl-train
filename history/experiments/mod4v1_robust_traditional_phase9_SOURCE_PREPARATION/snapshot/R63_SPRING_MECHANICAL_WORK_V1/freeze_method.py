"""Small-source metadata lock only. Never opens/hashes raw stream bodies."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parent
CASES=['r58_tall0_position_flat','r63_spring_release_nominal_flat']
CODE=['MINIHOP_AUDIT_V2/contact_grade_v2.py','MINIHOP_AUDIT_V2/schema_v2.py','MINIHOP_AUDIT_V2/physics_bridge_minihop_flat_v2.py','physics_bridge_v3.py','run_manual_position_v4.py','SPRING_PUSH_RELEASE_V1/run_manual_spring_push_v1.py']

def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(n,v):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
refs=[rec(ROOT/n)for n in CODE];cases=[];matches=[]
for case in CASES:
 base=ROOT/'results'/case;r=json.loads((base/'result.json').read_bytes());mf=json.loads((base/'SOURCE_MANIFEST.json').read_bytes());refs.extend([rec(base/'result.json'),rec(base/'SOURCE_MANIFEST.json')])
 assert r['complete']and r['controls']==800 and r['physics_steps']==16000 and r['config']['nominal']is True
 mp={str(Path(x['path']).resolve()):x for x in mf['files']}
 needed=CODE[:4]+[CODE[4]if case==CASES[0]else CODE[5]]
 for name in needed:
  p=ROOT/name;a=next(x for x in refs if x['path']==str(p.resolve()));assert str(p.resolve())in mp,(case,name,'missing producer source');assert a['SHA']==mp[str(p.resolve())]['SHA']and a['bytes']==mp[str(p.resolve())]['bytes'];matches.append(dict(case=case,path=str(p),SHA=a['SHA']))
 streams=[]
 for file,key,nrows in [('trace.jsonl','trace_artifact',800),('physics.jsonl','physical_artifact',16000)]:
  p=(base/file).resolve();s=p.stat();assert p==Path(r[key]['path']).resolve()and s.st_size==r[key]['bytes']
  streams.append(dict(path=str(p),relative=p.relative_to(ROOT).as_posix(),bytes=s.st_size,mtime_ns=s.st_mtime_ns,producer_SHA=r[key]['SHA'],SHA_recomputed=False,expected_rows=nrows))
 landing=r['first_landing'];cases.append(dict(case=case,result_config=r['config'],reported=dict(complete=r['complete'],original_pass=r['proposed_moving_flat_air80_stop_v1'],first_air_s=r['first_all_world_air_s'],first_landing_PRE_s=landing['stage_time_s'],first_landing_POST_s=landing['root_post_time_s'],landing_contact_identities=[dict(robot=x['robot_geom'],environment=x['environment_geom'],normal_N=x['normal_N'])for x in landing['contacts']],air_peak_main_mesh_clearance_m=r['maximum_main_mesh_clearance_during_full_air_m'],reported_peak_positive_mechanical_power_W=r['peak_positive_mechanical_power_W'],guide_ticks=r['guide_contact_physics_ticks'],hard_ticks=r['hard_contact_physics_ticks'],end_stable_s=r['end_stable_s']),streams=streams))
method=dict(kind='TWO_EXISTING_NOMINAL_FLAT_SINGLE_PASS_SIGNED_PRE_MECHANICAL_WORK_NOT_BUS_ENERGY',cases=CASES,allowed_raw_paths=[s['relative']for c in cases for s in c['streams']],max_total_rows=33600,each_raw_open_max=1,control_rows_each=800,physical_rows_each=16000,physical_dt_s=.0005,control_dt_s=.01,substeps=20,clock_tolerance_s=1e-8,row6_order=['Lhip','Lcrank','Lwheel','Rhip','Rcrank','Rwheel'],legs=[0,1,3,4],wheels=[2,5],integrand='drivepoint.actual_tau6_Nm * drivepoint.velocity6_rad_s at SAME captured PRE stage. P_i W; W_i=left-Riemann sum(P_i*.0005) J.',sign_split='Per axis before grouping: positive=max(P_i,0), negative=min(P_i,0) signed. Group net=positive+negative; no regeneration credit.',phase='actual control row.phase.phase at index physical.sample_index//20, not hardcoded1.95 or Npush; verify physical_sample_rows and command/post stamp. Keep all observed phases, whole episode includes approach.',time_check='sample_index and drivepoint.physics_tick both equal physical index; stage matches drive time/cache_stages.drive_s and control command+subindex*.0005, rootPOST=stage+.0005; final sample included as [lastPRE,lastPOST). No q/dqPOST reconstruction.',prefix_fields=['time_s','command_time_s','forward_command_m_s','sensor_time_s','sensor_age_s','estimated14','estimated_roll','raw_gyro','raw_proper','encoder_q4','encoder_qd4','wheel_rate_mean2','requested_tau6'],prefix='compare shared100Hz fields at same index strictly BEFORE min(actual first timed_push index), report value count/maxdiff/JSON float bits, not2k bitidentity or a qualification gate.',events='reported old grades preserved; from physical existing air_qualified/air_run_s extract first confirmation, first subsequent total>1N landing, main mesh peak; no newgrade or score mutation.',missing='missing fields/time/schema/nonfinite -> explicit unknown/instrumentation error and saved prefix only, never manufacture0. No retry/raw reread.',no_actions=['model/FK/driver/unit/QA/PHY rerun','otherDR/H5/raw/zip/large hash','gain/score/source edits','q reconstruction','newhypothesis/Git/agent/goal'])
put('METHOD.json',method);put('SOURCE_LOCK.json',dict(kind='PRE_RAW_SMALL_SOURCE_AND_REUSED_PRODUCER_SHA_LOCK',small_refs=refs,producer_source_matches=matches,cases=cases,raw_bodies_opened=0))
print(json.dumps(dict(status='LOCKED_BEFORE_RAW',small_sources=len(refs),producer_matches=len(matches),raw_allowlist=method['allowed_raw_paths'],rows_cap=33600,method_SHA=hashlib.sha256((O/'METHOD.json').read_bytes()).hexdigest(),source_SHA=hashlib.sha256((O/'SOURCE_LOCK.json').read_bytes()).hexdigest()),indent=2))
