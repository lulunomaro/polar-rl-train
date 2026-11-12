"""Matched nominal manual-stair retention; never opens or edits the user's replay."""
from pathlib import Path
import argparse,sys,json,hashlib,time,importlib.util,types,shutil
import torch,numpy as np,mujoco
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);a=p.parse_args();torch.set_num_threads(1)
T=Path(__file__).resolve().parent;R=T.parents[2];D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';plan=json.loads((T/'PLAN.json').read_text());ld=4;wd=1
spec=importlib.util.spec_from_file_location('repair_stair_source',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)
E=Path(a.out).resolve();E.mkdir(exist_ok=False);B=E/'scene_assets';(B/'tiles').mkdir(parents=True);tile='r00_c00';source_tile=np.load(D/'viewer/tiles/r03_c00.npz');vertices=source_tile['vertices'].copy();vertices[:,2]*=.2/float(np.unique(vertices[:,2])[1]);np.savez_compressed(B/'tiles'/f'{tile}.npz',vertices=vertices,faces=source_tile['faces']);show.B=B
show.CKPT=Path(a.model).resolve();show.EXPECTED=hashlib.sha256(show.CKPT.read_bytes()).hexdigest();rows=[]
for direction,height,speed in [('up',.365,2.2),('up',.4,2.2),('up',.365,1.5),('down',.28,1.)]:
 s=show.Replay(direction=direction);s.args.vx=speed;trajectory=[];success=False;peak_x=-100.;peak_ground=0.;scene=Path(s.args.xml);shutil.copy2(scene,E/(f'{direction}_h{height}_scene.xml'))
 def physics(env,act):
  act=act.clamp(-env.action_clip,env.action_clip)
  for j in range(env.decim):
   if j%ld==0 or j%wd==0:
    tau=env._torque(act).detach().numpy().reshape(-1)
    if j%ld==0:env.d.ctrl[env.act_ids[:4]]=tau[:4]
    if j%wd==0:env.d.ctrl[env.act_ids[4:]]=tau[4:]
   mujoco.mj_step(env.m,env.d)
   if not np.isfinite(env.d.qpos).all() or not np.isfinite(env.d.qvel).all():raise show.SafetyStop('nonfinite')
   s.closure=max(float(np.linalg.norm(env.d.site_xpos[u]-env.d.site_xpos[v])) for u,v in s.pairs)
   if s.closure>.002:raise show.SafetyStop('closure>2mm')
  env.a_prev=act.detach().to(env.device);return env.state()
 s.env.step=types.MethodType(physics,s.env)
 try:
  for k in range(1000):
   s.set_height(.28+(height-.28)*min(k/100.,1.));s.step({'w'} if k>=150 else set());x,y=map(float,s.env.d.qpos[:2]);ground=s.ground(x,y);peak_x=max(x,peak_x);peak_ground=max(ground,peak_ground)
   trajectory.append(dict(t=k*.02,x=x,y=y,ground=ground,relative_height=float(s.z),vx=float(s.env.vx),command_height=s.height,closure=s.closure,resets=s.reset_count-1,reason=s.reason))
   success=bool(s.reset_count==1 and s.cos_tilt>.766 and s.z>.18 and ((direction=='up' and x>-.9 and ground>.30) or (direction=='down' and x>3.8 and ground<.02)))
   if success or s.reset_count>1:break
  rows.append(dict(direction=direction,height=height,speed=speed,success=success,peak_x=peak_x,peak_ground=peak_ground,resets=s.reset_count-1,reason=s.reason,trajectory=trajectory));(E/f'{direction}_h{height}.json').write_text(json.dumps(rows[-1],indent=2))
 finally:s.close()
result=dict(model=str(show.CKPT),sha256=show.EXPECTED,protocol='Level3 horizontal geometry r03c00;two20cmsteps/40cmplatform;legacyrootpointheightguard;2sheight ramp;forward starts3s;deterministicnominal;1case/model/setting;original.28/1.0stall is reference,not an expected success;2mmguard;noGUI;no fullDR claim',physics_s=.0025,leg_PD_s=ld*.0025,wheel_PD_s=wd*.0025,source_showcase_sha256=hashlib.sha256((D/'viewer/showcase.py').read_bytes()).hexdigest(),rows=rows)
(E/'RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(sha256=show.EXPECTED,rows=[{k:v for k,v in x.items() if k!='trajectory'} for x in rows])),flush=True)
