"""R06: firstMPCnominalphysics +finishp25normaltrainwithoutreplaying3existingseeds."""
from pathlib import Path
import json,os,sys,subprocess,concurrent.futures,time
R=Path(__file__).resolve().parent;D=R/'batches/r06_mpc_and_p25_remaining';D.mkdir(parents=True,exist_ok=False)
with(D/'MPC_PREP.log').open('xb')as f:rc=subprocess.run([sys.executable,'-B',str(R/'prepare_mpc8_v1.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0,('MPCprepfailed',rc,str(D/'MPC_PREP.log'))
basec={'yaw_kp':.8,'yaw_ki':.5,'yaw_integral_limit':15,'yaw_rate_ff':.052};jobs=[('mpc',m,0)for m in('stand','forward')]+[('p25',m,s)for s in(201,202,204,206,207)for m in('stand','forward')];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
def run(spec):
 variant,mode,seed=spec;case=f'r06_{variant}_{mode}_{seed}';c=basec.copy()
 if variant=='p25':c.update(position_weight=25.,position_leash=1.)
 cfg=dict(case_id=case,seed=seed,nominal=variant=='mpc',feedback='sensors',duration_s=8,command_at_s=1,controller=c,accel_reference='wheel_midpoint',upright_arming_prior=True,cohort='train_newMPC_or_remainingp25normal_not_holdout',mode=mode)
 if mode=='forward':cfg['forward_m_s']=2
 p=D/(case+'.json');p.write_text(json.dumps(cfg,indent=2),encoding='utf-8');runner=R/('run_mpc_ground_v1.py'if variant=='mpc'else'run_ground_case_v5.py');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(runner),'--config',str(p),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);code=proc.wait()
 rp=R/'results'/case/'result.json';r=json.loads(rp.read_bytes())if rp.exists()else{};row=dict(case=case,variant=variant,mode=mode,seed=seed,returncode=code,start=start,end=time.time(),complete=r.get('complete'),pass_=r.get('proposed_gate_passed'),v=r.get('tail_velocity_mean_m_s'),w=r.get('tail_yawrate_mean_rad_s'),v_rmse=r.get('tail_v_tracking_RMSE'),xy=r.get('xy_displacement_m'),usage=r.get('controller_usage'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,jobs))
(D/'BATCH_RESULT.json').write_text(json.dumps({'kind':'R06_TRAIN_NOT_HOLDOUT','rows':rows},indent=2),encoding='utf-8');print('CLOSED',D/'BATCH_RESULT.json',flush=True)
