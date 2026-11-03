"""Own stdlib/API/AST tests only. NO Torch/SDK/native/numerical claim."""
import ast
from collections import Counter
from copy import deepcopy
import hashlib
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
CODEC_DIR = HERE.parent / 'source_phase1_typed_capture_codec_v1'
sys.path.insert(0, str(CODEC_DIR))
sys.path.insert(0, str(HERE))

from typed_capture_codec import CaptureCodec, ControlLedger, CaptureError
from field_snapshot import FieldSnapshot, tensor_snapshot_adapter
from fake_tensor import FakeTensor
from fake_typed_runtime import TypedEnv, TypedBridge, plain
import fake_runtime as original_fake
from passive_capture import PassiveCapture, BoundedRecorder, UNKNOWN


SOURCE_REFS = {name: 'OWN_FAKE_SOURCE_ONLY:' + name
               for name in ('feedback', 'sensor', 'delay', 'bridge', 'reset')}
POST_REF = 'OWN_FAKE_ORIGINAL_STEP_RETURN_NOT_SDK'


def clock(tick=4, feedback=1, phase='scene_update'):
    return dict(physics_tick=tick, feedback_tick=feedback, common_control_counter=0,
                phase=phase, reset_depth=0, is_original_100hz_slot=phase == 'scene_update',
                control_slot='mid' if tick % 8 == 4 else 'end')


def attach_fixture(env=None, first=1, last=1, max_events=3, controls=64):
    env = TypedEnv() if env is None else env
    bridge = TypedBridge(env)
    # Existing synthetic index created by the fake caller, never by the tap.
    index = FakeTensor(list(range(8)), 'torch.int64')
    snapshot = tensor_snapshot_adapter(FakeTensor, index, 80, witness_env_ids=tuple(range(8)))
    ledger = ControlLedger(snapshot.codec, controls=controls, run_id='OWN_FAKE_ONLY')
    recorder = BoundedRecorder(first=first, last=last, max_events=max_events)
    tap = PassiveCapture(env, bridge, original_fake, recorder, snapshot,
                         dict(source_only=True, native_preflight='BYPASSED_ONLY_IN_OWN_FAKE'),
                         ledger=ledger, source_refs=SOURCE_REFS).attach()
    return env, bridge, tap


def drive(tap, index, terminal_ids=(), trunc_ids=(), force_empty=False, actor=True):
    tap.begin_control(index)
    result = tap.env.step([.1 * index, -.2, .3, -.4, .5, -.6], terminal_ids, trunc_ids, force_empty)
    assert result is tap.env.last_step_return
    pack = tap.end_control(post_term=result[2], post_trunc=result[3],
                           source_ref=POST_REF, actor35=result[0] if actor else None)
    return result, pack


class ExplicitFieldTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = tensor_snapshot_adapter(FakeTensor, FakeTensor(list(range(8)), 'torch.int64'),
                                                80, witness_env_ids=tuple(range(8)))

    def test_full_ID_K0_1_79_80_original_int32_never_witness_selected(self):
        for k in (0, 1, 79, 80):
            with self.subTest(k=k):
                original = FakeTensor(list(range(k)), 'torch.int32')
                before = FakeTensor.operations['index_select']
                owned = self.snapshot.ids(original, source_ref='OWN_FAKE', source_field='entry.ids', clock=clock())
                self.assertEqual(owned['original_shape'], [k])
                self.assertEqual(owned['retained_shape'], [k])
                self.assertEqual(owned['original_dtype'], 'torch.int32')
                self.assertIsNone(owned['source_env_axis'])
                self.assertEqual(owned['values'].values, list(range(k)))
                self.assertIsNot(owned['values'], original)
                self.assertEqual(FakeTensor.operations['index_select'], before)
                if k:
                    original[0] = 79
                    self.assertEqual(owned['values'][0], 0)

    def test_witness_and_full_bool80_have_separate_explicit_semantics(self):
        rows = FakeTensor([[i, i + 1] for i in range(80)], 'torch.float32')
        owned = self.snapshot.rows(rows, source_ref='OWN_FAKE', source_field='rows', clock=clock())
        self.assertEqual(owned['original_shape'], [80, 2])
        self.assertEqual(owned['retained_shape'], [8, 2])
        self.assertEqual(owned['row_mapping']['env_ids'], list(range(8)))
        self.assertEqual(owned['row_mapping']['index_binding'], 'CALLER_DECLARED_INDEX_BINDING_NOT_READBACK')
        term = FakeTensor([False] * 79 + [True], 'torch.bool')
        full = self.snapshot.mask(term, source_ref='OWN_FAKE', source_field='term', clock=clock())
        self.assertEqual(full['original_shape'], full['retained_shape'])
        self.assertEqual(full['retained_shape'], [80])
        self.assertIs(full['values'][79], True)
        self.assertEqual(full['values'].values[:8], [False] * 8)
        self.assertEqual(full['original_dtype'], 'torch.bool')

    def test_original_ID_dtype_is_not_assumed_long_and_bad_semantics_fail(self):
        for dtype in ('torch.int16', 'torch.int32', 'torch.int64'):
            value = FakeTensor([79], dtype)
            owned = self.snapshot.ids(value, source_ref='OWN_FAKE', source_field='ids', clock=clock())
            self.assertEqual(owned['original_dtype'], dtype)
            self.assertEqual(owned['values'].dtype, dtype)
        with self.assertRaises(CaptureError):
            self.snapshot.ids(FakeTensor([79.], 'torch.float32'), source_ref='OWN_FAKE', source_field='ids', clock=clock())
        with self.assertRaises(CaptureError):
            self.snapshot.mask(FakeTensor([False] * 8, 'torch.bool'), source_ref='OWN_FAKE', source_field='term', clock=clock())
        with self.assertRaises(TypeError):
            tensor_snapshot_adapter(FakeTensor, FakeTensor(list(range(8)), 'torch.int64'), 80)
        with self.assertRaises(CaptureError):
            ControlLedger(self.snapshot.codec, controls=256, run_id='OWN_FAKE')


