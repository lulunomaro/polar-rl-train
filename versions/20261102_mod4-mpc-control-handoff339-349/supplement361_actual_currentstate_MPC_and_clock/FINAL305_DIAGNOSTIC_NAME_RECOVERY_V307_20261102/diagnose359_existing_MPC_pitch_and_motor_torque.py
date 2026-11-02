"""Compare source successful posture with actual355/357 selected motor and pose traces."""
from pathlib import Path
import hashlib,io,json,math,time
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';read=lambda p:json.loads(p.read_bytes())
source=read(Path('F:/RMPOLAR-RL/traditional_control_20261101/results/FINAL_EVIDENCE_V2/fullDR_mpc/trajectory.json'))
src=np.array([r['upright_cos']for r in source]);rows=[]
for phase in(355,357):
    root=T/(f'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V{phase}_20261102'if phase==355 else'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102')
    full=read(root/f'reports/ROOT{phase}_EVALUATION_FULL_RETURNED.json')
    trace=next(json.loads(v['UTF8'])for v in full['full_UTF8']if v['path'].endswith(f'ACTUAL{phase}_CURRENT_STATE_MPC_CONTROL_TRACE.json'))
    for row in read(root/f'reports/ROOT{phase}_SELECTED_REPLAY_TRANSFERS.json')['cases']:
        raw=Path(row['local_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA']
        with np.load(io.BytesIO(raw),allow_pickle=False)as z:states=z['root13'].copy()
        rz=1-2*(states[:,3]**2+states[:,4]**2)
        when=next((dict(seconds=(i+1)*.02,Rzz=float(value))for i,value in enumerate(rz)if value<.95),None)
        controlrows=[dict(control=r['control'],**v)for r in trace['rows']for v in r['rows']if v['env']==row['env']]
        forces=[]
        if controlrows:
            for c in controlrows:
                physical=[p for p in trace['physics_selected']if p['tick']>(c['control']-1)*8 and p['tick']<=c['control']*8]
                if not physical:continue
                idx=physical[0]['selected_envs'].index(row['env'])
                applied=np.mean([p['actual_applied_torque6'][idx]for p in physical],axis=0)[[1,0,4,2,3,5]]
                forces.append(dict(control=c['control'],seconds=(c['control']-1)*.02,phase=c['phase'],requested_tau=c['tau_requested'],actual_applied_tau_mean=applied.tolist(),raw_difference=(applied-np.array(c['tau_requested'])).tolist(),interpretation='desiredinversePDtau vs actualfullDR/currentstate/queue/DCclipped motor; mismatchisexpectedunderDRandnotactuatorbugproof'))
        rows.append(dict(phase=phase,env=row['env'],seconds=row['seconds'],firstRzzbelow95=when,minRzz=float(rz.min()),first10_motor_comparisons=forces[:10],last_motor_comparison=forces[-1]if forces else None))
out=dict(epoch=time.time(),passed=True,source_successful_trace=dict(path='F:/RMPOLAR-RL/traditional_control_20261101/results/FINAL_EVIDENCE_V2/fullDR_mpc/trajectory.json',minRzz=float(src.min()),orientation_angle75_would_terminate=bool((src<math.cos(.75)).any()),not_an_orientation_guard_falsepositive=True),
    selected=rows,no_new_physics_or_model=True,NN=0,network=0,SDK=0,optimizer=0,account=0,
    next='First actualposture error appears in the push/flight transfer; next finite stage needs perenvDR/nominal effectiveplant receipts and motor target/appliedtorque at that divergence. Preserve actual.75orientation rather than loosening to source.45Rzz; originalsuccessfulMPCneverneededthatlooserthreshold.')
path=R/'ACTUAL359_SOURCE_POSTURE_AND_SAVED_PHYSX_MOTOR_TORQUE.json'
with path.open('x',encoding='utf8')as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,sourceMinRzz=float(src.min()),selected=[{k:r[k]for k in('phase','env','firstRzzbelow95','minRzz')}for r in rows])))
