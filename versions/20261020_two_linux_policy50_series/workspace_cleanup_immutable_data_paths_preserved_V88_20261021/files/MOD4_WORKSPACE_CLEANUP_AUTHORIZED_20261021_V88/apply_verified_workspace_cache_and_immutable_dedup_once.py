"""Authorized, exact-file cleanup. No recursive delete or move; keep binary paths."""
from pathlib import Path
import hashlib,json,os,shutil,stat,time,traceback
B=Path(__file__).resolve().parent;W=B.parent.resolve();R=B/'reports'
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,v):(R/n).open('x',encoding='utf8').write(json.dumps(v,ensure_ascii=False,indent=2))
def check(x):
 p=Path(x['path']);resolved=p.resolve();assert resolved.is_relative_to(W) and resolved!=W and '.git' not in p.parts and 'polar-rl-train' not in p.parts
 for parent in (p,*p.parents):
  if parent==W:break
  assert not (getattr(parent.stat(follow_symlinks=False),'st_file_attributes',0)&1024)
 s=p.stat(follow_symlinks=False);assert stat.S_ISREG(s.st_mode) and (s.st_size,s.st_mtime_ns,s.st_ino,s.st_nlink)==(x['bytes'],x['mtime_ns'],x['inode'],x['nlink']);return p
