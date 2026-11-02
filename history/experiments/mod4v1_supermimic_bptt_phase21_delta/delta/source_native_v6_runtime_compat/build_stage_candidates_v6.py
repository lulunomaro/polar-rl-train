"""Build NEW V6 source-only stage CLIs after an explicit parent-pinned V6 App helper.

Reads only exact small source files; never prepare/stage/dispatch/import SDK or owner.
Original V5 and all sealed sources remain byte-identical. Outputs are exclusive.
"""
from __future__ import annotations
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
OLD = PROJECT / 'source_stage_a1_native_v5'
POSE_SHA = '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f'
OLD_PINS = {
    'stage_a1_native_v5.py': '2f8bc706744b2efa7f7bd4b4b960125baad833b02f6afdc376814c8c071b05eb',
    'dispatch_a1_native_v5_once.py': '7178d8abfb4cf06d943bb2a4a7ea7cdf8e34102ffa9b1bba0d003385cb257319',
    'test_stage_dispatch_stdlib_v5.py': 'fa3c2beb5b5b84a15952c3bdde2676e306c405adb1464cb49e71c63c4e1f17e5',
}


def digest(raw): return hashlib.sha256(raw).hexdigest()


def load(name):
    raw = (OLD / name).read_bytes()
    assert digest(raw) == OLD_PINS[name], name
    return raw.decode('utf-8')


def replace_once(text, old, new):
    assert text.count(old) == 1, ('literal uniqueness', old, text.count(old))
    return text.replace(old, new, 1)


def replace_function(text, name, replacement):
    tree = ast.parse(text)
    matches = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(matches) == 1, name
    node = matches[0];lines = text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno - 1]) + replacement + ''.join(lines[node.end_lineno:])


def stamp_v6(text):
    # Lowercase logical worker/owner/shim/helper file names deliberately remain V5.
    # This particular historical bundle receipt remains the unchanged V5 ABI receipt.
    text = text.replace('CODE_DELIVERABLES_SHA256_V5.json', '__UNCHANGED_ABI_RECEIPT__')
    text = text.replace('V5', 'V6')
    text = text.replace('__UNCHANGED_ABI_RECEIPT__', 'CODE_DELIVERABLES_SHA256_V5.json')
    text = text.replace('V6_CODE_SEAL_SHA', 'V5_ABI_CODE_SEAL_SHA')
    text = text.replace('v5_code_seal_SHA', 'v5_abi_code_seal_SHA')
    text = text.replace('stage_a1_native_v5', 'stage_a1_native_v6')
    text = text.replace('dispatch_a1_native_v5_once', 'dispatch_a1_native_v6_once')
    return text


def write_once(name, text):
    raw = text.encode('utf-8')
    if name.endswith('.py'):
        ast.parse(text);compile(text, str(HERE / name), 'exec')
    with (HERE / name).open('xb') as stream: stream.write(raw)
    return dict(relative=name, bytes=len(raw), SHA=digest(raw))


