"""Append-only source/CPU seal. Never dispatch/import an evaluator or touch model bytes."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import re
import build_microbatch_candidates_v1 as build

B = Path(__file__).resolve().parent
R = B.parent
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'
S = R / 'source_a1_frozen_eval_integration_v2'


def identity(path):
    path = Path(path).resolve()
    assert path.is_relative_to(R) or path.is_relative_to(T)
    assert path.suffix in ('.py', '.md', '.json', '.patch'), 'text source/metadata only'
    raw = path.read_bytes()
    assert len(raw) < 262144, 'bounded source only'
    return dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest(),
                line_count=len(raw.decode('utf-8-sig').splitlines()))


def put_new(name, value):
    path = B / name
    assert not path.exists(), 'append-only output already exists: ' + name
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def main():
    assert not (B / 'DELIVERABLES_SHA256_V1.json').exists(), 'sealed source is immutable'
    results = json.loads((B / 'CPU_TEST_RESULTS_V1.json').read_text(encoding='utf-8'))
    assert results['passed'] is True and results['tests'] == 24 and results['failures'] == results['errors'] == 0
    build.verify_validator()
    for old_name, pin, new_name, transform in [
        ('single_gpu_eight_a1_frozen_parent_candidate_v2.py', build.PARENT_PIN, build.PARENT, build.replacements),
        ('worker_formal_a1_frozen_candidate_v2.py', build.WORKER_PIN, build.WORKER, build.worker_replacements)]:
        old = build.read_pinned(old_name, pin); expected, pairs = transform(old)
        actual = (B / new_name).read_text(encoding='utf-8')
        assert actual == expected
        build.undo_equal(old, actual, pairs)
    index = json.loads(build.read_pinned('FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json', build.INDEX_PIN))
    assert len(index['entries']) == 12
    inputs = {str(S / 'FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json'): identity(S / 'FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json')}
    mappings = []
    for entry in index['entries']:
        current = identity(entry['path'])
        assert (current['bytes'], current['SHA256']) == (entry['bytes'], entry['SHA256']), 'old sealed source changed'
        inputs[current['path']] = current
        # Original strict-eight parent is kept sealed as an input, not used as this batch entry.
        # Formal worker gets only the two reviewed import changes in the NEW root.
        if entry['path'].endswith(('single_gpu_eight_a1_frozen_parent_candidate_v2.py', 'worker_formal_a1_frozen_candidate_v2.py')):
            continue
        mappings.append(dict(entry))
    for source, alias in [(build.PARENT, build.PARENT),
                          ('frozen_eval_microbatch_runtime_v1.py', 'frozen_eval_microbatch_runtime_v1.py'),
                          (build.WORKER, 'worker_sources/parent/worker_five_original_n80.py')]:
        item = identity(B / source)
        mappings.append(dict(path=item['path'], relative=alias, bytes=item['bytes'], SHA256=item['SHA256']))
    # The reviewed index uses its original alias field. Normalize without guessing an alias.
    normalized = []
    for entry in mappings:
        relative = entry.get('relative', entry.get('installed_alias'))
        assert type(relative) is str and relative, 'inspect original source-index alias schema'
        normalized.append(dict(path=entry['path'], relative=relative, bytes=entry['bytes'], SHA256=entry['SHA256']))
    assert len(normalized) == 13 and len({row['relative'] for row in normalized}) == 13
    # Check all expected install aliases by AST literal, without importing runtime.
    runtime_tree = ast.parse((B / 'frozen_eval_microbatch_runtime_v1.py').read_text(encoding='utf-8'))
    aliases = next(ast.literal_eval(node.value) for node in runtime_tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'STAGE_REQUIRED_ALIASES' for target in node.targets))
    assert set(aliases) == {row['relative'] for row in normalized}
    extras = [
        T / 'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/generic_eval_metadata.py',
        T / 'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/EIGHT_ROLE_FROZEN_EVAL_ROSTER_SOURCE_V1.json',
        T / 'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/single_gpu_group_supervisor.py',
        T / 'NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py',
        T / 'NINE_N80_PARALLEL_SOURCE_V8/positional_rows227.py',
        T / 'NINE_N80_PARALLEL_SOURCE_V8/parallel_eval_safe.py',
        R / 'source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json']
    for path in extras:
        item = identity(path); inputs[item['path']] = item
    source_files = [B / name for name in ['frozen_eval_microbatch_runtime_v1.py', 'build_microbatch_candidates_v1.py',
        build.PARENT, build.WORKER, 'test_microbatch_parent_stdlib_v1.py', 'seal_microbatch_source_v1.py']]
    for path in source_files:
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')  # Syntax only, no parent/worker execution.
    text = (B / 'MICROBATCH_PARENT_SOURCE_V1.md').read_text(encoding='utf-8')
    links = re.findall(r'\]\(<([^>]+)>\)', text)
    for target in links:
        value, _, fragment = target.partition('#')
        path = Path(value)
        assert path.is_file(), 'broken source link: ' + target
        if fragment:
            match = re.fullmatch(r'L(\d+)(?:-L(\d+))?', fragment); assert match
            n = len(path.read_text(encoding='utf-8-sig').splitlines())
            assert 1 <= int(match[1]) <= int(match[2] or match[1]) <= n
    own_fixtures = []
    for directory in B.iterdir():
        if directory.is_dir() and directory.name.startswith(('CPU_ONLY_BARRIER_', 'CPU_ONLY_ABORT_')):
            for path in directory.rglob('*.json'):
                assert path.resolve().is_relative_to(B)
                own_fixtures.append(identity(path))
    put_new('MICROBATCH_STAGE_INDEX_V1.json', dict(kind='SOURCE_ONLY_13_MAPPINGS_NEW_MICROBATCH_NOT_INSTALLED',
        original_reviewed_index=identity(S / 'FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json'), entries=normalized,
        keep_all_other_original_static_dependencies_and_worker_files=True,
        original_strict_eight_parent_unchanged_not_subset_entry=True, source_admission=False))
    put_new('AUDIT_INPUTS_SHA256_V1.json', dict(kind='BOUNDED_TEXT_INPUTS_ONLY_NO_MODEL_RAW_OR_ACCOUNT', files=list(inputs.values())))
    put_new('OWN_CPU_FIXTURE_FILES_V1.json', dict(kind='OWN_METADATA_FAKE_FILES_NOT_NATIVE_OR_PT', files=own_fixtures))
    verification = dict(kind='SOURCE_ONLY_MICROBATCH_SCHEMA_AST_CPU_NOT_FROZEN_EVAL', CPU_tests=24, CPU_passed=True,
        reviewed_runtime_mappings_unchanged=12, bounded_source_inputs=len(inputs), report_links_checked=len(links),
        new_source_files_compiled_not_executed=len(source_files), original_parent_whitelist_undo_AST_equal=True,
        original_formal_worker_import_undo_AST_equal=True, original_validator_AST_equal_except_one_membership_check=True,
        original_private_GPU_EX_global_finite_EX_canonical_read_only_block_unchanged=True,
        original_actualwait_cleanup_finally_blocks_unchanged=True, original_accepted_loops_and_scope_unchanged=True,
        original_role_catalog=8, requested_roles=['E3', 'W35'], deferred_roles=6,
        actual_resource_admission=None, actual_frozen_evaluation=None, comparison=None, overall_eight_pass_rate=None,
        E0_original_binary_predicate=None, SLOPE_INDEPENDENT50_original_binary_predicate=None,
        W35_moving_standing_split_rate=None, W35_future_split_consumer_implemented=False,
        SDK_Torch_GPU_PT_raw_C_account_locks_Git_or_native_operations=0, old_sources_or_sealed_files_written=False)
    put_new('SOURCE_REVIEW_VERIFICATION_V1.json', verification)
    entries = []
    for path in sorted(B.iterdir()):
        if path.is_file():
            item = identity(path); item['name'] = path.name; entries.append(item)
    bundle = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    put_new('DELIVERABLES_SHA256_V1.json', dict(kind='SOURCE_ONLY_SEALED_MICROBATCH_PARENT_V1_NOT_EXECUTION',
        created_UTC=datetime.now(timezone.utc).isoformat(), files=entries, bundle_SHA256=bundle,
        self_excluded=True, own_fixture_index='OWN_CPU_FIXTURE_FILES_V1.json'))
    print(json.dumps(dict(verification=verification, seal=identity(B / 'DELIVERABLES_SHA256_V1.json'),
                         bundle_SHA256=bundle, top_level_files=len(entries) + 1), sort_keys=True))


if __name__ == '__main__':
    main()
