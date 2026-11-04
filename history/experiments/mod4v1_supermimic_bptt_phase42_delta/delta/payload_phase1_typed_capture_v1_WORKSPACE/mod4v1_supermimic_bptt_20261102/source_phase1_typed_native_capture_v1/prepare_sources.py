"""Finite SOURCE inventory only. Does not copy, stage, launch or admit anything."""
from pathlib import Path
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V4 = ROOT / 'source_phase1_capture_worker_v4'
B4 = ROOT / 'source_phase1_passive_sensor_capture_v4'
CODEC = ROOT / 'source_phase1_typed_capture_codec_v1'
C2 = ROOT / 'source_phase1_actuation_clock_scope_v2'
PACKS = {
    'v4': (V4, 'ba3409a5450e378ea97eac64f0fec4c3409ac974a4c3378d0c6e6a6cfc405180', 13, '758dc867cc4040a6f1eb9f587cc88f69a3866e03a9553290128a1681cda039e8'),
    'sensor': (B4, '81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3', 21, '6c8cc456c752a57fd9963b919e398f3c91c0c2205c15b4d1a0dbd9b605c96107'),
    'codec': (CODEC, '2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219', 7, '4ceeeda60cde6f8ca6cc496b8d299e5ea3b4ff2770b707f84898f06c1b75eec8'),
    'actuation_clock_scope_v2': (C2, '105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b', 5, '56f6e326acbe362752ce375e8c1b0b7fa64a75a530a7120db5b5d7c25628e598'),
}
INHERITED = ('phase1_capture_contract.py', 'phase1_capture_observer.py', 'phase1_capture_runtime.py',
             'worker_passive_interface_v1.py', 'single_gpu_passive_capture_parent_v1.py')
UNCHANGED_RUNTIME = ('_metadata', 'source_index', 'load_file', 'dependency', 'core', '_pinned_module',
                     'put_json', 'record_primary_error', 'validate_inherited_admission', 'validate_installed_root',
                     'validate_group_task', 'task_args', 'install_paired_pose_before_original_reset',
                     'paired_protocol_receipt', 'close_original_eval_resources')
