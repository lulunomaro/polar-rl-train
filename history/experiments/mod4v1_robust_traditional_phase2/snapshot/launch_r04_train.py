"""32boundednewfullDRtraincases. Noheldoutseeds, currentcandidatefrozen.
Comparedeclaredspinmeasurementprofiles onTRAIN only beforechoosingholdoutprofile.
"""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;B=R/'batches/r04_train_32';B.mkdir(parents=True,exist_ok=False);assert subprocess.run([sys.executable,'-B',str(R/'prepare_r04_train.py')],cwd=R,stdin=subprocess.DEVNULL).returncode==0
assert 'producer_streamed_once' in(R/'run_ground_case_v5.py').read_text(encoding='utf-8')
c={'yaw_kp':.8,'yaw_ki':.5,'yaw_integral_limit':15,'yaw_rate_ff':.052};base=dict(nominal=False,feedback='sensors',duration_s=8,command_at_s=1,controller=c,accel_reference='wheel_midpoint',upright_arming_prior=True,cohort='train201to208',notes='R04allD0-D7train; noholdoutreuse; independentmodels/queues')
specs=[(mode,seed)for seed in range(201,209)for mode in('stand','forward','spin_gated','spin_gyro')]
for n in('run_ground_case_v5.py','sensor_core_v4.py','ground_controller_v4.py','physics_bridge_v3.py','physics_bridge.py','R04_FROZEN_TRAIN_SOURCE.json'):(B/n).write_bytes((R/n).read_bytes())
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
def run(item):
 mode,seed=item;case=f'r04_{mode}_{seed}';cfg={**base,'case_id':case,'seed':seed,'mode':'spin'if mode.startswith('spin')else mode}
 if mode=='forward':cfg['forward_m_s']=2
 if mode.startswith('spin'):cfg['yaw_rad_s']=12.566370614359172
 if mode=='spin_gyro':cfg['accel_correction']=0
 p=B/(case+'.json')
 with p.open('x')as f:json.dump(cfg,f,indent=2)
 start=time.time()
 with(B/(case+'.log')).open('xb')as log:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_ground_case_v5.py'),'--config',str(p),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);rc=proc.wait()
 path=R/'results'/case/'result.json';r=json.loads(path.read_bytes())if path.exists()else{};dr=r.get('DR',{});row=dict(case=case,pid=proc.pid,returncode=rc,start=start,end=time.time(),mode=mode,seed=seed,D3=dr.get('D3',{}).get('requested_delay_us'),complete=r.get('complete'),proposed_pass=r.get('proposed_gate_passed'),v=r.get('tail_velocity_mean_m_s'),w=r.get('tail_yawrate_mean_rad_s'),v_RMSE=r.get('tail_v_tracking_RMSE'),w_RMSE=r.get('tail_w_tracking_RMSE'),pitch_RMS=r.get('tail_pitch_RMS'),roll_RMS=r.get('tail_roll_RMS'),est_pitch_RMSE=r.get('estimator_pitch_RMSE'),est_v_RMSE=r.get('estimator_velocity_RMSE'),xy=r.get('xy_displacement_m'),normal_mean2=r.get('tail_physics_mean_wheel_force_N2'),nonwheel_physics=r.get('physics_nonwheel_contact_ticks'),turns=r.get('actual_yaw_turns'),trace=r.get('trace_artifact'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,specs))
summary={}
for mode in('stand','forward','spin_gated','spin_gyro'):
 rs=[r for r in rows if r['mode']==mode];summary[mode]={'n':len(rs),'complete':sum(bool(r['complete'])for r in rs),'proposed_pass':sum(bool(r['proposed_pass'])for r in rs),'delay0':{'n':sum(r['D3']==0 for r in rs),'pass':sum(r['D3']==0 and bool(r['proposed_pass'])for r in rs)},'delay10ms':{'n':sum(r['D3']==10000 for r in rs),'pass':sum(r['D3']==10000 and bool(r['proposed_pass'])for r in rs)}}
with(B/'BATCH_RESULT.json').open('x')as f:json.dump(dict(kind='R04_32_FULLDR_TRAIN_NOT_HOLDOUT',summary=summary,rows=rows,worker_limit=4,GPUs_used=0),f,indent=2)
print('SUMMARY',json.dumps(summary),flush=True);print('BATCH_CLOSED',B/'BATCH_RESULT.json',flush=True)
