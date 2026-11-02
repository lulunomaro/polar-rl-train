"""OnefreshR02eight-caseboundedCPUstudy, noholdoutorhardwareclaim."""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures,hashlib
R=Path(__file__).resolve().parent;B=R/'batches/r02_coherent_fixedleg';B.mkdir(parents=True,exist_ok=False)
assert subprocess.run([sys.executable,'-B',str(R/'derive_r02_sources.py')],cwd=R,stdin=subprocess.DEVNULL).returncode==0
base=dict(seed=0,nominal=True,feedback='sensors',duration_s=8,command_at_s=1,controller={},accel_reference='wheel_midpoint',notes='R02train/diagnosticstudy; originalR00/R01preserved, notholdout')
specs=[('stand_gated',dict(mode='stand')),('forward_gated',dict(mode='forward',forward_m_s=2)),('forward_gyro',dict(mode='forward',forward_m_s=2,accel_correction=0)),('spin_gated',dict(mode='spin',yaw_rad_s=12.566370614359172)),('spin_gyro',dict(mode='spin',yaw_rad_s=12.566370614359172,accel_correction=0)),('spin_truth_diagnostic',dict(mode='spin',yaw_rad_s=12.566370614359172,feedback='truth_diagnostic')),('spin_stiff_gyro',dict(mode='spin',yaw_rad_s=12.566370614359172,accel_correction=0,controller={'leg_kp':250,'leg_kd':8,'roll_kp':20,'roll_kd':2})),('spin_legacy_legs',dict(mode='spin',yaw_rad_s=12.566370614359172,controller={'fixed_legs':False}))]
for n in('sensor_core_v3.py','ground_controller_v3.py','physics_bridge_v3.py','run_ground_case_v3.py'):(B/n).write_bytes((R/n).read_bytes())
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
def run(item):
 name,delta=item;case='r02_'+name;cfg={**base,**delta,'case_id':case};p=B/(case+'.json')
 with p.open('x')as f:json.dump(cfg,f,indent=2)
 start=time.time()
 with(B/(case+'.log')).open('xb')as log:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_ground_case_v3.py'),'--config',str(p),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);rc=proc.wait()
 result=R/'results'/case/'result.json';r=json.loads(result.read_bytes())if result.exists()else{};row=dict(case=case,pid=proc.pid,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),proposed_pass=r.get('proposed_gate_passed'),v=r.get('tail_velocity_mean_m_s'),w=r.get('tail_yawrate_mean_rad_s'),v_RMSE=r.get('tail_v_tracking_RMSE'),w_RMSE=r.get('tail_w_tracking_RMSE'),pitch_RMS=r.get('tail_pitch_RMS'),roll_RMS=r.get('tail_roll_RMS'),est_pitch_RMSE=r.get('estimator_pitch_RMSE'),est_v_RMSE=r.get('estimator_velocity_RMSE'),xy=r.get('xy_displacement_m'),normal_mean2=r.get('tail_physics_mean_wheel_force_N2'),nonwheel_physics=r.get('physics_nonwheel_contact_ticks'),turns=r.get('actual_yaw_turns'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,specs))
with(B/'BATCH_RESULT.json').open('x')as f:json.dump(dict(kind='R02_FRESH_SCREEN_NOT_HOLDOUT',rows=rows,worker_limit=4,GPUs_used=0),f,indent=2)
print('BATCH_CLOSED',B/'BATCH_RESULT.json',flush=True)
