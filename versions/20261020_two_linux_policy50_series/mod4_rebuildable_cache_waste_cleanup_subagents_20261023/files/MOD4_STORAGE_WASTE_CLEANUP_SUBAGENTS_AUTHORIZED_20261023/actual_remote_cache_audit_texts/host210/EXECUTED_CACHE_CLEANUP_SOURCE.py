
from pathlib import Path
import fcntl,hashlib,json,os,shutil,stat,time,traceback,urllib.parse
B=Path(v['audit_root']);assert not B.exists();assert B.parent.resolve()==B.parent;B.mkdir()
def put(n,val):
 with (B/n).open('x',encoding='utf8') as f:json.dump(val,f,ensure_ascii=False,indent=2)
def meta(s):return dict(bytes=s.st_size,allocated_bytes=s.st_blocks*512,device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid,mtime_ns=s.st_mtime_ns,mode=stat.S_IMODE(s.st_mode))
def identity(s):return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_nlink,s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))
def expected(r):return (r['device'],r['inode'],r['bytes'],r['mtime_ns'],r['nlink'],r['uid'],r['gid'],int(r['mode'],0) if isinstance(r['mode'],str) else r['mode'])
assert all(Path(x).resolve()==Path(x) for x in v['roots'])
before={x:shutil.disk_usage(x)._asdict() for x in v['disk_paths']};registry={};checked=[];valid=[]
for root,kind in v['roots'].items():
 root=Path(root);assert root.is_dir() and not root.is_symlink()
 if kind=='conda_download_archive':
  u=root/'urls.txt';registry[str(root)]={Path(urllib.parse.urlsplit(line).path).name for line in u.read_text('utf8',errors='replace').splitlines()} if u.is_file() else set()
for row in v['files']:
 p=Path(row['path']);root=Path(row['cache_root']);reason=None;current=None
 try:
  assert str(root) in v['roots'] and p.is_relative_to(root) and p.resolve()==p and p!=root
  s=p.lstat();current=meta(s);assert stat.S_ISREG(s.st_mode) and not stat.S_ISLNK(s.st_mode)
  assert identity(s)==expected(row) and s.st_uid==os.getuid() and s.st_nlink==1 and time.time()-s.st_mtime>86400
  if row['kind']=='conda_download_archive':assert p.parent==root and p.name.endswith(('.conda','.tar.bz2')) and p.name in registry[str(root)]
  else:assert row['kind']=='pip_http_or_wheel_cache' and p.relative_to(root).parts[0] in ('http','http-v2','wheels')
  valid.append(row)
 except BaseException as e:reason=repr(e)
 checked.append(dict(row=row,fresh_stat=current,eligible=reason is None,skip_reason=reason))
put('FULL_EXACT_INTENT_BEFORE_ANY_UNLINK.json',dict(epoch=time.time(),explicit_human_waste_cleanup_authorized=True,cache_only=True,roots=v['roots'],source_manifest_SHA=v['manifest_SHA'],all_selected_freshstat=checked,before_disks=before,protected_unique_models_raw_sources_errors_logs_environments_budget_and_training_untouched=True))
(B/'EXECUTED_CACHE_CLEANUP_SOURCE.py').write_text(v['source_code'],encoding='utf8')
removed=[];skipped=[];errors=[]
for i,item in enumerate(checked):
 row=item['row'];p=Path(row['path']);fd=None;receipt=dict(epoch=time.time(),index=i,path=str(p),expected=row,removed=False)
 try:
  if not item['eligible']:receipt.update(result='SKIPPED_PREFLIGHT',reason=item['skip_reason']);skipped.append(str(p))
  else:
   fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0));fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   s=os.fstat(fd);assert identity(s)==expected(row) and identity(p.lstat())==expected(row) and p.resolve()==p
   p.unlink();receipt.update(result='REMOVED_REBUILDABLE_CACHE',removed=True,actual_before_unlink=meta(s),path_absent_after=not p.exists());assert receipt['path_absent_after'];removed.append(dict(path=str(p),bytes=s.st_size,allocated_bytes=s.st_blocks*512,device=s.st_dev))
 except BaseException as e:receipt.update(result='SKIPPED_OR_ERROR_NO_RETRY',error=repr(e));errors.append(dict(path=str(p),error=repr(e)))
 finally:
  if fd is not None:os.close(fd)
 put('ACTION_'+str(i).zfill(5)+'.json',receipt)
after={x:shutil.disk_usage(x)._asdict() for x in v['disk_paths']}
complete=dict(epoch=time.time(),passed=True,cache_only=True,selected_count=len(checked),removed_count=len(removed),removed_logical_bytes=sum(x['bytes'] for x in removed),removed_allocated_bytes_before=sum(x['allocated_bytes'] for x in removed),removed_by_device={str(dev):sum(x['bytes'] for x in removed if x['device']==dev) for dev in {x['device'] for x in removed}},skipped_preflight=len(skipped),errors=errors,before_disks=before,after_disks=after,free_snapshot_deltas={x:after[x]['free']-before[x]['free'] for x in before},free_delta_is_whole_filesystem_snapshot_not_exclusive_causation=True,no_model_raw_FINAL_source_error_log_installed_environment_GPU_signal_or_budget_access=True)
put('COMPLETE_ACTUAL.json',complete)
print(json.dumps(complete,ensure_ascii=False))
