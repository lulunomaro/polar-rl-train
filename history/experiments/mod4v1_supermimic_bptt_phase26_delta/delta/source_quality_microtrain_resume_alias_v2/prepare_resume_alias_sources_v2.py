"""SOURCE ONLY: prepare corrected-fixture CPU V2 and whole-ingress-copy core/CPU V3.
Never imports Torch, opens checkpoints, stages or executes training.
"""
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD_CPU = ROOT / 'source_quality_microtrain_torch_validation_v1/test_quality_microtrain_torch_cpu_v1.py'
OLD_CORE = ROOT / 'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py'
CPU_SHA = '753cf898edbf9015349509cd7e67d4086dbedb80828bb146d88bbc58c2ab74be'
CORE_SHA = '8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac'
OLD_STAGE = ROOT / 'source_native_v6_runtime_compat/stage_a1_native_v6.py'
ALIASES = ['worker_sources/ctx_reward_full_resume_candidate_v2.py', 'worker_sources/ctx_reward_learner.py']


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(node):
    return ast.dump(node, include_attributes=False)


def loader(tree):
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ContextRewardLearner')
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'load_full_checkpoint')


def once(text, old, new):
    assert text.count(old) == 1, ('literal uniqueness', old, text.count(old))
    return text.replace(old, new)


def diff(a, b, old_name, new_name):
    return ''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=old_name, tofile=new_name)).encode()


