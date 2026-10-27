"""One finite on original72/c27; NEW qualified88C frozen case, no learning."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
old=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/run_native87R5_old700_r2_fixed_frozen_diagnostics_once.py'
sp=importlib.util.spec_from_file_location('consumed_R2_parent_definitions_only_for_new88C',old);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
PREP="""from pathlib import Path
import json,psutil,shutil,subprocess,time,fcntl
q=v['q'];root=Path(q['eval_root']);owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks')
assert root.resolve().is_relative_to(owned.resolve()) and not root.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['remaining_training_seconds']==q['actual_closed_balance']==562175.5721518993
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107
assert [r['path'] for r in q['original_owner_locks']]==[str(C.parent/x) for x in ('native_floor_supervisor.lock','autonomy_controller.lock')]
for p in [r['path'] for r in q['original_owner_locks']]+q['selected_GPU_original_locks']:
 with open(p,'rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
gpu=subprocess.check_output(['nvidia-smi','-i',q['GPU_UUID'],'--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',')
assert gpu[0].strip()==q['GPU_UUID'] and int(gpu[1])>15669
users=subprocess.check_output(['nvidia-smi','-i',q['GPU_UUID'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert q['GPU_UUID'] not in users
for row in q['known_qualified_own_processes']:
 if row['role'].startswith('h1_'):continue
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['creation'],row['role']
 except psutil.NoSuchProcess:pass
assert C.read_bytes()==raw
root.mkdir()
print(json.dumps(dict(new_unused_root=str(root),canonical_None=True,canonical_SHA=__import__('hashlib').sha256(raw).hexdigest(),original_closed_balance=c['remaining_training_seconds'],selected_GPU_empty=True,original_locks_free=True,no_other_GPU_or_process_identity_queried=True,no_budget_write=True)))
"""
RUN=m.RUN
before="assert {m.name for m in members}=={x for x in expected if x=='BINDING.json' or x.startswith('code/')}"
after="assert {m.name for m in members}=={x for x in expected if x!=q['model_eval_relative']}"
assert RUN.count(before)==1;RUN=RUN.replace(before,after,1)
before="p=root/rel;assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'],rel"
after="p=root/rel;assert p.stat().st_size==row['bytes'],rel\n if rel!=q['model_eval_relative']:assert H(p)==row['SHA'],rel\n # The fixed SDK entry performs the one full-SHA verification of the new-purpose model copy before App/forward."
assert RUN.count(before)==1;RUN=RUN.replace(before,after,1)
assert RUN.count('native87R5_frozen_single_sdk_entry_unused_once.py')==1
RUN=RUN.replace('native87R5_frozen_single_sdk_entry_unused_once.py','native88C_frozen_single_sdk_entry_unused_once.py')
ast.parse(PREP);ast.parse(RUN)
def main():
 q=json.loads((S/'BINDING.json').read_bytes());index=json.loads((S/'INPUT_TRANSFER_INDEX.json').read_bytes())
 assert q['seeds']==[20260928] and q['selected_key']=='h1' and q['execution_backend']=='target72'
 assert q['source_model']['SHA']=='a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf'
 put('FINITE_STARTED_BEFORE_REMOTE_ACTUAL.json',dict(epoch=time.time(),purpose=q['purpose'],exact_one_fixed_seed=True,no_learning_or_budget_write=True,no_retry=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('existing_authorized_same_session_hidden_memory_for_native88C',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
 secret=a.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  pre=d.code(c,d.PY72,PREP,dict(q=q),timeout=60);put('ACTUAL72_FRESH_PREFLIGHT_BEFORE_NEW_FROZEN_CASE.json',pre)
  sf=c.open_sftp();sf.get_channel().settimeout(180)
  try:
   sf.put(index['archive']['path'],q['eval_root']+'/PINNED_NEW_EVAL_INPUTS.tar')
   dest=q['eval_root']+'/'+q['model_eval_relative'];sf.mkdir(q['eval_root']+'/qualified_model')
   source=next(r for r in index['files'] if r['relative']==q['model_eval_relative'])
   assert Path(source['local']).stat().st_size==source['bytes']
   sf.put(source['local'],dest+'.transfer_partial');assert sf.stat(dest+'.transfer_partial').st_size==source['bytes'];sf.rename(dest+'.transfer_partial',dest)
  finally:sf.close()
  value=d.code(c,d.PY72,RUN,dict(q=q,archive=index['archive'],files=index['files']),timeout=750)
  put('ACTUAL72_FROZEN_PARENT_RAW_RETURNED.json',value)
  local=[];sf=c.open_sftp();sf.get_channel().settimeout(180)
  try:
   for row in value['files']:
    rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts and row['bytes']<128*1024**2
    p=S/'actual72'/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
    sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
    local.append(dict(row,local_path=str(p),twohost_SHA_verified=True))
  finally:sf.close()
  put('FROZEN_NATIVE88C_FIXED_SINGLE_FINITE_RETURNED_ACTUAL.json',dict(value,actual_finite_transport_returned=True,local_files=local,source_SHA=q['source_model']['SHA'],gas400_same_point_objective_diagnostic=True))
  print(json.dumps(dict(actual_finite_returned=True,cases=len(value['cases']),all_own_out=value['all_own_children_actual_out'],parent_original_error=value['parent_original_error'])))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('LOCAL_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_kill=True));raise
