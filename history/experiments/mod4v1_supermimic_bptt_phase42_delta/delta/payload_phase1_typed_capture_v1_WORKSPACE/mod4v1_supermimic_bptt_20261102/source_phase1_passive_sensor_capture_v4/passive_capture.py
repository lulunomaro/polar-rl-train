"""V3 typed passive observer of ORIGINAL feedback calls; no Torch/SDK import.

No step/reset/observation/SDK getter is called by this module. install() only
wraps already-bound functions after preflight. The wrapped original is called
once with the original arguments; its exact return object or exception survives.
This is a SOURCE component, not native admission or an exactness receipt.
"""
from __future__ import annotations
from collections import Counter, deque
import inspect
import json
from pathlib import Path
import sys
from source_api import (CHANNELS, SCALES, verify_callable, verify_class, closure_functions, sha,
                        verify_existing_reset_chain, diagnose_preflight_bindings)

from field_snapshot import FieldSnapshot, tensor_snapshot_adapter

UNKNOWN = 'UNKNOWN'


def stdlib_snapshot(value):
    """Strict fake/stdlib copier. Unsupported live objects are never retained."""
    if value is None or type(value) in (bool, int, float, str, bytes):
        return value
    if type(value) is dict:
        return {k: stdlib_snapshot(v) for k, v in value.items()}
    if type(value) in (list, tuple):
        return type(value)(stdlib_snapshot(v) for v in value)
    if type(value) is slice:
        return {'slice': [value.start, value.stop, value.step]}
    raise TypeError('Snapshot adapter required for ' + type(value).__name__)




class BoundedRecorder:
    """O(1) amortized per event; bounded first/last plus scalar counters.

    max_events limits payload capture, not the plant or its clocks. Later calls
    pass through and increment counts only. There is no per-tick filesystem I/O,
    process signalling, timers, raw JSONL, or accumulated-history rewrite.
    """
    def __init__(self, first=2, last=2, max_events=256):
        if not (0 <= first <= 32 and 0 <= last <= 32 and 1 <= max_events <= 100000):
            raise ValueError('Recorder bounds invalid')
        self.first_limit, self.last_limit, self.max_events = first, last, max_events
        self.first, self.last = [], deque(maxlen=last)
        self.counts = Counter()
        self.seen = self.captured = self.capture_errors = 0
        self.first_error = self.last_error = None
        self._pending = 0

    def begin(self, kind):
        self.seen += 1
        self.counts[kind] += 1
        # Reservation counts nested/boundary events toward the same hard cap.
        if self.captured + self._pending >= self.max_events:
            return None
        if not (self.first_limit or self.last_limit):
            return None
        self._pending += 1
        return (self.seen, kind)

    def commit(self, ticket, payload):
        if ticket is None:
            return
        self._pending -= 1
        event = dict(sequence=ticket[0], kind=ticket[1], payload=payload)
        self.captured += 1
        if len(self.first) < self.first_limit:
            self.first.append(event)
        if self.last_limit:
            self.last.append(event)

    def capture_error(self, error):
        self.capture_errors += 1
        entry = dict(type=type(error).__name__, message=str(error)[:320])
        if self.first_error is None:
            self.first_error = entry
        self.last_error = entry

    def report(self):
        return dict(kind='BOUNDED_PASSIVE_CAPTURE_V1', native_enabled=False, exact=False,
                    count=self.seen, count_by_kind=dict(self.counts), captured=self.captured,
                    payload_capture_cap=self.max_events,
                    capture_exhausted=self.captured >= self.max_events,
                    retained_first=list(self.first), retained_last=list(self.last),
                    retained_bound=self.first_limit + self.last_limit,
                    capture_errors=self.capture_errors, first_error=self.first_error,
                    last_error=self.last_error)

    def write_stdlib_report(self, path):
        """Explicit one-shot fake/stdlib report only; never called on every tick."""
        path = Path(path).resolve()
        here = Path(__file__).resolve().parent
        if not path.is_relative_to(here) or path.suffix != '.json':
            raise ValueError('Report path must be NEW-directory JSON')
        if path.exists():
            raise FileExistsError(path)
        path.write_text(json.dumps(self.report(), indent=2, allow_nan=False), encoding='utf-8')


