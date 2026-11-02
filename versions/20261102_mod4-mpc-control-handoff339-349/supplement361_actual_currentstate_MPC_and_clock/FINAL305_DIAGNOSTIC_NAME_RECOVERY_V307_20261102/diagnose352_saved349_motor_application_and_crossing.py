"""Read existing349 body/motor traces to locate control handoff errors; no model/physics."""
from pathlib import Path
import hashlib,io,json,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
A=T/'MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V349_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
result=read(A/'reports/ROOT349_EVALUATION_FULL_RETURNED.json')['result']
trace=read(T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102/reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json')['commands']
transfers=read(A/'reports/ROOT349_SELECTED_REPLAY_TRANSFERS.json')
cases=[]
for row in transfers['cases']:
    path=Path(row['local_path']);raw=path.read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA']
    with np.load(io.BytesIO(raw),allow_pickle=False)as z:packet={k:z[k].copy()for k in z.files}
    n=len(packet['root13']);indices=np.arange(n)*2;processed=np.array([trace[i]['processed_target']for i in indices])
    expectedq=np.array([trace[i]['actual_motor_q']for i in indices]);expecteddq=np.array([trace[i]['actual_motor_dq']for i in indices])
    source_root=np.array([trace[min(i+2,499)]['qpos_initial'][:3]for i in indices]);source_root[:,0]+=.8
    root=packet['root13'][:,:3]-np.array(row['origin'])
    legs=[0,1,3,4];wheels=[2,5]
    actual_target=np.zeros_like(processed);actual_target[:,legs]=packet['motor_pos_target'][:,legs];actual_target[:,wheels]=packet['motor_vel_target'][:,wheels]
    expected=processed if row['env']>=40 else expectedq.copy()
    if row['env']<40:expected[:,wheels]=expecteddq[:,wheels]
    targeterr=actual_target-expected;position=np.linalg.norm(root-source_root,axis=-1)
    qerr=packet['motor_q'][:,legs]-expectedq[:,legs]
    first=lambda values,bound:next((dict(control=i+1,seconds=(i+1)*.02,value=float(v))for i,v in enumerate(values)if v>bound),None)
    cases.append(dict(env=row['env'],group='processed_MPC_target'if row['env']>=40 else'state_target',seconds=row['seconds'],
        target_application_max_abs=np.abs(targeterr).max(0).tolist(),target_units=['rad','rad','rad/s','rad','rad','rad/s'],
        position_error_first_5cm=first(position,.05),position_error_first_10cm=first(position,.1),
        leg_angle_RMSE_rad=np.sqrt((qerr*qerr).mean(0)).tolist(),end_position_error_m=float(position[-1]),
        original_result=row['result'],scope='4savedselectedcases; source commandprestate shifted20ms endpoint approximate last endpoint; no raw force samples or currentpolicy model'))
crossed=[dict(env=r['env'],seconds=r['seconds'],full_window=r['full_window'],terminal=r['episode_terminal'],longest_stable_seconds=r['longest_stable_seconds'],tracking_components=r['tracking_components'])for r in result['results']if r['first_flight_both_cross']]
out=dict(epoch=time.time(),kind='SAVED349_MOTOR_APPLICATION_AND_CROSSING_DIAGNOSIS352',passed=True,source=str(A/'reports/ROOT349_EVALUATION_FULL_RETURNED.json'),cases=cases,crossed13=crossed,
    fullwindow_processed=[dict(env=r['env'],cross=r['first_flight_both_cross'],stable=r['longest_stable_seconds'],tracking_components=r['tracking_components'])for r in result['results']if r['env']>=40 and r['full_window']],
    limitation='No physical torque telemetry in349 and no full100Hz/sourceclosedloop; selected4 are not all13crossing cases. Targetagreement proves mapping/application for selectedcases only.',
    NN=0,SDK=0,physics_steps=0,network=0,optimizer=0,account=0,next='A finite same50Hz comparison of openloop processedtargets versus sourceclosedloopstate/eventcontroller through originalactioninterface; report100Hz scheduling limitation explicitly.')
path=R/'ACTUAL352_SAVED349_MOTOR_APPLICATION_AND_POSTCROSS.json'
with path.open('x',encoding='utf8')as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,report=str(path),targets=[dict(env=r['env'],maxerr=max(r['target_application_max_abs']),first10cm=r['position_error_first_10cm'])for r in cases],crossed_cases=len(crossed),crossed_full=sum(r['full_window']for r in crossed),crossed_stablemax=max(r['longest_stable_seconds']for r in crossed))))
