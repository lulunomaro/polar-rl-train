"""Interactive latest40m low-speed stair replay using the existing MOD4 control framework."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys,time,traceback,types
import numpy as np,torch,mujoco,tkinter as tk
from tkinter import ttk
T=Path(__file__).resolve().parent;R=T.parents[2];D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
p=argparse.ArgumentParser();p.add_argument('--checkpoint',default=str(T/'weights/model_040m.pt'));a=p.parse_args();torch.set_num_threads(1)
O=T/'evidence/manual_low_speed'/time.strftime('%Y%m%d_%H%M%S');O.mkdir(parents=True,exist_ok=False)
CKPT=Path(a.checkpoint).resolve();SHA=hashlib.sha256(CKPT.read_bytes()).hexdigest();B=T/'manual_low_speed_scene';(B/'tiles').mkdir(parents=True,exist_ok=True)
source=np.load(D/'viewer/tiles/r03_c00.npz');v=source['vertices'].copy();v[:,2]*=.2/float(np.unique(v[:,2])[1]);np.savez_compressed(B/'tiles/r03_c00.npz',vertices=v,faces=source['faces'])
spec=importlib.util.spec_from_file_location('showcase',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);sys.modules['showcase']=show;spec.loader.exec_module(show);show.B=B;show.CKPT=CKPT;show.EXPECTED=SHA
sys.path.insert(0,str(T/'manual_replay'));from replay_supported_guards import replay_step
show.Replay.step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=O/'reset_events')
OriginalReplay=show.Replay
class LowReplay(OriginalReplay):
 def __init__(self,level=3,family=None,direction='up',show=True):
  super().__init__(level=3,family=globals()['show'].FAMILIES[0],direction='up',show=show)
  self.args.vx=.4;self.args.wz=1.;self.set_height(.42);self.paused=True
  owner=self
  def physics(env,act):
   act=act.clamp(-env.action_clip,env.action_clip)
   for j in range(env.decim):
    tau=env._torque(act).detach().cpu().numpy().reshape(-1)
    if j%4==0:env.d.ctrl[env.act_ids[:4]]=tau[:4]
    env.d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(env.m,env.d)
    if not np.isfinite(env.d.qpos).all() or not np.isfinite(env.d.qvel).all():raise globals()['show'].SafetyStop('nonfinite')
    owner.closure=max(float(np.linalg.norm(env.d.site_xpos[u]-env.d.site_xpos[w])) for u,w in owner.pairs)
    if owner.closure>.002:raise globals()['show'].SafetyStop('closure>2mm')
   env.a_prev=act.detach().to(env.device);return env.state()
  self.env.step=types.MethodType(physics,self.env)
  if self.viewer is not None:self.viewer.cam.azimuth=90.;self.viewer.cam.elevation=-12.;self.viewer.cam.distance=3.0
show.Replay=LowReplay
sys.path.insert(0,str(D/'viewer'));from manual_control import ManualRoughControl
class LowControl(ManualRoughControl):
 def _build(self):
  super()._build();self.root.title('MOD4 40m | 低速后摆上台阶 · 键盘操控');self.root.geometry('555x895+20+25');self.root.minsize(535,855)
  self.family_var.set(show.CN[0]);self.level_var.set(3);self._last_trace=0.
  def walk(widget):
   for child in widget.winfo_children():yield child;yield from walk(child)
  for widget in list(walk(self.root)):
   if isinstance(widget,ttk.Combobox):
    widget.configure(values=[show.CN[0]] if str(widget.cget('textvariable'))==str(self.family_var) else [3])
   if isinstance(widget,tk.Label) and widget.cget('text')=='Rough-v1 120m · 手动驾驶与高度控制':widget.configure(text='40分钟检查点 · 低速上连续20cm台阶')
   if isinstance(widget,tk.Button) and widget.cget('text') in ('载入下台阶起点','载入跑图起点','打开完整地形地图'):widget.configure(state='disabled')
   if isinstance(widget,tk.Scale) and widget.cget('label')=='行驶速度 m/s':widget.configure(to=1.,resolution=.05)
  frame=tk.Frame(self.root,bg=self.BG);frame.pack(fill='x',padx=14,pady=(0,8))
  tk.Button(frame,text='载入已搭阶姿态（观察后摆抬轮）',command=self.load_supported,takefocus=False).pack(fill='x')
  tk.Label(frame,text='默认0.4m/s；4 / 5 / 6 切换0.4 / 0.6 / 0.75m/s',bg=self.BG,fg=self.TEXT,font=('Microsoft YaHei UI',10)).pack(anchor='w',pady=4)
 def _handle_key_down(self,key):
  if key in {'4','5','6'}:
   speed={'4':.4,'5':.6,'6':.75}[key];self.speed_var.set(speed);self.sim.args.vx=speed;self._event(f'speed {speed:.2f}m/s');return
  super()._handle_key_down(key)
 def load_scene(self,direction):
  self.family_var.set(show.CN[0]);self.level_var.set(3);return super().load_scene('up')
 def load_supported(self):
  self.keys.clear();s=self.sim;s.reset_standing();e=s.env;d=e.d;m=e.m
  bank=json.loads((T/'support/mod4v3_ppo_v1/rearward_mount_bank.json').read_text())['poses'][0]
  for name,value in bank['joint_positions'].items():d.qpos[m.joint(name).qposadr[0]]=value
  d.qpos[:7]=[-2.9+bank['root_inward_of_edge_m'],0.,.3785,1.,0.,0.,0.];d.qvel[:]=0.;mujoco.mj_forward(m,d);e.state();s.z=float(e.z)-s.ground(float(d.qpos[0]),float(d.qpos[1]));s._repair_stair_stage=0;s._repair_contact_steps=0;s._replay_tilt_steps=0;s.paused=True;s.set_height(.42)
  if s.viewer is not None:s.viewer.sync()
  self._event('已载入底盘搭阶姿态，按P运行，再按住W');self._focus_control();print('SUPPORTED_START_LOADED',json.dumps(dict(epoch=time.time(),root=d.qpos[:3].tolist())),flush=True)
 def _update_ui(self):
  super()._update_ui();now=time.monotonic();s=self.sim;e=s.env;d=e.d;wb=[e.m.body(n).id for n in ('left_wheel_link','right_wheel_link')];w=d.xpos[wb];axis=d.xmat[e.base_id].reshape(3,3)[:,0];rear=((w-d.qpos[:3])@axis).tolist();contact=getattr(s,'last_contact_state',{});stage=int(contact.get('stair_landing_stage',0));target=.2 if stage==0 else .4;clear=(w[:,2]-.0625-target).tolist()
  self.status_var.set(self.status_var.get()+f'\n轮轴相对机身前后 {rear[0]:+.3f} / {rear[1]:+.3f}m\n（负数为向后）轮底距下一台面 {min(clear):+.3f}m')
  if now-self._last_trace>=.1:
   self._last_trace=now;row=dict(epoch=time.time(),simulation_time_s=float(d.time),paused=s.paused,keys=sorted(self.keys),root_xyz=d.qpos[:3].tolist(),wheel_xyz=w.tolist(),wheel_relative_forward_m=rear,wheel_bottom_to_target_tread_m=clear,vx=float(e.vx),cmd_vx=s.cmd_vx,height_command=s.height,closure_m=s.closure,body_guide_support_N=contact.get('upper_tread_body_guide_upward_N'),stair_stage=stage,resets=s.reset_count-1,reason=s.reason)
   with (O/'trajectory.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
   (O/'STATUS.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
try:
 root=tk.Tk();sim=LowReplay(show=True);app=LowControl(root,sim);root.update_idletasks();root.update();root.after(200,app._focus_control)
 ready=dict(epoch=time.time(),checkpoint=str(CKPT),sha256=SHA,manual=True,paused=True,speed_m_s=.4,height_m=.42,steps=2,riser_m=.2,tread_m=1.5,viewer_running=sim.viewer.is_running(),control_window_exists=bool(root.winfo_exists()),logs=str(O),same_control_framework=True,policy_optimizer_constructed=False)
 (O/'READY.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n');(T/'evidence/MANUAL_LOW_SPEED_LATEST.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n');print('MANUAL_LOW_SPEED_READY '+json.dumps(ready,ensure_ascii=False),flush=True);root.mainloop()
except BaseException:
 (O/'ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),ensure_ascii=False,indent=2)+'\n');raise