def preserved_functions(old, new, names):
    def lookup(text):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    before = lookup(old);after = lookup(new)
    for name in names: assert before[name] == after[name], name
    return list(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app-helper-source', type=Path, required=True)
    parser.add_argument('--app-helper-sha', required=True)
    parser.add_argument('--app-helper-bytes', type=int, required=True)
    args = parser.parse_args()
    app = args.app_helper_source.resolve(strict=True)
    assert app.is_relative_to(PROJECT.resolve()) and 'v6' in app.parent.name.lower(), 'explicit NEW V6 source only'
    app_raw = app.read_bytes()
    assert digest(app_raw) == args.app_helper_sha and len(app_raw) == args.app_helper_bytes
    assert len(args.app_helper_sha) == 64 and all(c in '0123456789abcdef' for c in args.app_helper_sha)
    app_tree = ast.parse(app_raw.decode('utf-8'))
    app_names = {n.name for n in app_tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
    assert {'close_original_resources', 'evaluate_waited_worker', 'BoundedPoseCacheEventsV5', 'force_pose_cache_event_receipt_v5'} <= app_names, 'sealed V5 shim ABI absent'
    pose = HERE / 'pose_cache_runtime_adapter_v4.py';pose_raw = pose.read_bytes()
    assert len(pose_raw) == 18161 and digest(pose_raw) == POSE_SHA
    originals = {name: load(name) for name in OLD_PINS}
    stage = stamp_v6(originals['stage_a1_native_v5.py'])
    stage = replace_once(stage, "POSE_SHA = '73145a1caa7819e0938e66e53a1bb0be73e48d0d06c3cf9cd5dc76e9f0862209'", "POSE_SHA = '" + POSE_SHA + "'")
    stage = replace_once(stage, 'POSE_BYTES = 16757', 'POSE_BYTES = 18161')
    stage = replace_once(stage, "'worker_sources/app_close_semantics_v5.py': 'd64732c9310da2db59b349ad921862c78a33e2be5b60a442d456e8a62d63f3c1'", "'worker_sources/app_close_semantics_v5.py': '" + args.app_helper_sha + "'")
    stage = stage.replace('parent V6 code/API seal identity differs', 'unchanged V5 owner/worker/shim ABI seal identity differs')
    stage = stage.replace('pinned V6 owner source preflight API missing', 'pinned V5 owner source preflight API missing')
    dispatch = stamp_v6(originals['dispatch_a1_native_v5_once.py'])
    test = stamp_v6(originals['test_stage_dispatch_stdlib_v5.py'])
    replacement = "    mapping['worker_sources/pose_cache_runtime_adapter_v3.py'] = HERE / 'pose_cache_runtime_adapter_v4.py'\n    mapping['worker_sources/app_close_semantics_v5.py'] = PROJECT / " + repr(app.relative_to(PROJECT).as_posix()) + "\n    return mapping\n"
    old_tail = "    mapping['worker_sources/pose_cache_runtime_adapter_v3.py'] = PROJECT / 'source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py'\n    return mapping\n"
    test = replace_once(test, old_tail, replacement)
    test = replace_function(test, 'test_sealed_v5_runtime_pins', '''    def test_sealed_v5_runtime_pins(self):
        mapping = actual_fourteen_sources()
        for rel in (stage.OWNER_NAME, 'worker_sources/' + stage.WORKER_NAME, 'worker_sources/app_close_semantics_v5.py', 'worker_sources/resume_runtime_app_close_v5.py'):
            self.assertEqual(stage.identity(mapping[rel])['SHA'], stage.FIXED_PINS[rel])
''')
    additions = '''
class V6SourceCompatibility(unittest.TestCase):
    def test_only_two_actual_source_pins_changed(self):
        prior = PROJECT / 'source_stage_a1_native_v5' / 'stage_a1_native_v5.py'
        namespace = {}
        tree = ast.parse(prior.read_text())
        selected = [n for n in tree.body if isinstance(n, ast.Assign)]
        exec(compile(ast.Module(body=selected, type_ignores=[]), str(prior) + ':CONSTANTS_ONLY', 'exec'), namespace)
        changed = {key for key in stage.FIXED_PINS if stage.FIXED_PINS[key] != namespace['FIXED_PINS'][key]}
        self.assertEqual(changed, {'worker_sources/pose_cache_runtime_adapter_v3.py', 'worker_sources/app_close_semantics_v5.py'})
        self.assertEqual(len(stage.FIXED_PINS), 14)

    def test_logical_old_ABI_has_explicit_new_source_bytes(self):
        mapping = actual_fourteen_sources()
        self.assertEqual(mapping['worker_sources/pose_cache_runtime_adapter_v3.py'].name, 'pose_cache_runtime_adapter_v4.py')
        self.assertIn('v6', mapping['worker_sources/app_close_semantics_v5.py'].parent.name.lower())
        self.assertEqual(stage.POSE_BYTES, 18161)
        self.assertNotEqual(stage.POSE_SHA, '73145a1caa7819e0938e66e53a1bb0be73e48d0d06c3cf9cd5dc76e9f0862209')

    def test_old_V5_run_prefix_is_not_a_new_V6_purpose(self):
        run = 'MOD4V1_A1_RAW35_V5_NOT_REPLAYED'
        with self.assertRaises(ValueError):
            stage.make_plan(synthetic_template(), new_folder() / run, run, stage.import_pure_gates(CONTRACTS))

    def test_old_V5_parent_kind_is_not_a_new_V6_dispatch(self):
        root, run, _, sha, parent = fake_complete_stage()
        value = json.loads(parent.read_bytes());value['kind'] = 'PARENT_APPROVED_NEW_A1_NATIVE_V5_DISPATCH_ONCE'
        path = new_folder() / 'OLD_KIND_ONLY.json';stage.put_once(path, value)
        with self.assertRaises(ValueError): dispatch.verify_parent_marker(path, root, run, sha)

    def test_old_V5_index_kind_fails_before_source_access(self):
        value = {'kind': 'SEALED_A1_NATIVE_V5_SOURCE_INDEX_V1', 'sealed': True, 'v5_abi_code_seal_SHA': stage.V5_ABI_CODE_SEAL_SHA, 'files': []}
        with self.assertRaises(ValueError): stage.source_index_files(Path('DO_NOT_OPEN'), value)

    def test_V6_names_and_original_owner_are_separate(self):
        self.assertEqual(stage.OWNER_NAME, 'supermimic_original_owner_shared_app_close_candidate_v5.py')
        self.assertEqual(stage.WORKER_NAME, 'worker_supermimic_bptt_app_close_candidate_v5.py')
        self.assertIn('V6', stage.ROOT_MANIFEST_NAME)
        self.assertEqual(dispatch.CONSUMED_NAME, 'PARENT_DISPATCH_CONSUMED_V6.json')
        self.assertEqual(stage.SOURCE_INDEX_KIND, 'SEALED_A1_NATIVE_V6_SOURCE_INDEX_V1')

    def test_static_and_original_resource_gate_helpers_AST_unchanged(self):
        old = ast.parse((PROJECT / 'source_stage_a1_native_v5/stage_a1_native_v5.py').read_text())
        new = ast.parse((HERE / 'stage_a1_native_v6.py').read_text())
        def functions(tree): return {n.name: ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, ast.FunctionDef)}
        a, b = functions(old), functions(new)
        for name in ('require', 'sha_bytes', 'is_sha', 'denied_name', 'safe_relative', 'identity', 'read_metadata', 'put_once', 'write_bytes_once', 'collect_tree', 'verify_owner_AST', 'import_pure_gates', 'copy_materials', 'source_only_owner_verify'):
            self.assertEqual(a[name], b[name], name)

    def test_new_plan_still_exact_A1_legacy_no_skill_offset_or_reward_change(self):
        run = 'MOD4V1_A1_RAW35_V6_PLAN_SNAPSHOT'
        plan = stage.make_plan(synthetic_template(), new_folder() / run, run, stage.import_pure_gates(CONTRACTS))
        self.assertEqual(plan['bound_anchor_reward_changes'], 0)
        self.assertFalse(plan['command_tracking_fixed']);self.assertFalse(plan['sensor_projection_exact'])
        self.assertFalse(plan['old_A0_counts_spliced']);self.assertEqual(plan['native_counter_start'], 0)
        self.assertEqual(plan['original_authority_limits_unchanged'], dict(parent_seconds=3900, save_seconds=3600, exit_headroom_seconds=300, resource_wait_seconds=1800))
        for entry in plan['entries']:
            self.assertEqual(entry['pose_cache_runtime_adapter']['SHA'], stage.POSE_SHA)
            self.assertEqual(entry['pose_cache_runtime_adapter']['bytes'], 18161)
            self.assertNotIn('resume_bptt', entry)

'''
    test = replace_once(test, '\ndef main():\n', '\n' + additions + '\ndef main():\n')
    # Pure functions below are byte/AST identical; versions affect metadata and pins only.
    protected = preserved_functions(originals['stage_a1_native_v5.py'], stage,
        ['require', 'sha_bytes', 'is_sha', 'denied_name', 'safe_relative', 'identity', 'read_metadata', 'put_once', 'write_bytes_once', 'collect_tree', 'verify_owner_AST', 'import_pure_gates', 'copy_materials', 'source_only_owner_verify'])
    preserved_dispatch = preserved_functions(originals['dispatch_a1_native_v5_once.py'], dispatch,
        ['verify_file_rows', 'verify_parent_marker', 'child_identity_metadata'])
    outputs = []
    for name, text in [('stage_a1_native_v6.py', stage), ('dispatch_a1_native_v6_once.py', dispatch), ('test_stage_dispatch_stdlib_v6.py', test)]:
        outputs.append(write_once(name, text))
    patch = ''.join(difflib.unified_diff(originals['stage_a1_native_v5.py'].splitlines(keepends=True), stage.splitlines(keepends=True), fromfile='sealed_source_stage_a1_native_v5/stage_a1_native_v5.py', tofile='NEW_source_native_v6_runtime_compat/stage_a1_native_v6.py'))
    patch += ''.join(difflib.unified_diff(originals['dispatch_a1_native_v5_once.py'].splitlines(keepends=True), dispatch.splitlines(keepends=True), fromfile='sealed_source_stage_a1_native_v5/dispatch_a1_native_v5_once.py', tofile='NEW_source_native_v6_runtime_compat/dispatch_a1_native_v6_once.py'))
    outputs.append(write_once('STAGE_RUNTIME_COMPAT_DIFF_V6.patch', patch))
    receipt = dict(kind='NEW_V6_SOURCE_ONLY_STAGE_CANDIDATE_BUILD_NO_STAGE_OR_DISPATCH', passed=True,
        explicit_parent_app_helper=dict(path=str(app), SHA=digest(app_raw), bytes=len(app_raw)),
        pose_adapter=dict(path=str(pose), SHA=POSE_SHA, bytes=len(pose_raw)),
        original_V5_sources=[dict(relative=n, SHA=digest((OLD/n).read_bytes())) for n in OLD_PINS],
        exact_original_stage_functions_AST=protected, exact_original_dispatch_functions_AST=preserved_dispatch,
        source_replacements=2, original_owner_worker_shim_bytes_changed=False,
        actual_stage_dispatch_SDK_GPU_PT_C_Git_operations=0, artifacts=outputs)
    write_once('BUILD_STAGE_CANDIDATES_V6.json', json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__': main()
