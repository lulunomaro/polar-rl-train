"""Bounded verified relocation of a NEW subset; only after bridge7 actual full closure."""
from pathlib import Path
import hashlib,json,re,shutil,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports';D=T/'relocated_forensic_originals/T3_1710v1_additional_after_bridge7'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 return h.hexdigest()
INVENTORY=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,re,shutil,time
old=Path('/mnt/mod4_linux_durable_20261013/T3_1710v1/h1');base=old/'job0/production/control_prefix_raw'
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(C.read_bytes())['active_segment'] is None
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
index=json.loads((base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());skip=set(v['skip']);out=[];total=0
for row in sorted(index['index'],key=lambda x:x['path']):
 p=Path(row['path'])
 if str(p) in skip or not p.exists():continue
 assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
 st=p.stat();assert st.st_size==row['bytes'] and st.st_nlink==1
 if total+st.st_size>v['max_bytes']:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 assert h.hexdigest()==row['SHA'];out.append(dict(path=str(p),bytes=st.st_size,SHA=row['SHA'],mtime_ns=st.st_mtime_ns,inode=st.st_ino));total+=st.st_size
assert out
print(json.dumps(dict(epoch=time.time(),files=out,total_bytes=total,free_before=shutil.disk_usage(old).free,actual_original_old_H1_allout_and_original_locks_free=True,no_GPU_or_account_write=True)))
'''
DELETE=r'''
from pathlib import Path
import fcntl,json,os,psutil,re,shutil,time
old=Path('/mnt/mod4_linux_durable_20261013/T3_1710v1/h1');base=old/'job0/production/control_prefix_raw'
assert json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(C.read_bytes())['active_segment'] is None
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
for row in v['files']:
 p=Path(row['path']);assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
 s=p.stat();assert (s.st_size,s.st_mtime_ns,s.st_ino,s.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1) and row['verified_C_SHA']==row['SHA'] and row['verified_C_bytes']==row['bytes']
before=shutil.disk_usage(old).free
for row in v['files']:Path(row['path']).unlink()
print(json.dumps(dict(epoch=time.time(),removed_only_verified_duplicate_NPZ=len(v['files']),bytes=sum(x['bytes'] for x in v['files']),free_before=before,free_after=shutil.disk_usage(old).free,FINAL_models_sources_logs_errors_budget_untouched=True)))
'''
def main():
 proof=read(T/'E3_bridge_continuation_V7/reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
 assert not D.exists();D.mkdir(parents=True);skip=[x['path'] for x in read(R/'H1_CLOSED_PREFIX12_FORENSICS_VERIFIED_RELOCATION_ACTUAL.json')['removed']]
 limit=min(12*1024**3,shutil.disk_usage(T).free-9*1024**3);assert limit>0
 put('ADDITIONAL_CLOSED_H1_FORENSICS_RELOCATION_STARTED_ACTUAL.json',dict(epoch=time.time(),max_bytes=limit,skip_consumed_paths=skip,not_a_new_training_admission_threshold=True,no_51GB_bulk_copy=True))
 c=None;saved=[];start=time.monotonic()
 try:
  c=d.t.connect();fresh=d.code(c,d.t.PY,INVENTORY,dict(skip=skip,max_bytes=limit),timeout=150);put('ADDITIONAL_CLOSED_H1_FORENSICS_FRESH_SOURCE_SHA_ACTUAL.json',fresh)
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in fresh['files']:
    assert time.monotonic()-start<600 and shutil.disk_usage(T).free>row['bytes']+8*1024**3
    p=D/Path(row['path']).name;part=p.with_suffix('.npz.partial');assert p.resolve().is_relative_to(D.resolve()) and not p.exists() and not part.exists()
    sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'];part.replace(p)
    saved.append(dict(row,local_path=str(p),verified_C_SHA=row['SHA'],verified_C_bytes=p.stat().st_size))
    with p.with_suffix('.verified.json').open('x',encoding='utf8') as f:json.dump(saved[-1],f,indent=2)
  finally:sf.close()
  result=d.code(c,d.t.PY,DELETE,dict(files=saved),timeout=60)
  put('ADDITIONAL_CLOSED_H1_FORENSICS_VERIFIED_C_RELOCATION_SPACE_RELEASED_ACTUAL.json',dict(epoch=time.time(),files=saved,source_fresh=fresh,actual=result,local_free_after=shutil.disk_usage(T).free,actual_elapsed_seconds=time.monotonic()-start,no_unique_forensic_contents_deleted=True,reason='preserve old full evidence while increasing writable headroom for authorized H1 learning; original admission disk25 and runtime disk8 guards unchanged'))
  print(json.dumps(dict(files=len(saved),actual=result,local_free_after=shutil.disk_usage(T).free)))
 except BaseException:
  put('ADDITIONAL_CLOSED_H1_FORENSICS_RELOCATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),verified_C_prefix=saved,do_not_rerun_once_missing_only_after_actual_return=True));raise
 finally:
  if c:c.close()
if __name__=='__main__':main()
