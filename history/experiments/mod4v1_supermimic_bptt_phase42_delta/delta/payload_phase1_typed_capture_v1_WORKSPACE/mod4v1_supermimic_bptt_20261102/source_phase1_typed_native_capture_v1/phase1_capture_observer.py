"""NEW typed producer metadata; never steps, samples, reads SDK or RNG state.
C2 already owns its clones. This module adopts explicit queue roles without a
second clone. Other known per-env stored memory uses the published witness role.
"""
from collections import deque
from pathlib import Path
import copy
import inspect
import sys
from phase1_capture_contract import need, sha, PRODUCER_ABI, INCOMPLETE_KIND

QUEUE_FIELDS = ('lag_steps', 'episode', 'pending', 'pending_valid', 'issued_tick', 'due_tick',
                'applied', 'applied_valid', 'applied_issue_tick', 'first_apply_tick',
                'last_submit_tick', 'last_apply_tick')
C2_CONTAINER = 'PHASE1_TYPED_C2_EVENT_WINDOWS_V1'


def stored_clock(env, *, phase='outside_scene_update'):
    memory = vars(env)
    return dict(physics_tick=memory.get('_sim_step_counter', 'UNKNOWN'),
                feedback_tick=memory.get('_feedback_100hz_tick', 'UNKNOWN'),
                common_control_counter=memory.get('common_step_counter', 'UNKNOWN'),
                phase=phase, control_slot='UNKNOWN', reset_depth=0,
                is_original_100hz_slot=False)


def unknown_tensor(value, codec, *, source_ref, field, reason):
    """Metadata only: in particular, joint IDs are NOT environment-ID tensors."""
    return dict(status='UNKNOWN', reason=reason, source_ref=source_ref, source_field=field,
                original_shape=list(value.shape), original_dtype=str(value.dtype),
                original_device=str(value.device), source_env_axis=None,
                semantic_role='NOT_REPRESENTED_BY_THE_FOUR_PUBLISHED_ROLES', values='UNKNOWN')


def adopt_queue_owned(value, codec, *, group, source_ref, field, clock):
    """Adopt an existing C2 detach+clone; no tensor operation or data comparison."""
    shape = list(value.shape)
    need(group in ('legs', 'wheels') and shape and shape[0] == 80,
         'known C2 group and explicit original N80 axis required')
    envelope = dict(envelope_kind='TYPED_SOURCE_TENSOR_V1', semantic_role='QUEUE_GROUP_FULL',
                    source_ref=source_ref, source_pin_ref=source_ref, source_field=field,
                    original_shape=shape, original_dtype=str(value.dtype), original_device=str(value.device),
                    source_env_axis=0, retained_shape=list(shape),
                    row_mapping=dict(kind='ALL_ENV_ROWS_IN_ORIGINAL_ORDER', env_axis=0, env_ids=list(range(80))),
                    source_clock=dict(clock), group=group, ownership='OWNED_BY_DETACH_CLONE',
                    selection='FULL_SEMANTIC_EXCEPTION',
                    evidence_level='OWNED_TENSOR_SNAPSHOT_NOT_SDK_PROVENANCE_QUALIFICATION', values=value,
                    ownership_origin='UNCHANGED_C2_FREEZE_MEMORY_ALREADY_DETACH_CLONED',
                    original_metadata_authority='C2_CLONE_METADATA_SOURCE_CODE_CLAIM_NOT_INDEPENDENT_INPUT_READBACK',
                    clock_authority='OUTSIDE_CONTROL_ADOPTION_CLOCK_NOT_ORIGINAL_EVENT_PHYSICS_TICK')
    codec.validate_owned(envelope, allowed_roles=('QUEUE_GROUP_FULL',))
    return envelope


