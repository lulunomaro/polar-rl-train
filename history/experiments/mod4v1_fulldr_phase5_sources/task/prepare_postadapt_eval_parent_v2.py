"""Source-only bounded original-lease wait, so another GPU's existing shared lease exits naturally.
No SDK/model/authority actions are executed by this preparer.
"""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent
s=(R/'w35_eval_parent_v1.py').read_text(encoding='utf-8')
old="""  for path in (BASE/'state'/('three_expert_v2_'+task['GPU_UUID']+'.lock'),BASE/'state/finite_environment_validation.lock'):
   f=path.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
"""
new="""  lease_deadline=time.time()+600
  while True:
   attempt=[]
   try:
    for path in (BASE/'state'/('three_expert_v2_'+task['GPU_UUID']+'.lock'),BASE/'state/finite_environment_validation.lock'):
     f=path.open('rb+');attempt.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:
    for f in reversed(attempt):fcntl.flock(f,fcntl.LOCK_UN);f.close()
    put('WAIT_ORIGINAL_RESOURCES.json',{'epoch':time.time(),'no_model_or_SDK_started':True,'no_locks_kept_while_waiting':True,'same_original_EX_modes':True,'max_wait_seconds':600,'canonical_reads_or_writes_so_far':0})
    if time.time()>=lease_deadline:raise TimeoutError('Original lease wait expired; case remains no-model/no-SDK and is not automatically replayed')
    time.sleep(45)
   else:
    locks=attempt;break
"""
assert s.count(old)==1;s=s.replace(old,new);p=R/'w35_eval_parent_resource_wait_v2.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
s=(R/'deploy_postadapt_w35_eval_ROOT_once.py').read_text(encoding='utf-8').replace('w35_eval_parent_v1.py','w35_eval_parent_resource_wait_v2.py')
p=R/'deploy_postadapt_w35_eval_ROOT_v2_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
report={'kind':'SOURCE_ONLY_POSTSAVE_RESOURCE_WAIT_DERIVATION','no_SDK_PT_GO_or_canonical_access':True,'original_private_and_validation_EX_modes_unchanged':True,'lease_wait_seconds':600,'lease_wait_holds_nothing':True,'worker_after_actual_lease_scope_unchanged_seconds':3780,'parent_source_SHA':hashlib.sha256((R/'w35_eval_parent_resource_wait_v2.py').read_bytes()).hexdigest(),'purpose':'After originalW35save/settled/waited/released, wait bounded for existing otherGPU SH lease to finish naturally; no steal/replay/extra learning'}
(R/'reports/POSTADAPT_EVAL_RESOURCE_WAIT_SOURCE_ONLY_V2.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
