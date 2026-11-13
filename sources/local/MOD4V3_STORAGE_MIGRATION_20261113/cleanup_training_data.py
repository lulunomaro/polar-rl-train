from pathlib import Path
import os,json,hashlib,shutil,subprocess,time,traceback
ROOT=Path('/mnt/mod4_windows_data/MOD4_training_data/rl_candidates');STATE=ROOT.parent/'migration_20261113'
INDEX=json.loads((STATE/'GIT_ARCHIVE_INDEX.json').read_text());PLAN=json.loads((STATE/'ACTIVE_TRAINING_PLAN.json').read_text())
def put(name,data):(STATE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main():
 assert ROOT.resolve()==ROOT and ROOT.parent==Path('/mnt/mod4_windows_data/MOD4_training_data')
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip()
 current=(ROOT/'mod4v3_stairs_success_refresh_40m_20261113_r1').resolve();protected={};link_dirs=[];cache=[]
 def read_paths(v):
  if isinstance(v,dict):
   for x in v.values():read_paths(x)
  elif isinstance(v,list):
   for x in v:read_paths(x)
  elif isinstance(v,str) and v.startswith('/home/egde/rl_candidates/') and v.endswith(('.pt','.pth')):protected[Path(v).resolve()]='referenced by current training PLAN'
 read_paths(PLAN)
 for p in ROOT.rglob('*'):
  if p.is_symlink():
   if p.resolve().is_dir():link_dirs.append(p.resolve())
   else:protected[p.resolve()]='symlink target'
  if p.name=='DerivedDataCache' and p.is_dir() and p.parent.name=='kit_isolation' and p.resolve()==p and (p.parent.parent/'SAFE_CLOSED.json').exists():
   size=int(subprocess.check_output(['du','-sb',str(p)],text=True).split()[0]);cache.append(dict(path=str(p),bytes=size,reason='rebuildable DerivedDataCache of safely closed native job'))
 known={};sizes=set()
 for row in INDEX['models']:known.setdefault(row['sha256'],row);sizes.add(row['bytes'])
 candidates=[];protected_count=0;checked=0
 for root,dirs,names in os.walk(ROOT,followlinks=False):
  here=Path(root)
  if here.is_relative_to(current):dirs[:]=[];continue
  for name in names:
   p=here/name
   if p.suffix not in {'.pt','.pth'} or p.is_symlink() or p.stat().st_size not in sizes:continue
   if p in protected or any(p.is_relative_to(d) for d in link_dirs):protected_count+=1;continue
   checked+=1;digest=sha(p)
   if digest in known:
    row=known[digest];candidates.append(dict(path=str(p),bytes=p.stat().st_size,sha256=digest,git_path=row['git_path'],git_blob=row['git_blob'],published_git_commit=INDEX['git_commit']))
 put('CLEANUP_PLAN.json',dict(epoch=time.time(),old_models=candidates,closed_derived_caches=cache,protected_current_run=str(current),other_protected_PT=protected_count,old_PT_hash_checked=checked))
 before=shutil.disk_usage(ROOT).free;removed=[]
 for row in candidates:
  p=Path(row['path']);assert p.resolve()==p and p.is_relative_to(ROOT) and not p.is_relative_to(current) and p not in protected and p.is_file()
  p.unlink();removed.append(row)
 for row in cache:
  p=Path(row['path']);assert p.resolve()==p and p.is_relative_to(ROOT) and p.name=='DerivedDataCache' and p.parent.name=='kit_isolation' and (p.parent.parent/'SAFE_CLOSED.json').exists();shutil.rmtree(p)
 result=dict(epoch=time.time(),status='complete',removed_old_PT=removed,old_PT_count=len(removed),old_PT_bytes=sum(x['bytes'] for x in removed),removed_closed_derived_caches=cache,derived_cache_bytes=sum(x['bytes'] for x in cache),windows_free_before=before,windows_free_after=shutil.disk_usage(ROOT).free,linux_free_after=shutil.disk_usage('/').free,protected_current_run=str(current),models_are_published_full_git_blobs=True)
 put('CLEANUP_COMPLETE.json',result);print(json.dumps({k:v for k,v in result.items() if k not in {'removed_old_PT','removed_closed_derived_caches'}}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('CLEANUP_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
