"""Fresh target72 SDK/native/Fudan CPU admission. No source promotion from native82Q."""
from pathlib import Path
import hashlib
import json
from mixed84_protocol_v1 import (SOURCES, PREVIOUS_NAMESPACE, validate_closed83B,
    require_native_manifest_pins, native_ready_value)

read = lambda path: json.loads(Path(path).read_bytes())
H = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(spec, B):
    B = Path(B)
    manifest = read(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    manifest_sha = H(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    bundle = read(B / 'MIXED84_REFERENCE_BINDING_ACTUAL.json')
    proof = read(B / 'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json')
    identity = read(B / 'MIXED84_PREVIOUS_OWNER_IDENTITY_ACTUAL.json')
    validate_closed83B(proof, identity)
    require_native_manifest_pins(manifest, bundle)
    origin = read(B / 'SOURCE_ORIGIN83B_H1_NODE_TERMINAL_ACTUAL.json')['row']
    origin_exit = read(B / 'SOURCE_ORIGIN83B_H1_NODE_EXIT_ACTUAL.json')
    assert origin['returncode'] == 0 and origin['terminal_all_own_children_waited']
    assert not origin['original_error'] and not origin['errors'] and origin['final']['passed']
    assert origin['final']['final']['SHA'] == spec['source_SHA'] == SOURCES['h1']['SHA']
    assert origin_exit['actual_all_own_children_waited'] and origin_exit['validation_fcntl_released_if_acquired']
    physical = Path(spec['previous_runtime_root'])
    assert str(physical).endswith('/' + PREVIOUS_NAMESPACE + '/e2')
    physical_exit = read(physical / 'NODE_EXIT_ACTUAL.json')
    physical_terminal = read(physical / 'NODE_TERMINAL_ACTUAL.json')['row']
    assert physical_exit['actual_all_own_children_waited'] and physical_exit['validation_fcntl_released_if_acquired']
    assert physical_terminal['terminal_all_own_children_waited'] and physical_terminal['returncode'] == 0
    assert not physical_terminal['original_error'] and not physical_terminal['errors']
    assert physical_terminal['final']['passed'] and physical_terminal['final']['final']['SHA'] == SOURCES['e2']['SHA']
    sdk = read(B / 'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')
    native = read(B / 'reports/NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V84_ACTUAL.json')
    value = native_ready_value(spec, bundle, sdk, native, manifest_sha)
    return dict(value=value, SHA=hashlib.sha256(json.dumps(value, indent=2).encode()).hexdigest(),
                actual_CPU_waited_EXIT0=True)
