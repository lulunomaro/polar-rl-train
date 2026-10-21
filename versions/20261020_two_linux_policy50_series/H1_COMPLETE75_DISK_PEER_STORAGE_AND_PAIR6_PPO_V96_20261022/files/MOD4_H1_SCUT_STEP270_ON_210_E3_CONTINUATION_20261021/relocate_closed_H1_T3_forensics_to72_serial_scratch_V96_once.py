"""Conditional bounded relocation after actual pair5 closure; no concurrent SSH.

Old, closed control NPZ evidence is retained with full SHA on 72. Local scratch
is bounded; source duplicates are removed only after target verification.
"""
from pathlib import Path
import hashlib,importlib.util,json,shutil,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports'
N=T/'H1_STEP270_E3_HEALTH_CLASSIFIER_PAIR_V5_20261022'
S=T/'relocation_scratch_T3_to72_V96'
TARGET='/home/lc01/Zonglin Li/zonglin2/forensic_originals/H1_T3_1710v1_verified_relocation_20261022_V96'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()

SOURCE_HEADER=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,re,shutil,time
old=Path('/mnt/mod4_linux_durable_20261013/T3_1710v1/h1');base=old/'job0/production/control_prefix_raw'
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
canonical_bytes=C.read_bytes();canonical=json.loads(canonical_bytes)
assert canonical['active_segment'] is None and canonical['authorized_training_seconds']==1548000 and len(canonical['budget_extensions'])==8
for root in (old,Path(v['current_h1']),Path(v['current_owner'])):
 if root==Path(v['current_owner']):assert json.loads((root/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
 else:assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
 assert not any(p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['h1_private_lock'])):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
'''
INVENTORY=SOURCE_HEADER+r'''
free=shutil.disk_usage(old).free;rows=[];total=0
if free<32*1024**3:
 index=json.loads((base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes())
 for row in sorted(index['index'],key=lambda x:x['path']):
  p=Path(row['path'])
  if not p.exists():continue
  assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
  s=p.stat();assert s.st_size==row['bytes'] and s.st_nlink==1
  if total+s.st_size>28*1024**3:continue
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
  assert h.hexdigest()==row['SHA']
  rows.append(dict(path=str(p),bytes=s.st_size,SHA=row['SHA'],mtime_ns=s.st_mtime_ns,inode=s.st_ino));total+=s.st_size
assert C.read_bytes()==canonical_bytes
print(json.dumps(dict(epoch=time.time(),files=rows,total_bytes=total,source_free_before=free,source_already_32GiB=free>=32*1024**3,canonical_SHA=hashlib.sha256(canonical_bytes).hexdigest(),all_current_and_old_ownout=True)))
'''
TARGET_PREP=r'''
from pathlib import Path
import json,shutil,time
B=Path(v['root']);parent=Path('/home/lc01/Zonglin Li/zonglin2')
assert B.resolve().is_relative_to(parent.resolve()) and not B.exists()
free=shutil.disk_usage(parent).free;assert free>v['total_bytes']+25*1024**3
B.mkdir(parents=True)
print(json.dumps(dict(epoch=time.time(),root=str(B),free_before=free,required_bytes=v['total_bytes'],no_GPU_or_training_or_account_writer=True)))
'''
TARGET_VERIFY=r'''
from pathlib import Path
import hashlib,json,time
B=Path(v['root']);out=[]
for row in v['files']:
 p=B/Path(row['path']).name;assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.stat().st_size==row['bytes']
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 assert h.hexdigest()==row['SHA'];out.append(dict(row,target_path=str(p),target_verified_SHA=h.hexdigest()))
receipt=B/('VERIFIED_BATCH_'+str(v['batch'])+'.json')
with receipt.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),files=out,original_source_evidence_contents_retained=True),f,indent=2)
print(json.dumps(dict(epoch=time.time(),files=out)))
'''
DELETE=SOURCE_HEADER+r'''
assert hashlib.sha256(canonical_bytes).hexdigest()==v['canonical_SHA']
for row in v['files']:
 p=Path(row['path']);assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
 s=p.stat();assert (s.st_size,s.st_mtime_ns,s.st_ino,s.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1)
 assert row['target_verified_SHA']==row['SHA'] and row['scratch_verified_SHA']==row['SHA']
 assert Path(row['target_path']).is_relative_to(Path(v['target_root']))
