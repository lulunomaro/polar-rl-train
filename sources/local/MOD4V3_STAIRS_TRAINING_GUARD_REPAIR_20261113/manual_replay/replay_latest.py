"""Manual latest-checkpoint replay on two200mm stairs, matched controller and wheel-height guard."""
from pathlib import Path
import importlib.util,sys,json,hashlib,types,shutil,time,traceback,math,xml.etree.ElementTree as ET
import numpy as np,torch,mujoco
sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay_training_guards import replay_step
T=Path(__file__).resolve().parents[1];R=T.parents[2];D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';OUT=Path(__file__).resolve().parent/'runtime'/'latest40m_guard_v3';OUT.mkdir(parents=True,exist_ok=True);(OUT/'tiles').mkdir(exist_ok=True)
MODEL=T/'weights/model_latest40m.pt';SHA='c90dac2ee66732e07faca8dae72877a7b3f2fe386deccf152d2d6d548eab3709';assert hashlib.sha256(MODEL.read_bytes()).hexdigest()==SHA
torch.set_num_threads(1)
spec=importlib.util.spec_from_file_location('showcase',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);sys.modules['showcase']=show;spec.loader.exec_module(show);show.CKPT=MODEL;show.EXPECTED=SHA;show.B=OUT
original_mesh=show.meshfile

def tiledata(level,family):
 name=f'r{level:02d}_c{show.COLS[family]:02d}';source=np.load(D/'viewer/tiles'/(name+'.npz'));vertices=source['vertices'].copy();faces=source['faces']
 if family in (show.FAMILIES[0],show.FAMILIES[4]) and level==3:
  vertices[:,2]*=.2/float(np.unique(vertices[:,2])[1]);name+='_200mm'
 dest=OUT/'tiles'/(name+'.npz')
 if not dest.exists():np.savez_compressed(dest,vertices=vertices,faces=faces)
 return name,vertices,faces
show.tiledata=tiledata
original_scene=show.make_scene

def scene(level,family):
 path,v,h=original_scene(level,family);tree=ET.parse(path);tree.getroot().set('model','MOD4 own recipe40m - manual200mm stairs');tree.write(path,encoding='utf8',xml_declaration=True);return path,v,h
show.make_scene=scene
OriginalReplay=show.Replay
class MatchedReplay(OriginalReplay):
 def __init__(self,level=3,family=None,direction='up',show=True):
  if family is None:family=globals()['show'].FAMILIES[0]
  super().__init__(level=level,family=family,direction=direction,show=show)
  owner=self
  def physics(env,act):
   act=act.clamp(-env.action_clip,env.action_clip)
   for j in range(env.decim):
    tau=env._torque(act).detach().cpu().numpy().reshape(-1)
    if j%4==0:env.d.ctrl[env.act_ids[:4]]=tau[:4]
    env.d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(env.m,env.d)
    if not np.isfinite(env.d.qpos).all() or not np.isfinite(env.d.qvel).all():raise globals()['show'].SafetyStop('nonfinite')
    owner.closure=max(float(np.linalg.norm(env.d.site_xpos[u]-env.d.site_xpos[v])) for u,v in owner.pairs)
    if owner.closure>.002:raise globals()['show'].SafetyStop('closure>2mm')
   env.a_prev=act.detach().to(env.device);return env.state()
  self.env.step=types.MethodType(physics,self.env);self.args.vx=2.2;self.args.wz=math.pi;self.set_height(.4);self.paused=True
 step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=OUT/'reset_events')
show.Replay=MatchedReplay
manual=types.ModuleType('manual_control');sys.modules['manual_control']=manual;source=(D/'viewer/manual_control.py').read_text(encoding='utf8').replace('MOD4 Rough-v1 120m | 手动控制与站立高度','MOD4 最新40分钟 | 台阶训练判定修复版').replace('Rough-v1 120m · 手动驾驶与高度控制','最新40分钟模型 · 台阶判定修复版')
source=source.replace('value=dict(manual=True,','value=dict(reset_count=self.sim.reset_count-1,last_guard_reset=getattr(self.sim,\"last_guard_reset\",None),last_reset_reason=self.sim.reason,manual=True,')
source=source.replace('\\n{self.last_event}', '\\n上次保护重置：{self.sim.reason}\\n{self.last_event}')
exec(compile(source,str(D/'viewer/manual_control.py'),'exec'),manual.__dict__)
def original_map(self):
 import subprocess
 subprocess.Popen([sys.executable,'-X','utf8','-u',str(D/'viewer/showcase.py'),'--mode','map'],cwd=D,stdin=subprocess.DEVNULL,stdout=(OUT/'original_map.log').open('w'),stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
manual.ManualRoughControl.open_map=original_map
try:
 (T/'evidence/MANUAL_REPLAY_READY.json').write_text(json.dumps({'epoch':time.time(),'model':str(MODEL),'sha256':SHA,'iteration':25050,'manual':True,'autoplay':False,'initial_paused':True,'terrain':'Level3 wide-stair geometry rescaled to2x200mm,tread1.5m','physics_s':.0025,'wheel_PD_s':.0025,'leg_PD_s':.01,'policy_s':.02,'height_reference':'minimum ground under the two drive wheels; no artificial0.18m reset; native terrain-fall rule','orientation_guard':'per-axis40deg for10consecutive50Hz endpoints, same native configured orientation dwell','closure_guard_m':.002,'contact_guard':'1N chassis/nonexempt guides for0.2s; guides allowed near ascending200mm stair edge','scope':'nominal MuJoCo contact analogue; latest frozen weights; not a PhysX force equivalence or new training pass'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 manual.run()
except BaseException:
 (T/'evidence/MANUAL_REPLAY_ERROR.json').write_text(json.dumps({'epoch':time.time(),'traceback':traceback.format_exc()},ensure_ascii=False,indent=2)+'\n',encoding='utf8');raise
