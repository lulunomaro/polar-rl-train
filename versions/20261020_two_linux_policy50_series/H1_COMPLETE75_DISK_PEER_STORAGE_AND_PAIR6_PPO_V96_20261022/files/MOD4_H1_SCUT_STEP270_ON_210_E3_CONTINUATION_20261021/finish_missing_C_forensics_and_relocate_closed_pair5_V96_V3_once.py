"""Missing-only continuation after V2's actual finite return; no old helper rerun."""
from pathlib import Path
import ast,importlib.util,json,shutil,time,traceback
T=Path(__file__).resolve().parent;R=T/'reports';W=T.parent
spec=importlib.util.spec_from_file_location('V2_definitions_only',T/'relocate_closed_forensics_C_and_current210_to72_serial_V96_V2_once.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
d=x.d;b=x.b;H=x.H;read=x.read;N=x.N;CBASE=x.CBASE;TARGET=x.TARGET
S=T/'relocation_scratch_closed_pair5_to72_V96_V3'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
PRESENCE=r'''
from pathlib import Path
import hashlib,json,shutil,time
B=Path(v['root']);assert B.is_dir() and B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/forensic_originals').resolve())
existing=[];missing=[]
for row in v['files']:
 p=B/'C_T3_batch38'/Path(row['path']).name
 if not p.exists():missing.append(row);continue
 assert not p.is_symlink() and p.stat().st_size==row['bytes']
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 assert h.hexdigest()==row['SHA'];existing.append(dict(path=str(p),bytes=row['bytes'],SHA=h.hexdigest()))
free=shutil.disk_usage(B).free;assert free>sum(r['bytes'] for r in missing)+20*1024**3+25*1024**3
print(json.dumps(dict(epoch=time.time(),existing_complete_full_SHA=existing,missing_only=missing,free_before=free,no_existing_complete_file_reupload=True)))
'''
INVENTORY=x.INVENTORY.replace('24*1024**3','20*1024**3')
ast.parse(PRESENCE);ast.parse(INVENTORY)

def main():
    proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
    assert not (R/'V96_V2_C38_TARGET_FULL_SHA_ACTUAL.json').exists()
    crows=read(R/'V96_V2_SERIAL_RELOCATION_STARTED_ACTUAL.json')['C_originals']
    assert read(R/'V96_V2_SERIAL_FRESH_TARGET_STORAGE_ACTUAL.json')['root']==TARGET and len(crows)==38
    for row in crows:
        p=Path(row['local_path']);assert p.resolve().is_relative_to(CBASE.resolve()) and not p.is_symlink()
        st=p.stat();assert (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['C_mtime_ns'],row['C_inode'],row['C_nlink'])
    assert not S.exists();S.mkdir()
    put('V96_V3_MISSING_ONLY_RELOCATION_STARTED_ACTUAL.json',dict(epoch=time.time(),reuse_existing_forensic_target_only_not_failed_training_root=True,target=TARGET,source_closed_pair=str(N),max_elapsed_seconds=2400,source210_max_bytes=20*1024**3,only_missing_C_uploads=True,one_connection_at_a_time=True))
    mod=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(mod);mod.loader.exec_module(memory)
    secret=memory.recover();c=None;done=[];C_deleted=[];start=time.monotonic()
    args=dict(current_h1=q['roots']['h1'],current_owner=q['owner_root'],h1_private_lock=q['specs']['h1']['private_lock'])
    try:
        c=d.connect72(secret);presence=d.code(c,d.PY72,PRESENCE,dict(root=TARGET,files=crows),timeout=180)
        put('V96_V3_EXISTING_TARGET_SHA_AND_MISSING_ONLY_ACTUAL.json',presence)
        sf=c.open_sftp();sf.get_channel().settimeout(90)
        try:
            for row in presence['missing_only']:
                assert time.monotonic()-start<2300 and H(row['local_path'])==row['SHA']
                sf.put(row['local_path'],TARGET+'/C_T3_batch38/'+Path(row['local_path']).name)
        finally:sf.close()
        verifiedC=d.code(c,d.PY72,b.TARGET_VERIFY,dict(root=TARGET+'/C_T3_batch38',batch=0,files=crows),timeout=180);c.close();c=None
        put('V96_V3_C38_TARGET_FULL_SHA_ACTUAL.json',verifiedC)
        before=shutil.disk_usage(T).free
        for row in verifiedC['files']:
            p=Path(row['local_path']);assert p.resolve().is_relative_to(CBASE.resolve()) and not p.is_symlink()
            st=p.stat();assert (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['C_mtime_ns'],row['C_inode'],row['C_nlink']) and row['target_verified_SHA']==row['SHA']
            p.unlink();C_deleted.append(row)
        put('V96_V3_C38_VERIFIED_DUPLICATE_SPACE_RELEASED_ACTUAL.json',dict(epoch=time.time(),files=C_deleted,bytes=sum(r['bytes'] for r in C_deleted),C_free_before=before,C_free_after=shutil.disk_usage(T).free,all_contents_full_SHA_retained_on72=True))
        c=d.t.connect();inventory=d.code(c,d.t.PY,INVENTORY,args,timeout=180);c.close();c=None
        put('V96_V3_PAIR5_FRESH_SOURCE_INVENTORY_ACTUAL.json',inventory)
        if inventory['source_already_32GiB']:
            put('V96_V3_PAIR5_SOURCE_NO_ADDITIONAL_RELOCATION_NEEDED_ACTUAL.json',dict(epoch=time.time(),source_free=inventory['source_free_before']));return
        assert inventory['files']
        pending=list(inventory['files']);batch_no=0
        while pending and time.monotonic()-start<2300:
            batch=[];size=0;available=min(8*1024**3,shutil.disk_usage(S).free-8*1024**3)
            while pending and size+pending[0]['bytes']<=available:
                row=pending.pop(0);batch.append(row);size+=row['bytes']
            assert batch
            c=d.t.connect();sf=c.open_sftp();sf.get_channel().settimeout(90)
            try:
                for row in batch:
                    assert time.monotonic()-start<2300
                    p=S/Path(row['path']).name;assert p.resolve().is_relative_to(S.resolve()) and not p.exists() and shutil.disk_usage(S).free>row['bytes']+8*1024**3
                    sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];row.update(scratch_path=str(p),scratch_verified_SHA=row['SHA'])
            finally:sf.close();c.close();c=None
            c=d.connect72(secret);sf=c.open_sftp();sf.get_channel().settimeout(90)
            try:
                for row in batch:
                    assert time.monotonic()-start<2300
                    sf.put(row['scratch_path'],TARGET+'/source_pair5/'+Path(row['path']).name)
            finally:sf.close()
            verified=d.code(c,d.PY72,b.TARGET_VERIFY,dict(root=TARGET+'/source_pair5',batch=batch_no,files=batch),timeout=180);c.close();c=None
            put('V96_V3_PAIR5_BATCH_'+str(batch_no)+'_TARGET_FULL_SHA_ACTUAL.json',verified)
            c=d.t.connect();deleted=d.code(c,d.t.PY,x.DELETE,dict(args,canonical_SHA=inventory['canonical_SHA'],files=verified['files'],target_root=TARGET+'/source_pair5'),timeout=60);c.close();c=None
            put('V96_V3_PAIR5_BATCH_'+str(batch_no)+'_SOURCE_DUPLICATES_RELEASED_ACTUAL.json',deleted)
            for row in verified['files']:
                p=Path(row['scratch_path']);assert p.resolve().is_relative_to(S.resolve()) and not p.is_symlink() and p.stat().st_size==row['bytes'];p.unlink()
            done.extend(verified['files']);batch_no+=1
        assert done
        result=dict(epoch=time.time(),C_relocated_files=C_deleted,files=done,source210_released_bytes=sum(r['bytes'] for r in done),C_released_bytes=sum(r['bytes'] for r in C_deleted),source_free_after=deleted['free_after'],C_free_after=shutil.disk_usage(T).free,pending_unprocessed_paths=[r['path'] for r in pending],target_root=TARGET,elapsed_seconds=time.monotonic()-start,all_contents_full_SHA_retained_on72=True,no_unique_forensic_contents_deleted=True,canonical_bytes_unchanged=True,one_SSH_connection_at_a_time=True,source_above_original_disk25=deleted['free_after']>25*1024**3,no_GPU_PPO_or_new_budget_writer=True)
        put('V96_V3_C_AND_PAIR5_FORENSICS_FULL_SHA_ON72_SPACE_RELEASED_ACTUAL.json',result)
        print(json.dumps(dict(C_files=len(C_deleted),source_files=len(done),source_bytes=result['source210_released_bytes'],C_bytes=result['C_released_bytes'],source_free_after=result['source_free_after'],C_free_after=result['C_free_after'],above_original_disk25=result['source_above_original_disk25'],elapsed_seconds=result['elapsed_seconds'])))
    except BaseException:
        put('V96_V3_SERIAL_RELOCATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),verified_C_relocated_prefix=C_deleted,verified_source210_relocated_prefix=done,scratch=str(S),target=TARGET,new_missing_only_after_actual_return_no_rerun=True));raise
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':main()
