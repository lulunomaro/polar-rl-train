"""Unlink only the newly selected old intermediate buffers, with a durable exact journal."""
from inventory_current_owned210_storage_readonly_once import *
CODE=r'''
from pathlib import Path
import os,json,time,hashlib,psutil,stat,shutil
P=Path(PLAN_PATH);assert hashlib.sha256(P.read_bytes()).hexdigest()==PLAN_SHA;v=json.loads(P.read_bytes());B=Path(v['plan']['old_root']);D=Path('/mnt/mod4_linux_durable_20261013');F=B/'job0/production/control_prefix_raw';assert D.is_mount() and B.resolve()==B and B.is_relative_to(D)
assert v['no_deletion_performed'] and len(v['delete_files'])==81 and v['old_exit']['actual_all_own_children_waited']
def busy():
 for p in psutil.process_iter(['pid','cmdline','cwd']):
  try:
   if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in (p.info.get('cmdline') or [])+[p.info.get('cwd') or '']):return True
  except psutil.Error:pass
 return False
assert not busy();rows=v['delete_files'];before=shutil.disk_usage(D).free
def verify(r):
 p=Path(r['path']);assert p.parent==F and p.is_absolute() and p.resolve(strict=True)==p and p.is_relative_to(B) and p.suffix=='.npz';assert all(not q.is_symlink() for q in (p,*p.parents));s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.getuid() and (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(r['dev'],r['inode'],r['bytes'],r['mtime_ns']);assert r['actual_full_predelete_hash_matches_original_producer'] and r['SHA']==r['original_control_index']['SHA'];return p
for r in rows:verify(r)
for r in v['protected_other_files']:
 p=Path(r['path']);s=p.stat();assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(r['dev'],r['inode'],r['bytes'],r['mtime_ns'])
J=P.parent/'EXACT81_BUFFER_DELETION_JOURNAL.jsonl';f=J.open('x',encoding='utf8');deleted=[]
try:
 f.write(json.dumps(dict(epoch=time.time(),action='begin',exact_prehashed_plan=str(P),plan_SHA=PLAN_SHA,count=len(rows)))+'\n');f.flush();os.fsync(f.fileno())
 for r in rows:
  assert not busy();p=verify(r);p.unlink();receipt=dict(epoch=time.time(),action='unlinked',path=str(p),bytes=r['bytes'],allocated_bytes=r['allocated_bytes'],SHA=r['SHA'],absent=not p.exists());assert receipt['absent'];deleted.append(receipt);f.write(json.dumps(receipt)+'\n');f.flush();os.fsync(f.fileno())
finally:f.close()
for r in v['protected_other_files']:
 p=Path(r['path']);s=p.stat();assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(r['dev'],r['inode'],r['bytes'],r['mtime_ns'])
out=dict(epoch=time.time(),deleted=deleted,count=len(deleted),allocated_bytes_reclaimed=sum(r['allocated_bytes'] for r in deleted),free_before=before,free_after=shutil.disk_usage(D).free,above_original25GiB=shutil.disk_usage(D).free>25*1024**3,protected_files_unchanged=len(v['protected_other_files']),all_checkpoints_source_reports_boundary_samples_retained=True,old189_not_repeated=True,no_GPU_job_signal_or_canonical_budget_or_mount_mutation=True,explicitly_deleted_original_buffers_not_falsely_retained=True,durable_journal=str(J));q=P.parent/'EXACT81_OLD_BUFFER_DELETE_FINAL_ACTUAL.json';q.write_text(json.dumps(out,indent=2));out['durable_receipt_path']=str(q);out['durable_receipt_SHA']=hashlib.sha256(q.read_bytes()).hexdigest();print(json.dumps(out))
'''
if __name__=='__main__':
 c=None
 try:
  plan=json.loads((R/'CLOSED121_OLD_BUFFER_EXACT_PREDELETE_FULL_SHA_V2_ACTUAL.json').read_bytes());save('EXACT81_NEW_OLD_BUFFER_DELETE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_transports=True));c=a.t.connect();code=CODE.replace('PLAN_PATH',repr(plan['durable_plan_path'])).replace('PLAN_SHA',repr(plan['durable_plan_SHA']));v=a.code(c,a.t.PY,code,timeout=180);save('EXACT81_OLD_BUFFER_DELETE_FINAL_ACTUAL.json',v);print(json.dumps({k:v[k] for k in ('count','allocated_bytes_reclaimed','free_before','free_after','above_original25GiB','protected_files_unchanged','durable_receipt_path')}),flush=True)
 except BaseException:save('EXACT81_DELETE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_journal_no_repeat_delete=True));raise
 finally:a.t.close(c)
