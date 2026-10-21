"""New bounded serial relocation; V1 returned without moving any file.

First preserve the 38 existing C forensic originals on 72 and free their C
duplicates. Then use that scratch for the newly closed pair5 H1 control NPZs.
Only one SSH connection exists at any time; all content receives full SHA proof.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports'
N=T/'H1_STEP270_E3_HEALTH_CLASSIFIER_PAIR_V5_20261022'
CBASE=T/'relocated_forensic_originals/T3_1710v1_additional_after_bridge7'
S=T/'relocation_scratch_closed_pair5_to72_V96_V2'
TARGET='/home/lc01/Zonglin Li/zonglin2/forensic_originals/H1_closed_C_and_pair5_serial_20261022_V96_V2'
spec=importlib.util.spec_from_file_location('reserved_V1_definitions',T/'relocate_closed_H1_T3_forensics_to72_serial_scratch_V96_once.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);d=b.d;H=b.H
read=lambda p:json.loads(Path(p).read_bytes())
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
HEADER=b.SOURCE_HEADER.replace("old=Path('/mnt/mod4_linux_durable_20261013/T3_1710v1/h1')","old=Path(v['current_h1'])")
INVENTORY=HEADER+b.INVENTORY[len(b.SOURCE_HEADER):].replace('if free<32*1024**3:','if free<32*1024**3:').replace('28*1024**3','24*1024**3')
DELETE=HEADER+b.DELETE[len(b.SOURCE_HEADER):]
PREP=b.TARGET_PREP.replace("B.mkdir(parents=True)","B.mkdir(parents=True);(B/'C_T3_batch38').mkdir();(B/'source_pair5').mkdir()")
for code in (INVENTORY,DELETE,PREP,b.TARGET_VERIFY):ast.parse(code)

def main():
    proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
    assert not S.exists();S.mkdir()
    rows=read(R/'ADDITIONAL_CLOSED_H1_FORENSICS_VERIFIED_C_RELOCATION_SPACE_RELEASED_ACTUAL.json')['files']
    crows=[]
    for row in rows:
        p=Path(row['local_path']);assert p.resolve().is_relative_to(CBASE.resolve()) and not p.is_symlink() and p.suffix=='.npz'
        st=p.stat();assert st.st_size==row['bytes'] and st.st_nlink==1 and H(p)==row['SHA']
        crows.append(dict(row,C_mtime_ns=st.st_mtime_ns,C_inode=st.st_ino,C_nlink=st.st_nlink))
    assert len(crows)==38
    put('V96_V2_SERIAL_RELOCATION_STARTED_ACTUAL.json',dict(epoch=time.time(),closed_pair=str(N),C_originals=crows,new_target=TARGET,scratch=str(S),max_elapsed_seconds=1800,source210_max_bytes=24*1024**3,previous_V1_consumed_no_files_moved=True,no_same_root_or_once_retry=True,one_connection_at_a_time=True))
    module=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(module);module.loader.exec_module(memory)
    secret=memory.recover();c=None;done=[];C_deleted=[];start=time.monotonic()
    args=dict(current_h1=q['roots']['h1'],current_owner=q['owner_root'],h1_private_lock=q['specs']['h1']['private_lock'])
    try:
        c=d.connect72(secret)
        prep=d.code(c,d.PY72,PREP,dict(root=TARGET,total_bytes=sum(r['bytes'] for r in crows)+24*1024**3),timeout=45)
        put('V96_V2_SERIAL_FRESH_TARGET_STORAGE_ACTUAL.json',prep)
        sf=c.open_sftp();sf.get_channel().settimeout(90)
        try:
            for row in crows:
                assert time.monotonic()-start<600
                sf.put(row['local_path'],TARGET+'/C_T3_batch38/'+Path(row['local_path']).name)
        finally:sf.close()
        verifiedC=d.code(c,d.PY72,b.TARGET_VERIFY,dict(root=TARGET+'/C_T3_batch38',batch=0,files=crows),timeout=180)
        c.close();c=None
        put('V96_V2_C38_TARGET_FULL_SHA_ACTUAL.json',verifiedC)
        C_before=shutil.disk_usage(T).free
        for row in verifiedC['files']:
            p=Path(row['local_path']);assert p.resolve().is_relative_to(CBASE.resolve()) and not p.is_symlink()
            st=p.stat();assert (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['C_mtime_ns'],row['C_inode'],row['C_nlink'])
            assert row['target_verified_SHA']==row['SHA'];p.unlink();C_deleted.append(row)
        put('V96_V2_C38_VERIFIED_DUPLICATE_SPACE_RELEASED_ACTUAL.json',dict(epoch=time.time(),files=C_deleted,bytes=sum(r['bytes'] for r in C_deleted),C_free_before=C_before,C_free_after=shutil.disk_usage(T).free,all_contents_retained_full_SHA_on72=True,no_unique_forensic_content_deleted=True,not_new_training_or_account_write=True))
        c=d.t.connect();inventory=d.code(c,d.t.PY,INVENTORY,args,timeout=180);c.close();c=None
        put('V96_V2_PAIR5_FRESH_SOURCE_INVENTORY_ACTUAL.json',inventory)
        if inventory['source_already_32GiB']:
            put('V96_V2_PAIR5_SOURCE_NO_ADDITIONAL_RELOCATION_NEEDED_ACTUAL.json',dict(epoch=time.time(),source_free=inventory['source_free_before'],C_38_contents_retained_on72=True));return
        assert inventory['files'] and inventory['total_bytes']>0
        pending=list(inventory['files']);batch_no=0
        while pending and time.monotonic()-start<1600:
            batch=[];size=0;available=min(10*1024**3,shutil.disk_usage(S).free-8*1024**3)
            while pending and size+pending[0]['bytes']<=available:
                row=pending.pop(0);batch.append(row);size+=row['bytes']
            assert batch,'Fresh local scratch insufficient; do not lower its preserved floor'
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
                for row in batch:sf.put(row['scratch_path'],TARGET+'/source_pair5/'+Path(row['path']).name)
            finally:sf.close()
            verified=d.code(c,d.PY72,b.TARGET_VERIFY,dict(root=TARGET+'/source_pair5',batch=batch_no,files=batch),timeout=180)
            c.close();c=None
            put('V96_V2_PAIR5_BATCH_'+str(batch_no)+'_TARGET_FULL_SHA_ACTUAL.json',verified)
            c=d.t.connect();deleted=d.code(c,d.t.PY,DELETE,dict(args,canonical_SHA=inventory['canonical_SHA'],files=verified['files'],target_root=TARGET+'/source_pair5'),timeout=60);c.close();c=None
            put('V96_V2_PAIR5_BATCH_'+str(batch_no)+'_SOURCE_DUPLICATES_RELEASED_ACTUAL.json',deleted)
            for row in verified['files']:
                p=Path(row['scratch_path']);assert p.resolve().is_relative_to(S.resolve()) and not p.is_symlink() and p.stat().st_size==row['bytes'];p.unlink()
            done.extend(verified['files']);batch_no+=1
        assert done
        result=dict(epoch=time.time(),C_relocated_files=C_deleted,files=done,source210_released_bytes=sum(r['bytes'] for r in done),C_released_bytes=sum(r['bytes'] for r in C_deleted),source_free_after=deleted['free_after'],C_free_after=shutil.disk_usage(T).free,remaining_unprocessed_paths=[r['path'] for r in pending],target_root=TARGET,elapsed_seconds=time.monotonic()-start,all_contents_full_SHA_retained_on72=True,source_duplicates_and_C_scratch_only_removed=True,no_unique_forensic_contents_deleted=True,canonical_bytes_unchanged=True,one_SSH_connection_at_a_time=True,source_above_original_disk25=deleted['free_after']>25*1024**3,no_GPU_PPO_or_new_budget_writer=True)
        put('V96_V2_C_AND_PAIR5_FORENSICS_FULL_SHA_ON72_SPACE_RELEASED_ACTUAL.json',result)
        print(json.dumps(dict(C_files=len(C_deleted),source_files=len(done),source_bytes=result['source210_released_bytes'],C_bytes=result['C_released_bytes'],source_free_after=result['source_free_after'],C_free_after=result['C_free_after'],above_original_disk25=result['source_above_original_disk25'],elapsed_seconds=result['elapsed_seconds'])))
    except BaseException:
        put('V96_V2_SERIAL_RELOCATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),verified_C_relocated_prefix=C_deleted,verified_source210_relocated_prefix=done,scratch=str(S),target=TARGET,new_missing_only_after_actual_return_no_rerun=True));raise
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':main()
