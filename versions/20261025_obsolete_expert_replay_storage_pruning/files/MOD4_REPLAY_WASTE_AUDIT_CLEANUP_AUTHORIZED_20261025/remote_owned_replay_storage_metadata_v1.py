"""Bounded metadata-only project storage inventory; no replay/model contents."""
from pathlib import Path
import collections,hashlib,heapq,json,os,shutil,stat,time,traceback
start=time.monotonic();deadline=start+160;out=Path(v['out']);assert not out.exists();out.mkdir(parents=True)
roots=[Path(p) for p in v['roots']];errors=[];skips=[];groups=collections.defaultdict(lambda:collections.Counter());largest=[];disks=[];count=0;seen=set();total_allocated=0;complete=True
def put(name,value):
 with (out/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
put('EXECUTION_IDENTITY_AND_READONLY_SCOPE_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),roots=v['roots'],no_source_content_hash_or_delete=True,no_GPU_or_peer_process_query=True))
canonical=None
if v['host']=='210':
 p=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw);canonical=dict(SHA=hashlib.sha256(raw).hexdigest(),active_segment_present=c['active_segment'] is not None,authorized_training_seconds=c['authorized_training_seconds'],extension_count=len(c['budget_extensions']),remaining_snapshot=c['remaining_training_seconds'])
manifest=out/'ALL_OWNED_PROJECT_FILE_METADATA.jsonl'
with manifest.open('x',encoding='utf8') as output:
 for root in roots:
  if not root.exists():skips.append(dict(path=str(root),reason='missing_root'));continue
  st=root.lstat();assert root.resolve()==root and stat.S_ISDIR(st.st_mode) and not stat.S_ISLNK(st.st_mode)
  usage=shutil.disk_usage(root);disks.append(dict(path=str(root),device=st.st_dev,total=usage.total,used=usage.used,free=usage.free))
  stack=[root]
  while stack:
   if time.monotonic()>deadline:complete=False;skips.append(dict(path=str(root),reason='bounded160s_partial',pending=len(stack)));break
   folder=stack.pop()
   try:entries=list(os.scandir(folder))
   except OSError as e:errors.append(dict(path=str(folder),error=repr(e)));continue
   for entry in entries:
    p=Path(entry.path)
    try:
     s=entry.stat(follow_symlinks=False)
     if stat.S_ISLNK(s.st_mode):skips.append(dict(path=str(p),reason='symlink_no_traversal'));continue
     if stat.S_ISDIR(s.st_mode):
      if s.st_dev!=st.st_dev:skips.append(dict(path=str(p),reason='different_device_no_traversal'));continue
      if p.name in ['.git','envs','node_modules','site-packages','.venv','venv','compat']:skips.append(dict(path=str(p),reason='protected_installed_environment_or_repo'));continue
      stack.append(p);continue
     if not stat.S_ISREG(s.st_mode):continue
     rel=p.relative_to(root);ext=p.suffix.lower();parts=[a.lower() for a in p.parts];kind='text_source_or_other'
     if ext in ['.pt','.pth','.onnx']:kind='model_or_preupdate_metadata_only'
     elif ext in ['.npz','.npy','.mp4','.gif','.avi','.mkv']:kind='array_or_replay_candidate_only'
     elif ext in ['.zip','.zst','.whl','.conda','.gz','.bz2','.tar']:kind='archive_candidate_only'
     if any(a in ['cache','__pycache__','.cache','tmp','computecache'] for a in parts):kind='cache_or_temporary_candidate_only'
     if p.name.startswith('MOD4_RESET_COLLISION_BANK') or ext in ['.usd','.usda','.usdc','.stl','.obj']:kind='asset_or_reset_input_metadata_only'
     identity=(s.st_dev,s.st_ino);allocated=s.st_blocks*512;unique=allocated if identity not in seen else 0;seen.add(identity);total_allocated+=unique
     row=dict(path=str(p),bytes=s.st_size,allocated_bytes=allocated,device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,mtime_ns=s.st_mtime_ns,mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,root=str(root),relative=rel.as_posix(),kind=kind)
     output.write(json.dumps(row,ensure_ascii=False)+'\n');count+=1
     group=str(root)+'/'+('/'.join(rel.parts[:min(2,len(rel.parts)-1)]) if len(rel.parts)>1 else '[root_files]');groups[group]['files']+=1;groups[group]['bytes']+=s.st_size;groups[group]['unique_allocated_bytes']+=unique;groups[group][kind+'_bytes']+=s.st_size
     item=(s.st_size,str(p),row)
     if len(largest)<100:heapq.heappush(largest,item)
     elif item[:2]>largest[0][:2]:heapq.heapreplace(largest,item)
    except OSError as e:errors.append(dict(path=str(p),error=repr(e)))
  if not complete:break
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 return h.hexdigest()
result=dict(epoch=time.time(),host=v['host'],complete_within_explicit_roots=complete,elapsed_seconds=time.monotonic()-start,files=count,total_logical_bytes=sum(g['bytes'] for g in groups.values()),unique_allocated_bytes=total_allocated,filesystem_snapshots=disks,canonical_readonly_summary=canonical,groups=[dict(path=k,**g) for k,g in sorted(groups.items(),key=lambda r:r[1]['bytes'],reverse=True)],largest=[r[2] for r in sorted(largest,reverse=True)],errors=errors,skips=skips,metadata_artifact=dict(path=str(manifest),bytes=manifest.stat().st_size,SHA=digest(manifest)),source_code_SHA=hashlib.sha256(v['source_code'].encode()).hexdigest(),no_model_raw_content_hash_load_delete_move_or_training_GPU_peer_query=True)
put('COMPLETE_METADATA_READ_ONLY_ACTUAL.json',result)
print(json.dumps(result))