class PassiveRetentionTests(unittest.TestCase):
    def tearDown(self):
        if getattr(self, 'tap', None) is not None:
            self.tap.close()

    def fixture(self, *args, **kwargs):
        env, bridge, self.tap = attach_fixture(*args, **kwargs)
        return env, bridge, self.tap

    def test_nonwitness79_terminal_and78_truncation_preserve_full_flags_and_IDs(self):
        env, bridge, tap = self.fixture()
        original, pack = drive(tap, 0, terminal_ids=(79,), trunc_ids=(78,))
        self.assertEqual(pack['pre_reset']['term']['retained_shape'], [80])
        self.assertTrue(pack['pre_reset']['term']['values'][79])
        self.assertTrue(pack['pre_reset']['trunc']['values'][78])
        self.assertEqual(pack['reset']['ids']['values'].values, [78, 79])
        self.assertEqual(pack['reset']['ids']['original_dtype'], 'torch.int32')
        self.assertEqual(env.last_reset_ids.dtype, 'torch.int32')
        self.assertEqual(pack['pre_reset']['payload']['state']['retained_shape'], [8, 3])
        self.assertEqual(pack['pre_reset']['payload']['state']['values'][0][1], 0)
        self.assertEqual(pack['reset']['before']['sensor_episode']['values'].values, [0] * 8)
        self.assertEqual(pack['reset']['after']['sensor_episode']['values'].values, [0] * 8)
        self.assertEqual(bridge.pack_calls, 1)
        self.assertEqual(env.counts['observe'], 1)
        self.assertIs(original[0], env.last_step_return[0])

    def test_K80_K79_callback_IDS_and_partial_state_are_owned_at_original_boundary(self):
        env, _, tap = self.fixture()
        _, first = drive(tap, 0, terminal_ids=tuple(range(80)))
        _, second = drive(tap, 1, terminal_ids=tuple(range(79)))
        for k, pack in ((80, first), (79, second)):
            self.assertEqual(pack['reset']['ids']['original_shape'], [k])
            self.assertEqual(pack['reset']['ids']['retained_shape'], [k])
            self.assertEqual(pack['reset']['ids']['values'].values, list(range(k)))
            self.assertEqual(pack['reset']['ids']['original_dtype'], 'torch.int32')
        self.assertEqual(first['reset']['before']['sensor_episode']['values'].values, [0] * 8)
        self.assertEqual(first['reset']['after']['sensor_episode']['values'].values, [1] * 8)
        self.assertEqual(second['reset']['after']['sensor_episode']['values'].values, [2] * 8)
        for cache in first['reset']['after']['queue'].values():
            self.assertEqual(cache['sample_tick']['values'].values, [-1] * 8)
        self.assertNotEqual(env._feedback_delay_mild.cache['base_ang_vel']['sample_tick'].values[:8], [-1] * 8)
        self.assertEqual(first['reset']['ids']['values'].values, list(range(80)))
        self.assertEqual(first['reset']['after']['sensor_episode']['source_clock']['phase'], 'inside_reset')
        self.assertEqual(first['reset']['after']['sensor_episode']['source_clock']['reset_depth'], 1)

    def test_NOT_OBSERVED_is_not_observed_empty_ID_argument(self):
        env, _, tap = self.fixture()
        _, absent = drive(tap, 0)
        _, empty = drive(tap, 1, force_empty=True)
        self.assertEqual(absent['reset']['callback_status'], 'NOT_OBSERVED')
        self.assertIsNone(absent['reset']['ids'])
        self.assertEqual(empty['reset']['callback_status'], 'OBSERVED')
        self.assertEqual(empty['reset']['ids']['original_shape'], [0])
        self.assertEqual(empty['reset']['ids']['values'].values, [])
        self.assertEqual(env.counts['reset'], 1)

    def test_all_normal_MID_END_channel_records_survive_disabled_debug_rings(self):
        env, _, tap = self.fixture(first=0, last=0, max_events=1)
        for index in range(5):
            _, pack = drive(tap, index, terminal_ids=(1,) if index == 2 else ())
            for slot, offset in (('mid', 4), ('end', 8)):
                self.assertEqual(set(pack['normal_samples'][slot]), set(original_fake.CHANNELS))
                for channel, sample in pack['normal_samples'][slot].items():
                    width = original_fake.CHANNELS[channel]
                    self.assertEqual(sample['clean']['original_shape'], [80, width])
                    self.assertEqual(sample['clean']['retained_shape'], [8, width])
                    self.assertEqual(sample['clock']['physics_tick'], index * 8 + offset)
                    self.assertEqual(sample['clock']['sim_time_us'], (index * 8 + offset) * 2500)
                    self.assertEqual(sample['clock']['reset_depth'], 0)
                    self.assertEqual(sample['payload']['full_clean35'], 'UNKNOWN_NOT_COMPUTED')
                    self.assertEqual(sample['payload']['sensor_stage']['noise_used']['source_field'], 'sensor.cache.noise_used')
                    self.assertEqual(sample['payload']['delay_stage']['selection_origin'],
                                     'original cache.sample_tick/out, not replayed delay logic')
        report = tap.finish()
        self.assertEqual(report['control_ledger']['normal_channel_records'], 50)
        self.assertEqual(report['bounded_debug_not_complete_sampling']['captured'], 0)
        self.assertEqual(report['original_wrapper_call_counts']['feedback'], 75)
        self.assertEqual(env.counts['raw_getter'], 75)
        self.assertEqual(env.counts['observe'], 5)

    def test_baseline_actor_queue_private_global_RNG_and_callcounts_identical(self):
        baseline, baseline_bridge = TypedEnv(), None
        baseline_bridge = TypedBridge(baseline)
        env, bridge, tap = self.fixture(first=0, last=0, max_events=1)
        for index in range(6):
            ids = (79,) if index == 1 else (0, 7) if index == 3 else tuple(range(80)) if index == 4 else ()
            action = [.1 * index, -.2, .3, -.4, .5, -.6]
            before = random.getstate()
            expected = baseline.step(action, ids)
            self.assertEqual(random.getstate(), before)
            original, _ = drive(tap, index, terminal_ids=ids)
            self.assertEqual(random.getstate(), before)
            self.assertEqual(plain(expected), plain(original))
            self.assertEqual(plain(baseline.evidence()), plain(env.evidence()))
            self.assertEqual(baseline_bridge.pack_calls, bridge.pack_calls)
            self.assertEqual(baseline_bridge.capture_calls, bridge.capture_calls)
        self.assertEqual(env.counts['step'], 6)
        self.assertEqual(env.counts['raw_getter'], 90)
        self.assertEqual(env._sensor_mild.calls['apply'], 90)
        self.assertEqual(env._feedback_delay_mild.calls['apply'], 90)
        self.assertEqual(env.counts['observe'], 6)
        self.assertEqual(tap.calls['scene_update'], 48)
        self.assertEqual(tap.calls['terminal_boundary'], 6)

    def test_same_tick_noise_cache_and_original_feedback_return_identity(self):
        env, _, tap = self.fixture(first=2, last=2, max_events=8)
        raw = env.original_raw_getter('leg_pos')
        first = original_fake.feedback(env, 'leg_pos', raw)
        self.assertIs(first, env._feedback_delay_mild.last_return)
        before = env._sensor_mild.rng['leg_pos'].getstate()
        draws = env._sensor_mild.draw_counts['leg_pos']
        second = original_fake.feedback(env, 'leg_pos', raw)
        self.assertIs(second, env._feedback_delay_mild.last_return)
        self.assertEqual(env._sensor_mild.rng['leg_pos'].getstate(), before)
        self.assertEqual(env._sensor_mild.draw_counts['leg_pos'], draws)
        self.assertEqual(tap.recorder.capture_errors, 0)
        self.assertIsNone(tap._active)

    def test_original_sensor_delay_term_reset_return_identity_and_entry_argument(self):
        env, _, tap = self.fixture()
        tap.begin_control(0)
        raw = env.original_raw_getter('leg_pos')
        out = env._sensor_mild.apply('leg_pos', raw, 0)
        self.assertIs(out, env._sensor_mild.last_return)
        delayed = env._feedback_delay_mild.apply('leg_pos', out, 0)
        self.assertIs(delayed, env._feedback_delay_mild.last_return)
        terminal = env.termination_manager.compute()
        self.assertIs(terminal, env.termination_manager.terminated)
        ids = FakeTensor(list(range(80)), 'torch.int32')
        env.reset_return = object()
        reset = env._reset_idx(ids)
        self.assertIs(reset, env.reset_return)
        self.assertIs(env.last_reset_ids, ids)
        self.assertEqual(ids.dtype, 'torch.int32')
        self.assertEqual(env.counts['reset'], 1)
        self.assertIsNone(tap._active)

    def test_observer_failures_preserve_original_reset_exception_identity(self):
        env = TypedEnv()
        sentinel = RuntimeError('OWN_ORIGINAL_EXCEPTION_SENTINEL')
        calls = []
        def original_reset(*args, **kwargs):
            calls.append((args, kwargs))
            raise sentinel
        env._reset_idx = original_reset
        env, _, tap = self.fixture(env)
        tap.begin_control(0)
        def failed_capture(*args, **kwargs):
            raise CaptureError('OWN_CODEC_FAILURE')
        tap.snapshot.codec.capture = failed_capture
        ids = FakeTensor([79], 'torch.int32')
        with self.assertRaises(RuntimeError) as observed:
            env._reset_idx(ids)
        self.assertIs(observed.exception, sentinel)
        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0][0][0], ids)
        self.assertEqual(tap._reset_depth, 0)
        self.assertEqual(tap._phase, 'outside_scene_update')
        self.assertGreater(tap.recorder.capture_errors, 0)

    def test_observer_failure_does_not_replace_original_success_return(self):
        env, _, tap = self.fixture()
        tap.begin_control(0)
        env.reset_return = object()
        def failed_capture(*args, **kwargs):
            raise CaptureError('OWN_CODEC_FAILURE')
        tap.snapshot.codec.capture = failed_capture
        self.assertIs(env._reset_idx(FakeTensor([79], 'torch.int32')), env.reset_return)
        self.assertEqual(env.counts['reset'], 1)
        self.assertEqual(tap._reset_depth, 0)

    def test_atomic_middle_boundary_survives_64_controls_and_tiny_debug_rings(self):
        env, _, tap = self.fixture(first=1, last=1, max_events=2)
        FakeTensor.operations.clear()
        for index in range(64):
            drive(tap, index, terminal_ids=(79,) if index == 37 else tuple(range(80)) if index == 60 else ())
        self.assertEqual(FakeTensor.operations['cpu'], 0)
        self.assertEqual(FakeTensor.operations['tolist'], 0)
        report = tap.finish()
        ledger = report['control_ledger']
        self.assertEqual(ledger['recorded_controls'], 64)
        self.assertEqual(ledger['normal_channel_records'], 640)
        self.assertEqual(ledger['controls'][37]['reset']['ids']['values'].values, [79])
        self.assertTrue(ledger['controls'][37]['pre_reset']['term']['values'][79])
        self.assertEqual(len(ledger['controls'][60]['reset']['ids']['values']), 80)
        self.assertEqual(ledger['controls'][36]['reset']['callback_status'], 'NOT_OBSERVED')
        self.assertTrue(report['metadata_retention_complete'])
        self.assertFalse(report['native_enabled'])
        self.assertFalse(report['exact'])
        self.assertEqual(report['untapped_bitwise_actor35'], 'UNKNOWN')
        self.assertEqual(report['bounded_debug_not_complete_sampling']['retained_bound'], 2)
        exported = tap.snapshot.codec.materialize(report)
        self.assertEqual(exported['control_ledger']['controls'][37]['reset']['ids']['values'], [79])
        self.assertEqual(exported['control_ledger']['controls'][37]['reset']['ids']['original_dtype'], 'torch.int32')
        self.assertGreater(FakeTensor.operations['cpu'], 0)
        self.assertGreater(FakeTensor.operations['tolist'], 0)
        self.assertEqual(env.counts['step'], 64)
        self.assertEqual(env.counts['raw_getter'], 960)

    def test_missing_actor_remains_unknown_and_bad_shape_is_observer_error(self):
        env, _, tap = self.fixture()
        _, pack = drive(tap, 0, actor=False)
        self.assertEqual(pack['retention_status'], 'INCOMPLETE')
        self.assertIn('ACTOR35_NOT_PROVIDED', pack['missing'])
        self.assertEqual(pack['post_return']['actor35_original_buffer'], 'UNKNOWN_NOT_CAPTURED')
        tap.begin_control(1)
        original = env.step([0.] * 6)
        out = tap.end_control(post_term=original[2], post_trunc=original[3], source_ref=POST_REF,
                              actor35=FakeTensor([[0.] * 34 for _ in range(80)]))
        self.assertEqual(out, UNKNOWN)
        self.assertIs(original, env.last_step_return)
        self.assertEqual(env.counts['step'], 2)
        self.assertEqual(env.counts['observe'], 2)
        self.assertGreater(tap.recorder.capture_errors, 0)
        pending = tap.report()['incomplete_current_control']
        self.assertEqual(pending['original_post_return'], 'CALLER_SUPPLIED_BUFFERS_END_NOT_CLOSED')
        self.assertEqual(pending['owned_partial_control']['post_return_callback']['term']['retained_shape'], [80])
        self.assertEqual(pending['owned_partial_control']['post_return_callback']['actor35_original_buffer']['retained_shape'], [8, 34])

    def test_missing_original_sampling_is_incomplete_without_replay(self):
        env = TypedEnv()
        env.scene.update = env.original_scene_update
        env, _, tap = self.fixture(env)
        _, pack = drive(tap, 0)
        self.assertEqual(pack['retention_status'], 'INCOMPLETE')
        self.assertEqual(len([x for x in pack['missing'] if x.startswith('MISSING_NORMAL:')]), 10)
        self.assertEqual(env.counts['raw_getter'], 5)
        self.assertEqual(env.counts['observe'], 1)


