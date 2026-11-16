"""Interactive WASD for the frozen pre-wall actors. Pure35->6, no teacher."""
from pathlib import Path
import sys,json,time,types,ast,inspect,textwrap,hashlib,argparse
import numpy as np,torch,mujoco as mj
import tkinter as tk
from tkinter import ttk
T=Path(__file__).resolve().parent;X=T.parent;R=X.parents[2]
D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';CORE=D/'runtime/core'
P=R/'sources/local/MOD4V3_FIXED200_SETTLE_CRUISE_REPAIR_10M_20261116'
sys.path.insert(0,str(CORE));import play_ppo_flatv1_control as base
CHOICES={'刚才64步副本 · faec0177':X/'offline_probe_keep1/actor_probe.pt','repair10m · 28360ac4':P/'weights/model_010m.pt'}
EXPECTED=['left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint']
MODES={'stair 上阶':np.array([0,1,0,0,0,1,0],np.float32),'normal 普通':np.array([1,0,0,0,0,0,0],np.float32)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def native_step(env,a):
 a=a.clamp(-6,6)
 for j in range(8):
  tau=env._torque(a).detach().cpu().numpy().reshape(-1)
  if j%4==0:env.d.ctrl[env.act_ids[:4]]=tau[:4]
  env.d.ctrl[env.act_ids[4:]]=tau[4:];mj.mj_step(env.m,env.d)
 env.a_prev=a.detach().clone();return env.state()

def raw_advance():
 tree=ast.parse(textwrap.dedent(inspect.getsource(base.Simulation.step)));fn=tree.body[0];out=[];removed=0
 for node in fn.body:
  if isinstance(node,ast.If)and any(isinstance(n,ast.Attribute)and n.attr=='term_height'for n in ast.walk(node)):removed+=1;continue
  out.append(node)
 assert removed==1;fn.body=out;ast.fix_missing_locations(tree);scope=dict(base.Simulation.step.__globals__);exec(compile(tree,'<manual_without_flat_height_reset>','exec'),scope);return scope['step']
ADVANCE=raw_advance()
class ModeActor(torch.nn.Module):
 def __init__(self,sim):super().__init__();self.sim=sim
 def forward(self,obs):
  obs=obs.clone();obs[:,28:35]=torch.as_tensor(MODES[self.sim.mode_name],device=obs.device)
  return self.sim.policy(obs)
class ManualSimulation(base.Simulation):
 def __init__(self,args):
  super().__init__(args);assert abs(self.env.m.opt.timestep-.0025)<1e-12
  self.env.step=types.MethodType(native_step,self.env);self.env.dt=.0025;self.env.decim=8
  cap=np.load(X/'dagger/model_010m/start_+000mm/student_capture/capture.npz');self.initial_qpos=cap['pre_qpos'][0].copy()
  self.mode_name='stair 上阶';self.policy_name=next(iter(CHOICES));self.policy=None;self.actor=ModeActor(self)
  self.loop_pairs=[(self.env.m.site(e.get('site1')).id,self.env.m.site(e.get('site2')).id)for e in __import__('xml.etree.ElementTree',fromlist=['parse']).parse(args.xml).getroot().findall('equality/connect')]
  self.tilt_ticks=0;self.paused=True;self.select_policy(self.policy_name)
  self.viewer.cam.azimuth=105.;self.viewer.cam.elevation=-18.;self.viewer.cam.distance=2.2
 def select_policy(self,name):
  ck=torch.load(CHOICES[name],map_location='cpu',weights_only=False)
  if 'action_order'in ck:assert list(ck['action_order'])==EXPECTED
  actor=base.ActorMLP();result=actor.load_state_dict(ck['actor_state_dict'],strict=False);assert not result.missing_keys;assert set(result.unexpected_keys)<={'distribution.std_param'}
  self.policy=actor.eval();self.policy_name=name;self.paused=True;self.reset_standing()
  put(T/'CURRENT_SELECTION.json',dict(policy=name,weight_path=str(CHOICES[name]),sha256=sha(CHOICES[name]),mode=self.mode_name,teacher_actions=0,policy_dimensions=[35,6],physics_s=.0025,leg_hz=100,wheel_hz=400,policy_hz=50,action_smoothing=0.,default_promoted=False))
 def reset_standing(self):
  mj.mj_resetData(self.env.m,self.env.d);self.env.d.qpos[:]=self.initial_qpos;mj.mj_forward(self.env.m,self.env.d);self.env.a_prev.zero_();self.a_prev.zero_();self._action_filter=None
  self.cmd_vx=self.cmd_vy=self.cmd_wz=0.;self.height=.4091;self.tilt_ticks=0;self.tracker.reset();self.z=self.env.z;self.cos_tilt=self.env.cos_tilt
 def step(self,pressed):
  result=ADVANCE(self,pressed)
  if self.paused:return result
  d=self.env.d;rot=d.xmat[self.env.base_id].reshape(3,3);pitch=float(np.arcsin(np.clip(-rot[2,0],-1,1)));roll=float(np.arctan2(rot[2,1],rot[2,2]));self.tilt_ticks=self.tilt_ticks+1 if max(abs(pitch),abs(roll))>np.deg2rad(40)else 0
  closure=max(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b])for a,b in self.loop_pairs)
  if not(np.isfinite(d.qpos).all()and np.isfinite(d.qvel).all())or closure>1. or d.qpos[2]<.11 or self.tilt_ticks>=10:
   print('MANUAL_RESET',float(d.time),'z',float(d.qpos[2]),'closure',float(closure),flush=True);self.reset_standing()
  if self.steps%50==0:put(T/'LIVE_STATUS.json',dict(policy=self.policy_name,mode=self.mode_name,paused=self.paused,steps=self.steps,simulation_time_s=float(d.time),root_xyz=d.qpos[:3].tolist(),height_command_m=self.height,forward_command_m_s=self.cmd_vx,actual_vx=float(self.env.vx),closure_diagnostic_m=float(closure),teacher_actions=0))
  return self.telemetry()
