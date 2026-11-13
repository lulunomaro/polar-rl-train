"""Move the user's quiescent training experiments to the mounted Windows data volume."""
from pathlib import Path
import os,json,time,hashlib,subprocess,shutil,traceback,stat
SRC=Path('/home/egde/rl_candidates')
BASE=Path('/mnt/mod4_windows_data/MOD4_training_data')
DST=BASE/'rl_candidates'
BACKUP=Path('/home/egde/rl_candidates.linux_migration_20261113')
STATE=BASE/'migration_20261113'
STATE.mkdir(parents=True,exist_ok=True)
def put(name,data):
 p=STATE/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');t.replace(p)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def progress(phase,**extra):
 put('PROGRESS.json',dict(epoch=time.time(),phase=phase,source=str(SRC),destination=str(DST),**extra))
 print(phase,json.dumps(extra),flush=True)
def main():
 assert SRC.is_dir() and not SRC.is_symlink() and SRC.resolve()==SRC
 assert not DST.exists() and not BACKUP.exists()
 mount=subprocess.check_output(['findmnt','-n','-o','SOURCE,FSTYPE','-T',str(BASE)],text=True).strip()
 assert mount.split()[0]=='/dev/nvme0n1p5' and mount.split()[1]=='ntfs3',mount
 assert os.stat('/mnt/mod4_windows_data').st_dev!=os.stat('/').st_dev
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip()
 files=[];links=[];directories=[];bad=[];size=0
 for root,dirs,names in os.walk(SRC,followlinks=False):
  here=Path(root)
  for name in dirs+names:
   item=here/name;rel=item.relative_to(SRC)
   if any(c in name for c in '<>:"\\|?*') or name.endswith((' ','.')):bad.append(str(rel))
   if item.is_symlink():links.append((rel,os.readlink(item)))
   elif item.is_file():files.append((rel,item.stat().st_size));size+=item.stat().st_size
   elif item.is_dir():directories.append(rel)
   else:raise RuntimeError('Unexpected special file: '+str(item))
 before=dict(root_free=shutil.disk_usage('/').free,windows_free=shutil.disk_usage(BASE).free,files=len(files),links=len(links),directories=len(directories),logical_bytes=size,mount=mount)
 put('PREFLIGHT.json',dict(**before,invalid_windows_names=bad))
 assert not bad,'Windows-incompatible names; source preserved: '+str(bad[:8])
 assert before['windows_free']>size+2*1024**3
 probe=BASE/'.mod4_storage_link_probe';probe.symlink_to('link_target');assert probe.is_symlink() and os.readlink(probe)=='link_target';probe.unlink()
 progress('copying',**before)
 cmd=['rsync','-aH','--no-perms','--no-owner','--no-group','--info=progress2','--stats','--partial-dir=.rsync-partial',str(SRC)+'/',str(DST)+'/']
 with(STATE/'rsync.log').open('wb') as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('rsync failed '+str(result.returncode)+'; source preserved; see rsync.log')
 progress('verifying',files_total=len(files),logical_bytes=size)
 checked=0;verified_bytes=0;last=time.time()
 with(STATE/'VERIFIED_FILES.jsonl').open('w') as manifest:
  for rel,expected_size in files:
   a=SRC/rel;b=DST/rel
   assert a.is_file() and b.is_file() and not b.is_symlink() and a.stat().st_size==b.stat().st_size==expected_size,str(rel)
   sha=digest(a);assert sha==digest(b),'Content mismatch: '+str(rel)
   manifest.write(json.dumps(dict(path=str(rel),bytes=expected_size,sha256=sha))+'\n')
   checked+=1;verified_bytes+=expected_size
   if time.time()-last>=10:
    manifest.flush();progress('verifying',files_verified=checked,files_total=len(files),bytes_verified=verified_bytes,logical_bytes=size);last=time.time()
 for rel,target in links:assert (DST/rel).is_symlink() and os.readlink(DST/rel)==target,str(rel)
 for rel in directories:assert (DST/rel).is_dir(),str(rel)
 destination_files=[]
 for root,dirs,names in os.walk(DST,followlinks=False):
  for name in names:
   f=Path(root)/name
   if not f.is_symlink():destination_files.append(f.relative_to(DST))
 assert len(destination_files)==len(files),'Unexpected destination file count'
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip()
 put('VERIFICATION_COMPLETE.json',dict(epoch=time.time(),files=checked,logical_bytes=verified_bytes,symlinks=len(links),manifest_sha256=digest(STATE/'VERIFIED_FILES.jsonl'),source_unchanged=True))
 SRC.rename(BACKUP)
 try:SRC.symlink_to(DST,target_is_directory=True)
 except BaseException:BACKUP.rename(SRC);raise
 assert SRC.is_symlink() and SRC.resolve()==DST.resolve() and BACKUP.resolve()==BACKUP and BACKUP.parent==Path('/home/egde')
 progress('reclaiming_verified_linux_copy',backup=str(BACKUP),files_verified=checked,bytes_verified=verified_bytes)
 shutil.rmtree(BACKUP)
 after=dict(root_free=shutil.disk_usage('/').free,windows_free=shutil.disk_usage(BASE).free)
 result=dict(epoch=time.time(),status='complete',source=str(SRC),destination=str(DST),source_is_compatibility_symlink=True,files_verified=checked,symlinks_verified=len(links),logical_bytes_verified=verified_bytes,before=before,after=after,linux_free_gained_bytes=after['root_free']-before['root_free'],original_linux_copy_removed=True,manifest=str(STATE/'VERIFIED_FILES.jsonl'))
 put('COMPLETE.json',result);progress('complete',**after,linux_free_gained_bytes=result['linux_free_gained_bytes'])
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
