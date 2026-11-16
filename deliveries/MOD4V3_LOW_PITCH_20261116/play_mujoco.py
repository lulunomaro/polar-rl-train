"""Play the user-adopted Nov16 low-pitch MOD4v3 policy with the existing WASD UI."""
from pathlib import Path
import argparse,hashlib,json,sys,time,types,traceback,tkinter as tk,subprocess
import numpy as np
import torch,mujoco
HERE=Path(__file__).resolve().parent;R=HERE.parents[1];OLD=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';T=R/'sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116'
OUT=HERE/'playback_runtime';OUT.mkdir(exist_ok=True)
IDENTITY=json.loads((HERE/'MODEL_IDENTITY.json').read_text(encoding='utf8'));MODEL=HERE/'model_full_ppo.pt';SHA='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'
assert hashlib.sha256(MODEL.read_bytes()).hexdigest()==SHA==IDENTITY['sha256']
sys.path.insert(0,str(OLD/'viewer'));import showcase as show;import manual_control as controls;import play_ppo_flatv1_control as core
sys.path.insert(0,str(T/'manual_replay'));from replay_supported_guards import replay_step
show.CKPT=MODEL;show.EXPECTED=SHA;show.B=OUT/'scene_assets';(show.B/'tiles').mkdir(parents=True,exist_ok=True)
show.Replay.step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=OUT/'reset_events')
controls.B=OUT;controls.EXPECTED=SHA
# Match the evaluated hard command changes; policy, actuators and physics are unchanged.
core.CMD_SLEW=.02

def prepare(level,family):
 name=f'r{level:02d}_c{show.COLS[family]:02d}'
 target=show.B/'tiles'/(name+'.npz')
 if not target.exists():target.write_bytes((OLD/'viewer/tiles'/(name+'.npz')).read_bytes())
 cache=OLD/'viewer'/(name+'_hf_v2.npz')
 if cache.exists()and not(show.B/cache.name).exists():(show.B/cache.name).write_bytes(cache.read_bytes())

class LowPitchReplay(show.Replay):
 def __init__(self,level=0,family='plane_for_rm',direction='run',show=False):
  prepare(level,family);super().__init__(level=level,family=family,direction=direction,show=show)
  owner=self
  def physics(env,act):
   act=act.clamp(-env.action_clip,env.action_clip)
   for j in range(env.decim):
    tau=env._torque(act).detach().cpu().numpy().reshape(-1)
    if j%4==0:env.d.ctrl[env.act_ids[:4]]=tau[:4]
    env.d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(env.m,env.d)
    if not np.isfinite(env.d.qpos).all()or not np.isfinite(env.d.qvel).all():raise owner.SafetyError('nonfinite')
    owner.closure=max(float(np.linalg.norm(env.d.site_xpos[u]-env.d.site_xpos[v]))for u,v in owner.pairs)
    if owner.closure>.002:raise owner.SafetyError('closure>2mm')
   env.a_prev=act.detach().to(env.device);return env.state()
  self.SafetyError=show_module.SafetyStop;self.env.step=types.MethodType(physics,self.env)
 def reset_standing(self):
  super().reset_standing()
  if self.family in ['plane_for_rm','random_uniform_for_rm']:
   x,y=-.8,-.1;self.env.d.qpos[:3]=[x,y,self.ground(x,y)+self.env.bank_z];self.env.d.qvel[:]=0.;self.env.d.time=0.;mujoco.mj_forward(self.env.m,self.env.d);self.env.state();self.z=float(self.env.z)-self.ground(x,y)

show_module=show
controls.Replay=LowPitchReplay
class LowPitchControl(controls.ManualRoughControl):
 def _build(self):
  super()._build();self.root.title('11月16日俯仰较低模型 · MOD4v3 · c874a1af');self.root.geometry('550x825+30+30')
  def rewrite(widget):
   for child in widget.winfo_children():
    try:text=str(child.cget('text'))
    except tk.TclError:text=''
    if text=='Rough-v1 120m · 手动驾驶与高度控制':child.configure(text='11月16日俯仰较低模型 · c874a1af')
    elif text=='先按 P 开始；点击本控制窗后使用键盘，松开运动键停车。':child.configure(text='点击本控制窗使用 WASD；松键立即发停车指令。')
    rewrite(child)
  rewrite(self.root)
 def open_map(self):
  with(OUT/'map.log').open('a',encoding='utf8')as log:subprocess.Popen([sys.executable,'-X','utf8','-B',str(OLD/'viewer/showcase.py'),'--mode','map'],cwd=OLD/'viewer',stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 def _update_ui(self):
  super()._update_ui();d=self.sim.env.d;m=self.sim.env.m;base=self.sim.env.base_id;rotation=np.asarray(d.xmat[base]).reshape(3,3);g=rotation.T@np.array([0.,0.,-1.]);pitch=float(np.rad2deg(np.arctan2(g[0],np.linalg.norm(g[1:]))));velocity=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,base,velocity,1)
  self.status_var.set(self.status_var.get()+f'\n俯仰 {pitch:+.2f}° / 角速度 {velocity[1]:+.3f} rad/s')
  if time.monotonic()-getattr(self,'_own_last_write',0.)>.5:
   status=dict(epoch=time.time(),display_name=IDENTITY['display_name'],checkpoint=str(MODEL),sha256=SHA,iteration=IDENTITY['iteration'],viewer_running=bool(self.sim.viewer and self.sim.viewer.is_running()),control_window_visible=bool(self.root.winfo_viewable()),control_window_title=self.root.title(),paused=self.sim.paused,family=self.sim.family,level=self.sim.level,height_command=self.sim.height,height_measured=self.sim.z,pitch_deg=pitch,pitch_rate_rad_s=float(velocity[1]),physics_time=float(d.time),reset_count=self.sim.reset_count-1,closure_m=self.sim.closure,command_vx=self.sim.cmd_vx,actual_vx=float(self.sim.env.vx),physics_dt=.0025,leg_feedback_hz=100,wheel_feedback_hz=400,policy_hz=50,hard_command_changes=True,native_contact_material=True)
   (OUT/'PLAYER_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8');self._own_last_write=time.monotonic()

def main():
 p=argparse.ArgumentParser();p.add_argument('--height',type=float,default=.4);p.add_argument('--speed',type=float,default=1.2);p.add_argument('--rough',action='store_true');args=p.parse_args()
 root=tk.Tk();sim=LowPitchReplay(level=9 if args.rough else 0,family='random_uniform_for_rm'if args.rough else'plane_for_rm',show=True);sim.set_height(args.height);sim.args.vx=args.speed;sim.paused=False
 app=LowPitchControl(root,sim);root.after(200,app._focus_control)
 print('LOW_PITCH_MUJOCO_PLAYER_READY',json.dumps(dict(model_name=IDENTITY['display_name'],sha256=SHA,iteration=IDENTITY['iteration'],viewer_running=sim.viewer.is_running(),height=args.height,speed=args.speed,paused=False),ensure_ascii=False),flush=True)
 root.mainloop()
if __name__=='__main__':
 try:main()
 except Exception:
  (OUT/'PLAYER_ERROR.txt').write_text(traceback.format_exc(),encoding='utf8');raise
