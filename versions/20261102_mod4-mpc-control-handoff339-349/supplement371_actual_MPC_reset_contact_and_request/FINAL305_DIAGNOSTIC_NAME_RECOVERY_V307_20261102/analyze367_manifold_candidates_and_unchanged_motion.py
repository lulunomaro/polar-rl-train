"""Independently verify366 contact candidates against saved363 motion/controls."""
from pathlib import Path
import hashlib,json,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
A=T/'MPC_PLANNED_INITIAL_QUEUE_HOLD_V363_20261102';B=T/'MPC_CONTACT_MANIFOLD_LANDING_AUDIT_V366_20261102'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(A/'reports/ROOT363_EVALUATION_FULL_RETURNED.json');b=read(B/'reports/ROOT366_EVALUATION_FULL_RETURNED.json')
assert a['result']['passed']and b['result']['passed']and not b['wrapper_error']
get=lambda full,name:next(json.loads(v['UTF8'])for v in full['full_UTF8']if v['path'].endswith(name))
ta=get(a,'ACTUAL363_CURRENT_STATE_MPC_CONTROL_TRACE.json');tb=get(b,'ACTUAL366_CURRENT_STATE_MPC_CONTROL_TRACE.json')
assert len(ta['rows'])==len(tb['rows'])==250
control_max=0.;state_max=0.
for ra,rb in zip(ta['rows'],tb['rows']):
    assert ra['control']==rb['control']and len(ra['rows'])==len(rb['rows'])
    for ca,cb in zip(ra['rows'],rb['rows']):
        assert ca['env']==cb['env']and ca['phase']==cb['phase']and ca['launch_time']==cb['launch_time']and ca['top_observed']==cb['top_observed']
        control_max=max(control_max,float(np.max(np.abs(np.array(ca['processed_target'])-cb['processed_target']))))
        state_max=max(state_max,float(np.max(np.abs(np.array(ca['source_state14'])-cb['source_state14']))))
assert control_max==state_max==0
motion=[]
for env in(0,1,40,41):
    za=np.load(A/f'replay/REPLAY363_env{env}.npz',allow_pickle=False);zb=np.load(B/f'replay/REPLAY366_env{env}.npz',allow_pickle=False)
    errors={k:float(np.max(np.abs(za[k]-zb[k])))for k in za.files}
    assert max(errors.values())==0
    motion.append(dict(env=env,all_saved_arrays_exact=True,max_errors=errors))
for ra,rb in zip(a['result']['results'],b['result']['results']):
    assert all(ra[k]==rb[k]for k in('env','controls','seconds','full_window','first_air_events','first_flight_whole_footprint_clear','episode_terminal'))

m=get(b,'ACTUAL366_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json');rows=m['rows'];assert len(rows)==2000
candidates=[]
for result in b['result']['results']:
    if not result['strict270_stable']:continue
    env=result['env'];runs=[];start=None
    for row in rows:
        on=row['steady'][env]and row['active'][env]
        if on and start is None:start=row['tick']
        if not on and start is not None:runs.append((start,row['tick']-1));start=None
    if start is not None:runs.append((start,len(rows)))
    lo,hi=max(runs,key=lambda pair:pair[1]-pair[0]);duration=(hi-lo+1)*.0025
    assert duration>=.5 and abs(duration-result['longest_stable_seconds'])<1e-7
    segment=rows[lo-1:hi];force=np.array([r['top_force_N'][env]for r in segment])
    assert (force>1).all()and all(r['first_flight_wholeclear_latched'][env]and not r['ground_return'][env]and not r['edge_return'][env]for r in segment)
    firstclear=next(r['tick']for r in rows if r['first_flight_wholeclear_latched'][env])
    assert rows[firstclear-1]['current_flight_id'][env]==1
    firststeady=next(r['tick']for r in rows if r['steady'][env])
    assert not result['ground_return_after_clear']and not result['edge_return_after_clear']
    candidates.append(dict(env=env,group=result['kind'],first_flight_wholeclear_time=firstclear*.0025,first_steady_time=firststeady*.0025,
        stable_interval_seconds=[(lo-1)*.0025,hi*.0025],stable_duration=duration,min_top_normal_force_N2=force.min(0).tolist(),
        no_ground_return=True,no_edge_return=True,first_clearance_flight_id=1,total_air_events=result['first_air_events'],
        old_gate_would_reject_ticks=result['old_flightgate_blocked_steady_ticks']))