def prepare():
    old_cpu_raw, old_core_raw = OLD_CPU.read_bytes(), OLD_CORE.read_bytes()
    assert H(old_cpu_raw) == CPU_SHA and H(old_core_raw) == CORE_SHA
    old_cpu, old_core = old_cpu_raw.decode('utf-8'), old_core_raw.decode('utf-8')
    old_core_tree = ast.parse(old_core)
    old_load = loader(old_core_tree)
    assert old_load.args.args[1].arg == 'payload'
    assert not any(isinstance(n, ast.Import) and any(a.name == 'copy' for a in n.names) for n in old_core_tree.body)
    lines = old_core_raw.splitlines(keepends=True)
    nl = b'\r\n' if b'\r\n' in old_core_raw else b'\n'
    lines.insert(old_load.body[0].lineno - 1, b'        payload = copy.deepcopy(payload)' + nl)
    insertion = next(n.lineno - 1 for n in old_core_tree.body if isinstance(n, ast.Import) and n.names[0].name == 'importlib')
    lines.insert(insertion, b'import copy' + nl)
    core_raw = b''.join(lines)
    core = core_raw.decode('utf-8')
    core_tree = ast.parse(core)
    new_load = loader(core_tree)
    assert dump(new_load.body[0]) == dump(ast.parse('payload = copy.deepcopy(payload)').body[0])
    normalized_core = copy.deepcopy(core_tree)
    normalized_core.body = [n for n in normalized_core.body if not (isinstance(n, ast.Import) and len(n.names) == 1 and n.names[0].name == 'copy')]
    normalized_load = loader(normalized_core)
    normalized_load.body.pop(0)
    assert dump(normalized_load) == dump(old_load)
    assert dump(normalized_core) == dump(old_core_tree)

    v2 = once(old_cpu, "REPORT_KIND = 'SYNTHETIC_CPU_A1_LEGACY_QUALITY_MICROTRAIN_FULL_RESUME_V1'", "REPORT_KIND = 'SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_CORRECTED_FIXTURE_ORIGINAL_811_V2'\nREPORT_PURPOSE = 'LEGAL_ORDERING_METADATA4_VS_PAYLOAD3_THEN_ORIGINAL_811_ALIAS_GUARD_V2'")
    old_stale = "    stale['counts']['pi_bptt_optimizer_steps'] += 1\n    stale['actual_BPTT_policy_steps'] += 1\n    # A self-consistent newly pinned JSON still loses to actual decoded payload counts."
    new_stale = "    for name in ('policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps'):\n        stale['counts'][name] += 1\n    stale['actual_BPTT_policy_steps'] = stale['counts']['pi_bptt_optimizer_steps']\n    stale['checkpoint']['counts'] = copy.deepcopy(stale['counts'])\n    assert base.validate_count_snapshot(stale['counts']) == stale['counts']\n    assert stale['checkpoint']['counts'] == stale['counts']\n    # Ordering is valid: metadata4 must lose to actual decoded payload3, not to metadata ordering."
    v2 = once(v2, old_stale, new_stale)
    old_reject = "        lambda: q.validate_microtrain_payload(root_values, stale_bound))\n    for field, wrong in"
    new_reject = "        lambda: q.validate_microtrain_payload(root_values, stale_bound))\n    assert negatives[-1]['message'] == 'actual full payload counters differ from source FINAL'\n    for field, wrong in"
    v2 = once(v2, old_reject, new_reject)
    v2 = once(v2, "result = dict(kind=REPORT_KIND, passed=False,", "result = dict(kind=REPORT_KIND, evidence_purpose=REPORT_PURPOSE, passed=False,")
    v2 = once(v2, "QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V1.json", "QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V2.json")
    v2 = once(v2, "isolated original core811 full loader -> strict pi.load_state_dict; prior models may already load", "isolated SHA-pinned payload-core full loader -> strict pi.load_state_dict; prior models may already load")
    v2 = once(v2, "OBSERVED_CPU_SOURCE_ALIASING_ONLY; old sealed sources remain unchanged; parent decides NEW erratum/v2", "OBSERVED_CPU_SOURCE_ALIASING_ONLY; sealed inputs unchanged; no automatic repair or acceptance downgrade")
    v3 = once(v2, "'payload_core': '" + CORE_SHA + "'", "'payload_core': '" + H(core_raw) + "'")
    v3 = once(v3, 'SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_CORRECTED_FIXTURE_ORIGINAL_811_V2', 'SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_WHOLE_INGRESS_COPY_CORE_V3')
    v3 = once(v3, 'LEGAL_ORDERING_METADATA4_VS_PAYLOAD3_THEN_ORIGINAL_811_ALIAS_GUARD_V2', 'SAME_CORRECTED_FIXTURE_WITH_CORE_V3_WHOLE_INGRESS_DEEPCOPY_V3')
    v3 = once(v3, 'QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V2.json', 'QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V3.json')
    reverse = v3.replace(H(core_raw), CORE_SHA).replace('SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_WHOLE_INGRESS_COPY_CORE_V3', 'SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_CORRECTED_FIXTURE_ORIGINAL_811_V2').replace('SAME_CORRECTED_FIXTURE_WITH_CORE_V3_WHOLE_INGRESS_DEEPCOPY_V3', 'LEGAL_ORDERING_METADATA4_VS_PAYLOAD3_THEN_ORIGINAL_811_ALIAS_GUARD_V2').replace('QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V3.json', 'QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V2.json')
    assert reverse == v2
    outputs = {
        'ctx_reward_full_resume_candidate_v3.py': core_raw,
        'test_quality_microtrain_torch_cpu_v2.py': v2.encode(),
        'test_quality_microtrain_torch_cpu_v3.py': v3.encode(),
        'CORE_V3_WHOLE_INGRESS_DELTA.patch': diff(old_core, core, str(OLD_CORE), 'NEW/ctx_reward_full_resume_candidate_v3.py'),
        'CPU_V1_TO_V2_FIXTURE_DELTA.patch': diff(old_cpu, v2, str(OLD_CPU), 'NEW/test_quality_microtrain_torch_cpu_v2.py'),
        'CPU_V2_TO_V3_ROUTE_DELTA.patch': diff(v2, v3, 'NEW/test_quality_microtrain_torch_cpu_v2.py', 'NEW/test_quality_microtrain_torch_cpu_v3.py'),
    }
    for name, raw in outputs.items():
        if name.endswith('.py'):
            compile(raw, str(HERE / name), 'exec')
    original_stage = OLD_STAGE.read_text(encoding='utf-8')
    assert "output['worker_sources/ctx_reward_learner.py'] = core" in original_stage
    proof = dict(kind='SOURCE_ONLY_WHOLE_RESUME_INGRESS_COPY_AST_PROOF_V2', original_core=dict(path=str(OLD_CORE), bytes=len(old_core_raw), SHA256=CORE_SHA), new_core=dict(path=str(HERE/'ctx_reward_full_resume_candidate_v3.py'), bytes=len(core_raw), SHA256=H(core_raw)), original_CPU=dict(path=str(OLD_CPU), bytes=len(old_cpu_raw), SHA256=CPU_SHA), load_signature=ast.unparse(old_load).splitlines()[0], added_first_statement='payload = copy.deepcopy(payload)', remaining_full_load_body_AST_identical=True, entire_module_AST_identical_after_removing_only_import_copy_and_first_assignment=True, protected_original_load_AST_SHA256=H(dump(old_load).encode()), protected_original_module_AST_SHA256=H(dump(old_core_tree).encode()), unknown_roots_whole_copy=True, keys_filtered=False, replay_sliced=False, extra_decode=False, external_working_copy_passed_to_loader=False, CPU_V2_all_input_PINs_same_as_V1=True, CPU_V2_fixture_correction='attempts/optimizer/verified and actual count all metadata4; checkpoint counts identical; metadata ordering succeeds then exact real-payload mismatch message required', CPU_V3_only_pair_differences=['payload_core SHA256', 'REPORT_KIND', 'REPORT_PURPOSE', 'receipt outfile'], CPU_V3_to_V2_reverse_bytes_identical=True, actual_Torch_tests_executed=0, actual_native_operations=0, actual_V2_receipt=None, actual_V3_receipt=None)
    outputs['RESUME_ALIAS_PROTECTED_AST_PROOF_V2.json'] = (json.dumps(proof, indent=2, ensure_ascii=False) + '\n').encode()
    bindings = dict(kind='FUTURE_ONLY_CORE_V3_LOGICAL_ALIAS_BINDINGS_V2', implemented_for_actual_training=False, enabled_for_actual_training=False, source=str(HERE/'ctx_reward_full_resume_candidate_v3.py'), bytes=len(core_raw), SHA256=H(core_raw), future_logical_aliases=ALIASES, aliases_source_evidence=dict(path=str(OLD_STAGE), lines='166-169'), original_core_SHA256=CORE_SHA, required_new_manifest_and_review=True, historical_old_thirteen_proof_covers_new_core=False, old_thirteen_sources_and_bindings_modified=False, legacy_executor_no_quality_gain_not_selected_for_native_enable=True, old_embedded_teacher_guard_7c_changed=False, actual_stage_or_dispatch=None, note='These two aliases must receive the SAME complete new-core bytes in a FUTURE separately admitted source manifest. This file neither installs nor admits anything; old 811 PINs and hard7c teacher guard remain historical and unchanged.')
    outputs['FUTURE_CORE_V3_BINDINGS_ONLY_V2.json'] = (json.dumps(bindings, indent=2, ensure_ascii=False) + '\n').encode()
    assert all(not (HERE/name).exists() for name in outputs), 'NEW outputs already exist; no overwrite'
    for name, raw in outputs.items():
        with (HERE/name).open('xb') as f:
            f.write(raw)
    print(json.dumps({name:dict(bytes=len(raw), SHA256=H(raw)) for name,raw in outputs.items()}, indent=2))


if __name__ == '__main__':
    prepare()
