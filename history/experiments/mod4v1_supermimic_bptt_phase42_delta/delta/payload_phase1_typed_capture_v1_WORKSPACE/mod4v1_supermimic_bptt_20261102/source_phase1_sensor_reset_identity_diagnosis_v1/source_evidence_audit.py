"""NEW SOURCE-only transfer audit: read bytes/AST/old receipts; no SDK imports.

This does not rerun old CPU/native programs. Output is a new, write-once receipt.
"""
import ast
import hashlib
import json
from pathlib import Path

R = Path('F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102')
HERE = Path(__file__).resolve().parent
OLD = R / 'source_phase1_passive_sensor_capture_v1'
NEW = R / 'source_phase1_passive_sensor_capture_v2'
OLD_SEAL_SHA = '3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881'


def digest(path):
    b = path.read_bytes()
    return dict(path=str(path), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def tree(path):
    return ast.parse(path.read_text(encoding='utf-8'))


def definition(t, name):
    return next(n for n in t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)


def ast_key(n):
    return ast.dump(n, annotate_fields=True, include_attributes=False)


def compare_definitions(name, selected):
    left, right = tree(OLD / name), tree(NEW / name)
    rows = []
    for symbol in selected:
        a, b = ast_key(definition(left, symbol)), ast_key(definition(right, symbol))
        assert a == b, 'Runtime AST changed: ' + name + ':' + symbol
        rows.append(dict(symbol=symbol, AST_equal=True, AST_sha256=hashlib.sha256(a.encode()).hexdigest()))
    return rows


def main():
    old_seal = OLD / 'SOURCE_SEAL.json'
    assert digest(old_seal)['sha256'] == OLD_SEAL_SHA
    seal = json.loads(old_seal.read_text(encoding='utf-8'))
    assert len(seal['files']) == 13
    for p in seal['files']:
        got = digest(OLD / p['relative'])
        assert (got['bytes'], got['sha256']) == (p['bytes'], p['sha256'])
    cpu_path = R / 'reports/PHASE1_PASSIVE_TAP_CPU_V1.json'
    old_cpu = json.loads(cpu_path.read_text(encoding='utf-8'))
    receipt = old_cpu['receipt']
    fixture = receipt['fixture']
    assert old_cpu['returncode'] == 0 and receipt['status'] == 'PASS'
    assert receipt['frozen_source_seal_SHA256'] == OLD_SEAL_SHA
    assert fixture['real_torch_CPU_classes_executed'] is True
    assert fixture['bitwise_class_output_comparisons'] == 25 and fixture['return_identity_checks'] == 50
    assert fixture['source_rng_and_queue_state_equal'] and fixture['global_torch_rng_unchanged']
    assert not receipt['SDK_executed'] and not receipt['native_binding_preflight_executed']
    assert not receipt['actor35_native_equality_tested']
    assert not fixture['native_enabled'] and not fixture['exact']
    for name, p in old_cpu['source_pins'].items():
        if (OLD / name).is_file():
            got = digest(OLD / name)
            assert (got['bytes'], got['sha256']) == (p['bytes'], p['sha256'])
    byte_equal = {}
    for name in ('cpu_reference_tap_fixture.py', 'fake_runtime.py', 'OBSERVER_HOOK_SPEC.md'):
        assert (OLD / name).read_bytes() == (NEW / name).read_bytes()
        byte_equal[name] = digest(NEW / name)
    runtime_ast = compare_definitions('passive_capture.py', (
        'stdlib_snapshot', 'tensor_snapshot_adapter', 'BoundedRecorder', '_same_callable',
        '_plain_scale', '_root_asset_configuration', 'PassiveCapture', 'install_passive_capture'))
    old_mod, new_mod = tree(OLD / 'passive_capture.py'), tree(NEW / 'passive_capture.py')
    for name in ('install_passive_capture', 'preflight'):
        assert ast_key(definition(old_mod, name).args) == ast_key(definition(new_mod, name).args)
    api_ast = compare_definitions('source_api.py', (
        'sha', '_nodes', 'pin', '_source_class_chain', '_code_key', '_find_code',
        'verify_callable', 'verify_class', 'closure_functions'))
    inherited_test_ast = compare_definitions('test_passive_capture.py', ('CaptureContractTests',))
    manifest_path = NEW / 'SOURCE_API_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert len(manifest['roles']) == 8
    roles = {}
    for name, role in manifest['roles'].items():
        s = role['reset_chain']
        assert s['status'] == 'SOURCE_CONFIRMED_LIVE_UNKNOWN' and s['live_binding'] == 'UNKNOWN'
        assert [x['env_attribute'] for x in s['layers']] == ['_explicit_pd', '_chassis_com', '_gas_damping', '_spring_pressure']
        assert len(s['constructor_order']) == 3
        for p in s['constructor_order']:
            assert ('/' + name + '/') in p['pin']['source_path'].replace('\\', '/')
        roles[name] = dict(status=s['status'], live_binding='UNKNOWN',
                           endpoint=s['endpoint']['qualname'],
                           constructor_source_pins=[x['pin'] for x in s['constructor_order']])
    cap = R / 'discovery/phase1_first_startup_failure_v1/worker_sources/parent/n80_gpu_capacity.py'
    assert digest(cap)['sha256'] == 'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc'
    output = dict(kind='ACTUAL_STDLIB_B2_SOURCE_INHERITANCE_AUDIT_V1', status='PASS',
        source_only=True, native_enabled=False, exact=False,
        old_source_seal=digest(old_seal), old_thirteen_members_read_only_verified=True,
        old_actual_CPU_receipt=digest(cpu_path),
        old_CPU_evidence_scope=dict(bitwise_class_output_comparisons=25, return_identity_checks=50,
            private_and_global_RNG_unchanged=True, real_original_Sensor_Delay_Torch_CPU=True,
            environment='FAKE_ENV_BOUNDARY', SDK=False, native_preflight=False, actor35_native=False,
            this_is_B1_historical_evidence_not_new_B2_execution=True),
        byte_equal_artifacts=byte_equal, passive_runtime_AST_equal=runtime_ast,
        source_verification_helper_AST_equal=api_ast, inherited_21_test_class_AST_equal=inherited_test_ast,
        unchanged_public_API_signatures=['install_passive_capture', 'preflight'],
        B2_change_scope='STRICT_PREFLIGHT_RESET_COMPOSITION_AND_METADATA_DIAGNOSTICS_ONLY',
        own_role_SOURCE_proofs=roles, B2_manifest=digest(manifest_path),
        verified_published_capacity_source=digest(cap),
        B2_actual_Torch_CPU_execution_by_child=False,
        B2_actual_native_preflight=False, B2_bitwise_actor35_native_equality=False,
        SDK_GPU_SSH_training_execution=False, source_artifacts_edited_by_audit=False)
    out = HERE / 'SOURCE_EVIDENCE_AUDIT.json'
    with out.open('x', encoding='utf-8') as stream:
        json.dump(output, stream, indent=2, ensure_ascii=False)
    print(json.dumps(dict(status='PASS', receipt=str(out),
                         runtime_AST_definitions=len(runtime_ast),
                         source_helper_AST_definitions=len(api_ast),
                         old_members_verified=13, roles=len(roles),
                         native_enabled=False, exact=False), indent=2))


if __name__ == '__main__':
    main()
