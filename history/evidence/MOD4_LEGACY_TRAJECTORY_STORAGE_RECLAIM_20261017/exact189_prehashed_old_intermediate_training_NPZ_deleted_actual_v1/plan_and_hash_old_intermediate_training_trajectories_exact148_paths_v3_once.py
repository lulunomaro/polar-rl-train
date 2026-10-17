"""Prepare an exact authorized file list and obtain pre-deletion hashes; never deletes."""
from pathlib import Path,PurePosixPath
from datetime import datetime
import os,sys,time,json,traceback,collections,re,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
sys.path.insert(0,str(W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017'))
import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
INV=R/'SOURCE210_OWN_LEGACY_TRAJECTORY_CANDIDATE_INVENTORY_READONLY_ACTUAL.json'
CUTOFF=datetime.fromisoformat('2026-10-16T00:00:00+08:00').timestamp()
CODE=r'''
from pathlib import Path
import os,sys,time,json,hashlib,stat,psutil,shutil
plan=PLAN;begin=time.time();items=plan['delete_files'];roots=sorted({r['root'] for r in items});assert items and len(items)<1000
def pathcheck(r):
 p=Path(r['path']);root=Path(r['root']);assert root.is_absolute() and p.is_absolute() and p.is_relative_to(root) and p.parent!=root
 assert root.parent in (Path('/mnt/mod4_linux_durable_20261013'),Path('/home/egde/rl_candidates')) and root.name.startswith('MOD4_')
 assert p.suffix=='.npz' and 'learning_logs' in p.parts and (p.name.startswith('S4_GATE_FULL_ROLLOUT_') or p.name.startswith('retention_prefix_'))
 assert p.resolve(strict=True)==p and root.resolve(strict=True)==root
 for v in (p,*p.parents):assert not v.is_symlink()
 st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_nlink==1
 assert st.st_dev==r['dev'] and st.st_ino==r['inode'] and st.st_size==r['bytes'] and st.st_mtime==r['mtime'] and st.st_mtime<plan['cutoff_epoch']
 return p,st
def busy():
 bad=[];paths={r['path'] for r in items}
 for q in psutil.process_iter(['pid','create_time','cmdline','cwd']):
  if q.pid==os.getpid():continue
  try:
   touched=[s for s in (q.info.get('cmdline') or [])+[q.info.get('cwd') or ''] if any(s==root or s.startswith(root+'/') for root in roots)]
   opened=[f.path for f in q.open_files() if f.path in paths]
   if touched or opened:bad.append(dict(pid=q.pid,creation=q.info['create_time'],owned_paths=touched,opened_candidates=opened))
  except psutil.NoSuchProcess:pass
  except psutil.AccessDenied:raise RuntimeError('Cannot audit another process file handles; reject cleanup')
 return bad
assert not busy();out=[]
for r in items:
 p,st=pathcheck(r);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);h=hashlib.sha256()
 try:
  before=os.fstat(fd)
  with os.fdopen(fd,'rb',closefd=False) as f:
   for data in iter(lambda:f.read(8*1024*1024),b''):h.update(data)
  after=os.fstat(fd);assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
 finally:os.close(fd)
 digest=h.hexdigest()
 if r.get('previous_archived_SHA'):assert digest==r['previous_archived_SHA']
 out.append(dict(r,SHA=digest,mtime_ns=after.st_mtime_ns,resolved_path=str(p.resolve(strict=True)),predelete_full_SHA_actually_read=True))
assert not busy();protected=[]
for root in roots:
 for folder,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[n for n in dirs if not Path(folder,n).is_symlink()]
  for name in files:
   p=Path(folder,name)
   if p.is_symlink() or str(p) in {r['path'] for r in items}:continue
   st=p.stat();protected.append(dict(path=str(p),bytes=st.st_size,mtime_ns=st.st_mtime_ns,inode=st.st_ino))
print(json.dumps(dict(epoch_begin=begin,epoch_end=time.time(),host='10.24.4.210',all_paths_resolved_within_explicit_owned_roots=True,no_symlink_or_hardlink_or_open_candidate=True,delete_files=out,protected_other_files_metadata=protected,protected_file_count=len(protected),candidate_full_SHA_and_predelete_identity_verified=True,no_delete_performed=True,no_GPU_training_ledger_signal_or_mount_action=True,filesystem_before={p:dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in ('/mnt/mod4_linux_durable_20261013','/home/egde/rl_candidates')})))
'''

def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def main():
 inv=json.loads(INV.read_bytes());assert not inv['errors'];items=inv['potential_large_nonmodel_files'];selected=[];keep=[]
 oldindex=W/'MOD4_S4_LINUX_LEARNER_FULLSTATE_ADMISSION_20261015/own_gate_closed_final_actual/1792026833033365300/learning_logs/S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json'
 original=json.loads(oldindex.read_bytes());index={r['path']:r for r in original['rows']};assert len(index)==148 and sorted(r['index'] for r in index.values())==list(range(148))
 s4=[r for r in items if re.fullmatch(r'S4_GATE_FULL_ROLLOUT_\d+\.npz',PurePosixPath(r['path']).name)]
 assert len(s4)==148 and {r['path'] for r in s4}==set(index)
 for r in s4:
  if r['path'] not in index:
   keep.append(dict(r,reason='Unindexed terminal raw sample retained; do not infer completed optimizer update'));continue
  row=index[r['path']];assert row['bytes']==r['bytes'] and row['optimizer_update_complete'];i=row['index']
  if i in (0,1,146,147):keep.append(dict(r,reason='Keep first two and last two original gate148 training samples'))
  else:selected.append(dict(r,reason='Old fully indexed and audited intermediate training buffer; source/checkpoints/reports/first-last samples retained',previous_archived_SHA=row['sha256'],original_rollout_index=i))
 folders=collections.defaultdict(list)
 for r in items:
  p=PurePosixPath(r['path']);root=PurePosixPath(r['root']);m=re.fullmatch(r'retention_prefix_(\d+)_(\d+)\.npz',p.name)
  if not m or 'learning_logs' not in p.parts or r['mtime']>=CUTOFF:continue
  date=re.search(r'(20\d{6})$',root.name)
  if not date or not ('20261009'<=date.group(1)<='20261015'):continue
  if any(re.search(r'failed|error|partial|preflight',part,re.I) for part in p.parts):continue
  folders[str(p.parent)].append((int(m.group(1)),int(m.group(2)),r))
 for folder,rr in folders.items():
  rr.sort(key=lambda x:(x[0],x[1]));
  for i,(_,__,r) in enumerate(rr):
   if len(rr)<3 or i in (0,len(rr)-1):keep.append(dict(r,reason='Keep per-run first and terminal retention sample; retain short/failure-only runs'))
   else:selected.append(dict(r,reason='Old middle retention training sample; first and terminal sample retained in same run'))
 assert len({r['path'] for r in selected})==len(selected) and all(r['mtime']<CUTOFF for r in selected)
 plan=dict(epoch=time.time(),explicit_human_authorization='大量老旧远古训练轨迹可以删除了',scope='Only single4090 source210 old intermediate .npz training buffers in explicitly listed owned learning_logs; no recursive directory deletion',cutoff_epoch=CUTOFF,cutoff_Beijing='2026-10-16T00:00:00+08:00',delete_files=sorted(selected,key=lambda r:r['path']),kept_boundary_samples=keep,delete_count=len(selected),expected_allocated_bytes=sum(r['allocated_bytes'] for r in selected),no_models_checkpoints_reports_code_assets_frozen_evaluation_raw_failure_prefixes_or_current_tasks_selected=True,original_S4_rollout_index=dict(path=str(oldindex),SHA=hashlib.sha256(oldindex.read_bytes()).hexdigest()),historical_raw_retention_exception_is_explicit_human_authorized_only_for_this_list=True,no_automatic_cleanup_policy=True)
 save('EXACT_OLD_INTERMEDIATE_TRAJECTORY_DELETE_PLAN_V3_BEFORE_ACTION.json',plan)
 save('OLD_INTERMEDIATE_TRAJECTORY_PREDELETE_HASH_READER_V3_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_source_transport=True,max_remote_seconds=900,no_delete_yet=True))
 c=None
 try:c=a.t.connect();v=a.code(c,a.t.PY,CODE.replace('plan=PLAN;','plan=json.loads('+repr(json.dumps(plan))+');'),timeout=900)
 finally:a.t.close(c)
 save('EXACT_OLD_INTERMEDIATE_TRAJECTORIES_PREDELETE_FULL_SHA_AND_PROTECTED_FILES_V3_ACTUAL.json',v)
 print(json.dumps(dict(delete_count=len(v['delete_files']),total_allocated=sum(r['allocated_bytes'] for r in v['delete_files']),by_filesystem={base:sum(r['allocated_bytes'] for r in v['delete_files'] if r['path'].startswith(base+'/')) for base in ('/mnt/mod4_linux_durable_20261013','/home/egde/rl_candidates')},protected_file_count=v['protected_file_count'],full_SHA_passed=v['candidate_full_SHA_and_predelete_identity_verified'],no_delete_yet=True)),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:
  save('OLD_INTERMEDIATE_PREDELETE_PLAN_HASH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_delete_performed_by_this_script=True));raise
