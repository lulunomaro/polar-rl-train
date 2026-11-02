"""TRAIN8 pressurepairs: strongerboundedcommonwheeltorque, nophysicalboundchange.
UsesunchangedR09runner/model; oldR08/R09failuresretained; noholdoutinputs.
"""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;D=R/'batches/r10_spin_torque_train24';D.mkdir(parents=True,exist_ok=False);variants={'k12':dict(center_torque_kp=12.,center_torque_cap=1.2),'k16':dict(center_torque_kp=16.,center_torque_cap=1.6),'k24':dict(center_torque_kp=24.,center_torque_cap=2.2)};jobs=[(v,s)for v in variants for s in range(201,209)];basec=dict(yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,yaw_rate_ff=.052,center_lead_s=.008390087918603841);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
for n in('run_spin_torque_v2.py','spin_center_torque_v2.py','spin_center_controller_v1.py','spin_base_v1.py'):(D/n).write_bytes((R/n).read_bytes())
def run(job):
 v,s=job;case=f'r10_{v}_{s}';cfg=dict(case_id=case,seed=s,nominal=False,feedback='sensors',duration_s=8,command_at_s=1,controller={**basec,**variants[v]},accel_reference='wheel_midpoint',accel_correction=0,upright_arming_prior=True,mode='spin',yaw_rad_s=12.566370614359172,cohort='spin_torque8train_not_holdout');cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_spin_torque_v2.py'),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);rc=proc.wait()
 p=R/'results'/case/'result.json';r=json.loads(p.read_bytes())if p.exists()else{};a=dict(case=case,variant=v,seed=s,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),pass_=r.get('proposed_gate_passed'),v_rmse=r.get('tail_v_tracking_RMSE'),w=r.get('tail_yawrate_mean_rad_s'),w_rmse=r.get('tail_w_tracking_RMSE'),xy=r.get('xy_displacement_m'),pitch=r.get('tail_pitch_RMS'));print(json.dumps(a),flush=True);return a
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,jobs))
summary={v:{'n':8,'pass':sum(r['variant']==v and bool(r['pass_'])for r in rows),'xymax':max((r['xy']or 0)for r in rows if r['variant']==v)}for v in variants};(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind='R10_SPIN8TRAIN',summary=summary,rows=rows,variants=variants),indent=2),encoding='utf-8');print('SUMMARY',json.dumps(summary),flush=True)
