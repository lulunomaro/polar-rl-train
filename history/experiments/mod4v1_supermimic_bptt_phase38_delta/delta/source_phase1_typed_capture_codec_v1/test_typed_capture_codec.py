"""Twelve own fake-tensor / metadata / AST tests. No Torch or SDK import."""
import ast
import copy
import hashlib
import inspect
import json
from pathlib import Path
import unittest

from typed_capture_codec import CaptureCodec, CaptureError, ControlLedger, CHANNEL_WIDTHS, ROLES


class FakeTensor:
    def __init__(self, values, dtype='torch.float32', device='fake:0', log=None):
        self.data, self.dtype, self.device = values, dtype, device
        self.log = [] if log is None else log
        def shape(value):
            if type(value) is list:
                return (len(value),) + (shape(value[0]) if value else ())
            return ()
        self.shape = shape(values)

    def detach(self):
        self.log.append('detach')
        return FakeTensor(self.data, self.dtype, self.device, self.log)

    def clone(self):
        self.log.append('clone')
        return FakeTensor(copy.deepcopy(self.data), self.dtype, self.device, self.log)

    def index_select(self, axis, index):
        self.log.append('index_select')
        def select(values, depth):
            if depth == 0:
                return [copy.deepcopy(values[i]) for i in index.data]
            return [select(row, depth - 1) for row in values]
        return FakeTensor(select(self.data, axis), self.dtype, self.device, self.log)

    def cpu(self):
        self.log.append('cpu')
        return FakeTensor(self.data, self.dtype, 'cpu', self.log)

    def tolist(self):
        self.log.append('tolist')
        return copy.deepcopy(self.data)


def make_codec(device='fake:0'):
    return CaptureCodec(FakeTensor, witness_index=FakeTensor(list(range(8)), 'torch.int64', device), witness_env_ids=list(range(8)))


def clock(tick=8, phase='outside_scene_update', depth=0):
    return dict(physics_tick=tick, sim_time_us=tick * 2500, feedback_tick=tick // 4,
                common_control_counter=(tick - 1) // 8 if phase == 'scene_update' else tick // 8, phase=phase,
                control_slot='mid' if tick % 8 == 4 else 'end', reset_depth=depth,
                is_original_100hz_slot=phase == 'scene_update' and depth == 0 and tick % 4 == 0)


def capture(codec, values, role='ENV_ROWS_WITNESS', dtype='torch.float32', c=None, axis=0, group=None):
    return codec.capture(FakeTensor(values, dtype), role=role, source_ref='SYNTHETIC_SOURCE_REF_NOT_LIVE',
                         source_field='synthetic.existing.tensor', clock=clock() if c is None else c,
                         env_axis=axis, group=group)


def flags(codec, c=None):
    c = clock() if c is None else c
    values = [False] * 80
    values[79] = True
    return (capture(codec, values, 'TERMINAL_BOOL_FULL', 'torch.bool', c),
            capture(codec, [False] * 80, 'TERMINAL_BOOL_FULL', 'torch.bool', c))


def actor(codec, c=None):
    return capture(codec, [[i] * 35 for i in range(80)], c=c)


def samples(ledger, codec, offset=0):
    saved = []
    for slot, tick in (('mid', offset + 4), ('end', offset + 8)):
        c = clock(tick, 'scene_update')
        for name, width in CHANNEL_WIDTHS.items():
            clean = capture(codec, [[i] * width for i in range(80)], c=c)
            payload = {'existing_owned_clean': clean, 'used_cache': 'UNKNOWN_NOT_CAPTURED'}
            ledger.normal_sample(name, slot, clean, clock=c, payload=payload)
            saved.append((clean, payload))
    return saved


