"""Small capture-only glue around sealed B/C APIs. No plant or RNG calls."""
from collections import Counter, deque
import copy
import inspect
import sys
from pathlib import Path
from phase1_capture_contract import need, sha

CHANNELS = ('base_ang_vel', 'projected_gravity', 'leg_pos', 'leg_vel', 'wheel_vel')


def make_recorder(base, snapshot):
    class CoverageRecorder(base):
        """Count global original100Hz call slots, NOT per-row episode fresh samples."""
        def __init__(self):
            super().__init__(first=32, last=32, max_events=100000)
            self.global_slot_calls = Counter()
            self.global_slot_identities = set()
            self.duplicate_slot_calls = 0
            self.reset_callbacks = 0
            self.pre_reset_callbacks = 0
            self.special = {k: deque(maxlen=4) for k in ('reset_boundary', 'terminal_pre_reset', 'actor35_original_buffer')}

        def commit(self, ticket, payload):
            if ticket is not None:
                kind = ticket[1]
                if kind == 'feedback':
                    clock = payload['clock']
                    if clock['is_original_100hz_slot']:
                        identity = (payload['key'], clock['physics_tick'], clock['feedback_tick'])
                        if identity in self.global_slot_identities:
                            self.duplicate_slot_calls += 1
                        else:
                            # At most 128 controls * 2 slots * 5 channels; no unbounded run.
                            if len(self.global_slot_identities) < 1280:
                                self.global_slot_identities.add(identity)
                                self.global_slot_calls[(payload['key'], clock['control_slot'])] += 1
                            else:
                                self.capture_error(RuntimeError('bounded unique-feedback index exhausted'))
                elif kind == 'reset_boundary': self.reset_callbacks += 1
                elif kind == 'terminal_pre_reset': self.pre_reset_callbacks += 1
                if kind in self.special:
                    self.special[kind].append(dict(kind=kind, payload=payload))
            super().commit(ticket, payload)

        def actor(self, value, original, index):
            need(value is original and tuple(value.shape) == (80, 35), 'actor35 must be original returned N80 policy buffer')
            ticket = self.begin('actor35_original_buffer')
            payload = dict(control_index=index, original_return_identity=True, untapped_bitwise='UNKNOWN')
            try:
                if ticket is not None: payload['actor35'] = snapshot(value)
            except BaseException as exc:
                self.capture_error(exc)
            self.commit(ticket, payload)
            return value

        def coverage(self, controls):
            deficits = []
            for key in CHANNELS:
                for slot in ('mid', 'end'):
                    if self.global_slot_calls[(key, slot)] != controls: deficits.append('GLOBAL_100HZ_SLOT_CALL_COUNT:' + key + ':' + slot)
            if self.duplicate_slot_calls: deficits.append('DUPLICATE_GLOBAL_100HZ_SLOT_CALL')
            if self.capture_errors or self.captured >= self.max_events: deficits.append('SENSOR_CAPTURE_ERROR_OR_EXHAUSTED')
            return dict(unique_channel_global_physics_feedback_slots=len(self.global_slot_identities),
                        per_channel_global_slot_call_counts={k: {s: self.global_slot_calls[(k, s)] for s in ('mid', 'end')} for k in CHANNELS},
                        duplicate_global_slot_calls=self.duplicate_slot_calls, reset_callbacks=self.reset_callbacks,
                        pre_reset_callbacks=self.pre_reset_callbacks, per_row_episode_pairs='UNKNOWN_NEEDS_LIVE_VERIFIER',
                        per_row_episode_fresh_samples='UNKNOWN_NEEDS_LIVE_VERIFIER',
                        counter_scope='GLOBAL_ORIGINAL100HZ_CALL_SLOTS_NOT_PER_ROW_EPISODE_FRESHNESS',deficits=deficits)
    return CoverageRecorder()


class WindowRetention:
    """Retain two first/two last control windows, never accumulated raw history."""
    def __init__(self):
        self.first, self.last, self.seen = [], deque(maxlen=2), 0

    def add(self, control_index, events):
        value = dict(control_index=control_index, events=events)
        if len(self.first) < 2: self.first.append(value)
        self.last.append(value)
        self.seen += 1

    def report(self):
        return dict(control_windows_seen=self.seen, retained_window_bound=4,
                    first=self.first, last=list(self.last),
                    cap_note='Actuation cap bounds storage only; sealed tap still snapshots/clones every event after cap')


def stored_rng_counts(env):
    """Stored counters only; does not query/draw/restore any generator state."""
    sensor = vars(env).get('_sensor_mild')
    counts = vars(sensor).get('draw_counts') if sensor is not None else None
    return dict(sensor_draw_counts=copy.deepcopy(dict(counts)) if counts is not None else 'UNKNOWN',
                observer_rng_draws=0, scope='STORED_SENSOR_COUNTERS_NOT_GLOBAL_RNG_STREAM_EQUALITY')


