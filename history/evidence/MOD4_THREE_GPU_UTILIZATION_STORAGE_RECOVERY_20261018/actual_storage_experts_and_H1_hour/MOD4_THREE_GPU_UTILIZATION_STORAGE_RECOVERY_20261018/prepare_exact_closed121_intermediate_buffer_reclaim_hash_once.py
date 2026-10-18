"""Hash a new exact list of obsolete closed121 intermediate training buffers."""
from inventory_current_owned210_storage_readonly_once import *
import re,hashlib
CODE=r'''
from pathlib import Path
import os,sys,json,time,hashlib,stat,psutil,shutil
plan=json.loads(sys.stdin.readline());D=Path('/mnt/mod4_linux_durable_20261013');B=Path(plan['old_root']);F=B/'job0/production/control_prefix_raw';assert D.is_mount() and B.resolve()==B and B.is_relative_to(D)
final=json.loads((B/'job0/production/FINAL.json').read_bytes());exit=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());assert final['passed'] and final['final']['updates']==121 and exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired']
index=json.loads((F/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());assert len(index['index'])==121;by={r['path']:r for r in index['index']}
def busy():
 result=[]
 for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
  try:
   if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in (p.info.get('cmdline') or [])+[p.info.get('cwd') or '']):result.append(p.pid)
  except psutil.Error:pass
 return result
assert not busy();rows=[]
for r in plan['delete_files']:
 p=Path(r['path']);assert p.parent==F and p.resolve()==p and not p.is_symlink() and p.name.startswith('control_prefix_') and p.suffix=='.npz'
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.getuid() and (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(r['dev'],r['inode'],r['bytes'],r['mtime_ns'])
 original=by[str(p)];assert original['bytes']==s.st_size;fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);h=hashlib.sha256()
 try:
  before=os.fstat(fd)
  with os.fdopen(fd,'rb',closefd=False) as f:
   for part in iter(lambda:f.read(8*1024**2),b''):h.update(part)
  after=os.fstat(fd);assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
 finally:os.close(fd)
 assert h.hexdigest()==original['SHA'];rows.append(dict(r,SHA=h.hexdigest(),original_control_index=original,actual_full_predelete_hash_matches_original_producer=True))
assert not busy();selected={r['path'] for r in rows};protected=[]
for folder,dirs,files in os.walk(B,followlinks=False):
 dirs[:]=[n for n in dirs if not Path(folder,n).is_symlink()]
 for n in files:
  p=Path(folder,n)
  if str(p) in selected or p.is_symlink():continue
  s=p.stat();protected.append(dict(path=str(p),dev=s.st_dev,inode=s.st_ino,bytes=s.st_size,mtime_ns=s.st_mtime_ns))
O=D/'MOD4_STORAGE_RECLAIM_1810B';O.mkdir();v=dict(epoch=time.time(),plan=plan,delete_files=rows,protected_other_files=protected,old_final=final,old_exit=exit,free_before=shutil.disk_usage(D).free,all_models_code_reports_first_last_milestones_retained=True,original_human_current_request=plan['human_request'],no_deletion_performed=True,no_global_FD_absence_claim=True)
p=O/'EXACT_PREHASHED_CLOSED121_INTERMEDIATE_BUFFER_DELETE_PLAN.json';p.write_text(json.dumps(v,indent=2));v['durable_plan_path']=str(p);v['durable_plan_SHA']=hashlib.sha256(p.read_bytes()).hexdigest();print(json.dumps(v))
'''
def main():
 inv=json.loads((R/'OWNED210_CURRENT_STORAGE_INVENTORY_READONLY_ACTUAL.json').read_bytes());old=json.loads((R/'OLD_CLOSED_H1_PREFIX_SOURCE_INDEX_READONLY_ACTUAL.json').read_bytes());assert not old['own_old_root_processes'];root=old['root'];folder=root+'/job0/production/control_prefix_raw/';items=[]
 for r in inv['large_files']:
  if not r['path'].startswith(folder):continue
  match=re.fullmatch(r'control_prefix_(\d+)\.npz',Path(r['path']).name)
  if match:items.append((int(match.group(1)),r))
 assert len(items)==121 and sorted(i for i,_ in items)==list(range(121));chosen=[]
 for i,r in sorted(items):
  if i in (0,1,119,120) or i%25==0:continue
  chosen.append(r)
  if sum(x['allocated_bytes'] for x in chosen)>=25*1024**3:break
 assert sum(r['allocated_bytes'] for r in chosen)>=25*1024**3
 plan=dict(epoch=time.time(),human_request='210主机我不是说了删除不需要的老旧数据了吗？还有我不是要求三张显卡都要运用上吗？',old_root=root,delete_files=chosen,scope='Only original-indexed intermediate .npz buffers from actual closed H1 update121; retain first2/last2/every25 milestone and every weight/source/report/other file',old189_cleanup_not_repeated=True,no_current_training_or_frozen_case_selected=True)
 save('EXACT_CLOSED121_OLD_BUFFER_NEW_CLEANUP_PLAN_BEFORE_HASH.json',plan);save('CLOSED121_PREDELETE_HASH_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transports=True));c=None
 try:
  c=a.t.connect();v=a.code(c,a.t.PY,CODE,stdin=json.dumps(plan)+'\n',timeout=900);save('CLOSED121_OLD_BUFFER_EXACT_PREDELETE_FULL_SHA_ACTUAL.json',v)
 finally:a.t.close(c)
 print(json.dumps(dict(files=len(v['delete_files']),reclaim_allocated=sum(r['allocated_bytes'] for r in v['delete_files']),original_producer_SHA_all_match=True,protected_files=len(v['protected_other_files']),durable_plan=v['durable_plan_path'],no_delete_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('CLOSED121_HASH_PLAN_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_delete=True));raise
