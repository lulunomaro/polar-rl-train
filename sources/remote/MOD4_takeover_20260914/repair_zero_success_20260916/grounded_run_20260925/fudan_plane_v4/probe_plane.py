import argparse, json, os, sys
from pathlib import Path
from isaaclab.app import AppLauncher
parser=argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args=parser.parse_args()
app=AppLauncher(args).app
import torch
from pxr import UsdPhysics
sys.path.insert(0,str(Path(__file__).parent/'source'/'mod4'))
from mod4_task import Mod4EnvCfg
from mod4_env import Mod4Env
import skills_isaac as skills
try:
 cfg=Mod4EnvCfg();cfg.scene.num_envs=64
 env=Mod4Env(cfg=cfg)
 stage=env.sim.stage
 ground=stage.GetPrimAtPath('/World/ground')
 coll=[str(p.GetPath()) for p in stage.Traverse() if str(p.GetPath()).startswith('/World/ground') and p.HasAPI(UsdPhysics.CollisionAPI)]
 print('GROUND',ground.IsValid(),coll[:20],flush=True)
 for q in stage.Traverse():
  name=str(q.GetPath())
  if 'left_wheel' in name and q.HasAPI(UsdPhysics.CollisionAPI):
   print('WHEEL_COLLIDER',name,q.GetTypeName(),[(a.GetName(),a.Get()) for a in q.GetAttributes() if a.GetName() in ('radius','height','xformOp:translate','xformOp:scale')],flush=True)
 env.reset()
 robot=env.scene['robot']; names=robot.body_names
 wheelids=[names.index('left_wheel'),names.index('right_wheel')]
 z=torch.zeros(env.num_envs,env.action_manager.total_action_dim,device=env.device)
 for i in range(301):
  if i: env.step(z)
  if i in (0,5,10,20,40,80,120,200,300):
   wf=env.scene.sensors['wheel_contact'].data.net_forces_w
   gf=env.scene.sensors['guide_contact'].data.net_forces_w
   print('POSE',i,'tiltdeg',float(torch.rad2deg(torch.acos((-robot.data.projected_gravity_b[:,2]).clamp(-1,1))).mean()),'joints',dict(zip(robot.joint_names,robot.data.joint_pos[0].cpu().tolist())),'episode0',int(env.episode_length_buf[0]),flush=True)
   print('CMD',i,'twist',env.command_manager.get_term('twist').command[:5].cpu().tolist(),'flag',env.command_manager.get_term('twist').is_standing_env[:5].cpu().tolist(),'standmask',skills._stand_mask(env)[:5].cpu().tolist(),'task',getattr(env,'_mod4_task_id',None),'route',getattr(env,'_mod4_routes',None) is not None,flush=True)
   print('STEP',i,'rootz',float(robot.data.root_pos_w[:,2].mean()),'wheelz',robot.data.body_pos_w[0,wheelids,2].cpu().tolist(),'wheelquat',robot.data.body_quat_w[0,wheelids].cpu().tolist(),'wforce',wf[0].norm(dim=-1).cpu().tolist(),'guideFmax',float(gf[0].norm(dim=-1).max()),'chassisF',float(env.scene.sensors['chassis_contact'].data.net_forces_w[0].norm(dim=-1).max()),'vz',float(robot.data.root_lin_vel_w[0,2]),'groundz',float(getattr(env,'_mod4_ground_z',torch.zeros(1,device=env.device))[0]),'eps',float(env.episode_length_buf.float().mean()),flush=True)
 env.close()
except BaseException as e:
 import traceback;traceback.print_exc()
 raise
finally:
 app.close()
