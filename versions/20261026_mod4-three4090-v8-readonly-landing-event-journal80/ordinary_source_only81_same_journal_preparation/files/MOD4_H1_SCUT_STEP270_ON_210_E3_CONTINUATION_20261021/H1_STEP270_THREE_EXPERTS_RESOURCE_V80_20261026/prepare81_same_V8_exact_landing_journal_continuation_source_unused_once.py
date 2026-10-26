"""Source preparation only while80 runs. No payload, model, controller, Task or GO."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time
import traceback

N = Path(__file__).resolve().parent
T = N.parent
F = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026'
R = N / 'reports'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def once(s, before, after):
    assert s.count(before) == 1, before
    return s.replace(before, after, 1)

def put(p, s):
    ast.parse(s)
    with p.open('x', encoding='utf8', newline='\n') as f:
        f.write(s)

try:
    assert not F.exists()
    F.mkdir()
    (F / 'reports').mkdir()
    (F / 'candidates').mkdir()
    shutil.copy2(N / 'candidates/same_optimized_source_contract_metadata_candidate_v1.py', F / 'candidates/same_optimized_source_contract_metadata_candidate_v1.py')
    s = (N / 'candidates/closed_three_V8_landing_journal_source_CPU_v1.py').read_text('utf8')
    s = once(s, " if key=='h1':allowed|={'h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py'}\n", '')
    s = once(s, 'AUTH_80_ACTUAL.json', 'AUTH_81_ACTUAL.json')
    s = once(s, 'actual_closed_three_V8_landing_journal_continuation', 'actual_closed_three_same_V8_landing_journal_continuation')
    helper = '''
def validate_same_landing_journal_lineage(B,old,diag):
 B=Path(B);old=Path(old)
 name='H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json'
 assert H(B/name)==H(old/name)
 journal=read(B/name)
 assert journal['approved'] and journal['no_reward_actor_command_physics_or_success_change']
 assert set(journal['candidate_files'])=={'h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py','reference_sources/actual79c_counter_original_bytes.txt'}
 assert diag['candidate_files']['h1_lifetime_goal_counter_v1.py']==journal['base_counter_SHA']
 assert diag['candidate_files']['sampling_acceleration_installed_CPU_v2.py']==journal['base_sampler_SHA']
 for name,digest in journal['candidate_files'].items():assert H(B/name)==H(old/name)==digest
 assert H(B/'reference_sources/actual79c_counter_original_bytes.txt')==journal['base_counter_SHA']
 assert H(B/'h1_production_control_prefix_trace_v1.py')==H(old/'h1_production_control_prefix_trace_v1.py')==diag['candidate_files']['h1_production_control_prefix_trace_v1.py']
 return True

'''
    s = once(s, '\ndef load(spec,B):', '\n' + helper + 'def load(spec,B):')
    s = once(s, "  for name,digest in diag['candidate_files'].items():assert H(old/name)==digest", '  validate_same_landing_journal_lineage(B,old,diag)')
    start = s.index("  journal=read(B/'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json');")
    end = s.index("  assert cpu['sampling_acceleration_CPU']['landing_event_journal_CPU']['passed']", start)
    s = s[:start] + s[end:]
    put(F / 'candidates/same_three_closed_source_V8_landing_journal_CPU_v1.py', s)

    s = (N / 'bind_complete79c_sources_V8_readonly_landing_journal_unused_once.py').read_text('utf8')
    s = s.replace('V79C_', 'V80_').replace('2610v80', '2610v81').replace('actual79c', 'actual80').replace('latest79c', 'latest80')
    s = s.replace('AUTH_80_ACTUAL.json', 'AUTH_81_ACTUAL.json').replace('actual_closed79c_report_SHA', 'actual_closed80_report_SHA')
    s = s.replace('actual_closed_three_V8_landing_journal_continuation', 'actual_closed_three_same_V8_landing_journal_continuation')
    s = s.replace('candidates/closed_three_V8_landing_journal_source_CPU_v1.py', 'candidates/same_three_closed_source_V8_landing_journal_CPU_v1.py')
    start = s.index("  if key=='h1':\n   diag=")
    end = s.index("  if key=='recovery':", start)
    s = s[:start] + '''  if key=='h1':
   diag=read(out/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json');assert diag['approved'] and diag['no_reward_actor_command_PPO_physics_or_success_change']
   journal=read(out/'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json');assert journal['approved'] and journal['no_reward_actor_command_physics_or_success_change']
   assert H(out/'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json')==H(base/'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json')
   for name,digest in journal['candidate_files'].items():assert H(out/name)==H(base/name)==digest
   assert diag['candidate_files']['h1_lifetime_goal_counter_v1.py']==journal['base_counter_SHA']
   assert diag['candidate_files']['sampling_acceleration_installed_CPU_v2.py']==journal['base_sampler_SHA']
   assert H(out/'h1_production_control_prefix_trace_v1.py')==diag['candidate_files']['h1_production_control_prefix_trace_v1.py']
   assert H(out/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']
''' + s[end:]
    put(F / 'bind_complete80_sources_same_V8_exact_journal_unused_once.py', s)

    names = [
        ('e2_target72_same_backend_install_source_v1.py', 'e2_target72_same_backend_install_source_v1.py'),
        ('collect_three_experts80_readonly_landing_journal_first_PPO_finite_unused_once.py', 'collect_three_experts81_same_V8_journal_first_PPO_finite_unused_once.py'),
        ('collect_actual_three80_finals_original_cost_unused_once.py', 'collect_actual_three81_finals_original_cost_unused_once.py'),
        ('review_three_expert_complete_models_original_cost_CPU_V5_unused_once.py', 'review_three_expert_complete_models_original_cost_CPU_V5_unused_once.py'),
        ('deploy_actual_three_experts80_V8_readonly_landing_journal_original_writer_unused_once.py', 'deploy_actual_three_experts81_same_V8_journal_original_writer_unused_once.py'),
    ]
    for source, target in names:
        s = (N / source).read_text('utf8')
        s = s.replace('V80_', 'V81_').replace('V79C_', 'V80_')
        s = s.replace('2610v80', '2610v81').replace('2610v79c', '2610v80')
        s = s.replace('actual80', 'actual81').replace('active79c', 'active80').replace('from complete79c', 'from complete80')
        if source.startswith('deploy_'):
            s = s.replace('only after78 closes', 'only after80 closes')
        put(F / target, s)
    notice = dict(epoch=time.time(), source_only=True, no_payload_Task_controller_model_GO_fee=True,
        qualified80_source_SHA_Adam_and_closing=None,
        binder_requires_complete80_models_CPU_original_cost_allout_and_normal_duration=True,
        same_V8_reward_trace_counter_journal_sampler_and_original_approvals_bytes=True,
        role_guard_only_root_Python_change_except_original_recovery_saved_Adam_assert=True,
        no_new_python_modules_or_diagnostic_migration=True,
        metadata_helper_byte_exact_SHA=H(F / 'candidates/same_optimized_source_contract_metadata_candidate_v1.py'),
        metadata_helper_bytes=(F / 'candidates/same_optimized_source_contract_metadata_candidate_v1.py').stat().st_size,
        target_SDK_fullsource_CPU_resources_original_valid_ready_still_required=True,
        optional_journal_not_a_model_or_skill_gate=True,
        scheduling_decision_must_first_inspect_complete80_landing_journal_evidence=True,
        not_an_instruction_to_blindly_run_identical_windows=True)
    with (F / 'reports/SOURCE_ONLY81_SAME_V8_EXACT_JOURNAL_PROTOCOL_PREPARED_ACTUAL.json').open('x', encoding='utf8') as f:
        json.dump(notice, f, indent=2)
    print(json.dumps(dict(prepared81_source_only=True, no_GO=True)))
except BaseException:
    with (R / ('SOURCE_ONLY81_PREPARATION_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
        json.dump(dict(epoch=time.time(), error=traceback.format_exc(), no_same_namespace_retry=True), f, indent=2)
    raise