class OriginalFailureAndPendingTests(unittest.TestCase):
    tearDown = PassiveRetentionTests.tearDown
    fixture = PassiveRetentionTests.fixture

    def test_original_reset_RAISED_retains_full_owned_pending_control_without_post_return(self):
        env = TypedEnv()
        original = env._reset_idx
        sentinel = RuntimeError('OWN_ORIGINAL_AFTER_PARTIAL_RESET')
        def original_reset_then_raise(ids):
            original(ids)
            raise sentinel
        env._reset_idx = original_reset_then_raise
        env, bridge, tap = self.fixture(env, first=0, last=0, max_events=1)
        FakeTensor.operations.clear()
        tap.begin_control(0)
        with self.assertRaises(RuntimeError) as observed:
            env.step([0.] * 6, terminal_ids=tuple(range(80)))
        self.assertIs(observed.exception, sentinel)
        report = tap.report()
        pending = report['incomplete_current_control']
        self.assertEqual(pending['retention_status'], 'INCOMPLETE')
        self.assertEqual(pending['original_post_return'], 'NOT_OBSERVED')
        own = pending['owned_partial_control']
        self.assertIsNone(own['post_return_callback'])
        self.assertEqual([len(own['normal_samples'][slot]) for slot in ('mid', 'end')], [5, 5])
        reset = own['reset_callback']
        self.assertEqual(reset['outcome'], 'RAISED')
        self.assertEqual(reset['ids']['original_dtype'], 'torch.int32')
        self.assertEqual(reset['ids']['retained_shape'], [80])
        self.assertEqual(reset['ids']['values'].values, list(range(80)))
        self.assertEqual(reset['before']['sensor_episode']['values'].values, [0] * 8)
        self.assertEqual(reset['after']['sensor_episode']['values'].values, [1] * 8)
        self.assertTrue(own['terminal_callback']['retained']['term']['values'][79])
        self.assertEqual(pending['provenance']['original_reset_callbacks'], 1)
        self.assertEqual(env.counts['reset'], 1)
        self.assertEqual(env.counts['step'], 1)
        self.assertEqual(env.counts['observe'], 0)
        self.assertEqual(bridge.pack_calls, 1)
        self.assertEqual(tap._reset_depth, 0)
        self.assertEqual(tap._phase, 'outside_scene_update')
        self.assertIsNone(tap._active)
        self.assertEqual(FakeTensor.operations['cpu'], 0)
        self.assertEqual(FakeTensor.operations['tolist'], 0)
        self.assertFalse(report['metadata_retention_complete'])
        exported = tap.snapshot.codec.materialize(report)
        self.assertEqual(exported['incomplete_current_control']['owned_partial_control']['reset_callback']['ids']['values'][-1], 79)

    def test_observed_ID_capture_failure_is_not_natural_no_callback(self):
        env, _, tap = self.fixture(first=0, last=0, max_events=1)
        with patch.object(tap.snapshot, 'ids', side_effect=CaptureError('OWN_IDS_CAPTURE_FAILURE')):
            original, pack = drive(tap, 0, terminal_ids=(79,))
        self.assertIs(original, env.last_step_return)
        self.assertEqual(env.counts['reset'], 1)
        summary = pack['b3_callback_provenance']
        self.assertEqual(summary['original_reset_callbacks'], 1)
        self.assertEqual(summary['reset_observation'], 'OBSERVED_METADATA_FAILED')
        self.assertEqual(pack['reset']['callback_status'], 'NOT_OBSERVED')
        self.assertIsNone(pack['reset']['ids'])
        self.assertEqual(pack['retention_status'], 'INCOMPLETE')
        self.assertIn('B3_OBSERVED_RESET_NOT_EXACTLY_RETAINED', pack['missing'])
        self.assertIn('B3_OBSERVER_METADATA_ERRORS', pack['missing'])
        self.assertIsNone(tap.report()['incomplete_current_control'])

    def test_duplicate_actual_callback_is_forwarded_once_each_and_marked_incomplete(self):
        env, _, tap = self.fixture()
        tap.begin_control(0)
        original = env.step([0.] * 6, terminal_ids=(79,))
        # Deliberate OWN FAKE extra source call, never an adapter repair/replay.
        env._reset_idx(FakeTensor([78], 'torch.int32'))
        pack = tap.end_control(post_term=original[2], post_trunc=original[3], source_ref=POST_REF, actor35=original[0])
        self.assertEqual(env.counts['reset'], 2)
        self.assertEqual(pack['b3_callback_provenance']['original_reset_callbacks'], 2)
        self.assertEqual(pack['reset']['ids']['values'].values, [79])
        self.assertEqual(pack['retention_status'], 'INCOMPLETE')
        self.assertIn('B3_OBSERVED_RESET_NOT_EXACTLY_RETAINED', pack['missing'])

    def test_five_other_original_exceptions_are_identical_once_and_cleanup_restores_phase(self):
        class OddOriginal(RuntimeError):
            def __str__(self):
                raise ValueError('OWN_EXCEPTION_STRING_METADATA_FAILURE')
        for kind in ('feedback', 'sensor', 'delay', 'scene', 'terminal'):
            with self.subTest(kind=kind):
                env = TypedEnv()
                sentinel = OddOriginal()
                calls = []
                def original_raises(*args, **kwargs):
                    calls.append((args, kwargs))
                    raise sentinel
                owner, name = {'feedback': (original_fake, 'feedback'),
                               'sensor': (env._sensor_mild, 'apply'),
                               'delay': (env._feedback_delay_mild, 'apply'),
                               'scene': (env.scene, 'update'),
                               'terminal': (env.termination_manager, 'compute')}[kind]
                with patch.object(owner, name, original_raises):
                    env, _, tap = self.fixture(env)
                    try:
                        raw = FakeTensor([[.25] * 4 for _ in range(80)])
                        actions = {'feedback': lambda: original_fake.feedback(env, 'leg_pos', raw),
                                   'sensor': lambda: env._sensor_mild.apply('leg_pos', raw, 0),
                                   'delay': lambda: env._feedback_delay_mild.apply('leg_pos', raw, 0),
                                   'scene': lambda: env.scene.update(.0025),
                                   'terminal': lambda: env.termination_manager.compute()}
                        with self.assertRaises(OddOriginal) as observed:
                            actions[kind]()
                        self.assertIs(observed.exception, sentinel)
                        self.assertEqual(len(calls), 1)
                        self.assertEqual(tap._phase, 'outside_scene_update')
                        self.assertEqual(tap._reset_depth, 0)
                        self.assertIsNone(tap._active)
                    finally:
                        tap.close()
                        self.tap = None

    def test_128_controls_keep_1280_samples_without_debug_and_no_129th_control(self):
        env, _, tap = self.fixture(first=0, last=0, max_events=1, controls=128)
        for index in range(128):
            drive(tap, index, terminal_ids=tuple(range(79)) if index == 27 else tuple(range(80)) if index == 102 else ())
        report = tap.finish()
        ledger = report['control_ledger']
        self.assertEqual(ledger['recorded_controls'], 128)
        self.assertEqual(ledger['normal_channel_records'], 1280)
        self.assertEqual(ledger['controls'][27]['reset']['ids']['retained_shape'], [79])
        self.assertEqual(ledger['controls'][102]['reset']['ids']['retained_shape'], [80])
        self.assertTrue(report['metadata_retention_complete'])
        self.assertIsNone(report['incomplete_current_control'])
        self.assertEqual(report['bounded_debug_not_complete_sampling']['retained_bound'], 0)
        self.assertEqual(env.counts['step'], 128)
        self.assertEqual(env.counts['observe'], 128)
        self.assertEqual(env.counts['raw_getter'], 1920)
        self.assertEqual(tap.begin_control(128), UNKNOWN)
        self.assertEqual(env.counts['step'], 128)
        self.assertEqual(len(ledger['controls']), 128)

    def test_scene_original_return_and_forwarded_arguments_are_identity_preserved(self):
        env = TypedEnv()
        sentinel = object()
        calls = []
        def original_update(*args, **kwargs):
            calls.append((args, kwargs))
            return sentinel
        env.scene.update = original_update
        env, _, tap = self.fixture(env)
        self.assertIs(env.scene.update(.0025, own_flag=True), sentinel)
        self.assertEqual(calls, [((.0025,), dict(own_flag=True))])
        self.assertEqual(tap._phase, 'outside_scene_update')