def _same_callable(a, b):
    if inspect.ismethod(a) and inspect.ismethod(b):
        return a.__self__ is b.__self__ and a.__func__ is b.__func__
    return a is b


def _plain_scale(value):
    if type(value) in (int, float):
        return float(value)
    # Configuration-only preflight conversion; never a sensor/physics getter.
    if type(value).__module__.startswith('torch'):
        return value.detach().cpu().tolist()
    raise ValueError('Unknown term scale representation')


def _root_asset_configuration(term):
    """Validate mutable defaults and explicit parameters, not merely their IDs."""
    defaults = term.func.__defaults__ or ()
    if len(defaults) != 1 or getattr(defaults[0], 'name', None) != 'robot':
        raise ValueError('Original root observation default asset must be robot')
    if set(term.params) - {'asset_cfg'}:
        raise ValueError('Unexpected root observation parameters')
    actual = term.params.get('asset_cfg', defaults[0])
    if getattr(actual, 'name', None) != 'robot':
        raise ValueError('Actual root observation asset must be robot')
    return dict(default_asset_name=defaults[0].name, actual_asset_name=actual.name,
                default_asset_identity=id(defaults[0]), actual_asset_identity=id(actual),
                explicit_asset_override='asset_cfg' in term.params)


def preflight(env, bridge, module, role_api, bridge_pin):
    """Same public API; attach bounded metadata to fail-closed pre-install errors."""
    try:
        return _preflight_impl(env, bridge, module, role_api, bridge_pin)
    except (AttributeError, KeyError, TypeError, ValueError, OSError) as error:
        diagnostic = diagnose_preflight_bindings(env, bridge, module, role_api, bridge_pin)
        error.binding_diagnostic = diagnostic
        # Keep ValueError/AttributeError category and include observed data in traces.
        if error.args:
            error.args = (str(error.args[0]) + '; binding_diagnostic=' +
                          json.dumps(diagnostic, separators=(',', ':'), ensure_ascii=False),) + error.args[1:]
        raise


