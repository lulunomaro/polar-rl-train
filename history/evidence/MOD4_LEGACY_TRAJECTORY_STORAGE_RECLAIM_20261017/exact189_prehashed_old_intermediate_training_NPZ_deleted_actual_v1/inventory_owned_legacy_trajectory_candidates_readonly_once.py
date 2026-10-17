"""One source210 metadata-only candidate inventory following explicit human cleanup authorization."""
from pathlib import Path
import os,sys,time,json,traceback
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(B.parent/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017'))
import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
CODE=r'''
from pathlib import Path
import os,time,json,re,shutil,collections,psutil
D=Path('/mnt/mod4_linux_durable_20261013');H=Path('/home/egde/rl_candidates');begin=time.time()
assert D.is_dir() and H.is_dir();roots=[]
for base in (D,H):
 for p in base.iterdir():
  if not p.is_dir() or p.is_symlink():continue
  if p.name.startswith('MOD4_') or (base==D and p.name in ('T3_1710v1','T3_1710v2','H125_1710n1','N72_1710v2','C275_1610v2')):roots.append(p)
rows=[];ext=collections.defaultdict(lambda:dict(files=0,bytes=0,allocated=0));groups=collections.defaultdict(lambda:dict(files=0,bytes=0,allocated=0));errors=[]
for root in sorted(roots):
 for folder,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[n for n in dirs if not Path(folder,n).is_symlink()]
  for name in files:
   p=Path(folder,name)
   try:
    st=p.lstat()
    if not p.is_file() or p.is_symlink():continue
    suffix=p.suffix.lower();alloc=st.st_blocks*512;ext[suffix]['files']+=1;ext[suffix]['bytes']+=st.st_size;ext[suffix]['allocated']+=alloc
    rel=p.relative_to(root);group=str(root.joinpath(*rel.parts[:min(3,len(rel.parts)-1)]));g=groups[group];g['files']+=1;g['bytes']+=st.st_size;g['allocated']+=alloc
    if st.st_size>=16*1024*1024 and suffix not in ('.pt','.pth','.onnx','.usd','.usda','.usdc','.zip','.gz','.tar','.mp4','.dmp'):
     rows.append(dict(path=str(p),root=str(root),bytes=st.st_size,allocated_bytes=alloc,mtime=st.st_mtime,dev=st.st_dev,inode=st.st_ino,nlink=st.st_nlink,suffix=suffix))
   except OSError as e:errors.append(dict(path=str(p),error=str(e)))
processes=[]
for q in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if q.pid==os.getpid():continue
  owned_args=[s for s in q.info.get('cmdline') or [] if any(s.startswith(str(base)+'/') for base in (D,H))]
  cwd=q.info.get('cwd') or ''
  if owned_args or any(cwd.startswith(str(base)+'/') for base in (D,H)):
   processes.append(dict(pid=q.pid,creation=q.info['create_time'],cwd=cwd,owned_path_arguments_only=owned_args))
 except psutil.Error:pass
print(json.dumps(dict(epoch_begin=begin,epoch_end=time.time(),host='10.24.4.210 original single4090',read_only_inventory=True,explicit_human_authorization='大量老旧远古训练轨迹可以删除了',roots=[str(p) for p in roots],potential_large_nonmodel_files=sorted(rows,key=lambda r:r['allocated_bytes'],reverse=True),extensions=ext,largest_groups=sorted([dict(path=p,**v) for p,v in groups.items()],key=lambda r:r['allocated'],reverse=True)[:70],own_process_path_metadata=processes,errors=errors,filesystem_usage={str(p):dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in (D,H)},no_delete_move_training_GPU_ledger_or_mount_change=True)))
'''

def save(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)

if __name__=='__main__':
 c=None
 try:
  save('LEGACY_TRAJECTORY_READONLY_INVENTORY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_source_transport=True,max_seconds=300))
  c=a.t.connect();v=a.code(c,a.t.PY,CODE,timeout=300)
  save('SOURCE210_OWN_LEGACY_TRAJECTORY_CANDIDATE_INVENTORY_READONLY_ACTUAL.json',v)
  print(json.dumps(dict(potential_file_count=len(v['potential_large_nonmodel_files']),potential_bytes=sum(r['bytes'] for r in v['potential_large_nonmodel_files']),largest=v['potential_large_nonmodel_files'][:32],largest_groups=v['largest_groups'][:24],filesystem_usage=v['filesystem_usage'],own_processes=v['own_process_path_metadata'],errors=v['errors'])),flush=True)
 except BaseException:
  save('LEGACY_TRAJECTORY_INVENTORY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_deletion_attempted=True));raise
 finally:a.t.close(c)
