import argparse, sys
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser();AppLauncher.add_app_launcher_args(p);args=p.parse_args();app=AppLauncher(args).app
import torch
sys.path.insert(0,str(Path(__file__).parent/'source'/'mod4'))
from mod4_task import Mod4EnvCfg
from mod4_env import Mod4Env
cfg=Mod4EnvCfg();cfg.scene.num_envs=128
env=Mod4Env(cfg=cfg)
try:
 env.reset();robot=env.scene['robot'];dev=env.device
 combos=[(v,x) for v in (-8,-4,-2,-1,0,1,2,4) for x in (-2,-1,0,1)]
 g=torch.tensor([i//4 for i in range(128)],device=dev)
 kvs=torch.tensor([x[0] for x in combos],device=dev)[g]
 kxs=torch.tensor([x[1] for x in combos],device=dev)[g]
 ever=torch.zeros(128,dtype=torch.bool,device=dev)
 a=torch.zeros(128,6,device=dev)
 for i in range(201):
  grav=robot.data.projected_gravity_b[:,0]
  rate=robot.data.root_ang_vel_b[:,1]
  vx=robot.data.root_lin_vel_w[:,0]
  x=robot.data.root_pos_w[:,0]-env.scene.env_origins[:,0]
  a[:,4:6]=(10*grav+3*rate+kvs*vx+kxs*x).clamp(-1,1).unsqueeze(1)
  _,_,term,trunc,_=env.step(a)
  ever|=term|trunc
  if i in (20,40,80,120,200):
   tilt=torch.rad2deg(torch.acos((-robot.data.projected_gravity_b[:,2]).clamp(-1,1)))
   print('STEP',i,flush=True)
   for j,(kv,kx) in enumerate(combos):
    sl=slice(j*4,(j+1)*4)
    print('GAIN',kv,kx,'tilt',round(float(tilt[sl].mean()),2),'ever_done',round(float(ever[sl].float().mean()),2),'speed',round(float(robot.data.root_lin_vel_b[sl,:2].norm(dim=1).mean()),2),flush=True)
finally:
 env.close();app.close()
