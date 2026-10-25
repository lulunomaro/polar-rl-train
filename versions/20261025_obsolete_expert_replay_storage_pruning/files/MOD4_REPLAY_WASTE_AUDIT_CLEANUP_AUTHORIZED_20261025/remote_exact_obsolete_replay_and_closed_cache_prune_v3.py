"""Exact human-authorized obsolete replay pruning; executed through pinned transport.

No traversal-based deletion, raw hashing, model load, training or accounting write.
The input is an already reviewed finite list from this turn's metadata inventory.
"""
from pathlib import Path
import fcntl,hashlib,json,os,psutil,re,shutil,stat,sys,time,traceback

started=time.time();host=v['host'];groups=v['groups'];audit=Path(v['audit'])
assert host in ('210','72')
assert v['human_lower_threshold']=='删除门槛要降低一些，不要什么都留着占用大量地方'
bases=([Path('/mnt/mod4_linux_durable_20261013'),Path('/home/egde/rl_candidates'),Path('/home/egde/rl_audits')]
       if host=='210' else [Path('/home/lc01/Zonglin Li/zonglin2/tasks'),Path('/home/lc01/Zonglin Li/zonglin2/forensic_originals')])
assert audit.parent==(Path('/home/egde/rl_candidates') if host=='210' else Path('/home/lc01/Zonglin Li/zonglin2/audit'))
assert audit.name.startswith('OBSOLETE_REPLAY_PRUNE_20261025_') and not audit.exists()
audit.mkdir();actions=[];skips=[];closures=[];kept=[]

def save(name,value):
    with (audit/name).open('x',encoding='utf8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())

def inspect(row):
    p=Path(row['path'])
    assert p.is_absolute() and any(p.is_relative_to(b) for b in bases)
    assert p.resolve(strict=True)==p and not p.is_symlink()
    s=p.stat();assert stat.S_ISREG(s.st_mode)
    assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_nlink)==(row['device'],row['inode'],row['bytes'],row['mtime_ns'],row['nlink']),('Identity changed',str(p))
    return p,s

def check_group(g):
    assert g['obsolete_evidence'] and (g['keep'] or g.get('kind')=='closed_task_compiled_cache')
    allrows=g['delete']+g['keep'];roots={str(Path(r['path']).parent) for r in allrows}
    assert not {r['path'] for r in g['delete']}&{r['path'] for r in g['keep']}
    text_proofs=[]
    for name in g.get('closure_text_paths',[]):
        p=Path(name);assert any(p.is_relative_to(b) for b in bases)
        raw=p.read_bytes();assert len(raw)<32*1024**2
        value=json.loads(raw);text_proofs.append(dict(path=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=value))
        if p.name=='NODE_EXIT_ACTUAL.json':assert value['actual_all_own_children_waited'] and value['validation_fcntl_released_if_acquired']
    assert text_proofs or g.get('saved_complete_receipt_evidence'),('Missing original closure evidence',g['id'])
    # Inspect only exact recorded owned identities supplied by the closure receipts.
    for ident in g.get('recorded_owned_identities',[]):
        try:live=abs(psutil.Process(ident['pid']).create_time()-ident['creation'])<.02
        except psutil.NoSuchProcess:live=False
        assert not live,('Recorded own identity still alive',g['id'])
    for r in allrows:inspect(r)
    for r in g['delete']:
        p=Path(r['path'])
        if g.get('kind')=='closed_task_compiled_cache':
            assert r['nlink']==1 and ((p.suffix=='.pch' and '/job0/tmp/wp_pch_' in str(p)) or (p.suffix=='.cubin' and '/job0/cache/warp/' in str(p)) or '/job0/home/.nv/ComputeCache/' in str(p))
        else:
            assert p.suffix.lower() in ('.npz','.npy','.pt')
            if p.suffix.lower()=='.pt':assert re.fullmatch(r'preupdate_fullsource_\d+\.pt',p.name)
            assert not any(x in str(p) for x in ('reward_airfeasible5_2510v67','CLOSED67_CURRENT67','CLOSED65_CURRENT65','full20k_native','native32_v4','query9'))
    return dict(id=g['id'],closure_texts=text_proofs,saved_complete_receipt_evidence=g.get('saved_complete_receipt_evidence'),all_selected_and_retained_metadata_unchanged=True)

