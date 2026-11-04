"""Injection-only CPU experiment: own FakeEnv/Asset/Term; original full Queue/C2/typed producer.
SOURCE preparation never calls run_fixture; no native binding or SDK qualification.
"""
from pathlib import Path
import hashlib
import json
import random


def _same(a, b, torch):
    if isinstance(a, torch.Tensor):
        assert isinstance(b, torch.Tensor) and a.shape == b.shape and a.dtype == b.dtype and a.device == b.device
        assert torch.equal(a.detach().contiguous().reshape(-1).view(torch.uint8), b.detach().contiguous().reshape(-1).view(torch.uint8))
    elif type(a) is dict:
        assert type(b) is dict and set(a) == set(b)
        for key in a: _same(a[key], b[key], torch)
    elif type(a) in (list, tuple):
        assert type(a) is type(b) and len(a) == len(b)
        for x, y in zip(a, b): _same(x, y, torch)
    else: assert type(a) is type(b) and a == b


def _pairs(raw, typed, torch):
    if isinstance(raw, torch.Tensor):
        yield raw, typed
    elif type(raw) is dict:
        assert type(typed) is dict and set(raw) <= set(typed)
        for key in raw: yield from _pairs(raw[key], typed[key], torch)
    elif type(raw) in (list, tuple):
        assert type(typed) is list and len(raw) == len(typed)
        for a, b in zip(raw, typed): yield from _pairs(a, b, torch)
    else: assert type(raw) is type(typed) and raw == typed


