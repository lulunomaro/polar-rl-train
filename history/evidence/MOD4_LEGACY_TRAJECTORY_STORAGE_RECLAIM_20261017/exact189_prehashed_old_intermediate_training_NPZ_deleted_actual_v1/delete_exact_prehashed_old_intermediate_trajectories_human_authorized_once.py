"""Delete only the explicit prehashed old training NPZ list; no recursive deletion."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
sys.path.insert(0,str(B.parent/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017'))
import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
P=R/'EXACT_OLD_INTERMEDIATE_TRAJECTORIES_PREDELETE_FULL_SHA_AND_PROTECTED_FILES_V5_ACTUAL.json'
CODE=r'''
from pathlib import Path
import os,stat,time,json,hashlib,fcntl,psutil,shutil,re,traceback
manifest=MANIFEST;expected=EXPECTED;assert hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()==expected
items=manifest['delete_files'];roots=sorted({r['root'] for r in items});paths={r['path'] for r in items};assert len(items)==189 and manifest['candidate_full_SHA_and_predelete_identity_verified']
assert manifest['no_delete_performed'];D=Path('/mnt/mod4_linux_durable_20261013');home=Path('/home/egde/rl_candidates')
root=D/'MOD4_LEGACY_TRAJECTORY_STORAGE_RECLAIM_20261017';assert not root.exists();root.mkdir();assert root.resolve()==root
lock=open(root/'OWN_CLEANUP_ONCE.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def dump(path,value):
 with path.open('x',encoding='utf8') as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
dump(root/'PREDELETE_FULL_SHA_AND_PROTECTED_FILES_ACTUAL.json',manifest)
dump(root/'HUMAN_AUTHORIZED_APPLY_ONCE_CONSUMED.json',dict(epoch=time.time(),pid=os.getpid(),manifest_SHA=expected,explicit_human_authorization='大量老旧远古训练轨迹可以删除了',exact_count=len(items),no_recursive_delete=True))
def validate(r):
 p=Path(r['path']);base=Path(r['root']);assert base.parent in (D,home) and base.name.startswith('MOD4_') and p.is_relative_to(base)
 assert p.resolve(strict=True)==p and base.resolve(strict=True)==base
 for q in (p,*p.parents):assert not q.is_symlink()
 assert 'learning_logs' in p.parts and bool(re.fullmatch(r'(?:S4_GATE_FULL_ROLLOUT_\d+|retention_prefix_\d+_\d+)\.npz',p.name))
 st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==os.getuid() and st.st_nlink==1
 assert (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)==(r['dev'],r['inode'],r['bytes'],r['mtime_ns'])
 return p,st
def process_guard():
 for q in psutil.process_iter(['pid','cmdline','cwd']):
  if q.pid==os.getpid():continue
  args=(q.info.get('cmdline') or [])+[q.info.get('cwd') or '']
  assert not any(x==s or x.startswith(s+'/') for x in args for s in roots),dict(owned_old_scope_referenced_by_pid=q.pid)
def protected_guard():
 for r in manifest['protected_other_files_metadata']:
  p=Path(r['path']);st=p.lstat();assert not p.is_symlink() and (st.st_ino,st.st_size,st.st_mtime_ns)==(r['inode'],r['bytes'],r['mtime_ns']),r['path']
for r in items:validate(r)
process_guard();protected_guard();before={str(p):dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in (D,home)};deleted=[];receipt=None
try:
 with (root/'DELETED_FILE_JOURNAL.jsonl').open('x',encoding='utf8') as journal:
  for i,r in enumerate(items):
   if i%10==0:process_guard()
   p,st=validate(r);parent=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
   fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
   try:
    fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);fdst=os.fstat(fd);assert (fdst.st_dev,fdst.st_ino,fdst.st_size,fdst.st_mtime_ns)==(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
    assert os.stat(p.name,dir_fd=parent,follow_symlinks=False).st_ino==st.st_ino
    os.unlink(p.name,dir_fd=parent)
    row=dict(path=r['path'],bytes=r['bytes'],allocated_bytes=r['allocated_bytes'],SHA_before_deletion=r['SHA'],epoch=time.time(),deleted=True,explicit_authorization_scope='old middle training trajectory; checkpoint and boundary samples retained')
    deleted.append(row);journal.write(json.dumps(row)+'\n');journal.flush();os.fsync(journal.fileno())
   finally:os.close(fd);os.close(parent)
 protected_guard();assert all(not Path(r['path']).exists() for r in items)
 after={str(p):dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in (D,home)}
 receipt=dict(epoch=time.time(),passed=True,host='10.24.4.210 original single4090',explicit_human_authorization='大量老旧远古训练轨迹可以删除了',manifest_SHA=expected,deleted_files=deleted,deleted_count=len(deleted),deleted_apparent_bytes=sum(r['bytes'] for r in deleted),deleted_allocated_bytes=sum(r['allocated_bytes'] for r in deleted),filesystem_before=before,filesystem_after=after,protected_other_files_metadata_exact_unchanged=True,protected_file_count=manifest['protected_file_count'],all_selected_deleted_paths_absent=True,retained_all_models_checkpoints_source_reports_frozen_evaluation_raw_failure_prefixes_and_first_last_samples=True,no_live_runtime_GPU_budget_canonical_lock_or_mount_modified=True,no_Windows_C_system_or_other_user_or_host72_files_touched=True,no_automatic_future_cleanup=True,global_process_FD_absence_not_claimed=True,old_reports_indexes_remain_historical_precleanup_evidence=True,only_listed_remote_raw_originals_intentionally_deleted_not_claimed_still_retained=True)
 dump(root/'HUMAN_AUTHORIZED_LEGACY_TRAJECTORY_DELETE_COMPLETE_ACTUAL.json',receipt)
 print(json.dumps(receipt))
except BaseException:
 value=dict(epoch=time.time(),passed=False,manifest_SHA=expected,error=traceback.format_exc(),deleted_files_before_error=deleted,deleted_count=len(deleted),do_not_rerun_delete_once_read_durable_journal_first=True)
 dump(root/'HUMAN_AUTHORIZED_DELETE_ORIGINAL_ERROR_ACTUAL.json',value);print(json.dumps(value));raise
finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
'''

def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

if __name__=='__main__':
 c=None
 try:
  manifest=json.loads(P.read_bytes());assert manifest['candidate_full_SHA_and_predelete_identity_verified']
  expected=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
  save('EXACT_OLD_INTERMEDIATE_DELETE_APPLY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_source_transport=True,manifest_path=str(P),manifest_SHA=expected,exact_authorization='大量老旧远古训练轨迹可以删除了',one_new_scope_no_recursive_delete=True))
  program=CODE.replace('manifest=MANIFEST;expected=EXPECTED;', 'manifest=json.loads('+repr(json.dumps(manifest))+');expected='+repr(expected)+';')
  c=a.t.connect();v=a.code(c,a.t.PY,program,timeout=300)
  save('SOURCE210_HUMAN_AUTHORIZED_OLD_INTERMEDIATE_TRAJECTORY_DELETION_ACTUAL.json',v)
  assert v['passed']
  print(json.dumps({k:v[k] for k in ('passed','deleted_count','deleted_apparent_bytes','deleted_allocated_bytes','filesystem_before','filesystem_after','protected_other_files_metadata_exact_unchanged','protected_file_count','all_selected_deleted_paths_absent')}),flush=True)
 except BaseException:
  save('LEGACY_DELETE_APPLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),outcome_if_transport_error_unknown_read_remote_journal_no_replay=True));raise
 finally:a.t.close(c)
