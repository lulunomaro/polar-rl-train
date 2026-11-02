"""Finite no-optimizer W35/MOD4v1 evaluation parent; never writes the canonical."""
from pathlib import Path
import json,os,sys,time,hashlib,fcntl,subprocess,traceback,shutil
B=Path(__file__).resolve().parent;BASE=Path('/home/lc01/Zonglin Li/zonglin2')
def put(name,v):
 p=B/name;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2,allow_nan=False));q.replace(p)
def main():
 assert not(B/'PARENT_STARTED.json').exists();task=json.loads((B/'TASK_PENDING.json').read_bytes());put('PARENT_STARTED.json',{'pid':os.getpid(),'epoch':time.time(),'purpose':task['kind'],'canonical_writes':0})
 locks=[];p=None;rows={};err=None
 try:
  for row in json.loads((B/'PACKAGE.json').read_bytes())['files']:
   f=B/row['relative'];assert f.stat().st_size==row['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==row['SHA']
  for path in (BASE/'state'/('three_expert_v2_'+task['GPU_UUID']+'.lock'),BASE/'state/finite_environment_validation.lock'):
   f=path.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  import psutil
  raw=(BASE/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes();c=json.loads(raw)
  assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
  active=c['active_segment'];fact=None
  if active is not None:
   owner=psutil.Process(active['owner_parent_pid']);assert owner.is_running() and owner.status()!=psutil.STATUS_ZOMBIE;fact={'pid':owner.pid,'creation':owner.create_time(),'kind':active['kind']}
  gpu=subprocess.check_output(['/usr/bin/nvidia-smi','-i',task['GPU_UUID'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[v.strip() for v in gpu.split(',')]
  apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
  assert task['GPU_UUID'] not in apps and a[0]==task['GPU_UUID'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(B).free>25*1024**3
  admission={'passed':True,'epoch':time.time(),'canonical_SHA':hashlib.sha256(raw).hexdigest(),'canonical_current_owner':fact,'canonical_generation':c['authority_generation'],'canonical_writes':0,'new_GO':False,'GPU_line':gpu,'private_EX':True,'finite_validation_EX':True,'selected_GPU_empty':True,'source_model_opens_parent':0}
  put('ACTUAL_EVAL_ADMISSION.json',admission);task.update(actual_current_authority_private_shared_resources_admitted=True,original_eval_parent_holds_private_and_validation_EX=True);put('TASK_ADMITTED.json',task)
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
  for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
   d=B/'private'/rel;d.mkdir(parents=True,exist_ok=True);env[key]=str(d)
  log=(B/'FULL_EVAL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([str(BASE/'run-python.sh'),'-u','-B',str(B/'evaluate_mod4v1_w35.py'),'--task',str(B/'TASK_ADMITTED.json')],cwd=B,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=tuple(f.fileno() for f in locks),start_new_session=True);log.close();q=psutil.Process(p.pid);put('WORKER_IDENTITY.json',{'pid':q.pid,'creation':q.create_time(),'root':str(B)})
  rc=p.wait(timeout=3780);put('ACTUAL_ORIGINAL_WAIT.json',{'returncode':rc,'waited':True})
  out=B/'actual_latest32'
  for name in ('ACTUAL227_CLOSED_RM70_SKILL_FACTS.json','SOURCE227_FINAL_READ_COUNTS.json','MOD4V1_FULLRESTORE_GUARD_ACTUAL.json'):
   f=out/name
   if f.exists():rows[name]=json.loads(f.read_bytes())
  errors=[str(f) for f in out.glob('*ERROR*.json')];facts=rows.get('ACTUAL227_CLOSED_RM70_SKILL_FACTS.json')
  counts=rows.get('SOURCE227_FINAL_READ_COUNTS.json',{})
  passed=bool(rc==0 and facts and facts['passed_execution'] and not errors and (out/'APP227_CLOSING.json').exists() and counts.get('source_physical_byte_opens')==1 and counts.get('source_decodes')==1)
  put('FINAL.json',{'passed_execution':passed,'rows':rows,'errors':errors,'returncode':rc,'canonical_writes':0,'optimizer_updates':0,'bounded32s_complete':bool(facts and facts.get('bounded_window_complete')),'expert_skill_graduation':'UNKNOWN_UNTIL_FACTS_REVIEW','epoch':time.time()})
 except BaseException:
  err=traceback.format_exc();put('PARENT_ORIGINAL_ERROR.json',{'error':err,'new_GO':False,'canonical_writes':0})
 finally:
  if p is not None and p.poll() is None:
   p.terminate()
   try:p.wait(timeout=30)
   except subprocess.TimeoutExpired:pass
  waited=p is None or p.poll() is not None
  if waited:
   for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN)
  for f in locks:f.close()
  put('PARENT_EXIT_SCOPE.json',{'all_own_children_waited':waited,'owned_private_validation_locks_released':waited,'error':err,'canonical_writes':0})
if __name__=='__main__':main()
