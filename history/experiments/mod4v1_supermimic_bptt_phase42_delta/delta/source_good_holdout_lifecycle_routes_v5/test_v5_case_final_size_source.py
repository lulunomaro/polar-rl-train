"""NEW twelve SOURCE tests: own full functions, deterministic memory/owned temp only.

No old suite, actual task module, original FINAL, App/Base substitute, watcher,
collector, SSH, or native execution. A fake transport never executes its command.
"""
from pathlib import Path
import ast
import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R = HERE.parent
OLD = R / 'source_good_holdout_lifecycle_routes_v4'
import good_holdout_contract as C
import good_holdout_remote_reader as M
import collect_good_holdout_result as K

CASE_NAMES = ('cases/CURB_PROTECTED878/FINAL.json', 'cases/SLOPE135/FINAL.json')
AUDIT = dict(native_imports=0, forbidden_artifact_accesses=0,
             process_network_signal_or_lock_operations=0, forbidden_production_calls=0)
NATIVE = {'torch', 'numpy', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'carb', 'warp', 'rsl_rl', 'tensordict', 'psutil', 'fcntl'}
STDLIB = Path(sys.base_prefix).resolve()
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'


def audit(event, args):
    if event == 'import' and str(args[0]).split('.')[0] in NATIVE:
        AUDIT['native_imports'] += 1
        raise AssertionError('native import blocked in SOURCE tests')
    if event.startswith('socket.') or event in ('subprocess.Popen', 'os.system', 'os.kill', 'os.killpg', 'fcntl.flock', 'os.startfile'):
        AUDIT['process_network_signal_or_lock_operations'] += 1
        raise AssertionError('process/network/signal/lock blocked in SOURCE tests')
    if event == 'open' and not isinstance(args[0], int):
        path = Path(os.fsdecode(args[0])).resolve()
        parts = {v.lower() for v in path.parts}
        leaf = path.name.lower()
        denied = (path.suffix.lower() in ('.pt', '.pth', '.ckpt', '.safetensors', '.npz', '.npy', '.onnx', '.jsonl')
                  or 'reports' in parts or 'budget' in leaf or leaf.endswith('.lock'))
        writable = ((len(args) > 1 and type(args[1]) is str and any(c in args[1] for c in 'wax+'))
                    or (len(args) > 2 and type(args[2]) is int and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
        if denied or not (path.is_relative_to(R) or path.is_relative_to(T) or path.is_relative_to(STDLIB)) or (writable and not path.is_relative_to(HERE)):
            AUDIT['forbidden_artifact_accesses'] += 1
            raise AssertionError('SOURCE artifact scope blocked: ' + str(path))


def profile(frame, event, arg):
    if event != 'call':
        return
    path = Path(frame.f_code.co_filename)
    leaf = path.name
    name = frame.f_code.co_name
    blocked = (leaf == 'good_holdout_parent_actual_wait_controller_v1.py'
               or (leaf == 'good_holdout_remote_reader.py' and name in ('watch', 'remote_main', 'load_metadata_closure'))
               or (leaf == 'collect_good_holdout_result.py' and name in ('collect', 'main', 'connect_original', 'atomic_closed', 'conditional_two_seed_summary'))
               or leaf.startswith('stage_good_expert_holdout_')
               or leaf in ('good_expert_holdout_runtime_v1.py', 'producer_teacher_guard_v1.py', 'a1_frozen_eval_runtime_v2.py', 'app_close_semantics_v5.py', 'app_close_semantics_v6.py', 'resume_runtime_contracts_v3.py'))
    if blocked:
        AUDIT['forbidden_production_calls'] += 1
        raise AssertionError('actual production function blocked: ' + leaf + ':' + name)


@contextlib.contextmanager
def owned_temp():
    temp = tempfile.TemporaryDirectory(prefix='_SOURCE_FAKE_V5_', dir=HERE)
    root = Path(temp.name).resolve()
    assert root.parent == HERE and root.name.startswith('_SOURCE_FAKE_V5_') and not root.is_symlink()
    try:
        yield root
    finally:
        # Verify the intended resolved target before stdlib recursive cleanup.
        assert root.parent == HERE and root.name.startswith('_SOURCE_FAKE_V5_') and not root.is_symlink()
        temp.cleanup()


def encode(value):
    return json.dumps(value, allow_nan=False).encode('utf-8')


def sized_object(size, *, tag='SYNTHETIC_SOURCE_ONLY'):
    value = dict(tag=tag, metrics={'unknown': None}, route_scope={'fixture': True},
                 fresh_fullDR_before={'fixture': True}, fresh_fullDR_after={'fixture': True},
                 source_cache={'fixture_only_no_checkpoint': True},
                 unknown_future={'unicode': '保留🌑', 'nested': [None, False, {'x': 17}]}, padding='')
    delta = size - len(encode(value))
    assert delta >= 0
    value['padding'] = 'x' * delta
    raw = encode(value)
    assert len(raw) == size
    return value, raw


def put(root, name, raw):
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    assert target.resolve().is_relative_to(root)
    target.write_bytes(raw)
    return target


def info(raw):
    return dict(status='READ', read_count=1, bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest(),
                whole_JSON_read=True, projection_applied=False, terminal_full_original_bytes=True)


def ast_nodes(path):
    text = path.read_text(encoding='utf-8')
    tree = ast.parse(text)
    nodes = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            assignments[node.targets[0].id] = node.value
    return text, tree, nodes, assignments


def packet_with_documents(documents, metadata=None):
    return dict(kind='GOOD_HOLDOUT_OWN_METADATA_PACKET_V1', root='SOURCE_ONLY_FAKE_ROOT',
                group_id='SOURCE_ONLY_FAKE_GROUP', seed=20260929,
                evaluation_purpose=C.purpose(20260929), documents=documents,
                file_metadata={} if metadata is None else metadata,
                secondary_worker_errors={r: [] for r in C.REQUESTED}, collector_errors=[],
                metadata_closure=None, cached_validation=None,
                polling={'collector_cap_reached': None, 'outer_wait_observed': None, 'native_deadline_extended': False},
                whole_original_FINALs_read_once=False, FINAL_projection_applied=False,
                read_only_own_metadata=True, logs={}, unknown_packet={'preserve': [None, '原字段']}, padding='')


def sized_packet(size):
    cases = {r: {'role': r, 'unknown': {'a': [None, 1, 'fixture']}} for r in C.REQUESTED}
    rows = [dict(role=r, data=cases[r], unknown_row={'keep': True}) for r in C.REQUESTED]
    documents = {'FINAL.json': {'rows': rows, 'unknown_group': 'keep'}, 'TERMINAL_ROWS.json': rows}
    documents.update({'cases/' + r + '/FINAL.json': cases[r] for r in C.REQUESTED})
    value = packet_with_documents(documents)
    delta = size - len(encode(value))
    assert delta >= 0
    value['padding'] = 'p' * delta
    raw = encode(value)
    assert len(raw) == size
    return value, raw


class FakeChannel:
    def recv_exit_status(self):
        return 0


class FakeStream(io.BytesIO):
    def __init__(self, raw):
        super().__init__(raw)
        self.channel = FakeChannel()
        self.requested = []

    def read(self, size=-1):
        self.requested.append(size)
        return super().read(size)


class FakeTransport:
    """Whole existing remote_packet is called; captured command is never run."""
    def __init__(self, raw):
        self.outgoing = FakeStream(raw)
        self.stderr = FakeStream(b'')
        self.commands = []

    def exec_command(self, command, timeout):
        self.commands.append((command, timeout))
        return io.BytesIO(), self.outgoing, self.stderr


def source_dispatch():
    # Pure synthetic metadata; never passed to a launcher, watch, main or collect.
    return dict(kind=C.DISPATCH_KIND, root=C.BASE + '/tasks/SOURCE_FAKE_20260929',
                group_id='SOURCE_FAKE_20260929', seed=20260929, GPU_UUID='GPU-00000000',
                evaluation_purpose=C.purpose(20260929), controller={'pid': 71, 'linux_start_ticks': '101'},
                parent={'pid': 72, 'linux_start_ticks': '102'}, parent_source_SHA=C.PARENT_PIN[1],
                controller_source_SHA=C.CONTROLLER_SOURCE_PIN[1], stage_receipt_SHA256='3' * 64,
                GROUP_PLAN_bytes=23, GROUP_PLAN_SHA256='4' * 64,
                actual_native_parent_Popen_calls=1, SDK_scene_or_skill_admission=False)


class CaseFinalSizeSourceTests(unittest.TestCase):
    def test_01_whole_source_delta_and_pending_final_pins_before_IO(self):
        for name, pin in {
            'good_holdout_parent_actual_wait_controller_v1.py': (5170, '4cb6994a9afa0b399598f9af012529c9cd06bf6a8ad2e91c7d34f1c8496399c0'),
            'collect_good_holdout_result.py': (15045, '988f4fcce7f58fe33c105e86e2f1028c9b37ded7696bba00250d02b0359d3eab')}.items():
            old = (OLD / name).read_bytes(); new = (HERE / name).read_bytes()
            self.assertEqual(new, old)
            self.assertEqual((len(new), hashlib.sha256(new).hexdigest()), pin)
        old_text, old_tree, old_nodes, old_assign = ast_nodes(OLD / 'good_holdout_remote_reader.py')
        new_text, new_tree, new_nodes, new_assign = ast_nodes(HERE / 'good_holdout_remote_reader.py')
        self.assertEqual(set(old_nodes), set(new_nodes))
        for name in old_nodes:
            if name != 'maximum':
                self.assertEqual(ast.dump(old_nodes[name]), ast.dump(new_nodes[name]), name)
                self.assertEqual(ast.get_source_segment(old_text, old_nodes[name]), ast.get_source_segment(new_text, new_nodes[name]), name)
        self.assertEqual(new_text.replace("    if name in ('cases/CURB_PROTECTED878/FINAL.json', 'cases/SLOPE135/FINAL.json'):\n        return C.CASE_FINAL_MAX\n", '', 1), old_text)
        a, _, old_funcs, old_a = ast_nodes(OLD / 'good_holdout_contract.py')
        b, _, new_funcs, new_a = ast_nodes(HERE / 'good_holdout_contract.py')
        self.assertEqual(set(old_funcs), set(new_funcs))
        for name in old_funcs:
            if name == 'validate_stage':
                old_src = ast.get_source_segment(a, old_funcs[name])
                new_src = ast.get_source_segment(b, new_funcs[name])
                self.assertEqual(new_src.replace("stage['source_derivation_version'] == 7", "stage['source_derivation_version'] == 6").replace('final V7 materialization', 'final V6 materialization'), old_src)
            else:
                self.assertEqual(ast.dump(old_funcs[name]), ast.dump(new_funcs[name]), name)
        changed = {k for k in set(old_a) | set(new_a) if k not in old_a or k not in new_a or ast.dump(old_a[k]) != ast.dump(new_a[k])}
        self.assertEqual(changed, {'STAGE_KIND', 'RUNTIME_PIN', 'INDEX_PIN', 'STAGER_SOURCE_PINS', 'OVERLAY_PINS', 'CASE_FINAL_MAX'})
        self.assertEqual((C.PLAN_MAX, C.CASE_FINAL_MAX, C.GROUP_MAX, C.EXPORT_MAX), (262144, 2097152, 8388608, 16777216))
        self.assertEqual(C.STAGE_NAME, 'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json')
        self.assertEqual(C.STAGE_KIND, 'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V7')
        if C.STAGER_SOURCE_PINS is None:
            with mock.patch.object(Path, 'open', side_effect=AssertionError('no I/O before final SOURCE pins')):
                with self.assertRaisesRegex(ValueError, 'PENDING_FINAL_D664'):
                    C.require_final_pins()
                with self.assertRaisesRegex(ValueError, 'PENDING_FINAL_D664'):
                    C.validate_stage(b'{}', b'{}', b'', root='', group_id='', seed=20260929, gpu_uuid='', stage_sha='0' * 64)
        else:
            self.assertTrue(C.require_final_pins())
            from source_pins import verify_sources
            self.assertEqual(verify_sources()['actual_native_binding'], 'UNKNOWN')

    def test_02_exact_selector_never_expands_other_case_aliases(self):
        for name in CASE_NAMES:
            self.assertEqual(M.maximum(name), C.CASE_FINAL_MAX)
        for name in M.SMALL:
            expected = C.PLAN_MAX if name == 'GROUP_PLAN.json' or name.startswith('cases/') else C.GROUP_MAX
            self.assertEqual(M.maximum(name), expected, name)
        for name in ('FINAL.json', 'TERMINAL_ROWS.json'):
            self.assertEqual(M.maximum(name), C.GROUP_MAX)
        for role in ('E3', 'W35', 'CURB_PROTECTED878_extra', 'SLOPE135_extra', 'H1'):
            self.assertEqual(M.maximum('cases/' + role + '/FINAL.json'), C.PLAN_MAX)
        for name in CASE_NAMES:
            for changed in (name.lower(), name + '.partial', name + '/', name.replace('/', '\\'), name.replace('FINAL.json', 'FINAL.JSON'), name.replace('cases/', 'cases/./'), name.replace('/FINAL.json', '/nested/FINAL.json')):
                self.assertNotEqual(M.maximum(changed), C.CASE_FINAL_MAX, changed)
        with owned_temp() as root:
            reader = M.MetadataReader(root)
            with self.assertRaisesRegex(ValueError, 'metadata alias rejected'):
                reader.read('cases/E3/FINAL.json', terminal=True)
            self.assertEqual(reader.info, {})

    def test_03_both_case_complete_dict_below_and_exact_2MiB(self):
        for name in CASE_NAMES:
            for size in (C.CASE_FINAL_MAX - 1, C.CASE_FINAL_MAX):
                with self.subTest(name=name, size=size), owned_temp() as root:
                    expected, raw = sized_object(size)
                    put(root, name, raw)
                    reader = M.MetadataReader(root)
                    with mock.patch.object(json, 'loads', wraps=json.loads) as decode:
                        value = reader.read(name, terminal=True)
                        self.assertEqual(decode.call_count, 1)
                    self.assertEqual(value, expected)
                    self.assertEqual(reader.info[name], info(raw))
                    self.assertIs(reader.read(name, terminal=True), value)
                    self.assertEqual(reader.info[name]['read_count'], 1)
                    self.assertEqual(M._complete(reader.info, name)['bytes'], size)

    def test_04_2MiB_plus1_and_small_case_limits_fail_before_open_decode(self):
        names = list(CASE_NAMES) + ['GROUP_PLAN.json'] + ['cases/' + role + '/' + name for role in C.REQUESTED for name in ('task.json', 'WORKER_SCENE_READY.json', 'WORKER_ERROR.json')]
        for name in names:
            with self.subTest(name=name), owned_temp() as root:
                limit = M.maximum(name)
                _, raw = sized_object(limit + 1)
                put(root, name, raw)
                reader = M.MetadataReader(root)
                with mock.patch.object(Path, 'open', side_effect=AssertionError('oversize must fail at stat')), mock.patch.object(json, 'loads', side_effect=AssertionError('oversize must not decode')):
                    self.assertIsNone(reader.read(name, terminal=name in M.BIG))
                self.assertEqual(reader.info[name]['status'], 'ERROR')
                self.assertEqual(reader.info[name]['read_count'], 0)
                self.assertIsNone(reader.info[name]['bytes'])
                self.assertIsNone(reader.info[name]['SHA256'])
                self.assertNotIn(name, reader.cache)
                self.assertIn('original metadata bound exceeded', reader.errors[0]['error'])

    def test_05_truncated_invalid_and_case_nondict_keep_original_failure_gates(self):
        name = CASE_NAMES[0]
        for raw in (b'{"padding":"unfinished', b'{"x":}', b'\xff'):
            with self.subTest(raw=raw), owned_temp() as root:
                put(root, name, raw); reader = M.MetadataReader(root)
                self.assertIsNone(reader.read(name, terminal=True))
                self.assertEqual(reader.info[name]['status'], 'ERROR')
                self.assertEqual(reader.info[name]['read_count'], 1)
                self.assertIsNone(reader.info[name]['SHA256'])
                self.assertNotIn(name, reader.cache)
        for value in (None, [], 7, 'source-fixture'):
            with self.subTest(value=value), owned_temp() as root:
                raw = encode(value); put(root, name, raw); reader = M.MetadataReader(root)
                self.assertEqual(reader.read(name, terminal=True), value)
                self.assertEqual(M._complete(reader.info, name)['SHA256'], hashlib.sha256(raw).hexdigest())
                # None denotes unavailable closure, NOT an App/Base stub. The
                # existing own gate fails before using either original module.
                with self.assertRaisesRegex(ValueError, 'complete successful own role/group FINAL required'):
                    M.validate_case_cache(reader.cache, reader.info, C.REQUESTED[0], {}, {'group_id': 'FAKE'}, {'runtime': None, 'app': None}, {})
        with owned_temp() as root:
            put(root, 'TERMINAL_ROWS.json', b'[]'); reader = M.MetadataReader(root)
            self.assertEqual(reader.read('TERMINAL_ROWS.json', terminal=True), [])

    def test_06_complete_uses_shared_cap_and_strict_once_metadata(self):
        for name in CASE_NAMES + ('GROUP_PLAN.json', 'FINAL.json', 'TERMINAL_ROWS.json'):
            limit = M.maximum(name)
            good = dict(status='READ', read_count=1, bytes=limit, SHA256='1' * 64, whole_JSON_read=True, projection_applied=False)
            self.assertIs(M._complete({name: good}, name), good)
            for key, value in (('bytes', limit + 1), ('bytes', 0), ('bytes', True), ('read_count', True), ('read_count', 2), ('whole_JSON_read', False), ('projection_applied', True), ('status', 'ERROR'), ('SHA256', 'bad')):
                bad = dict(good); bad[key] = value
                with self.subTest(name=name, key=key, value=value), self.assertRaisesRegex(ValueError, 'complete once-cached'):
                    M._complete({name: bad}, name)
        _, _, nodes, _ = ast_nodes(HERE / 'good_holdout_remote_reader.py')
        for node in (nodes['_complete'], nodes['MetadataReader']):
            self.assertTrue(any(isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == 'maximum' for v in ast.walk(node)))

    def test_07_equal_decoded_objects_are_not_interchangeable_raw_identity(self):
        expected = {'unknown_future': {'x': [1, None, '保留']}, 'counts': None}
        one = json.dumps(expected, allow_nan=False).encode('utf-8')
        two = json.dumps(expected, indent=2, allow_nan=False).encode('utf-8') + b'\n'
        self.assertNotEqual(one, two)
        receipts = []
        for raw in (one, two):
            with owned_temp() as root:
                put(root, CASE_NAMES[0], raw); reader = M.MetadataReader(root)
                self.assertEqual(reader.read(CASE_NAMES[0], terminal=True), expected)
                receipts.append(reader.info[CASE_NAMES[0]])
        self.assertNotEqual((receipts[0]['bytes'], receipts[0]['SHA256']), (receipts[1]['bytes'], receipts[1]['SHA256']))
        for raw, receipt in zip((one, two), receipts):
            self.assertEqual((receipt['bytes'], receipt['SHA256']), (len(raw), hashlib.sha256(raw).hexdigest()))
            self.assertFalse(receipt['projection_applied'])

    def test_08_all_four_whole_original_caches_preserve_unknowns_and_rows(self):
        cases = {r: sized_object(C.PLAN_MAX + 99, tag='SOURCE_ONLY_' + r)[0] for r in C.REQUESTED}
        rows = [dict(role=r, data=cases[r], unknown_row=[None, {'keep': 9}]) for r in C.REQUESTED]
        documents = {'FINAL.json': {'rows': rows, 'unknown_group': {'keep': 'whole'}}, 'TERMINAL_ROWS.json': rows}
        documents.update({'cases/' + r + '/FINAL.json': cases[r] for r in C.REQUESTED})
        with owned_temp() as root:
            raws = {name: encode(value) for name, value in documents.items()}
            for name, raw in raws.items():
                put(root, name, raw)
            reader = M.MetadataReader(root)
            for name in M.BIG:
                value = reader.read(name, terminal=True)
                self.assertIs(reader.read(name, terminal=True), value)
                self.assertEqual(M._complete(reader.info, name), info(raws[name]))
            self.assertEqual(reader.cache, documents)
            self.assertEqual(reader.cache['FINAL.json']['rows'], reader.cache['TERMINAL_ROWS.json'])
            for row in reader.cache['TERMINAL_ROWS.json']:
                original = reader.cache['cases/' + row['role'] + '/FINAL.json']
                self.assertEqual(row['data'], original)
                self.assertIsNot(row['data'], original)
            self.assertEqual(reader.raw_cache, {})
            with self.assertRaisesRegex(ValueError, 'only at terminal'):
                M.MetadataReader(root).read(CASE_NAMES[0])

    def test_09_changed_stat_during_after_read_and_disappearance_are_errors(self):
        name = CASE_NAMES[0]
        with owned_temp() as root:
            path = put(root, name, b'{"unknown":null}'); reader = M.MetadataReader(root)
            value = reader.read(name, terminal=True); old_hash = reader.info[name]['SHA256']
            path.write_bytes(path.read_bytes() + b' ')
            self.assertIsNone(reader.read(name, terminal=True))
            self.assertIs(reader.cache[name], value)
            self.assertEqual(reader.info[name]['read_count'], 1)
            self.assertEqual(reader.info[name]['SHA256'], old_hash)
            self.assertEqual(reader.info[name]['status'], 'ERROR')
            self.assertIn('changed after its sole read', reader.errors[0]['error'])
        with owned_temp() as root:
            path = put(root, name, b'{"unknown":null}'); reader = M.MetadataReader(root)
            reader.read(name, terminal=True)
            assert path.resolve().is_relative_to(root) and path.name == 'FINAL.json'
            path.unlink()
            self.assertIsNone(reader.read(name, terminal=True))
            self.assertEqual(reader.info[name]['read_count'], 1)
            self.assertIn('disappeared after observation', reader.errors[-1]['error'])
        with owned_temp() as root:
            path = put(root, name, b'{"unknown":null}'); reader = M.MetadataReader(root)
            original_open = Path.open
            class MutatingRead:
                def __enter__(self):
                    self.stream = original_open(path, 'rb'); return self
                def __exit__(self, *args):
                    self.stream.close()
                def read(self, size):
                    raw = self.stream.read(size)
                    with original_open(path, 'ab') as writer:
                        writer.write(b' ')
                    return raw
            def intercept(target, *args, **kwargs):
                if target == path and args and args[0] == 'rb':
                    return MutatingRead()
                return original_open(target, *args, **kwargs)
            with mock.patch.object(Path, 'open', intercept):
                self.assertIsNone(reader.read(name, terminal=True))
            self.assertNotIn(name, reader.cache)
            self.assertEqual(reader.info[name]['read_count'], 1)
            self.assertIsNone(reader.info[name]['SHA256'])
            self.assertIn('changed during complete bounded read', reader.errors[0]['error'])

    def test_10_full_packet_wire_16MiB_and_plus1_and_existing_print_LF(self):
        dispatch = source_dispatch()
        for serialized_bytes, accepted in ((C.EXPORT_MAX - 1, True), (C.EXPORT_MAX, False)):
            packet, raw = sized_packet(serialized_bytes)
            wire = raw + b'\n'
            self.assertEqual(len(wire), C.EXPORT_MAX + (not accepted))
            fake = FakeTransport(wire)
            if accepted:
                result = K.remote_packet(fake, dispatch)
                result.pop('transport')
                self.assertEqual(result, packet)
                self.assertEqual(set(result['documents']), set(M.BIG))
                self.assertFalse(result['FINAL_projection_applied'])
            else:
                with mock.patch.object(json, 'loads', side_effect=AssertionError('overbound wire must not decode')):
                    with self.assertRaisesRegex(ValueError, 'complete metadata export/stdout exceeds bound'):
                        K.remote_packet(fake, dispatch)
            self.assertEqual(fake.outgoing.requested, [C.EXPORT_MAX + 1])
            self.assertEqual(fake.stderr.requested, [65537])
            self.assertEqual(len(fake.commands), 1)
        # Source-lock complete producer/export functions; no remote_main call.
        for name in ('good_holdout_remote_reader.py', 'collect_good_holdout_result.py'):
            a, _, old_nodes, _ = ast_nodes(OLD / name); b, _, new_nodes, _ = ast_nodes(HERE / name)
            func = 'remote_main' if name.startswith('good_') else 'remote_packet'
            self.assertEqual(ast.get_source_segment(a, old_nodes[func]), ast.get_source_segment(b, new_nodes[func]))
        _, _, nodes, _ = ast_nodes(HERE / 'good_holdout_remote_reader.py')
        main = nodes['remote_main']
        self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'print' and len(n.args) == 1 and isinstance(n.args[0], ast.Name) and n.args[0].id == 'raw' for n in ast.walk(main)))

    def test_11_individual_file_caps_do_not_guarantee_whole_packet_export(self):
        cases = {r: sized_object(C.CASE_FINAL_MAX, tag='SOURCE_ONLY_' + r)[0] for r in C.REQUESTED}
        rows = [dict(role=r, data=cases[r], unknown_row_blob='r' * (1024 * 1024)) for r in C.REQUESTED]
        documents = {'FINAL.json': {'rows': rows, 'unknown_group_blob': 'g' * 256}, 'TERMINAL_ROWS.json': rows}
        documents.update({'cases/' + r + '/FINAL.json': cases[r] for r in C.REQUESTED})
        with owned_temp() as root:
            for name, value in documents.items():
                raw = encode(value)
                self.assertLessEqual(len(raw), M.maximum(name))
                put(root, name, raw)
            reader = M.MetadataReader(root)
            for name in M.BIG:
                self.assertIsNotNone(reader.read(name, terminal=True))
                M._complete(reader.info, name)
            packet = packet_with_documents(reader.cache, reader.info)
            raw = encode(packet)
            self.assertGreater(len(raw), C.EXPORT_MAX)
            fake = FakeTransport(raw + b'\n')
            with self.assertRaisesRegex(ValueError, 'complete metadata export/stdout exceeds bound'):
                K.remote_packet(fake, source_dispatch())
            self.assertEqual(reader.cache, documents)
            for name in M.BIG:
                self.assertEqual(reader.info[name]['read_count'], 1)
                self.assertFalse(reader.info[name]['projection_applied'])
            self.assertFalse(packet['FINAL_projection_applied'])
            self.assertIs(packet['documents'], reader.cache)

    def test_12_historical_grade_ERROR_outerwait_failure_and_unknown_counts_stay(self):
        dispatch = source_dispatch()
        producer = dict(kind='CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1', passed_closed_reference_source_grade=False,
                        original_error=True, reasons=['SOURCE_ONLY_SYNTHETIC_OLD_CLOSE_ERROR'], checked_roles=list(C.REQUESTED),
                        group_root=dispatch['root'], batch_purpose=dispatch['evaluation_purpose'])
        outer = dict(dispatch, kind=C.WAITED_KIND, actual_parent_p_wait_returned=True, returncode=1,
                     controller_errors=[], original_parent_resource_close_wait_not_replaced=True)
        documents = {C.GRADE: producer, C.WAITED: outer, 'cases/' + C.REQUESTED[0] + '/WORKER_ERROR.json': {'error': 'SYNTHETIC_ERROR'},
                     'PARENT_EXIT_SCOPE.json': {'all_own_children_waited': True, 'child_waits': [dict(role=r, actual_waited=True, returncode=0) for r in C.REQUESTED],
                      'original_single_GPU_private_EX_released': True, 'original_global_finite_EX_released': True, 'errors': [], 'canonical_writes': 0}}
        packet = packet_with_documents(documents)
        # Only pending metadata pins are given deterministic memory rows for this
        # independent failure test. No App/Base object or execution is fabricated.
        synthetic_pins = {k: {'path': 'SOURCE_ONLY_SYNTHETIC', 'bytes': 1, 'SHA256': '1' * 64} for k in ('source', 'index', 'seal', 'mirror')}
        with mock.patch.object(C, 'STAGER_SOURCE_PINS', C.STAGER_SOURCE_PINS or synthetic_pins):
            result = K.summarize(dispatch, packet)
        self.assertFalse(result['passed_closed_good_reference_execution'])
        self.assertEqual(result['status'], 'FAILED_ORIGINAL_ERROR_OR_SOURCE_GRADE')
        self.assertIs(result['producer_original_source_grade'], producer)
        self.assertFalse(result['producer_grade_rewritten'])
        self.assertEqual(result['actual_outer_parent_returncode'], 1)
        self.assertTrue(result['gates']['original_ownchild_actual_waits'])
        self.assertTrue(result['gates']['original_both_EX_released'])
        self.assertFalse(result['gates']['producer_original_source_grade'])
        self.assertFalse(result['gates']['independent_outer_actual_Popen_wait'])
        self.assertIsNone(result['pooled_whole_skill_rate'])
        self.assertIsNone(result['relative_improvement'])
        self.assertFalse(result['stage2_GO'])
        for role in C.REQUESTED:
            self.assertTrue(all(v is None for v in result['observed_counts'][role].values()))
        self.assertIsNone(C.nullable_count(True))
        self.assertIsNone(C.nullable_count(-1))


