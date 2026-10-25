"""UNINSTALLED proposal; requires explicit human approval before new-root use.

Only future control-prefix NPZ / matching pre-update PT retention changes.
No environment, policy, optimizer, RNG, physics, reward, or health access.
"""
from pathlib import Path
import functools,hashlib,json,re,time,traceback

POLICY='future_first1_latest2_complete_pairs_plus_incomplete_and_current_failure_v1'
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def put(path,value):
    path=Path(path);tmp=path.with_name(path.name+'.partial')
    with tmp.open('w',encoding='utf8') as f:json.dump(value,f,indent=2)
    tmp.replace(path)
def member(folder,row,source=False):
    p=Path(row['path'])
    pattern=r'preupdate_fullsource_\d+\.pt' if source else r'control_prefix_\d+\.npz'
    if not re.fullmatch(pattern,p.name) or p.is_symlink() or p.resolve().parent!=folder:
        raise RuntimeError('Retention target is not its exact own prefix filename')
    return p
def apply_retention(folder,index):
    folder=Path(folder).resolve();ledger=folder/'PREFIX_PAIR_RETENTION_HISTORY_ACTUAL.json'
    history=json.loads(ledger.read_bytes()).get('transactions',[]) if ledger.exists() else []
    done={x['path'] for txn in history for x in txn['removed']}
    protected=set(range(min(1,len(index))))|set(range(max(0,len(index)-2),len(index)))
    protected|={i for i,row in enumerate(index) if row['controls']<24}
    failed=(folder/'ACTUAL_STEP_ORIGINAL_ERROR.json').exists()
    selected=[]
    try:
        if not failed:
            # Validate the entire proposed batch before removing any pair.
            for i,row in enumerate(index):
                if i in protected:continue
                pair=[]
                for source,r in ((False,row),(True,row['preupdate_source'])):
                    p=member(folder,r,source)
                    if str(p) in done:continue
                    if not p.is_file():raise RuntimeError('Unrecorded missing retention candidate')
                    st=p.stat()
                    if st.st_nlink!=1 or st.st_size!=r['bytes'] or sha(p)!=r['SHA']:
                        raise RuntimeError('Retention candidate identity/bytes/SHA mismatch')
                    pair.append(dict(path=str(p),bytes=st.st_size,SHA=r['SHA'],inode=st.st_ino,mtime_ns=st.st_mtime_ns))
                if pair:selected.append(dict(index=i,files=pair))
            if selected:
                token=str(time.time_ns());intent=folder/('PREFIX_PAIR_RETENTION_INTENT_'+token+'.json')
                plan=dict(epoch=time.time(),policy=POLICY,protected_indices=sorted(protected),selected=selected,only_this_future_own_trace=True)
                # The intent is immutable evidence, including any partial IO failure.
                with intent.open('x',encoding='utf8') as f:json.dump(plan,f,indent=2)
                removed=[]
                for pair in selected:
                    for r in pair['files']:
                        p=Path(r['path']);st=p.stat()
                        if p.is_symlink() or st.st_ino!=r['inode'] or st.st_mtime_ns!=r['mtime_ns'] or st.st_size!=r['bytes'] or st.st_nlink!=1:
                            raise RuntimeError('Retention candidate changed after intent')
                        p.unlink();removed.append(r)
                txn=dict(epoch=time.time(),intent=str(intent),removed=removed,all_selected_actual_removed=True)
                receipt=folder/('PREFIX_PAIR_RETENTION_RECEIPT_'+token+'.json')
                with receipt.open('x',encoding='utf8') as f:json.dump(txn,f,indent=2)
                history.append(txn);put(ledger,dict(policy=POLICY,transactions=history))
    except BaseException:
        path=folder/('PREFIX_PAIR_RETENTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
        with path.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),policy=POLICY,no_claim_partial_removal_complete=True,original_trace_error_path_preserves_all_remaining_files=True),f,indent=2)
        raise
    # Preserve every original producer path, bytes and SHA; add truthful status.
    path=folder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'
    report=json.loads(path.read_bytes());status=[]
    for i,row in enumerate(index):
        raw=member(folder,row);source=member(folder,row['preupdate_source'],True)
        status.append(dict(index=i,path=str(raw),raw_retained=raw.is_file(),preupdate_path=str(source),preupdate_retained=source.is_file(),protected=i in protected))
    report['all_success_and_failed_control_prefixes_retained']=all(x['raw_retained'] and x['preupdate_retained'] for x in status)
    report['approved_future_retention_policy']=POLICY
    report['retention_status']=status
    report['retention_failure_flag_preserves_all_currently_present_files']=failed
    report['older_pruned_prefixes_not_recoverable_on_later_failure']=True
    report['retention_history']=str(ledger) if ledger.exists() else None
    put(path,report)
    return dict(policy=POLICY,prefixes=len(index),retained_complete_pairs=sum(x['raw_retained'] and x['preupdate_retained'] for x in status),current_failure_flag=failed)
def wrap_trace_persist(original):
    @functools.wraps(original)
    def persist(self):
        result=original(self)
        apply_retention(self.folder,self.index)
        return result
    return persist
