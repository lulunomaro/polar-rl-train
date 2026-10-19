"""Delete only the frozen exact file list, entirely inside this workspace; no recursion."""
from pathlib import Path
import hashlib,json,os,shutil,stat,time,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf').resolve();B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def check_path(p):
 assert p.is_absolute() and p.resolve(strict=True).is_relative_to(W) and p.resolve(strict=True)!=W
 rel=p.relative_to(W);assert rel.parts[0].startswith('MOD4_') and rel.parts[0] not in (B.name,'MOD4_LOCAL_MUJOCO_DRIVE_20261008');assert not any(x.lower() in ('.git','.venv','env','runtime','payload','source','source_snapshot','site-packages') for x in rel.parts)
 for parent in [p,*p.parents]:
  assert parent==W or parent.is_relative_to(W)
  s=parent.stat(follow_symlinks=False);assert not parent.is_symlink() and not getattr(s,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT
  if parent==W:break
 assert p.is_file() and not p.is_dir();return p.stat()
def main():
 plan_path=R/'EXACT_WORKSPACE_OBSOLETE_REPLAY_AND_REDUNDANT_ZIP_CLEANUP_PLAN_ACTUAL.json';raw=plan_path.read_bytes();plan=json.loads(raw);assert plan['workspace']==str(W) and plan['total_files']==173 and not (R/'EXACT_LOCAL_DELETION_STARTED_ACTUAL.json').exists();selected=plan['selected'];assert len({x['path'].casefold() for x in selected})==len(selected)
 # Validate the whole list before deleting the first file.
 for row in selected:
  p=Path(row['path']);s=check_path(p);assert s.st_size==row['bytes'] and s.st_mtime_ns==row['mtime_ns']
  if row['category']=='old_closed_frozen_replay_array':
   assert p.name in ('retention_full_control_substep_actual.npz','route_raw.npz');assert hashlib.sha256(Path(row['producer_report']).read_bytes()).hexdigest()==row['producer_report_SHA'];assert hashlib.sha256(Path(row['numerical_summary']).read_bytes()).hexdigest()==row['numerical_summary_SHA']
  else:
   assert row['category']=='redundant_zip_all_extracted_members_verified' and p.name=='TESTED_MINIMAL_NATIVE311_WHEELHOUSE_20261013.zip';assert all(Path(m['kept_file']).is_file() and Path(m['kept_file']).stat().st_size==m['bytes'] for m in row['all_extracted_members'])
 before=shutil.disk_usage(W);put('EXACT_LOCAL_DELETION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),workspace=str(W),plan_SHA=hashlib.sha256(raw).hexdigest(),files=len(selected),logical_bytes=plan['total_logical_bytes'],disk_before=dict(zip(('total','used','free'),before)),explicit_human_authorization=plan['human_request'],all_paths_absolute_resolved_inside_workspace_no_reparse=True,no_recursive_delete_or_remote_action=True))
 done=[];failures=[]
 for row in selected:
  p=Path(row['path'])
  try:
   s=check_path(p);assert s.st_size==row['bytes'] and s.st_mtime_ns==row['mtime_ns'];os.unlink(p);assert not p.exists();rec=dict(path=str(p),bytes=row['bytes'],category=row['category'],producer_SHA=row['producer'].get('SHA',row['producer'].get('sha256')) if 'producer' in row else None,deleted=True,epoch=time.time());done.append(rec)
   with (R/'EXACT_LOCAL_DELETION_APPEND_ONLY_JOURNAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(rec)+'\n');f.flush();os.fsync(f.fileno())
  except BaseException:failures.append(dict(path=str(p),error=traceback.format_exc()));break
 after=shutil.disk_usage(W);out=dict(epoch=time.time(),workspace=str(W),plan_SHA=hashlib.sha256(raw).hexdigest(),completed_all=not failures and len(done)==len(selected),deleted_files=len(done),deleted_logical_bytes=sum(x['bytes'] for x in done),deleted=done,failures=failures,disk_before=dict(zip(('total','used','free'),before)),disk_after=dict(zip(('total','used','free'),after)),actual_free_delta_bytes=after.free-before.free,free_delta_may_include_concurrent_filesystem_changes=True,all_producer_reports_and_summaries_retained=all(Path(x['path']).is_file() and hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['SHA'] for x in plan['producer_reports_and_summaries_retained']),all_model_PT_runtime_reset_bank_player_Git_current_stages_retained=True,no_complete_or_partial_checkpoint_deleted=True,no_remote_or_training_or_budget_or_peer_action=True,no_recursive_directory_deletion=True)
 put('EXPLICIT_LOCAL_WORKSPACE_CLEANUP_COMPLETE_ACTUAL.json',out);assert out['completed_all'] and out['all_producer_reports_and_summaries_retained'];print(json.dumps(dict(completed_all=True,deleted_files=len(done),deleted_logical_GiB=out['deleted_logical_bytes']/1024**3,actual_free_delta_GiB=out['actual_free_delta_bytes']/1024**3,current_free_GiB=after.free/1024**3,original_reports_retained=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_EXACT_DELETION_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay=True));raise