assert len(candidates)==b['result']['strict_successes']==9

selected=next(r for r in candidates if r['env']==40);lo,hi=selected['stable_interval_seconds'];proof=[]
for row in m['selected_solver_contact_points']:
    if not(lo<=row['tick']*.0025<=hi):continue
    for contact in row['contacts']:
        if contact['env']!=40:continue
        for force,point,normal,sep in zip(contact['force_N'],contact['position_relative'],contact['normal_w'],contact['separation_m']):
            if force>1 and point[2]>.267 and abs(normal[2])>.8:
                assert .8<=point[0]<=3.8 and abs(point[1])<=1 and point[2]<.28
                proof.append(dict(tick=row['tick'],wheel=contact['wheel'],normal_force_N=force,point_relative=point,normal_w=normal,separation_m=sep))
assert len(proof)>20 and {p['wheel']for p in proof}=={0,1}
for root,phase in((A,363),(B,366)):
    closed=read(root/f'reports/ROOT{phase}_ALL_SSH_CLOSED_FREE.json');assert closed['all_owned_SSH_closed']and closed['SESSION_restored']
    full=a if phase==363 else b
    release=get(full,f'ACTUAL{phase}_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json')
    assert release['all_own_children_waited']and release['all_owned_locks_released']

value=dict(epoch=time.time(),kind='ACTUAL367_INDEPENDENT_SAVED366_MANIFOLD_CANDIDATE_VERIFICATION',passed=True,
    groups=b['result']['comparisons'],candidates=candidates,selected_env40_actual_manifold_points=proof,
    measurement_did_not_change_control=dict(all80source_state14_max_error=state_max,all80processed_target_max_error=control_max,all80termination_and_lifetime_exact=True,selected_motion=motion),
    original363raw_zero_success_retained=True,old_failure='stablecounter gated by currentfirst_air==1 after landingbounces; firstflight crossing was not latched into later recovery eligibility',
    corrected_requirements='Firstflight whole authored footprint clearance;actual solvercontact pointson270top andnormals,fullhorizontalfootprint,nonwheel<=1N,strictvxy/vz<=.03,rollpitch<10deg/yaw<.2rad,continuous.5s,no returnground or behindedge',
    native_visual_review=dict(completed=True,image=str(B/'RECORDED366_NATIVE_FRAMES/ACTUAL366_MPC_TARGET_BODY_POSE_SEQUENCE.png'),observation='Actualenv40hasvisibleflightthenbothwheelsonplatformandlateruprightrecovery. Env0/41tiptowardedgeabout1s. Env1landsandrecoverstopbutstrictsteadywindow<.5s.'),
    qualification='9of80 successes for this privileged traditional MPC finite diagnostic on fixed270course/fullDR. Not a depthonlylearnedpolicy,not robustskillgraduation,and not exactsource100Hzreproduction.',
    reset_hold_comparison='legacy7/40versusplannedhold2/40strict;DRsame distributionnotpaired. Physicalinitialholdcorrectionconfirmed but notoverallperformanceimprovement.',
    next='Preserve correctedmeasurement and actualnamedtelemetry; target push/flightangularstate and torqueenvelope with samephysical50/100/400interface, rather than blind345training. A newshort finitecontrollercontrast may limit air wheel request to sourcevoltageenvelope BEFORE inversePD using alreadyobservedwheelvelocity; originalphysicalclip remains.',
    provenance=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in(A/'reports/ROOT363_EVALUATION_FULL_RETURNED.json',B/'reports/ROOT366_EVALUATION_FULL_RETURNED.json')],NN=0,SDK=0,network=0,physics=0,checkpoint_reads=0)
with(R/'ACTUAL367_366_MANIFOLD_CANDIDATES_AND_CONTROL_IDENTITY.json').open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,candidates=len(candidates),groups=b['result']['comparisons'],all80controls_exact=True,selectedmotion_exact=True,env40_actual_top_contact_points=len(proof)),indent=2))