def _preflight_impl(env, bridge, module, role_api, bridge_pin):
    """Fail closed before any assignment; does not call task functions."""
    pins = role_api['pins']
    required = ('_sensor_mild', '_feedback_delay_mild', '_sim_step_counter',
                '_feedback_100hz_tick', 'common_step_counter', '_physics_handles_decimation')
    if any(name not in vars(env) for name in required):
        raise ValueError('Require already-initialized original environment')
    if env.physics_dt != .0025 or env.step_dt != .02 or env.cfg.decimation != 8 or env._physics_handles_decimation:
        raise ValueError('Require 400Hz physics callbacks and 50Hz control, not backend decimation')
    sensor, delay = vars(env)['_sensor_mild'], vars(env)['_feedback_delay_mild']
    actual_mro = type(env).__mro__
    expected_mro = role_api['env_mro_local']
    if len(actual_mro) < len(expected_mro):
        raise ValueError('Active environment MRO too short')
    classes = [verify_class(c, p) for c, p in zip(actual_mro, expected_mro)]
    identities = dict(sensor_class=verify_class(type(sensor), pins['sensor_class']),
                      delay_class=verify_class(type(delay), pins['delay_class']))
    for label, value in (('sensor_apply', sensor.apply), ('sensor_reset', sensor.reset),
                         ('delay_apply', delay.apply), ('delay_reset', delay.reset),
                         ('feedback', module.feedback)):
        identities[label] = verify_callable(value, pins[label])
    # Both proofs are mandatory: actual installed chain AND original class descriptor.
    identities['env_reset'] = verify_existing_reset_chain(env, role_api['reset_chain'])
    if sys.modules.get(module.__name__) is not module:
        raise ValueError('Feedback module is not actual sys.modules binding')
    if module.feedback.__globals__ is not module.__dict__:
        raise ValueError('Feedback function global module mismatch')
    # Original helper aliases must still resolve to the pinned, already-bound components.
    if module.__dict__.get('sensor_state') is None or module.__dict__.get('delay_state') is None:
        raise ValueError('Missing original sensor/delay helpers')
    helper = module.sensor_state
    if not inspect.isfunction(helper) or helper.__module__ != 'sensor_a0_runtime':
        raise ValueError('Unexpected sensor state helper')
    helper_module = sys.modules.get(helper.__module__)
    if helper_module is None or helper.__globals__ is not helper_module.__dict__:
        raise ValueError('Sensor helper module identity mismatch')
    # Manifest pins were fixed before installation; never pin a changed file on demand.
    identities['sensor_state'] = verify_callable(helper, pins['sensor_state'])
    identities['delay_state'] = verify_callable(module.delay_state, pins['delay_state'])
    if helper.__globals__.get('SensorCorruption') is not type(sensor):
        raise ValueError('Sensor helper resolves another class')
    if module.__dict__.get('FeedbackDelay') is not type(delay):
        raise ValueError('Delay helper resolves another class')
    task = module.__dict__.get('task')
    if task is None or sys.modules.get('mod4_task') is not task:
        raise ValueError('Actual task module binding differs')
    if sha(task.__file__) != role_api['task_source']['source_sha256']:
        raise ValueError('Actual task module source hash changed')
    sdk = vars(task).get('mdp_obs')
    if sdk is None or sys.modules.get('isaaclab.envs.mdp.observations') is not sdk:
        raise ValueError('Actual SDK observation module differs')
    for name, expected in role_api['sdk_observation_pins'].items():
        identities['sdk_' + name] = verify_callable(vars(sdk)[name], expected)
    term_for = {'base_ang_vel': 'base_ang_vel', 'projected_gravity': 'projected_gravity',
                'leg_pos': 'leg_pos', 'leg_vel': 'joint_vel', 'wheel_vel': 'joint_vel'}
    manager = env.observation_manager
    names = list(manager.active_terms['policy'])
    cfgs = manager._group_obs_term_cfgs['policy']
    term_receipts = {}
    for key, label in term_for.items():
        if names.count(key) != 1:
            raise ValueError('Missing/duplicate active feedback term: ' + key)
        term = cfgs[names.index(key)]
        identities['term_' + key] = verify_callable(term.func, pins[label])
        if term.func.__globals__ is not module.__dict__ or term.func.__globals__['feedback'] is not module.feedback:
            raise ValueError('Term does not resolve actual feedback symbol: ' + key)
        if term.noise is not None or term.clip is not None:
            raise ValueError('Unexpected additional term noise/clip: ' + key)
        scale = _plain_scale(term.scale) if term.scale is not None else 1.
        # Expanded torch scale is accepted only when every existing entry equals expected.
        def all_equal(x):
            return all(all_equal(y) for y in x) if isinstance(x, list) else abs(x - SCALES[key]) < 1e-7
        if not all_equal(scale):
            raise ValueError('Unexpected manager scale: ' + key)
        params = term.params
        asset = params.get('asset_cfg')
        record = dict(scale=scale, parameters=list(params), default_argument_identities=identities['term_' + key]['defaults_identity'])
        if key in ('base_ang_vel', 'projected_gravity'):
            record['root_asset_configuration'] = _root_asset_configuration(term)
        if key in ('leg_pos', 'leg_vel', 'wheel_vel'):
            want_params = {'asset_cfg', 'bias_key' if key == 'leg_pos' else 'key'}
            if set(params) != want_params:
                raise ValueError('Unexpected joint observation parameters: ' + key)
            want = ['left_wheel_spin', 'right_wheel_spin'] if key == 'wheel_vel' else ['left_crank', 'left_hip', 'right_crank', 'right_hip']
            if asset is None or asset.name != 'robot' or list(asset.joint_names) != want or asset.preserve_order is not True:
                raise ValueError('Actual joint configuration differs: ' + key)
            record.update(joint_names=list(asset.joint_names), joint_ids=stdlib_snapshot(asset.joint_ids), preserve_order=True)
        if key == 'leg_pos' and params.get('bias_key') != '_mod4_leg_bias':
            raise ValueError('Unexpected legacy encoder bias key')
        if key in ('leg_vel', 'wheel_vel') and params.get('key') != key:
            raise ValueError('Unexpected velocity key')
        term_receipts[key] = record
    candidates = [fn for fn in closure_functions(env.scene.update)
                  if fn.__qualname__ == pins['sampling_update']['qualname']]
    if len(candidates) != 1:
        raise ValueError('Actual scene.update chain lacks unique original 100Hz closure')
    sampling = candidates[0]
    identities['sampling_update'] = verify_callable(sampling, pins['sampling_update'])
    cells = dict(zip(sampling.__code__.co_freevars, sampling.__closure__ or ()))
    if 'self' not in cells or cells['self'].cell_contents is not env or sampling.__globals__ is not module.__dict__:
        raise ValueError('100Hz sampling closure belongs to another environment/module')
    if not _same_callable(env.termination_manager.compute, bridge._termination_capture) or bridge.real is not env:
        raise ValueError('Require active original NativeTaskBridge pre-reset boundary')
    bridge_module = sys.modules.get(bridge_pin['module'])
    bridge_class_name = bridge_pin['qualname'].split('.')[0]
    bridge_class = vars(bridge_module).get(bridge_class_name) if bridge_module is not None else None
    if bridge_class is None or bridge_class not in type(bridge).__mro__:
        raise ValueError('Original bridge class absent from actual MRO')
    identities['bridge_class'] = verify_class(bridge_class, dict(bridge_pin, qualname=bridge_class_name))
    if env.termination_manager.compute.__func__ is not vars(bridge_class)['_termination_capture']:
        raise ValueError('Bridge terminal callback differs from original class descriptor')
    identities['terminal_boundary'] = verify_callable(env.termination_manager.compute, bridge_pin)
    return dict(kind='PASSIVE_CAPTURE_BINDING_INSPECTION_V1', binding_inspection_pass=True,
                native_enabled=False, exact=False, identities=identities,
                active_environment_MRO=classes, active_policy_terms=names,
                term_configuration=term_receipts,
                mid_end_clock='actual _sim_step_counter * 2500us; no wall clock inference',
                actual_live_capture_calls=0,
                full_clean35_mid_end=UNKNOWN, actual_default_joint_vel=UNKNOWN,
                observed_dtype='PENDING_ACTUAL_ARGUMENT_CAPTURE')


