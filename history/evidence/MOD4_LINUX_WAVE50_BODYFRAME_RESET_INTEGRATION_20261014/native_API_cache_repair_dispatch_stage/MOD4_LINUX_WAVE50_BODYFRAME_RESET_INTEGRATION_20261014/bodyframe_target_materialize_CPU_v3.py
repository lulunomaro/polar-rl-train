"""Single new target creation under original two locks; CPU only."""
from pathlib import Path
import hashlib,json,os,sys,time,shutil,fcntl,traceback

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def write(p,v):
    with Path(p).open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())

def main(context):
    stage=Path(context['upload_stage']);root=Path(context['root']);base=Path(context['base']);old=Path(context['old'])
    assert root.parent==base and stage.parent==base and not root.exists()
    for name,h in context['files'].items():
        assert Path(name).name==name and sha(stage/name)==h
        if name.endswith('.py'):compile((stage/name).read_bytes(),str(stage/name),'exec')
    sys.path.insert(0,str(stage));import bodyframe_original_CPU_guard as g
    locks=[];created=False
    try:
        for path in g.LOCKS:
            f=path.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        d=json.loads(g.B.read_bytes());g.budget_guard(d);budget_before=sha(g.B)
        import psutil,subprocess,torch,numpy as np
        assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(base).free>=30000000000
        assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
        first=base/'left_exploration20k_first_formal_v1'
        original=json.loads((first/'LEFT_FORMAL_ADMISSION_MANIFEST.json').read_bytes());assert len(original['sourcefreeze'])==522
        ready=json.loads((old/'LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json').read_bytes());source=Path(ready['own_checkpoint'])
        assert ready['checkpoint_sha256']==context['source_SHA'] and sha(source)==context['source_SHA'] and source.stat().st_size==19044152
        root.mkdir();created=True;runtime=root/'base_runtime';runtime.mkdir()
        rows=[]
        for item in original['sourcefreeze']:
            p=Path(item['path']);assert p.resolve().is_relative_to(first.resolve()) and p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
            relative=p.relative_to(first);target=runtime/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
            assert sha(target)==item['sha256'];rows.append(dict(path=str(target),relative=str(relative),sha256=item['sha256'],bytes=target.stat().st_size))
        active=[]
        for name,h in context['files'].items():
            dst=root/name;shutil.copy2(stage/name,dst);assert sha(dst)==h
            active.append(dict(name=name,sha256=h,bytes=dst.stat().st_size))
        rng=torch.get_rng_state().clone();assert not torch.cuda.is_initialized()
        ck=torch.load(source,map_location='cpu',weights_only=False);info=g.logical_fullsave(ck);fingerprint=g.tree_sha(ck)
        disk=root/'E3_WHOLESTATE_CPU_EVIDENCE_NOT_SOURCE.pt';torch.save(ck,disk)
        with disk.open('r+b') as f:os.fsync(f.fileno())
        loaded=torch.load(disk,map_location='cpu',weights_only=False);assert g.same(ck,loaded)
        for key,tensor in g.walk(ck):
            other=dict(g.walk(loaded))[key]
            if tensor.numel():assert tensor.untyped_storage().data_ptr()!=other.untyped_storage().data_ptr()
        negatives=g.negative_logical_checks(ck)
        sys.path.insert(0,str(root));from birth_bodyframe_state_v1 import from_whole_predecessor
        from birth_bodyframe_full_checkpoint_v4 import bindings_from_checkpoint
        state=from_whole_predecessor(ck,context['source_SHA'],bindings_from_checkpoint(ck));assert int(state['wave_mask'].sum())==2820
        assert g.tree_sha(ck)==fingerprint and sha(source)==context['source_SHA'] and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
        assert sha(g.B)==budget_before
        result=dict(epoch=time.time(),passed=True,target_CPU_actual=True,source=rec(source),source_CPU=info,source_tree_SHA=fingerprint,
            whole195_independent_CPU_disk_roundtrip=True,disk_evidence_NOT_source=rec(disk),negative_cases=negatives,
            original522_runtime_bytes_exact=True,base_runtime=rows,active_files=active,original_environment=original['original_environment'],
            canonical_bytes_unchanged=budget_before,GPU_dispatched=False,approved_PPO_before_native_and_fullrestore=False)
        write(root/'PIPELINE_TARGET_CPU_ACTUAL.json',result)
        print(json.dumps(dict(passed=True,root=str(root),source=rec(source),source_CPU=info,base522=True,active_count=len(active),target_receipt=rec(root/'PIPELINE_TARGET_CPU_ACTUAL.json'),GPU_dispatched=False)))
    except BaseException:
        write((root if created else stage)/('BODYFRAME_TARGET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),new_root_created=created,no_GPU_or_budget_write=True))
        raise
    finally:
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()

if __name__=='__main__':main(CONTEXT)
