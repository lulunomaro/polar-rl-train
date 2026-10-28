from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=B/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,psutil,shutil,subprocess,socket
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
account=dict(canonical_None=c['active_segment'] is None,remaining=c['remaining_training_seconds'],expected_source_seal_closed_snapshot=v['expected_closed_remaining'],generation=c['authority_generation'],budget_mode=c['budget_mode'])
assert account['generation']=='MOD4_SINGLE_WRITER72_20261026' and account['budget_mode']=='finite_original_limits_restored_after_single4090_return'
locks={}
for path in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock',*[Path(s['private_lock']) for s in v['experts'].values()]):
 try:
  with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  locks[str(path)]=True
 except BlockingIOError:locks[str(path)]=False
resources={}
for key,s in v['experts'].items():
 gpu=s['GPU_UUID'];line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=15).strip();a=[x.strip() for x in line.split(',')]
 assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090'
 apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15)
 resources[key]=dict(GPU_UUID=gpu,actual_GPU_line=line,free_MiB=int(a[2]),utilization_percent=int(a[3]),compute_UUID_only_output=apps,selected_compute_empty=gpu not in apps,disk_available=shutil.disk_usage(s['job_root']).free)
ram=psutil.virtual_memory().available
ready=account['canonical_None'] and account['remaining']==account['expected_source_seal_closed_snapshot'] and account['remaining']>86412.86069250107 and all(locks.values()) and ram>32*1024**3 and all(x['utilization_percent']<=30 and x['free_MiB']>15669 and x['disk_available']>25*1024**3 for x in resources.values())
assert C.read_bytes()==raw
print(json.dumps(dict(passed_fresh_original_startup_resource_snapshot=ready,resources=resources,account=account,locks=locks,RAM_available=ram,canonical_SHA=hashlib.sha256(raw).hexdigest(),read_only_no_model_CUDA_unknown_PID_or_account_write=True,no_GO=True)))
'''
def main():
 public=json.loads((L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V3/reports/TWO103_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes())
 put('SHARED104_USER_AUTHORIZED_RESOURCE_ENTRY_CONSUMED_ACTUAL.json',dict(epoch=time.time(),one_scheduling_boundary_snapshot=True,no_periodic_loop=True))
 wrapper=mod('new103_resource_memory_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=mod('new103_resource_existing_secret_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None
 try:
  client=d.connect72(secret);secret=None;value=d.code(client,d.PY72,CODE,public,timeout=60)
  put('SHARED104_USER_AUTHORIZED_RESOURCE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,**value));print(json.dumps(value))
 finally:
  secret=None
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('SHARED104_RESOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_interference=True));raise