def main():
    sys.addaudithook(audit)
    sys.setprofile(profile)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CaseFinalSizeSourceTests)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    sys.setprofile(None)
    log = stream.getvalue()
    print(log, end='')
    report = dict(kind='GOOD_HOLDOUT_LIFECYCLE_V5_CASE_FINAL_SIZE_SOURCE_TESTS',
                  scope='NEW_TWELVE_FAKE_TEMP_MEMORY_AST_NOT_PRIOR40_11_8_7_OR_NATIVE',
                  tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                  passed=result.wasSuccessful(), audit=AUDIT, excluded_test_names=[], declared_suite=12,
                  old_test_modules_replayed=False, actual_task_modules_imported=False,
                  actual_controller_watch_collect_or_main_executed=False,
                  App_Base_substitute_created=False, AST_cropped_production_execution=False,
                  original_reports_or_FINALs_read=False, fake_transport_command_executed=False,
                  D7_final_pins_received=C.STAGER_SOURCE_PINS is not None,
                  actual_native_binding='UNKNOWN', actual_quality=None, stage2_GO=False)
    if '--receipt' in sys.argv:
        for name in ('SOURCE_TEST_LOG.txt', 'SOURCE_TEST_REPORT.json'):
            assert not (HERE / name).exists(), 'exclusive NEW SOURCE test receipt only'
        (HERE / 'SOURCE_TEST_LOG.txt').write_text(log, encoding='utf-8')
        actual = (HERE / 'SOURCE_TEST_LOG.txt').read_bytes()
        report['SOURCE_test_log'] = {'bytes': len(actual), 'SHA256': hashlib.sha256(actual).hexdigest()}
        with (HERE / 'SOURCE_TEST_REPORT.json').open('x', encoding='utf-8') as writer:
            json.dump(report, writer, indent=2, allow_nan=False)
            writer.write('\n')
    print(json.dumps(report, ensure_ascii=False))
    return 0 if result.wasSuccessful() and result.testsRun == 12 and not result.skipped and not any(AUDIT.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
