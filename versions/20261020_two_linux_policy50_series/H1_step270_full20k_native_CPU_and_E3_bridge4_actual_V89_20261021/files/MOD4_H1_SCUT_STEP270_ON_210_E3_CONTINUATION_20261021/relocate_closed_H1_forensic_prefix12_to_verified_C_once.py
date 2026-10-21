"""Preserve closed forensic NPZ bytes on writable C: before releasing old D: copies."""
from pathlib import Path
import hashlib,json,shutil,sys,time,traceback

B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';NAME=Path(__file__).stem
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()

READ=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil
old=Path('/mnt/mod4_linux_durable_20261013/T3_1710v1/h1');root=old/'job0/production/control_prefix_raw'
ex=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());assert ex['actual_all_own_children_waited'] and ex['validation_fcntl_released_if_acquired']
for p in psutil.process_iter(['pid','cmdline']):
 try:assert p.pid==os.getpid() or not any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or [])
 except psutil.NoSuchProcess:pass
lease=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 rows=[]
 for row in v['files']:
  p=Path(row['path']);assert not p.is_symlink() and p.resolve().is_relative_to(root.resolve()) and p.suffix=='.npz' and p.name.startswith('control_prefix_');st=p.stat();assert st.st_size==row['bytes'] and st.st_nlink==1
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
  rows.append(dict(path=str(p),bytes=st.st_size,SHA=h.hexdigest(),mtime_ns=st.st_mtime_ns,inode=st.st_ino))
 print(json.dumps(dict(epoch=__import__('time').time(),files=rows,actual_closed_original_h1_out=True,own_private_lease_checked=True,free_before=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,no_account_or_GPU_write=True)))
finally:lease.close()
'''
DELETE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,time
old=Path('/mnt/mod4_linux_durable_20261013/T3_1710v1/h1');root=old/'job0/production/control_prefix_raw';assert json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
for p in psutil.process_iter(['pid','cmdline']):
 try:assert p.pid==os.getpid() or not any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or [])
 except psutil.NoSuchProcess:pass
lease=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 for row in v['files']:
  p=Path(row['path']);assert not p.is_symlink() and p.resolve().is_relative_to(root.resolve()) and p.suffix=='.npz';st=p.stat();assert (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1) and row['verified_C_SHA']==row['SHA'] and row['verified_C_bytes']==row['bytes']
 # All exact resolved targets verified, then unlink only the verified redundant copies.
 removed=[]
 for row in v['files']:
  p=Path(row['path']);p.unlink();removed.append(dict(**row,old_remote_copy_unlinked=True,full_forensic_original_retained_at_verified_C_path=row['local_path']))
 print(json.dumps(dict(epoch=time.time(),removed=removed,free_after=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,no_FINAL_source_text_error_or_log_deleted=True,no_budget_or_training_or_GPU_write=True)))
finally:lease.close()
'''

client=None;copied=[]
try:
    inventory=json.loads((W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/reports/COHORT50_ACTUAL_OWNER_BYTES_AND_OLD_RAW_STORAGE_ACTUAL.json').read_bytes())
    group=next(g for g in inventory['old_storage_groups'] if g['root']=='/mnt/mod4_linux_durable_20261013/T3_1710v1')
    targets=[dict(path=p,bytes=n) for n,p in group['largest_files'][:12]];assert len(targets)==12
    total=sum(x['bytes'] for x in targets);assert shutil.disk_usage('C:/').free>total+8*1024**3
    dest=B/'relocated_forensic_originals/T3_1710v1_control_prefix_batch12';assert not dest.exists();dest.mkdir(parents=True)
    put(R/(NAME+'_STARTED_ACTUAL.json'),dict(epoch=time.time(),exact_targets=targets,total=total,storage_integrity_hashing_not_Git_archival=True));start=time.monotonic()
    client=d.t.connect();fresh=d.code(client,d.t.PY,READ,dict(files=targets),timeout=240)
    put(R/'H1_CLOSED_PREFIX12_RELOCATION_FRESH_SOURCE_SHA_ACTUAL.json',fresh)
    sftp=client.open_sftp();sftp.get_channel().settimeout(90)
    try:
        for row in fresh['files']:
            assert time.monotonic()-start<800 and shutil.disk_usage('C:/').free>row['bytes']+8*1024**3
            p=dest/Path(row['path']).name;part=p.with_suffix('.npz.partial');assert not p.exists() and not part.exists();sftp.get(row['path'],str(part));assert part.stat().st_size==row['bytes'];h=sha(part);assert h==row['SHA'];part.rename(p)
            copied.append(dict(**row,local_path=str(p),verified_C_SHA=h,verified_C_bytes=p.stat().st_size));put(dest/(p.name+'.verified_receipt.json'),copied[-1])
    finally:sftp.close()
    assert len(copied)==12 and all(Path(x['local_path']).stat().st_size==x['bytes'] for x in copied)
    result=d.code(client,d.t.PY,DELETE,dict(files=copied),timeout=90);result.update(source_fresh=fresh,files=copied,total_forensic_bytes_preserved=total,all_C_full_SHA_verified_before_any_remote_unlink=True,C_free_after=shutil.disk_usage('C:/').free,transport_finite_elapsed_seconds=time.monotonic()-start)
    put(R/'H1_CLOSED_PREFIX12_FORENSICS_VERIFIED_RELOCATION_ACTUAL.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('removed','source_fresh','files')}))
except BaseException:
    put(R/(NAME+'_ORIGINAL_ERROR_ACTUAL.json'),dict(epoch=time.time(),error=traceback.format_exc(),verified_local_prefix=copied,no_replay=True,remote_copy_unlink_requires_actual_return_and_fresh_missing_only_helper=True));raise
finally:
    if client:client.close()
