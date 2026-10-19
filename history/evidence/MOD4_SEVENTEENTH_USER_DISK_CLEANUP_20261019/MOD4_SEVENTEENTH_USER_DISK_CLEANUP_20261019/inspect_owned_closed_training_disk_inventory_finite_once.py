"""Read-only owned-tree size inventory before the user's requested disk cleanup."""
from pathlib import Path
import getpass,importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019'))
import deploy_three_next_closed_source_hours_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
READ=r'''
from pathlib import Path
import collections,json,os,psutil,shutil,stat,sys,time
base=Path('/home/lc01/Zonglin Li/zonglin2');roots=[Path(x) for x in json.loads(sys.argv[1])];start=time.monotonic();deadline=start+180
for root in roots:assert root.resolve().is_relative_to((base/'tasks').resolve()) and root.name in ('h1','recovery') and root.parent.name.startswith('T3sf')
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
active=[root for root in roots if any(any(a.startswith(str(root)+'/') for a in p['cmdline'] or []) for p in own)]
sizes=collections.defaultdict(int);counts=collections.defaultdict(int);compiled=[];large=[];errors=[];seen=set();pending=[base]
while pending:
 if time.monotonic()>deadline:raise TimeoutError('Bounded owned disk inventory exceeded180seconds')
 parent=pending.pop()
 try:
  for item in os.scandir(parent):
   p=Path(item.path)
   try:
    if item.is_symlink():continue
    if item.is_dir(follow_symlinks=False):pending.append(p);continue
    if not item.is_file(follow_symlinks=False):continue
    s=item.stat(follow_symlinks=False);rel=p.relative_to(base);group='/'.join(rel.parts[:min(2,len(rel.parts))]);sizes[group]+=s.st_size;counts[group]+=1
    row=dict(path=str(p),bytes=s.st_size,mtime_ns=s.st_mtime_ns,device=s.st_dev,inode=s.st_ino,links=s.st_nlink)
    if '__pycache__' in p.parts and p.suffix in ('.pyc','.pyo') and any(p.is_relative_to(root) for root in roots) and not any(p.is_relative_to(root) for root in active):compiled.append(row)
    if s.st_size>=50*1024**2:large.append(row)
   except (OSError,ValueError) as e:errors.append(dict(path=str(p),error=type(e).__name__+':'+str(e)))
 except OSError as e:errors.append(dict(path=str(parent),error=type(e).__name__+':'+str(e)))
large=sorted(large,key=lambda x:x['bytes'],reverse=True)[:120]
print(json.dumps(dict(epoch=time.time(),durable=dict(zip(('total','used','free'),shutil.disk_usage(base))),owned_base=str(base),exact_our_training_roots=[str(x) for x in roots],actual_own_processes_in_exact_roots=own,active_roots_excluded_from_candidates=[str(x) for x in active],groups=[dict(path=k,bytes=v,files=counts[k]) for k,v in sorted(sizes.items(),key=lambda x:x[1],reverse=True)],disposable_compiled_cache_files=compiled,disposable_compiled_cache_total_bytes=sum(x['bytes'] for x in compiled),largest_files_stat_only_not_deletion_candidates=large,errors=errors,elapsed_seconds=time.monotonic()-start,read_only_no_delete_move_hash_old_PT_raw_GPU_Task_or_account_change=True)))
'''
def main():
 assert not (R/'OWNED_DISK_INVENTORY_STARTED_ACTUAL.json').exists()
 roots=[];sources=[]
 for p in sorted(W.glob('MOD4_SCUT_FUDAN_*_HOUR_20261019/reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json')):
  v=json.loads(p.read_bytes())
  for key in ('h1','recovery'):
   root=v['roots'][key]
   if root not in roots:roots.append(root)
  sources.append(str(p))
 assert any('T3sf16_1910v21/h1' in x for x in roots)
 put('OWNED_DISK_INVENTORY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,authorization='[REDACTED]',read_only_inventory_before_exact_safe_cleanup=True,exact_root_sources=sources,actual_alive_finite_only_owns_all_transport=True))
 pw=getpass.getpass('72 owned disk read-only inventory (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;c.get_transport().set_keepalive(15);out=d.a.code(c,d.a.PY,READ,json.dumps(roots),timeout=210)
 finally:
  pw=None
  if c:c.close()
 out['actual_finite_transport_returned']=True;put('OWNED_CLOSED_TRAINING_DISK_INVENTORY_ACTUAL.json',out)
 print(json.dumps(dict(free_GiB=out['durable']['free']/1024**3,compiled_cache_GiB=out['disposable_compiled_cache_total_bytes']/1024**3,candidate_files=len(out['disposable_compiled_cache_files']),groups=out['groups'][:24],errors=len(out['errors']),own_live_roots=out['active_roots_excluded_from_candidates'])))
if __name__=='__main__':
 try:main()
 except BaseException:put('OWNED_DISK_INVENTORY_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_cleanup_or_GPU_or_account_change=True));raise
