"""One bounded resource-only boundary reader after pre-App rejection. No model/scene."""
from pathlib import Path
import sys,json,time,traceback,importlib.util
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE="""from pathlib import Path
import json,psutil,subprocess,shutil,fcntl,hashlib
q=v['q'];backend=v['backend'];gpu=v['gpu'];checks=[]
for r in q['known_qualified_own_processes']:
 source=r['role'].startswith('h1_')
 if source!=(backend=='source210'):continue
 try:
  p=psutil.Process(r['pid']);assert p.create_time()!=r['creation'],'original owned process remains'
  checks.append(dict(role=r['role'],original_out_PID_recycled_no_foreign_identity_read=True))
 except psutil.NoSuchProcess:checks.append(dict(role=r['role'],original_owned_process_out=True))
line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
assert line[0].strip()==gpu
apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
result=dict(backend=backend,GPU_UUID=gpu,memory_free_MiB=int(line[2]),utilization_percent=int(line[3]),selected_compute_UUID_rows=sum(gpu in x for x in apps.splitlines()),unknown_PID_identity_not_queried=True,own_original_out=checks,eval_root_exists=Path(q['eval_root']).exists(),no_model_actor_physics_account_write=True)
if backend=='target72':
 C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
 assert c['active_segment'] is None and c['remaining_training_seconds']==562175.5721518993
 result.update(canonical_None=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),closed_remaining_snapshot=c['remaining_training_seconds'])
 for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
  with (C.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 result['original_owner_locks_free']=True
 assert C.read_bytes()==raw
else:
 volume=Path('/mnt/mod4_linux_durable_20261013');result.update(durable_free_bytes=shutil.disk_usage(volume).free,RAM_available_bytes=psutil.virtual_memory().available)
 result['original_mount']=subprocess.check_output(['findmnt','-n','-o','UUID,OPTIONS,TARGET','--target',str(volume)],text=True).strip()
print(json.dumps(result))
"""
def main():
 q=json.loads((S/'BINDING.json').read_bytes());put('RESOURCE_BOUNDARY_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),original_stage_consumed_pre_App=True,one_resource_read_only=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native88C_prelaunch_boundary_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None;rows={}
 try:
  c=d.connect72(secret);secret=None;rows['target72']=d.code(c,d.PY72,CODE,dict(q=q,backend='target72',gpu=q['GPU_UUID']),timeout=60);put('ACTUAL72_SELECTED_GPU_PREAPP_BOUNDARY.json',rows['target72']);c.close();c=None
  c=route.connect();rows['source210']=d.code(c,route.PY,CODE,dict(q=q,backend='source210',gpu='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'),timeout=60);put('ACTUAL210_OTHER_AUTHORIZED_GPU_RESOURCE_BOUNDARY.json',rows['source210'])
  put('PREAPP_BOUNDARY_AND_OTHER_CARD_RETURNED_ACTUAL.json',dict(actual_finite_transport_returned=True,rows=rows,no_model_or_rollout_or_budget_write=True))
  print(json.dumps(rows))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('RESOURCE_BOUNDARY_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_process_action=True));raise