class DependencyBindingTests(unittest.TestCase):
    def setUp(self):
        from dependency_contract import verify_typed_dependency
        import typed_capture_codec as codec_module
        self.verify = verify_typed_dependency
        self.module = codec_module
        self.snapshot = tensor_snapshot_adapter(FakeTensor, FakeTensor(list(range(8)), 'torch.int64'),
                                                80, witness_env_ids=tuple(range(8)))
        self.ledger = ControlLedger(self.snapshot.codec, controls=64, run_id='OWN_API_FAKE')
        # Final SOURCE pins must exist; an unsealed provisional codec is not bound here.
        import json
        self.pins = json.loads((HERE / 'CODEC_SOURCE_PINS.json').read_text(encoding='utf-8'))

    def test_final_source_dependency_owner_module_code_defaults_and_no_readback(self):
        FakeTensor.operations.clear()
        result = self.verify(self.snapshot, self.ledger)
        self.assertTrue(result['publisher_final'])
        self.assertEqual(result['codec_source_sha256'], self.pins['codec_source_sha256'])
        self.assertEqual(result['actual_MDP_calls'], 0)
        self.assertFalse(result['actual_tensor_index_readback'])
        self.assertEqual(FakeTensor.operations['cpu'], 0)
        self.assertEqual(FakeTensor.operations['tolist'], 0)
        self.assertFalse(result['native_enabled'])
        self.assertFalse(result['exact'])

    def test_stale_SHA_line_and_unfinal_pins_fail_closed(self):
        for field in ('sha', 'line', 'final'):
            with self.subTest(field=field):
                pins = deepcopy(self.pins)
                if field == 'sha':
                    pins['codec_source_sha256'] = '0' * 64
                elif field == 'line':
                    pins['codec_functions']['CaptureCodec.capture']['code_firstlineno'] += 1
                else:
                    pins['publisher_final'] = False
                with self.assertRaises(ValueError):
                    self.verify(self.snapshot, self.ledger, dependency_pins=pins)

    def test_unknown_wrapped_method_is_not_unwrapped_and_admitted(self):
        from functools import wraps
        original = self.snapshot.codec.capture
        @wraps(original)
        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)
        self.snapshot.codec.capture = wrapper
        with self.assertRaises(ValueError):
            self.verify(self.snapshot, self.ledger)

    def test_changed_kwdefaults_constants_and_explicit_field_binding_fail(self):
        fn = self.module.CaptureCodec.capture
        with patch.object(fn, '__kwdefaults__', dict(fn.__kwdefaults__, group='legs')):
            with self.assertRaises(ValueError):
                self.verify(self.snapshot, self.ledger)
        with patch.object(self.module, 'CHANNEL_WIDTHS', dict(self.module.CHANNEL_WIDTHS, wheel_vel=3)):
            with self.assertRaises(ValueError):
                self.verify(self.snapshot, self.ledger)
        self.snapshot.ids = lambda *args, **kwargs: None
        with self.assertRaises(ValueError):
            self.verify(self.snapshot, self.ledger)

    def test_foreign_codec_used_ledger_and_invalid_declared_rows_fail(self):
        other = tensor_snapshot_adapter(FakeTensor, FakeTensor(list(range(8)), 'torch.int64'),
                                        80, witness_env_ids=tuple(range(8)))
        foreign = ControlLedger(other.codec, controls=64, run_id='OWN_API_OTHER')
        with self.assertRaises(ValueError):
            self.verify(self.snapshot, foreign)
        self.ledger.begin(0, clock=clock())
        with self.assertRaises(ValueError):
            self.verify(self.snapshot, self.ledger)
        fresh = ControlLedger(self.snapshot.codec, controls=64, run_id='OWN_API_FRESH')
        self.snapshot.codec.witness_env_ids = (79, 80)
        with self.assertRaises(ValueError):
            self.verify(self.snapshot, fresh)

    def test_bad_dependency_precedes_original_preflight_and_all_assignments(self):
        from passive_capture import install_passive_capture
        env = TypedEnv()
        bridge = TypedBridge(env)
        original_scene, original_reset = env.scene.update, env._reset_idx
        pins = deepcopy(self.pins)
        pins['codec_source_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            install_passive_capture(env, bridge, original_fake, {}, {}, snapshot=self.snapshot,
                                    ledger=self.ledger, dependency_pins=pins)
        self.assertIs(env.scene.update, original_scene)
        self.assertIs(env._reset_idx.__func__, original_reset.__func__)
        self.assertEqual(dict(env.counts), {})
        self.assertEqual(bridge.pack_calls, 0)
        self.assertEqual(bridge.capture_calls, 0)
        self.assertEqual(self.ledger._packs, [])
        self.assertIsNone(self.ledger._open)


