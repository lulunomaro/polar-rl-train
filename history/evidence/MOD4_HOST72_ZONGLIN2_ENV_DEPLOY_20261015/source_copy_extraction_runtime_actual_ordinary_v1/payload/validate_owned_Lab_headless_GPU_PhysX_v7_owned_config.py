"""New Lab-initialized physics-only deployment cases; original SDK V3 false retained."""
from pathlib import Path
import fcntl,json,os,subprocess,time,traceback
ROOT=Path('/home/lc01/Zonglin Li/zonglin2')
CODE=r'''
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
'''
def put(n,v):
 with (ROOT/'audit'/n).open('x') as f:json.dump(v,f,indent=2)
def identity(pid):
 q=Path('/proc')/str(pid)
 try:return dict(pid=pid,stat=(q/'stat').read_text(),argv=(q/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'))
 except FileNotFoundError:return dict(pid=pid,already_out=True)
def main():
 assert ROOT.resolve()==ROOT
 old=json.loads((ROOT/'audit/SDK_V3_FAILURE_CONFIG_API_EXIT_LOCK_READONLY_ACTUAL.json').read_bytes())
 assert old['actual_validation_fcntl_free'] and not old['actual_nvidia_compute_snapshot']['stdout'].strip()
 assert all(not x['actual_proc_exists'] for x in old['processes'])
 assert not (ROOT/'audit/LAB_PHYSX_V7_STARTED.json').exists()
 p=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],capture_output=True,text=True,check=True);assert not p.stdout.strip()
 with (ROOT/'state/finite_environment_validation.lock').open('rb+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  put('LAB_PHYSX_V7_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),identity=identity(os.getpid()),old_V3_errors_retained=True,no_tiny_CUDA_replay=True,original_V4_Warp_array_reader_error_preserved=True,original_V5_parent_package_attribute_metadata_error_preserved=True,read_only_Warp_to_Torch_then_clone=True,crashreporter_disabled_and_dump_preservation_requested=True))
  for gpu in (0,1):
   name='owned_Lab_gpu'+str(gpu)+'_physics_v7.py';script=ROOT/'audit'/name
   with script.open('x') as f:f.write(CODE)
   env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),ZONGLIN2_PHYSICAL_GPU=str(gpu),ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
   with (ROOT/'logs'/(name+'.stdout.log')).open('xb') as out,(ROOT/'logs'/(name+'.stderr.log')).open('xb') as err:
    child=subprocess.Popen([str(ROOT/'run-python-compat.sh'),str(script)],cwd=ROOT,env=env,stdout=out,stderr=err)
    put(name+'_STARTED.json',dict(epoch=time.time(),pid=child.pid,identity=identity(child.pid),physical_GPU=gpu))
    try:rc=child.wait(timeout=180)
    except subprocess.TimeoutExpired:
     put(name+'_TIMEOUT_NO_SIGNAL.json',dict(epoch=time.time(),pid=child.pid,no_kill_signal_or_next_worker=True));raise
   put(name+'_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=child.pid,returncode=rc,parent_waited_actual_exit=True))
   assert rc==0,'Read preserved own log and error report'
   assert json.loads((ROOT/('audit/LAB_GPU'+str(gpu)+'_PHYSX_V7_DATA_COMPLETE_ACTUAL.json')).read_bytes())['passed']
  put('LAB_PHYSX_V7_COMPLETE_ACTUAL.json',dict(epoch=time.time(),passed=True,both_actual_GPU_PhysX24steps_and_Lab_runtime_imports_passed=True,both_natural_exit0=True,original_V3_false_retained=True,no_training_or_MOD4_full_contract_claim=True))
  fcntl.flock(lock,fcntl.LOCK_UN)
 print(json.dumps(dict(both_Lab_GPU_PhysX_cases_passed=True,no_training=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('LAB_PHYSX_V7_PARENT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_delete_kill_or_blind_replay=True));raise
