"""SOURCE-only typed tensor codec and bounded ownership ledger.

No Torch import or target construction. Callers supply the already-existing
Tensor class, witness index, tensors and original clocks. CaptureError is a
metadata error, never permission to replay or replace an original callback.
"""
import math


ROLES = ('ENV_ROWS_WITNESS', 'ENV_IDS_FULL', 'TERMINAL_BOOL_FULL', 'QUEUE_GROUP_FULL')
CHANNEL_WIDTHS = {'base_ang_vel': 3, 'projected_gravity': 3, 'leg_pos': 4,
                  'leg_vel': 4, 'wheel_vel': 2}
INTEGER_DTYPES = ('torch.int8', 'torch.int16', 'torch.int32', 'torch.int64',
                  'torch.uint8', 'torch.uint16', 'torch.uint32', 'torch.uint64')


class CaptureError(ValueError):
    """Explicit metadata/ownership contract failure, not a native outcome."""


def _need(condition, message):
    if not condition:
        raise CaptureError(message)


def _metadata(value, depth=0):
    _need(depth <= 64, 'metadata nesting exceeds 64')
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        _need(math.isfinite(value), 'nonfinite Python metadata')
        return value
    if type(value) in (list, tuple):
        return [_metadata(item, depth + 1) for item in value]
    if type(value) is dict:
        result = {}
        for key, item in value.items():
            _need(type(key) is str, 'metadata keys must be strings')
            result[key] = _metadata(item, depth + 1)
        return result
    raise CaptureError('metadata must be plain Python, not a tensor/getter/object')


def _clock(value):
    result = _metadata(value)
    _need(type(result) is dict, 'clock must be a dictionary')
    for key in ('physics_tick', 'feedback_tick', 'reset_depth'):
        _need(type(result.get(key)) is int, 'missing/inexact original clock: ' + key)
    _need(result['reset_depth'] >= 0, 'negative reset depth')
    _need(type(result.get('phase')) is str, 'missing original phase')
    return result


def _clock_key(value):
    return tuple(value.get(key) for key in ('physics_tick', 'feedback_tick',
                 'common_control_counter', 'phase', 'reset_depth'))


