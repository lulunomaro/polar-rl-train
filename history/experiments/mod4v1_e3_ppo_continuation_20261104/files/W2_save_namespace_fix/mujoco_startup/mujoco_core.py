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
  b=Path(path).read_bytes();self.SHA=hashlib.sha256(b).hexdigest();assert self.SHA=='a3cef1489614a018492bbe3078e752e3384604371ddaf7a3fa0062d728923fec';self.root=torch.load(io.BytesIO(b),map_location='cpu',weights_only=False);s=self.root['actor_state_dict'];assert set(k for k in s if not k.startswith('mlp.'))=={'distribution.std_param'},list(s);self.input_width=int(s['mlp.0.weight'].shape[1]);assert self.input_width==35;layers=[]
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
  self.reset_bank=json.loads((PLAYER/'src_snapshot/reset_bank.json').read_text())['poses'];self.spawn=(-4.,0.,0.);cfg=json.loads((PLAYER/'runtime_config.json').read_text());cfg.update(policy_hz=50,yaw_assist_gain=0);rt.Mod4Sim.__init__(self,Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4/scene.xml'),D/'current_E3.pt',rt.RuntimeConfig(**cfg));self.model.opt.timestep=.0025;self.decimation=8;
  for n in ('left_gas_slide','right_gas_slide'):
   j=self._joint(n);self.model.jnt_stiffness[j]=2000.;self.model.dof_damping[self.model.jnt_dofadr[j]]=3.;self.model.qpos_spring[self.model.jnt_qposadr[j]]=.2
  self.fall(0)
 def fall(self,which):
  CurrentSim.reset(self,-4,0,0,0);self.command.mode=3;self.command.auto_mode=False;self.command.vx=self.command.vy=self.command.wz=0.;r,p=((math.pi/2,0),(-math.pi/2,0),(0,math.pi/2),(math.pi,0),(0,0))[which];cr,sr,cp,sp=math.cos(r/2),math.sin(r/2),math.cos(p/2),math.sin(p/2);self.data.qpos[3:7]=(cr*cp,sr*cp,cr*sp,-sr*sp);self.data.qpos[2]=.44 if which<4 else .25;self.data.qvel[:]=0;self.data.ctrl[:]=0;mujoco.mj_forward(self.model,self.data);self._seed_observation_history(self.observation_frame());self.last_action[:]=0
