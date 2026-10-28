"""No model/task import: separate cloned-runtime metadata/CUDA/simple-scene slices."""
from pathlib import Path
import argparse,hashlib,importlib.metadata as md,importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;COPY=Path('/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1/runtime_copy_v1');GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def tensor(x):return x.torch if hasattr(x,'torch') else x
def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['metadata','tensor','scene'],required=True);a=p.parse_args();assert B.resolve()==B and B.is_relative_to(Path('/data/robemo/polar-rl-train'));put(a.phase+'_BASIC_PYTHON_ACTUAL.json',dict(executable=sys.executable,prefix=sys.prefix,base_prefix=sys.base_prefix,version=sys.version,actual_glibc=os.confstr('CS_GNU_LIBC_VERSION')));assert Path(sys.prefix).resolve()==COPY/'envs/mod4'
 proc=Path('/proc/self');raw=(proc/'stat').read_text();fields=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));put(a.phase+'_OWN_CLONED_WORKER_IDENTITY.json',dict(pid=os.getpid(),creation=boot+int(fields[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink(proc/'exe'),argv=[os.fsdecode(x) for x in (proc/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.getcwd()))
 versions={k:md.version(k) for k in ['torch','torchvision','isaacsim','isaaclab','rsl-rl-lib','numpy','packaging','coverage']};expected={'torch':'2.10.0+cu128','torchvision':'0.25.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1','numpy':'2.5.2','packaging':'23.2','coverage':'7.6.1'};assert versions==expected
 if a.phase=='metadata':
  paths={k:importlib.util.find_spec(k).origin for k in ['isaaclab','rsl_rl']};assert all(Path(q).resolve().is_relative_to(COPY) for q in paths.values());put('CLONED_METADATA_AND_IMPORT_ROUTES_ACTUAL.json',dict(passed=True,epoch=time.time(),versions=versions,paths=paths,python_executable=sys.executable,prefix=sys.prefix,actual_runtime_glibc=os.confstr('CS_GNU_LIBC_VERSION'),original_dependency_metadata_conflicts_retained=True,no_Torch_SDK_GPU_or_model_import=True));return
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==GPU
 if a.phase=='tensor':
  import torch
  assert torch.cuda.is_available() and torch.cuda.device_count()==1 and torch.cuda.get_device_name(0)=='NVIDIA GeForce RTX 4090';x=torch.arange(1024,device='cuda:0',dtype=torch.float32);y=x*.5+1;torch.cuda.synchronize();assert torch.isfinite(y).all() and float(y.sum())==262912.0
  put('CLONED_TORCH_CUDA_TENSOR_EXECUTION_ACTUAL.json',dict(passed=True,epoch=time.time(),GPU_UUID_binding=GPU,visible_cuda_devices=1,device_name=torch.cuda.get_device_name(0),torch_version=torch.__version__,CUDA_build=torch.version.cuda,total_device_memory=torch.cuda.get_device_properties(0).total_memory,actual_tensor_device=str(y.device),actual_tensor_elements=y.numel(),simple_checksum=float(y.sum()),no_policy_model_SDK_scene_or_optimizer_loaded=True,not_model_or_training_readiness=True));return
 app=None
 try:
  from zonglin2_app_launcher import Zonglin2AppLauncher
  parser=argparse.ArgumentParser();Zonglin2AppLauncher.add_app_launcher_args(parser);args=parser.parse_args(['--headless','--device','cuda:0']);launcher=Zonglin2AppLauncher(args);app=launcher.app
  import torch,isaaclab.sim as sim_utils
  from isaaclab_physx.physics import PhysxCfg
  from isaaclab.assets import RigidObject,RigidObjectCfg
  cfg=sim_utils.SimulationCfg(dt=.0025,device='cuda:0',render_interval=1);cfg.physics=PhysxCfg(solver_type=1,min_position_iteration_count=32,max_position_iteration_count=32,min_velocity_iteration_count=4,max_velocity_iteration_count=4)
  sim=sim_utils.SimulationContext(cfg);ground=sim_utils.CuboidCfg(size=(2.,2.,.1),collision_props=sim_utils.CollisionPropertiesCfg());ground.func('/World/OwnProbeGround',ground,translation=(0.,0.,-.05))
  bodycfg=RigidObjectCfg(prim_path='/World/OwnProbeCube',spawn=sim_utils.CuboidCfg(size=(.1,.1,.1),rigid_props=sim_utils.RigidBodyPropertiesCfg(),collision_props=sim_utils.CollisionPropertiesCfg(),mass_props=sim_utils.MassPropertiesCfg(mass=1.)),init_state=RigidObjectCfg.InitialStateCfg(pos=(0.,0.,.5)));body=RigidObject(bodycfg);sim.reset();body.update(.0025);start=tensor(body.data.root_pos_w).detach().clone();calls=0
  for _ in range(24):sim.step(render=False);body.update(.0025);calls+=1
  end=tensor(body.data.root_pos_w).detach().clone();assert calls==24 and torch.isfinite(end).all() and bool((end[:,2]<start[:,2]).all());torch.cuda.synchronize()
  put('CLONED_SDK_SIMPLE_NATIVE_CUDA_SCENE_24_PHYSICS_STEPS_ACTUAL.json',dict(passed=True,epoch=time.time(),GPU_UUID_binding=GPU,actual_isaaclab_module_path=sim_utils.__file__,physics_dt_s=.0025,physics_step_calls=calls,simulated_seconds=.06,TGS_solver_type=cfg.physics.solver_type,position_iterations=[cfg.physics.min_position_iteration_count,cfg.physics.max_position_iteration_count],velocity_iterations=[cfg.physics.min_velocity_iteration_count,cfg.physics.max_velocity_iteration_count],cube_initial_xyz=start.cpu().tolist(),cube_final_xyz=end.cpu().tolist(),actual_cube_state_device=str(end.device),no_robot_asset_model_policy_resetbank_or_optimizer=True,not_MOD4_native24_controls_or_fullstate_restore=True,not_skill_or_training_readiness=True))
 except BaseException:put('CLONED_SCENE_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),exception_type=type(sys.exc_info()[1]).__name__,traceback=traceback.format_exc()));raise
 finally:
  if app:put('CLONED_SCENE_APP_CLOSING.json',dict(epoch=time.time()));app.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('CLONED_PROBE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_model_source_promotion=True));raise
