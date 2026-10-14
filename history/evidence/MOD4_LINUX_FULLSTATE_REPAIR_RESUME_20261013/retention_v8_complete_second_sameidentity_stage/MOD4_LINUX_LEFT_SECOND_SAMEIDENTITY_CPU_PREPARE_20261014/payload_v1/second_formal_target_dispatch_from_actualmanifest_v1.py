"""Futureunique dispatch only after independent targetCPU/full4case actualgate."""
from pathlib import Path
import os,sys,json,time,subprocess,traceback,fcntl
def write(p,v):
    p=Path(p);q=p.with_name(p.name+'.partial')
    with q.open('xb') as f:f.write(json.dumps(v,indent=2).encode());f.flush();os.fsync(f.fileno())
    os.replace(q,p)
    fd=os.open(p.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(context):
    root=Path(context['proposed_root']);sys.path.insert(0,str(root));import second_target_CPU_pure_guard_v2 as g
    assert root==g.ROOT and context['source_SHA']==g.SOURCE_SHA
    mpath=root/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json';assert g.sha(mpath)==context['actual_manifest_SHA']
    m=json.loads(mpath.read_bytes());assert m['approved_GPU'] is True and m['target_CPU_actual_passed'] is True and m['actual_GPU_dispatched'] is False
    assert m['source']['path']==str(g.SOURCE) and m['source']['sha256']==g.SOURCE_SHA
    assert m['duration_seconds']==3600 and m['scope_learning_block_index']==2 and m['max_blocks_same_axis']==2 and m['planned_first_plus_second_seconds']==7200
    decision=m['actual_four_case_scope_decision'];assert g.sha(decision['path'])==decision['sha256']
    g.validate_evidence_packet(json.loads(Path(decision['path']).read_bytes()),{k:v['path'] for k,v in m['actual_four_case_evidence_files'].items()})
    proof=m['target_CPU_actual_proof'];assert g.sha(proof['path'])==proof['sha256'] and json.loads(Path(proof['path']).read_bytes())['passed'] is True
    assert len(m['sourcefreeze'])>=522
    for x in m['sourcefreeze']:assert g.sha(x['path'])==x['sha256'],x['path']
    assert not (root/'LEFT_SECOND_FORMAL_ONCE_CONSUMED.json').exists() and not (root/'LEFT_SECOND_DISPATCH_INTENT.json').exists()
    assert not (root/'PARENT_IDENTITY.json').exists()
    locks=[]
    try:
        for p in g.LOCKS:
            f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        boundary=g.boundary_and_resources();before=g.sha(g.B)
        import torch
        assert not torch.cuda.is_initialized()
        c=torch.load(g.SOURCE,map_location='cpu',weights_only=False);g.logical_fullsave(c)
        assert g.sha(g.B)==before
        # Consumeone dispatchintent before Popen. Unknowntransportoutcome MUST
        # inspectactualreceipt/process/canonical; neverblindretry this dispatcher.
        argv=[context['python'],'-u',str(root/'left_second_sameidentity_typed_parent_v1.py')]
        write(root/'LEFT_SECOND_DISPATCH_INTENT.json',dict(epoch=time.time(),argv=argv,cwd=str(root),source=m['source'],actual_manifest_SHA=g.sha(mpath),canonical_before=before,GPU_PPO_NOT_yet_claimed=True))
    finally:
        # Originaluniqueparent reacquires the sameglobal locks and owns allcost.
        # Dispatcher makesno budgetwrite and neverholdslocks across childlaunch.
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
    env=os.environ.copy();env.pop('CUDA_VISIBLE_DEVICES',None);env.pop('MOD4_LEFT_ADMISSION_MODE',None)
    child=subprocess.Popen(argv,cwd=root,env=env,stdout=(root/'left_second_formal_parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
    try:
        stat=Path('/proc',str(child.pid),'stat').read_text();start_ticks=int(stat.split(') ',1)[1].split()[19])
    except FileNotFoundError:start_ticks=None
    out=dict(epoch=time.time(),pid=child.pid,start_ticks=start_ticks,parent_immediate_returncode=child.poll(),argv=argv,cwd=str(root),source=m['source'],manifest_SHA=g.sha(mpath),actual_sourcefreeze_count=len(m['sourcefreeze']),second_bounded_formal_seconds=3600,actual_startup_PPO_ownsave_proof_pending=True,PPO_claimed=False,dispatcher_budget_write=False,qualified50=False)
    write(root/'LEFT_SECOND_FORMAL_DISPATCH_ACTUAL.json',out);print(json.dumps(out))
if __name__=='__main__':
    try:main(CONTEXT)
    except BaseException:
        root=Path(CONTEXT['proposed_root'])
        if root.is_dir():write(root/('LEFT_SECOND_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),unknown_launch_outcome_requires_actual_inspection_not_retry=True,no_budget_write=True))
        raise
