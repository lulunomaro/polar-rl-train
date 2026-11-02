"""Read ONLY known local JSON/py metadata; join actual historical close to8d cert.
No PT/raw telemetry/SSH/SDK/GPU/C/GO operations. All writes child source_v2 only.
"""
from pathlib import Path
import ast,difflib,hashlib,json,sys
B=Path(__file__).resolve().parent;D=B.parent;T=D.parent;sys.path.insert(0,str(B))
import w35_posttrain_source_builder_v2 as s

def read(path):
    p=Path(path);assert p.suffix in('.py','.json','.patch')
    return p.read_bytes()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8')as f:json.dump(value,f,indent=2,ensure_ascii=False)

def main():
    cp=T/'staged_sources/W35_NEW8D_GPU_FULLRESTORE_CERTIFICATE_V1/CERTIFICATE_INDEX.json'
    tp=T/'reports/W35_after_resume89aca_eval_terminal_watch_20261102_080039.json'
    ap=T/'reports/W35_NEW8D_ADMISSION_METADATA_20261102_071212.json'
    cb=read(B/s.GPU_CERT_FILE);ib=read(cp);tb=read(tp);ab=read(ap)
    cert=json.loads(cb);ci=json.loads(ib);terminal=json.loads(tb);admission=json.loads(ab)
    root=terminal['job'];fin=terminal['FINAL'];exit=terminal['parent_exit'];rows=fin['rows']
    task=terminal['files']['TASK_PENDING.json'];facts=rows['ACTUAL227_CLOSED_RM70_SKILL_FACTS.json'];guard=rows['MOD4V1_FULLRESTORE_GUARD_ACTUAL.json']
    assert sha(cb)==ci['SHA']==s.GPU_CERT_SHA and len(cb)==ci['bytes']
    assert ci['remote_path']==root+'/actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json'
    assert admission['job']==task['runtime_job']==root
    assert admission['files']['TASK_ADMITTED.json']['runtime_job']==root
    assert cert['source_SHA']==ci['newsource_model_SHA']==facts['source_SHA']==task['model_SHA']==s.SHA
    assert cert['source_cache']['selected_source_path']==facts['source_cache']['selected_source_path']==task['model_path']==s.MODEL
    assert cert['source_cache']['source_bytes']==facts['source_cache']['source_bytes']==task['model_bytes']==s.BYTES
    assert cert['iteration']==task['model_iteration']==s.ITER and cert['Adam17']==task['Adam17']==s.ADAM and cert['actual_LR']==s.LR
    assert fin['passed_execution'] and fin['returncode']==0 and not fin['errors'] and fin['bounded32s_complete']
    assert exit['all_own_children_waited'] and exit['owned_private_validation_locks_released'] and exit['error']is None
    assert guard['num_envs']==task['num_envs']==20000 and guard['usd_sha256']==s.USD and guard['contract_sha256']==s.CONTRACT
    assert guard['original_fresh_reset_calls']==1 and guard['new_constructor_nominal_caches_preserved']
    assert cert['passed'] and cert['actor_critic_STD_optimizer_verified'] and cert['original_D0_D7_then_one_new_episode']
    assert facts['core_and_17Adam_unchanged'] and facts['optimizer_steps']==0
    refs=[]
    for rel,src,raw in [('INPUT8D_GPU_FULLRESTORE_ACTUAL.json',B/s.GPU_CERT_FILE,cb),
        ('evidence/W35_NEW8D_CERTIFICATE_INDEX_RAW_METADATA.json',cp,ib),
        ('evidence/W35_NEW8D_FULL32_CLOSED_RAW_METADATA.json',tp,tb),
        ('evidence/W35_NEW8D_ADMISSION_RAW_METADATA.json',ap,ab)]:
        if rel!=s.GPU_CERT_FILE:
            dst=B/rel;dst.parent.mkdir(parents=True,exist_ok=True)
            with dst.open('xb')as f:f.write(raw)
        refs.append(dict(relative=rel,original_local_path=str(src),bytes=len(raw),SHA=sha(raw)))
    proof=dict(kind='NORMALIZED_EXISTING_ACTUAL_W35_NEW8D_FULL20K_RESTORE_AND_CLOSE_HISTORY',
        actual_not_mock=ci['kind'].startswith('ACTUAL_NEW8D_') and fin['passed_execution'] and fin['returncode']==0,
        source_SHA=cert['source_SHA'],source_bytes=cert['source_cache']['source_bytes'],source_iteration=cert['iteration'],
        source_17Adam=cert['Adam17'],actual_LR=cert['actual_LR'],asset_USD_SHA=guard['usd_sha256'],asset_contract_SHA=guard['contract_sha256'],
        num_envs=guard['num_envs'],whole_state_restore_passed=cert['passed'] and cert['actor_critic_STD_optimizer_verified']
            and cert['original_D0_D7_then_one_new_episode'] and facts['core_and_17Adam_unchanged'],
        all_own_children_waited=exit['all_own_children_waited'],returncode=fin['returncode'],errors=fin['errors'],
        parent_exit_error=exit['error'],original_private_locks_released=exit['owned_private_validation_locks_released'],
        remote_root=root,certificate_remote_path=ci['remote_path'],raw_byte_refs=refs,
        field_evidence=dict(actual_not_mock='certificate-index.kind ACTUAL_NEW8D + terminal.FINAL passed_execution/returncode0; all same remoteRoot',
            whole_state_restore_passed='3571B certificate passed/coreSTDoptimizer/D0D7 + same closed case facts.core_and_17Adam_unchanged',
            all_own_children_waited='terminal.parent_exit.all_own_children_waited (not invented from before-control certificate)',
            assets_and_num_envs='terminal.FINAL.rows.MOD4V1_FULLRESTORE_GUARD_ACTUAL.json'),
        historical_full32_execution=dict(controls=facts['controls'],physics=facts['physics'],feedback=facts['feedback'],bounded32s_complete=fin['bounded32s_complete']),
        current_training_live_restore_already_passed=False,RM70_skill_graduated=False,normalizer_PT_or_raw_reads_by_this_join=0)
    relative='evidence/W35_NEW8D_FULL20K_CLOSED_HISTORY_PROOF_V2.json';put(B/relative,proof)
    # Refresh only the dedicated NEW unused SOURCE index, never original IDX.
    idx_path=B/s.DERIVATION_FILE;idx=json.loads(read(idx_path));idx['outputs']=[s.source_row(B,n)for n in(s.WORKER,s.PROTOCOL)]
    idx_path.write_text(json.dumps(idx,indent=2,ensure_ascii=False),encoding='utf-8')
    desc_path=B/s.DESCRIPTOR;desc=json.loads(read(desc_path));desc['source_runtime_files']=[s.source_row(B,n)for n in(s.WORKER,s.PROTOCOL,'w35_posttrain_source_builder_v2.py',s.GPU_CERT_FILE)]
    desc['historical_whole20k_closed_proof']=dict(relative=relative,local_path=str(B/relative),SHA=s.file_sha(B/relative),raw_byte_refs=refs,remote_root=root)
    desc['test_report']='W35_SOURCE_AST_MOCK_REVIEW_V2_FINAL_SEALED.json'
    desc['parent_entry_fields'].update(actual_prior_full20k_proof_file=relative,native0pt_evidence_file='evidence/NEW_ASSET_NATIVE_ACTUAL.json',target_source_SDK_receipt_file=s.GPU_CERT_FILE)
    desc['required_runtime_uploads']+= [relative]+[r['relative']for r in refs if r['relative']!=s.GPU_CERT_FILE]
    desc['do_not_upload_stage_generated_index']=s.DERIVATION_FILE
    desc_path.write_text(json.dumps(desc,indent=2,ensure_ascii=False),encoding='utf-8')
    diffs=[]
    for old,new in [('worker_mod4v1_w35_posttrain20_v1.py',s.WORKER),('mod4v1_w35_posttrain_protocol_v1.py',s.PROTOCOL)]:
        a=read(D/'source_w35'/old).decode('utf-8-sig');b=read(B/new).decode('utf-8-sig')
        diffs+=list(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='preserved_source_w35/'+old,tofile='unused_source_w35_v2/'+new))
    with (B/'SOURCE_V1_TO_V2_FINAL_DIFF.patch').open('x',encoding='utf-8')as f:f.write(''.join(diffs))
    put(B/'SOURCE_TEST_AND_HISTORY_JOIN_ERRATUM_V2.json',dict(status='SOURCE_ONLY_NO_NEW_SDK_OR_GO',
        first_test_failure='Initial textual no-assignment check misread == as =; actual AST assignment-target check already passed. Historical failed report retained.',
        correction='Use AST assignment targets only; final tests rerun after full source sealing.',
        final_prelearning_stop='Also honor pre-existing original health/output STOP flags before any update, without changing original update/save boundary policy.',
        historical_proof='Joined actual8d3571B BEFORE certificate to existing same-root full32 RC0 parent allwait/lockrelease metadata, not filling closed=True on certificate',
        raw_refs=refs,old_sources_parent_owner_and_stager_edited=False,PT_SDK_GPU_C_GO_operations=0))
    print(json.dumps(dict(status='HISTORICAL8D_CLOSED_PROOF_JOINED_SOURCE_SEALED',proof=str(B/relative),remote_root=root,allwait=proof['all_own_children_waited'],RC=proof['returncode'],PT_SDK_GO=0),indent=2))
if __name__=='__main__':main()
