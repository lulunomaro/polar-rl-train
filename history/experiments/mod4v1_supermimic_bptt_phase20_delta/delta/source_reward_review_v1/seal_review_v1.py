"""Seal only this new source review after bounded read-only consistency checks.
No workspace traversal, simulator/task imports, training, Git or source edits.
"""
from __future__ import annotations
import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
FILES = [
    'REWARD_COMMAND_AUDIT_SOURCE_V1.md', 'NEXT_WINDOW_AB_PLAN_V1.json',
    'reward_command_candidates_v1.py', 'build_source_audit_v1.py',
    'test_reward_command_candidates_v1.py', 'seal_review_v1.py',
    'ROLE_EFFECTIVE_REWARD_PARAMS_SOURCE_V1.json', 'FORMULA_COUNTEREXAMPLES_CPU_V1.json',
    'AUDIT_INPUTS_SHA256_V1.json', 'CPU_TEST_RESULTS_V1.json',
    'CPU_TEST_EXECUTION_HISTORY_V1.json',
]
SEAL_NAME = 'DELIVERABLES_SHA256_V1.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tests = json.loads((OUT/'CPU_TEST_RESULTS_V1.json').read_text(encoding='utf-8'))
    assert tests['tests_run'] == 62 and tests['passed']
    assert tests['errors'] == tests['failures'] == tests['skipped'] == 0
    inputs = json.loads((OUT/'AUDIT_INPUTS_SHA256_V1.json').read_text(encoding='utf-8'))
    assert inputs['file_count'] == len(inputs['files']) == 89
    changed = [row['path'] for row in inputs['files'] if sha(Path(row['path'])) != row['SHA256']]
    assert not changed, f'input source changed since source join: {changed}'
    plan = json.loads((OUT/'NEXT_WINDOW_AB_PLAN_V1.json').read_text(encoding='utf-8'))
    assert not plan['enabled'] and not plan['apply_to_active_sources']
    assert plan['invariants']['E0_binary_acceptance'] is None
    assert plan['invariants']['SLOPE_INDEPENDENT50_binary_acceptance'] is None
    assert all(not arm['enabled'] for arm in plan['comparisons'])
    params = json.loads((OUT/'ROLE_EFFECTIVE_REWARD_PARAMS_SOURCE_V1.json').read_text(encoding='utf-8'))
    assert len(params['roles']) == 8 and not params['actual_live_cfg']
    assert params['all_eight_task_hashes_equal']
    assert params['all_eight_skills_hashes_equal']
    assert params['all_eight_scut_reward_functions_AST_equal']
    assert not params['all_eight_scut_hashes_equal']
    links = re.findall(r'\]\(<([^>]+)>\)', (OUT/FILES[0]).read_text(encoding='utf-8'))
    missing = []
    for url in links:
        path = Path(url.split('#')[0])
        if path.name == SEAL_NAME and path.parent == OUT:
            continue
        if not path.is_file():
            missing.append(url)
    assert not missing, f'broken file references: {missing}'
    for name in FILES:
        path = OUT/name
        assert path.is_file() and path.parent == OUT
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    rows = [dict(name=name, path=str(OUT/name), bytes=(OUT/name).stat().st_size,
                 SHA256=sha(OUT/name)) for name in FILES]
    bundle_digest = hashlib.sha256('\n'.join(r['name']+'\0'+r['SHA256'] for r in rows).encode()).hexdigest()
    result = dict(
        kind='NEW_DIRECTORY_SOURCE_AUDIT_FORMULAS_AND_PLAN_ONLY_NOT_RUNTIME_VALIDATION',
        created_at=datetime.now().astimezone().isoformat(),
        role_count=8, bounded_input_count=89, input_hashes_reverified_unchanged=True,
        tests_run=62, tests_passed=62, failures=0, errors=0,
        all_JSON_parsed=True, all_Python_AST_parsed=True,
        report_existing_file_links_validated=len(links),
        files=rows, files_in_manifest=len(rows), seal_self_excluded=True,
        bundle_SHA256=bundle_digest,
        actual_live_cfg=False, runtime_pass_rates={role:None for role in params['roles']},
        SDK_imports=0, torch_imports=0, GPU_operations=0, models_read=0,
        old_raw_JSONL_reads=0, SSH_operations=0, Git_operations=0,
        active_or_sealed_source_edits=0, training_executed=False,
        E0_original_binary_predicate=None, SLOPE_INDEPENDENT50_original_binary_predicate=None,
        parent_owns_actual_validation_and_git=True)
    seal_path = OUT/SEAL_NAME
    seal_path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status='SOURCE_REVIEW_SEALED', files=len(rows)+1,
                          inputs=89, tests_passed=62, bundle_SHA256=bundle_digest,
                          seal_SHA256=sha(seal_path),
                          primary={r['name']:r['SHA256'] for r in rows if r['name'] in
                                   {FILES[0], FILES[1], FILES[2], 'CPU_TEST_RESULTS_V1.json'}}),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
