"""Model-free ROOT target admission/case parent. Original children waited, no signals."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,psutil,shutil,subprocess,sys,time,traceback
from contract_latest32 import CANONICAL,validate_task,validate_authority
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def audit_current(binding):
 raw=Path(CANONICAL).read_bytes();c=json.loads(raw);o=binding['owner'];O=Path(o['root'])
 identity=read(O/'OWNER_IDENTITY.json');current=read(O/'OWNER_CURRENT.json');fact=dict(running=False)
 try:
  q=psutil.Process(o['pid'])
  if q.create_time()==o['creation'] and q.status()!=psutil.STATUS_ZOMBIE:
   fact=dict(running=True,pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd())
 except psutil.NoSuchProcess:pass
 closed=None
 if c['active_segment'] is None:closed=dict(cohort_final=read(O/'COHORT_FINAL.json'),owner_exit=read(O/'OWNER_EXIT_ACTUAL.json'))
 mode=validate_authority(c,binding,identity,current,fact,closed)
 return dict(epoch=time.time(),passed=True,scope=mode,canonical_SHA=hashlib.sha256(raw).hexdigest(),actual_canonical_active=c['active_segment'],
  actual_owner_identity=identity,actual_owner_current_GO=current['go'],exact_original_process_fact=fact,original_closed_proof=closed,account_writes=0)
def main():
 p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent
 task=read(a.task);validate_task(task);package=read(P/'PACKAGE_LATEST32_SOURCE_AND_TASK.json')
 for r in package['files']:
  f=P/r['relative'];assert f.resolve().is_relative_to(P) and f.suffix in ('.py','.json');b=f.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA']
 locks=[];child=None;wait=None;error=None;result=None;rc=None;admission=None
 try:
  private=Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+task['GPU_UUID']+'.lock')
  shared=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')
  for path in (private,shared):
   f=path.open('rb+')
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BaseException:f.close();raise
   locks.append(f)
  authority=audit_current(task['current_authority_binding'])
  assert authority['scope']['active_GPU_UUID']!=task['GPU_UUID']
  line=subprocess.check_output(['nvidia-smi','-i',task['GPU_UUID'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
  fields=[x.strip() for x in line.split(',')];ram=psutil.virtual_memory().available;disk=shutil.disk_usage(P).free
  assert fields[0]==task['GPU_UUID'] and fields[1]=='NVIDIA GeForce RTX 4090' and int(fields[2])>15669 and int(fields[3])<=30 and ram>32*1024**3 and disk>25*1024**3
  admission=dict(epoch=time.time(),passed=True,authority=authority,GPU_line=line,RAM_available=ram,disk_free=disk,
   selected_private_EX=True,original_finite_validation_EX=True,nonempty_compute_UUID_allowed=True,account_writes=0,GO=False)
  put(P/'ACTUAL_LATEST32_AUTHORITY_RESOURCE_ADMISSION.json',admission)
  admitted=dict(task,actual_current_authority_private_shared_resources_admitted=True,original_eval_parent_holds_private_and_validation_EX=True,
   admission_SHA=hashlib.sha256((P/'ACTUAL_LATEST32_AUTHORITY_RESOURCE_ADMISSION.json').read_bytes()).hexdigest())
  validate_task(admitted,True);actual_task=P/'TASK_LATEST32_ADMITTED_ACTUAL.json';put(actual_task,admitted)
  put(P/'PARENT_LATEST32_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=task['purpose_id'],model_SHA=task['model_SHA'],
   selected_model_byte_decode_max=[1,1],old_model_reads=0,optimizer_steps=0,account_writes=0,new_GO=False,worker_seconds=3600,parent_seconds=3780))
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
  for k,leaf in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
   f=P/'private'/leaf;f.mkdir(parents=True,exist_ok=True);env[k]=str(f)
  args=[task['sdk_python'],'-u','-B',str(P/'evaluate_latest32481_full32s_ROOT_ONLY_once.py'),'--task',str(actual_task)]
  with (P/'ACTUAL_LATEST32_STDOUT_STDERR.log').open('xb') as log:
   child=subprocess.Popen(args,cwd=P,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,close_fds=True)
   q=psutil.Process(child.pid);identity=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd());put(P/'ACTUAL_LATEST32_CHILD_IDENTITY_BEFORE_WAIT.json',identity)
   rc=child.wait(timeout=3780);wait=dict(epoch=time.time(),returncode=rc,original_waited=True,identity=identity)
  put(P/'ACTUAL_LATEST32_ORIGINAL_WAIT.json',wait)
  out=P/'actual_latest32';result=read(out/'ACTUAL227_CLOSED_RM70_SKILL_FACTS.json')
  counts=read(out/'SOURCE227_FINAL_READ_COUNTS.json');assert counts['source_SHA']==task['model_SHA'] and counts['source_physical_byte_opens']==counts['source_decodes']==1
  errors=[str(x) for x in out.glob('*ERROR*.json')];text=(P/'ACTUAL_LATEST32_STDOUT_STDERR.log').read_text(encoding='utf8',errors='replace')
  material=[x for x in text.splitlines() if 'PxPhysics::createMaterial' in x and '64K' in x]
  assert rc==0 and result['passed_execution'] and not errors and not material and read(out/'APP227_CLOSING.json')
 except BaseException:
  error=traceback.format_exc();put(P/'ACTUAL_LATEST32_ORIGINAL_PARENT_ERROR.json',dict(epoch=time.time(),error=error,no_automatic_retry=True))
 finally:
  if child is not None:
   rc=child.wait()
   if wait is None:
    wait=dict(epoch=time.time(),returncode=rc,original_waited=True,after_original_parent_error=True);put(P/'ACTUAL_LATEST32_FINAL_ORIGINAL_WAIT.json',wait)
  acquired=len(locks)==2
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(P/'ACTUAL_LATEST32_ALL_WAITED_EX_RELEASED.json',dict(epoch=time.time(),all_own_children_waited=child is None or child.poll() is not None,private_and_validation_EX_acquired=acquired,all_owned_locks_released=True,private_and_validation_EX_released=acquired,wait=wait))
 facts={} if not result else result.get('facts',{});producer=facts.get('producer',{})
 returned=dict(epoch=time.time(),passed_execution=error is None and bool(result and result['passed_execution']),original_parent_error=error,result=result,wait=wait,
  complete32s=bool(result and result.get('bounded_window_complete')),telemetry_complete=bool(result and result.get('bounded_window_complete') and not producer.get('dropped_rows',0) and not facts.get('diagnostic_errors')),
  full_expert_skill='UNKNOWN',app_close_by_original_source_and_wait_not_postclose_marker=True,account_writes=0,new_GO=False,model_artifact_transfers=0,GUI=False)
 put(P/'ACTUAL_LATEST32_ORIGINAL_PARENT_RETURNED.json',returned);print(json.dumps(returned,allow_nan=False))
if __name__=='__main__':main()