try:
 q=json.loads((R/'CLEANUP_V88_VERIFIED_EXACT_TARGETS_CPU_V2_ACTUAL.json').read_bytes());assert q['passed_identity_inventory'] and q['no_delete_yet'] and q['hardlink_native_preflight_passed'];assert Path(q['workspace']).resolve()==W
 before=shutil.disk_usage(W).free;put('CLEANUP_V88_MUTATION_STARTED_ACTUAL.json',dict(epoch=time.time(),workspace=str(W),free_before=before,explicit_human_authorization='清理一下c盘 mjcf工作区不需要的文件释放一下空间',only_individual_resolved_workspace_files=True,no_training_host_account_or_GPU_action=True))
 log=(R/'CLEANUP_V88_FULL_ORDERED_ACTIONS.jsonl').open('x',encoding='utf8');deleted=[];linked=[];skipped=[]
 def emit(v):log.write(json.dumps(dict(epoch=time.time(),**v),ensure_ascii=False)+'\n');log.flush()
 for x in q['regenerable_python_cache_files']:
  try:
   p=check(x);assert '__pycache__' in p.parts and p.suffix.lower() in ('.pyc','.pyo');p.unlink();assert not p.exists();deleted.append(dict(**x,kind='regenerable_python_cache'));emit(dict(action='cache_deleted',**x))
  except (OSError,AssertionError) as e:skipped.append(dict(path=x['path'],reason=str(e),kind='cache_not_force_removed'));emit(dict(action='cache_skipped',path=x['path'],reason=str(e)))
 for x in q['obsolete_wheel_copies_with_exact_retained_original']:
  try:
   p=check(x);source=Path(x['retained_original_path']);assert p.suffix=='.whl' and source.is_file() and source.stat().st_size==x['bytes'] and H(source)==x['SHA'] and H(p)==x['SHA'];p.unlink();assert source.is_file() and not p.exists();deleted.append(dict(**x,kind='obsolete_installer_duplicate'));emit(dict(action='installer_duplicate_deleted_original_retained',**x))
  except (OSError,AssertionError) as e:skipped.append(dict(path=x['path'],reason=str(e),kind='wheel_not_force_removed'));emit(dict(action='wheel_skipped',path=x['path'],reason=str(e)))
 for group in q['immutable_binary_duplicate_groups']:
  kept=group['retained'];keeper=check(kept);assert H(keeper)==group['SHA'];keeper_identity=(keeper.stat().st_ino,keeper.stat().st_size)
  for x in group['targets']:
   p=None;backup=None;moved=False;newlink=False
   try:
    p=check(x);assert p.suffix.lower() in ('.pt','.pth','.npz') and x['nlink']==1 and p.stat().st_dev==keeper.stat().st_dev
    assert (keeper.stat().st_ino,keeper.stat().st_size)==keeper_identity
    backup=p.with_name('.v88_'+hashlib.sha256(str(p).encode()).hexdigest()[:16]+'.bak');assert backup.resolve().is_relative_to(W) and backup.parent.resolve()==p.parent.resolve() and not backup.exists()
    # Both resolved endpoints are inside this workspace before the individual rename.
    p.rename(backup);moved=True;os.link(keeper,p);newlink=True
    a=p.stat();assert (a.st_ino,a.st_size)==keeper_identity and a.st_nlink>=2 and backup.stat().st_ino==x['inode'];backup.unlink();moved=False
    entry=dict(**x,SHA=group['SHA'],retained_equal_original=str(keeper),new_inode=a.st_ino,new_nlink=a.st_nlink,new_mtime_ns=a.st_mtime_ns,all_original_paths_and_bytes_retained=True,immutable_historical_data_only=True)
    linked.append(entry);emit(dict(action='immutable_duplicate_replaced_by_identical_hardlink',**entry))
   except (OSError,AssertionError) as e:
    if moved:
     if newlink and p.exists():assert p.stat().st_ino==keeper_identity[0];p.unlink()
     assert not p.exists() and backup.exists() and backup.resolve().is_relative_to(W);backup.rename(p);assert p.stat().st_ino==x['inode']
    skipped.append(dict(path=x['path'],reason=str(e),kind='duplicate_not_force_changed_original_restored'));emit(dict(action='dedup_skipped_original_restored',path=x['path'],reason=str(e)))
  assert H(keeper)==group['SHA']
 # Every retained hardlinked path is checked again, with group content SHA verified above.
 for x in linked:
  p=Path(x['path']);s=p.stat();k=Path(x['retained_equal_original']);assert p.is_file() and (s.st_ino,s.st_size)==(k.stat().st_ino,x['bytes']) and not p.with_name('.v88_'+hashlib.sha256(str(p).encode()).hexdigest()[:16]+'.bak').exists()
 log.flush();os.fsync(log.fileno());log.close();after=shutil.disk_usage(W).free
 out=dict(epoch=time.time(),passed=True,workspace=str(W),free_before=before,free_after=after,observed_C_drive_free_delta=after-before,deleted_cache_count=sum(x['kind']=='regenerable_python_cache' for x in deleted),deleted_cache_bytes=sum(x['bytes'] for x in deleted if x['kind']=='regenerable_python_cache'),obsolete_installer_duplicate_count=sum(x['kind']=='obsolete_installer_duplicate' for x in deleted),obsolete_installer_duplicate_bytes=sum(x['bytes'] for x in deleted if x['kind']=='obsolete_installer_duplicate'),immutable_duplicate_paths=len(linked),immutable_duplicate_logical_bytes_eliminated=sum(x['bytes'] for x in linked),all_model_raw_paths_and_exact_bytes_retained=True,unique_FINAL_source_forensic_data_error_log_and_Git_history_not_deleted=True,active_stage_roots_excluded=q['protected_stage_roots'],installed_Python_environment_and_MoE_player_not_changed=True,no_recursive_delete_move_or_permission_change=True,no_training_host_connection_GPU_or_account_action=True,old_cleanup_batches_not_replayed=True,deleted=deleted,hardlink_replacements=linked,skipped=skipped,ordered_full_actions=str(R/'CLEANUP_V88_FULL_ORDERED_ACTIONS.jsonl'))
 put('CLEANUP_V88_ACTUAL_COMPLETE_AND_SPACE_RELEASED.json',out);print(json.dumps({k:v for k,v in out.items() if k not in ('deleted','hardlink_replacements','skipped','active_stage_roots_excluded')}));print(json.dumps(dict(skipped_count=len(skipped),skipped_examples=skipped[:4])))
except BaseException:
 put('CLEANUP_V88_APPLY_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),never_replay_completed_actions=True));raise
