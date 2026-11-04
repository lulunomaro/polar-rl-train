"""Own stdlib PREINSTALL verifier tests only. No capture/control/sample calls.

Imports the frozen stdlib publisher and FakeTensor, NOT old test suites, SDK,
Torch, worker or passive_capture. Live Python mutations are scoped/restored;
source file bytes stay unchanged. This is no tensor/numerical/native proof.
"""
import ast
from copy import deepcopy
import functools
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT / 'source_phase1_typed_capture_codec_v1'))

import typed_capture_codec as publisher
import dependency_contract as contract
from field_snapshot import FieldSnapshot
from fake_tensor import FakeTensor
from source_api import pin


def own_zero_kwdefault(*, zero=0):
    """Never invoked: own-source helper for int-zero KW default proof."""
    return zero


def fixture():
    index = FakeTensor([0, 1, 2, 3, 4, 5, 6, 7], 'torch.int64')
    codec = publisher.CaptureCodec(FakeTensor, witness_index=index,
                                   witness_env_ids=(0, 1, 2, 3, 4, 5, 6, 7), n=80)
    return FieldSnapshot(codec), publisher.ControlLedger(codec, controls=64, run_id='V4_SOURCE_PREINSTALL')


class StrictDependencyTests(unittest.TestCase):
    def setUp(self):
        self.snapshot, self.ledger = fixture()
        self.pins = json.loads((HERE / 'CODEC_SOURCE_PINS.json').read_text(encoding='utf-8'))
        self.original_operations = dict(FakeTensor.operations)

    def verify(self, pins=None):
        return contract.verify_typed_dependency(self.snapshot, self.ledger, dependency_pins=pins)

    def tearDown(self):
        self.assertEqual(dict(FakeTensor.operations), self.original_operations)
        self.assertEqual(self.ledger._packs, [])
        self.assertIs(self.ledger._open, None)
        self.assertIs(self.ledger._finished, False)

    def test_01_default_fixed_publication_checks_22_functions_3_classes(self):
        result = self.verify()
        wanted = set(self.pins['codec_functions']) | {'FieldSnapshot.' + key for key in self.pins['field_functions']}
        self.assertEqual(set(result['checked_functions']), wanted)
        self.assertEqual(len(result['checked_functions']), 22)
        self.assertEqual(set(result['classes']), {'CaptureError', 'CaptureCodec', 'ControlLedger'})
        self.assertEqual(result['source_revision'], 4)
        self.assertEqual(result['expected_pins_sha256'], contract.FIXED_PINS_SHA256)
        self.assertFalse(result['native_enabled'])
        self.assertFalse(result['exact'])
        self.assertFalse(result['actual_tensor_index_readback'])
        self.assertEqual(result['actual_MDP_calls'], 0)

    def test_02_identical_complete_override_only_and_fixed_tree_used(self):
        supplied = dict(reversed(list(deepcopy(self.pins).items())))
        fixed = contract._published_pins(supplied)
        self.assertIsNot(fixed, supplied)
        self.assertIsNot(fixed['codec_functions'], supplied['codec_functions'])
        self.assertTrue(contract._same_literal_tree(fixed, self.pins))
        self.assertEqual(len(self.verify(supplied)['checked_functions']), 22)
        self.assertEqual(len(self.verify(supplied)['classes']), 3)

    def test_03_all_four_keysets_empty_missing_extra_fail(self):
        for field in ('codec_constants', 'codec_classes', 'codec_functions', 'field_functions'):
            for variant in ('empty', 'missing', 'extra'):
                changed = deepcopy(self.pins)
                first = next(iter(changed[field]))
                if variant == 'empty':
                    changed[field] = {}
                elif variant == 'missing':
                    del changed[field][first]
                else:
                    changed[field]['UNPUBLISHED_EXTRA'] = deepcopy(changed[field][first])
                with self.subTest(field=field, variant=variant), self.assertRaises(ValueError):
                    self.verify(changed)
        changed = deepcopy(self.pins)
        for field in ('codec_constants', 'codec_classes', 'codec_functions', 'field_functions'):
            changed[field] = {}
        with self.assertRaises(ValueError):
            self.verify(changed)

    def test_04_full_tree_missing_extra_altered_hash_publisher_identity_fail(self):
        cases = []
        for path, value in (
            (('codec_source_sha256',), '0' * 64),
            (('codec_module',), 'different_publisher'),
            (('publisher_source_seal_sha256',), '1' * 64),
            (('publisher_final',), False),
            (('publisher_source_seal_path',), 'REPLACEMENT_SOURCE_SEAL'),
            (('codec_classes', 'CaptureCodec', 'qualname'), 'OtherClass'),
            (('codec_functions', '_need', 'module'), 'other_function_module'),
            (('field_functions', 'rows', 'source_sha256'), '2' * 64),
            (('field_class', 'module'), 'replacement_field_module'),
        ):
            changed = deepcopy(self.pins)
            node = changed
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
            cases.append((path, changed))
        missing = deepcopy(self.pins)
        del missing['codec_source_bytes']
        cases.append(('top_missing', missing))
        extra = deepcopy(self.pins)
        extra['authorization'] = True
        cases.append(('top_extra', extra))
        missing_nested = deepcopy(self.pins)
        del missing_nested['codec_functions']['_metadata']['literal_defaults']
        cases.append(('nested_missing', missing_nested))
        for label, changed in cases:
            with self.subTest(case=label), self.assertRaises(ValueError):
                self.verify(changed)

    def test_05_override_bool_int_float_aliases_fail(self):
        for path, value in (
            (('publisher_final',), 1),
            (('native_enabled',), 0),
            (('codec_source_bytes',), float(self.pins['codec_source_bytes'])),
            (('codec_classes', 'CaptureError', 'definition_line'), 17.0),
            (('codec_functions', '_metadata', 'literal_defaults'), [False]),
            (('codec_functions', '_metadata', 'literal_defaults'), [0.0]),
            (('codec_functions', 'CaptureCodec.__init__', 'literal_kwdefaults'), {'n': 80.0}),
            (('codec_constants', 'CHANNEL_WIDTHS', 'leg_pos'), 4.0),
        ):
            changed = deepcopy(self.pins)
            node = changed
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
            with self.subTest(path=path, actual_type=type(value).__name__), self.assertRaises(ValueError):
                self.verify(changed)

    def test_06_actual_published_positional_zero_defaults_reject_false_float(self):
        function = publisher._metadata
        original = function.__defaults__
        for value in (False, 0.0):
            with self.subTest(actual_type=type(value).__name__):
                with patch.object(function, '__defaults__', (value,)):
                    with self.assertRaisesRegex(ValueError, 'positional defaults'):
                        self.verify()
                self.assertIs(function.__defaults__, original)
        self.assertEqual(len(self.verify()['checked_functions']), 22)

    def test_07_actual_published_keyword_default_rejects_aliases_and_restores(self):
        function = publisher.CaptureCodec.__init__
        original = function.__kwdefaults__
        for value in (80.0, False, 0, 0.0):
            with self.subTest(actual_type=type(value).__name__, zero=(value == 0)):
                with patch.object(function, '__kwdefaults__', {'n': value}):
                    with self.assertRaisesRegex(ValueError, 'keyword defaults'):
                        self.verify()
                self.assertIs(function.__kwdefaults__, original)
        self.assertEqual(len(self.verify()['classes']), 3)

    def test_08_zero_keyword_recursive_literals_and_no_arbitrary_equality(self):
        expected = pin(__file__, __name__, 'own_zero_kwdefault')
        expected.update(literal_defaults=[], literal_kwdefaults={'zero': 0})
        original = own_zero_kwdefault.__kwdefaults__
        contract._function(own_zero_kwdefault, expected, sys.modules[__name__])
        for value in (False, 0.0):
            with self.subTest(actual_type=type(value).__name__):
                with patch.object(own_zero_kwdefault, '__kwdefaults__', {'zero': value}):
                    with self.assertRaisesRegex(ValueError, 'keyword defaults'):
                        contract._function(own_zero_kwdefault, expected, sys.modules[__name__])
                self.assertIs(own_zero_kwdefault.__kwdefaults__, original)
        baseline = {'nested': [0, {'flag': False, 'none': None, 'text': 'ok'}]}
        self.assertTrue(contract._same_literal_tree(deepcopy(baseline), baseline))
        for value in (False, 0.0):
            changed = deepcopy(baseline)
            changed['nested'][0] = value
            self.assertFalse(contract._same_literal_tree(changed, baseline))
        self.assertFalse(contract._same_literal_tree((0,), [0]))
        calls = []
        class Hostile:
            def __eq__(self, other):
                calls.append('eq')
                raise AssertionError('Arbitrary equality invoked')
            def __repr__(self):
                calls.append('repr')
                raise AssertionError('Arbitrary repr invoked')
            def __bool__(self):
                calls.append('bool')
                raise AssertionError('Arbitrary truth invoked')
        for value in (Hostile(), [], (), True):
            with self.assertRaises(ValueError):
                self.verify(value)
        with patch.object(publisher._metadata, '__defaults__', (Hostile(),)):
            with self.assertRaises(ValueError):
                self.verify()
        self.assertEqual(calls, [])

    def test_09_module_constants_exact_types_and_named_outer_tuple_only(self):
        original = publisher.CHANNEL_WIDTHS
        changed = dict(original, leg_pos=4.0)
        with patch.object(publisher, 'CHANNEL_WIDTHS', changed):
            with self.assertRaisesRegex(ValueError, 'module constant'):
                self.verify()
        self.assertIs(publisher.CHANNEL_WIDTHS, original)
        for name in ('ROLES', 'INTEGER_DTYPES'):
            original = getattr(publisher, name)
            self.assertIs(type(original), tuple)
            with patch.object(publisher, name, list(original)):
                with self.assertRaisesRegex(ValueError, 'module constant'):
                    self.verify()
            self.assertIs(getattr(publisher, name), original)
        self.assertEqual(len(self.verify()['checked_functions']), 22)

    def test_10_existing_wrapper_owner_source_checks_retained(self):
        original = publisher.CaptureCodec.capture
        @functools.wraps(original)
        def unknown_wrapper(*args, **kwargs):
            raise AssertionError('The wrapper must never execute')
        with patch.object(publisher.CaptureCodec, 'capture', unknown_wrapper):
            with self.assertRaisesRegex(ValueError, 'no unwrap skip'):
                self.verify()
        self.assertIs(publisher.CaptureCodec.capture, original)
        function = publisher._metadata
        original_code = function.__code__
        try:
            function.__code__ = original_code.replace(co_firstlineno=original_code.co_firstlineno + 1)
            with self.assertRaisesRegex(ValueError, 'Source hash/line'):
                self.verify()
        finally:
            # __code__ cannot be deleted by mock's generic descriptor cleanup.
            function.__code__ = original_code
        self.assertIs(function.__code__, original_code)
        foreign_snapshot, foreign_ledger = fixture()
        with self.assertRaisesRegex(ValueError, 'same-codec'):
            contract.verify_typed_dependency(self.snapshot, foreign_ledger)
        self.assertIsNot(foreign_snapshot.codec, self.snapshot.codec)
        self.assertEqual(len(self.verify()['checked_functions']), 22)

    def test_11_immutable_original_production_scope_and_source_only_ast(self):
        old = ROOT / 'source_phase1_passive_sensor_capture_v3'
        for name in ('passive_capture.py', 'field_snapshot.py', 'source_api.py', 'fake_tensor.py', 'CODEC_SOURCE_PINS.json'):
            self.assertEqual((HERE / name).read_bytes(), (old / name).read_bytes())
        self.assertEqual(hashlib.sha256((HERE / 'CODEC_SOURCE_PINS.json').read_bytes()).hexdigest(),
                         '5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452')
        tree = ast.parse((HERE / 'dependency_contract.py').read_text(encoding='utf-8'))
        forbidden = {'step', 'reset', 'observe', 'get_observations', 'capture', 'materialize',
                     'cpu', 'tolist', 'index_select', 'clone', 'detach', 'apply', 'rand', 'randn',
                     'random', 'getstate', 'signal', 'kill', 'Popen', 'run'}
        called = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
                  for node in ast.walk(tree) if isinstance(node, ast.Call)
                  and isinstance(node.func, (ast.Name, ast.Attribute))}
        self.assertEqual(called & forbidden, set())
        self.assertEqual(dict(FakeTensor.operations), {})
        self.assertNotIn('torch', sys.modules)
        self.assertNotIn('passive_capture', sys.modules)
        self.assertNotIn('test_passive_capture_v3', sys.modules)


if __name__ == '__main__':
    unittest.main(verbosity=2)