before=shutil.disk_usage(old).free
for row in v['files']:Path(row['path']).unlink()
assert C.read_bytes()==canonical_bytes
print(json.dumps(dict(epoch=time.time(),removed_only_target_verified_duplicates=len(v['files']),bytes=sum(r['bytes'] for r in v['files']),free_before=before,free_after=shutil.disk_usage(old).free,canonical_bytes_unchanged=True,FINAL_source_models_text_errors_untouched=True)))
'''

def main():
    proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
    q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
    assert not S.exists();S.mkdir()
    args=dict(current_h1=q['roots']['h1'],current_owner=q['owner_root'],h1_private_lock=q['specs']['h1']['private_lock'])
    put('V96_SERIAL_T3_FORENSICS_RELOCATION_STARTED_ACTUAL.json',dict(epoch=time.time(),source_closed_pair=str(N),scratch=str(S),target=TARGET,max_elapsed_seconds=1500,max_selected_bytes=28*1024**3,one_connection_at_a_time=True,no_old_manifest_or_batch_repeated=True))
    module=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(module);module.loader.exec_module(memory)
    secret=memory.recover();c=None;done=[];start=time.monotonic()
    try:
        c=d.t.connect();inventory=d.code(c,d.t.PY,INVENTORY,args,timeout=180);c.close();c=None
        put('V96_SERIAL_T3_FORENSICS_FRESH_SOURCE_INVENTORY_ACTUAL.json',inventory)
        if inventory['source_already_32GiB']:
            put('V96_SERIAL_T3_FORENSICS_NO_RELOCATION_NEEDED_ACTUAL.json',dict(epoch=time.time(),source_free=inventory['source_free_before'],no_transfer_or_delete=True));return
        assert inventory['files'] and inventory['total_bytes']>0
        c=d.connect72(secret);target=d.code(c,d.PY72,TARGET_PREP,dict(root=TARGET,total_bytes=inventory['total_bytes']),timeout=45);c.close();c=None
        put('V96_SERIAL_T3_FORENSICS_FRESH_TARGET_STORAGE_ACTUAL.json',target)
        pending=list(inventory['files']);batch_no=0
        while pending and time.monotonic()-start<1300:
            batch=[];size=0;available=min(1100*1024**2,shutil.disk_usage(S).free-8*1024**3)
            while pending and size+pending[0]['bytes']<=available:
                row=pending.pop(0);batch.append(row);size+=row['bytes']
            assert batch,'Local scratch cannot preserve the existing 8GiB floor'
            c=d.t.connect();sf=c.open_sftp();sf.get_channel().settimeout(90)
            try:
                for row in batch:
                    p=S/Path(row['path']).name;assert p.resolve().is_relative_to(S.resolve()) and not p.exists()
                    assert shutil.disk_usage(S).free>row['bytes']+8*1024**3
                    sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
                    row.update(scratch_path=str(p),scratch_verified_SHA=row['SHA'])
            finally:sf.close();c.close();c=None
            c=d.connect72(secret);sf=c.open_sftp();sf.get_channel().settimeout(90)
            try:
                for row in batch:sf.put(row['scratch_path'],TARGET+'/'+Path(row['path']).name)
            finally:sf.close()
            verified=d.code(c,d.PY72,TARGET_VERIFY,dict(root=TARGET,batch=batch_no,files=batch),timeout=150);c.close();c=None
            put('V96_SERIAL_T3_FORENSICS_BATCH_'+str(batch_no)+'_TARGET_SHA_ACTUAL.json',verified)
            c=d.t.connect();deleted=d.code(c,d.t.PY,DELETE,dict(args,canonical_SHA=inventory['canonical_SHA'],files=verified['files'],target_root=TARGET),timeout=60);c.close();c=None
            put('V96_SERIAL_T3_FORENSICS_BATCH_'+str(batch_no)+'_SOURCE_DUPLICATES_RELEASED_ACTUAL.json',deleted)
            for row in verified['files']:
                p=Path(row['scratch_path']);assert p.resolve().is_relative_to(S.resolve()) and not p.is_symlink() and p.stat().st_size==row['bytes']
                p.unlink()
            done.extend(verified['files']);batch_no+=1
            if deleted['free_after']>35*1024**3:break
        assert done
        result=dict(epoch=time.time(),files=done,bytes=sum(r['bytes'] for r in done),source_free_after=deleted['free_after'],remaining_unprocessed_paths=[r['path'] for r in pending],elapsed_seconds=time.monotonic()-start,target_root=TARGET,target_contents_full_SHA_verified=True,no_unique_forensic_contents_deleted=True,canonical_bytes_unchanged=True,one_SSH_connection_at_a_time=True,C_scratch_released_only_after_target_full_SHA_and_source_receipt=True,source_above_original_25GiB_admission=deleted['free_after']>25*1024**3,no_GPU_PPO_or_new_budget_writer=True)
        put('V96_SERIAL_T3_FORENSICS_TO72_VERIFIED_SPACE_RELEASED_ACTUAL.json',result)
        print(json.dumps(dict(files=len(done),bytes=result['bytes'],source_free_after=result['source_free_after'],above_original_disk25=result['source_above_original_25GiB_admission'],elapsed_seconds=result['elapsed_seconds'])))
    except BaseException:
        put('V96_SERIAL_T3_FORENSICS_RELOCATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),verified_target_and_released_source_prefix=done,scratch=str(S),new_missing_only_after_actual_return_no_rerun_once=True));raise
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':main()
