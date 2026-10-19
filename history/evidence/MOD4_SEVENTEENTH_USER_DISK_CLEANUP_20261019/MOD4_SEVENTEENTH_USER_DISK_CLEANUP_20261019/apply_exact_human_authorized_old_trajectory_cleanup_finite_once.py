"""Delete only the inspected, authorized old binary-output list; preserve all text/models."""
from pathlib import Path
import getpass,hashlib,json,os,re,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
sys.path.insert(0,str(W/'MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019'))
import deploy_three_next_closed_source_hours_once as d
AUDIT='/home/lc01/Zonglin Li/zonglin2/audit/USER_OLD_TRAJECTORY_CLEANUP_20261019'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
PREP=r'''
from pathlib import Path
import json,sys
B=Path('/home/lc01/Zonglin Li/zonglin2');p=Path(sys.argv[1]);assert B.resolve()==B and p==B/'audit/USER_OLD_TRAJECTORY_CLEANUP_20261019' and p.resolve()==p and not p.exists();p.mkdir();print(json.dumps(dict(new_cleanup_audit=str(p),no_old_file_deleted=True)))
'''
APPLY=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,re,shutil,stat,sys,time
B=Path('/home/lc01/Zonglin Li/zonglin2');A=B/'audit/USER_OLD_TRAJECTORY_CLEANUP_20261019';planp=A/'EXACT_PLAN.json';expected=sys.argv[1];raw=planp.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;v=json.loads(raw)
assert v['human_latest_authorization']=='你去吧老旧的轨迹数据，回放，残缺检查点都给删除释放空间' and v['actual_finite_transport_returned'] and not v['errors']
rows=v['candidates'];assert len(rows)==782 and v['candidate_count']==782 and len({x['path'] for x in rows})==782
roots={x['root']:x for x in v['roots']};held=[];deleted=[];start=time.monotonic()
for name in ('three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock','three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock','finite_environment_validation.lock'):
 f=(B/'state'/name).open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held.append(f)
