"""User's reference-style whole-leg same-end fall, current1cd E3 LIVE MuJoCo."""
from pathlib import Path
import json,time,os,threading,ctypes,traceback,math
D=Path(__file__).resolve().parent;SRC=D.parent/'mod4v1_e3_mujoco_view_20261104/view_current_e3_v2.py';text=SRC.read_text(encoding='utf8').split("state={'paused'")[0];assert text.count("D/'current_E3.pt'")==1;text=text.replace("D/'current_E3.pt'","Path(r'F:/RMPOLAR-RL/mod4v1_e3_mujoco_view_20261104/current_E3.pt')");ns={'__file__':str(D/'live_core.py'),'__name__':'requested_whole_leg_live_core'};exec(compile(text,str(SRC),'exec'),ns);np=ns['np'];mujoco=ns['mujoco'];sim=ns['E3Sim']();pose=json.loads((D/'POSE.json').read_bytes());state={'paused':False,'reset':False,'initial_pause':False,'camera':1};lock=threading.Lock();handles=[];total=0

def put(name,v):
 p=D/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf8');os.replace(t,p)
def reset():
 mujoco.mj_resetData(sim.model,sim.data);sim.data.qpos[:]=pose['qpos'];sim.data.qvel[:]=0;sim.data.ctrl[:]=0;sim.data.xfrc_applied[:]=0;sim.last_action[:]=0;sim.control_steps=0;sim._push_remaining=0;sim._observation_history=[];sim.command=ns['rt'].UserCommand(height=.25,mode=3,auto_mode=False);sim.command.vx=sim.command.vy=sim.command.wz=0.;mujoco.mj_forward(sim.model,sim.data);sim._seed_observation_history(sim.observation_frame());assert sim.closure_error()<1e-6
 for side,values in pose['joint_values'].items():
  for name,value in values.items():
   j=sim.model.joint(side+'_'+name)
   if sim.model.jnt_limited[j.id]:assert sim.model.jnt_range[j.id,0]-1e-9<=value<=sim.model.jnt_range[j.id,1]+1e-9

def key(k):
 with lock:
  if k in(ord('G'),ord('g'),32):state['paused']=not state['paused']
  elif k in(ord('R'),ord('r')):state.update(reset=True,paused=False,initial_pause=False)
  elif k in(ord('S'),ord('s')):state.update(reset=True,paused=True,initial_pause=True)
  elif k==ord('1'):state['camera']=1
  elif k==ord('2'):state['camera']=2

def windows():
 user=ctypes.windll.user32;cb=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
 def visit(hwnd,_):
  pid=ctypes.c_ulong();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
  if pid.value==os.getpid()and user.IsWindowVisible(hwnd):handles.append(hwnd)
  return True
 user.EnumWindows(cb(visit),0)

try:
 reset();sim.model.vis.headlight.active=1;sim.model.vis.headlight.ambient[:]=.6;sim.model.vis.headlight.diffuse[:]=.8
 with mujoco.viewer.launch_passive(sim.model,sim.data,key_callback=key)as viewer:
  viewer.cam.distance=1.4;viewer.cam.azimuth=105.;viewer.cam.elevation=-10.;viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT]=False;viewer.cam.lookat[:]=sim.data.qpos[:3]+np.array([-.08,0,-.015]);viewer.sync();windows();warm=time.perf_counter()+4.;last=0.;put('VIEWER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),window_handles=handles,model_SHA=sim.policy.SHA,iteration=sim.policy.iteration,kind='LIVE_CURRENT_E3_WHOLE_LEG_REFERENCE_POSE_NOT_ANIMATION',initial_pose=pose,policy_hz=50,physics_dt=.0025,initial_hold_wall_seconds=4,repeat_after_sim_seconds=12,training_or_registry_changes=False,joint_limits_changed=False,keys='R reset and run; S initial pose paused; G/Space pause;1 side;2 oblique'))
  while viewer.is_running():
   begin=time.perf_counter()
   with lock:s=dict(state);state['reset']=False
   if s['reset']:reset();warm=begin+3.
   if not s['paused']and begin>=warm:
    sim.step_control();total+=1
    if sim.data.time>=12.:
     with lock:state.update(reset=True,paused=False,initial_pause=False)
   viewer.cam.azimuth=105. if s['camera']==1 else 135.;viewer.cam.elevation=-10. if s['camera']==1 else-20.;viewer.cam.lookat[:]=sim.data.qpos[:3]+np.array([-.08,0,-.015]);viewer.sync()
   if begin-last>.4:
    rot=sim.data.xmat[sim.chassis_id].reshape(3,3);g=rot.T@np.array([0.,0.,-1.]);phase='INITIAL POSE / PAUSED'if s['paused']and s['initial_pause']else('START POSE HOLD'if begin<warm else'LIVE E3 RECOVERY');title=f'MOD4v1 E3 1cd99995 | WHOLE LEG EXTENDED | {phase} {sim.data.time:.2f}s | R reset S initial G pause 1/2 camera'
    for h in handles:ctypes.windll.user32.SetWindowTextW(ctypes.c_void_p(h),title)
    put('CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),viewer_running=viewer.is_running(),model_SHA=sim.policy.SHA,live_policy=True,scripted_joint_animation=False,policy_controls=total,sim_time_s=float(sim.data.time),paused=s['paused'],phase=phase,body_xyz=sim.data.qpos[:3].tolist(),tilt_degrees=math.degrees(math.acos(float(np.clip(-g[2],-1,1)))),closure_m=sim.closure_error(),finite=bool(np.isfinite(sim.data.qpos).all()and np.isfinite(sim.data.qvel).all()),joint_limits_changed=False));last=begin
   time.sleep(max(0.,.02-(time.perf_counter()-begin)))
 put('CLOSED.json',dict(epoch=time.time(),pid=os.getpid(),normal_viewer_context_returned=True,policy_controls=total))
except BaseException:put('ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc()));raise