def initial_sensor_memory(env, snapshot):
    """Existing instance memory only, after original compute66; never fresh clean0.

    Original sensor/delay caches may legally reuse pre-placement values at the
    same feedback tick. No invalidation, tick advance, getter or resampling.
    """
    fields = ('cache', 'fifo', 'cur', 'out', 'last', 'sample_tick', 'episode',
              'bias', 'delay', 'draw_counts')
    result = dict(clean0='UNKNOWN', initial_sensor_freshness='UNKNOWN_SAME_TICK_CACHE_MAY_BE_REUSED',
                  source='EXISTING_INSTANCE_MEMORY_AFTER_ORIGINAL66_BEFORE_CONTROL', components={})
    for name in ('_sensor_mild', '_feedback_delay_mild'):
        component = vars(env).get(name)
        memory = vars(component) if component is not None else {}
        try:
            result['components'][name] = snapshot({key: memory.get(key, 'UNKNOWN') for key in fields})
        except BaseException as exc:
            result['components'][name] = dict(status='UNKNOWN_SNAPSHOT_ERROR', error_type=type(exc).__name__)
    result['stored_clocks'] = {key: vars(env).get(key, 'UNKNOWN')
                              for key in ('_sim_step_counter', '_feedback_100hz_tick')}
    return result


def materialize(value, tensor_class):
    """After tap callbacks/restoration only; own captured tensors -> bounded JSON."""
    if isinstance(value, tensor_class): return value.detach().cpu().tolist()
    if type(value) is dict: return {str(k): materialize(v, tensor_class) for k, v in value.items()}
    if type(value) in (tuple, list, deque): return [materialize(v, tensor_class) for v in value]
    if value is None or type(value) in (str, bool, int, float): return value
    return dict(status='UNKNOWN', opaque_type=type(value).__module__ + '.' + type(value).__name__)


def verify_actuation_binding(env, api, role_source_rows):
    """Before C install: actual queue/adapter/wrapper source+code, not mere file pins.

    SDK target writers remain observed bindings, not source-qualified physical
    readback; a future live verifier must review their exact SDK provenance.
    """
    expected = {Path(p).name: r for p, r in role_source_rows.items()}
    adapter = vars(env)['_physics_action_delay']
    queue = vars(adapter)['queue']
    result = dict(classes=[], functions=[], target_writers=[],
                  physical_readback='UNKNOWN', sdk_target_writer_qualified=False)

    def approved_pin(value, module, qual):
        fn = value.__func__ if inspect.ismethod(value) else value
        fn = inspect.unwrap(fn)
        path = Path(fn.__code__.co_filename)
        raw = path.read_bytes()
        row = expected.get(path.name)
        need(row is not None and (len(raw), sha(raw)) == (row['bytes'], row['sha256']), 'actual actuation source differs: ' + path.name)
        pin = api.pin(path, module, qual)
        result['functions'].append(api.verify_callable(value, pin))

    for obj, module, qual in ((adapter, 'action_delay_sdk_adapter', 'PhysicalActionDelayAdapter'),
                              (queue, 'action_delay_physics_queue', 'PhysicsActionQueue')):
        path = Path(sys.modules[module].__file__)
        row = expected.get(path.name)
        need(row is not None and sha(path.read_bytes()) == row['sha256'], 'actuation actual class source differs')
        result['classes'].append(api.verify_class(type(obj), api.pin(path, module, qual)))
    for name in ('submit', 'apply'):
        approved_pin(getattr(queue, name), 'action_delay_physics_queue', 'PhysicsActionQueue.' + name)
    for group, term in vars(adapter)['terms'].items():
        for name, qual in (('process_actions', 'process'), ('apply_actions', 'apply')):
            approved_pin(getattr(term, name), 'action_delay_sdk_adapter', 'PhysicalActionDelayAdapter._wrap.<locals>.' + qual)
        asset = vars(term)['_asset']
        method = 'set_joint_position_target' if group == 'legs' else 'set_joint_velocity_target'
        target = getattr(asset, method)
        result['target_writers'].append(dict(group=group, method=method, same_asset_instance_id=id(asset),
                                             bound_self_is_asset=getattr(target, '__self__', None) is asset,
                                             module=getattr(target, '__module__', None),
                                             qualname=getattr(target, '__qualname__', None),
                                             binding='OBSERVED_NOT_QUALIFIED_SDK_PHYSICAL_READBACK'))
    return result


def restore_interfaces(actuation, sensor, bridge):
    """Try all original closes in reverse installation order; conflicts stay errors."""
    result = dict(ok=True, order=[], errors=[])
    for name, value in (('actuation', actuation), ('sensor', sensor), ('bridge', bridge)):
        if value is None: continue
        result['order'].append(name)
        try:
            returned = value.close()
            if name == 'actuation' and (type(returned) is not dict or returned.get('restored') is not True):
                raise RuntimeError('Actuation restore conflict: ' + repr(returned))
        except BaseException as exc:
            result['ok'] = False
            result['errors'].append(dict(phase=name, type=type(exc).__name__, message=str(exc)[:320]))
    return result
