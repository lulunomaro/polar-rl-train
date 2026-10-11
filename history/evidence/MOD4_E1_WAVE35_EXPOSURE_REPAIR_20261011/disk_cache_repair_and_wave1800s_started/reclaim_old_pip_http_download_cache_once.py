"""Reclaim old reproducible pip HTTP downloads only; never touch trials/envs/weights."""
from wave_io import *
def main():
 assert not (R/'WAVE_CACHE_RECLAIM_ACTUAL.json').exists()
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import json,time,hashlib,os,shutil
cache=(Path.home()/'.cache/pip').resolve();assert str(cache)=='/home/egde/.cache/pip'
report=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/WAVE35_PIP_HTTP_CACHE_RECLAIM_ACTUAL.json');assert not report.exists()
def installers():
 found=[]
 for proc in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   a=proc.read_bytes().split(b'\0');names=[Path(x.decode(errors='replace')).name for x in a[:3]]
   if any(x in ('pip','pip3','conda') for x in names) or any(a[k:k+2]==[b'-m',b'pip'] for k in range(len(a)-1)):found.append(int(proc.parent.name))
  except OSError:pass
 return found
assert not installers();before=shutil.disk_usage(cache).free;cut=time.time()-7*86400;rows=[]
for directory in ('http','http-v2'):
 root=cache/directory
 if not root.is_dir():continue
 for parent,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[x for x in dirs if not (Path(parent)/x).is_symlink()]
  for name in files:
   p=Path(parent)/name
   if p.is_symlink():continue
   target=p.resolve();assert target.is_relative_to(root.resolve());s=p.stat()
   if s.st_mtime>=cut:continue
   h=hashlib.sha256()
   with p.open('rb') as f:
    for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
   rows.append(dict(path=str(target),bytes=s.st_size,sha256=h.hexdigest(),mtime=s.st_mtime,reproducible_pip_HTTP_download_not_trial_or_installed_dependency=True))
assert rows and not installers()
started=report.with_name('WAVE35_PIP_HTTP_CACHE_RECLAIM_STARTED.json');assert not started.exists()
started.write_text(json.dumps(dict(epoch=time.time(),files=rows,reason='system_disk_only_2_5GB_before_new_Wave_complete_save',only_old7day_HTTP_cache=True),indent=2))
removed=[]
for row in rows:
 p=Path(row['path']);assert p.resolve().is_relative_to(cache) and not p.is_symlink();s=p.stat();assert s.st_size==row['bytes'] and s.st_mtime==row['mtime'];p.unlink();removed.append(row)
v=dict(epoch=time.time(),completed=True,free_before_bytes=before,free_after_bytes=shutil.disk_usage(cache).free,removed_cached_download_bytes=sum(x['bytes'] for x in removed),removed_cached_download_files=len(removed),files=removed,
 no_trial_raw_weight_source_installed_dependency_or_canonical_touched=True,no_GPU_or_budget_write=True)
report.write_text(json.dumps(v,indent=2));print(json.dumps(v))
''');save('WAVE_CACHE_RECLAIM_ACTUAL.json',v);print(json.dumps({k:val for k,val in v.items() if k!='files'}))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_CACHE_RECLAIM_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_trial_or_weight_cleanup_requested=True));raise
