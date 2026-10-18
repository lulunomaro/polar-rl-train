"""First Linux backend E2/E3 frozen observations with actual loaded reward/frame readouts."""
from pathlib import Path
import os,sys,json,time,argparse,hashlib,fcntl,subprocess,shutil,traceback,importlib.metadata
B=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);args=parser.parse_args();config=json.loads(Path(args.config).read_bytes());manifest=json.loads((B/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json').read_bytes());kind=config['expert'];assert kind==manifest['expert'] and config['steps']==120 and config['no_PPO'] and config['source_SHA']==manifest['source_SHA'] and config['worker_SHA']==H(__file__)
assert os.environ['CUDA_VISIBLE_DEVICES']==config['GPU_UUID'];O=B/'native120_observation';assert not O.exists()
for row in manifest['files']:
 p=B/row['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==row['bytes'] and H(p)==row['SHA'],row['relative']
private=Path(config['actual_existing_private_lock']);assert private.is_file();lock=private.open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
if config['host']=='72':
 shared=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')
 with shared.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(config['GPU_UUID'] in line for line in compute.splitlines()),compute
gpu=next(s for s in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if config['GPU_UUID'] in s);assert int(gpu.split(',')[-1])>7000 and shutil.disk_usage(B).free>25*1024**3
import psutil
assert psutil.virtual_memory().available>8*1024**3;O.mkdir()
def save(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,source_SHA=manifest['source_SHA'],GPU=config['GPU_UUID'],purpose='new Linux backend actual loaded reward/frame/legacy observation, not repeat Windows case or new paid learning',private_lock=str(private),other_GPU_compute_preserved=compute,no_PPO=True))
for k,v in manifest['env'].items():os.environ[k]=str(v)
L=B/'frozen_shared/runtime';C=L/'isaac/mod4';os.environ.update(RM_MOD4_USD=str(L/'assets/robot.usd'),RM_MILD_DR_PROFILE='white_v3',RM_SPIN_MAX_RAD_S='4.0',RM_SPIN_WORLD_PROGRESS_M_S='0.5',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES');sys.path[:0]=[str(B),str(C),str(L),str(B/'frozen_shared')];app=None;context={};failure=None
try:
 import torch,numpy as np,tensordict
 torch.set_num_threads(1);source=torch.load(B/manifest['source_relative'],map_location='cpu',weights_only=False)
 if kind=='E3':
  from recovery_closed85_source_guard_v1 import validate_E3_source as validate
 else:
  from e2_closed112_source_guard_CPU_v1 import validate_E2_source as validate
 validate(source);assert not torch.cuda.is_initialized();del source
 versions={}
 for name in ('torch','isaaclab','isaaclab_rl','rsl-rl','tensordict'):
  try:versions[name]=importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError:versions[name]=None
 if config['host']=='72':
  from zonglin2_app_launcher import Zonglin2AppLauncher
  app=Zonglin2AppLauncher(headless=True,device='cuda:0').app
 else:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cuda:0').app
 loaded=[]
 for line in Path('/proc/self/maps').read_text().splitlines():
  path=line.split()[-1]
  if path.startswith('/') and any(x in path.lower() for x in ('physx','physics.tensors')) and Path(path).is_file() and path not in {r['path'] for r in loaded}:loaded.append(dict(path=path,bytes=Path(path).stat().st_size,SHA=H(path)))
 save('ACTUAL_LINUX_INSTALLED_BACKEND_AND_LOADED_PHYSX_READBACK.json',dict(epoch=time.time(),host=config['host'],versions=versions,actual_loaded_PhysX=loaded,Windows_DLL_or_MSVCRT_not_reused=True,no_installed_SDK_edit=True))
 import importlib
 witness=importlib.import_module('e3_native_witness_v1' if kind=='E3' else 'retention_native_witness_v8');context=witness.CONTEXT;context.update(save=save,output_dir=str(O),router_mode='single_eval')
 from actual_reward_frame_observer_v1 import install
 install(witness,context)
 a=argparse.Namespace(router_mode='single_eval',kind='recovery' if kind=='E3' else 'world',steps=120,num_envs=104 if kind=='E3' else 88,seed=20260928,headless=True,device='cuda:0',checkpoint=str(B/manifest['source_relative']),checkpoint_sha=manifest['source_SHA'],case_id=config['case_id'],shared_payload=str(B/'frozen_shared'),dr_profile='white_v3',speed_limit=1.5,ramp_suite=False,reset_smoke=False,max_rate=4.,contact_readback=True,manual_reference=False,output=str(O/'probe.json'))
 if kind=='E3':
  from e3_frozen_recovery_loop_v1 import run_recovery
  run_recovery(a)
 else:
  from retention_world_native_v8 import run_world
  run_world(a)
 save('OBSERVATION_LOOP_RETURNED.json',dict(epoch=time.time(),controls=120,physical_callbacks=480,source_SHA=manifest['source_SHA'],not_paid_training_or_skill_pass=True));app.close();app=None;save('EXIT_NATURAL.json',dict(epoch=time.time(),returncode=0,no_PPO=True))
except BaseException:
 failure=traceback.format_exc();save('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=failure,no_PPO=True,no_qualification_claim=True))
 try:
  from e2_frozen_prefix_guard_v4 import save_failed_prefix
  save_failed_prefix(context,O,save)
 except BaseException:save('FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()))
finally:
 if app is not None:
  try:app.close()
  except BaseException:save('APP_CLOSE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()))
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if failure:raise RuntimeError('Original Linux diagnostic failure preserved')
