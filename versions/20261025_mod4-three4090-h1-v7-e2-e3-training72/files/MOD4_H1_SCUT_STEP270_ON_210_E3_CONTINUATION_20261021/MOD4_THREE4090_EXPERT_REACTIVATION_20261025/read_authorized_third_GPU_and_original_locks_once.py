"""Human explicitly requested all three GPUs for expert training. Device/lock probe only."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports';R.mkdir(exist_ok=True)
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import fcntl,json,psutil,shutil,subprocess,time
base=Path('/home/lc01/Zonglin Li/zonglin2');uuid='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines() if uuid in x)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
allocation_count=sum(uuid in x for x in compute.splitlines())
paths=[base/'state'/('three_expert_v2_'+uuid+'.lock'),base/'state/finite_environment_validation.lock'];locks=[]
for p in paths:
 row=dict(path=str(p),exists=p.is_file(),exclusive_probe_free=False)
 if row['exists']:
  with p.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);row['exclusive_probe_free']=True;fcntl.flock(f,fcntl.LOCK_UN)
   except BlockingIOError:pass
 locks.append(row)
free=shutil.disk_usage(base).free;ram=psutil.virtual_memory().available
print(json.dumps(dict(epoch=time.time(),GPU_UUID=uuid,GPU_resource_line=line,own_candidate_compute_allocation_count=allocation_count,expected_GPU_empty=allocation_count==0,free_MiB=int(line.split(',')[1]),GPU7000_passed=int(line.split(',')[1])>7000,disk_free=free,disk25_passed=free>25*1024**3,RAM_available=ram,RAM8_passed=ram>8*1024**3,locks=locks,no_unknown_peer_identity_PID_argv_or_lock_deletion=True,no_training_or_budget_write=True)))
'''
try:
 put('HUMAN_THREE_GPU_TRAINING_SCOPE_AND_PROBE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,human_instruction='三张都用上，继续修复h1上台阶还有继续推进其他专家训练',new_scope='Third4090 may advance existing qualified experts; original E2 deferred/shared-evaluation-only restriction superseded within safe original accounting/resources. No peer kill, lock deletion, budget extension, subagents or T2z training.',single_original_writer_requires_new_three_slot_owner_after_actual71_close=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 p=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py';sp=importlib.util.spec_from_file_location('memory',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:result=d.code(c,d.PY72,CODE,{},timeout=30)
 finally:c.close()
 put('THIRD_GPU_ORIGINAL_PRIVATE_SHARED_LOCKS_RESOURCE_RETURNED_ACTUAL.json',dict(result,actual_finite_returned=True))
 print(json.dumps(result))
except BaseException:
 put('THIRD_GPU_RESOURCE_PROBE_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_once_or_peer_action=True));raise
