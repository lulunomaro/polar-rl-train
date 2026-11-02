"""Summarize new368 finite control contrast; verify actual contact successes."""
from pathlib import Path
import hashlib,json,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';N=T/'MPC_AIR_WHEEL_REQUEST_ENVELOPE_V368_20261102'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
full=read(N/'reports/ROOT368_EVALUATION_FULL_RETURNED.json');s=full['result'];assert s['passed']and not full['wrapper_error']
get=lambda n:next(json.loads(v['UTF8'])for v in full['full_UTF8']if v['path'].endswith(n))
trace=get('ACTUAL368_CURRENT_STATE_MPC_CONTROL_TRACE.json');manifold=get('ACTUAL368_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json')
checks=[];groups=[];candidates=[]
for low,high in((0,40),(40,80)):
    rs=[dict(control=r['control'],**v)for r in trace['rows']for v in r['rows']if low<=v['env']<high]
    air=[r for r in rs if r['phase']in('push','flight','extend')]
    for row in rs:
        source=np.array(row['tau_source_requested']);current=np.array(row['tau_requested'])
        if row['wheel_request_prebounded']:
            assert low==40 and row['phase']in('push','flight','extend')
            assert np.array_equal(source[[0,1,3,4]],current[[0,1,3,4]])
        else:assert np.array_equal(source,current)
    groups.append(dict(group=s['comparisons'][low//40]['group'],air_phase_control_envs=len(air),source_requested_wheel_over5_7759=sum(any(abs(r['tau_source_requested'][i])>5.77591 for i in(2,5))for r in air),issued_requested_wheel_over5_7759=sum(any(abs(r['tau_requested'][i])>5.77591 for i in(2,5))for r in air),processed_target60=sum(any(abs(r['processed_target'][i])>=59.999 for i in(2,5))for r in air),max_source_requested_wheel=max(abs(r['tau_source_requested'][i])for r in air for i in(2,5)),max_issued_requested_wheel=max(abs(r['tau_requested'][i])for r in air for i in(2,5))))
for result in s['results']:
    if not result['strict270_stable']:continue
    env=result['env'];rows=manifold['rows'];start=None;runs=[]
    for row in rows:
        good=row['steady'][env]and row['active'][env]
        if good and start is None:start=row['tick']
        if not good and start is not None:runs.append((start,row['tick']-1));start=None
    if start is not None:runs.append((start,len(rows)))
    lo,hi=max(runs,key=lambda q:q[1]-q[0]);duration=(hi-lo+1)*.0025;assert duration>=.5
    segment=rows[lo-1:hi];forces=np.array([r['top_force_N'][env]for r in segment]);assert (forces>1).all()
    assert all(r['first_flight_wholeclear_latched'][env]and not r['ground_return'][env]and not r['edge_return'][env]for r in segment)
    candidates.append(dict(env=env,group=result['kind'],stable_interval=[(lo-1)*.0025,hi*.0025],stable_duration=duration,min_top_normal_force_N2=forces.min(0).tolist(),first_flight_whole_footprint=True,no_ground_or_edge_return=True))
assert len(candidates)==s['strict_successes']
selected=[]
for row in read(N/'reports/ROOT368_SELECTED_REPLAY_TRANSFERS.json')['cases']:
    z=np.load(row['local_path'],allow_pickle=False);q=z['root13'][:,3:7];rzz=1-2*(q[:,0]**2+q[:,1]**2);idx=np.flatnonzero(rzz<.95)
    selected.append(dict(env=row['env'],group=row['result']['kind'],seconds=row['seconds'],strict=row['result']['strict270_stable'],first_Rzz_below95=None if not len(idx)else float((idx[0]+1)*.02),end_root_relative=(z['root13'][-1,:3]-np.array(row['origin'])).tolist()))
release=get('ACTUAL368_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json');assert release['all_own_children_waited']and release['all_owned_locks_released']
closed=read(N/'reports/ROOT368_ALL_SSH_CLOSED_FREE.json');assert closed['all_owned_SSH_closed']and closed['SESSION_restored']
value=dict(epoch=time.time(),kind='ACTUAL369_SAVED368_CONTROL_CONTRAST_AND_MANIFOLD',passed=True,groups=s['comparisons'],request_diagnostics=groups,strict_candidates=candidates,selected_pose=selected,
    fullDR_same_distribution_not_exactpaired=True,not_causal_or_robustness_graduation=True,NN=0,SDK=0,network=0,physics=0,optimizer=0,checkpoint_reads=0,account=0,
    previous366_successes9_are_traditional_MPC_only=True,trained324_depthreference_actor_remains0of80=True,
    source_receipt=dict(path=str(N/'reports/ROOT368_EVALUATION_FULL_RETURNED.json'),bytes=(N/'reports/ROOT368_EVALUATION_FULL_RETURNED.json').stat().st_size,SHA=H(N/'reports/ROOT368_EVALUATION_FULL_RETURNED.json')))
with(R/'ACTUAL369_368_REQUEST_ENVELOPE_MANIFOLD_RESULTS.json').open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,groups=s['comparisons'],request_diagnostics=groups,strict_candidates=candidates,selected=selected),indent=2))
