"""Single finite, uncharged GPU1 pose admission alongside known own GPU0 learner."""
from pathlib import Path
import os,sys,json,time,subprocess,traceback,fcntl,hashlib
B=Path(__file__).resolve().parent;ROOT=Path('/home/lc01/Zonglin Li/zonglin2');PY=ROOT/'run-python.sh';GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
def put(p,v):
 p=Path(p);q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def ident(pid):
 import psutil
 p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
def lock_owners(st,raw):
 owners=[]
 for line in raw.splitlines():
  bits=line.split()
  if len(bits)<6 or '->' in bits:continue
  try:dev=bits[5].split(':');matched=int(dev[0],16)==os.major(st.st_dev) and int(dev[1],16)==os.minor(st.st_dev) and int(dev[2])==st.st_ino
  except (ValueError,IndexError):continue
  if matched:owners.append(int(bits[4]))
 return owners
def main():
 import psutil,shutil
 assert B.resolve().is_relative_to(ROOT.resolve());put(B/'PARENT_IDENTITY.json',ident(os.getpid()));locks=[];child=None
 try:
  mine=(ROOT/'state/e3_gpu1_legal_fall_validation.lock').open('a+b');fcntl.flock(mine,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(mine)
  globalfile=(ROOT/'state/finite_environment_validation.lock').open('rb+')
  try:fcntl.flock(globalfile,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(globalfile);sharing=dict(original_global_lock_acquired=True)
  except BlockingIOError:
   raw=Path('/proc/locks').read_text();owners=lock_owners(os.fstat(globalfile.fileno()),raw);assert owners==[3119751],owners;p=ident(owners[0]);E=ROOT/'tasks/MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016/e2';assert abs(p['creation']-1792143911.61)<.1 and str(E/'cohort_finite.py') in p['argv'];manifest=E/'CONTINUATION_COMPLETE_MANIFEST_V2.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='3354a1404027470c7bfa16fd779919ad58bb9fdc14f5b295d3a53f0260dc4313';task=json.loads((E/'job0/TASK.json').read_bytes());assert task['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842';sharing=dict(original_global_actual_owner=p,actual_proc_lock_owner_verified=True,known_owned_GPU0_cohort_manifest_SHA=hashlib.sha256(manifest.read_bytes()).hexdigest(),distinct_GPU1_explicit_zeroPPO_co_scheduling=True);globalfile.close()
  query=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in query.splitlines() if GPU in x);compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(GPU in x for x in compute.splitlines());assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>4*1024**3 and shutil.disk_usage(B).free>5*1024**3;put(B/'OWN_GPU1_ACTUAL_LOCK_RESOURCE_AND_COSCHEDULING.json',dict(epoch=time.time(),GPU_line=line,compute_snapshot=compute,RAM_available=psutil.virtual_memory().available,sharing=sharing,no_canonical_or_learning_authority=True))
  e=dict(os.environ)
  for k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):e.pop(k,None)
  for n in ('home','tmp','cache','config','data'):(B/n).mkdir()
  e.update(CUDA_VISIBLE_DEVICES=GPU,PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(B/'home'),TMPDIR=str(B/'tmp'),XDG_CACHE_HOME=str(B/'cache'),XDG_CONFIG_HOME=str(B/'config'),XDG_DATA_HOME=str(B/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');child=subprocess.Popen([str(PY),'-u','-B',str(B/'e3_legal_pose_contact_native80_v1.py')],cwd=B,env=e,stdout=(B/'worker.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(B/'WORKER_STARTED_ACTUAL.json',ident(child.pid));rc=child.wait();put(B/'WORKER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=child.pid,returncode=rc,actual_waited=True));good=rc==0 and (B/'output/COMPLETE_ACTUAL.json').exists() and not list((B/'output').glob('*ORIGINAL_ERROR*.json'));put(B/'PARENT_FINAL.json',dict(epoch=time.time(),passed=good,actual_child_waited=True,no_PPO_or_canonical_charge=True))
 finally:
  if child:child.wait()
  for f in locks:fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),own_child_actual_out=True,own_locks_released=True,no_other_process_or_old_global_lock_changed=True))
if __name__=='__main__':
 assert not (B/'PARENT_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),finite_no_PPO=True)),flush=True)
 else:
  os.setsid();f=os.open(str(B/'parent.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
  try:main()
  except BaseException:put(B/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True));raise
