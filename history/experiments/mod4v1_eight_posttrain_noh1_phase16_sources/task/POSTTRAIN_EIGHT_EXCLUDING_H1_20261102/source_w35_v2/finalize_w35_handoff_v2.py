"""Seal minimal nonPT source upload Spec after focused AST/mock review."""
from pathlib import Path
import ast,hashlib,json,sys
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
import w35_posttrain_source_builder_v2 as s

def main():
    report=json.loads((B/'W35_SOURCE_AST_MOCK_REVIEW_V2_FINAL_SEALED.json').read_bytes())
    assert report['all_passed'] and report['PT_open_stat_hash_decode']==0
    desc_path=B/s.DESCRIPTOR;desc=json.loads(desc_path.read_bytes())
    desc['parent_entry_fields']['source_contract_AST_MOCK_passed']=True
    desc['source_contract_AST_MOCK_passed']=True
    desc_path.write_text(json.dumps(desc,indent=2,ensure_ascii=False),encoding='utf-8')
    names=desc['required_runtime_uploads']
    assert s.DERIVATION_FILE not in names
    upload=[s.source_row(B,n)for n in names]
    entry=dict(desc['parent_entry_fields'])
    entry['base_root']=desc['runtime_root_base_remote']
    entry['required_immutable_files']+= [s.source_row(B,n)for n in names if n.startswith('evidence/')]
    proof=json.loads((B/entry['actual_prior_full20k_proof_file']).read_bytes())
    spec=dict(status='SOURCE_READY_FOR_PARENT_STAGE_NOT_ACTUAL_ADMISSION_NOT_TRAINING_PASS',role='W35',source_family='w35',
        base_root=desc['runtime_root_base_remote'],entry=entry,
        parent_must_supply=['unused job_root','unique role_key','historical_geometry_evidence_file from actual existing RM70 geometry proof',
            'stage evidence/NEW_ASSET_NATIVE_ACTUAL.json from actual existing native0PT proof'],
        upload_files=[dict(**r,local_path=str(B/r['relative']))for r in upload],
        upload_bundle_SHA=hashlib.sha256(json.dumps(upload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        DO_NOT_UPLOAD_local_stage_generated_index=s.DERIVATION_FILE,
        stage_generated=dict(file=s.DERIVATION_FILE,creator='w35_posttrain_source_builder_v2.create_derivation_from_installed_source(dst)',
            outputs_only=[s.WORKER,s.PROTOCOL],old_IDX_untouched='MOD4V1_DERIVATION_INDEX.json'),
        pure_templates='w35_posttrain_source_builder_v2.build_source_templates(*, job_root, run_id, role_key, manifest_SHA)',
        required_fields_file='W35_REQUIRED_PARENT_FIELDS_V2.json',
        normalized_historical_proof=desc['historical_whole20k_closed_proof'],
        actual_prior_proof_fields={k:proof[k]for k in('actual_not_mock','source_SHA','asset_USD_SHA','asset_contract_SHA','num_envs',
            'whole_state_restore_passed','all_own_children_waited','returncode','remote_root')},
        final_receipt='production/FINAL.json',final_checkpoint='production/model_final_complete.pt',
        actual_updates_key='actual_new_PPO_updates',saved_iter_key='final.saved_iteration (unmodified original RSL value)',
        tests=dict(path=str(B/'W35_SOURCE_AST_MOCK_REVIEW_V2_FINAL_SEALED.json'),passed=4,actual_SDK_or_PPO=False),
        new_model_PT_SDK_GPU_C_GO_Git_or_owner_lock_actions=0,H1_excluded=True,
        original_budget_lock_lifecycle_changed=False,old_source_w35_and_89aca_and_original_IDX_edited=False,
        notes=['Task.kind/install.kind/deriv.kind match parent W35 branch and generic stager',
            'source_read_purpose remains parent string; source_read_plan is separate independent count plan',
            'Generic manifest binds dedicated derivation through files[] row, no top-level derivation_index_SHA required',
            'No raw iteration/LR/STD writes; save/stop occurs after original log publication, update/minibatch arithmetic only assertions',
            'Original known live save roots validated before unknown-root union; whole cached source RAM truth unchanged',
            '3571B certificate alone is not allwait evidence; normalized proof joins same-root actual full32 RC0 close metadata',
            'Source Ready and historical proof are not current-training live restore or skill pass'])
    with (B/'W35_PARENT_STAGE_SPEC_V2.json').open('x',encoding='utf-8')as f:json.dump(spec,f,indent=2,ensure_ascii=False)
    names_all=names+[s.DERIVATION_FILE,'W35_REQUIRED_PARENT_FIELDS_V2.json','W35_SOURCE_TASK_GO_DRAFT_EXAMPLE_V2.json',
        'SOURCE_REVIEW_ERRORS_AND_FIXES_V2.json','SOURCE_TEST_AND_HISTORY_JOIN_ERRATUM_V2.json','SOURCE_V1_TO_V2_DIFF.patch',
        'SOURCE_V1_TO_V2_FINAL_DIFF.patch','W35_SOURCE_AST_MOCK_REVIEW_V2.json','W35_SOURCE_AST_MOCK_REVIEW_V2_FINAL.json',
        'W35_SOURCE_AST_MOCK_REVIEW_V2_FINAL_SEALED.json','derive_w35_source_v2.py','prepare_w35_metadata_v2.py',
        'seal_w35_history_and_source_v2.py','test_w35_source_v2.py','finalize_w35_handoff_v2.py','W35_PARENT_STAGE_SPEC_V2.json']
    files=[]
    for name in dict.fromkeys(names_all):
        p=B/name;assert p.suffix in('.py','.json','.patch')
        raw=p.read_bytes()
        if p.suffix=='.py':compile(ast.parse(raw.decode('utf-8-sig')),str(p),'exec')
        files.append(dict(relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    result=dict(status=spec['status'],child_root=str(B),stage_spec=s.source_row(B,'W35_PARENT_STAGE_SPEC_V2.json'),
        upload_bundle_SHA=spec['upload_bundle_SHA'],all_child_text_files_for_parent_Git_archive=files,
        runtime_sources=upload,normalized_actual_old_proof=desc['historical_whole20k_closed_proof'],
        source_only_AST_MOCK_groups_passed=4,new_PT_SDK_GPU_PPO_C_GO_Git_or_agents=0,
        no_budget_or_lock_lifecycle_changes=True,no_actual_new_training_pass_claim=True)
    with (B/'FINAL_W35_SOURCE_HANDOFF_INDEX_V2.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,ensure_ascii=False)
    print(json.dumps(dict(status=spec['status'],final_index=str(B/'FINAL_W35_SOURCE_HANDOFF_INDEX_V2.json'),
        stage_spec=str(B/'W35_PARENT_STAGE_SPEC_V2.json'),upload_bundle_SHA=spec['upload_bundle_SHA'],
        upload_files=upload,normalized_proof_SHA=s.file_sha(B/entry['actual_prior_full20k_proof_file']),tests_passed=4),indent=2))
if __name__=='__main__':main()
