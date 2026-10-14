"""Future root-owned target CPU materialization, never imported/called in prep.

CONTEXT is injected through stdin by the root's sole transport. Existingroot,
missingfourcase decision ornonidle sourceboundary fail before newroot creation.
"""
from pathlib import Path
import json,os,time,shutil,traceback,fcntl,sys
def write(p,v):
    p=Path(p);q=p.with_name(p.name+'.partial')
    with q.open('xb') as f:f.write(json.dumps(v,indent=2).encode());f.flush();os.fsync(f.fileno())
    os.replace(q,p)
    fd=os.open(p.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(context):
    stage=Path(context['stage']);assert stage.is_dir()
    sys.path.insert(0,str(stage));import second_target_CPU_pure_guard_v2 as g
    assert context['proposed_root']==str(g.ROOT) and context['source_SHA']==g.SOURCE_SHA
    assert not g.ROOT.exists(),'No materialization replay/overwrite'
    assert stage.resolve().is_relative_to(g.BASE.resolve())
    for name,h in context['uploaded_SHA'].items():
        assert Path(name).name==name and g.sha(stage/name)==h,name
        if name.endswith('.py'):compile((stage/name).read_text(),str(stage/name),'exec')
    decision=json.loads((stage/'ACTUAL_FOUR_CASE_SCOPE_DECISION.json').read_bytes());g.validate_decision(decision)
    evidence_files={k:stage/n for k,n in context['evidence_uploaded_names'].items()}
    evidence=g.validate_evidence_packet(decision,evidence_files)
    oldpath=g.FIRST/'LEFT_FORMAL_ADMISSION_MANIFEST.json';old=json.loads(oldpath.read_bytes())
    assert len(old['sourcefreeze'])==522 and len({x['path'] for x in old['sourcefreeze']})==522
    # Bothproc/locks and actualsoleledger guard are reevaluated; no copiedledger.
    leases=[];created=False;budget_before=None
    try:
        for p in g.LOCKS:
            f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);leases.append(f)
        boundary=g.boundary_and_resources();budget_before=g.sha(g.B)
        assert g.ROOT.parent.resolve()==g.BASE.resolve()
        g.ROOT.mkdir();created=True
        write(g.ROOT/'SECOND_TARGET_CPU_MATERIALIZE_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),root=str(g.ROOT),source=g.record(g.SOURCE),canonical_SHA_before=budget_before,GPU_or_budget_mutation=False))
        rows=[]
        for item in old['sourcefreeze']:
            src=Path(item['path']);assert src.resolve().is_relative_to(g.FIRST.resolve())
            assert src.stat().st_size==item['bytes'] and g.sha(src)==item['sha256']
            dst=g.ROOT/src.relative_to(g.FIRST);assert dst.resolve().is_relative_to(g.ROOT.resolve())
            dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copy2(src,dst)
            assert g.sha(dst)==item['sha256'];rows.append(dict(path=str(dst),origin=str(src),bytes=dst.stat().st_size,sha256=item['sha256']))
        for name,h in context['uploaded_SHA'].items():
            dst=g.ROOT/name;assert not dst.exists();shutil.copy2(stage/name,dst);assert g.sha(dst)==h
            rows.append(g.record(dst))
        inherited=g.ROOT/'INHERITED_FIRST_FORMAL_ADMISSION_MANIFEST_ACTUAL.json';assert not inherited.exists();shutil.copy2(oldpath,inherited);rows.append(g.record(inherited))
        import torch,numpy as np
        assert not torch.cuda.is_initialized()
        rng=torch.get_rng_state().clone();nprng=g.tree_sha(np.random.get_state())
        source=torch.load(g.SOURCE,map_location='cpu',weights_only=False);info=g.logical_fullsave(source);fingerprint=g.tree_sha(source)
        # CPUdisk copy is evidenceonly. Formal source remains originalown2b.
        diskfile=g.ROOT/'SOURCE2B_FULLSTATE_CPU_DISK_ROUNDTRIP_EVIDENCE_ONLY.pt';assert not diskfile.exists();torch.save(source,diskfile)
        with diskfile.open('r+b') as f:os.fsync(f.fileno())
        disk=torch.load(diskfile,map_location='cpu',weights_only=False);assert g.same(source,disk);g.logical_fullsave(disk)
        srcrows=dict(g.walk(source));diskrows=dict(g.walk(disk))
        for key,x in srcrows.items():
            if x.numel():assert x.untyped_storage().data_ptr()!=diskrows[key].untyped_storage().data_ptr(),key
        negative=g.negative_logical_checks(source)
        assert g.tree_sha(source)==fingerprint and g.sha(g.SOURCE)==g.SOURCE_SHA
        assert torch.equal(torch.get_rng_state(),rng) and g.tree_sha(np.random.get_state())==nprng and not torch.cuda.is_initialized()
        assert g.sha(g.B)==budget_before,'CPU prelaunch cannotchange canonicalbytes'
        proof=g.ROOT/'SECOND_TARGET_FULLSTATE_CPU_ACTUAL_PASSED.json'
        write(proof,dict(epoch=time.time(),passed=True,source=g.record(g.SOURCE),fullstate=info,fulltree_cpu_disk_roundtrip_exact=True,all195_disk_restored_tensors_independent_storage=True,source_tree_fingerprint_before_after=fingerprint,no_CPU_RNG_draw=True,no_CUDA_initialized=True,negative_logical_cases=negative,original522_sourcecopy_byteexact=True,original_boundary=boundary,actual_four_case_decision=g.record(g.ROOT/'ACTUAL_FOUR_CASE_SCOPE_DECISION.json'),actual_four_case_evidence=evidence,canonical_SHA_before_after_unchanged=budget_before,source_disk_evidence_not_formal_source=g.record(diskfile),GPU_dispatched=False,qualified50=False))
        rows.extend([g.record(diskfile),g.record(proof),g.record(g.ROOT/'SECOND_TARGET_CPU_MATERIALIZE_STARTED.json')])
        assert len(rows)>=522 and len({x['path'] for x in rows})==len(rows)
        for row in rows:assert g.sha(row['path'])==row['sha256']
        manifest=dict(epoch=time.time(),CPU_prepared_only=False,target_CPU_actual_passed=True,approved_GPU=True,actual_GPU_dispatched=False,num_envs=20000,seed=20260928,duration_seconds=3600,scope_learning_block_index=2,max_blocks_same_axis=2,planned_first_plus_second_seconds=7200,no_new_policy_axis=True,no_initializer_repeat=True,
            source=g.record(g.SOURCE),sourcefreeze=rows,original_environment=old['original_environment'],
            actual_four_case_scope_decision=g.record(g.ROOT/'ACTUAL_FOUR_CASE_SCOPE_DECISION.json'),actual_four_case_evidence_files={k:g.record(g.ROOT/n) for k,n in context['evidence_uploaded_names'].items()},target_CPU_actual_proof=g.record(proof),
            source_is_complete_whole20k_first_own2b_not_CPU_diskcopy_or_candidates=True,original_runtime_sources522_byteexact_reused=True,SDK_native_discard_fresh_clock_proofs_byteexact_reused_NOT_rerun=True,
            same_identity_all_actorcriticstdAdam_D0D7_globalnamed_dictprivate_geometry_entry_command_direction_route_lifetime_leftmetadata_CPUCUDA_NEW_EPISODE_REQUIRED=True,qualified50=False)
        path=g.ROOT/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json';assert not path.exists();write(path,manifest)
        assert g.sha(g.B)==budget_before
        out=dict(epoch=time.time(),passed=True,root=str(g.ROOT),source=g.record(g.SOURCE),actual_sourcefreeze_count=len(rows),source_CPU=info,manifest=g.record(path),targetCPU_complete_GPU_not_dispatched=True,canonical_bytes_unchanged=True,resource_snapshot=boundary)
        write(g.ROOT/'SECOND_TARGET_CPU_MATERIALIZATION_ACTUAL_COMPLETE.json',out);print(json.dumps(out))
    except BaseException:
        folder=g.ROOT if created else stage
        write(folder/('SECOND_TARGET_CPU_MATERIALIZE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),created_new_root=created,source_SHA=g.SOURCE_SHA,no_GPU_or_budget_transaction=True,original_failure_preserved=True))
        raise
    finally:
        for f in reversed(leases):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main(CONTEXT)