def run_fixture(torch_module, PhysicsActionQueue, actuation_module, codec_module, observer_module, field_module):
    """Parent alone may execute later with full pinned modules in a NEW CPU namespace."""
    t, c2, cm, om = torch_module, actuation_module, codec_module, observer_module
    pins = json.loads((Path(__file__).parent / 'SOURCE_PINS.json').read_bytes())['runtime_sources']
    origins = dict(queue=PhysicsActionQueue.__init__.__code__.co_filename, actuation=c2.__file__,
                   codec=cm.__file__, observer=om.__file__, field=field_module.__file__,
                   contract=om.need.__code__.co_filename)
    for key, filename in origins.items():
        data = Path(filename).read_bytes()
        assert (len(data), hashlib.sha256(data).hexdigest()) == (pins[key]['bytes'], pins[key]['sha256'])
    assert PhysicsActionQueue.__init__.__globals__['torch'] is t
    assert PhysicsActionQueue.__init__.__globals__['PhysicsActionQueue'] is PhysicsActionQueue
    assert field_module.FieldSnapshot.__init__.__globals__['CaptureCodec'] is cm.CaptureCodec
    assert c2.install_actuation_tap.__globals__['ActuationTap'] is c2.ActuationTap
    assert c2.QUEUE_FIELDS == om.QUEUE_FIELDS and c2.GROUPS == {'legs': 4, 'wheels': 2}
    global_before = (t.get_rng_state().clone(), random.getstate())
    widths, ids = c2.GROUPS, t.tensor([78, 79], dtype=t.int64)
    codec = cm.CaptureCodec(t.Tensor, witness_index=t.arange(8, dtype=t.int64), witness_env_ids=list(range(8)), n=80)
    snapshot = field_module.FieldSnapshot(codec)

    class Asset:
        def __init__(self): self.last, self.token, self.fault = {}, object(), None
        def write(self, group, value, joint_ids):
            if self.fault is not None: raise self.fault
            self.last[group] = (value, joint_ids)
            return self.token
        def set_joint_position_target(self, value, joint_ids=None): return self.write('legs', value, joint_ids)
        def set_joint_velocity_target(self, value, joint_ids=None): return self.write('wheels', value, joint_ids)

    class Term:
        def __init__(self, env, group):
            self.env, self.group, self._asset = env, group, env.asset
            self._joint_ids, self.token = t.arange(widths[group], dtype=t.int64), object()
        def process_actions(self, command):
            self.env.queue.submit(self.group, command, self.env._sim_step_counter)
            return self.token
        def apply_actions(self):
            value = self.env.queue.apply(self.group, self.env._sim_step_counter - 1)
            writer = self._asset.set_joint_position_target if self.group == 'legs' else self._asset.set_joint_velocity_target
            return writer(value, joint_ids=self._joint_ids)

    class Env:
        def __init__(self):
            self._sim_step_counter = self._feedback_100hz_tick = self.common_step_counter = 0
            self.queue, self.asset = PhysicsActionQueue(80, 'cpu', 20261103), Asset()
            self.terms = {key: Term(self, key) for key in widths}
            self._physics_action_delay = type('OwnAdapter', (), {})()
            self._physics_action_delay.queue, self._physics_action_delay.terms = self.queue, self.terms
            for key, width in widths.items():
                self.queue.reset(key, t.arange(80), t.zeros((80, width), dtype=t.float32), new_scene_clock=True)
                self.queue.groups[key]['lag_steps'].fill_(2 if key == 'legs' else 1)
                self.queue.groups[key]['episode'].fill_(2**53 + 7)  # explicit synthetic serde stress, not a natural episode

    baseline, tapped = Env(), Env()
    def state(env):
        extra = {k: v for k, v in vars(env.queue).items() if k not in ('groups', 'rng', 'device', 'submit', 'apply')}
        return dict(extra=extra, device=str(env.queue.device), original_state=env.queue.state_dict())
    _same(state(baseline), state(tapped), t)
    tap = c2.install_actuation_tap(tapped, capacity=8192)
    retention = om.WindowRetention(codec, snapshot, 'PINNED_C2_FULL_MODULE_OWN_CPU_FIXTURE')
    retained_owned = []  # fixture verification clones, NOT producer ownership operations
    def verify_events(events, typed_events):
        assert len(events) == len(typed_events)
        for raw, typed in zip(events, typed_events):
            assert typed['tick'] == raw['tick'] and typed['raw_stored_counter'] == raw['raw_stored_counter']
            assert typed['adoption_clock']['control_slot'] == 'UNKNOWN' and 'sim_time_us' not in typed['adoption_clock']
            for value, envelope in _pairs(raw, typed, t):
                assert envelope['original_shape'] == list(value.shape) and envelope['original_dtype'] == str(value.dtype)
                assert envelope['original_device'] == str(value.device)
                if envelope.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1':
                    codec.validate_owned(envelope, allowed_roles=('QUEUE_GROUP_FULL',))
                    assert envelope['values'] is value and envelope['values'].data_ptr() == value.data_ptr()
                    assert envelope['values']._version == value._version and envelope['retained_shape'][0] == 80
                else:
                    assert envelope['values'] == 'UNKNOWN' and envelope['source_env_axis'] is None
                    assert envelope['semantic_role'] != 'ENV_IDS_FULL'
            if type(raw['group']) is str and raw['group'] in widths:
                for name in ('pre', 'post'):
                    assert set(raw[name]) == set(c2.QUEUE_FIELDS)
                    for field in c2.QUEUE_FIELDS: assert raw[name][field].shape[0] == 80
                if raw['kind'] == 'queue_submit': assert list(raw['args'][1].shape) == [80, widths[raw['group']]]
            if raw['kind'] == 'target_write' and raw['write_scope'] == 'NON_TERM_SETTER':
                assert raw['tick']['status'] == 'NOT_APPLICABLE' and typed['args'][0]['values'] == 'UNKNOWN'
            if raw['kind'] == 'target_write' and raw['write_scope'] == 'SAME_ASSET_TERM_APPLY_CONTEXT':
                assert raw['group'] in widths and raw['parent_term_apply_seq'] is not None
                assert typed['setter']['joint_ids']['values'] == 'UNKNOWN'

    try:
        for env in (baseline, tapped):
            assert env.asset.set_joint_position_target(t.zeros((80, 4)), joint_ids=ids) is env.asset.token
            assert env.asset.set_joint_velocity_target(t.zeros((80, 2)), joint_ids=ids) is env.asset.token
        for control in range(64):
            for env in (baseline, tapped):
                env.common_step_counter, env._sim_step_counter = control, control * 8
                if control == 32:  # one OWN partial reset, never a natural termination/reset claim
                    for key, width in widths.items():
                        env.queue.reset(key, ids, t.zeros((80, width), dtype=t.float32), new_scene_clock=False)
                        env.queue.groups[key]['lag_steps'][ids] = 2 if key == 'legs' else 1
                commands = {key: t.arange(80 * width, dtype=t.float32).reshape(80, width) / 1000 + control / 100 for key, width in widths.items()}
                for key in widths: assert env.terms[key].process_actions(commands[key]) is env.terms[key].token
                once = state(env)
                for key in widths: assert env.terms[key].process_actions(commands[key]) is env.terms[key].token
                _same(once, state(env), t)  # genuine same-tick submit no-op
            for tick in range(control * 8, control * 8 + 8):
                for env in (baseline, tapped):
                    env._sim_step_counter, env._feedback_100hz_tick = tick + 1, (tick + 1) // 4
                    for key in widths: assert env.terms[key].apply_actions() is env.asset.token
                _same(state(baseline), state(tapped), t)
                for key in widths: _same(baseline.asset.last[key], tapped.asset.last[key], t)
            for env in (baseline, tapped):
                once = state(env)
                for key in widths: assert env.terms[key].apply_actions() is env.asset.token
                _same(once, state(env), t)  # genuine same-tick apply no-op
            events = tap.drain()
            owned = [(v, v.clone(), v._version, list(v.shape), str(v.dtype), str(v.device)) for v, unused in _pairs(events, events, t)]
            if control in (0, 1, 62, 63): retained_owned.extend(owned)
            retention.add(control, events, clock=om.stored_clock(tapped))
            verify_events(events, retention.last[-1]['events'])
            for value, before, version, shape, dtype, device in owned:
                _same(value, before, t)
                assert (value._version, list(value.shape), str(value.dtype), str(value.device)) == (version, shape, dtype, device)
        errors = []
        for env in (baseline, tapped):
            once = state(env)
            try: env.queue.submit('legs', t.zeros((79, 4)), 512)
            except AssertionError as exc: errors.append(exc)
            else: raise AssertionError('Original Queue must reject N79 before mutation')
            _same(once, state(env), t)
        rejected = tap.drain()
        assert len(rejected) == 1 and rejected[0]['outcome'] == 'RAISED' and rejected[0]['exception_identity'] == id(errors[-1])
        try: om.typed_c2_event(rejected[0], codec, snapshot, source_ref='bad-original-shape', clock=om.stored_clock(tapped))
        except ValueError: pass
        else: raise AssertionError('Typed adoption must reject original N79 at its explicit N80 gate')
        original = next(e for e in retention.first[0]['events'] if e['kind'] == 'queue_submit')['pre']['episode']
        try: codec.validate_owned(dict(original, original_dtype='torch.float32'))
        except cm.CaptureError: pass
        else: raise AssertionError('Codec must reject changed original dtype metadata')
        for env in (baseline, tapped):
            fault = RuntimeError('OWN_ASSET_ORIGINAL_EXCEPTION')
            env.asset.fault, once = fault, state(env)
            try: env.terms['legs'].apply_actions()
            except RuntimeError as exc: assert exc is fault
            else: raise AssertionError('Original target exception must propagate unchanged')
            env.asset.fault = None
            _same(once, state(env), t)
        fault_events = tap.drain()
        assert sum(e['outcome'] == 'RAISED' for e in fault_events) == 2
        assert all(e['exception_identity'] == id(fault) for e in fault_events if e['outcome'] == 'RAISED')
        typed_fault = [om.typed_c2_event(e, codec, snapshot, source_ref='original-exception', clock=om.stored_clock(tapped)) for e in fault_events]
        verify_events(fault_events, typed_fault)
        status = tap.status()
        assert status['dropped_events'] == status['observer_errors'] == 0
    finally:
        assert tap.close()['restored'] is True
    windows = retention.report()
    assert windows['control_windows_seen'] == 64 and windows['middle_windows'] == 'UNKNOWN_UNRETAINED'
    assert [r['control_index'] for r in windows['first'] + windows['last']] == [0, 1, 62, 63]
    wire = codec.materialize(dict(windows=windows, original_exception_events=typed_fault))
    text = json.dumps(wire, allow_nan=False, sort_keys=True)
    assert json.loads(text) == wire
    for value, before, version, shape, dtype, device in retained_owned:
        _same(value, before, t)
        assert (value._version, list(value.shape), str(value.dtype), str(value.device)) == (version, shape, dtype, device)
    episode = next(e for e in wire['windows']['first'][0]['events'] if e['kind'] == 'queue_submit')['pre']['episode']['values']
    assert all(type(v) is int and v == 2**53 + 7 for v in episode)
    flags = next(e for e in wire['windows']['first'][0]['events'] if e['kind'] == 'queue_submit')['pre']['pending_valid']['values']
    assert all(type(v) is bool for v in flags)
    _same(state(baseline), state(tapped), t)
    _same(global_before, (t.get_rng_state(), random.getstate()), t)
    return dict(kind='TYPED_C2_OWN_CPU_FIXTURE_V1', n=80, controls=64, physics_ticks=512,
                fixed_lags={'legs': 2, 'wheels': 1}, own_partial_reset_ids=[78, 79], retained_controls=[0, 1, 62, 63],
                same_owned_object_data_ptr_version=True, all12_full80=True, fullstate_private_global_rng_equal=True,
                original_exception_and_shape_gates=True, serde_int64_bool_preserved=True,
                unparented_numeric_payload='UNKNOWN_INTENTIONALLY_NOT_REPRESENTED_BY_FOUR_ROLES',
                wire_bytes=len(text.encode()), wire_sha256=hashlib.sha256(text.encode()).hexdigest(),
                actual_SDK=False, native=False, DOF_pipeline='UNKNOWN', Gate1='UNKNOWN', stage2_GO=False)
