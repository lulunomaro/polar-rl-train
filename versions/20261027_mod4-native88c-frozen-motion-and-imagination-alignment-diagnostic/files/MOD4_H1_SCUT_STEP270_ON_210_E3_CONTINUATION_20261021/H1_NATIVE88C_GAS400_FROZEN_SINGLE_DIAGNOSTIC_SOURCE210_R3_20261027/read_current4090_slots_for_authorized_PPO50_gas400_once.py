"""Fresh GPU-only selection for the newly authorized expert adaptation schedule."""
from pathlib import Path
import json,time,sys,importlib.util,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
def put(n,x):
    with (R/n).open('x',encoding='utf8') as f: json.dump(x,f,indent=2)
CODE='''from pathlib import Path
import json,psutil,subprocess,shutil,fcntl,hashlib
rows=[]
for gpu in v['GPU_UUIDs']:
 line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
 assert line[0].strip()==gpu
 apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
 rows.append(dict(GPU_UUID=gpu,name=line[1].strip(),total_MiB=int(line[2]),free_MiB=int(line[3]),utilization_percent=int(line[4]),compute_UUID_only_rows=sum(gpu in x for x in apps.splitlines()),unknown_PID_identity_not_queried=True))
root=Path(v['disk_root']); result=dict(backend=v['backend'],epoch=__import__('time').time(),GPU_rows=rows,disk_root=str(root),disk_free_bytes=shutil.disk_usage(root).free,RAM_available_bytes=psutil.virtual_memory().available,no_model_actor_physics_or_account_write=True)
if v['backend']=='target72':
 C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
 assert c['active_segment'] is None
 assert c['remaining_training_seconds']>86412.86069250107
 result.update(canonical_None=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),closed_remaining_snapshot=c['remaining_training_seconds'])
 for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
  with (C.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 result['original_owner_locks_free']=True
 assert C.read_bytes()==raw
else:
 result['durable_mount']=subprocess.check_output(['findmnt','-n','-o','UUID,OPTIONS,TARGET','--target',str(root)],text=True).strip()
print(json.dumps(result))
'''
def main():
 put('FRESH4090_ADAPTATION_RESOURCE_READER_CONSUMED_ACTUAL.json',dict(epoch=time.time(),new_purpose='User requests expert adaptation only on free remote4090, no localGPU',no_training_or_process_action=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('authorized4090_adaptation_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None;rows={}
 try:
  c=d.connect72(secret);secret=None
  rows['target72']=d.code(c,d.PY72,CODE,dict(backend='target72',GPU_UUIDs=['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'],disk_root='/home/lc01/Zonglin Li/zonglin2'),timeout=60)
  put('CURRENT72_GPU_ONLY_AND_SOLE_ACCOUNT_FOR_PPO_ADAPTATION_ACTUAL.json',rows['target72']);c.close();c=None
  c=route.connect();rows['source210']=d.code(c,route.PY,CODE,dict(backend='source210',GPU_UUIDs=['GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'],disk_root='/mnt/mod4_linux_durable_20261013'),timeout=60)
  put('CURRENT210_GPU_ONLY_DURABLE_RESOURCE_FOR_PPO_ADAPTATION_ACTUAL.json',rows['source210'])
  result=dict(actual_finite_returned=True,rows=rows,no_unknown_process_identity_or_GPU_training=True)
  put('CURRENT4090_RESOURCE_SELECTION_FOR_EXPERT_PPO_ADAPTATION_RETURNED_ACTUAL.json',result)
  print(json.dumps(result))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('FRESH4090_ADAPTATION_RESOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_foreign_process_action=True));raise