def typed_c2_memory(value, codec, snapshot, *, source_ref, field, clock, group=None, role='UNKNOWN'):
    """Role is supplied by the source field, never selected by matching shape 80."""
    if isinstance(value, codec.tensor_type):
        if role == 'QUEUE_GROUP_FULL' and group in ('legs', 'wheels'):
            return adopt_queue_owned(value, codec, group=group, source_ref=source_ref, field=field, clock=clock)
        if role == 'ENV_ROWS_WITNESS':
            if list(value.shape) and list(value.shape)[0] == 80:
                return snapshot.rows(value, source_ref=source_ref, source_field=field, clock=clock)
            return unknown_tensor(value, codec, source_ref=source_ref, field=field,
                                  reason='Declared stored per-env field has no qualified N80 axis; no substitute role')
        return unknown_tensor(value, codec, source_ref=source_ref, field=field,
                              reason='Joint/opaque/non-env tensor values have no published applicable semantic role')
    if type(value) is dict:
        need(all(type(key) is str for key in value), 'C2 metadata dictionary needs original string keys')
        return {key: typed_c2_memory(item, codec, snapshot, source_ref=source_ref,
                                    field=field+'.'+key, clock=clock, group=group, role=role)
                for key, item in value.items()}
    if type(value) in (list, tuple):
        return [typed_c2_memory(item, codec, snapshot, source_ref=source_ref,
                               field=field+'['+str(index)+']', clock=clock, group=group, role=role)
                for index, item in enumerate(value)]
    if type(value) is slice:
        return dict(kind='PYTHON_SLICE_NOT_ENV_IDS', start=value.start, stop=value.stop, step=value.step)
    if value is None or type(value) in (bool, int, float, str):
        return value
    return dict(status='UNKNOWN', opaque_type=type(value).__module__+'.'+type(value).__name__)


def typed_c2_event(event, codec, snapshot, *, source_ref, clock):
    need(type(event) is dict, 'original C2 event dictionary required')
    group = event.get('group') if type(event.get('group')) is str else None
    group = group if group in ('legs', 'wheels') else None
    result = {}
    for key, value in event.items():
        role = 'ENV_ROWS_WITNESS' if key == 'static' else 'UNKNOWN'
        if key in ('pre', 'post', 'selected_target') and group is not None:
            role = 'QUEUE_GROUP_FULL'
        if key in ('args', 'kwargs'):
            if type(value) in (list, tuple):
                result[key] = [typed_c2_memory(item, codec, snapshot, source_ref=source_ref,
                    field='event.'+key+'['+str(index)+']', clock=clock, group=group,
                    role=('QUEUE_GROUP_FULL' if group is not None and
                          ((event.get('kind') == 'queue_submit' and index == 1) or
                           (event.get('kind') in ('issue', 'target_write') and index == 0)) else 'UNKNOWN'))
                    for index, item in enumerate(value)]
            elif type(value) is dict:
                result[key] = {name: typed_c2_memory(item, codec, snapshot, source_ref=source_ref,
                    field='event.'+key+'.'+name, clock=clock, group=group,
                    role=('QUEUE_GROUP_FULL' if group is not None and name in ('command', 'action', 'target', 'positions', 'velocities')
                          else 'UNKNOWN')) for name, item in value.items()}
            else:
                result[key] = typed_c2_memory(value, codec, snapshot, source_ref=source_ref,
                    field='event.'+key, clock=clock)
        else:
            result[key] = typed_c2_memory(value, codec, snapshot, source_ref=source_ref,
                field='event.'+key, clock=clock, group=group, role=role)
    result['adoption_clock'] = dict(clock)
    result['typed_producer_metadata'] = dict(schema=C2_CONTAINER,
        original_capture_schema_preserved=True, event_tick_is_original_unvalidated=True,
        envelope_clock_is_adoption_only=True, group_is_source_context_not_DOF=True,
        DOF_target_pipeline_join='UNKNOWN', physical_readback='UNKNOWN')
    return result


class WindowRetention:
    """Original two-first/two-last bound; middle windows explicitly unretained."""
    def __init__(self, codec, snapshot, source_ref):
        self.codec, self.snapshot, self.source_ref = codec, snapshot, source_ref
        self.first, self.last, self.count = [], deque(maxlen=2), 0

    def add(self, control_index, events, *, clock):
        need(type(control_index) is int and 0 <= control_index < 128 and self.count < 128,
             'finite control-window bound')
        need(type(events) is list and len(events) <= 8192, 'original C2 per-window event bound')
        row = dict(control_index=control_index, adoption_clock=dict(clock),
                   events=[typed_c2_event(event, self.codec, self.snapshot,
                           source_ref=self.source_ref, clock=clock) for event in events])
        if len(self.first) < 2:
            self.first.append(row)
        self.last.append(row)
        self.count += 1

    def report(self):
        return dict(control_windows_seen=self.count, retained_window_bound=4,
                    first=list(self.first), last=list(self.last),
                    retention='ORIGINAL_FIRST2_LAST2_NOT_ALL_C2_WINDOWS', middle_windows='UNKNOWN_UNRETAINED')


