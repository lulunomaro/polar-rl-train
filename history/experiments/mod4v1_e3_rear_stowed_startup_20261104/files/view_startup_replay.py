"""Replay the actual just-recorded E3 startup test. No policy/model-weight reload.
All poses are from the real MuJoCo rollout, not a hand-authored stand-up animation.
"""
from pathlib import Path
import os,json,time,threading,ctypes,traceback
import numpy as np
import mujoco,mujoco.viewer
D=Path(__file__).resolve().parent;M=Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4/scene.xml');model=mujoco.MjModel.from_xml_path(str(M));data=mujoco.MjData(model);cases={}
for name in('E3_recover_then_drive_same_weights','zero_motor_torque_control'):
 with np.load(D/(name+'.npz'),allow_pickle=False)as a:cases[name]={k:a[k].copy()for k in a.files}
 assert cases[name]['qpos'].shape==(651,model.nq)
model.vis.headlight.active=1;model.vis.headlight.ambient[:]=.55;model.vis.headlight.diffuse[:]=.8
state={'case':'E3_recover_then_drive_same_weights','frame':0,'paused':False,'reset':True};lock=threading.Lock();window=[];total=0

def put(name,value):
 p=D/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(value,indent=2),encoding='utf8');os.replace(t,p)
def key(k):
 with lock:
  if k in(ord('G'),ord('g'),32):state['paused']=not state['paused']
  elif k in(ord('R'),ord('r')):state.update(frame=0,reset=True,paused=False)
  elif k in(ord('S'),ord('s')):state.update(frame=0,reset=True,paused=True)
  elif k in(ord('B'),ord('b')):state.update(case='zero_motor_torque_control',frame=0,reset=True,paused=False)
  elif k in(ord('E'),ord('e')):state.update(case='E3_recover_then_drive_same_weights',frame=0,reset=True,paused=False)
def windows():
 u=ctypes.windll.user32;cb=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
 def visit(hwnd,_):
  p=ctypes.c_ulong();u.GetWindowThreadProcessId(hwnd,ctypes.byref(p))
  if p.value==os.getpid()and u.IsWindowVisible(hwnd):window.append(hwnd)
  return True
 u.EnumWindows(cb(visit),0)
try:
 start=time.perf_counter();last=0;hold_until=start+3
 with mujoco.viewer.launch_passive(model,data,key_callback=key)as viewer:
  viewer.cam.distance=1.25;viewer.cam.azimuth=90.;viewer.cam.elevation=-13.;viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT]=False
  # Non-colliding display markers make startup rollback visible while camera follows.
  with viewer.lock():
   for n,x in enumerate(np.arange(-5.,-2.99,.25)):
    g=viewer.user_scn.geoms[n];mujoco.mjv_initGeom(g,mujoco.mjtGeom.mjGEOM_BOX,np.array([.003,.55,.001]),np.array([x,0,.001]),np.eye(3).ravel(),np.array([1.,.8,.1,1.]if abs(x+4)<1e-8 else[.55,.6,.65,1.]));g.label=('START'if abs(x+4)<1e-8 else'')
   viewer.user_scn.ngeom=9
  data.qpos[:]=cases[state['case']]['qpos'][0];mujoco.mj_forward(model,data);viewer.cam.lookat[:]=data.qpos[:3];viewer.sync();windows();put('VIEWER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),window_handles=window,kind='Actual_E3_MuJoCo_startup_rollout_replay_NOT_live_policy',actual_rollout_completed_before_view=True,model_weights_opened=0,keys='R replay; G/Space pause; S initial pose pause; B zero-torque baseline; E E3'))
  while viewer.is_running():
   begin=time.perf_counter()
   with lock:
    s=dict(state)
    if state['reset']:hold_until=begin+3.;state['reset']=False
   f=s['frame'];case=cases[s['case']];data.qpos[:]=case['qpos'][f];data.time=float(case['time'][f]);mujoco.mj_forward(model,data);viewer.cam.lookat[:]=data.qpos[:3];viewer.sync()
   phase='POWER-ON / RECOVER'if f<400 else'DRIVE COMMAND 0.2 m/s';tag='E3 1cd99995'if s['case'].startswith('E3')else'MOTORS OFF BASELINE'
   if begin-last>.4:
    title=f'MOD4v1 {tag} | STARTUP TEST REPLAY {f*.02:.2f}s | {phase} | R replay G pause S parked B baseline E E3'
    for hwnd in window:ctypes.windll.user32.SetWindowTextW(ctypes.c_void_p(hwnd),title)
    put('CURRENT_REPLAY.json',dict(epoch=time.time(),pid=os.getpid(),viewer_running=viewer.is_running(),case=s['case'],frame=f,sim_time_s=f*.02,paused=s['paused'],root_xyz=data.qpos[:3].tolist(),actual_recorded_rollout=True,live_policy=False));last=begin
   if not s['paused']and begin>=hold_until:
    with lock:
     if state['case']==s['case']and state['frame']==f:
      if f<650:state['frame']+=1
      else:state.update(frame=0,reset=True)
    total+=1
   time.sleep(max(0.,.02-(time.perf_counter()-begin)))
 put('REPLAY_CLOSED.json',dict(epoch=time.time(),pid=os.getpid(),viewer_context_returned=True,display_frames=total))
except BaseException:put('REPLAY_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
