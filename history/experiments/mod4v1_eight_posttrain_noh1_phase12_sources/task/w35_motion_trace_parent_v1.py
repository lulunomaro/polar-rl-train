"""Finite no-PPO motion-wiring diagnostic. OwnGPU0privateEX+originalfiniteSH, no ledger access."""
from pathlib import Path
import os,json,time,hashlib,fcntl,subprocess,psutil,traceback,shutil
B=Path(__file__).resolve().parent;BASE=Path('/home/lc01/Zonglin Li/zonglin2')
def put(name,v):
 p=B/name;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 assert not(B/'PARENT_STARTED.json').exists();task=json.loads((B/'TASK_PENDING.json').read_bytes());put('PARENT_STARTED.json',dict(pid=os.getpid(),epoch=time.time(),purpose=task['kind'],canonical_reads=0,canonical_writes=0));locks=[];p=None;err=None;tracked={};remaining=[]
 try:
  for row in json.loads((B/'PACKAGE.json').read_bytes())['files']:
   f=B/row['relative'];assert f.stat().st_size==row['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==row['SHA']
  for path,mode in ((BASE/'state'/('three_expert_v2_'+task['GPU_UUID']+'.lock'),fcntl.LOCK_EX),(BASE/'state/finite_environment_validation.lock',fcntl.LOCK_SH)):
   f=path.open('rb+');locks.append(f);fcntl.flock(f,mode|fcntl.LOCK_NB)
  gpu=subprocess.check_output(['/usr/bin/nvidia-smi','-i',task['GPU_UUID'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);a=[x.strip()for x in gpu.split(',')]
  assert task['GPU_UUID']not in apps and a[0]==task['GPU_UUID'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(B).free>25*1024**3
  task.update(actual_current_authority_private_shared_resources_admitted=True,actual_parent_privateEX_finiteSH=True);put('TASK_ADMITTED.json',task);put('ACTUAL_TRACE_ADMISSION.json',dict(passed=True,private_EX=True,finite_validation_SH=True,GPU_line=gpu,selected_GPU_empty=True,source_model_opens_parent=0,canonical_reads=0,canonical_writes=0,new_training_GO=False))
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for k in('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
  for key,rel in{'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
   q=B/'private'/rel;q.mkdir(parents=True,exist_ok=True);env[key]=str(q)
  log=(B/'MOTION_TRACE_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([str(BASE/'run-python.sh'),'-u','-B',str(B/'evaluate_mod4v1_w35.py'),'--task',str(B/'TASK_ADMITTED.json')],cwd=B,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=tuple(f.fileno()for f in locks),start_new_session=True);log.close();proc=psutil.Process(p.pid);tracked[p.pid]=proc.create_time();put('WORKER_IDENTITY.json',dict(pid=p.pid,creation=tracked[p.pid],root=str(B)));deadline=time.monotonic()+1200
  while p.poll()is None:
   try:
    for q in proc.children(recursive=True):tracked[q.pid]=q.create_time()
   except psutil.NoSuchProcess:pass
   if time.monotonic()>deadline:raise TimeoutError('Own traceparent1200s cap reached, nolearningorforeignprocess touched')
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:pass
  rc=p.wait();put('ACTUAL_ORIGINAL_WAIT.json',dict(returncode=rc,waited=True));out=B/'actual_latest32';f=out/'ACTUAL227_CLOSED_RM70_SKILL_FACTS.json';facts=json.loads(f.read_bytes())if f.exists()else None;t=out/'MOTION_COMMAND_OBS_ACTION_ACTUAL_TRACE.json';errors=[str(x)for x in out.glob('*ERROR*.json')];passed=bool(rc==0 and facts and facts['passed_execution'] and facts['controls']==200 and facts['core_and_17Adam_unchanged'] and facts['optimizer_steps']==0 and t.exists()and not errors)
  put('FINAL.json',dict(passed_execution=passed,controls_expected=200,sim_seconds_expected=4,optimizer_updates=0,canonical_reads=0,canonical_writes=0,returncode=rc,errors=errors,facts=facts,trace_path=str(t)if t.exists()else None,not_full32_skill_evaluation=True))
 except BaseException:err=traceback.format_exc();put('PARENT_ORIGINAL_ERROR.json',dict(error=err,canonical_reads=0,canonical_writes=0))
 finally:
  if p is not None and p.poll()is None:
   p.terminate()
   try:p.wait(timeout=30)
   except subprocess.TimeoutExpired:pass
  for pid,created in tracked.items():
   try:
    q=psutil.Process(pid)
    if q.create_time()==created and q.is_running()and q.status()!=psutil.STATUS_ZOMBIE:remaining.append(dict(pid=pid,creation=created))
   except psutil.NoSuchProcess:pass
  waited=(p is None or p.poll()is not None)and not remaining
  for f in reversed(locks):
   if waited:fcntl.flock(f,fcntl.LOCK_UN)
   f.close()
  put('PARENT_EXIT_SCOPE.json',dict(all_own_children_waited=waited,owned_private_validation_locks_released=waited,tracked_own_processes=tracked,remaining_own_processes=remaining,error=err,canonical_reads=0,canonical_writes=0))
if __name__=='__main__':main()
