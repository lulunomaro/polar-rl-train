"""One own native plus CPU qualification, no learning GO or canonical accounting writes."""
from pathlib import Path
import os,sys,json,time,subprocess,hashlib,fcntl,psutil,traceback,shutil
B=Path(__file__).resolve().parent;J=B/'job0';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 p=B/n;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def run(cfg):
 lock=None;p=None;err=None;cpu=None
 try:
  m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());assert H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==cfg['manifest_SHA'] and m['source_SHA']==cfg['source_SHA']
  for row in m['files']:q=B/row['relative'];assert q.resolve().is_relative_to(B.resolve()) and q.stat().st_size==row['bytes'] and H(q)==row['SHA']
  D=Path('/mnt/mod4_linux_durable_20261013');assert D.is_mount() and B.resolve().is_relative_to(D.resolve());lock=Path(cfg['private_lock']).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(cfg['GPU_UUID'] in x for x in compute.splitlines());line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if cfg['GPU_UUID'] in x);assert int(line.split(',')[-1])>7000 and shutil.disk_usage(B).free>25*1024**3 and psutil.virtual_memory().available>8*1024**3
  e=dict(os.environ);e.update(CUDA_VISIBLE_DEVICES=cfg['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for name,part in [('HOME','home'),('TMPDIR','tmp'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:q=J/part;q.mkdir(exist_ok=True);e[name]=str(q)
  args=[cfg['python'],'-B',str(B/'native_admission_worker.py'),'--job','0','--phase','native'];log=(J/'native_WORKER.log').open('xb');p=subprocess.Popen(args,cwd=B,env=e,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);put('NATIVE_ONLY_PARENT_IDENTITY.json',dict(epoch=time.time(),parent_pid=os.getpid(),parent_creation=psutil.Process().create_time(),worker_pid=p.pid,worker_creation=psutil.Process(p.pid).create_time(),argv=args));begin=time.monotonic()
  while p.poll() is None:
   if time.monotonic()-begin>3600 and (J/'native').is_dir() and not (J/'native/STOP_AFTER_SAVE.json').exists():(J/'native/STOP_AFTER_SAVE.json').write_text(json.dumps(dict(epoch=time.time(),reason='Own bounded native save-stop no signal')))
   time.sleep(3)
  rc=p.wait();log.close();assert rc==0 and not list((J/'native').glob('*ORIGINAL_ERROR*.json')) and json.loads((J/'native/FINAL.json').read_bytes())['native_only'];put('NATIVE_ONLY_WORKER_WAITED_EXIT_ACTUAL.json',dict(epoch=time.time(),worker_pid=p.pid,returncode=rc,actual_waited=True))
  e['CUDA_VISIBLE_DEVICES']='';args=[cfg['python'],'-B',str(B/'native_CPU.py'),'--job','0'];log=(J/'native_CPU.log').open('xb');cp=subprocess.Popen(args,cwd=B,env=e,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);rc=cp.wait();log.close();assert rc==0;path=J/'native/NATIVE_ALL_ROWS_CPU_ADMITTED.json';v=json.loads(path.read_bytes());assert v['passed'] and v['source_SHA']==cfg['source_SHA'];cpu=dict(value=v,path=str(path),SHA=H(path),actual_CPU_waited_EXIT0=True);put('NATIVE_ONLY_FINAL_ACTUAL.json',dict(epoch=time.time(),passed_native_GPU_and_full_CPU=True,native_CPU=cpu,actual_GPU_worker_EXIT0=True,no_production_GO_or_PPO_or_canonical_charge=True))
 except BaseException:
  err=traceback.format_exc();put('NATIVE_ONLY_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=err,no_automatic_retry=True))
 finally:
  if p:p.wait()
  if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  put('NATIVE_ONLY_PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),all_actual_own_GPU_children_waited=True,private_GPU_fcntl_released_if_acquired=True,passed_native_CPU=bool(cpu and not err),original_error=bool(err),no_PPO_or_canonical_or_production_GO=True))
 if err:raise RuntimeError('Native error preserved')
if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert not (B/'native_only_CONSOLE.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='native_only')),flush=True)
 else:
  os.setsid();fd=os.open(str(B/'native_only_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);run(cfg)
