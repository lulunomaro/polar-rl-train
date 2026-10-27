"""Missing-only original first case/error/allout; no second attempt or model read."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
CODE="""from pathlib import Path
import json,hashlib,fcntl,psutil,time
q=v['q'];root=Path(q['eval_root']);original=json.loads((root/'PARENT_FINITE_RESULT_ACTUAL.json').read_bytes())
assert 'pid=515220' in original['parent_original_error'] and original['cases']==[]
pids=[]
try:
 p=psutil.Process(515220);creation=p.create_time()
 if creation>original['epoch']:pids.append(dict(pid=515220,original_own_out_PID_recycled=True,no_foreign_identity_query=True))
 else:
  assert v['started']<=creation<=original['epoch'],'not the recorded own child creation window'
  if p.status()==psutil.STATUS_ZOMBIE:
   pids.append(dict(pid=515220,creation=creation,own_process_zombie_not_running=True))
  else:
   argv=p.cmdline();assert str(root/'code/native87R5_frozen_single_sdk_entry_unused_once.py') in argv and argv[-1]=='20260928'
   try:p.wait(timeout=60)
   except psutil.TimeoutExpired:raise AssertionError('exact own first case still running; preserve it')
   pids.append(dict(pid=515220,creation=creation,exact_own_child_now_out=True))
except psutil.NoSuchProcess:pids.append(dict(pid=515220,actual_original_own_PID_out=True))
lock_rows=[]
paths=[r['path'] for r in q['original_owner_locks']]+q['selected_GPU_original_locks']
for name in paths:
 with open(name,'rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);lock_rows.append(dict(path=name,actual_fcntl_free=True))
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes())
assert c['active_segment'] is None and c['remaining_training_seconds']==569553.363275528
files=[]
for p in root.iterdir():
 if p.is_file() and p.name in ('PARENT_FINITE_RESULT_ACTUAL.json','PARENT_ORIGINAL_ERROR_ACTUAL.json'):
  raw=p.read_bytes();files.append(dict(path=str(p),relative=p.relative_to(root).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for p in root.rglob('*'):
 rel=p.relative_to(root)
 if p.is_file() and not p.is_symlink() and rel.parts[0].startswith('seed_') and not any(x in rel.parts for x in ('private','home','tmp','cache','config','data','__pycache__')) and p.suffix in ('.json','.jsonl','.log'):
  raw=p.read_bytes();assert len(raw)<128*1024**2
  files.append(dict(path=str(p),relative=rel.as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
print(json.dumps(dict(original_parent_error_preserved=original['parent_original_error'],own_pid_evidence=pids,locks=lock_rows,canonical_None=True,closed_balance=c['remaining_training_seconds'],files=files,no_new_case_actor_or_model_read=True)))
"""
def main():
 q=json.loads((S/'BINDING.json').read_bytes());started=json.loads((R/'FINITE_STARTED_BEFORE_REMOTE_ACTUAL.json').read_bytes())['epoch']
 put('MISSING_ONLY_OWN_FIRST_CASE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),own_pid=515220,no_new_case=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('missing_old700_case_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  value=d.code(c,d.PY72,CODE,dict(q=q,started=started),timeout=90);local=[]
  sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in value['files']:
    rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
    p=S/'missing_actual72'/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
    sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
    local.append(dict(row,local_path=str(p),twohost_SHA_verified=True))
  finally:sf.close()
  put('MISSING_ONLY_OWN_FIRST_CASE_ERROR_AND_ALLOUT_RETURNED_ACTUAL.json',dict(value,actual_finite_returned=True,local_files=local))
  print(json.dumps(dict(returned=True,files=len(local),own_pid=value['own_pid_evidence'],locks_free=True,no_new_case=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('MISSING_ONLY_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
