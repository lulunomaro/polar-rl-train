"""Injection-only real Sensor/Delay + B4 CPU software fixture; never run by child.

OWN_CPU_FAKE_ENV drives synthetic original callbacks. No SDK/MRO preflight,
loader, CLI, launcher, worker or C2 consumer. Oracle comparisons/state_dict calls
are OUTSIDE tap callbacks. All normal/probe/negative denominators stay separate.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
from types import SimpleNamespace

B4_SEAL = '81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3'
B4_ROOT = '6c8cc456c752a57fd9963b919e398f3c91c0c2205c15b4d1a0dbd9b605c96107'
CODEC_SEAL = '2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219'
CODEC_ROOT = '4ceeeda60cde6f8ca6cc496b8d299e5ea3b4ff2770b707f84898f06c1b75eec8'
SENSOR_SHA = 'aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8'
DELAY_SHA = '90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665'
WIDTHS = {'base_ang_vel': 3, 'projected_gravity': 3, 'leg_pos': 4,
          'leg_vel': 4, 'wheel_vel': 2}


def _frozen(directory, seal_sha, content_root, count):
    directory = Path(directory).resolve()
    raw = (directory / 'SOURCE_SEAL.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == seal_sha
    seal = json.loads(raw)
    assert len(seal['files']) == count and seal['content_root_sha256'] == content_root
    assert hashlib.sha256(json.dumps(seal['files'], sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest() == content_root
    for name, row in seal['files'].items():
        assert Path(name).name == name
        data = (directory / name).read_bytes()
        assert (len(data), hashlib.sha256(data).hexdigest()) == (row['bytes'], row['sha256'])
    return raw


def _real_class(cls, name, expected_sha, torch_module, api):
    """Full file AND live methods; supports original runner's module aliases.

    No sys.modules registration is invented for the two original math modules.
    Their real exec_module globals/file/class binding must exist and match.
    """
    assert cls.__qualname__ == name
    namespace = cls.__init__.__globals__
    path = Path(namespace['__file__']).resolve()
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected_sha
    assert namespace.get(name) is cls and namespace.get('torch') is torch_module
    receipts = {}
    for method in ('__init__', 'apply', 'reset', 'state_dict'):
        fn = vars(cls)[method]
        assert fn.__globals__ is namespace and fn.__module__ == namespace['__name__']
        pin = api['pin'](path, cls.__module__, name + '.' + method)
        assert pin['source_sha256'] == expected_sha
        receipts[method] = api['verify_callable'](fn, pin)
    return dict(path=str(path), bytes=len(data), sha256=expected_sha,
                class_name=name, full_live_method_checks=len(receipts))


def _same(torch_module, left, right):
    if isinstance(left, torch_module.Tensor):
        return (isinstance(right, torch_module.Tensor) and left.dtype == right.dtype
                and left.shape == right.shape and left.device == right.device
                and torch_module.equal(left, right))
    if type(left) is dict:
        return (type(right) is dict and left.keys() == right.keys()
                and all(_same(torch_module, left[key], right[key]) for key in left))
    if type(left) in (list, tuple):
        return (type(left) is type(right) and len(left) == len(right)
                and all(_same(torch_module, a, b) for a, b in zip(left, right)))
    return type(left) is type(right) and left == right


def _track(original, record):
    """Explicit fixture oracle forwarding once, not a native-qualified wrapper."""
    def call(*args, **kwargs):
        record['calls'] += 1
        try:
            out = original(*args, **kwargs)
        except BaseException as error:
            record['error'] = error
            raise
        record['last'] = out
        return out
    return call


def _feedback(env, key, raw):
    env.counts['feedback'] += 1
    noisy = env._sensor_mild.apply(key, raw, env._feedback_100hz_tick)
    assert noisy is env.sensor_record['last']
    result = env._feedback_delay_mild.apply(key, noisy, env._feedback_100hz_tick)
    assert result is env.delay_record['last']
    env.last_feedback = result
    return result


class OWN_CPU_FAKE_ENV:
    """Synthetic CALLER, not an Isaac class, native clock or physical plant."""
    def __init__(self, torch_module, sensor_class, delay_class, *,
                 profile='noise_bias_mild_v1', enabled=True, reset_mode='real'):
        self.t, self.reset_mode = torch_module, reset_mode
        t = torch_module
        self.module = SimpleNamespace(feedback=_feedback)
        self._sensor_mild = sensor_class(80, 'cpu', 20261103, profile)
        self._feedback_delay_mild = delay_class(80, 'cpu', 20261103, enabled)
        self.sensor_record = dict(calls=0, last=None, error=None)
        self.delay_record = dict(calls=0, last=None, error=None)
        self._sensor_mild.apply = _track(self._sensor_mild.apply, self.sensor_record)
        self._feedback_delay_mild.apply = _track(self._feedback_delay_mild.apply, self.delay_record)
        self._sim_step_counter = self._feedback_100hz_tick = self.common_step_counter = 0
        self.counts, self.latest, self.samples = Counter(), {}, {}
        self.templates = {k: t.arange(80 * w, dtype=t.float64, device='cpu').reshape(80, w) * .001
                          for k, w in WIDTHS.items()}
        self.term = t.zeros(80, dtype=t.bool, device='cpu')
        self.trunc = t.zeros(80, dtype=t.bool, device='cpu')
        self.fake_state = t.arange(240, dtype=t.float64, device='cpu').reshape(80, 3)
        self.other19 = t.zeros((80, 19), dtype=t.float64, device='cpu')
        self.scene_token, self.reset_token = object(), object()
        self.reset_error = RuntimeError('OWN_CPU_FAKE_ENV controlled partial-reset failure')
        self.last_return = self.last_reset_ids = self.last_reset_return = None
        self.scene = SimpleNamespace(update=self.original_scene_update)
        self.bridge = SimpleNamespace(pre=None, real=self)
        self.termination_manager = SimpleNamespace(compute=self.original_terminal_capture)
        # Explicit fixture initialization, BEFORE tap. Neither observer nor verifier resets.
        self._reset_idx(t.arange(80, dtype=t.int32, device='cpu'))

    def original_scene_update(self, dt):
        assert dt == .0025
        self.counts['scene_update'] += 1
        tick = self._sim_step_counter
        if tick % 4 == 0:
            self._feedback_100hz_tick = tick // 4
            slot = 'mid' if tick % 8 == 4 else 'end'
            values = {}
            for key in WIDTHS:
                raw = self.templates[key] + tick * .01
                out = self.module.feedback(self, key, raw)
                assert out is self.last_feedback
                values[key] = dict(raw=raw, noisy=self.sensor_record['last'], out=out)
                self.latest[key] = out
            self.samples[slot] = values
        return self.scene_token

    def original_terminal_capture(self):
        self.counts['terminal'] += 1
        self.counts['synthetic_bridge_capture'] += 1
        self.bridge.pre = dict(s1=self.fake_state, term=self.term.clone(), trunc=self.trunc.clone())
        return self.term

    def _reset_idx(self, ids):
        self.counts['reset'] += 1
        self.last_reset_ids = ids
        if self.reset_mode != 'metadata_only_fake_return':
            self.counts['real_sensor_reset'] += 1
            self._sensor_mild.reset(ids)
            if self.reset_mode == 'raise_after_real_sensor':
                raise self.reset_error
            self.counts['real_delay_reset'] += 1
            self._feedback_delay_mild.reset(ids)
        else:
            self.counts['metadata_only_fake_reset'] += 1
        self.last_reset_return = self.reset_token
        return self.reset_token

    def step(self, control_index, *, reset_rows=None, reset_dtype=None, ticks=8):
        self.counts['step'] += 1
        self.samples = {}
        for _ in range(ticks):
            self._sim_step_counter += 1
            assert self.scene.update(.0025) is self.scene_token
        self.common_step_counter += 1
        self.term.zero_()
        self.trunc.zero_()
        if control_index == 37:
            self.term[79] = True
            self.trunc[78] = True
        elif reset_rows:
            self.term[reset_rows] = True
        assert self.termination_manager.compute() is self.term
        if reset_rows is not None:
            ids = self.t.tensor(reset_rows, dtype=self.t.int32 if reset_dtype is None else reset_dtype,
                                device='cpu')
            assert self._reset_idx(ids) is self.reset_token
        # FAKE original actor: existing END16 plus explicit synthetic19, no feedback call.
        self.counts['synthetic_actor35'] += 1
        actor = self.t.cat([self.latest[k] for k in WIDTHS] + [self.other19], dim=1)
        self.last_return = (actor, self.term, self.trunc)
        return self.last_return

    def evidence(self):
        """OUTSIDE callbacks, using original complete software state snapshots."""
        return dict(sensor=self._sensor_mild.state_dict(), delay=self._feedback_delay_mild.state_dict(),
                    counts=dict(self.counts), sensor_calls=self.sensor_record['calls'],
                    delay_calls=self.delay_record['calls'], samples=self.samples,
                    clocks=(self._sim_step_counter, self._feedback_100hz_tick, self.common_step_counter))


def _bindings(env):
    return (env._sensor_mild.apply, env._feedback_delay_mild.apply, env.module.feedback,
            env.scene.update, env.termination_manager.compute, env._reset_idx)


def _binding_identity(value):
    return (id(getattr(value, '__self__', None)), id(getattr(value, '__func__', value)))


def run_fixture(torch_module, real_sensor_class, real_delay_class, *, codec_module,
                passive_module, field_module, dependency_module):
    """Parent injects complete reviewed modules/classes; no loading or output I/O.

    Must run with assertions enabled. Only the FIXED typed dependency verifier is
    executed; original SDK/MRO binding preflight is deliberately NOT executed.
    """
    assert __debug__
    t, c, p, f, d = torch_module, codec_module, passive_module, field_module, dependency_module
    b4_dir, codec_dir = Path(p.__file__).resolve().parent, Path(c.__file__).resolve().parent
    assert Path(f.__file__).resolve().parent == Path(d.__file__).resolve().parent == b4_dir
    api = p.verify_callable.__globals__
    assert Path(api['__file__']).resolve().parent == b4_dir
    before_b4 = _frozen(b4_dir, B4_SEAL, B4_ROOT, 21)
    before_codec = _frozen(codec_dir, CODEC_SEAL, CODEC_ROOT, 7)
    rng_before, python_before = t.get_rng_state().clone(), random.getstate()
    assert p.FieldSnapshot is f.FieldSnapshot and f.CaptureCodec is c.CaptureCodec
    assert d.FieldSnapshot is f.FieldSnapshot and p.CHANNELS == c.CHANNEL_WIDTHS == WIDTHS
    originals = dict(sensor=_real_class(real_sensor_class, 'SensorCorruption', SENSOR_SHA, t, api),
                     delay=_real_class(real_delay_class, 'FeedbackDelay', DELAY_SHA, t, api))
    index = t.arange(8, dtype=t.int64, device='cpu')
    index_before = index.clone()  # Explicit oracle baseline, not observer work.
    own_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    source_refs = {name: 'OWN_CPU_FAKE_ENV@sha256:' + own_sha + '::' + name
                   for name in ('feedback', 'bridge', 'reset')}
    source_refs.update(sensor='ORIGINAL_SOURCE@sha256:' + SENSOR_SHA + '::SensorCorruption.apply',
                       delay='ORIGINAL_SOURCE@sha256:' + DELAY_SHA + '::FeedbackDelay.apply')
    checks, opened, dependency_checks = {}, [], []

    def pair(label, *, profile='noise_bias_mild_v1', enabled=True):
        a = OWN_CPU_FAKE_ENV(t, real_sensor_class, real_delay_class, profile=profile, enabled=enabled)
        b = OWN_CPU_FAKE_ENV(t, real_sensor_class, real_delay_class, profile=profile, enabled=enabled)
        codec = c.CaptureCodec(t.Tensor, witness_index=index, witness_env_ids=tuple(range(8)), n=80)
        ledger = c.ControlLedger(codec, controls=64, run_id='OWN_CPU_FAKE_ENV:' + label)
        snapshot = f.FieldSnapshot(codec)
        # REAL fixed default verifier, before any capture assignment. No pin override.
        dependency = d.verify_typed_dependency(snapshot, ledger)
        assert len(dependency['checked_functions']) == 22 and len(dependency['classes']) == 3
        assert dependency['expected_pins_sha256'] == '5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452'
        dependency_checks.append(dict(label=label, functions=22, codec_classes=3, field_class_also_checked=True))
        inspection = dict(kind='OWN_CPU_FAKE_ENV_SOFTWARE_ONLY', native_enabled=False, exact=False,
                          native_binding_preflight_executed=False, typed_codec_binding=dependency)
        old = tuple(map(_binding_identity, _bindings(b)))
        tap = p.PassiveCapture(b, b.bridge, b.module, p.BoundedRecorder(first=2, last=2, max_events=10000),
                               snapshot, inspection, ledger=ledger, source_refs=source_refs).attach()
        assert len(tap._patches) == 6
        opened.append((b, tap, old))
        return a, b, codec, tap

    def parity(a, b):
        assert _same(t, a.evidence(), b.evidence())
        assert a.last_return is None or a.last_return is not b.last_return

    def close_one(b, tap):
        expected = next(old for env, current, old in opened if env is b and current is tap)
        tap.close()
        assert not tap._patches and tap.closed
        assert tuple(map(_binding_identity, _bindings(b))) == expected

    try:
        a, b, codec, tap = pair('main64')
        reset_schedule = {0: [], 20: [79], 37: [78, 79], 40: list(range(79)), 50: list(range(80))}
        owned_records = 0
        for control in range(64):
            assert tap.begin_control(control) is True
            rows = reset_schedule.get(control)
            left = a.step(control, reset_rows=rows)
            right = b.step(control, reset_rows=rows)
            assert left is a.last_return and right is b.last_return and _same(t, left, right)
            pack = tap.end_control(post_term=right[1], post_trunc=right[2],
                                   source_ref=source_refs['bridge'], actor35=right[0])
            assert type(pack) is dict and pack['retention_status'] == 'EXPECTED_FIELDS_RETAINED'
            assert _same(t, pack['post_return']['actor35_original_buffer']['values'], right[0].index_select(0, index))
            assert pack['pre_reset']['term']['original_shape'] == [80]
            assert pack['pre_reset']['term']['original_dtype'] == 'torch.bool'
            for boundary in (pack['pre_reset'], pack['post_return']):
                for flag, original in (('term', right[1]), ('trunc', right[2])):
                    assert boundary[flag]['retained_shape'] == [80]
                    assert boundary[flag]['original_dtype'] == 'torch.bool'
                    assert _same(t, boundary[flag]['values'], original)
                    assert boundary[flag]['values'].data_ptr() != original.data_ptr()
            if rows is None:
                assert pack['reset']['callback_status'] == 'NOT_OBSERVED' and pack['reset']['ids'] is None
            else:
                ids = pack['reset']['ids']
                assert ids['semantic_role'] == 'ENV_IDS_FULL' and ids['original_dtype'] == 'torch.int32'
                assert ids['original_shape'] == ids['retained_shape'] == [len(rows)]
                assert t.equal(ids['values'], b.last_reset_ids)
                assert pack['reset']['prior_termination_event_id'] == pack['pre_reset']['event_id']
            for slot in ('mid', 'end'):
                for key in WIDTHS:
                    entry, actual = pack['normal_samples'][slot][key], b.samples[slot][key]
                    payload = entry['payload']
                    for envelope, source in ((entry['clean'], actual['raw']),
                            (payload['sensor_stage']['actual_noisy_return'], actual['noisy']),
                            (payload['delay_stage']['actual_return'], actual['out'])):
                        assert envelope['original_shape'] == list(source.shape)
                        assert envelope['original_dtype'] == str(source.dtype) == 'torch.float64'
                        assert envelope['row_mapping']['env_ids'] == list(range(8))
                        assert envelope['row_mapping']['index_binding'] == 'CALLER_DECLARED_INDEX_BINDING_NOT_READBACK'
                        assert _same(t, envelope['values'], source.index_select(0, index))
                        assert envelope['values'].data_ptr() != source.data_ptr()
                    owned_records += 1
            parity(a, b)
        main_report = tap.finish()
        main = main_report['control_ledger']
        assert main['recorded_controls'] == 64 and main['normal_channel_records'] == owned_records == 640
        assert main_report['metadata_retention_complete'] and tap.recorder.capture_errors == 0
        assert tap.calls == dict(feedback=640, sensor_apply=640, delay_apply=640,
                                 scene_update=512, terminal_boundary=64, reset_boundary=5)
        assert a.sensor_record['calls'] == b.sensor_record['calls'] == 640
        assert a.delay_record['calls'] == b.delay_record['calls'] == 640
        assert main['controls'][37]['pre_reset']['term']['values'][79] and main['controls'][37]['pre_reset']['trunc']['values'][78]
        assert main['controls'][37]['reset']['ids']['original_shape'] == [2]
        # Stop all hooks BEFORE any CPU/list/JSON export; six original bindings restored.
        close_one(b, tap)
        exported = codec.materialize(main_report)
        wire = json.loads(json.dumps(exported, allow_nan=False))
        assert wire['control_ledger']['controls'][37]['reset']['ids']['values'] == [78, 79]
        precision = t.arange(80, dtype=t.int64, device='cpu').reshape(80, 1) + (2**60 + 7)
        envelope = f.FieldSnapshot(codec).rows(precision, source_ref=source_refs['bridge'],
                    source_field='OWN_CPU_PRECISION_PROBE_NOT_SENSOR', clock=main['controls'][0]['begin_clock'])
        precision_wire = json.loads(json.dumps(codec.materialize(envelope), allow_nan=False))
        assert precision_wire['original_dtype'] == 'torch.int64' and precision_wire['values'][0][0] == 2**60 + 7
        checks['main64'] = dict(controls=64, normal_channel_records=640, physics_callbacks=512,
            original_sensor_apply_calls_per_path=640, original_delay_apply_calls_per_path=640,
            output_and_owned_snapshot_parity=True, full_ID_K_cases=[0, 1, 2, 79, 80], full_masks_80=True,
            actor35='SYNTHETIC_ORIGINAL_FAKE_RETURN_NOT_NATIVE', metadata_errors=0,
            outside_export_after_restore=True, native_int64_precision=True)

        # Separate IDLE probe: none of these original calls is a normal scene sample.
        a, b, _, probe = pair('idle_cache_partialreset')
        assert probe.begin_control(0) is True
        draws = []
        for ordinal, tick in enumerate((1, 2, 2, 2, 3)):
            for env in (a, b):
                env._sim_step_counter, env._feedback_100hz_tick = tick * 4, tick
            if ordinal == 3:
                for env in (a, b):
                    assert env.termination_manager.compute() is env.term
                    assert env._reset_idx(t.tensor([78, 79], dtype=t.int32, device='cpu')) is env.reset_token
            before = dict(b._sensor_mild.draw_counts)
            outputs = []
            for key in WIDTHS:
                raw = a.templates[key] + ordinal
                left = a.module.feedback(a, key, raw)
                right = b.module.feedback(b, key, raw)
                assert _same(t, left, right) and right is b.delay_record['last']
                outputs.append(right)
            if ordinal == 1:
                previous = outputs
            if ordinal == 2:
                assert _same(t, previous, outputs) and before == b._sensor_mild.draw_counts
            if ordinal == 3:
                assert all(b._sensor_mild.draw_counts[k] - before[k] == 2 for k in WIDTHS)
                for cache in b._feedback_delay_mild.cache.values():
                    assert t.equal(cache['sample_tick'][[78, 79]], t.full((2,), tick, dtype=t.int64, device='cpu'))
                    assert t.equal(cache['ready'][[78, 79]], t.zeros(2, dtype=t.bool, device='cpu'))
            parity(a, b)
            draws.append(dict(b._sensor_mild.draw_counts))
        assert probe.ledger._open['normal_samples'] == dict(mid={}, end={})
        assert probe.recorder.capture_errors == 0 and b.sensor_record['calls'] == b.delay_record['calls'] == 25
        checks['idle_probe'] = dict(real_channel_calls_per_path=25, normal_channel_records=0,
            same_tick_changed_raw_cache_hit=True, partial_reset_same_tick_two_fresh_rows=True,
            original_warmup_cache_checked=True, complete_private_states_equal=True,
            unfinished_control='EXPECTED_INCOMPLETE_NO_FAKE_END_OR_FINISH')
        close_one(b, probe)

        # Original disabled classes must return the exact input through all tap layers.
        a, b, _, off = pair('off_identity', profile='off', enabled=False)
        raw = t.zeros((80, 3), dtype=t.float64, device='cpu')
        assert a.module.feedback(a, 'base_ang_vel', raw) is raw
        assert b.module.feedback(b, 'base_ang_vel', raw) is raw
        parity(a, b)
        assert off.recorder.capture_errors == 0
        checks['off_identity'] = dict(real_calls_per_path=1, original_input_return_identity=True)
        close_one(b, off)

        # Real original apply exceptions must survive every passive layer by identity.
        a, b, _, invalid = pair('real_original_apply_exceptions')
        invalid_raw = t.zeros((80, 1), dtype=t.float64, device='cpu')
        for env in (a, b):
            before_sensor = env._sensor_mild.state_dict()
            try:
                env.module.feedback(env, 'UNKNOWN', invalid_raw)
            except AssertionError as error:
                assert error is env.sensor_record['error']
            else:
                raise AssertionError('real original Sensor validation disappeared')
            assert _same(t, before_sensor, env._sensor_mild.state_dict())
            for tick in (1, 3):
                env._feedback_100hz_tick = tick
                env._sim_step_counter = tick * 4
                try:
                    env.module.feedback(env, 'base_ang_vel', env.templates['base_ang_vel'])
                except AssertionError as error:
                    assert tick == 3 and error is env.delay_record['error']
                else:
                    assert tick == 1
        parity(a, b)
        assert invalid.recorder.capture_errors == 0
        checks['real_original_apply_exceptions'] = dict(sensor_error_identity=True,
            delay_skipped_clock_error_identity=True, original_partial_states_equal=True,
            sensor_attempts_per_path=3, delay_attempts_per_path=2, normal_channel_records=0)
        close_one(b, invalid)

        # Synthetic original ENV reset raises AFTER the real sensor reset. No fake end.
        a, b, _, raised = pair('raised_partial_original_reset')
        a.reset_mode = b.reset_mode = 'raise_after_real_sensor'
        assert raised.begin_control(0) is True
        for env in (a, b):
            try:
                env.step(0, reset_rows=[79])
            except RuntimeError as error:
                assert error is env.reset_error
            else:
                raise AssertionError('controlled original reset exception disappeared')
        parity(a, b)
        pending = raised.report()['incomplete_current_control']
        assert pending['retention_status'] == 'INCOMPLETE' and pending['original_post_return'] == 'NOT_OBSERVED'
        partial = pending['owned_partial_control']['reset_callback']
        assert partial['outcome'] == 'RAISED' and partial['after'] != 'UNKNOWN'
        assert raised.ledger._open['reset']['outcome'] == 'RAISED'
        assert raised.recorder.capture_errors == 0 and raised.ledger._open['post_return'] is None
        checks['raised_reset'] = dict(original_ENV_exception_identity=True, real_sensor_partial_state_equal=True,
            real_delay_reset_not_called_on_raised_path=True, pending_incomplete=True,
            end_called=False, finish_called=False, exception_origin='OWN_CPU_FAKE_ENV_AFTER_REAL_SENSOR_RESET')
        close_one(b, raised)

        # Metadata-only negative: NO claim that real Sensor/Delay accept malformed IDs.
        a, b, _, bad = pair('bad_ID_metadata_fake_original_return')
        a.reset_mode = b.reset_mode = 'metadata_only_fake_return'
        assert bad.begin_control(0) is True
        left = a.step(0, reset_rows=[79], reset_dtype=t.float32)
        right = b.step(0, reset_rows=[79], reset_dtype=t.float32)
        assert _same(t, left, right) and b.last_reset_return is b.reset_token
        pack = bad.end_control(post_term=right[1], post_trunc=right[2],
                               source_ref=source_refs['bridge'], actor35=right[0])
        summary = pack['b3_callback_provenance']
        assert summary['original_reset_callbacks'] == 1 and summary['reset_observation'] == 'OBSERVED_METADATA_FAILED'
        assert pack['retention_status'] == 'INCOMPLETE' and 'B3_OBSERVED_RESET_NOT_EXACTLY_RETAINED' in pack['missing']
        assert bad.recorder.capture_errors > 0
        parity(a, b)
        checks['bad_ID_metadata'] = dict(original_callback_observed=True, classified='OBSERVED_METADATA_FAILED',
            real_class_malformed_ID_reset_executed=False, fake_original_return_identity=True,
            pending_or_closed_incomplete=True, observer_errors_expected=True)
        close_one(b, bad)

        # Truncated synthetic caller returns after MID; observer must NOT invent END.
        a, b, _, missing = pair('missing_END_truncated_caller')
        assert missing.begin_control(0) is True
        left, right = a.step(0, ticks=4), b.step(0, ticks=4)
        assert _same(t, left, right)
        pack = missing.end_control(post_term=right[1], post_trunc=right[2],
                                   source_ref=source_refs['bridge'], actor35=right[0])
        assert pack['normal_samples']['end'] == {} and pack['retention_status'] == 'INCOMPLETE'
        assert all('MISSING_NORMAL:end:' + key in pack['missing'] for key in WIDTHS)
        assert missing.recorder.capture_errors == 0
        parity(a, b)
        checks['missing_END'] = dict(synthetic_physics_ticks=4, retained_mid_channels=5,
                                    retained_end_channels=0, no_fabricated_END=True)
        close_one(b, missing)
        assert t.equal(index, index_before)
        assert t.equal(rng_before, t.get_rng_state()) and python_before == random.getstate()
        result = dict(kind='B4_REAL_SENSOR_DELAY_TYPED_TAP_CPU_SOFTWARE_FIXTURE_V1', status='PASS',
            N=80, checks=checks, dependency_verifier_runs=dependency_checks,
            original_complete_source_bindings=originals, source_seals_unchanged=True,
            Torch_CPU_and_Python_global_RNG_unchanged=True, private_generators_queue_cache_parity=True,
            witness_mapping=dict(declared=list(range(8)), codec_claim='CALLER_DECLARED_INDEX_BINDING_NOT_READBACK',
                                 fixture_CPU_index_unchanged=True),
            actual_real_Tensor_and_original_Sensor_Delay=True, native_binding_preflight_executed=False,
            SDK_PhysX_DR_readback_executed=False, natural_clock_or_reset_evidence=False,
            native_actor35_equality=False, clean35_MID=None, C2_enabled=False,
            exact=False, Gate1='UNKNOWN', stage2_GO=False)
    finally:
        for env, tap, old in reversed(opened):
            tap.close()
            assert tuple(map(_binding_identity, _bindings(env))) == old
        assert _frozen(b4_dir, B4_SEAL, B4_ROOT, 21) == before_b4
        assert _frozen(codec_dir, CODEC_SEAL, CODEC_ROOT, 7) == before_codec
    return result
