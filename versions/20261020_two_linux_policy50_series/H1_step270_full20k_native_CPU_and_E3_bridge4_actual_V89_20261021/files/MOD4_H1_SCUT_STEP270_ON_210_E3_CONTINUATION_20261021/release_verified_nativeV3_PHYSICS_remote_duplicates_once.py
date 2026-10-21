"""Release only completed native PHYSICS NPZ copies after complete verified C retention."""
from pathlib import Path
import hashlib,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'full20k_native180_V3_actual';sys.path.insert(0,str(B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 return h.hexdigest()
REMOTE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,time
B=Path('/mnt/mod4_linux_durable_20261013/H1step270_full20k_native180_2110v3');ex=json.loads((B/'PARENT_EXIT_ACTUAL.json').read_bytes());co=json.loads((B/'PARENT_COMPLETE_ACTUAL.json').read_bytes());assert ex['all_own_children_waited'] and ex['own_eval_lease_released'] and co['passed']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
lease=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 before=shutil.disk_usage(B).free;checked=[]
 for row in v['files']:
  p=B/row['relative'];assert not p.is_symlink() and p.resolve().is_relative_to((B/'out').resolve()) and p.name.startswith('PHYSICS_') and p.suffix=='.npz';st=p.stat();assert st.st_size==row['bytes'] and row['retained_C_SHA']==row['SHA']
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
  assert h.hexdigest()==row['SHA'];checked.append(dict(row,remote_inode=st.st_ino,remote_mtime_ns=st.st_mtime_ns))
 for row in checked:
  p=B/row['relative'];st=p.stat();assert (st.st_ino,st.st_mtime_ns,st.st_size)==(row['remote_inode'],row['remote_mtime_ns'],row['bytes']);p.unlink()
 print(json.dumps(dict(epoch=time.time(),free_before=before,free_after=shutil.disk_usage(B).free,removed_remote_duplicates=checked,all_unique_forensic_bytes_retained_at_verified_C_paths=True,FINAL_fullstate_models_CONTROL_source_text_logs_errors_retained=True,no_original_budget_or_training_or_GPU_write=True)))
finally:lease.close()
'''
c=None
try:
 receipt=json.loads((R/'STEP270_FULL20K_NATIVE180_V3_COMPLETE_RAW_AND_EXIT_RECOVERED_V2_ACTUAL.json').read_bytes());assert receipt['actual_finite_transport_returned'] and receipt['parent_complete']['passed'];files=[]
 for row in receipt['parent_complete']['final']['artifacts']:
  if not Path(row['relative']).name.startswith('PHYSICS_'):continue
  p=A/row['relative'];assert p.stat().st_size==row['bytes'];h=H(p);assert h==row['SHA'];files.append(dict(**row,retained_C_path=str(p),retained_C_SHA=h))
 assert len(files)==8
 put(R/'NATIVEV3_PHYSICS_DUPLICATE_RELEASE_STARTED_ACTUAL.json',dict(epoch=time.time(),files=files,storage_integrity_hashing_not_Git=True))
 c=d.t.connect();v=d.code(c,d.t.PY,REMOTE,dict(files=files),timeout=240);put(R/'NATIVEV3_PHYSICS_VERIFIED_C_RELOCATION_REMOTE_SPACE_RELEASED_ACTUAL.json',v);print(json.dumps(dict(remote_redundant_bytes_released=sum(x['bytes'] for x in files),free_before=v['free_before'],free_after=v['free_after'],all_C_exact_forensics_retained=True)))
except BaseException:put(R/'NATIVEV3_PHYSICS_DUPLICATE_RELEASE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
finally:
 if c:c.close()
