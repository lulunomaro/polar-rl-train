"""Locate remaining transfer failures in saved357 rather than start another blind training."""
from pathlib import Path
import hashlib,io,json,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
A=T/'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102'
read=lambda p:json.loads(p.read_bytes())
full=read(A/'reports/ROOT357_EVALUATION_FULL_RETURNED.json');result=full['result'];assert result['passed']
trace=next(json.loads(r['UTF8'])for r in full['full_UTF8']if r['path'].endswith('ACTUAL357_CURRENT_STATE_MPC_CONTROL_TRACE.json'))
groups=[];events=[]
for lo,hi,group in((0,40,'source10ms_prediction_hold20ms'),(40,80,'actual20ms_prediction_hold20ms')):
    per=[]
    for env in range(lo,hi):
        rows=[dict(control=row['control'],**r)for row in trace['rows']for r in row['rows']if r['env']==env]
        out=result['results'][env];recover=next((dict(control=r['control'],seconds=(r['control']-1)*.02,state14=r['source_state14'])for r in rows if r['phase']=='recover'),None)
        item=dict(env=env,group=group,seconds=out['seconds'],cross=out['first_flight_both_cross'],strict=out['strict270_stable'],stable=out['longest_stable_seconds'],full5s=out['full_window'],recover=recover,terminal=out['episode_terminal'],last_phase=rows[-1]['phase'],overflow=out['action_overflow'],max_source_requested_tau=[max(abs(r['tau_requested'][i])for r in rows)for i in range(6)])
        per.append(item);events.append(item)
    groups.append(dict(group=group,cases=40,cross=sum(r['cross']for r in per),strict=sum(r['strict']for r in per),full5s=sum(r['full5s']for r in per),recover=sum(r['recover']is not None for r in per),cross_without_recover=sum(r['cross']and r['recover']is None for r in per),recover_then_orientation=sum(r['recover']is not None and bool((r['terminal']or{}).get('flags',{}).get('bad_orientation'))for r in per),stablemax=max(r['stable']for r in per)))
cases=[]
for row in read(A/'reports/ROOT357_SELECTED_REPLAY_TRANSFERS.json')['cases']:
    raw=Path(row['local_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA']
    with np.load(io.BytesIO(raw),allow_pickle=False)as z:
        root=z['root13'].copy();pos=z['body_position_w'].copy()-np.array(row['origin']);force=z['wheel_contact_xyz'].copy()
    chassis=row['body_names'].index('chassis');wheel=[row['body_names'].index(n)for n in('left_wheel','right_wheel')]
    # Center/radius is a diagnostic approx, original full collision bounds in result remain authoritative.
    wp=pos[:,wheel];front=wp[:,:,0]+.0625;rear=wp[:,:,0]-.0625;bottom=wp[:,:,2]-.0625
    frontproxy=(front>=.8).all(1)&(bottom>=.27).all(1);footproxy=(rear>=.8).all(1)&(bottom>=.269).all(1)
    below=(bottom.min(1)<.269);center=root[:,:3]-np.array(row['origin'])
    cases.append(dict(env=row['env'],seconds=row['seconds'],cross_fullgeometry_authoritative=row['result']['first_flight_both_cross'],strict=row['result']['strict270_stable'],wheel_centers_maxx=wp[:,:,0].max(0).tolist(),minwheelbottom_at_maxx=bottom[np.argmax(wp[:,:,0].min(1))].tolist(),front_center_proxy_true_controls=int(frontproxy.sum()),full_rear_center_proxy_true_controls=int(footproxy.sum()),end_root=center[-1].tolist(),full_wheel_footprint_proxy_not_exact_collision=True,
        interpretation='Front of wheel can cross upper edge while rear footprint has not cleared. Existingcrossflag is provisionaledgeprogress, not sourceMPC fullfootprintcross or stabletop success.'))
out=dict(epoch=time.time(),kind='SAVED357_PHASE_AND_FOOTPRINT_DIAGNOSIS358',passed=True,groups=groups,events=events,selected=cases,
    native_review=dict(completed=True,image=str(A/'RECORDED357_NATIVE_FRAMES/ACTUAL357_MPC_TARGET_BODY_POSE_SEQUENCE.png'),observation='Allselected357case snapshots tipnearplatform, including40on.02model. Frontedgeprogress doesnotshowfullstablelanding.'),
    correction_to_cross_language='339/349/355/357 first_flight_both_cross is per-wheel leading collision-bound crossing duringfirstflight; it is not full footprint overedge. SourceMPC cross checked minimumwheelcenterx-minusradius positive. Keep originalrawflags, use edgeprogress wording, never call13/37/32 successful jumps.',
    timing_result='20ms model adaptation increased full5s13vs7 in its nonpairedgroups; edgeprogress32vs33 and strict0both. Cannot claim completeclockfix or solecausalbenefit.',
    decision='No new training345. First finish fullfootprint/landing diagnosis and compare exactsourcecontrol/gain/nominalplant and staged sameinterface controller. Nextunusedphysicstest should focus on mechanism identified by these actualrows rather than repeat fullrun unchanged.',
    next_design='Target sourcecontroller timing within declared50Hz interface, inspect posture/wheelfootprint and actualPDtorque at firsttop. Consider sourcephase landingsignal preservation with geometry/contact verification; no relaxedcriterion, no directforcebypass or unauthorized100Hzqueuechange.',
    NN=0,SDK=0,physics=0,network=0,account=0,newtrainingGO=False)
path=R/'ACTUAL358_SAVED357_PHASE_FULL_FOOTPRINT_DIAGNOSIS.json'
with path.open('x',encoding='utf8')as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,groups=groups,selected=cases,correction=out['correction_to_cross_language']),indent=2))
