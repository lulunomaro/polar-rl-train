"""OneR03trainingstudy. Supporteduprightprior is explicit, notobservedtruth."""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;B=R/'batches/r03_upright_yawpi';B.mkdir(parents=True,exist_ok=False);assert subprocess.run([sys.executable,'-B',str(R/'derive_r03_sources.py')],cwd=R,stdin=subprocess.DEVNULL).returncode==0
c={'yaw_kp':.8,'yaw_ki':.5,'yaw_integral_limit':15,'yaw_rate_ff':.052}
base=dict(seed=0,nominal=True,feedback='sensors',duration_s=8,command_at_s=1,controller=c,accel_reference='wheel_midpoint',upright_arming_prior=True,notes='R03trainstudy; uprightarmingprior explicit; notholdout/HW')
specs=[('stand',dict(mode='stand')),('forward_gated',dict(mode='forward',forward_m_s=2)),('forward_gyro',dict(mode='forward',forward_m_s=2,accel_correction=0)),('spin_gated',dict(mode='spin',yaw_rad_s=12.566370614359172)),('spin_gyro',dict(mode='spin',yaw_rad_s=12.566370614359172,accel_correction=0)),('spin_truth_diagnostic',dict(mode='spin',yaw_rad_s=12.566370614359172,feedback='truth_diagnostic')),('stand_DR101',dict(mode='stand',nominal=False,seed=101)),('forward_DR101',dict(mode='forward',forward_m_s=2,nominal=False,seed=101))]
for n in('sensor_core_v4.py','ground_controller_v4.py','run_ground_case_v4.py','physics_bridge_v3.py'):(B/n).write_bytes((R/n).read_bytes())
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
def run(item):
 name,delta=item;case='r03_'+name;cfg={**base,**delta,'case_id':case};p=B/(case+'.json')
 with p.open('x')as f:json.dump(cfg,f,indent=2)
 start=time.time()
 with(B/(case+'.log')).open('xb')as log:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_ground_case_v4.py'),'--config',str(p),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);rc=proc.wait()
 path=R/'results'/case/'result.json';r=json.loads(path.read_bytes())if path.exists()else{};row=dict(case=case,pid=proc.pid,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),proposed_pass=r.get('proposed_gate_passed'),v=r.get('tail_velocity_mean_m_s'),w=r.get('tail_yawrate_mean_rad_s'),v_RMSE=r.get('tail_v_tracking_RMSE'),w_RMSE=r.get('tail_w_tracking_RMSE'),pitch_RMS=r.get('tail_pitch_RMS'),roll_RMS=r.get('tail_roll_RMS'),est_pitch_RMSE=r.get('estimator_pitch_RMSE'),est_v_RMSE=r.get('estimator_velocity_RMSE'),xy=r.get('xy_displacement_m'),normal_mean2=r.get('tail_physics_mean_wheel_force_N2'),nonwheel_physics=r.get('physics_nonwheel_contact_ticks'),turns=r.get('actual_yaw_turns'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,specs))
with(B/'BATCH_RESULT.json').open('x')as f:json.dump(dict(kind='R03_SUPPORTEDUPRIGHTTRAIN_SCREEN_NOT_HOLDOUT',rows=rows,worker_limit=4,GPUs_used=0),f,indent=2)
print('BATCH_CLOSED',B/'BATCH_RESULT.json',flush=True)