class PassiveCapture:
    """V3 thin tap. Scientific ownership is independent of mixed debug rings.

    Parent must call begin_control before the already-existing bridge.step, and
    end_control only after that same step and strict boundary. This class never
    performs a step, actor calculation, reset, SDK getter or terminal reduction.
    """
    def __init__(self, env, bridge, module, recorder, snapshot, inspection, *, ledger, source_refs):
        if type(snapshot) is not FieldSnapshot or ledger.codec is not snapshot.codec:
            raise TypeError('V3 explicit FieldSnapshot and same-codec ledger required')
        if set(source_refs) != {'feedback', 'sensor', 'delay', 'bridge', 'reset'}:
            raise ValueError('Explicit pinned field provenance required')
        if any(type(value) is not str or not value for value in source_refs.values()):
            raise ValueError('Nonempty source references required')
        self.env, self.bridge, self.module = env, bridge, module
        self.recorder, self.snapshot, self.inspection = recorder, snapshot, inspection
        self.ledger, self.source_refs = ledger, dict(source_refs)
        self._patches = []
        self._active = None
        self._phase = 'outside_scene_update'
        self._reset_depth = 0
        self._call_id = self._event_sequence = 0
        self._control_index = None
        self._pending_control = None
        self._ledger_result = None
        self.calls = Counter()
        self.closed = False

    def _try(self, thunk):
        try:
            return thunk()
        except BaseException as error:
            self.recorder.capture_error(error)
            return UNKNOWN

    def _rows(self, value, field, origin, clock):
        return self.snapshot.rows(value, source_ref=self.source_refs[origin],
                                  source_field=field, clock=clock)

    def _state(self, value, field, origin, clock):
        return self.snapshot.state(value, source_ref=self.source_refs[origin],
                                   source_field=field, clock=clock)

    def _event_id(self, kind):
        self._event_sequence += 1
        return kind + ':' + str(self._event_sequence)

    def _pending_summary(self):
        pending = self._pending_control
        if pending is None:
            return None
        counts = pending['original_callback_counts']
        reset = pending['reset_callback']
        owned_ids = (type(reset) is dict and type(reset.get('ids')) is dict
                     and reset['ids'].get('semantic_role') == 'ENV_IDS_FULL')
        return dict(original_terminal_callbacks=counts['terminal'], original_reset_callbacks=counts['reset'],
                    observer_error_count=self.recorder.capture_errors - pending['capture_errors_at_begin'],
                    reset_observation=('NOT_OBSERVED' if counts['reset'] == 0 else
                                       'OBSERVED_WITH_OWNED_IDS' if owned_ids else 'OBSERVED_METADATA_FAILED'))

    def _close_metadata(self, pack):
        summary = self._pending_summary()
        pack['b3_callback_provenance'] = summary
        problems = []
        if summary['observer_error_count']:
            problems.append('B3_OBSERVER_METADATA_ERRORS')
        if summary['original_terminal_callbacks'] != 1:
            problems.append('B3_ORIGINAL_TERMINAL_CALLBACK_COUNT')
        count = summary['original_reset_callbacks']
        if (count not in (0, 1) or
                (count == 1) != (pack['reset']['callback_status'] == 'OBSERVED')):
            problems.append('B3_OBSERVED_RESET_NOT_EXACTLY_RETAINED')
        if problems:
            pack['retention_status'] = 'INCOMPLETE'
            pack['missing'].extend(problems)

    def begin_control(self, control_index):
        """Parent-only explicit context; contains no original task call."""
        def begin():
            self.ledger.begin(control_index, clock=self._clock())
            self._control_index = control_index
            self._pending_control = dict(worker_control_index=control_index,
                normal_samples={'mid': {}, 'end': {}}, terminal_callback=None, reset_callback=None, post_return_callback=None,
                original_callback_counts=dict(terminal=0, reset=0),
                capture_errors_at_begin=self.recorder.capture_errors)
            return True
        return self._try(begin)

    def end_control(self, *, post_term, post_trunc, source_ref, actor35=None):
        """Consume only caller's already-returned original flags/END actor buffer.

        No flag recreation, terminal reduction, observation, context/pack getter,
        or fallback actor is performed. Missing actor remains UNKNOWN in ledger.
        """
        def end():
            clock = self._clock()
            owned_post = dict(clock=clock, source_ref=source_ref, term=UNKNOWN, trunc=UNKNOWN,
                              actor35_original_buffer='UNKNOWN_NOT_CAPTURED')
            if self._pending_control is not None:
                self._pending_control['post_return_callback'] = owned_post
            term = self.snapshot.mask(post_term, source_ref=source_ref,
                                      source_field='original_post_return.terminated', clock=clock)
            owned_post['term'] = term
            trunc = self.snapshot.mask(post_trunc, source_ref=source_ref,
                                       source_field='original_post_return.truncated', clock=clock)
            owned_post['trunc'] = trunc
            actor = None if actor35 is None else self.snapshot.rows(
                actor35, source_ref=source_ref, source_field='original_END_actor35_buffer', clock=clock)
            owned_post['actor35_original_buffer'] = actor if actor is not None else 'UNKNOWN_NOT_CAPTURED'
            result = self.ledger.end(post_term=term, post_trunc=trunc, clock=clock, actor=actor)
            self._close_metadata(result)
            self._control_index = None
            self._pending_control = None
            return result
        return self._try(end)

    def _delay_state(self):
        d = self.env._feedback_delay_mild
        key = self._active['key'] if self._active is not None else None
        return self._state(dict(enabled=d.enabled, delay_steps=d.delay, episode=d.episode,
                                cache=d.cache.get(key, UNKNOWN) if key else d.cache),
                           'original_delay_state', 'delay', self._clock())

    def _boundary_state(self, clock):
        sensor, delay = self.env._sensor_mild, self.env._feedback_delay_mild
        return dict(sensor_episode=self._state(sensor.episode, 'sensor.episode', 'sensor', clock),
                    delay_episode=self._state(delay.episode, 'delay.episode', 'delay', clock),
                    queue=self._state(delay.cache, 'delay.cache', 'delay', clock))

    @staticmethod
    def _normal(clock, key):
        return (type(clock) is dict and type(key) is str and key in CHANNELS
                and clock.get('phase') == 'scene_update' and clock.get('reset_depth') == 0
                and clock.get('is_original_100hz_slot') is True
                and clock.get('control_slot') in ('mid', 'end'))

    def attach(self):
        e, m, r = self.env, self.module, self.recorder
        sensor, delay = e._sensor_mild, e._feedback_delay_mild
        original_feedback, original_sensor, original_delay = m.feedback, sensor.apply, delay.apply
        original_update, original_term, original_reset = e.scene.update, e.termination_manager.compute, e._reset_idx

        def feedback(env, key, raw):
            if env is not e:
                return original_feedback(env, key, raw)
            self.calls['feedback'] += 1
            self._call_id += 1
            ticket = r.begin('feedback')
            parent = self._active
            clock = self._try(self._clock)
            normal = self._normal(clock, key)
            retain = normal or ticket is not None
            record = dict(call_id=self._call_id, key=key, clock=clock,
                          clean_origin='actual feedback raw argument, before noise and lag',
                          clean=self._try(lambda: self._rows(raw, 'feedback.raw', 'feedback', clock)) if retain else UNKNOWN,
                          full_clean35='UNKNOWN_NOT_COMPUTED', sensor_stage=UNKNOWN, delay_stage=UNKNOWN,
                          exception=None)
            self._active = record if retain else None
            try:
                out = original_feedback(env, key, raw)
                if retain:
                    record['return'] = self._try(lambda: self._rows(out, 'feedback.original_return', 'feedback', clock))
                return out
            except BaseException as error:
                record['exception'] = self._try(lambda: dict(type=type(error).__name__, message=str(error)[:320]))
                raise
            finally:
                self._active = parent
                if normal:
                    if self._pending_control is not None:
                        self._pending_control['normal_samples'][clock['control_slot']].setdefault(key, record)
                    self._try(lambda: self.ledger.normal_sample(
                        key, clock['control_slot'], record['clean'], clock=clock,
                        payload={name: value for name, value in record.items() if name != 'clean'}))
                self._try(lambda: r.commit(ticket, record))

        def sensor_apply(*args, **kwargs):
            self.calls['sensor_apply'] += 1
            record = self._active
            def capture_before():
                cached = sensor.cache.get(record['key'])
                clock = self._clock()
                return dict(noise_cache_last=self._rows(cached[0], 'sensor.cache.last.before', 'sensor', clock) if cached is not None else UNKNOWN,
                            episode=self._state(sensor.episode, 'sensor.episode.before', 'sensor', clock),
                            draw_counts=dict(sensor.draw_counts))
            before = self._try(capture_before) if record is not None else UNKNOWN
            out = original_sensor(*args, **kwargs)
            if record is not None:
                key = record['key']
                def capture_sensor():
                    cached = sensor.cache.get(key)
                    clock = self._clock()
                    return dict(profile=sensor.profile, before=before, fresh_due_local=UNKNOWN,
                                noise_used=self._rows(cached[1], 'sensor.cache.noise_used', 'sensor', clock) if cached is not None and sensor.profile != 'off' else UNKNOWN,
                                noise_cache_last=self._rows(cached[0], 'sensor.cache.last.after', 'sensor', clock) if cached is not None and sensor.profile != 'off' else UNKNOWN,
                                leg_bias_used=self._rows(sensor.bias, 'sensor.bias', 'sensor', clock) if key == 'leg_pos' and sensor.profile != 'off' else UNKNOWN,
                                episode=self._state(sensor.episode, 'sensor.episode.after', 'sensor', clock),
                                draw_counts=dict(sensor.draw_counts),
                                actual_noisy_return=self._rows(out, 'sensor.original_return', 'sensor', clock),
                                dtype=str(getattr(out, 'dtype', UNKNOWN)))
                record['sensor_stage'] = self._try(capture_sensor)
            return out

        def delay_apply(*args, **kwargs):
            self.calls['delay_apply'] += 1
            record = self._active
            before = self._try(self._delay_state) if record is not None else UNKNOWN
            if record is not None:
                record['delay_actual_input'] = self._try(lambda: self._rows(
                    args[1] if len(args) > 1 else kwargs['x'], 'delay.actual_input', 'delay', self._clock()))
            out = original_delay(*args, **kwargs)
            if record is not None:
                record['delay_stage'] = dict(before=before, after=self._try(self._delay_state),
                    actual_return=self._try(lambda: self._rows(out, 'delay.original_return', 'delay', self._clock())),
                    selection_origin='original cache.sample_tick/out, not replayed delay logic', local_delayed_mask=UNKNOWN)
            return out

        def update(*args, **kwargs):
            self.calls['scene_update'] += 1
            previous = self._phase
            self._phase = 'scene_update'
            try:
                return original_update(*args, **kwargs)
            finally:
                self._phase = previous

        def terminal(*args, **kwargs):
            self.calls['terminal_boundary'] += 1
            if self._pending_control is not None:
                self._pending_control['original_callback_counts']['terminal'] += 1
            out = original_term(*args, **kwargs)
            ticket = r.begin('terminal_pre_reset')
            clock = self._try(self._clock)
            event_id = self._event_id('terminal')
            def capture_terminal():
                pre = self.bridge.pre
                return dict(term=self.snapshot.mask(pre['term'], source_ref=self.source_refs['bridge'],
                                                    source_field='bridge.pre.term', clock=clock),
                            trunc=self.snapshot.mask(pre['trunc'], source_ref=self.source_refs['bridge'],
                                                     source_field='bridge.pre.trunc', clock=clock),
                            state=self._rows(pre['s1'], 'bridge.pre.s1', 'bridge', clock),
                            boundary=self._boundary_state(clock), terminal_clean35='UNKNOWN_NOT_COMPUTED')
            retained = self._try(capture_terminal)
            if self._pending_control is not None and self._pending_control['terminal_callback'] is None:
                self._pending_control['terminal_callback'] = dict(clock=clock, event_id=event_id, retained=retained)
            def retain_terminal():
                self.ledger.pre_reset(retained['term'], retained['trunc'], clock=clock,
                                      event_id=event_id, payload={key: value for key, value in retained.items()
                                                                 if key not in ('term', 'trunc')})
            self._try(retain_terminal)
            self._try(lambda: r.commit(ticket, dict(clock=clock, event_id=event_id, bridge_pre=retained,
                origin='existing bridge.pre after original termination capture, before reset')))
            return out

        def reset(*args, **kwargs):
            self.calls['reset_boundary'] += 1
            if self._pending_control is not None:
                self._pending_control['original_callback_counts']['reset'] += 1
            ticket = r.begin('reset_boundary')
            ids = args[0] if args else kwargs.get('env_ids', kwargs.get('ids', UNKNOWN))
            clock = self._try(self._clock)
            event_id = self._event_id('reset')
            retained_ids = self._try(lambda: self.snapshot.ids(ids, source_ref=self.source_refs['reset'],
                                        source_field='original_reset_callback_entry_ids', clock=clock))
            record = dict(clock=clock, event_id=event_id, ids=retained_ids,
                          before=self._try(lambda: self._boundary_state(clock)), after=UNKNOWN,
                          exception=None, outcome='RAISED')
            previous = self._phase
            self._phase = 'inside_reset'
            self._reset_depth += 1
            try:
                out = original_reset(*args, **kwargs)
                record['outcome'] = 'RETURNED'
                return out
            except BaseException as error:
                record['exception'] = self._try(lambda: dict(type=type(error).__name__, message=str(error)[:320]))
                raise
            finally:
                # On RAISED, this is the actually remaining partial state, not a completed reset claim.
                record['after'] = self._try(lambda: self._boundary_state(self._clock()))
                self._reset_depth -= 1
                self._phase = previous
                if self._pending_control is not None and self._pending_control['reset_callback'] is None:
                    self._pending_control['reset_callback'] = record
                self._try(lambda: self.ledger.reset(retained_ids, clock=clock, event_id=event_id,
                    before=record['before'], after=record['after'], outcome=record['outcome']))
                self._try(lambda: r.commit(ticket, record))

        try:
            self._patch(sensor, 'apply', sensor_apply)
            self._patch(delay, 'apply', delay_apply)
            self._patch(m, 'feedback', feedback)
            self._patch(e.scene, 'update', update)
            self._patch(e.termination_manager, 'compute', terminal)
            self._patch(e, '_reset_idx', reset)
        except BaseException:
            self.close()
            raise
        return self

    def finish(self):
        """Explicit outside-step ownership finalization, not JSON/CPU export."""
        self._ledger_result = self._try(self.ledger.finish)
        return self.report()

    def report(self):
        ledger = self._ledger_result if self._ledger_result is not None else 'PENDING_EXPLICIT_FINISH'
        retained = (type(ledger) is dict and ledger.get('all_controls_observed') is True
                    and all(pack['retention_status'] == 'EXPECTED_FIELDS_RETAINED' for pack in ledger['controls']))
        pending = None if self._pending_control is None else dict(
            kind='B3_INCOMPLETE_OWNED_CONTROL', retention_status='INCOMPLETE',
            original_post_return=('NOT_OBSERVED' if self._pending_control['post_return_callback'] is None
                                  else 'CALLER_SUPPLIED_BUFFERS_END_NOT_CLOSED'), provenance=self._pending_summary(),
            owned_partial_control=self._pending_control)
        return dict(kind='PASSIVE_SENSOR_CAPTURE_V3', binding=self.inspection,
                    bounded_debug_not_complete_sampling=self.recorder.report(), control_ledger=ledger,
                    incomplete_current_control=pending,
                    original_wrapper_call_counts=dict(self.calls), native_enabled=False, exact=False,
                    metadata_retention_complete=bool(retained and self.recorder.capture_errors == 0),
                    metadata_retention_is_not_native_admission=True,
                    clean0='UNKNOWN_NOT_CAPTURED', mid_remaining19='UNKNOWN_NOT_SAMPLED_AT_MID',
                    mid_full_clean35='UNKNOWN_NOT_COMPUTED', mid_actor35='UNKNOWN_50HZ_ONLY',
                    untapped_bitwise_actor35='UNKNOWN', private_global_RNG_parity='UNKNOWN',
                    source_only_not_native_admission=True)

    def _clock(self):
        e = self.env
        tick = vars(e)['_sim_step_counter']
        return dict(physics_tick=tick, sim_time_us=tick * 2500,
                    feedback_tick=vars(e)['_feedback_100hz_tick'],
                    common_control_counter=vars(e)['common_step_counter'], phase=self._phase,
                    control_slot=('mid' if tick % 8 == 4 else 'end' if tick > 0 and tick % 8 == 0 else UNKNOWN),
                    reset_depth=self._reset_depth,
                    is_original_100hz_slot=self._phase == 'scene_update' and self._reset_depth == 0 and tick % 4 == 0,
                    sample_identity='key + per-row episode + feedback_tick; repeated calls are not fresh samples')


    def _patch(self, owner, name, wrapped):
        values = vars(owner)
        present, original_stored = name in values, values.get(name)
        original_resolved = getattr(owner, name)
        setattr(owner, name, wrapped)
        self._patches.append((owner, name, present, original_stored, wrapped, original_resolved))


    def close(self):
        if self.closed:
            return
        # Refuse to overwrite wrappers installed by somebody else after this tap.
        if any(vars(owner).get(name) is not wrapped for owner, name, _, _, wrapped, _ in self._patches):
            raise RuntimeError('Restore conflict: a later owner replaced a tap binding')
        for owner, name, present, stored, _, _ in reversed(self._patches):
            if present:
                setattr(owner, name, stored)
            else:
                delattr(owner, name)
        self._patches.clear()
        self.closed = True



