"""Exact source copy and V5-only migration; no model load, App, GO or writer."""
from pathlib import Path
import json,time,hashlib,importlib.util,sys,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent
N=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027';R=N/'reports'
A=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E0_PPO50_gas400_logger_presave_V5_source_candidate_20261027'
OLD='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0'
NAME='E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,x):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
COPY='''from pathlib import Path
import json,hashlib,shutil,fcntl,psutil,subprocess,time
old=Path(v['old']);B=Path(v['root']);assert not B.exists()
close=Path(v['ending_remote']);assert hashlib.sha256(close.read_bytes()).hexdigest()==v['ending_SHA'];closed=json.loads(close.read_bytes());assert closed['actual_early_error_ending_returned'] and closed['all_original_locks_free']
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None and c['remaining_training_seconds']==561777.961785078 and c['remaining_training_seconds']>86412.86069250107
for path in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock'):
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(old).free>25*1024**3
B.mkdir(parents=True);copied=[]
for r in v['rows']:
 rel=r['relative']
 if not (rel.startswith(('runtime/','source/')) or rel=='original_run_manifest.json'):continue
 p=old/rel;dest=B/rel;assert p.is_file() and not p.is_symlink() and p.stat().st_size==r['bytes'] and dest.resolve().is_relative_to(B.resolve())
 a=p.stat();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);b=p.stat();assert (a.st_size,a.st_mtime_ns,a.st_ino)==(b.st_size,b.st_mtime_ns,b.st_ino)
 with dest.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 assert h==r['SHA'],rel;copied.append(rel)
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(actual_unchanged_qualified_model_runtime_copy_fullSHA=True,files=len(copied),canonical_None=True,remaining_snapshot=c['remaining_training_seconds'],actual_failed89C_resource_cost_only=True,resource=dict(GPU_UUID=gpu,GPU_name=line[1].strip(),free_MiB=int(line[2]),utilization_percent=int(line[3]),compute_UUID_only_rows=0),no_model_load_or_GPU_scene=True)))
'''
EXTEND='''from pathlib import Path
import json,hashlib,time
B=Path(v['root']);old=Path(v['old']);new=(B/v['name']).read_bytes();previous=(old/'E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py').read_bytes()
assert hashlib.sha256(new).hexdigest()=='ec8eba0365f0129b2799ef4e1ae7f3673beb585f87d4e25d2c36cf7bdb33b08c' and hashlib.sha256(previous).hexdigest()=='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
expected=previous.replace(b' def work(runner,n,log_dir):\n',b' def work(runner,n,log_dir):\n  runner.logger.writer=None\n',1).replace(b'  runner.logger.writer=None;completed=0;',b'  completed=0;',1)
assert expected==new,'only existing assignment move before save'
cpu=old/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';base=cpu.read_bytes();assert hashlib.sha256(base).hexdigest()=='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c'
lr=old/'E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json';lrraw=lr.read_bytes();assert hashlib.sha256(lrraw).hexdigest()=='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e'
value=dict(epoch=time.time(),passed=True,kind='MOD4_E0_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1',source_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371',base_actual_fullstate_CPU_SHA=hashlib.sha256(base).hexdigest(),base_actual_fullstate_CPU_path=str(cpu),base_actual_fullstate_CPU_value=json.loads(base),base_V4_worker_only_LR_source_migration_SHA=hashlib.sha256(lrraw).hexdigest(),base_V4_worker_only_LR_source_migration_path=str(lr),base_V4_worker_only_LR_source_migration_value=json.loads(lrraw),base_worker_SHA=hashlib.sha256(previous).hexdigest(),target_worker_SHA=hashlib.sha256(new).hexdigest(),target_worker_filename=v['name'],exact_existing_writer_assignment_move=True,no_model_reload=True,no_new_fullstate_CPU_load_claim=True,actual_CUDA_fullrestore_pending=True,new_job_root=str(B),failed89C_resource_cost_only=True,failed89C_original_ending_SHA=v['ending_SHA'],source_copy_receipt=v['copy_receipt'])
p=B/'E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json'
with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(path=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=value)))
'''
def main():
 assert not N.exists();N.mkdir();R.mkdir()
 put('E0_UNUSED89D_V5_SOURCE_MIGRATION_CONSUMED_ACTUAL.json',dict(epoch=time.time(),original89C_failed_before_newPPO=True,source_still_original_typed54f=True,no_model_reload=True))
 ending=S/'reports/E0_89C_ORIGINAL_LOGGER_FAILURE_SETTLED_FEE_ALLOUT_V3_RETURNED_ACTUAL.json';endingSHA=H(ending);assert endingSHA=='e90bda2d34777c60661880f9aa390bd6974437e21a4a9adfade71b933d096ef1'
 rows=json.loads((T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89B_20261027/reports/E0_V89B_ACTUAL_INSTALL_PAYLOAD_MANIFEST.json').read_bytes())['rows']
 worker=A/NAME;assert H(worker)=='ec8eba0365f0129b2799ef4e1ae7f3673beb585f87d4e25d2c36cf7bdb33b08c'
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('E0_V5_prepare_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  # This is the receipt, never a copied canonical ledger.
  endingRemote=OLD+'/FAILED89C_ORIGINAL_ENDING_RESOURCE_ONLY_RECEIPT.json'
  assert d.code(c,d.PY72,"from pathlib import Path;import json;assert not Path(v['p']).exists();print(json.dumps(dict(new_receipt_path=True)))",dict(p=endingRemote),timeout=30)['new_receipt_path']
  sf=c.open_sftp()
  try:sf.put(str(ending),endingRemote)
  finally:sf.close()
  copy=d.code(c,d.PY72,COPY,dict(old=OLD,root=ROOT,rows=rows,ending_remote=endingRemote,ending_SHA=endingSHA),timeout=90)
  put('E0_89D_ACTUAL_QUALIFIED_SOURCE_COPY_AND_FAILED_RESOURCE_ADMITTED.json',copy)
  sf=c.open_sftp()
  try:sf.put(str(worker),ROOT+'/'+NAME)
  finally:sf.close()
  result=d.code(c,d.PY72,EXTEND,dict(old=OLD,root=ROOT,name=NAME,ending_SHA=endingSHA,copy_receipt=copy),timeout=60)
  sf=c.open_sftp()
  try:
   with sf.open(result['path'],'rb') as f:raw=f.read()
  finally:sf.close()
  assert hashlib.sha256(raw).hexdigest()==result['SHA']
  with (R/'E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json').open('xb') as f:f.write(raw)
  final=dict(actual_finite_returned=True,actual_new89D_source_copy_and_V5_only_migration_passed=True,source_CPU_SHA=result['SHA'],source_SHA=result['value']['source_SHA'],worker_SHA=result['value']['target_worker_SHA'],root=ROOT,no_GPU_GO_or_model_reload=True)
  put('E0_UNUSED89D_SOURCE_V5_ORIGINAL_RESOURCE_ADMITTED_RETURNED_ACTUAL.json',final);print(json.dumps(final))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_89D_SOURCE_MIGRATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_GPU_GO=True));raise