class ASTScopeTests(unittest.TestCase):
    def test_B2_strict_reset_source_api_and_existing_preflight_are_unchanged(self):
        old_dir = HERE.parent / 'source_phase1_passive_sensor_capture_v2'
        self.assertEqual((HERE / 'source_api.py').read_bytes(), (old_dir / 'source_api.py').read_bytes())
        self.assertEqual(hashlib.sha256((HERE / 'source_api.py').read_bytes()).hexdigest(),
                         'a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62')
        old = ast.parse((old_dir / 'passive_capture.py').read_text(encoding='utf-8'))
        new = ast.parse((HERE / 'passive_capture.py').read_text(encoding='utf-8'))
        def nodes(tree):
            return {n.name: ast.dump(n, include_attributes=False) for n in tree.body
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        a, b = nodes(old), nodes(new)
        for name in ('stdlib_snapshot', 'BoundedRecorder', '_same_callable', '_plain_scale',
                     '_root_asset_configuration', 'preflight', '_preflight_impl'):
            self.assertEqual(a[name], b[name], name)
        for name in ('_clock', '_patch', 'close'):
            cls_old = next(n for n in old.body if isinstance(n, ast.ClassDef) and n.name == 'PassiveCapture')
            cls_new = next(n for n in new.body if isinstance(n, ast.ClassDef) and n.name == 'PassiveCapture')
            ao = next(n for n in cls_old.body if isinstance(n, ast.FunctionDef) and n.name == name)
            bn = next(n for n in cls_new.body if isinstance(n, ast.FunctionDef) and n.name == name)
            self.assertEqual(ast.dump(ao, include_attributes=False), ast.dump(bn, include_attributes=False), name)

    def test_original_call_sites_and_forwarding_counts_are_fixed(self):
        tree = ast.parse((HERE / 'passive_capture.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PassiveCapture')
        attach = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'attach')
        originals = [n for n in ast.walk(attach) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Name) and n.func.id.startswith('original_')]
        self.assertEqual(Counter(n.func.id for n in originals),
                         Counter(original_feedback=2, original_sensor=1, original_delay=1,
                                 original_update=1, original_term=1, original_reset=1))
        for call in originals:
            wanted = 'env, key, raw' if call.func.id == 'original_feedback' else '*args, **kwargs'
            self.assertEqual(ast.unparse(call), call.func.id + '(' + wanted + ')')
        forbidden = {'step', 'observe', 'pack', 'context', 'compute', 'nonzero', 'any',
                     'rand', 'randn', 'randint', 'normal', 'arange', 'getstate', 'get_rng_state',
                     'cpu', 'tolist', 'to', 'long', 'bool', 'sum', 'write_text', 'open'}
        for node in ast.walk(attach):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, forbidden, ast.unparse(node))
        for name in ('begin_control', 'end_control', '_delay_state', '_boundary_state'):
            method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
            for node in ast.walk(method):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, forbidden, ast.unparse(node))

    def test_snapshot_roles_are_explicit_not_shape_inference(self):
        tree = ast.parse((HERE / 'field_snapshot.py').read_text(encoding='utf-8'))
        captures = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute) and node.func.attr == 'capture']
        self.assertEqual(len(captures), 3)
        roles = {next(k.value.value for k in call.keywords if k.arg == 'role') for call in captures}
        self.assertEqual(roles, {'ENV_ROWS_WITNESS', 'ENV_IDS_FULL', 'TERMINAL_BOOL_FULL'})
        attrs = [node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)]
        self.assertNotIn('shape', attrs)
        self.assertNotIn('nonzero', attrs)
        self.assertNotIn('any', attrs)
        self.assertNotIn('QUEUE_GROUP_FULL', (HERE / 'field_snapshot.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
