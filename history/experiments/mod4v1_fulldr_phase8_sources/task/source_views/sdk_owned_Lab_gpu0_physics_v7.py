
from pathlib import Path
import json,os,sys,time,traceback
r=Path('/home/lc01/Zonglin Li/zonglin2');gpu=int(os.environ['ZONGLIN2_PHYSICAL_GPU']);app=None
try:
 from isaaclab.app import AppLauncher
 class OwnedAppLauncher(AppLauncher):
  def _create_app(self):
   self._sim_app_config['enable_crashreporter']=False
   self._sim_app_config['extra_args']=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false']
   super()._create_app()
 launcher=OwnedAppLauncher(headless=True,device='cuda:0',enable_cameras=False,livestream=0,enable_crashreporter=False,extra_args=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false'])
 app=launcher.app
 import torch,isaaclab,isaaclab.sim as sim_utils,isaaclab.envs,isaaclab.assets,isaaclab_physx,tensordict,rsl_rl
 from pxr import UsdGeom,UsdPhysics,Gf
 sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.0025,device='cuda:0'))
 stage=sim.stage
 ground=UsdGeom.Cube.Define(stage,'/World/OwnedLabProbeGround');ground.CreateSizeAttr(1.)
 ground.AddTranslateOp().Set(Gf.Vec3d(0.,0.,-.05));ground.AddScaleOp().Set(Gf.Vec3f(10.,10.,.1));UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
 box=UsdGeom.Cube.Define(stage,'/World/OwnedLabProbeBox');box.CreateSizeAttr(.1);box.AddTranslateOp().Set(Gf.Vec3d(0.,0.,1.))
 UsdPhysics.CollisionAPI.Apply(box.GetPrim());UsdPhysics.RigidBodyAPI.Apply(box.GetPrim())
 sim.reset()
 view=sim.physics_sim_view
 assert view.cuda_context is not None,'No actual GPU physics context'
 body=view.create_rigid_body_view('/World/OwnedLabProbeBox')
 import warp as wp
 def tensor(x):return x.clone() if isinstance(x,torch.Tensor) else wp.to_torch(x).clone()
 initial=tensor(body.get_transforms())
 assert initial.is_cuda and bool(torch.isfinite(initial).all())
 for i in range(24):sim.step(render=False)
 pose=tensor(body.get_transforms());vel=tensor(body.get_velocities());torch.cuda.synchronize()
 assert pose.is_cuda and vel.is_cuda and bool(torch.isfinite(pose).all()) and bool(torch.isfinite(vel).all())
 assert sim.get_physics_step_count()==24 and abs(sim.get_physics_dt()-.0025)<1e-12
 assert 0.<float(pose[0,2])<float(initial[0,2])
 import subprocess
 env={k:v for k,v in os.environ.items() if k not in ('LD_LIBRARY_PATH','LD_PRELOAD','PYTHONHOME','PYTHONPATH')}
 nv=subprocess.run(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],capture_output=True,text=True,env=env,check=True)
 rows=[x.split(', ') for x in nv.stdout.strip().splitlines() if x.strip()];own=[x for x in rows if int(x[1])==os.getpid()]
 expected={0:'GPU-16828f91-2b45-b646-8dc0-9481138e2842',1:'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}
 assert {x[0] for x in own}=={expected[gpu]},own
 imports={name:getattr(sys.modules[name],'__file__',None) for name in ('isaaclab','isaaclab.envs','isaaclab.assets','isaaclab_physx','tensordict','rsl_rl')}
 assert all(p is None or str(p).startswith(str(r)+'/') for p in imports.values())
 v=dict(epoch=time.time(),passed=True,physical_GPU=gpu,actual_own_compute_rows=own,Lab_AppLauncher_headless=True,
  actual_physics_steps=sim.get_physics_step_count(),dt=sim.get_physics_dt(),initial_pose=initial.cpu().tolist(),final_pose=pose.cpu().tolist(),final_velocity=vel.cpu().tolist(),
  actual_native_CUDA_context_and_CUDA_pose_velocity=True,imports=imports,
  actual_source_Lab_SimulationContext_stage_reset_and_PhysX=True,not_default_World_V3_replay=True,
  no_renderer_GUI_MOD4_contact_fullstate_policy_PPO_or_budget_admission=True)
 with (r/('audit/LAB_GPU'+str(gpu)+'_PHYSX_V7_DATA_COMPLETE_ACTUAL.json')).open('x') as f:json.dump(v,f,indent=2)
 print(json.dumps(v),flush=True)
 body=None;view=None;pose=None;vel=None;initial=None
 sim.stop();sim_utils.SimulationContext.clear_instance()
 app.close()
except BaseException:
 with (r/('audit/LAB_GPU'+str(gpu)+'_PHYSX_V7_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc()),f,indent=2)
 traceback.print_exc()
 if app is not None:app.close(exit_code=1)
 raise