canonical=None;canon_sha=None;locks=[]
try:
    save('SOURCE_EXECUTED.py.json',dict(source=v['source'],SHA=hashlib.sha256(v['source'].encode()).hexdigest()))
    save('HUMAN_LOWER_THRESHOLD_AND_EXACT_FULL_INTENT_ACTUAL.json',v)
    if host=='210':
        canonical=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
        raw=canonical.read_bytes();canon_sha=hashlib.sha256(raw).hexdigest();c=json.loads(raw)
        assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
        lockpaths=[canonical.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')]
    else:
        lockpaths=[Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'),Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock')]
    for p in lockpaths:
        with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
        locks.append(dict(path=str(p),original_existing_fcntl_free=True))
    before={str(b):dict(zip(('total','used','free'),shutil.disk_usage(b))) for b in bases if b.exists()}
    for g in groups:
        try:closures.append(check_group(g));kept.extend(g['keep'])
        except Exception as e:skips.append(dict(group=g['id'],kind='GROUP_PREFLIGHT_REJECTED_NO_DELETE',error=repr(e)))
    admitted={x['id'] for x in closures}
    save('EXACT_GROUP_PREFLIGHT_ACTUAL.json',dict(epoch=time.time(),closures=closures,rejected=skips,locks=locks,canonical_SHA=canon_sha,filesystem_before=before))
    for g in groups:
        if g['id'] not in admitted:continue
        for row in g['delete']:
            try:
                p,s=inspect(row)
                fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
                try:
                    fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    fs=os.fstat(fd);assert (fs.st_dev,fs.st_ino,fs.st_size,fs.st_mtime_ns,fs.st_nlink)==(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_nlink)
                    # Each exact unlink has an immutable intent before the mutation.
                    seq=len(actions);save('INTENT_'+str(seq).zfill(5)+'_ACTUAL.json',dict(group=g['id'],row=row,unique_old_middle_original_loss_explicitly_authorized=True))
                    inspect(row);p.unlink();assert not p.exists()
                    action=dict(sequence=seq,group=g['id'],path=str(p),bytes=s.st_size,allocated_bytes=s.st_blocks*512,device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,mtime_ns=s.st_mtime_ns,producer_SHA=row.get('producer_SHA'),kind=('CLOSED_TASK_REBUILDABLE_COMPILED_CACHE_UNLINK' if g.get('kind')=='closed_task_compiled_cache' else 'AUTHORIZED_OBSOLETE_REPLAY_UNLINK'),irrecoverable=(g.get('kind')!='closed_task_compiled_cache'),absent_after=True)
                    actions.append(action);save('ACTION_'+str(seq).zfill(5)+'_ACTUAL.json',action)
                finally:os.close(fd)
            except Exception:
                skips.append(dict(group=g['id'],path=row['path'],kind='FILE_CHANGED_LOCKED_OR_UNLINK_ERROR',error=traceback.format_exc()))
    # Representatives, all original text and models are never selected; recheck representatives.
    kept_actual=[]
    for row in kept:
        p,s=inspect(row);kept_actual.append(dict(path=str(p),bytes=s.st_size,device=s.st_dev,inode=s.st_ino,mtime_ns=s.st_mtime_ns))
    if canonical:assert hashlib.sha256(canonical.read_bytes()).hexdigest()==canon_sha
    after={str(b):dict(zip(('total','used','free'),shutil.disk_usage(b))) for b in bases if b.exists()}
    byinode={}
    for x in actions:byinode.setdefault((x['device'],x['inode']),[]).append(x)
    release=sum(a[0]['allocated_bytes'] for a in byinode.values() if len(a)==a[0]['nlink'])
    result=dict(epoch=time.time(),passed=not skips,audit_root=str(audit),deleted_count=len(actions),deleted_logical_bytes=sum(x['bytes'] for x in actions),allocated_bytes_all_selected_links_removed=release,actions=actions,skips=skips,retained_representatives=kept_actual,closures=closures,filesystem_before=before,filesystem_after=after,filesystem_snapshot_deltas={b:after[b]['free']-before[b]['free'] for b in before},whole_filesystem_deltas_include_concurrent_writes=True,canonical_SHA_unchanged=canon_sha,all_text_reports_logs_models_current_sources_preserved=True,no_GPU_training_budget_write_or_peer_identity_enumeration=True,elapsed_seconds=time.time()-started)
    save('COMPLETE_ACTUAL.json',result)
    result['all_audit_texts']=[]
    for p in sorted(audit.iterdir()):
        raw=p.read_bytes();result['all_audit_texts'].append(dict(path=str(p),relative=p.name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8')))
    print(json.dumps(result))
except BaseException:
    err=dict(epoch=time.time(),error=traceback.format_exc(),actions=actions,skips=skips,partial_unlinks_not_rolled_back=True)
    save('ORIGINAL_ERROR_ACTUAL.json',err);raise
