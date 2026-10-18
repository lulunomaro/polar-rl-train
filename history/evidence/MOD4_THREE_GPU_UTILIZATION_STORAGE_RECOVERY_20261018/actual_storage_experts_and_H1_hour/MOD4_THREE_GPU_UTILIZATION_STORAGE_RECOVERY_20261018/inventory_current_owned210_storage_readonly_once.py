"""New human-directed cleanup inventory, not a replay of the old189 deletion."""
from pathlib import Path
import sys,os,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True);W=B.parent
sys.path.insert(0,str(W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017'))
import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
CODE=r'''
from pathlib import Path
import os,time,json,shutil,collections,psutil,stat
D=Path('/mnt/mod4_linux_durable_20261013');H=Path('/home/egde/rl_candidates');assert D.is_mount();start=time.time();roots=[]
for base in (D,H):
 for p in base.iterdir():
  if p.is_dir() and not p.is_symlink() and (p.name.startswith('MOD4_') or (base==D and p.name.startswith(('T3_','H1','N72_','C275_')))):roots.append(p)
large=[];totals=[];errors=[]
for root in sorted(roots):
 total=0;alloc=0;count=0;ext=collections.defaultdict(lambda:dict(files=0,bytes=0,allocated=0))
 for folder,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[n for n in dirs if not Path(folder,n).is_symlink()]
  for name in files:
   p=Path(folder,name)
   try:
    s=p.lstat()
    if not stat.S_ISREG(s.st_mode) or p.is_symlink():continue
    size=s.st_size;allocated=s.st_blocks*512;count+=1;total+=size;alloc+=allocated;e=ext[p.suffix.lower()];e['files']+=1;e['bytes']+=size;e['allocated']+=allocated
    if size>=16*1024**2:large.append(dict(path=str(p),root=str(root),bytes=size,allocated_bytes=allocated,dev=s.st_dev,inode=s.st_ino,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,uid=s.st_uid,nlink=s.st_nlink))
   except OSError as e:errors.append(dict(path=str(p),error=str(e)))
 totals.append(dict(path=str(root),files=count,bytes=total,allocated=alloc,extensions=dict(ext)))
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid==os.getpid():continue
  info=p.info;args=[x for x in info.get('cmdline') or [] if x.startswith(str(D)+'/') or x.startswith(str(H)+'/')];cwd=info.get('cwd') or ''
  if args or cwd.startswith(str(D)+'/') or cwd.startswith(str(H)+'/'):own.append(dict(pid=p.pid,creation=info['create_time'],cwd=cwd,owned_path_arguments_only=args))
 except psutil.Error:pass
print(json.dumps(dict(epoch_begin=start,epoch_end=time.time(),human_request='210主机我不是说了删除不需要的老旧数据了吗？还有我不是要求三张显卡都要运用上吗？',roots=sorted(totals,key=lambda r:r['allocated'],reverse=True),large_files=sorted(large,key=lambda r:r['allocated_bytes'],reverse=True),filesystem={str(p):dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in (D,H)},own_processes=own,errors=errors,readonly=True,no_delete_or_GPU_runtime_budget_mutation=True)))
'''
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
if __name__=='__main__':
 c=None
 try:
  save('OWNED210_NEW_CLEANUP_INVENTORY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transports=True))
  c=a.t.connect();v=a.code(c,a.t.PY,CODE,timeout=240);save('OWNED210_CURRENT_STORAGE_INVENTORY_READONLY_ACTUAL.json',v)
  print(json.dumps(dict(top_roots=[{k:r[k] for k in ('path','files','bytes','allocated')} for r in v['roots'][:25]],largest=v['large_files'][:25],filesystems=v['filesystem'],own_processes=v['own_processes'],errors=v['errors'])),flush=True)
 except BaseException:save('OWNED210_INVENTORY_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_delete_or_GPU_mutation=True));raise
 finally:a.t.close(c)