def _pin_reference(pin):
    return (pin['source_path'] + ':' + str(pin['definition_line']) + '-' + str(pin['end_line'])
            + '@sha256:' + pin['source_sha256'] + '::' + pin['module'] + '.' + pin['qualname'])


def _source_references(role_api, bridge_pin):
    pins = role_api['pins']
    return dict(feedback=_pin_reference(pins['feedback']), sensor=_pin_reference(pins['sensor_apply']),
                delay=_pin_reference(pins['delay_apply']), bridge=_pin_reference(bridge_pin),
                reset=_pin_reference(role_api['reset_chain']['layers'][0]['function']))


def install_passive_capture(env, bridge, feedback_module, role_api, bridge_pin, *,
                            snapshot, ledger, recorder=None, dependency_pins=None):
    """V3 explicit install; no backward fallback to B2 generic snapshot.

    Parent owns source admission and supplies an existing same-codec ledger.
    All dependency and original binding checks happen before any assignment.
    """
    from dependency_contract import verify_typed_dependency
    codec_binding = verify_typed_dependency(snapshot, ledger, dependency_pins=dependency_pins)
    inspection = dict(preflight(env, bridge, feedback_module, role_api, bridge_pin),
                      capture_schema='PASSIVE_SENSOR_CAPTURE_V3', typed_codec_binding=codec_binding)
    return PassiveCapture(env, bridge, feedback_module,
                          recorder if recorder is not None else BoundedRecorder(),
                          snapshot, inspection, ledger=ledger,
                          source_refs=_source_references(role_api, bridge_pin)).attach()
