"""Add exact V4 worker; reuse actual fullstate witness, never reload a model."""
from pathlib import Path
import json,hashlib,importlib.util,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
A=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E0_PPO50_gas400_single72_controller_source_preparation_v1'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0'
NAME='E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE='''from pathlib import Path
import hashlib,json,fcntl,time
B=Path(v['root']);assert not (B/'GO_PRODUCTION.json').exists() and not (B/'adaptation').exists()
p=B/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';base=p.read_bytes();assert hashlib.sha256(base).hexdigest()=='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c'
q=json.loads(base);assert q['passed'] and q['worker_SHA']=='1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152'
old=(B/'E0_PPO50_gas400_finite_worker_v1.py').read_bytes();assert hashlib.sha256(old).hexdigest()==q['worker_SHA']
new=(B/v['name']).read_bytes();assert hashlib.sha256(new).hexdigest()=='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
a=b"'--learning_rate','.0001'";b=b"'--learning_rate','.00038443359375000017'";assert old.count(a)==1 and old.replace(a,b,1)==new
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None and c['remaining_training_seconds']>86412.86069250107
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (C.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
model=B/'source/E0_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt';assert model.stat().st_size==14035948
result=dict(epoch=time.time(),passed=True,kind='MOD4_E0_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1',source_SHA=q['source_SHA'],base_actual_fullstate_CPU_SHA=hashlib.sha256(base).hexdigest(),base_actual_fullstate_CPU_path=str(p),base_actual_fullstate_CPU_value=q,base_worker_SHA=q['worker_SHA'],target_worker_SHA=hashlib.sha256(new).hexdigest(),target_worker_filename=v['name'],original_optimizer_LR_and_required_constructor_scalar=.00038443359375000017,exact_single_CLI_literal_change=True,no_model_reload=True,no_new_fullstate_CPU_load_claim=True,actual_CUDA_fullrestore_pending=True,no_Task_GO_PPO_or_account_write=True)
assert C.read_bytes()==raw
out=B/'E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json'
with out.open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(value=result,path=str(out),SHA=hashlib.sha256(out.read_bytes()).hexdigest())))
'''
def main():
 put('E0_V4_WORKER_ONLY_EXACT_LR_PUBLISH_CONSUMED_ACTUAL.json',dict(epoch=time.time(),base89C_actualmodelCPU_witness_reused=True,no_model_SDK_GPU_or_training=True))
 worker=A/NAME;assert hashlib.sha256(worker.read_bytes()).hexdigest()=='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('E0_workerLR_publish_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  assert d.code(c,d.PY72,"from pathlib import Path;import json;assert not Path(v['p']).exists();print(json.dumps(dict(new_additive_worker_absent=True)))",dict(p=ROOT+'/'+NAME),timeout=30)['new_additive_worker_absent']
  sf=c.open_sftp()
  try:sf.put(str(worker),ROOT+'/'+NAME)
  finally:sf.close()
  result=d.code(c,d.PY72,CODE,dict(root=ROOT,name=NAME),timeout=60)
  # Save the exact JSON bytes produced remotely, not a reserialized substitute.
  sf=c.open_sftp()
  try:
   with sf.open(result['path'],'rb') as f:raw=f.read()
  finally:sf.close()
  assert hashlib.sha256(raw).hexdigest()==result['SHA']
  with (R/'E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json').open('xb') as f:f.write(raw)
  put('E0_V4_ADDITIVE_WORKER_SOURCE_EXTENSION_RETURNED_ACTUAL.json',dict(actual_finite_returned=True,source_CPU_SHA=result['SHA'],worker_V4_SHA=result['value']['target_worker_SHA'],root=ROOT,no_model_reload_no_GPU_GO=True))
  print(json.dumps(dict(actual_finite_returned=True,extension_SHA=result['SHA'],worker=result['value']['target_worker_SHA'],no_model_reload_no_GPU=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_V4_WORKER_SOURCE_EXTENSION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_GPU=True));raise