UNCHANGED_OBSERVER = ('stored_rng_counts', 'verify_actuation_binding', 'restore_interfaces')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def identity(path):
    path = Path(path)
    if path.suffix.lower() not in ('.py', '.json', '.md', '.txt', '.patch'):
        raise ValueError('SOURCE-only suffix required: ' + str(path))
    raw = path.read_bytes()
    if path.suffix == '.py':
        ast.parse(raw, filename=str(path))
    return dict(bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def check(row, path=None):
    path = Path(path if path is not None else row['path'])
    expected = dict(bytes=row['bytes'], SHA256=row.get('SHA256', row.get('sha256')))
    if identity(path) != expected:
        raise ValueError('Full SOURCE identity differs: ' + str(path))
    return dict(path=str(path), **expected)


def sealed_pack(folder, digest, count, expected_root):
    folder = Path(folder)
    path = folder / 'SOURCE_SEAL.json'
    info = identity(path)
    if info['SHA256'] != digest:
        raise ValueError('Upstream seal bytes/SHA differ: ' + str(path))
    value = json.loads(path.read_bytes())
    slots = value['files'] if 'files' in value else value['members']
    root = value.get('content_root_sha256', value.get('content_root_SHA256'))
    # Exactly the original algorithms, not a replacement normalized root.
    if folder.name in ('source_phase1_actuation_capture_v1', 'source_phase1_state_context_partition_v1'):
        root_bytes = ''.join(name + '\0' + slots[name]['sha256'] + '\n' for name in sorted(slots)).encode()
    else:
        root_bytes = canonical(slots)
    # The exact B2 seal has no root field: retain its pinned null, never invent one.
    # Its fixed complete seal bytes and every member are still checked independently.
    if len(slots) != count or root != expected_root or (root is not None and hashlib.sha256(root_bytes).hexdigest() != root):
        raise ValueError('Upstream complete root/count differs: ' + str(path))
    entries = [(name, row) for name, row in slots.items()] if type(slots) is dict else [
        (row.get('relative', row.get('name')), row) for row in slots]
    members = []
    for name, row in entries:
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('Upstream member escapes SOURCE root')
        item = check(row, folder / rel)
        members.append(dict(relative=name, bytes=item['bytes'], SHA256=item['SHA256']))
    return dict(path=str(path), **info, members=members, content_root_sha256=root)


def functions(path):
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.parse(Path(path).read_bytes()).body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def verify_minimal_diff():
    if (HERE / INHERITED[-1]).read_bytes() != (V4 / INHERITED[-1]).read_bytes():
        raise ValueError('Complete original parent changed')
    for name, names in (('phase1_capture_runtime.py', UNCHANGED_RUNTIME),
                        ('phase1_capture_observer.py', UNCHANGED_OBSERVER),
                        ('worker_passive_interface_v1.py', ('bootstrap_original_helpers',))):
        old, new = functions(V4 / name), functions(HERE / name)
        for function in names:
            if old[function] != new[function]:
                raise ValueError('Frozen complete function changed: ' + name + ':' + function)
    return dict(parent_byte_identical=True, original_resource_preflight_and_complete_close_AST_unchanged=True,
                unchanged_runtime_functions=list(UNCHANGED_RUNTIME), unchanged_observer_functions=list(UNCHANGED_OBSERVER),
                original_bootstrap_full_function_AST_unchanged=True, original_plant_source_edits=0)


def verify_upstream():
    seals = {name: sealed_pack(*row) for name, row in PACKS.items()}
    old = json.loads((V4 / 'CAPTURE_SOURCE_INDEX.json').read_bytes())
    for row in old['original17'] + old['new_sources'] + old['dependency_sources'] + old['bootstrap_original_sources']:
        check(row)
    inherited = {}
    for name, row in old['dependency_seals'].items():
        path = Path(row['path'])
        inherited[name] = sealed_pack(path.parent, row['SHA256'], len(row['members']), row['content_root_sha256'])
    closure = old['sensor_source_manifest']['original_source_closure']
    if (closure['pin_references'], closure['unique_full_source_files'], len(closure['sources'])) != (435, 155, 155):
        raise ValueError('Original full B2 manifest source closure differs')
    for row in closure['sources']:
        check(row)
    if len(old['all_actuation_original_sources']) != 182:
        raise ValueError('Complete original C source closure differs')
    for name, row in old['all_actuation_original_sources'].items():
        check(row, ROOT / name)
    # B4's original source API is unchanged B2, so the full old manifest still binds it.
    before = next(row for row in old['dependency_sources'] if row['install_relative'] == 'phase1_deps/sensor/source_api.py')
    check(before, B4 / 'source_api.py')
    return old, seals, inherited


def source_row(path, alias):
    return dict(path=str(path), install_relative=alias, **identity(path))


def build_metadata():
    old, seals, inherited = verify_upstream()
    minimal = verify_minimal_diff()
    index = copy.deepcopy(old)
    index.update(kind='PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_INDEX_V1', source_version=1,
                 legacy_passive_source_version=4, typed_producer_schema='PHASE1_TYPED_NATIVE_PRODUCER_ABI_V1')
    index['new_sources'] = [source_row(HERE / name, name) for name in INHERITED]
    manifest = next(row for row in old['dependency_sources'] if row['install_relative'] == 'phase1_deps/sensor/SOURCE_API_MANIFEST.json')
    original_C_pins = next(row for row in old['dependency_sources'] if row['install_relative'] == 'phase1_deps/actuation/SOURCE_PINS.json')
    index['dependency_sources'] = [source_row(B4 / name, 'phase1_deps/sensor/' + name) for name in
        ('source_api.py', 'field_snapshot.py', 'dependency_contract.py', 'passive_capture.py', 'CODEC_SOURCE_PINS.json')]
    index['dependency_sources'] += [copy.deepcopy(manifest), copy.deepcopy(original_C_pins),
        source_row(CODEC / 'typed_capture_codec.py', 'phase1_deps/codec/typed_capture_codec.py'),
        source_row(C2 / 'actuation_tap_v2.py', 'phase1_deps/actuation_c2/actuation_tap_v2.py')]
    index['original_B2_reference_seal'] = inherited['sensor']
    index['dependency_seals'].update(sensor=seals['sensor'], codec=seals['codec'],
                                     actuation_clock_scope_v2=seals['actuation_clock_scope_v2'])
    index['producer_abi'] = source_row(HERE / 'PRODUCER_ABI.json', 'PRODUCER_ABI.json')
    index['source_derivation'] = dict(kind='PHASE1_TYPED_NATIVE_MINIMAL_PRODUCER_SOURCE_DERIVATION_V1',
        v4_frozen_seal=seals['v4'], inherited_v4_source_derivation=old['source_derivation'],
        minimal_diff=minimal, native_B4_uses_unchanged_DEFAULT_fixed_22_plus_3=True,
        C2_source_schema_literal_unchanged=True, old_tests_reexecuted=False,
        actual_Torch_CPU_executed=False, actual_SDK_native_executed=False,
        new_resource_budget_approval_or_canonical_writer=False)
    index['full_B4_package_verified'] = True
    index['typed_codec_package_verified'] = True
    index['complete_C2_package_verified'] = True
    rows = index['original17'] + index['new_sources'] + index['dependency_sources'] + index['bootstrap_original_sources'] + [index['producer_abi']]
    aliases = [row['install_relative'] for row in rows]
    if len(set(aliases)) != len(rows):
        raise ValueError('Finite full SOURCE aliases overlap')
    bundle = dict(kind='PHASE1_TYPED_NATIVE_FINITE_SOURCE_BUNDLE_V1', source_only=True,
        typed_producer_schema=index['typed_producer_schema'], full_module_files=rows,
        original17=len(index['original17']), new_candidate_files=5, runtime_dependency_files=9,
        bootstrap_original_full_files=2, producer_abi_files=1,
        required_complete_original_static_tree_reference=old['full_original_static_tree_banks_and_vendor7_preservation'],
        baseline_provenance=old['full_static_baseline_provenance'],
        all_eight_runtime_trees_and_banks_REQUIRED=True, vendor7_full_original_files_REQUIRED=True,
        original_static_tree_is_not_replaced_by_this_finite_source_overlay=True,
        independently_pinned_complete_static_baseline='PENDING_PARENT_NEW_MATERIALIZER_REVIEW',
        materialized_files=0, stage_dispatch_or_copy_calls=0, native_executed=False,
        gate1='UNKNOWN', exact=False, capture_interface_passed=False, stage2_GO=False)
    return index, bundle


def write_metadata():
    if (HERE / 'SOURCE_SEAL.json').exists():
        raise RuntimeError('Frozen SOURCE package; new lineage required')
    index, bundle = build_metadata()
    for name, value in (('CAPTURE_SOURCE_INDEX.json', index), ('FINITE_SOURCE_BUNDLE.json', bundle)):
        path = HERE / name
        raw = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()
        if path.exists():
            before = path.read_bytes()
            if before != raw:
                path.write_bytes(raw)
        else:
            with path.open('xb') as stream:
                stream.write(raw)
    return dict(index=identity(HERE / 'CAPTURE_SOURCE_INDEX.json'), bundle=identity(HERE / 'FINITE_SOURCE_BUNDLE.json'),
                original17=17, candidate_files=5, dependency_files=9, bootstrap_files=2, ABI_files=1,
                frozen_upstream_members=dict(v4=13, sensor=21, codec=7, C2=5),
                original_sensor_sources=155, original_sensor_pin_references=435, original_actuation_sources=182,
                native_Torch_SDK_resource_or_stage_executed=False)


if __name__ == '__main__':
    print(json.dumps(write_metadata(), indent=2))
