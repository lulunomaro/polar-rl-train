from pathlib import Path
import hashlib, json, os, re, signal, subprocess, sys, time, traceback
stage=Path(__file__).resolve().parent
root=stage.parent
out=stage/'run'
out.mkdir(exist_ok=True)
status=out/'status.json'
python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
trainer=stage/'source/mod4/train_mod4_ppo.py'
v7=root/'fudan_plane_v7/run'
deadline=time.time()+8*3600
state={'status':'WAIT_BOOTSTRAP','start_local':time.strftime('%Y-%m-%d %H:%M:%S %z'),
       'deadline_epoch':deadline,'num_envs':12000,'steps_per_env':48,
       'solver_pos':16,'solver_vel':4,'source_stage':str(v7),'phases':[]}
def save():
    status.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
def models(path):
    return sorted(path.glob('logs/*/model_*.pt'),key=lambda p:int(re.search(r'model_(\d+)',p.name).group(1)))
def metrics(path):
    try: s=path.read_text(errors='replace')
    except OSError: return {}
    keys=['Metrics/stand/tilt_deg_rms','Metrics/stand/speed_xy_m_s_rms',
          'Metrics/run/tilt_deg_rms','Metrics/run/velocity_error_m_s_rms',
          'Metrics/run/wheel_contact_rate','Metrics/gate/run_smooth_stable_pass']
    return {k:float(x[-1]) for k in keys if (x:=re.findall(re.escape(k)+r':\s*([0-9.]+)',s))}
save()
while time.time()<deadline:
    mm=models(v7)
    parent=os.popen("pgrep -f '[f]udan_plane_v7/launch.py'").read().strip()
    if mm and not parent: break
    time.sleep(20)
else:
    state['status']='BOOTSTRAP_TIMEOUT';save();sys.exit(2)
ckpt=mm[-1]
state['bootstrap_checkpoint']=str(ckpt)
state['bootstrap_sha256']=hashlib.sha256(ckpt.read_bytes()).hexdigest()
manifest=ckpt.parent/'run_manifest.json'
source=json.loads(manifest.read_text())['env']
base={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
base.update({k:str(v) for k,v in source.items() if k.startswith('RM_') and v is not None})
base.update({
 'RM_MOD4_MAP':'fudan_plane','RM_MOD4_TERRAIN':'flat',
 'RM_MOD4_USD':str(stage/'asset/robot_wheel_convex24.usd'),
 'RM_DR_OFF':'1','RM_GAS_FORCE_DR':'1','RM_GAS_FORCE_DR_ONLY':'1',
 'RM_GAS_FORCE_FRAME':'full_stroke',
 'RM_GAS_FORCE_NOMINAL_N':'500','RM_CMD_WZ_MIN':'0','RM_CMD_WZ_MAX':'0',
 'RM_HEIGHT_MIN':'0.30','RM_HEIGHT_MAX':'0.30',
 'RM_LEG_ACTION_SCALE':'0.5','RM_CRANK_ACTION_SCALE':'0.75',
 'RM_W_RUN_POSE':'0','RM_W_FLAT_ORIENT':'-80',
 'RM_W_WHEEL_CONTACT':'1','RM_W_RUN_HEIGHT_DEFICIT':'-30',
 'RM_W_STAND_QUIET':'8','RM_W_STAND_MOTION':'-2',
 'RM_WORKSPACE_ROOT':'/home/egde/rl_candidates/MOD4_takeover_20260914/env_scaling_20260915/source',
 'RM_SOLVER_POS':'16','RM_SOLVER_VEL':'4',
 'OMNI_KIT_ACCEPT_EULA':'YES','PYTHONUNBUFFERED':'1','CUDA_VISIBLE_DEVICES':'0'})
phases=[
 ('walk_low',400,'0.05','0.55','500','500'),
 ('run_build',600,'0.35','1.20','500','500'),
 ('mixed_gas_dr',1800,'0.05','1.50','300','700')]
for name,iters,vmin,vmax,gmin,gmax in phases:
    if time.time()>deadline-180: break
    env=base.copy()
    frame='reference' if gmin==gmax else 'full_stroke'
    env.update(RM_CMD_VX_MIN=vmin,RM_CMD_VX_MAX=vmax,
               RM_GAS_FORCE_MIN_N=gmin,RM_GAS_FORCE_MAX_N=gmax,
               RM_GAS_FORCE_FRAME=frame)
    phase=out/name
    phase.mkdir(exist_ok=True)
    item={'name':name,'checkpoint_in':str(ckpt),'iterations_requested':iters,
          'cmd_vx':[vmin,vmax],'gas_n':[gmin,gmax],'gas_frame':frame,
          'start_epoch':time.time(),'status':'TRAINING'}
    state['phases'].append(item)
    state['status']='TRAINING_'+name;save()
    cmd=[python,str(trainer),'--headless','--num_envs','12000',
         '--steps_per_env','48','--additional_iterations',str(iters),
         '--save_interval','5','--learning_rate','0.00004',
         '--run_name','flat_'+name+'_20260926','--seed','202609268',
         '--init_checkpoint',str(ckpt),'--log_root',str(phase/'logs'),
         '--report',str(phase/'train_report.json')]
    with (phase/'train.log').open('w') as log:
        p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,
                           start_new_session=True)
        item['pid']=p.pid;save()
        while p.poll() is None:
            if time.time()>=deadline:
                os.killpg(p.pid,signal.SIGINT)
                try: p.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid,signal.SIGTERM)
                    try: p.wait(timeout=30)
                    except subprocess.TimeoutExpired: os.killpg(p.pid,signal.SIGKILL)
                break
            time.sleep(30)
    item['returncode']=p.returncode
    item['end_epoch']=time.time()
    item['latest_metrics']=metrics(phase/'train.log')
    mm=models(phase)
    if not mm:
        item['status']='NO_CHECKPOINT'
        state['status']='FAILED_NO_CHECKPOINT';save()
        break
    ckpt=mm[-1]
    item['checkpoint_out']=str(ckpt)
    item['checkpoint_sha256']=hashlib.sha256(ckpt.read_bytes()).hexdigest()
    item['status']='SAVED'
    save()
state['latest_checkpoint']=str(ckpt)
state['latest_sha256']=hashlib.sha256(ckpt.read_bytes()).hexdigest()
state['end_epoch']=time.time()
if state['status'] not in ('FAILED_NO_CHECKPOINT','BOOTSTRAP_TIMEOUT'):
    state['status']='TIME_BUDGET_COMPLETE' if time.time()>=deadline-180 else 'STAGES_COMPLETE'
save()
