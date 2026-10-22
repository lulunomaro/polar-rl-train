from pathlib import Path
import hashlib,importlib.util,json,os,sys,time,traceback
S=Path(__file__).resolve().parent;W=S.parent;R=S/'reports';B=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022';BR=B/'reports'
R.mkdir(exist_ok=True)
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CODE=r'''
from pathlib import Path
import hashlib,json,os,psutil,re,shutil,stat,sys,time,traceback
base=Path('/home/lc01/Zonglin Li/zonglin2/tasks');audit=Path(v['audit'])
assert audit.parent==Path('/home/lc01/Zonglin Li/zonglin2/audit') and not audit.exists()
assert v['approval']['exact_human_reply']=='两项都做，约256.21GB（推荐）'
assert v['approval']['approved_duplicate_and_exact15_old_complete_windows']
before=shutil.disk_usage(base);started=time.time();actions=[];completed=False
audit.mkdir()
def save(name,value):
    with (audit/name).open('x',encoding='utf8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()
def check(row):
    p=Path(row['path']);assert p.resolve(strict=True)==p and p.is_relative_to(base) and not p.is_symlink()
    s=p.stat();assert stat.S_ISREG(s.st_mode)
    assert (s.st_size,s.st_ino,s.st_mtime_ns,s.st_dev,s.st_nlink)==(row['bytes'],row['inode'],row['mtime_ns'],row['device'],row['nlink'])
    return p,s
def closed(node):
    p=Path(node);assert p.resolve(strict=True)==p and p.is_relative_to(base)
    ex=json.loads((p/'NODE_EXIT_ACTUAL.json').read_bytes());assert ex['actual_all_own_children_waited'] and ex['validation_fcntl_released_if_acquired']
    # Only inspect exact identities already recorded by these owned nodes. Never enumerate peers.
    identities=[]
    def scan(x):
        if isinstance(x,dict):
            if isinstance(x.get('pid'),int) and isinstance(x.get('creation'),(float,int)):
                root=x.get('root','');argv=x.get('argv',[])
                if str(root).startswith(str(p)) or any(str(a).startswith(str(p)+'/') for a in argv):identities.append((x['pid'],x['creation']))
            for value in x.values():scan(value)
        elif isinstance(x,list):
            for value in x:scan(value)
    for name in ('NODE_IDENTITY.json','NODE_CURRENT.json','NODE_TERMINAL_ACTUAL.json'):
        f=p/name
        if f.is_file() and f.stat().st_size<8*1024**2:scan(json.loads(f.read_bytes()))
    for pid,creation in set(identities):
        try:live=abs(psutil.Process(pid).create_time()-creation)<.02
        except psutil.NoSuchProcess:live=False
        assert not live,('Original owned process identity still alive',node)
    return dict(node=node,original_EXIT_all_children_waited=True,recorded_own_identities_out=len(set(identities)),peer_identities_not_enumerated=True)
try:
    save('HUMAN_APPROVAL_ACTUAL.json',v['approval'])
    save('FULL_EXACT_INTENT_BEFORE_ANY_REPLACEMENT_OR_UNLINK.json',dict(epoch=time.time(),duplicate=v['duplicates'],old_prune=v['prune'],all_old_INDEX_manifests_are_historical_not_current_existence=True))
    save('EXECUTION_IDENTITY_ACTUAL.json',dict(pid=os.getpid(),creation=psutil.Process().create_time(),exe=sys.executable,argv=sys.argv))
    allnodes=set(x['closed_node'] for g in v['duplicates']['groups'] for x in [g['keeper']]+g['copies'])|set(x['node'] for x in v['prune']['stages'])
    closure=[closed(n) for n in sorted(allnodes)]
    copies={x['path'] for g in v['duplicates']['groups'] for x in g['copies']}
    prune={x['path'] for s in v['prune']['stages'] for x in s['proposed_removed_unique_originals']}
    retained={x['path'] for s in v['prune']['stages'] for x in s['retained_files']}
    assert len(copies)==164 and len(prune)==1450 and len(v['prune']['stages'])==15
    assert not copies&prune and not retained&prune
    # Check the whole exact batch before the first mutation; reuse this turn's full-SHA verification only when every identity is unchanged.
    for g in v['duplicates']['groups']:
        keep,ks=check(g['keeper']);assert digest(keep)==g['SHA']
        for row in g['copies']:
            p,s=check(row);assert row['actual_full_SHA']==g['SHA'] and (s.st_mode,s.st_uid,s.st_gid,s.st_dev)==(ks.st_mode,ks.st_uid,ks.st_gid,ks.st_dev)
    for stage in v['prune']['stages']:
        final=json.loads(Path(stage['original_FINAL']).read_bytes());assert final['passed']
        index=json.loads(Path(stage['index']).read_bytes());assert index['all_success_and_failed_control_prefixes_retained'] and not index.get('retention_failure_flag_preserves_all_currently_present_files',False)
        assert len(index['index'])==stage['prefix_pairs']
        for row in stage['retained_files']+stage['proposed_removed_unique_originals']:
            p,s=check(row);assert p.parent==Path(stage['index']).parent
            assert re.fullmatch(r'(control_prefix_\d+\.npz|preupdate_fullsource_\d+\.pt)',p.name)
    save('PREFLIGHT_ALL_EXACT_IDENTITIES_RETAINED_SETS_AND_ORIGINAL_OWNED_EXITS_ACTUAL.json',dict(epoch=time.time(),passed=True,closure=closure,source_free_snapshot=before.free,unique_final_source_failed_native_evaluation_log_error_paths_not_selected=True))
    for g in v['duplicates']['groups']:
        keep=Path(g['keeper']['path'])
        for row in g['copies']:
            p,s=check(row);tmp=p.with_name('.'+p.name+'.approved_V112_link_'+str(os.getpid()))
            assert not tmp.exists();os.link(keep,tmp)
            try:
                assert tmp.stat().st_ino==keep.stat().st_ino
                check(row);os.replace(tmp,p)
            except BaseException:
                if tmp.exists():tmp.unlink()
                raise
            z=p.stat();assert z.st_ino==keep.stat().st_ino and z.st_size==row['bytes']
            action=dict(sequence=len(actions),kind='atomic_path_preserving_full_SHA_identical_hardlink_dedup',path=str(p),keeper=str(keep),bytes=row['bytes'],SHA=g['SHA'],old_inode=s.st_ino,new_inode=z.st_ino,old_mtime_ns=s.st_mtime_ns,new_mtime_ns=z.st_mtime_ns,all_original_path_and_bytes_retained=True)
            save('ACTION_'+str(len(actions)).zfill(5)+'_ACTUAL.json',action);actions.append(action)
    # Deliberately authorized old intermediate data loss; no recursive deletion or directory removal.
    for stage in v['prune']['stages']:
        for row in stage['proposed_removed_unique_originals']:
            p,s=check(row);p.unlink();assert not p.exists()
            action=dict(sequence=len(actions),kind='explicitly_authorized_old_complete_window_middle_raw_preupdate_pruned_irrecoverable',path=str(p),bytes=row['bytes'],producer_SHA=row['producer_SHA'],inode=s.st_ino,mtime_ns=s.st_mtime_ns,retained_pair_indices=stage['retain_indices'],original_index_remains_historical=True)
            save('ACTION_'+str(len(actions)).zfill(5)+'_ACTUAL.json',action);actions.append(action)
    for g in v['duplicates']['groups']:
        keep=Path(g['keeper']['path']);assert digest(keep)==g['SHA']
        for row in g['copies']:
            p=Path(row['path']);assert p.exists() and p.stat().st_ino==keep.stat().st_ino and p.stat().st_size==row['bytes']
    for stage in v['prune']['stages']:
        for row in stage['retained_files']:check(row)
        assert Path(stage['original_FINAL']).is_file() and json.loads(Path(stage['original_FINAL']).read_bytes())['passed']
    after=shutil.disk_usage(base)
    result=dict(epoch=time.time(),passed=True,audit_root=str(audit),actions=actions,duplicate_replacements=164,pruned_old_middle_files=1450,old_stages=15,
      retained_old_first_latest2_files=sum(len(s['retained_files']) for s in v['prune']['stages']),
      expected_duplicate_allocated_released_bytes=v['duplicates']['potential_released_allocated_bytes'],expected_old_middle_allocated_released_bytes=v['prune']['proposed_released_allocated_bytes'],
      filesystem_free_before=before.free,filesystem_free_after=after.free,observed_free_delta=after.free-before.free,source_above_original_disk25=after.free>25*1024**3,
      all_duplicate_paths_and_exact_bytes_retained=True,all_retained_old_pairs_and_unique_final_source_failed_native_evaluation_error_log_bytes_preserved=True,
      middle_originals_pruned_by_new_explicit_human_approval_are_irrecoverable=True,
      old_indices_are_historical_snapshots_not_false_claims_of_present_files=True,
      no_training_signal_stop_hotpatch_GPU_new_job_budget_or_peer_identity_query=True,elapsed=time.time()-started)
    save('COMPLETE_ACTUAL.json',result);completed=True;print(json.dumps(result))
except BaseException:
    error=dict(epoch=time.time(),error=traceback.format_exc(),completed_actions=actions,partial_actions_not_rolled_back_or_refunded=True,resume_only_new_missing_exact_subset_not_old_once=True)
    save('ORIGINAL_ERROR_ACTUAL.json',error)
    print(json.dumps(dict(passed=False,audit_root=str(audit),original_error=error)));raise
'''
try:
    approval=dict(epoch=time.time(),question_item_id='call_6221d991f6124bd08ee0984c31a5f3aa',
      exact_human_reply='两项都做，约256.21GB（推荐）',approved_duplicate_and_exact15_old_complete_windows=True,
      duplicate_plan=str(BR/'V112_HOST72_IMMUTABLE_DUPLICATE_ACTUAL_FULL_SHA_VERIFIED_REVIEWABLE_CANDIDATES.json'),
      old_retention_plan=str(BR/'V112_OLD_COMPLETE_TRAINING_PREFIX_FIRST_LATEST2_EXPANSION_PROPOSAL_NOT_AUTHORIZED_CPU_ACTUAL.json'),
      old_middle_originals_irrecoverable_explicitly_disclosed=True,all_other_existing_originals_and_current_training_outside_scope=True)
    approval['duplicate_plan_SHA']=H(approval['duplicate_plan']);approval['old_retention_plan_SHA']=H(approval['old_retention_plan'])
    put('HUMAN_EXPLICIT_BOTH_CLEANUP_ACTIONS_APPROVAL_ACTUAL.json',approval)
    put('CLEANUP_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,read_only_previous_audit_not_reexecuted=True))
    q=dict(approval=approval,duplicates=read(approval['duplicate_plan']),prune=read(approval['old_retention_plan']),audit='/home/lc01/Zonglin Li/zonglin2/audit/closed_tasks_cleanup_20261022_V112_'+str(time.time_ns()))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    secret=m.recover()
    try:c=d.connect72(secret)
    finally:secret=None
    try:result=d.code(c,d.PY72,CODE,q,timeout=300)
    finally:c.close()
    put('HOST72_APPROVED_EXACT_CLEANUP_ACTUAL_RETURNED.json',result)
    assert result['passed'] and result['source_above_original_disk25']
    print(json.dumps({k:val for k,val in result.items() if k!='actions'}))
except BaseException:
    put('LOCAL_CLEANUP_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_once_rerun=True));raise
