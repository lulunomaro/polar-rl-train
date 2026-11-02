"""R05pairedtrain ablation: R04positionleash limitsintegralaction underbias.
Onlydeclaredconfigchanges; oldfailuresretained; noholdouttouched.
"""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;B=R/'batches/r05_position_27';B.mkdir(parents=True,exist_ok=False)
basec={'yaw_kp':.8,'yaw_ki':.5,'yaw_integral_limit':15,'yaw_rate_ff':.052};variants={'p10':{'position_weight':10.,'position_leash':1.},'p25':{'position_weight':25.,'position_leash':1.},'p10v4':{'position_weight':10.,'velocity_weight':4.,'position_leash':1.}}
specs=[(v,mode,seed)for v in variants for seed in(203,205,208)for mode in('stand','forward','spin_gyro')];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
for n in('run_ground_case_v5.py','sensor_core_v4.py','ground_controller_v4.py','physics_bridge_v3.py'):(B/n).write_bytes((R/n).read_bytes())
def run(item):
 v,mode,seed=item;case=f'r05_{v}_{mode}_{seed}';cfg=dict(case_id=case,seed=seed,nominal=False,feedback='sensors',duration_s=8,command_at_s=1,controller={**basec,**variants[v]},accel_reference='wheel_midpoint',upright_arming_prior=True,cohort='paired_training_existingfailseeds_not_holdout',mode='spin'if mode=='spin_gyro'else mode,notes='Purposefulchangedpositionweight/leashablation; notsameconfigreplay')
 if mode=='forward':cfg['forward_m_s']=2
 if mode=='spin_gyro':cfg['yaw_rad_s']=12.566370614359172;cfg['accel_correction']=0
 p=B/(case+'.json')
 with p.open('x')as f:json.dump(cfg,f,indent=2)
 started=time.time()
 with(B/(case+'.log')).open('xb')as log:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_ground_case_v5.py'),'--config',str(p),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);rc=proc.wait()
 path=R/'results'/case/'result.json';r=json.loads(path.read_bytes())if path.exists()else{};row=dict(case=case,variant=v,mode=mode,seed=seed,pid=proc.pid,returncode=rc,start=started,end=time.time(),complete=r.get('complete'),pass_=r.get('proposed_gate_passed'),v=r.get('tail_velocity_mean_m_s'),w=r.get('tail_yawrate_mean_rad_s'),v_RMSE=r.get('tail_v_tracking_RMSE'),w_RMSE=r.get('tail_w_tracking_RMSE'),pitch_RMS=r.get('tail_pitch_RMS'),xy=r.get('xy_displacement_m'),nonwheel_physics=r.get('physics_nonwheel_contact_ticks'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,specs))
summary={v:{m:{'n':sum(r['variant']==v and r['mode']==m for r in rows),'pass':sum(r['variant']==v and r['mode']==m and bool(r['pass_'])for r in rows)}for m in('stand','forward','spin_gyro')}for v in variants}
with(B/'BATCH_RESULT.json').open('x')as f:json.dump(dict(kind='R05_CONFIG_ONLY_TRAIN_ABLATION',summary=summary,rows=rows,worker_limit=4),f,indent=2)
print('SUMMARY',json.dumps(summary),flush=True);print('BATCH_CLOSED',B/'BATCH_RESULT.json',flush=True)
