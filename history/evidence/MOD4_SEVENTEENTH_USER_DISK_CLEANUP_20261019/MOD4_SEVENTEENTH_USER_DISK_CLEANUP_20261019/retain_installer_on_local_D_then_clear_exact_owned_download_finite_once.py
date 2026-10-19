"""User-authorized cleanup of one installer download, only after durable exact backup."""
from pathlib import Path
import getpass,hashlib,json,os,shutil,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
sys.path.insert(0,str(W/'MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019'))
import deploy_three_next_closed_source_hours_once as d
SOURCE='/home/lc01/Zonglin Li/zonglin2/downloads/source4090_environment_and_lab_v2_linuxpaths.tar.gz'
BACKUP=Path('D:/MOD4_RETAINED_INSTALLERS_20261019/source4090_environment_and_lab_v2_linuxpaths.tar.gz')
SIZE=20988865638;SHA='77b823a63570fd5f0acfa7b1ce935cd61b914e9a5727e1e3333b39a95be7e184'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
META=r'''
from pathlib import Path
import json,os,shutil,stat,time
B=Path('/home/lc01/Zonglin Li/zonglin2');p=B/'downloads/source4090_environment_and_lab_v2_linuxpaths.tar.gz'
assert B.resolve()==B and p.resolve()==p and p.is_file() and not p.is_symlink()
s=p.stat();assert stat.S_ISREG(s.st_mode) and s.st_size==20988865638
print(json.dumps(dict(epoch=time.time(),path=str(p),bytes=s.st_size,device=s.st_dev,inode=s.st_ino,mtime_ns=s.st_mtime_ns,links=s.st_nlink,durable_free=shutil.disk_usage(B).free,only_exact_installer_download_candidate=True)))
'''
CLEAR=r'''
from pathlib import Path
import fcntl,json,os,shutil,stat,sys,time
B=Path('/home/lc01/Zonglin Li/zonglin2');p=B/'downloads/source4090_environment_and_lab_v2_linuxpaths.tar.gz';v=json.loads(sys.argv[1]);original=v['remote_before'];backup=v['local_backup']
assert B.resolve()==B and p.resolve()==p and not p.is_symlink() and str(p)==original['path']
assert backup['bytes']==20988865638 and backup['SHA']=='77b823a63570fd5f0acfa7b1ce935cd61b914e9a5727e1e3333b39a95be7e184' and backup['actual_local_durable_readback_SHA_verified']
intent=B/'audit/USER_AUTHORIZED_INSTALLER_DOWNLOAD_CLEANUP_20261019_INTENT.json';actual=B/'audit/USER_AUTHORIZED_INSTALLER_DOWNLOAD_CLEANUP_20261019_ACTUAL.json';assert not intent.exists() and not actual.exists()
fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
try:
 fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);s=os.fstat(fd);current=os.stat(p,follow_symlinks=False)
 for name,attr in [('bytes','st_size'),('device','st_dev'),('inode','st_ino'),('mtime_ns','st_mtime_ns')]:assert getattr(s,attr)==original[name] and getattr(current,attr)==original[name]
 assert stat.S_ISREG(s.st_mode) and s.st_nlink==original['links']
 before=shutil.disk_usage(B).free
 with intent.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),human_authorization='你去清空--- in response to72 disk capacity question',exact_source=original,retained_exact_backup=backup,one_file_only_no_recursive_delete=True,no_environment_model_raw_trajectory_report_state_lock_or_other_job_change=True),f,indent=2);f.flush();os.fsync(f.fileno())
 parent=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:
  again=os.stat(p.name,dir_fd=parent,follow_symlinks=False);assert again.st_ino==s.st_ino and again.st_dev==s.st_dev and again.st_size==s.st_size and again.st_mtime_ns==s.st_mtime_ns
  os.unlink(p.name,dir_fd=parent);os.fsync(parent)
 finally:os.close(parent)
finally:os.close(fd)
after=shutil.disk_usage(B).free
out=dict(epoch=time.time(),deleted_only_exact_remote_installer_download=str(p),deleted_logical_bytes=20988865638,retained_exact_local_backup=backup,source_path_absent=not p.exists(),durable_free_before=before,durable_free_after=after,actual_observed_free_delta=after-before,observed_delta_may_include_other_filesystem_activity=True,no_recursive_delete_or_environment_model_raw_trajectory_report_state_lock_other_job_or_budget_change=True)
with actual.open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(out))
'''
def main():
 assert not (R/'USER_EXACT_INSTALLER_BACKUP_CLEANUP_STARTED_ACTUAL.json').exists()
 producer=Path(W/'MOD4_HOST72_ZONGLIN2_ENV_DEPLOY_20261015/reports/SOURCE4090_TO_ZONGLIN2_TRANSFER_V2_COMPLETE.json');original=json.loads(producer.read_bytes());assert original['archive']['bytes']==SIZE and original['archive']['sha256']==SHA and original['archive']['path']==SOURCE
 assert BACKUP.is_absolute() and str(BACKUP).startswith('D:') and shutil.disk_usage('D:/').free>SIZE+8*1024**3 and not BACKUP.exists()
 BACKUP.parent.mkdir(parents=True,exist_ok=True);part=BACKUP.with_suffix(BACKUP.suffix+'.partial');assert not part.exists()
 ci=subprocess.run(['powershell','-NoProfile','-Command','$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,ExecutablePath,CreationDate,CommandLine|ConvertTo-Json -Compress'],capture_output=True,text=True,encoding='utf8',check=True)
 put('USER_EXACT_INSTALLER_BACKUP_CLEANUP_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_local_CIM=json.loads(ci.stdout),source=SOURCE,backup=str(BACKUP),expected_bytes=SIZE,expected_SHA=SHA,original_producer_report=str(producer),original_producer_report_SHA=hashlib.sha256(producer.read_bytes()).hexdigest(),authorization='[REDACTED]',actual_alive_finite_only_exclusive_all_training_transports=True,no_delete_before_durable_full_backup_and_hash_readback=True))
 pw=getpass.getpass('72 exact installer backup then owned download cleanup (hidden): ');c=None;sf=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);before=d.a.code(c,d.a.PY,META,timeout=45);put('USER_EXACT_INSTALLER_REMOTE_BEFORE_BACKUP_ACTUAL.json',before)
  sf=c.open_sftp();sf.get_channel().settimeout(90);start=last=time.monotonic();h=hashlib.sha256();count=0
  with sf.open(SOURCE,'rb') as src,part.open('xb') as out:
   src.prefetch(file_size=SIZE,max_concurrent_requests=16)
   while True:
    if time.monotonic()-start>1500:raise TimeoutError('Bounded installer backup exceeded1500seconds; source retained and actual partial backup preserved')
    block=src.read(4*1024**2)
    if not block:break
    out.write(block);h.update(block);count+=len(block)
    if time.monotonic()-last>=20:
     row=dict(epoch=time.time(),phase='installer_backup_stream',bytes=count,expected_bytes=SIZE,elapsed_seconds=time.monotonic()-start,mean_MiB_s=count/(time.monotonic()-start)/1024**2)
     with (R/'USER_INSTALLER_BACKUP_PROGRESS_JOURNAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row)+'\n')
     print(json.dumps(row),flush=True);last=time.monotonic()
   out.flush();os.fsync(out.fileno())
  sf.close();sf=None;assert count==SIZE and part.stat().st_size==SIZE and h.hexdigest()==SHA
  actual=hashlib.sha256()
  with part.open('rb') as f:
   for block in iter(lambda:f.read(8*1024**2),b''):actual.update(block)
  assert actual.hexdigest()==SHA;part.replace(BACKUP)
  backup=dict(path=str(BACKUP),bytes=BACKUP.stat().st_size,SHA=actual.hexdigest(),actual_local_durable_readback_SHA_verified=True,original_archive_bytes_retained_not_reconstructed=True)
  put('USER_INSTALLER_FULL_DURABLE_LOCAL_BACKUP_ACTUAL.json',dict(epoch=time.time(),local_backup=backup,original_remote_before=before,source_original_producer_SHA_exact=True,elapsed_seconds=time.monotonic()-start,no_remote_deletion_before_this_verified_backup=True))
  out=d.a.code(c,d.a.PY,CLEAR,json.dumps(dict(remote_before=before,local_backup=backup)),timeout=90);put('USER_EXACT_REMOTE_INSTALLER_DOWNLOAD_CLEANUP_ACTUAL.json',out)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
 put('USER_EXACT_INSTALLER_BACKUP_CLEANUP_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True,retained_backup=backup,remote_cleanup=out,no_new_GPU_Task_native_or_account_change=True))
 print(json.dumps(dict(cleaned_only_one_installer_download=True,retained_backup=backup,free_GiB_after=out['durable_free_after']/1024**3,finite_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  part=BACKUP.with_suffix(BACKUP.suffix+'.partial')
  put('USER_INSTALLER_BACKUP_CLEANUP_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_backup=dict(path=str(part),bytes=part.stat().st_size) if part.exists() else None,complete_backup_exists=BACKUP.exists(),inspect_actual_original_backup_cleanup_receipts_before_any_missing_only_followup=True,no_automatic_delete_or_old_once_replay=True));raise
