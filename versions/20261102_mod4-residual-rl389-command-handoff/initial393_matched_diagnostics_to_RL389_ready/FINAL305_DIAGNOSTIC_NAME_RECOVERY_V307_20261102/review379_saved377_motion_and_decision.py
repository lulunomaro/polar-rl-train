"""Saved377 phase/actuation limits and human-readable continuation decision."""
from pathlib import Path
import hashlib,json,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;N=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102'
full=json.loads((N/'reports/ROOT377_EVALUATION_FULL_RETURNED.json').read_bytes());s=full['result']
assert s['passed']and not full['wrapper_error']
get=lambda name:next(json.loads(x['UTF8'])for x in full['full_UTF8']if x['path'].endswith(name))
tr=get('ACTUAL377_CURRENT_STATE_MPC_CONTROL_TRACE.json');man=get('ACTUAL377_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json')
by=[[]for _ in range(80)]
for step in tr['rows']:
 for r in step['rows']:by[r['env']].append(dict(seconds=step['seconds'],**r))
groups=[]
for low in(0,40):
 air=[r for rr in by[low:low+40]for r in rr if r['phase']in('push','flight','extend')]
 source_wheel=np.array([r['tau_source_requested'][i]for r in air for i in(2,5)])
 issued=np.array([r['tau_requested'][i]for r in air for i in(2,5)])
 target=np.array([r['processed_target'][i]for r in air for i in(2,5)])
 groups.append(dict(group=s['comparisons'][low//40]['group'],air_control_env_count=len(air),source_request_abs_max_Nm=float(abs(source_wheel).max()),issued_request_abs_max_Nm=float(abs(issued).max()),issued_over_nominalwheelpeak=int((abs(issued)>5.77591).sum()),wheel_target60_count=int((abs(target)>=59.999).sum())))
selected=[]
for replay in s['replay']:
 env=replay['env'];local=N/'replay'/Path(replay['path']).name
 with np.load(local,allow_pickle=False)as z:
  root=z['root13'];q=root[:,3:7];rzz=1-2*(q[:,0]**2+q[:,1]**2)
  firsttilt=np.flatnonzero(rzz<.95);start=next((r for r in by[env]if r['phase']=='push'),None)
  firsttop=next((r['tick']*.0025 for r in man['rows']if min(r['top_force_N'][env])>1 and r['active'][env]),None)
  recover=next((r['seconds']for r in by[env]if r['phase']=='recover'),None)
  selected.append(dict(env=env,strict=replay['result']['strict270_stable'],seconds=replay['seconds'],first_push=None if start is None else start['seconds'],push_pitch=None if start is None else start['source_state14'][2],first_Rzz_under95=None if not len(firsttilt)else float((firsttilt[0]+1)*.02),first_two_wheel_actual_top_manifold=firsttop,first_recover=recover,final_root_relative=(root[-1,:3]-replay['origin']).tolist()))
# Matched physical parameters do not imply bitwise matched contact trajectories.
firsttwo=[]
for step in tr['rows'][:2]:
 d={r['env']:r for r in step['rows']};firsttwo.append(dict(control=step['control'],state_max_abs_delta=max(float(np.max(np.abs(np.array(d[i]['source_state14'])-d[i+40]['source_state14'])))for i in range(40)),target_max_abs_delta=max(float(np.max(np.abs(np.array(d[i]['processed_target'])-d[i+40]['processed_target'])))for i in range(40))))
v=dict(epoch=time.time(),kind='ACTUAL379_SAVED377_LIMITS_NATIVE_REVIEW_AND_NEXT_CONTROL_SCOPE',passed=True,groups=s['comparisons'],request_diagnostics=groups,selected_motion=selected,firsttwo_controls=firsttwo,first_control_state_andtargets_exact=True,secondcontrol_motion_divergence_before_request_intervention=True,interpretation='377 matches original per-env backend D0-D7,noise schedule and first measured feedback. After first20ms contacts already differ across world positions/instances; matching parameters does not establish identical full plant state.5/40vs7/40 and6bounded-only/4source-only are small and not decisive. Do not treat3752vs12/p.006 as clean causal evidence;376appendcorrects that.',native_image_review='Current model nativeview reviewed3774x3 sheet: sourceenv7 supported onplatform at2.5and5s; bounded47 tilted/failsnearstep; source11fallsnearstep; bounded51supportedonplatform2.5and5s. Both counterexamples retained. These are recordedactualPhysX poses, noNN/newphysics.',decision='No345/324 neural continuation.373->376->377 targeted initialIMU repair has been executed with safeclose/replay/independent378review. Keep physical PD/queue/DCclip/10mm thresholds unchanged. Feasiblewheelprebound remains optional candidate,notrobustskillfix. Next finitecontrol version must address source100Hz feedback/event timing explicitly and/or log exact initial derived SDK cache/reset consistency before changing controller. First inspect source100Hz/current50Hz push phase timing: sourcepush duration~90.896ms yields10commands vs50Hz5commands. Do not silentlychangequeuecontrol_us; separate100Hz targetcontract or declared100Hzvirtualevent/20mshold required,with0NN/oldasset,andoriginalparentadmission. No identicalrepeat377 or exploratorygain/rewardhorizonhour.',student_status='324closed609finite;339independent0/80;traditional12/80in377notdepthstudentgraduation',model_reads=0,network=0,SDK=0,physics=0,NN=0,account_writes=0)
with(P/'reports/ACTUAL379_377_MOTION_REQUEST_AND_REPAIR_DECISION.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
print(json.dumps(dict(groups=s['comparisons'],request_diagnostics=groups,selected_motion=selected,firsttwo_controls=firsttwo,decision=v['decision']),indent=2))