class TypedCaptureCodecTests(unittest.TestCase):
    def test_01_roles_owned_storage_and_source_metadata(self):
        codec = make_codec()
        source = FakeTensor([[i] * 3 for i in range(80)], 'torch.float16')
        env = codec.capture(source, role='ENV_ROWS_WITNESS', source_ref='S', source_field='raw', clock=clock(), env_axis=0)
        self.assertEqual(env['original_shape'], [80, 3])
        self.assertEqual(env['retained_shape'], [8, 3])
        self.assertEqual(env['original_dtype'], 'torch.float16')
        self.assertEqual(env['source_env_axis'], 0)
        self.assertEqual(env['row_mapping']['env_ids'], list(range(8)))
        self.assertEqual(env['row_mapping']['index_binding'], 'CALLER_DECLARED_INDEX_BINDING_NOT_READBACK')
        self.assertEqual(source.log, ['detach', 'index_select'])
        source.data[0][0] = -999
        self.assertEqual(env['values'].data[0][0], 0)
        full = capture(codec, list(range(80)), 'ENV_IDS_FULL', 'torch.int32', axis=None)
        self.assertEqual(full['values'].log, ['detach', 'clone'])
        self.assertEqual(len(full['values'].data), 80)
        self.assertEqual(full['row_mapping']['kind'], 'VALUES_ARE_ENV_IDS_NOT_ENV_AXIS')

    def test_02_ids_k0_k1_k79_k80_and_strict_negative_shapes(self):
        codec = make_codec()
        for k in (0, 1, 79, 80):
            value = capture(codec, list(range(k)), 'ENV_IDS_FULL', 'torch.int32', axis=None)
            self.assertEqual(value['original_shape'], [k])
            self.assertEqual(value['retained_shape'], [k])
            self.assertEqual(value['values'].data, list(range(k)))
        for values, dtype, axis in ((list(range(81)), 'torch.int32', None),
                                    ([True], 'torch.bool', None), ([1.0], 'torch.float32', None),
                                    ([[1]], 'torch.int32', None), ([1], 'torch.int32', 0)):
            with self.subTest(dtype=dtype, axis=axis, length=len(values)):
                with self.assertRaises(CaptureError):
                    capture(codec, values, 'ENV_IDS_FULL', dtype, axis=axis)

    def test_03_explicit_nonzero_env_axis_and_existing_index_device(self):
        codec = make_codec()
        result = capture(codec, [list(range(80)), list(range(80))], axis=1)
        self.assertEqual(result['original_shape'], [2, 80])
        self.assertEqual(result['retained_shape'], [2, 8])
        self.assertEqual(result['values'].data[0], list(range(8)))
        with self.assertRaises(CaptureError):
            codec.capture(FakeTensor([[0] for _ in range(80)], device='fake:1'), role='ENV_ROWS_WITNESS', source_ref='S', source_field='x', clock=clock(), env_axis=0)
        with self.assertRaises(CaptureError):
            CaptureCodec(FakeTensor, witness_index=FakeTensor([0], 'torch.int64'), witness_env_ids=[True])
        with self.assertRaises(CaptureError):
            CaptureCodec(FakeTensor, witness_index=FakeTensor([0, 0], 'torch.int64'), witness_env_ids=[0, 0])

    def test_04_materialize_preserves_dtype_large_int_bool_without_float_cast(self):
        codec = make_codec()
        large = 2 ** 60 + 7
        values = [large + i for i in range(80)]
        integer = capture(codec, values, dtype='torch.int64')
        boolean, _ = flags(codec)
        half = capture(codec, [[.125] * 3 for _ in range(80)], dtype='torch.float16')
        self.assertNotIn('cpu', integer['values'].log)
        output = codec.materialize({'integer': integer, 'bool': boolean, 'half': half})
        decoded = json.loads(json.dumps(output, allow_nan=False))
        self.assertEqual(decoded['integer']['original_dtype'], 'torch.int64')
        self.assertEqual(decoded['integer']['values'][0], large)
        self.assertIs(type(decoded['integer']['values'][0]), int)
        self.assertIs(type(decoded['bool']['values'][79]), bool)
        self.assertEqual(decoded['half']['original_dtype'], 'torch.float16')
        self.assertEqual(decoded['half']['values'][0], [.125] * 3)
        self.assertEqual(integer['values'].log.count('clone'), 0)
        self.assertEqual(integer['values'].log[-3:], ['detach', 'cpu', 'tolist'])
        with self.assertRaises(CaptureError):
            codec.materialize(FakeTensor([0]))

    def test_05_reject_unknown_roles_and_malformed_owned_envelopes(self):
        codec = make_codec()
        tensor = FakeTensor(list(range(80)))
        with self.assertRaises(CaptureError):
            codec.capture(tensor, role='AUTO_FROM_SHAPE', source_ref='S', source_field='x', clock=clock(), env_axis=0)
        self.assertEqual(tensor.log, [])
        env = capture(codec, list(range(80)))
        for key in ('row_mapping', 'source_clock', 'source_ref', 'ownership'):
            invalid = dict(env)
            invalid.pop(key)
            with self.assertRaises(CaptureError):
                codec.validate_owned(invalid)
        invalid = dict(env, retained_shape=[80])
        with self.assertRaises(CaptureError):
            codec.validate_owned(invalid)
        bad_metadata = FakeTensor(list(range(8)), 'torch.int64')
        invalid = dict(env, row_mapping={'env_ids': bad_metadata})
        with self.assertRaises(CaptureError):
            codec.validate_owned(invalid)
        self.assertEqual(bad_metadata.log, [])
        with self.assertRaises(CaptureError):
            codec.capture(tensor, role=bad_metadata, source_ref='S', source_field='x', clock=clock(), env_axis=0)
        self.assertEqual(bad_metadata.log, [])
        with self.assertRaises(CaptureError):
            capture(codec, [False] * 80, 'TERMINAL_BOOL_FULL', 'torch.int32')
        with self.assertRaises(CaptureError):
            capture(codec, [False] * 79, 'TERMINAL_BOOL_FULL', 'torch.bool')

    def test_06_atomic_complete_pack_reuses_owned_payload_no_clone(self):
        codec = make_codec()
        ledger = ControlLedger(codec, controls=64, run_id='toy')
        ledger.begin(0, clock=clock(0))
        retained = samples(ledger, codec)
        term, trunc = flags(codec)
        ids = capture(codec, [79], 'ENV_IDS_FULL', 'torch.int32', axis=None)
        old_log = list(ids['values'].log)
        ledger.pre_reset(term, trunc, clock=clock(), event_id='terminal0', payload={'same_term': term})
        ledger.reset(ids, clock=clock(), event_id='reset0', before=retained[0][1], after=retained[1][1])
        out = ledger.end(post_term=term, post_trunc=trunc, clock=clock(), actor=actor(codec))
        self.assertEqual(out['retention_status'], 'EXPECTED_FIELDS_RETAINED')
        self.assertIs(out['normal_samples']['mid']['base_ang_vel']['clean'], retained[0][0])
        self.assertIs(out['normal_samples']['mid']['base_ang_vel']['payload'], retained[0][1])
        self.assertIs(out['reset']['ids'], ids)
        self.assertIs(out['pre_reset']['term'], term)
        self.assertEqual(ids['values'].log, old_log)
        self.assertEqual(out['reset']['prior_termination_event_id'], 'terminal0')
        self.assertEqual(out['reset']['ids']['values'].data, [79])
        self.assertEqual(out['pre_reset']['term']['retained_shape'], [80])
        self.assertEqual(len(out['normal_samples']['mid']), 5)
        self.assertEqual(len(out['normal_samples']['end']), 5)
        self.assertFalse(out['event_ids_are_clock'])

    def test_07_missing_callback_is_not_empty_ids_and_missing_fields_stay_unknown(self):
        codec = make_codec()
        ledger = ControlLedger(codec, controls=64, run_id='toy')
        ledger.begin(0, clock=clock(0))
        term, trunc = flags(codec)
        out = ledger.end(post_term=term, post_trunc=trunc, clock=clock())
        self.assertEqual(out['reset']['callback_status'], 'NOT_OBSERVED')
        self.assertIsNone(out['reset']['ids'])
        self.assertNotEqual(out['reset']['ids'], [])
        self.assertEqual(out['retention_status'], 'INCOMPLETE')
        self.assertIn('MISSING_PRE_RESET_FLAGS', out['missing'])
        self.assertEqual(out['unknowns']['mid_remaining19'], 'UNKNOWN_NOT_SAMPLED_AT_MID')
        result = ledger.finish()
        self.assertFalse(result['all_controls_observed'])
        self.assertEqual(result['Gate1'], 'UNKNOWN')
        self.assertFalse(result['stage2_GO'])
        self.assertIs(result['controls'][0], out)

    def test_08_normal_duplicate_phase_clock_width_and_bounds_errors(self):
        codec = make_codec()
        ledger = ControlLedger(codec, controls=64, run_id='toy')
        ledger.begin(0, clock=clock(0))
        c = clock(4, 'scene_update')
        clean = capture(codec, [[0] * 3 for _ in range(80)], c=c)
        ledger.normal_sample('base_ang_vel', 'mid', clean, clock=c)
        with self.assertRaises(CaptureError):
            ledger.normal_sample('base_ang_vel', 'mid', clean, clock=c)
        bad_phase = clock(4, 'inside_reset', 1)
        with self.assertRaises(CaptureError):
            ledger.normal_sample('projected_gravity', 'mid', capture(codec, [[0] * 3 for _ in range(80)], c=bad_phase), clock=bad_phase)
        with self.assertRaises(CaptureError):
            ledger.normal_sample('leg_pos', 'mid', clean, clock=c)
        with self.assertRaises(CaptureError):
            ledger.begin(1, clock=clock())
        with self.assertRaises(CaptureError):
            ledger.finish()
        for count in (0, 63, 65, 129, True):
            with self.assertRaises(CaptureError):
                ControlLedger(codec, controls=count, run_id='toy')

    def test_09_reset_raised_and_out_of_order_links_not_repaired(self):
        codec = make_codec()
        ledger = ControlLedger(codec, controls=64, run_id='toy')
        ledger.begin(0, clock=clock(0))
        ids = capture(codec, list(range(80)), 'ENV_IDS_FULL', 'torch.int32', axis=None)
        ledger.reset(ids, clock=clock(), event_id='reset0', outcome='RAISED')
        term, trunc = flags(codec)
        ledger.pre_reset(term, trunc, clock=clock(), event_id='late-terminal')
        with self.assertRaises(CaptureError):
            ledger.reset(ids, clock=clock(), event_id='repeat-reset')
        out = ledger.end(post_term=term, post_trunc=trunc, clock=clock())
        self.assertIn('ORIGINAL_RESET_RAISED', out['missing'])
        self.assertIn('RESET_WITHOUT_PRIOR_RETAINED_TERMINATION', out['missing'])
        self.assertIsNone(out['reset']['prior_termination_event_id'])
        self.assertEqual(len(out['reset']['ids']['values'].data), 80)

    def test_10_queue_group_full_preserves_original_eighty_rows(self):
        codec = make_codec()
        data = [[i] * 4 for i in range(80)]
        queue = capture(codec, data, 'QUEUE_GROUP_FULL', group='legs')
        witness = capture(codec, data)
        self.assertEqual(queue['original_shape'], [80, 4])
        self.assertEqual(queue['retained_shape'], [80, 4])
        self.assertEqual(queue['values'].data[79], [79] * 4)
        self.assertEqual(queue['values'].log, ['detach', 'clone'])
        self.assertEqual(witness['retained_shape'], [8, 4])
        self.assertEqual(codec.materialize(queue)['semantic_role'], 'QUEUE_GROUP_FULL')
        for group in (None, 'same_asset_not_DOF', 'other'):
            with self.assertRaises(CaptureError):
                capture(codec, data, 'QUEUE_GROUP_FULL', group=group)
        with self.assertRaises(CaptureError):
            capture(codec, [[0] * 4 for _ in range(8)], 'QUEUE_GROUP_FULL', group='legs')

    def test_11_ast_no_target_import_extra_sampling_rng_or_inside_cpu(self):
        path = Path(__file__).with_name('typed_capture_codec.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        imports = [n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)]
        self.assertEqual(imports, ['math'])
        forbidden = {'nonzero', 'any', 'rand', 'randn', 'randint', 'getstate', 'get_state',
                     'get_rng_state', 'set_state', 'reset', 'compute_observations', 'compute_obs',
                     'clean_policy', 'state_dict', 'export_resume', 'float', 'double', 'to'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, forbidden)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, ('float', 'int', 'any', 'eval', 'exec', '__import__', 'open'))
        materializer = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'materialize')
        permitted_ids = {id(n) for n in ast.walk(materializer)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ('cpu', 'tolist'):
                self.assertIn(id(node), permitted_ids)

    def test_12_api_schema_upstream_seven_and_128_control_cap(self):
        here = Path(__file__).resolve().parent
        schema = json.loads((here / 'SCHEMA_V1.json').read_text(encoding='utf-8'))
        self.assertEqual(schema['semantic_roles'], list(ROLES))
        self.assertEqual(schema['ledger']['controls'], [64, 128])
        self.assertEqual(schema['ledger']['max_normal_channel_records'], 1280)
        self.assertEqual(schema['queue_full_rows'], 80)
        self.assertIn('env_axis', str(inspect.signature(CaptureCodec.capture)))
        pins = json.loads((here / 'SOURCE_PINS.json').read_text(encoding='utf-8'))
        upstream = pins['upstream_design']
        self.assertEqual(len(upstream['files']), 7)
        for name, row in upstream['files'].items():
            raw = (Path(upstream['directory']) / name).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (row['bytes'], row['sha256']))
        for row in pins['unchanged_source_references'].values():
            raw = Path(row['path']).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (row['bytes'], row['sha256']))
        codec = make_codec()
        ledger = ControlLedger(codec, controls=128, run_id='cap-toy-not-physics')
        term, trunc = flags(codec)
        for index in range(128):
            ledger.begin(index, clock=clock(0))
            ledger.end(post_term=term, post_trunc=trunc, clock=clock())
        with self.assertRaises(CaptureError):
            ledger.begin(128, clock=clock())
        result = ledger.finish()
        self.assertEqual(len(result['controls']), 128)
        self.assertEqual(result['recorded_controls'], 128)
        self.assertEqual(result['normal_channel_records'], 0)
        self.assertTrue(result['all_controls_observed'])
        self.assertTrue(all(p['retention_status'] == 'INCOMPLETE' for p in result['controls']))
        self.assertEqual(result['Gate1'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main(verbosity=2)