class CaptureCodec:
    def __init__(self, tensor_type, *, witness_index, witness_env_ids, n=80):
        _need(type(n) is int and n == 80, 'this lineage requires N80')
        _need(isinstance(tensor_type, type), 'supply the existing tensor class')
        _need(type(witness_env_ids) in (list, tuple), 'explicit Python witness IDs required')
        ids = tuple(witness_env_ids)
        _need(1 <= len(ids) <= 8, 'witness count must be 1..8')
        for item in ids:
            _need(type(item) is int and 0 <= item < n, 'invalid declared witness ID')
        _need(len(set(ids)) == len(ids), 'duplicate declared witness ID')
        _need(isinstance(witness_index, tensor_type), 'existing witness index tensor required')
        _need(tuple(witness_index.shape) == (len(ids),), 'witness index shape differs')
        _need(str(witness_index.dtype) == 'torch.int64', 'witness index must be existing int64')
        self.tensor_type, self.n = tensor_type, n
        self.witness_index, self.witness_env_ids = witness_index, ids

    def capture(self, tensor, *, role, source_ref, source_field, clock, env_axis, group=None):
        _need(type(role) is str and role in ROLES, 'unknown explicit semantic role')
        _need(group is None or type(group) is str, 'group must be a Python string or None')
        _need(isinstance(tensor, self.tensor_type), 'capture requires existing tensor')
        _need(type(source_ref) is str and bool(source_ref), 'source_ref required')
        _need(type(source_field) is str and bool(source_field), 'source_field required')
        shape, dtype, device = list(tensor.shape), str(tensor.dtype), str(tensor.device)
        original_clock = _clock(clock)
        for dimension in shape:
            _need(type(dimension) is int and dimension >= 0, 'invalid tensor shape')
        retained = list(shape)
        if role == 'ENV_IDS_FULL':
            _need(env_axis is None and len(shape) == 1 and shape[0] <= self.n,
                  'IDs require a full one-dimensional argument, K<=80, no env axis')
            _need(dtype in INTEGER_DTYPES, 'IDs require original integer dtype')
            _need(group is None, 'IDs have no queue group')
            mapping = dict(kind='VALUES_ARE_ENV_IDS_NOT_ENV_AXIS', preserve_entire_argument=True)
        else:
            _need(type(env_axis) is int and 0 <= env_axis < len(shape), 'explicit env axis required')
            _need(shape[env_axis] == self.n, 'declared env axis must be N80')
            if role == 'TERMINAL_BOOL_FULL':
                _need(shape == [80] and env_axis == 0 and dtype == 'torch.bool',
                      'terminal masks require original bool[80]')
                _need(group is None, 'terminal mask has no queue group')
            elif role == 'QUEUE_GROUP_FULL':
                _need(group in ('legs', 'wheels'), 'explicit queue group required')
            else:
                _need(group is None, 'witness tensor has no queue group')
                _need(str(self.witness_index.device) == device, 'witness index must share original device')
                _need(tuple(self.witness_index.shape) == (len(self.witness_env_ids),)
                      and str(self.witness_index.dtype) == 'torch.int64', 'witness index metadata changed')
                retained[env_axis] = len(self.witness_env_ids)
            ids = list(self.witness_env_ids) if role == 'ENV_ROWS_WITNESS' else list(range(self.n))
            mapping = dict(kind='EXPLICIT_ORIGINAL_ENV_ROWS' if role == 'ENV_ROWS_WITNESS'
                           else 'ALL_ENV_ROWS_IN_ORIGINAL_ORDER', env_axis=env_axis, env_ids=ids)
            if role == 'ENV_ROWS_WITNESS':
                mapping['index_binding'] = 'CALLER_DECLARED_INDEX_BINDING_NOT_READBACK'
        # Every source metadata field above is saved before selection/copy.
        detached = tensor.detach()
        if role == 'ENV_ROWS_WITNESS':
            owned = detached.index_select(env_axis, self.witness_index)
            ownership = 'OWNED_BY_INDEX_SELECT'
        else:
            owned = detached.clone()
            ownership = 'OWNED_BY_DETACH_CLONE'
        result = dict(envelope_kind='TYPED_SOURCE_TENSOR_V1', semantic_role=role,
                      source_ref=source_ref, source_pin_ref=source_ref, source_field=source_field,
                      original_shape=shape, original_dtype=dtype, original_device=device,
                      source_env_axis=env_axis, retained_shape=retained, row_mapping=mapping,
                      source_clock=original_clock, group=group, ownership=ownership,
                      selection='ROWS_FROM_EXPLICIT_ROLE_NOT_SHAPE_INFERENCE' if role == 'ENV_ROWS_WITNESS'
                                else 'FULL_SEMANTIC_EXCEPTION',
                      evidence_level='OWNED_TENSOR_SNAPSHOT_NOT_SDK_PROVENANCE_QUALIFICATION', values=owned)
        self.validate_owned(result)
        return result

    def validate_owned(self, envelope, *, allowed_roles=None):
        _need(type(envelope) is dict, 'typed owned envelope required')
        for key, item in envelope.items():
            _need(type(key) is str, 'envelope keys must be Python strings')
            if key != 'values':
                _metadata(item)
        _need(envelope.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1', 'typed owned envelope required')
        role = envelope.get('semantic_role')
        _need(type(role) is str and role in ROLES, 'invalid envelope role')
        if allowed_roles is not None:
            _need(type(allowed_roles) in (tuple, list), 'allowed roles must be explicit Python tuple/list')
            for allowed in allowed_roles:
                _need(type(allowed) is str and allowed in ROLES, 'invalid allowed role')
            _need(role in allowed_roles, 'envelope role disallowed at this field')
        required = ('source_ref', 'source_pin_ref', 'source_field', 'original_shape', 'original_dtype',
                    'original_device', 'source_env_axis', 'retained_shape', 'row_mapping',
                    'source_clock', 'group', 'ownership', 'selection', 'evidence_level', 'values')
        for key in required:
            _need(key in envelope, 'missing envelope metadata: ' + key)
        _need(type(envelope['row_mapping']) is dict, 'row mapping dictionary required')
        _need(type(envelope['source_ref']) is str and bool(envelope['source_ref'])
              and type(envelope['source_field']) is str and bool(envelope['source_field']),
              'source identity metadata required')
        _need(envelope['source_pin_ref'] == envelope['source_ref'], 'source reference aliases differ')
        _need(envelope['selection'] == ('ROWS_FROM_EXPLICIT_ROLE_NOT_SHAPE_INFERENCE'
                                       if role == 'ENV_ROWS_WITNESS' else 'FULL_SEMANTIC_EXCEPTION'),
              'selection metadata differs')
        _need(envelope['evidence_level'] == 'OWNED_TENSOR_SNAPSHOT_NOT_SDK_PROVENANCE_QUALIFICATION',
              'snapshot evidence scope differs')
        value = envelope.get('values')
        _need(isinstance(value, self.tensor_type), 'owned tensor payload required')
        _need(list(value.shape) == envelope.get('retained_shape'), 'owned tensor shape changed')
        _need(str(value.dtype) == envelope.get('original_dtype'), 'owned tensor dtype changed')
        _need(str(value.device) == envelope.get('original_device'), 'owned tensor device changed')
        _clock(envelope.get('source_clock'))
        original, retained = envelope.get('original_shape'), envelope.get('retained_shape')
        axis = envelope.get('source_env_axis')
        _need(type(original) is list and type(retained) is list, 'shape metadata required')
        for dimension in original + retained:
            _need(type(dimension) is int and dimension >= 0, 'invalid envelope shape dimension')
        if role == 'ENV_IDS_FULL':
            _need(axis is None and len(original) == 1 and original == retained
                  and original[0] <= 80 and envelope['original_dtype'] in INTEGER_DTYPES,
                  'invalid full ID envelope')
            _need(envelope.get('ownership') == 'OWNED_BY_DETACH_CLONE'
                  and envelope['row_mapping'].get('kind') == 'VALUES_ARE_ENV_IDS_NOT_ENV_AXIS'
                  and envelope['row_mapping'].get('preserve_entire_argument') is True
                  and envelope.get('group') is None, 'invalid ID ownership/mapping')
        else:
            _need(type(axis) is int and 0 <= axis < len(original) and original[axis] == 80,
                  'invalid source env axis')
            expected = list(original)
            if role == 'ENV_ROWS_WITNESS':
                expected[axis] = len(self.witness_env_ids)
                _need(envelope['row_mapping'].get('env_ids') == list(self.witness_env_ids)
                      and envelope['row_mapping'].get('kind') == 'EXPLICIT_ORIGINAL_ENV_ROWS'
                      and envelope['row_mapping'].get('env_axis') == axis
                      and envelope['row_mapping'].get('index_binding') == 'CALLER_DECLARED_INDEX_BINDING_NOT_READBACK'
                      and envelope.get('group') is None, 'witness row mapping differs')
                _need(envelope.get('ownership') == 'OWNED_BY_INDEX_SELECT', 'invalid witness ownership')
            else:
                _need(envelope['row_mapping'].get('env_ids') == list(range(80))
                      and envelope['row_mapping'].get('kind') == 'ALL_ENV_ROWS_IN_ORIGINAL_ORDER'
                      and envelope['row_mapping'].get('env_axis') == axis, 'full rows differ')
                _need(envelope.get('ownership') == 'OWNED_BY_DETACH_CLONE', 'invalid full ownership')
            _need(retained == expected, 'retained shape differs from explicit role')
            if role == 'TERMINAL_BOOL_FULL':
                _need(original == [80] and axis == 0 and envelope['original_dtype'] == 'torch.bool'
                      and envelope.get('group') is None, 'invalid terminal bool envelope')
            if role == 'QUEUE_GROUP_FULL':
                _need(envelope.get('group') in ('legs', 'wheels'), 'missing queue group')

    def _validate_tree(self, value, allowed_roles=None, depth=0):
        _need(depth <= 64, 'owned payload nesting exceeds 64')
        if isinstance(value, self.tensor_type):
            raise CaptureError('bare tensor lacks explicit semantic role')
        if type(value) is dict:
            if type(value.get('envelope_kind')) is str and value.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1':
                self.validate_owned(value, allowed_roles=allowed_roles)
                return
            for key, item in value.items():
                _need(type(key) is str, 'owned payload keys must be strings')
                self._validate_tree(item, allowed_roles, depth + 1)
        elif type(value) in (list, tuple):
            for item in value:
                self._validate_tree(item, allowed_roles, depth + 1)
        else:
            _metadata(value)

    def materialize(self, value):
        """Outside-loop only. No dtype cast, float conversion or second clone."""
        self._validate_tree(value)
        def convert(item):
            if type(item) is dict:
                if item.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1':
                    result = {key: _metadata(val) for key, val in item.items() if key != 'values'}
                    result['values'] = _metadata(item['values'].detach().cpu().tolist())
                    return result
                return {key: convert(val) for key, val in item.items()}
            if type(item) in (list, tuple):
                return [convert(val) for val in item]
            return _metadata(item)
        return convert(value)


class ControlLedger:
    def __init__(self, codec, *, controls, run_id):
        _need(isinstance(codec, CaptureCodec), 'codec instance required')
        _need(type(controls) is int and controls in (64, 128), 'controls must be 64 or 128')
        _need(type(run_id) is str and bool(run_id), 'run_id required')
        self.codec, self.controls, self.run_id = codec, controls, run_id
        self._packs, self._open, self._finished = [], None, False

    def _active(self):
        _need(not self._finished and self._open is not None, 'no active control')
        return self._open

    def begin(self, control_index, *, clock):
        _need(not self._finished and self._open is None, 'control already open or ledger finished')
        _need(type(control_index) is int and control_index == len(self._packs)
              and control_index < self.controls, 'control index/cap differs')
        self._open = dict(worker_control_index=control_index, begin_clock=_clock(clock),
                          normal_samples={'mid': {}, 'end': {}}, pre_reset=None,
                          reset=dict(callback_status='NOT_OBSERVED', ids=None), post_return=None)

    def normal_sample(self, channel, slot, clean, *, clock, payload=None):
        pack = self._active()
        _need(type(channel) is str and channel in CHANNEL_WIDTHS
              and type(slot) is str and slot in ('mid', 'end'), 'unknown normal channel/slot')
        _need(channel not in pack['normal_samples'][slot], 'duplicate normal channel slot')
        c = _clock(clock)
        tick = c['physics_tick']
        _need(c['phase'] == 'scene_update' and c['reset_depth'] == 0
              and c.get('is_original_100hz_slot') is True, 'not an original normal 100Hz call')
        _need((slot == 'mid' and tick % 8 == 4) or (slot == 'end' and tick > 0 and tick % 8 == 0),
              'normal slot/physics clock differs')
        if 'control_slot' in c:
            _need(c['control_slot'] == slot, 'original slot label differs')
        self.codec.validate_owned(clean, allowed_roles=('ENV_ROWS_WITNESS',))
        _need(clean['source_env_axis'] == 0 and clean['original_shape'] == [80, CHANNEL_WIDTHS[channel]],
              'clean channel source shape differs')
        _need(_clock_key(clean['source_clock']) == _clock_key(c), 'clean source clock differs')
        self.codec._validate_tree(payload, ('ENV_ROWS_WITNESS',))
        existing = pack['normal_samples'][slot]
        if existing:
            first = next(iter(existing.values()))
            _need(_clock_key(first['clock']) == _clock_key(c), 'channels do not share original slot clock')
        existing[channel] = dict(clock=c, clean=clean, payload=payload)

    def pre_reset(self, term, trunc, *, clock, event_id, payload=None):
        pack = self._active()
        _need(pack['pre_reset'] is None, 'duplicate original termination record')
        _need(type(event_id) is str and bool(event_id), 'termination event ID required')
        self.codec.validate_owned(term, allowed_roles=('TERMINAL_BOOL_FULL',))
        self.codec.validate_owned(trunc, allowed_roles=('TERMINAL_BOOL_FULL',))
        c = _clock(clock)
        _need(_clock_key(term['source_clock']) == _clock_key(c)
              and _clock_key(trunc['source_clock']) == _clock_key(c), 'pre flags clock differs')
        self.codec._validate_tree(payload, ('ENV_ROWS_WITNESS', 'QUEUE_GROUP_FULL', 'TERMINAL_BOOL_FULL'))
        pack['pre_reset'] = dict(event_id=event_id, clock=c, term=term, trunc=trunc, payload=payload)

    def reset(self, ids, *, clock, event_id, before=None, after=None, outcome='RETURNED'):
        pack = self._active()
        _need(pack['reset']['callback_status'] == 'NOT_OBSERVED', 'duplicate original reset callback')
        _need(type(event_id) is str and bool(event_id), 'reset event ID required')
        _need(type(outcome) is str and outcome in ('RETURNED', 'RAISED'), 'original reset outcome required')
        self.codec.validate_owned(ids, allowed_roles=('ENV_IDS_FULL',))
        c = _clock(clock)
        _need(_clock_key(ids['source_clock']) == _clock_key(c), 'reset IDs source clock differs')
        self.codec._validate_tree(before, ('ENV_ROWS_WITNESS', 'QUEUE_GROUP_FULL'))
        self.codec._validate_tree(after, ('ENV_ROWS_WITNESS', 'QUEUE_GROUP_FULL'))
        prior = pack['pre_reset']
        pack['reset'] = dict(callback_status='OBSERVED', event_id=event_id, clock=c,
                             prior_termination_event_id=prior['event_id'] if prior is not None else None,
                             ids=ids, before=before, after=after, outcome=outcome)

    def end(self, *, post_term, post_trunc, clock, actor=None):
        pack = self._active()
        self.codec.validate_owned(post_term, allowed_roles=('TERMINAL_BOOL_FULL',))
        self.codec.validate_owned(post_trunc, allowed_roles=('TERMINAL_BOOL_FULL',))
        c = _clock(clock)
        _need(_clock_key(post_term['source_clock']) == _clock_key(c)
              and _clock_key(post_trunc['source_clock']) == _clock_key(c), 'post flags source clock differs')
        if actor is not None:
            self.codec.validate_owned(actor, allowed_roles=('ENV_ROWS_WITNESS',))
            _need(actor['source_env_axis'] == 0 and actor['original_shape'] == [80, 35], 'actor35 source shape differs')
            _need(_clock_key(actor['source_clock']) == _clock_key(c), 'actor source clock differs')
        pack['post_return'] = dict(clock=c, term=post_term, trunc=post_trunc,
                                   actor35_original_buffer=actor if actor is not None else 'UNKNOWN_NOT_CAPTURED')
        missing = []
        for slot in ('mid', 'end'):
            for channel in CHANNEL_WIDTHS:
                if channel not in pack['normal_samples'][slot]:
                    missing.append('MISSING_NORMAL:' + slot + ':' + channel)
        if pack['pre_reset'] is None:
            missing.append('MISSING_PRE_RESET_FLAGS')
        if actor is None:
            missing.append('ACTOR35_NOT_PROVIDED')
        if pack['reset'].get('outcome') == 'RAISED':
            missing.append('ORIGINAL_RESET_RAISED')
        if pack['normal_samples']['mid'] and pack['normal_samples']['end']:
            mid = next(iter(pack['normal_samples']['mid'].values()))['clock']
            end = next(iter(pack['normal_samples']['end'].values()))['clock']
            if end['physics_tick'] - mid['physics_tick'] != 4 or end['feedback_tick'] - mid['feedback_tick'] != 1:
                missing.append('NORMAL_PAIR_CLOCK_MISMATCH')
        if pack['reset']['callback_status'] == 'OBSERVED':
            pre, reset = pack['pre_reset'], pack['reset']
            if pre is None or reset['prior_termination_event_id'] != pre['event_id']:
                missing.append('RESET_WITHOUT_PRIOR_RETAINED_TERMINATION')
            elif (pre['clock']['physics_tick'], pre['clock']['feedback_tick']) != (
                    reset['clock']['physics_tick'], reset['clock']['feedback_tick']):
                missing.append('TERMINATION_RESET_CLOCK_UNJOINED')
        pack['retention_status'] = 'EXPECTED_FIELDS_RETAINED' if not missing else 'INCOMPLETE'
        pack['missing'] = missing
        pack['event_ids_are_clock'] = False
        pack['unknowns'] = dict(mid_remaining19='UNKNOWN_NOT_SAMPLED_AT_MID',
                                mid_full_clean35='UNKNOWN_NOT_COMPUTED', mid_actor35='UNKNOWN_50HZ_ONLY',
                                terminal_clean35='UNKNOWN_NOT_COMPUTED', nonwitness_episodes='UNKNOWN',
                                untapped_bitwise_actor='UNKNOWN', private_global_rng_states='UNKNOWN')
        self._packs.append(pack)
        self._open = None
        return pack

    def finish(self):
        _need(self._open is None, 'cannot finish with an open control')
        self._finished = True
        normal_count = sum(len(p['normal_samples'][s]) for p in self._packs for s in ('mid', 'end'))
        return dict(kind='BOUNDED_TYPED_CONTROL_LEDGER_V1', run_id=self.run_id,
                    requested_controls=self.controls, recorded_controls=len(self._packs),
                    control_cap=128, normal_channel_records=normal_count,
                    normal_record_cap=1280, all_controls_observed=len(self._packs) == self.controls,
                    controls=self._packs, scope='METADATA_RETENTION_NOT_INTERFACE_QUALIFICATION',
                    Gate1='UNKNOWN', stage2_GO=False)
