"""Real saved text lineage and negative metadata fixtures; not target SDK/model admission."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys
import time
import traceback

N = Path(__file__).resolve().parent
T = N.parent
F = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026'
R = F / 'reports'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_bytes())
cases = []

def check(label, fn, reject=False):
    try:
        fn()
    except AssertionError:
        assert reject, label
        cases.append(dict(case=label, rejected=True))
    else:
        assert not reject, label
        cases.append(dict(case=label, accepted=True))

try:
    assert all(not (F / x).exists() for x in ('payloads', 'controllers', 'model', 'job0'))
    sys.path.insert(0, str(F / 'candidates'))
    guard = F / 'candidates/same_three_closed_source_V8_landing_journal_CPU_v1.py'
    sp = importlib.util.spec_from_file_location('source_only81_guard_test', guard)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    b = N / 'payloads/h1'
    diag = read(b / 'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json')
    journal_name = 'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json'
    journal = read(b / journal_name)
    check('actual80_existing_counter_sampler_trace_auth_lineage', lambda: m.validate_same_landing_journal_lineage(b, b, diag))
    oldH, oldread = m.H, m.read
    old = Path('/source_fixture_old80')
    new = Path('/source_fixture_new81')
    names = set(journal['candidate_files']) | {journal_name, 'h1_production_control_prefix_trace_v1.py'}
    hashes = {str(parent / name): H(b / name) for parent in (old, new) for name in names}
    docs = {str(parent / journal_name): copy.deepcopy(journal) for parent in (old, new)}
    def trial(label, mutate):
        hh = copy.deepcopy(hashes)
        dd = copy.deepcopy(docs)
        dg = copy.deepcopy(diag)
        mutate(hh, dd, dg)
        m.H = lambda p: hh[str(p)]
        m.read = lambda p: dd[str(p)]
        try:
            check(label, lambda: m.validate_same_landing_journal_lineage(new, old, dg), reject=True)
        finally:
            m.H, m.read = oldH, oldread
    for name in names:
        trial('reject_changed_' + name, lambda hh, dd, dg, name=name: hh.__setitem__(str(new / name), '0' * 64))
    trial('reject_counter_base_link_forgery', lambda hh, dd, dg: dg['candidate_files'].__setitem__('h1_lifetime_goal_counter_v1.py', '0' * 64))
    trial('reject_sampler_base_link_forgery', lambda hh, dd, dg: dg['candidate_files'].__setitem__('sampling_acceleration_installed_CPU_v2.py', '0' * 64))
    trial('reject_extra_journal_file', lambda hh, dd, dg: dd[str(new / journal_name)]['candidate_files'].__setitem__('extra.py', '0' * 64))
    trial('reject_removed_journal_approval', lambda hh, dd, dg: dd[str(new / journal_name)].__setitem__('approved', False))
    metadata_bytes = (F / 'candidates/same_optimized_source_contract_metadata_candidate_v1.py').read_bytes()
    assert len(metadata_bytes) == 2536
    assert hashlib.sha256(metadata_bytes).hexdigest() == 'c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
    for key in ('h1', 'e2', 'recovery'):
        rows = read(N / ('payloads/' + key + '/THREE_SLOT_COMPLETE_MANIFEST_V1.json'))['files']
        before = {v['relative']: v for v in rows}
        after = copy.deepcopy(before)
        role = 'closed_production_continuation_CPU_v2.py' if key == 'h1' else 'original_account_policy50_source_CPU.py'
        after[role]['SHA'] = '1' * 64
        if key == 'recovery':
            after['recovery_worker.py']['SHA'] = '2' * 64
        check(key + '_only_reviewed_guard_role_change', lambda before=before, after=after, role=role, key=key: m.strict_same_V8_root_inventory(before, after, role, key))
        for name in (['h1_lifetime_goal_counter_v1.py', 'sampling_acceleration_installed_CPU_v2.py', 'h1_production_control_prefix_trace_v1.py', 'h1_step270_path_reward_v1.py'] if key == 'h1' else []) + ['same_optimized_source_contract_metadata_candidate_v1.py']:
            bad = copy.deepcopy(after)
            bad[name]['SHA'] = '0' * 64
            if name.endswith('metadata_candidate_v1.py'):
                bad[name]['bytes'] = 2499
            check(key + '_reject_root_change_' + name, lambda before=before, bad=bad, role=role, key=key: m.strict_same_V8_root_inventory(before, bad, role, key), reject=True)
        bad = copy.deepcopy(after)
        bad['extra.py'] = dict(SHA='0' * 64, bytes=12)
        check(key + '_reject_added_Python', lambda before=before, bad=bad, role=role, key=key: m.strict_same_V8_root_inventory(before, bad, role, key), reject=True)
    original = 'def run(steps,updates):\n assert steps=={854140+20*updates}\n return updates\n'
    newer = original.replace('854140', '855760')
    check('exact_recovery_saved_Adam_assert_only', lambda: m.exact_recovery_step(original, newer, 854140, 855760))
    check('reject_unrelated_recovery_body_change', lambda: m.exact_recovery_step(original, newer.replace('return updates', 'return updates+1'), 854140, 855760), reject=True)
    check('reject_recovery_wrong_Adam_literal', lambda: m.exact_recovery_step(original, newer.replace('855760', '855761'), 854140, 855760), reject=True)
    check('reject_missing_source_Adam_assert', lambda: m.exact_recovery_step(original.replace('854140', '854141'), newer, 854140, 855760), reject=True)
    for name in ('collect_actual_three81_finals_original_cost_unused_once.py', 'review_three_expert_complete_models_original_cost_CPU_V5_unused_once.py', 'collect_three_experts81_same_V8_journal_first_PPO_finite_unused_once.py', 'deploy_actual_three_experts81_same_V8_journal_original_writer_unused_once.py', 'e2_target72_same_backend_install_source_v1.py'):
        p = F / name
        ast.parse(p.read_text('utf8'))
        assert '2610v79c' not in p.read_text('utf8') and 'RESOURCE_V79C_' not in p.read_text('utf8'), name
    binder = (F / 'bind_complete80_sources_same_V8_exact_journal_unused_once.py').read_text('utf8')
    assert 'H1_READONLY_LANDING_JOURNAL_PREPARATION' not in binder
    assert "put(out/'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json'" not in binder
    assert "P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'" in binder
    assert "proof['remaining_actual_snapshot']>86412.86069250107" in binder
    assert not (N / 'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').exists()
    result = dict(epoch=time.time(), passed_source_only_CPU=True, cases=cases,
        source_guard_SHA=H(guard), source_metadata_bytes=len(metadata_bytes), source_metadata_SHA=hashlib.sha256(metadata_bytes).hexdigest(),
        actual80_small_text_lineage_checked_without_model_reload=True,
        no_payload_Task_controller_model_GO_fee=True,
        original_reward_trace_counter_sampler_journal_and_auth_bytes_unchanged_required=True,
        no_optional_journal_runtime_validity_or_skill_success_promoted_to_model_gate=True,
        actual_new_payload_target_SDK_source_original_valid_ready_resources_still_required=True,
        no_current80_runtime_or_remote_or_canonical_action=True,
        not_actual81_model_or_installed_admission=True)
    with (R / 'SOURCE_ONLY81_SAME_JOURNAL_LINEAGE_AND_REJECTION_CPU_ACTUAL.json').open('x', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(dict(source_only81_CPU_passed=True, cases=len(cases), no_GO=True)))
except BaseException:
    with (R / ('SOURCE_ONLY81_CPU_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
        json.dump(dict(epoch=time.time(), error=traceback.format_exc(), not_a_training_failure=True), f, indent=2)
    raise
