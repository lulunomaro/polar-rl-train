"""ROOT-only host72 single model-free-parent admission and one N1 evaluation.



Read current original authority. Never create GO/writer or alter its account.

Original child must be waited OUT before private/shared EX are released.

"""

from pathlib import Path

import argparse,fcntl,hashlib,json,os,psutil,shutil,subprocess,sys,time,traceback

N=Path(__file__).resolve().parent;sys.path.insert(0,str(N))

from contract272 import validate_task,validate_current_authority

CANONICAL=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')





def read(p):return json.loads(Path(p).read_bytes())

def put(p,v):

 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)





def main():

 p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args()

 P=a.task.resolve().parent;task=read(a.task);validate_task(task)

 assert not (P/'PARENT272_ONCE_CONSUMED.json').exists() and not (P/'actual_capture').exists()

 package=read(P/'PACKAGE272_SOURCE_AND_TASK.json')

 for r in package['files']:

  q=P/r['relative'];assert q.resolve().is_relative_to(P) and q.suffix in ('.py','.json')

  b=q.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA']

 locks=[];child=None;parent_error=None;wait=None;result=None;rc=None

 try:

  private=Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+task['GPU_UUID']+'.lock')

  shared=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')

  for path in (private,shared):

   f=path.open('rb+')

   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)

   except BaseException:f.close();raise

   locks.append(f)

  c_raw=CANONICAL.read_bytes();c=json.loads(c_raw);binding=task['current_authority_binding'];identity=current=None

  if binding['kind']=='EXACT_ORIGINAL219_OWNER_GO':

   O=Path(binding['owner']['root']);identity=read(O/'OWNER_IDENTITY.json');current=read(O/'OWNER_CURRENT.json')

   q=psutil.Process(identity['pid']);assert q.create_time()==identity['creation'] and q.status()!=psutil.STATUS_ZOMBIE

  validate_current_authority(c,binding,identity,current)

  line=subprocess.check_output(['nvidia-smi','-i',task['GPU_UUID'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()

  fields=[x.strip() for x in line.split(',')];ram=psutil.virtual_memory().available;disk=shutil.disk_usage(P).free

  assert fields[0]==task['GPU_UUID'] and fields[1]=='NVIDIA GeForce RTX 4090' and int(fields[2])>15669 and int(fields[3])<=30

  assert ram>32*1024**3 and disk>25*1024**3

  admission=dict(epoch=time.time(),passed=True,authority_binding=binding,

   canonical_SHA=hashlib.sha256(c_raw).hexdigest(),actual_canonical_active=c['active_segment'],

   actual_owner_identity=identity,actual_current_GO=None if current is None else current['go'],

   GPU_line=line,RAM_available=ram,disk_free=disk,selected_private_EX=True,original_shared_EX=True,

   nonempty_compute_UUID_allowed=True,unrelated_GPU_PID_scan=False,account_writes=0)

  put(P/'ACTUAL272_CURRENT_AUTHORITY_AND_N1_RESOURCE_ADMISSION.json',admission)

  admitted=dict(task,actual_parent_private_EX_and_authority_admitted=True,actual_resource_admission_SHA=hashlib.sha256((P/'ACTUAL272_CURRENT_AUTHORITY_AND_N1_RESOURCE_ADMISSION.json').read_bytes()).hexdigest())

  actual_task=P/'TASK272_ADMITTED_ACTUAL.json';put(actual_task,admitted)

  put(P/'PARENT272_ONCE_CONSUMED.json',dict(epoch=time.time(),model_SHA=task['model_SHA'],

   model_byte_reads_by_worker_max=1,model_decodes_max=1,old_source_model_reads=0,

   controls_max=64,physics_max=512,NN_actor_only=False,optimizer_steps=0,account_writes=0,

   geometry_queries_max=0,artifact_transfers=0,GUI=False))

  env=dict(os.environ,CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',

   PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')

  for key in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(key,None)

  for key,leaf in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config',

   'XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch',

   'CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():

   q=P/'private'/leaf;q.mkdir(parents=True,exist_ok=True);env[key]=str(q)

  args=[task['sdk_python'],'-u','-B',str(P/'evaluate272_front_depth_zero_PT_UNUSED_once.py'),'--task',str(actual_task)]

  with (P/'ACTUAL272_STDOUT_STDERR.log').open('xb') as log:

   child=subprocess.Popen(args,cwd=P,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,close_fds=True)

   q=psutil.Process(child.pid);worker=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd())

   put(P/'ACTUAL272_WORKER_IDENTITY_BEFORE_WAIT.json',worker)

   rc=child.wait(timeout=900);wait=dict(epoch=time.time(),returncode=rc,original_waited=True,identity=worker)

  put(P/'ACTUAL272_WAITED_EXIT.json',wait)

  out=P/'actual_capture';r=out/'CAPTURE272_ACTUAL_RESULT.json';result=read(r) if r.is_file() else None

  errors=[str(p) for p in out.glob('*ERROR*.json')] if out.is_dir() else []

  assert rc==0 and result and result['passed'] and not errors and read(out/'ENV272_CLOSE_RETURNED.json')['closed'] and read(out/'APP272_CLOSE_REQUESTED.json')['close_call_next']

 except BaseException:

  parent_error=traceback.format_exc();put(P/'ACTUAL272_ORIGINAL_PARENT_ERROR.json',dict(epoch=time.time(),error=parent_error,no_automatic_retry=True))

 finally:

  #A timeout never makes a still-running SDK child FREE. Root keeps its lease

  #and any necessary exact-process handling;no signal or forced kill here.

  if child is not None:

   rc=child.wait()

   if wait is None:

    wait=dict(epoch=time.time(),returncode=rc,original_waited=True,after_parent_original_error=True)

    put(P/'ACTUAL272_FINAL_ORIGINAL_WAIT.json',wait)

  acquired_both=len(locks)==2

  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()

  put(P/'ACTUAL272_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json',dict(epoch=time.time(),

   all_own_children_waited=child is None or child.poll() is not None,

   private_shared_EX_acquired=acquired_both,all_owned_locks_released=True,

   private_shared_EX_released=acquired_both,wait=wait))

 returned=dict(epoch=time.time(),passed_execution=parent_error is None and bool(result and result['passed']),app_close_returned_marker_optional=True,

  parent_error=parent_error,result=result,wait=wait,account_writes=0,model_artifact_transfers=0,GUI=False)

 put(P/'ACTUAL272_ORIGINAL_PARENT_RETURNED.json',returned)

 print(json.dumps(returned,allow_nan=False))





if __name__=='__main__':main()