try:
 for root,proof in roots.items():
  p=Path(root);m=re.fullmatch(r'T3sf(\d*)_1910v\d+',p.parent.name);assert p.resolve()==p and p.is_relative_to(B/'tasks') and p.name in ('h1','recovery') and m and (int(m[1]) if m[1] else 1)<16
  for name in ('exit','terminal'):assert hashlib.sha256(Path(proof[name]['path']).read_bytes()).hexdigest()==proof[name]['SHA']
 for proc in psutil.process_iter(['pid','cmdline']):
  try:
   if proc.pid!=os.getpid():assert not any(any(a.startswith(root+'/') for root in roots) for a in proc.info['cmdline'] or [])
  except psutil.Error:pass
 def validate(x):
  p=Path(x['path']);root=Path(x['root']);assert str(root) in roots and p.resolve()==p and p.is_relative_to(root/'job0/production') and not p.is_symlink()
  # The inspected plan contains only these producer-indexed trajectories.
  assert x['category']=='old_control_trajectory_npz' and p.parent==root/'job0/production/control_prefix_raw' and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
  assert str(p) not in roots[str(root)]['protected_complete_checkpoint_paths'] and re.fullmatch('[0-9a-f]{64}',x['producer_SHA'])
  s=p.lstat();assert stat.S_ISREG(s.st_mode)
  for field,attr in [('bytes','st_size'),('device','st_dev'),('inode','st_ino'),('mtime_ns','st_mtime_ns'),('links','st_nlink')]:assert getattr(s,attr)==x[field]
  return p
 for x in rows:validate(x)
 before=shutil.disk_usage(B).free
 intent=dict(epoch=time.time(),authorization=v['human_latest_authorization'],plan_SHA=expected,exact_binary_files=len(rows),candidate_logical_bytes=sum(x['bytes'] for x in rows),latest16_complete_models_runtime_reset_banks_text_reports_and_locks_preserved=True,one_exact_list_only_no_recursive_delete=True)
 with (A/'DELETE_INTENT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(intent,f,indent=2);f.flush();os.fsync(f.fileno())
 with (A/'DELETE_JOURNAL_ACTUAL.jsonl').open('x',encoding='utf8') as journal:
  for i,x in enumerate(rows):
   if time.monotonic()-start>240:raise TimeoutError('Bounded exact-list deletion exceeded240s; retain actual journal, do not replay once')
   p=validate(x);journal.write(json.dumps(dict(index=i,phase='before_unlink',row=x))+'\n');journal.flush();os.fsync(journal.fileno())
   os.unlink(p);assert not p.exists();row=dict(index=i,**x,actual_deleted=True,actual_path_absent=True);deleted.append(row);journal.write(json.dumps(dict(index=i,phase='after_unlink',row=row))+'\n');journal.flush();os.fsync(journal.fileno())
 after=shutil.disk_usage(B).free
 out=dict(epoch=time.time(),actual_deleted=deleted,actual_deleted_count=len(deleted),actual_deleted_logical_bytes=sum(x['bytes'] for x in deleted),durable_free_before=before,durable_free_after=after,actual_observed_free_delta=after-before,observed_delta_may_include_other_filesystem_activity=True,all_current_file_metadata_matched_plan=True,producer_SHA_retained_not_claimed_newly_rehashed=True,latest_completed16_all_complete_models_source_runtime_reset_banks_text_reports_and_lock_paths_retained=True,partial_checkpoint_and_replay_candidates_found=0,no_GPU_Task_canonical_account_environment_or_other_job_change=True)
 with (A/'DELETE_COMPLETE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
 print(json.dumps(out))
finally:
 for f in held:fcntl.flock(f,fcntl.LOCK_UN);f.close()
'''
def main():
 assert not (R/'EXPLICIT_OLD_RAW_DELETE_STARTED_ACTUAL.json').exists()
 p=R/'EXPLICIT_OLD_TRAJECTORY_AND_PARTIAL_CLEANUP_PLAN_ACTUAL.json';raw=p.read_bytes();v=json.loads(raw);assert v['candidate_count']==782 and not v['errors'] and all(x['category']=='old_control_trajectory_npz' for x in v['candidates'])
 put('EXPLICIT_OLD_RAW_DELETE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,exact_plan=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),human_authorization=v['human_latest_authorization'],actual_alive_finite_only_exclusive_all_transport=True,old_installer_backup_stopped_not_resumed=True))
 pw=getpass.getpass('72 exact authorized old trajectory list deletion (hidden): ');c=None;sf=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);put('EXPLICIT_OLD_RAW_NEW_AUDIT_DIRECTORY_ACTUAL.json',d.a.code(c,d.a.PY,PREP,AUDIT,timeout=45))
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  with sf.open(AUDIT+'/EXACT_PLAN.json','wx') as f:f.write(raw);f.flush()
  sf.close();sf=None;out=d.a.code(c,d.a.PY,APPLY,hashlib.sha256(raw).hexdigest(),timeout=270);put('EXPLICIT_OLD_TRAJECTORY_DELETION_COMPLETE_ACTUAL.json',out)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
 put('EXPLICIT_OLD_RAW_DELETE_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True,actual_deleted_count=out['actual_deleted_count'],actual_deleted_logical_bytes=out['actual_deleted_logical_bytes'],free_after_bytes=out['durable_free_after'],no_training_or_account_change=True))
 print(json.dumps(dict(deleted_files=out['actual_deleted_count'],deleted_GiB=out['actual_deleted_logical_bytes']/1024**3,free_GiB_after=out['durable_free_after']/1024**3,finite_returned=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('EXPLICIT_OLD_RAW_DELETE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_remote_exact_audit_and_journal_before_only_missing_followup=True,no_old_once_or_blind_delete_replay=True));raise
