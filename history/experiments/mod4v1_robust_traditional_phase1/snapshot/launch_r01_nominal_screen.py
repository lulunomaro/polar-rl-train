"""OneboundedCPU4workerR01screen. NoGPU, selectedPT, learner oroldonce.
Sourcesaregeneratedbeforelaunch; oncefolderandcasefoldersareexclusive.
"""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures,hashlib
R=Path(__file__).resolve().parent;B=R/'batches/r01_nominal_screen';B.mkdir(parents=True,exist_ok=False)
base=dict(seed=0,nominal=True,feedback='sensors',duration_s=8,command_at_s=1,controller={},notes='R01train/diagnosticscreen; newfrontend; notholdout/hardwarequalification')
specs=[('stand_midpoint',dict(mode='stand',accel_reference='wheel_midpoint')),('forward_midpoint',dict(mode='forward',forward_m_s=2,accel_reference='wheel_midpoint')),('forward_chassis',dict(mode='forward',forward_m_s=2,accel_reference='chassis')),('forward_truth_diagnostic',dict(mode='forward',forward_m_s=2,feedback='truth_diagnostic',accel_reference='wheel_midpoint')),('spin_midpoint',dict(mode='spin',yaw_rad_s=4*3.141592653589793,accel_reference='wheel_midpoint')),('spin_chassis',dict(mode='spin',yaw_rad_s=4*3.141592653589793,accel_reference='chassis')),('spin_midpoint_roll',dict(mode='spin',yaw_rad_s=4*3.141592653589793,accel_reference='wheel_midpoint',controller={'roll_kp':20,'roll_kd':2})),('spin_midpoint_slow',dict(mode='spin',yaw_rad_s=4*3.141592653589793,accel_reference='wheel_midpoint',controller={'yaw_accel':3,'yaw_kp':.35,'yaw_ki':.08}))]
for gen in('derive_r01_sensor_controller.py','derive_r01_case_runner.py'):
 rc=subprocess.run([sys.executable,'-B',str(R/gen)],cwd=R,stdin=subprocess.DEVNULL,check=False).returncode
 assert rc==0,(gen,rc)
source=[]
for n in('sensor_core_v2.py','physics_bridge_v2.py','ground_controller_v2.py','run_ground_case_v2.py','launch_r01_nominal_screen.py'):
 raw=(R/n).read_bytes();(B/n).write_bytes(raw);source.append(dict(path=n,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
with(B/'SOURCE_INDEX.json').open('x')as f:json.dump(source,f,indent=2)
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
def run(item):
 name,delta=item;case='r01_'+name;cfg={**base,**delta,'case_id':case};p=B/(case+'.json')
 with p.open('x')as f:json.dump(cfg,f,indent=2)
 start=time.time()
 with(B/(case+'.log')).open('xb')as log:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_ground_case_v2.py'),'--config',str(p),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);rc=proc.wait()
 resultpath=R/'results'/case/'result.json';r=json.loads(resultpath.read_bytes())if resultpath.exists()else{};row=dict(case=case,pid=proc.pid,returncode=rc,started=start,ended=time.time(),result=str(resultpath),complete=r.get('complete'),proposed_pass=r.get('proposed_gate_passed'),v=r.get('tail_velocity_mean_m_s'),w=r.get('tail_yawrate_mean_rad_s'),v_RMSE=r.get('tail_v_tracking_RMSE'),w_RMSE=r.get('tail_w_tracking_RMSE'),pitch_RMS=r.get('tail_pitch_RMS'),roll_RMS=r.get('tail_roll_RMS'),est_pitch_RMSE=r.get('estimator_pitch_RMSE'),est_v_RMSE=r.get('estimator_velocity_RMSE'),xy=r.get('xy_displacement_m'),normal_mean2=r.get('tail_physics_mean_wheel_force_N2'),nonwheel_physics=r.get('physics_nonwheel_contact_ticks'),turns=r.get('actual_yaw_turns'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,specs))
with(B/'BATCH_RESULT.json').open('x')as f:json.dump(dict(kind='R01_NOMINAL_SCREEN_NOT_HOLDOUT',cases=rows,worker_limit=4,physics_engine='CPU_MuJoCo',GPUs_used=0),f,indent=2)
print('BATCH_CLOSED',B/'BATCH_RESULT.json',flush=True)
