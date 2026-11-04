"""Current frozen E3 policy in the existing local MuJoCo adapter; not an Isaac score."""
from pathlib import Path
import sys,json,time,os,math,hashlib,io,traceback,threading,ctypes
D=Path(__file__).resolve().parent;PLAYER=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023\player');sys.path.insert(0,str(PLAYER))
import numpy as np
import torch
import mujoco,mujoco.viewer
from torch import nn
import sim_runtime as rt
from current_sim import CurrentSim
torch.set_num_threads(1)
class Policy:
 def __init__(self,path):
  b=Path(path).read_bytes();self.SHA=hashlib.sha256(b).hexdigest();assert self.SHA=='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8';self.root=torch.load(io.BytesIO(b),map_location='cpu',weights_only=False);s=self.root['actor_state_dict'];assert set(k for k in s if not k.startswith('mlp.'))=={'distribution.std_param'},list(s);self.input_width=int(s['mlp.0.weight'].shape[1]);assert self.input_width==35;layers=[]
  for i in(0,2,4,6):
   weight=s[f'mlp.{i}.weight'];layers.append(nn.Linear(weight.shape[1],weight.shape[0]));
   if i!=6:layers.append(nn.ELU())
  self.model=nn.Module();self.model.add_module('mlp',nn.Sequential(*layers));self.model.load_state_dict({k:v for k,v in s.items()if k.startswith('mlp.')},strict=True);self.model.eval();self.iteration=int(self.root['iter'])
 def __call__(self,obs):
  with torch.inference_mode():a=self.model.mlp(torch.from_numpy(np.asarray(obs,dtype=np.float32).reshape(1,35))).clamp(-6,6)[0].numpy().astype(np.float64)
  assert np.isfinite(a).all();return a
rt.OnnxPolicy=Policy
class E3Sim(CurrentSim):
 def __init__(self):
  self.reset_bank=json.loads((PLAYER/'src_snapshot/reset_bank.json').read_text())['poses'];self.spawn=(-4.,0.,0.);cfg=json.loads((PLAYER/'runtime_config.json').read_text());cfg.update(policy_hz=50,yaw_assist_gain=0);rt.Mod4Sim.__init__(self,PLAYER/'playground.xml',D/'current_E3.pt',rt.RuntimeConfig(**cfg));self.model.opt.timestep=.0025;self.decimation=8;self.fall(0)
 def fall(self,which):
  CurrentSim.reset(self,-4,0,0,0);self.command.mode=3;self.command.auto_mode=False;self.command.vx=self.command.vy=self.command.wz=0.;r,p=((math.pi/2,0),(-math.pi/2,0),(0,math.pi/2),(math.pi,0),(0,0))[which];cr,sr,cp,sp=math.cos(r/2),math.sin(r/2),math.cos(p/2),math.sin(p/2);self.data.qpos[3:7]=(cr*cp,sr*cp,cr*sp,-sr*sp);self.data.qpos[2]=.44 if which<4 else .25;self.data.qvel[:]=0;self.data.ctrl[:]=0;mujoco.mj_forward(self.model,self.data);self._seed_observation_history(self.observation_frame());self.last_action[:]=0
state={'paused':False,'recipe':0,'reset':False,'normal':False};lock=threading.Lock();names=['LEFT SIDE','RIGHT SIDE','FORWARD FALL','UPSIDE DOWN','UPRIGHT'];sim=None

def put(name,x):
 p=D/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf8');os.replace(t,p)
def key(k):
 with lock:
  if k in(ord('G'),ord('g')):state['paused']=not state['paused']
  elif k in(ord('F'),ord('f')):state['recipe']=(state['recipe']+1)%4;state['reset']=True
  elif k in(ord('R'),ord('r')):state['reset']=True
  elif k in(ord('N'),ord('n')):state['recipe']=4;state['reset']=True

def title():
 try:
  user=ctypes.windll.user32;cb=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
  def visit(hwnd,lparam):
   pid=ctypes.c_ulong();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
   if pid.value==os.getpid()and user.IsWindowVisible(hwnd):user.SetWindowTextW(hwnd,'MOD4v1 E3 1cd99995 | Live MuJoCo | F fall / R reset / G pause / N upright')
   return True
  user.EnumWindows(cb(visit),0)
 except Exception:pass
try:
 sim=E3Sim();last_status=0;warm=time.perf_counter()+1.;recipe_time=sim.data.time;total=0
 with mujoco.viewer.launch_passive(sim.model,sim.data,key_callback=key)as viewer:
  viewer.cam.lookat[:]=sim.data.qpos[:3];viewer.cam.distance=2.;viewer.cam.azimuth=135.;viewer.cam.elevation=-20.;viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT]=False;viewer.sync();title();put('VIEWER_STARTED.json',dict(pid=os.getpid(),epoch=time.time(),viewer_running=viewer.is_running(),model_SHA=sim.policy.SHA,iteration=sim.policy.iteration,physics_backend='MuJoCo local demonstration, not Isaac/fullDR score',policy_hz=50,physics_dt=.0025,adapter=str(PLAYER),runtime_config=vars(sim.cfg),controls='F next fall; R reset; G pause; N upright; close window exits',training_or_registry_changes=False))
  while viewer.is_running():
   begin=time.perf_counter()
   with lock:s=dict(state);state['reset']=False
   if s['reset']:sim.fall(s['recipe']);recipe_time=sim.data.time;warm=time.perf_counter()+.5
   if not s['paused']and time.perf_counter()>=warm:
    sim.step_control();total+=1
    if sim.data.time-recipe_time>=8.:
     with lock:state['reset']=True
   viewer.cam.lookat[:]=sim.data.qpos[:3];viewer.sync()
   if time.perf_counter()-last_status>.5:
    gravity=sim.data.xmat[sim.chassis_id].reshape(3,3).T@np.array([0.,0.,-1.]);put('CURRENT.json',dict(pid=os.getpid(),epoch=time.time(),viewer_running=viewer.is_running(),total_controls=total,recipe=names[s['recipe']],paused=s['paused'],finite=bool(np.isfinite(sim.data.qpos).all()),base_xyz=sim.data.qpos[:3].tolist(),projected_gravity=gravity.tolist(),model_SHA=sim.policy.SHA));last_status=time.perf_counter()
   time.sleep(max(0,.02-(time.perf_counter()-begin)))
 put('CLOSED.json',dict(epoch=time.time(),pid=os.getpid(),actual_viewer_context_returned=True,total_controls=total))
except BaseException:
 put('ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc()));raise
