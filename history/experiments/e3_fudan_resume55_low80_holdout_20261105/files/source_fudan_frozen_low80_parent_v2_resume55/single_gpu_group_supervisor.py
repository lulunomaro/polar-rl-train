"""OneoriginalGPUprivateEX+globalfiniteEXowner, oneE3isolatedSDKworker, honestreadybarrier/result/closewait. No learner/GO/ledgerwrite."""
from pathlib import Path
import os,sys,json,time,hashlib,fcntl,subprocess,traceback,signal,shutil
import psutil
from worker_sources.parent.fudan_task_contract_v2 import make_task
from worker_sources.parent.fudan_eval_parent_wait_contract_v1 import qualify_waited_eval
B=Path(__file__).resolve().parent;OWN=Path('/home/lc01/Zonglin Li/zonglin2')
def put(n,v):
 p=B/n;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2,allow_nan=False));q.replace(p)
def nvidia(uuid):
 raw=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();x=[v.strip()for v in raw.split(',')];return dict(GPU_UUID=x[0],name=x[1],total_MiB=int(x[2]),free_MiB=int(x[3]),utilization_percent=int(x[4]))
def main():
 assert B.is_relative_to(OWN/'tasks')and not(B/'PARENT_STARTED.json').exists();plan=json.loads((B/'GROUP_PLAN.json').read_bytes());uuid=plan['GPU_UUID'];roles=plan['roles'];assert len(roles)==3 and {r['role']for r in roles}==set(['E3_LOW80_20261002', 'E3_LOW80_20261003', 'E3_LOW80_20261004']);put('PARENT_STARTED.json',dict(pid=os.getpid(),creation=psutil.Process().create_time(),epoch=time.time(),kind='ONEGPU_E3_LOW80_THREE_SEED_HOLDOUT_RESUME55_NO_LEARNING',GPU_UUID=uuid));locks=[];children=[];errors=[];group_start=None;started=time.time();terminal=[]
 try:
  for r in plan['worker_files']:
   p=B/r['relative'];raw=p.read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA']
  class BusyResource(Exception):pass
  wait_until=time.monotonic()+1800;wait_rows=[]
  while True:
   candidate=None
   try:
    for path in(OWN/'state'/('three_expert_v2_'+uuid+'.lock'),OWN/'state/finite_environment_validation.lock'):
     candidate=path.open('rb+');fcntl.flock(candidate,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(candidate);candidate=None
    canonical=OWN/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';raw=canonical.read_bytes();c=json.loads(raw);assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['remaining_training_seconds']>c['finite_minimum_remaining_seconds']
    if c['active_segment']is not None:raise BusyResource('Originalcanonicalhasactiveowner;nointerference')
    apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
    if uuid in apps:raise BusyResource('Selectedcardhasexistingcomputeprocess')
    res=nvidia(uuid)
    if res['free_MiB']<23500 or res['utilization_percent']!=0:raise BusyResource('Selectedcardnotemptyatfreshadmission')
    assert psutil.virtual_memory().available>96*1024**3 and shutil.disk_usage(B).free>25*1024**3
    break
   except (BlockingIOError,BusyResource)as busy:
    if candidate is not None:candidate.close()
    for fd in reversed(locks):fcntl.flock(fd,fcntl.LOCK_UN);fd.close()
    locks.clear();wait_rows.append(dict(epoch=time.time(),reason=str(busy),locks_held=0,SDK_or_selected_model_opened=False,canonical_writes=0,remaining_wait_seconds=max(0,wait_until-time.monotonic())));put('BOUNDED_ORIGINAL_RESOURCE_WAIT.json',wait_rows)
    if time.monotonic()>=wait_until:raise TimeoutError('Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions')
    time.sleep(15)
  put('ACTUAL_GROUP_ADMISSION.json',dict(epoch=time.time(),group_id=plan['group_id'],resource=res,selected_card_compute_processes=[],original_private_GPU_EX_held=True,original_global_finite_EX_held=True,canonical_SHA_at_read=hashlib.sha256(raw).hexdigest(),canonical_original_generation=c['authority_generation'],canonical_remaining_snapshot=c['remaining_training_seconds'],canonical_minimum=c['finite_minimum_remaining_seconds'],canonical_owner_at_read=None,canonical_writes=0,canonical_bytes_copied=False,no_PPO_BPTT_GO=True));del raw,c
  deadline=time.time()+2400
  for r in roles:
   out=B/'cases'/r['role'];out.mkdir(parents=True,exist_ok=True);task=make_task(r,plan,deadline,[f.fileno()for f in locks]);(out/'task.json').write_text(json.dumps(task,indent=2));env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
   for key in('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(key,None)
   for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
    p=out/'private'/rel;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
   log=(out/'SDK_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/r['worker']),'--task',str(out/'task.json'),'--group-root',str(B)],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(f.fileno()for f in locks),start_new_session=True);log.close();children.append((r,out,p,psutil.Process(p.pid).create_time()));put('CHILDREN.json',[dict(role=r['role'],pid=p.pid,creation=creation,GPU_UUID=uuid,root=str(out),worker=r['worker'])for r,out,p,creation in children])
  assert len(children)==3;ready_until=time.time()+900;memory=[]
  while time.time()<ready_until:
   ready=[r['role']for r,out,p,creation in children if(out/'WORKER_SCENE_READY.json').exists()];failed=[r['role']for r,out,p,creation in children if(out/'WORKER_ERROR.json').exists()or(p.poll()is not None and r['role']not in ready)];put('GROUP_BARRIER_STATUS.json',dict(epoch=time.time(),ready=ready,failed=failed,members=[r['role']for r in roles]))
   if failed:raise RuntimeError('Someownmemberfailedbeforecommonstart:'+str(failed))
   if len(ready)==3:
    group_start=time.time();put('GROUP_EVAL_START.json',dict(group_id=plan['group_id'],GPU_UUID=uuid,members=ready,all_members_ready=True,epoch=group_start,source='E3SDKscene+livefrozenmean+N80fullDRreadybeforeanycontrolledstep'));break
   if not memory or time.time()-memory[-1]['epoch']>=30:memory.append(dict(epoch=time.time(),**nvidia(uuid)));put('GROUP_GPU_MEMORY_SAMPLES.json',memory)
   time.sleep(2)
  if group_start is None:raise TimeoutError('E3SDKstartupreadybarrier900s expired')
  while time.time()<deadline and any(p.poll()is None for r,out,p,creation in children):
   if not memory or time.time()-memory[-1]['epoch']>=30:memory.append(dict(epoch=time.time(),**nvidia(uuid)));put('GROUP_GPU_MEMORY_SAMPLES.json',memory)
   time.sleep(2)
  for r,out,p,creation in children:
   if p.poll()is None:raise TimeoutError('Owngroup2400s boundedworkerend:'+r['role'])
   rc=p.wait();data=json.loads((out/'FINAL.json').read_bytes())if(out/'FINAL.json').exists()else None;err=json.loads((out/'WORKER_ERROR.json').read_bytes())if(out/'WORKER_ERROR.json').exists()else None;qualification=qualify_waited_eval(out,json.loads((out/"task.json").read_bytes()),actual_child_pid=p.pid,actual_parent_pid=os.getpid(),returncode=rc,actual_waited=True);terminal.append(dict(fdn_wait_qualification=qualification,role=r['role'],pid=p.pid,GPU_UUID=uuid,returncode=rc,actual_waited=True,ready=(out/'WORKER_SCENE_READY.json').exists(),started=(out/'WORKER_EVAL_STARTED.json').exists(),pre_close=(out/'PRE_CLOSE.json').exists(),passed_execution=bool(rc==0 and data and data.get('passed_execution')and err is None and(out/'PRE_CLOSE.json').exists()and qualification.get('qualified')is True),data=data,error=err));put('TERMINAL_ROWS.json',terminal)
   if not terminal[-1]['passed_execution']:raise RuntimeError('FDN actual-wait qualification failed; own metadata preserved')
  put('FINAL.json',dict(kind='ACTUAL_SINGLE_GPU_E3_LOW80_THREE_SEED_HOLDOUT_RESUME55',group_id=plan['group_id'],GPU_UUID=uuid,common_start_epoch=group_start,nine_ready_before_start=True,all_nine_actual_execution_complete=all(v['passed_execution']for v in terminal),rows=terminal,source20k_DR_history_sliced=False,source20k_histories_physically_applied=False,old20k_fullrestore_proof_preserved_separately=True,new_PPO_BPTT_GO=0,canonical_writes=0,epoch=time.time()))
 except BaseException:
  errors.append(traceback.format_exc());put('GROUP_ABORT.json',dict(epoch=time.time(),errors=errors,ownscope_only=True));put('GROUP_STARTUP_ABORT.json',dict(epoch=time.time(),errors=errors,ownscope_only=True));put('PARENT_ORIGINAL_ERROR.json',dict(errors=errors,no_samepurpose_automatic_retry=True))
 finally:
  waits=[]
  for r,out,p,creation in children:
   if p.poll()is None:
    try:
     q=psutil.Process(p.pid);assert abs(q.create_time()-creation)<.02 and str(B)in' '.join(q.cmdline());os.killpg(p.pid,signal.SIGTERM)
    except psutil.NoSuchProcess:pass
    try:p.wait(timeout=25)
    except subprocess.TimeoutExpired:
     q=psutil.Process(p.pid);assert abs(q.create_time()-creation)<.02 and str(B)in' '.join(q.cmdline());os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=25)
   waits.append(dict(role=r['role'],pid=p.pid,returncode=p.wait(),actual_waited=True))
  waited=len(waits)==len(children)and all(v['actual_waited']for v in waits)
  if waited:
   for fd in reversed(locks):fcntl.flock(fd,fcntl.LOCK_UN)
  for fd in locks:fd.close()
  put('PARENT_EXIT_SCOPE.json',dict(epoch=time.time(),all_own_children_waited=waited,child_waits=waits,original_single_GPU_private_EX_released=waited,original_global_finite_EX_released=waited,errors=errors,no_foreign_scope_touched=True,canonical_writes=0,SDK_PT_opens_by_parent=0,wall_seconds=time.time()-started))
if __name__=='__main__':main()
