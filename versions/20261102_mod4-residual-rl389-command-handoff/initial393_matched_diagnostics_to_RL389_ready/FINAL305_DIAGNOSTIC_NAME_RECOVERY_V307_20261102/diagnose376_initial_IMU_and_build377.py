"""Preserve373 results; repair stale initial derived IMU caches in independent377."""
from pathlib import Path
import ast,hashlib,json,shutil,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;OLD=T/'MPC_MATCHED_DR_AIR_REQUEST_V373_20261102';N=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
full=json.loads((OLD/'reports/ROOT373_EVALUATION_FULL_RETURNED.json').read_bytes())
get=lambda n:next(json.loads(x['UTF8'])for x in full['full_UTF8']if x['path'].endswith(n))
tr=get('ACTUAL373_CURRENT_STATE_MPC_CONTROL_TRACE.json');rr={r['env']:r for r in tr['rows'][0]['rows']}
first=[]
for i in range(40):
 delta=np.array(rr[i]['source_state14'])-rr[i+40]['source_state14']
 first.append(dict(pair=i,first_state_delta=delta.tolist(),max_abs=float(abs(delta).max()),first_target_delta=float(np.max(np.abs(np.array(rr[i]['processed_target'])-rr[i+40]['processed_target'])))))
sdk=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/saved_actual_SDK_source/actual_physx_articulation_data_for_R5_tensor_view.py.txt'
source=sdk.read_text('utf8');assert 'if self._root_com_ang_vel_b.timestamp < self._sim_timestamp:'in source and 'if self._projected_gravity_b.timestamp < self._sim_timestamp:'in source
put(P/'reports/ACTUAL376_373_FIRST_IMU_MATCH_FAILURE_AND_REPAIR.json',dict(epoch=time.time(),kind='ACTUAL376_FIRST_IMU_CACHE_MATCH_FAILURE',passed_diagnostic=True,actual373_execution_and14manifold_successes_preserved=True,DRbackend_pair_match=True,noise_pair_match=True,initial_q_dq_root_exact=True,first_controller_state_match=False,pairs=first,first_max_state_delta=max(x['max_abs']for x in first),first_max_target_delta=max(x['first_target_delta']for x in first),source_evidence=dict(path=str(sdk),SHA=H(sdk)),finding='Source SDK caches projected_gravity_b and root_com_ang_vel_b by simulation timestamp. Planned reset rewrites pose/velocity without advancing time; matching COM helper invalidates root_link_ang_vel_b but omits root_com_ang_vel_b and projected_gravity_b.373 firstcontrol only IMU-derived slots differ, motor q/dq and rootstate slots match. New377 refreshes those existing derived caches then reuses originalD1-D3. No changing state/noise/delay/physics or copying measured futurevalues.',statistical_correction='375 nominal McNemar p is descriptive only; initial measured IMU mismatch prevents clean single-intervention causal claim. Keep375 raw and append this correction.',native_review='373env1/7 fall nearstep, paired41/47 recover on270platform at2.5and5s; contact0.7025/0.6575s verified.',no_model=True,network=0,SDK=0,physics=0))
assert not N.exists();N.mkdir();(N/'reports').mkdir();shutil.copytree(OLD/'source',N/'source',ignore=shutil.ignore_patterns('__pycache__'))
for old,new in [('contract373.py','contract377.py'),('target373_parent.py','target377_parent.py'),('run373_probe_once.py','run377_probe_once.py'),('view373_actual_MPC_target_replay.py','view377_actual_MPC_target_replay.py'),('render373_recorded_frames.py','render377_recorded_frames.py')]:
 (N/new).write_text((OLD/old).read_text('utf8').replace('373','377'),encoding='utf8')
for name in ('evaluate373.py','planned_hold373.py','matched_DR373.py'):
 p=N/'source'/name;s=p.read_text('utf8').replace('373','377');p.unlink();(N/'source'/name.replace('373','377')).write_text(s,encoding='utf8')
for name in ('planned_mpc_motor373.json','source353_gains.json','reference324.npz'):shutil.copyfile(OLD/name,N/name.replace('373','377'))
p=N/'source/matched_DR377.py';s=p.read_text('utf8')
old=" # Refresh existing D1-D3 policy cache at the current tick; no physical step.\n env.observation_manager.compute_group('policy')"
new=""" # Planned state writes do not advance SDK time. Refresh derived IMU values
 # from the current measured root pose/velocity, then original D1-D3 applies.
 refreshed=[]
 for name in ('_root_com_ang_vel_b','_root_link_ang_vel_b','_projected_gravity_b'):
  assert hasattr(robot.data,name),name
  getattr(robot.data,name).timestamp=-float('inf');refreshed.append(name)
 policy=env.observation_manager.compute_group('policy').clone()
 sensor_pair_delta=float((policy[:40,4:22]-policy[40:,4:22]).abs().max())
 assert sensor_pair_delta<1e-6,('Initial measured D1-D3 channels differ',sensor_pair_delta)
"""
assert old in s;s=s.replace(old,new);s=s.replace('initial_q_exact=True,initial_dq_exact=True,','initial_q_exact=True,initial_dq_exact=True,derived_IMU_caches_refreshed=refreshed,first_policy_feedback_max_delta=sensor_pair_delta,')
p.write_text(s,encoding='utf8')
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
task=json.loads(json.dumps(json.loads((OLD/'TASK373_FROZEN.json').read_bytes())).replace('373','377'))
task['human_request']='New377 repairs stale plannedinitial derivedIMU caches discovered in373; actual initial measured D1-D3 channels must match before first control.40matchedDR pairs source vs boundedrequest, same50/100/400Hz, zeroNN/account.'
task['distinct_evaluation_purpose']='New finite377 after consumed373 firstIMU mismatch; original373 results and375 descriptive p retained.'
task['initial_measured_IMU_pair_admission']=True;task['worker_SHA']=H(N/'source/evaluate377.py')
put(N/'TASK377_FROZEN.json',task)
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()]
put(N/'INDEX377_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=files,new377_not373_replay=True,zeroNN=True))
put(P/'reports/STATIC376_FROZEN377_IMU_REPAIR_VALIDATION.json',dict(epoch=time.time(),passed=True,root=str(N),files=len(files),index_SHA=H(N/'INDEX377_SOURCE_TASK_CALLERS_FROZEN.json'),worker_SHA=task['worker_SHA'],new_physics_admission_before_controls=True,only_change_vs373='Refresh3existingderivedIMUcachetimestamps,initialD1D3paircheckbeforefirstcontrol',sourcecontroller_exact=H(N/'source/source_event_mpc353.py')==H(OLD/'source/source_event_mpc353.py'),source373_frozen_untouched=True,network=0,SDK=0,physics=0))
print(json.dumps(dict(passed=True,root=str(N),index_SHA=H(N/'INDEX377_SOURCE_TASK_CALLERS_FROZEN.json'),first373_state_delta=max(x['max_abs']for x in first))))