class ManualApp(base.ControlApp):
 def _build(self):
  super()._build();self.root.title('MOD4v3 WASD · 刚才实验策略 · 200mm单台阶');self.root.geometry('540x930')
  top=tk.Frame(self.root,bg=self.BG,padx=16,pady=7);top.pack(fill='x',before=self.root.winfo_children()[0])
  tk.Label(top,text='实验策略手动试玩 · 初始暂停，P 开始',bg=self.BG,fg=self.YELLOW,font=('Microsoft YaHei UI',11,'bold')).pack(anchor='w')
  self.model_var=tk.StringVar(value=self.sim.policy_name);cb=ttk.Combobox(top,textvariable=self.model_var,values=list(CHOICES),state='readonly',width=42);cb.pack(fill='x',pady=4);cb.bind('<<ComboboxSelected>>',self.change_model)
  self.mode_var=tk.StringVar(value=self.sim.mode_name);mb=ttk.Combobox(top,textvariable=self.mode_var,values=list(MODES),state='readonly',width=42);mb.pack(fill='x');mb.bind('<<ComboboxSelected>>',self.change_mode)
  tk.Label(top,text='W/S 前后 · A/D 转向 · Q/E 高度 · P 暂停 · R 复位',bg=self.BG,fg=self.TEXT,font=('Microsoft YaHei UI',9)).pack(anchor='w',pady=4)
 def change_model(self,event=None):
  self.keys.clear();self.sim.select_policy(self.model_var.get());self._event('已换策略并暂停；P开始');self._focus_control()
 def change_mode(self,event=None):
  self.keys.clear();self.sim.mode_name=self.mode_var.get();self.sim.select_policy(self.sim.policy_name);self._event('已换模式并暂停；P开始');self._focus_control()

def main():
 args=argparse.Namespace(ckpt=str(P/'weights/model_010m.pt'),xml=str(P/'evidence/checkpoint_evals/model_010m/single_step/start_+000mm/scene.xml'),runtime=str(D/'plant/MOD4v3_HW300N60_R3/runtime_config.json'),semantics=str(D/'plant/MOD4v3_HW300N60_R3/semantics.json'),bank=str(D/'plant/reset_bank.json'),template=str(CORE/'template_spec.json'),device='cpu',height=.4091,vx=.47,vy=.5,wz=1.2,term_height=.11,fall_interval=7.,drop_height=1.,drop_tilt=.75,action_ema=0.,start_fall=False,auto_fall=False,headless=False,steps=0,log_every=25)
 root=tk.Tk();sim=ManualSimulation(args);app=ManualApp(root,sim);root.after(100,app._focus_control)
 put(T/'READY.json',dict(ready=True,created_at=time.time(),selected_policy=sim.policy_name,policy_sha256=sha(CHOICES[sim.policy_name]),mode=sim.mode_name,initial_paused=True,control_interface='existing project WASD console',scene_xml=args.xml,scene_sha256=sha(Path(args.xml)),physics_s=.0025,leg_hz=100,wheel_hz=400,policy_hz=50,teacher_actions=0,no_optimizer=True,default_weights_changed=False))
 root.mainloop()
if __name__=='__main__':main()
