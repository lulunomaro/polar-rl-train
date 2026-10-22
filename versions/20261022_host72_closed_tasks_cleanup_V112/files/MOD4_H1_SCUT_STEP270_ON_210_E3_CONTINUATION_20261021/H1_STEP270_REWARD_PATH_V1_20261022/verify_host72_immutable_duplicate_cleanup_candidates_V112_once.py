from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,os,shutil,time
base=Path('/home/lc01/Zonglin Li/zonglin2/tasks');started=time.time();out=[];issues=[]
for group in v['groups']:
    checked=[]
    for row in [group['keeper']]+group['copies']:
        assert time.time()-started<180,'Bounded candidate verification elapsed'
        p=Path(row['path']);assert p.resolve(strict=True).is_relative_to(base) and not p.is_symlink()
        ex=json.loads((Path(row['closed_node'])/'NODE_EXIT_ACTUAL.json').read_bytes())
        assert ex['actual_all_own_children_waited'] and ex['validation_fcntl_released_if_acquired']
        s=p.stat();assert s.st_size==row['bytes'] and s.st_ino==row['inode'] and s.st_mtime_ns==row['mtime_ns'] and s.st_nlink==1
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
        z=p.stat();assert (s.st_size,s.st_ino,s.st_mtime_ns,s.st_nlink)==(z.st_size,z.st_ino,z.st_mtime_ns,z.st_nlink)
        assert h.hexdigest()==row['producer_SHA']==group['SHA']
        checked.append(dict(row,actual_full_SHA=h.hexdigest(),mode=s.st_mode,uid=s.st_uid,gid=s.st_gid))
    keeper=checked[0];copies=[]
    for x in checked[1:]:
        if (x['mode'],x['uid'],x['gid'],x['device'])!=(keeper['mode'],keeper['uid'],keeper['gid'],keeper['device']):
            issues.append(dict(path=x['path'],reason='Mode/owner/group/device differs; no path replacement proposed'))
        else:copies.append(x)
    if copies:out.append(dict(SHA=group['SHA'],bytes=group['bytes'],keeper=keeper,copies=copies,possible_released_allocated_bytes=sum(x['allocated_bytes'] for x in copies)))
disk=shutil.disk_usage(base)
print(json.dumps(dict(epoch=time.time(),groups=out,excluded=issues,actual_full_SHA_verified=True,
  exact_closure_identity_and_size_inode_mtime_nlink_before_after_bound=True,
  duplicate_files=sum(len(x['copies']) for x in out),potential_released_allocated_bytes=sum(x['possible_released_allocated_bytes'] for x in out),
  proposal='Atomic path-preserving hardlink deduplication, every exact path and byte remains; mtime/inode/nlink changes would be explicitly receipted.',
  no_deletion_link_replace_chmod_or_remote_file_write_performed=True,
  no_unique_data_pruning_authorized_by_this_verification=True,
  no_GPU_model_load_optimizer_actor_budget_process_peer_identity_query=True,
  elapsed=time.time()-started,filesystem_free_snapshot=disk.free)))
'''
try:
    candidate=json.loads((R/'V112_MANIFEST_BOUND_IMMUTABLE_INPUT_DUPLICATE_CANDIDATES_CPU_ACTUAL.json').read_bytes())
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    secret=m.recover()
    try:c=d.connect72(secret)
    finally:secret=None
    try:result=d.code(c,d.PY72,CODE,dict(groups=candidate['candidate_groups']),timeout=210)
    finally:c.close()
    put('V112_HOST72_IMMUTABLE_DUPLICATE_ACTUAL_FULL_SHA_VERIFIED_REVIEWABLE_CANDIDATES.json',result)
    print(json.dumps(dict(groups=len(result['groups']),files=result['duplicate_files'],potential_released_bytes=result['potential_released_allocated_bytes'],excluded=result['excluded'],actual_fullSHA_verified=result['actual_full_SHA_verified'],no_mutation=True)))
except BaseException:
    put('V112_DUPLICATE_FULL_SHA_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
