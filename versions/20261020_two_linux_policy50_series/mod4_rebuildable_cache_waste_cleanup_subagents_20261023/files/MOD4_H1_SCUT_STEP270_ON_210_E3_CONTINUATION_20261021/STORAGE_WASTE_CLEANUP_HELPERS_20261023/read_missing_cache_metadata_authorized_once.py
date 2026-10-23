from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;S=W/'MOD4_STORAGE_WASTE_CLEANUP_SUBAGENTS_AUTHORIZED_20261023';R=S/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE210=r'''
from pathlib import Path
import json,os,stat,shutil,time,urllib.parse
roots=[Path('/mnt/mod4_linux_durable_20261013/anaconda/pkgs'),Path('/home/egde/anaconda3/pkgs')];out=[];errors=[]
for root in roots:
 row=dict(path=str(root),exists=root.exists(),files=[],excluded=[],only_direct_download_archives=True);out.append(row)
 if not root.exists():continue
 assert root.resolve()==root and not root.is_symlink();known=set();urls=root/'urls.txt'
 row['urls_txt_exists']=urls.is_file()
 if urls.is_file():
  for line in urls.read_text('utf8',errors='replace').splitlines():known.add(Path(urllib.parse.urlsplit(line).path).name)
 for p in sorted(root.iterdir()):
  if not (p.name.endswith('.conda') or p.name.endswith('.tar.bz2')):continue
  try:
   s=p.lstat();v=dict(path=str(p),bytes=s.st_size,allocated_bytes=s.st_blocks*512,device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid,mode=stat.S_IMODE(s.st_mode),mtime_ns=s.st_mtime_ns,regular=stat.S_ISREG(s.st_mode),symlink=stat.S_ISLNK(s.st_mode),listed_in_cache_urls_by_basename=p.name in known,age_seconds=time.time()-s.st_mtime)
   row['files'].append(v)
  except Exception as e:errors.append(dict(path=str(p),error=repr(e)))
 row['disk_free']=shutil.disk_usage(root).free
print(json.dumps(dict(epoch=time.time(),groups=out,errors=errors,no_content_hash_or_model_or_process_or_budget_access=True,only_cache_urls_basename_boolean_no_URL_or_credentials_output=True,no_delete=True)))
'''
def main():
 put('MISSING_CACHE_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),read_only=True,old_full_audits_not_repeated=True,one_connection_at_a_time=True))
 c=d.t.connect()
 try:v=d.code(c,d.t.PY,CODE210,{},timeout=35)
 finally:c.close()
 put('HOST210_DIRECT_CONDA_ARCHIVE_METADATA_ACTUAL.json',v)
 source=R/'host72_agent/host72_missing_cache_downloads_metadata_remote.py';code=source.read_text('utf8');ast.parse(code)
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:v=d.code(c,d.PY72,code,{},timeout=70)
 finally:c.close()
 put('HOST72_MISSING_CACHE_DOWNLOADS_METADATA_ACTUAL.json',dict(epoch=time.time(),source_SHA=hashlib.sha256(code.encode()).hexdigest(),remote=v,actual_call_returned=True))
 put('MISSING_CACHE_METADATA_ALL_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,all_connections_closed=True,no_deletion_or_training_change=True))
 print(json.dumps(dict(passed=True,metadata_only=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('MISSING_CACHE_METADATA_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_repeat_once=True));raise
