"""Analyze actual355 saved controller and recorded poses; no new physics or model."""
from pathlib import Path
import hashlib,io,json,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
A=T/'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'
read=lambda p:json.loads(p.read_bytes())
full=read(A/'reports/ROOT355_EVALUATION_FULL_RETURNED.json');result=full['result'];assert result['passed']
trace=next(json.loads(r['UTF8'])for r in full['full_UTF8']if r['path'].endswith('ACTUAL355_CURRENT_STATE_MPC_CONTROL_TRACE.json'))
controls={env:[dict(control=row['control'],**r)for row in trace['rows']for r in row['rows']if r['env']==env]for env in range(40,80)}
events=[]
for env,rows in controls.items():
    events.append(dict(env=env,launched=any(r['launch_time']is not None for r in rows),launch_time=next((r['launch_time']for r in rows if r['launch_time']is not None),None),
        first_recover=next((dict(control=r['control'],seconds=(r['control']-1)*.02,x14=r['source_state14'],tau=r['tau_requested'])for r in rows if r['phase']=='recover'),None),
        last=rows[-1],actual_result=result['results'][env]))
cases=[]
for row in read(A/'reports/ROOT355_SELECTED_REPLAY_TRANSFERS.json')['cases']:
    p=Path(row['local_path']);raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA']
    with np.load(io.BytesIO(raw),allow_pickle=False)as z:root=z['root13'].copy();q=z['motor_q'].copy();qd=z['motor_dq'].copy();force=z['wheel_contact_xyz'].copy()
    positions=root[:,:3]-np.array(row['origin']);rz=1-2*(root[:,3]**2+root[:,4]**2)
    last=min(25,len(root));tail=root[-last:];tailp=positions[-last:]
    perenv=[x for x in events if x['env']==row['env']]
    cases.append(dict(env=row['env'],seconds=row['seconds'],cross=row['result']['first_flight_both_cross'],strict=row['result']['strict270_stable'],end_local_xyz=positions[-1].tolist(),max_x=float(positions[:,0].max()),max_z=float(positions[:,2].max()),last_halfsecond_speed_mean=float(np.linalg.norm(tail[:,7:10],axis=-1).mean()),last_halfsecond_Rzz_min=float(rz[-last:].min()),last_halfsecond_x_range=[float(tailp[:,0].min()),float(tailp[:,0].max())],net_wheel_vertical_force_mean_last_half=force[-last:,:,2].mean(0).tolist(),first_recover=perenv[0]['first_recover']if perenv else None,scope='actual355recordedposes; netforcesnotcontactmanifold'))
solvers=[r['solver']for rows in controls.values()for r in rows if r['solver']is not None]
out=dict(epoch=time.time(),passed=True,kind='SAVED355_CURRENT_STATE_MPC_LANDING_CLOCK_DIAGNOSIS356',groups=result['comparisons'],events=events,selected=cases,
    phases={phase:sum(r['phase']==phase for rows in controls.values()for r in rows)for phase in('approach','push','flight','extend','recover')},
    launched_cases=sum(e['launched']for e in events),recover_cases=sum(e['first_recover']is not None for e in events),
    solver=dict(calls=len(solvers),nonconverged=sum(not s['converged']for s in solvers),warmfallback=sum(s['used_feasible_warm_start_fallback']for s in solvers),max_ms=max(s['solve_ms']for s in solvers)),
    known_clock_mismatch=dict(source_MPC_prediction_dt=.01,current_command_hold_dt=.02,nominal_gain_dt=.01,already_disclosed=True,proposed='Re-discretize same source continuousA/B at actual.02 command period and choose horizon8 for.16s vs source15*.01=.15s. Same50Hz interface,feedback100/physics400/PD/queues unchanged. This is a finite controller timing adaptation, not a newlearninghorizon experiment.'),
    criterion_difference=dict(source_stable='upright>.95,linear_norm<.3,angular_norm<.5 plus sourcecontact/cross restrictions',current_strict='vertical<=.03,horizontalnorm<=.03,rollpitch<10deg,heading<.2,200physicsticks stable plus contact/firstflight footprint',unchanged=True,no_relaxation_to_claim_success=True),
    native_review=dict(completed=True,image=str(A/'RECORDED355_NATIVE_FRAMES/ACTUAL355_MPC_TARGET_BODY_POSE_SEQUENCE.png'),observation='0/1openloop and40event case tiltnearstep;41eventcase staysupright through5s but final selectedframe atnearfrontedge; no visualstabletop claim.'),
    NN=0,SDK=0,physics=0,network=0,new_GO=False,next='Prepare no-step sourceMPC20ms discretization candidate, then one independent finite comparison only after original resource clearance; no345 training yet.')
path=R/'ACTUAL356_SAVED355_LANDING_AND_CLOCK.json'
with path.open('x',encoding='utf8')as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,groups=result['comparisons'],recover_cases=out['recover_cases'],selected=cases,solver=out['solver']),indent=2))