def initial_sensor_memory(env, snapshot, source_refs):
    fields = ('cache', 'fifo', 'cur', 'out', 'last', 'sample_tick', 'episode', 'bias', 'delay', 'draw_counts')
    result = dict(clean0='UNKNOWN', initial_sensor_freshness='UNKNOWN_SAME_TICK_CACHE_MAY_BE_REUSED',
                  source='EXISTING_INSTANCE_MEMORY_AFTER_ORIGINAL66_BEFORE_CONTROL', components={})
    clock = stored_clock(env)
    for name, origin in (('_sensor_mild', 'sensor'), ('_feedback_delay_mild', 'delay')):
        component = vars(env).get(name)
        memory = vars(component) if component is not None else {}
        value = {key: memory.get(key, 'UNKNOWN') for key in fields}
        if type(value['draw_counts']) is not str:
            value['draw_counts'] = dict(value['draw_counts'])
        try:
            result['components'][name] = snapshot.state(value, source_ref=source_refs[origin],
                                                       source_field='initial.'+name, clock=clock)
        except BaseException as exc:
            result['components'][name] = dict(status='UNKNOWN_SNAPSHOT_ERROR', error_type=type(exc).__name__)
    result['stored_clocks'] = clock
    return result


def stored_actuation_evidence(env, codec, *, source_ref):
    adapter = vars(env).get('_physics_action_delay')
    memory = vars(adapter) if adapter is not None else {}
    result = dict(original_adapter_stored_target_check={}, terms={}, observer_independent_readback='UNKNOWN',
                  external_physical_readback='UNKNOWN', source_ref=source_ref,
                  scope='ORIGINAL_D4_STORED_NUMBERS_NOT_ADDITIONAL_TARGET_READBACK')
    for key in ('calls', 'formula_max_error', 'collect'):
        value = memory.get(key, 'UNKNOWN')
        result['original_adapter_stored_target_check'][key] = typed_c2_memory(
            value, codec, None, source_ref=source_ref, field='adapter.'+key, clock=stored_clock(env))
    terms = memory.get('terms')
    for group, term in terms.items() if type(terms) is dict else ():
        data = vars(term)
        ids = data.get('_joint_ids', 'UNKNOWN')
        result['terms'][group] = dict(term_identity=id(term), asset_identity=id(data.get('_asset')),
            stored_joint_ids=typed_c2_memory(ids, codec, None, source_ref=source_ref,
                field='term.'+group+'._joint_ids', clock=stored_clock(env)),
            identity_scope='STORED_TERM_BINDING_NOT_QUALIFIED_DOF_OR_TARGET_JOIN')
    return result


def verify_c2_source_binding(api, module):
    path = Path(module.__file__)
    result = dict(classes=[api.verify_class(module.ActuationTap, api.pin(path, module.__name__, 'ActuationTap'))], functions=[])
    for name in ('stored', 'freeze_memory', 'queue_snapshot', 'snapshot_static', 'install_actuation_tap',
                 'ActuationTap.__init__', 'ActuationTap._guard', 'ActuationTap._keep', 'ActuationTap._patch',
                 'ActuationTap.snapshot_static', 'ActuationTap.drain', 'ActuationTap.status', 'ActuationTap.close'):
        value = module
        for part in name.split('.'):
            value = getattr(value, part)
        result['functions'].append(api.verify_callable(value, api.pin(path, module.__name__, name)))
    need(module.QUEUE_FIELDS == QUEUE_FIELDS and module.GROUPS == {'legs':4, 'wheels':2} and module.PHYSICS_US == 2500,
         'original complete C2 literal configuration differs')
    return result


def incomplete_capture(task, sensor, actuation, retained, *, source_error):
    """No finish/end is invented for an open original B4 pending control."""
    report = sensor.report()
    return dict(kind=INCOMPLETE_KIND, purpose=task['purpose'], group_id=task['group_id'],
                typed_producer_schema=PRODUCER_ABI, execution_closed_before_app=False,
                sensor=report, typed_pending_control=report.get('incomplete_current_control'),
                actuation=dict(capture_schema=C2_CONTAINER, status=actuation.status() if actuation is not None else None,
                               windows=retained.report() if retained is not None else None),
                source_error=source_error, science_consistency_status='UNKNOWN_PENDING_TYPED_CONSUMER',
                capture_interface_passed=False, gate1='UNKNOWN', exact=False, paper_ready=False, stage2_GO=False)


def stored_rng_counts(env):
    """Stored counters only; does not query/draw/restore any generator state."""
    sensor = vars(env).get('_sensor_mild')
    counts = vars(sensor).get('draw_counts') if sensor is not None else None
    return dict(sensor_draw_counts=copy.deepcopy(dict(counts)) if counts is not None else 'UNKNOWN',
                observer_rng_draws=0, scope='STORED_SENSOR_COUNTERS_NOT_GLOBAL_RNG_STREAM_EQUALITY')


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
