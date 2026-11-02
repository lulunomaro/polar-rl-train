"""Hash/AST only the explicit child TEXT deliverables, never model/SDK/ledger.
Create one SOURCE_ONLY handoff index; no Task/GO/Ready/actual install manifest.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
from posttrain_fullstate_common_v1 import EXPERTS, POSTTRAIN_KIND, ADMISSION_KIND
NAMES = [
    'posttrain_fullstate_common_v1.py', 'worker_posttrain_e0_v1.py', 'worker_posttrain_e2_v1.py', 'worker_posttrain_e3_v1.py',
    'construct_source_task_go_v1.py', 'build_source_handoff_v1.py', 'check_ast_mock_v1.py', 'finalize_source_review_v1.py',
    'E0_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json', 'E2_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json', 'E3_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json',
    'PARENT_REQUIRED_FIELDS_SOURCE_ONLY_V1.json', 'MOCK_SOURCE_CONSTRUCTION_EXAMPLE_V1.json',
    'SOURCE_API_AND_ACTUAL_PROOF_INDEX_V1.json', 'SOURCE_REVIEW_HISTORY_V1.json', 'SOURCE_REVIEW_ADDENDUM_V1.json',
    'AST_MOCK_REVIEW_V1.json', 'AST_MOCK_REVIEW_V2_WITH_CACHE_ALIAS_AND_CONSTRUCTOR.json', 'README_SOURCE_HANDOFF_V1.md',
]


def main():
    rows = []
    for name in NAMES:
        p = B / name
        assert p.suffix in ('.py', '.json', '.md')
        raw = p.read_bytes()
        if p.suffix == '.py': compile(ast.parse(raw.decode('utf-8-sig')), str(p), 'exec')
        if p.suffix == '.json': json.loads(raw)
        rows.append(dict(relative=name, path=str(p), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest()))
    by_name = {r['relative']: r for r in rows}
    report = json.loads((B / 'AST_MOCK_REVIEW_V2_WITH_CACHE_ALIAS_AND_CONSTRUCTOR.json').read_bytes())
    assert report['all_passed'] and len(report['tests']) == 8
    assert report['real_model_PT_opens'] == report['real_model_PT_stats'] == report['real_torch_imports'] == 0
    api = json.loads((B / 'SOURCE_API_AND_ACTUAL_PROOF_INDEX_V1.json').read_bytes())
    role_rows = {}
    for role, cfg in EXPERTS.items():
        entry = 'worker_posttrain_' + role.lower() + '_v1.py'
        descriptor = role + '_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json'
        desc = json.loads((B / descriptor).read_bytes())
        assert desc['seed'] == 20260928 and desc['steps_per_env'] == 24
        role_rows[role] = dict(pinned_source_metadata_only=cfg,
            worker_entry=by_name[entry], common=by_name['posttrain_fullstate_common_v1.py'], descriptor=by_name[descriptor],
            historical_nonmodel_complete_runtime_root=api['roles'][role]['historical_remote_nonmodel_runtime'],
            original_trainer=api['roles'][role]['original_trainer'], derived_trainer=api['roles'][role]['derived_trainer'],
            actual_old_proof_refs=api['roles'][role]['prior_actual_proof_refs'])
    result = dict(status='SOURCE_READY_FOR_PARENT_REVIEW_NOT_ACTUAL_ADMISSION_NOT_SDK_NOT_TRAINING',
        scope='E0/E2/E3 only; H1 frozen excluded; no parent/other-child/sealed source edits',
        child_root=str(B), posttrain_kind=POSTTRAIN_KIND, parent_admission_kind=ADMISSION_KIND,
        max_additional_updates=20, num_envs=20000, seed=20260928, steps_per_env=24,
        original_bounded_learn_and_init_at_random_ep_len_True_preserved=True,
        actual_live_critic_optimizer_fullrestore_and_complete_own_save_required_at_future_runtime=True,
        raw_model_or_GPU_execution_done=False,
        actual_child_activity=dict(model_PT_opens=0, model_PT_stats=0, model_PT_hashes=0, model_decodes=0,
            torch_imports=0, SDK_calls=0, GPU_calls=0, actual_optimizer_steps=0, SSH_calls=0,
            canonical_reads=0, canonical_writes=0, actual_Task_GO_Ready_files=0, new_agents=0, Git_writes=0),
        review_report=by_name['AST_MOCK_REVIEW_V2_WITH_CACHE_ALIAS_AND_CONSTRUCTOR.json'],
        review_tests_passed=8, mock_is_not_actual_SDK_or_skill_pass=True,
        role_deploy_sources=role_rows,
        pure_constructor=by_name['construct_source_task_go_v1.py'],
        required_fields=by_name['PARENT_REQUIRED_FIELDS_SOURCE_ONLY_V1.json'],
        source_only_mock_example=by_name['MOCK_SOURCE_CONSTRUCTION_EXAMPLE_V1.json'],
        source_cache_alias_review=[t['detail'] for t in report['tests'] if t['name'] == 'source_cache_full_root_mutable_alias_isolation'][0],
        immutable_cache_truth_runtime_audit='Whole-root RAM deepcopy snapshot checked on every complete save and final; no source PT re-open',
        all_child_text_files_for_parent_archive=rows,
        original_owner_responsibility='Original b.LOCKS doubleEX + GPUprivateEX + finiteSH, same C/charge_values sole writer, actual admission/GO, periodic stop/budget, complete save-closewait-terminal settlement; child installs no canonical hook',
        pending_actual=['parent review and actual admission/GO', 'new live whole20k fullrestore + complete startup save',
                        'up to20 original PPO updates + complete derived final save', 'original Appclose/childwait/accounting',
                        'independent original skill retention replay'],
        no_automatic_next_window=True)
    target = B / 'FINAL_SOURCE_HANDOFF_INDEX_V1.json'
    with target.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps(dict(status=result['status'], final_index=str(target),
        common_SHA=by_name['posttrain_fullstate_common_v1.py']['SHA'], child_text_files=len(rows),
        AST_mock_groups_passed=8, actual_GPU_SDK_PT_or_PPO=0), indent=2))


if __name__ == '__main__':
    main()
