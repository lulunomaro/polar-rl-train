from pathlib import Path
import importlib.util, json, sys, time, traceback
B=Path(__file__).resolve().parent; T=B.parent; W=T.parent; R=B/'reports'
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import json,os,shutil,subprocess,time
base=Path('/home/lc01/Zonglin Li/zonglin2');assert base.resolve(strict=True)==base
before=shutil.disk_usage(base)
rows=[]
for p in (base,base/'forensic_originals',base/'tasks'):
    assert p.resolve(strict=True)==base or base in p.resolve(strict=True).parents
    q=subprocess.run(['du','-x','-B1','--max-depth=1','--',str(p)],capture_output=True,text=True,timeout=100)
    rows.append(dict(path=str(p),returncode=q.returncode,stdout=q.stdout,stderr=q.stderr))
after=shutil.disk_usage(base)
print(json.dumps(dict(epoch=time.time(),host='10.24.0.72',root=str(base),
  filesystem_before=dict(total=before.total,used=before.used,free=before.free),
  filesystem_after=dict(total=after.total,used=after.used,free=after.free),du_actual=rows,
  read_only_allocated_bytes_not_binary_read_or_hash=True,no_GPU_process_identity_training_or_budget_access=True,
  other_users_disk_usage_not_queried=True,no_delete_move_write_or_permission_change=True)))
'''
try:
    put('V111_HUMAN_500GB_STORAGE_QUESTION_AND_SCOPE_ACTUAL.json',dict(epoch=time.time(),
      previous_question_item_id='call_9322b542a01c4f54bb9c899a228f3ab4',
      exact_human_reply='zonglin2整个盘最开始训练的时候不都还有500g吗？',
      request='Explain current storage use in the already designated root using read-only capacity and allocated directory sizes.',
      no_new_path_yet_no_deletion_authorization_inferred=True))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory)
    secret=memory.recover()
    try:c=d.connect72(secret)
    finally:secret=None
    try:v=d.code(c,d.PY72,CODE,{},timeout=320)
    finally:c.close()
    put('V111_DESIGNATED72_DIRECTORY_ALLOCATED_USAGE_READONLY_ACTUAL.json',v)
    print(json.dumps(v,ensure_ascii=False))
except BaseException:
    put('V111_DESIGNATED72_USAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
