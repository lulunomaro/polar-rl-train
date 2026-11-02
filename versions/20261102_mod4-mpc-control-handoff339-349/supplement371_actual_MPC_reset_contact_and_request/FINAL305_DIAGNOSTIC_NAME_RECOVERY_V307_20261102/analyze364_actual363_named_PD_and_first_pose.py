"""Read saved363 facts once. No new model, SDK, inference or physics."""
from pathlib import Path
import hashlib,json,time
import numpy as np

P=Path(__file__).resolve().parent;R=P/'reports';N=P.parent/'MPC_PLANNED_INITIAL_QUEUE_HOLD_V363_20261102'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
full=read(N/'reports/ROOT363_EVALUATION_FULL_RETURNED.json');s=full['result'];assert not full['wrapper_error']and s['passed']
def item(name):return next(json.loads(v['UTF8'])for v in full['full_UTF8']if v['path'].endswith(name))
binding=item('ACTUAL363_NAMED_ACTUATOR_AND_RESET_PARAMETER_MEMORY.json')
trace=item('ACTUAL363_NAMED_ACTUATOR_INPUT_EFFORT_TRACE.json')
controller=item('ACTUAL363_CURRENT_STATE_MPC_CONTROL_TRACE.json')
source_order=['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin']
assert binding['actuators']['legs']['joint_names']==['left_hip','left_crank','right_hip','right_crank']
check=[];max_error=0.
for row in trace['rows']:
    key=row['group'];b=binding['actuators'][key]
    assert row['joint_names']==b['joint_names']
    for j,env in enumerate(row['selected_envs']):
        if not row['active'][j]:continue
        kp=np.array(b['stiffness'][env]);kd=np.array(b['damping'][env])
        raw=kp*(np.array(row['position_target'][j])-row['q'][j])+kd*(np.array(row['velocity_target'][j])-row['dq'][j])
        error=float(np.max(np.abs(raw-row['computed_effort'][j])));max_error=max(error,max_error)
        if row['tick']<=2:check.append(dict(env=env,group=key,tick=row['tick'],names=row['joint_names'],q=row['q'][j],target=row['position_target'][j],requested_original_PD=row['computed_effort'][j],applied=row['applied_effort'][j],formula_error=error))
assert max_error<2e-4,max_error
cases=[]
for row in read(N/'reports/ROOT363_SELECTED_REPLAY_TRANSFERS.json')['cases']:
    z=np.load(row['local_path'],allow_pickle=False);q=z['root13'][:,3:7];rzz=1-2*(q[:,0]**2+q[:,1]**2)
    first=np.flatnonzero(rzz<.95);env=row['env']
    cr=[dict(control=r['control'],**v)for r in controller['rows']for v in r['rows']if v['env']==env]
    onset=next((dict(control=r['control'],time=(r['control']-1)*.02,phase=r['phase'],state14=r['source_state14'])for r in cr if r['phase']=='push'),None)
    cases.append(dict(env=env,group=row['result']['kind'],seconds=row['seconds'],first_Rzz_below95=None if not len(first)else float((first[0]+1)*.02),min_Rzz=float(rzz.min()),first_push=onset,first_flight_whole_footprint=row['result']['first_flight_whole_footprint_clear'],leadingedge=row['result']['first_flight_both_cross'],strict=row['result']['strict270_stable'],end_root_relative=(z['root13'][-1,:3]-np.array(row['origin'])).tolist()))

initial=binding['D4']['legs'];g0=np.array(initial['applied'])[:40];g1=np.array(initial['applied'])[40:]
assert np.array_equal(g0,np.zeros_like(g0))
ids=[binding['joint_names'].index(n)for n in binding['policy_order'][:4]]
assert np.max(np.abs(g1-np.array(binding['initial_physical_q'])[40:][:,ids]))==0
decision='Initialqueue hold correction is physically verified; do not equate removal of firstpulse with landingfix. Assess group outcomes and firstpush posture; maintain no blind345training.'
value=dict(epoch=time.time(),kind='ACTUAL364_SAVED363_NAMED_PD_AND_INITIAL_HOLD_REVIEW',passed=True,
    source_receipt=dict(path=str(N/'reports/ROOT363_EVALUATION_FULL_RETURNED.json'),bytes=(N/'reports/ROOT363_EVALUATION_FULL_RETURNED.json').stat().st_size,SHA=H(N/'reports/ROOT363_EVALUATION_FULL_RETURNED.json')),
    actual_actuator_order=binding['applied_effort_order'],actual_permutation_to_source=[binding['applied_effort_order'].index(n)for n in source_order],
    original360telemetry_correction_confirmed=True,PD_inputs_computed_effort_max_error=max_error,named_first_ticks=check,
    queue_group0_defaultzero=True,queue_group40_plannedactual_exact=True,groups=s['comparisons'],selected_pose=cases,decision=decision,
    strict_requires_contactmanifold_if_candidate=True,DR_exactpaired=False,NN=0,SDK=0,network=0,physics=0,checkpoint_reads=0)
with(R/'ACTUAL364_363_NAMED_PD_RESET_AND_POSE_REVIEW.json').open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,groups=s['comparisons'],actual_actuator_order=binding['applied_effort_order'],PD_formula_max_error=max_error,selected=cases),indent=2))
