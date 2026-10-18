"""Human-authorized Linux GPU1 evaluation, isolated from GPU0 paid training."""
from pathlib import Path
import sys,json,time,os,argparse,hashlib,traceback,fcntl,subprocess,shutil,psutil,importlib.metadata as metadata
B=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();p=argparse.ArgumentParser();p.add_argument('--lease',required=True);p.add_argument('--output',required=True);args=p.parse_args();lease=json.loads(Path(args.lease).read_bytes());O=Path(args.output);m=json.loads((B/'H1_CR3_FINAL_LINUX4090_MANIFEST_V1.json').read_bytes());case=lease['case_parameters']
from h1_linux_eval_contract_v1 import validate,GPU
validate(lease,m,case);assert lease['worker_sha256']==H(__file__) and lease['source_manifest_sha256']==H(B/'H1_CR3_FINAL_LINUX4090_MANIFEST_V1.json')
assert H(B/m['source_relative'])==lease['checkpoint_sha256'] and os.environ['CUDA_VISIBLE_DEVICES']==GPU and not O.exists()
for row in m['files']:
 q=B/row['relative'];assert q.resolve().is_relative_to(B.resolve()) and q.stat().st_size==row['bytes'] and H(q)==row['SHA'],row['relative']
sdk=json.loads((B/'EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json').read_bytes());assert H(B/'EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json')==lease['actual_Linux_backend_SHA']
for n,v in sdk['versions'].items():assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['SHA']
assert sdk['files'] and sdk['native_binding']['SHA'] and H(sdk['native_binding']['path'])==sdk['native_binding']['SHA']
owned=Path('/home/lc01/Zonglin Li/zonglin2');lockpath=owned/'state'/('three_expert_v2_'+GPU+'.lock');lock=lockpath.open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(GPU in x for x in compute.splitlines()),compute
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if GPU in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
O.mkdir(parents=True)
def save(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
save('STARTED.json',dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,case=case,GPU_UUID=GPU,actual_private_fcntl_path=str(lockpath),global_validation_only_briefly_checked_not_held=True,compute_snapshot=compute,actual_Linux_backend=sdk,no_PPO=True,other_GPU_training_not_signalled=True))
for k,v in m['env'].items():os.environ[k]=str(v)
L=B/'frozen_shared/runtime';C=L/'isaac/mod4';os.environ.update(RM_MOD4_USD=str(L/'assets/robot.usd'),RM_MILD_DR_PROFILE='white_v3');sys.path[:0]=[str(B),str(C),str(L),str(B/'frozen_shared')];app=None;context={};failure=None
try:
 import torch,numpy as np,tensordict
 torch.set_num_threads(1)
 from h1_cr3_finite_final_source_guard_v1 import validate_H1_source
 source=torch.load(B/m['source_relative'],map_location='cpu',weights_only=False);validate_H1_source(source);assert not torch.cuda.is_initialized();del source
 from zonglin2_app_launcher import Zonglin2AppLauncher
 app=Zonglin2AppLauncher(headless=True,device='cuda:0').app
 from h1_frozen_witness_v1 import CONTEXT
 context=CONTEXT;context.update(save=save,output_dir=str(O),router_mode='single_eval');a=argparse.Namespace(**case);a.checkpoint=str(B/m['source_relative']);a.checkpoint_sha=m['source']['SHA'];a.case_id=lease['case_id'];a.shared_payload=str(B/'frozen_shared');a.dr_profile='white_v3';a.speed_limit=1.5;a.ramp_suite=False;a.reset_smoke=False;a.max_rate=4.;a.contact_readback=True;a.manual_reference=False;a.output=str(O/'probe.json')
 from h1_frozen_jump_loop_v1 import run_jump
 run_jump(a);app.close();app=None;save('EXIT_NATURAL.json',dict(epoch=time.time(),pid=os.getpid(),exit_code=0,no_PPO=True))
except BaseException:
 failure=traceback.format_exc();save('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=failure,no_PPO=True,no_qualification_claim=True))
 try:
  from e2_frozen_prefix_guard_v4 import save_failed_prefix
  save_failed_prefix(context,O,save)
 except BaseException:save('FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_failure_preserved=True))
finally:
 if app is not None:
  try:app.close()
  except BaseException:save('APP_CLOSE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()))
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if failure:raise RuntimeError('Original frozen evaluation error saved before SDK close')
