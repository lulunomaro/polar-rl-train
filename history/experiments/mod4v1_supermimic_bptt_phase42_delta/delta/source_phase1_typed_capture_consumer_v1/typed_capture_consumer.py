"""SOURCE-only decoded JSON checks. Producer adapter is bound only to its published ABI.
No I/O, target imports, hooks, tensors, coercive clock repair or admission.
The unchanged legacy module supplies complete original arithmetic/scalar helpers.
"""
import math
import capture_evidence_verifier_v1 as original

CHANNELS = {'base_ang_vel': 3, 'projected_gravity': 3, 'leg_pos': 4, 'leg_vel': 4, 'wheel_vel': 2}
GROUPS = {'legs': 4, 'wheels': 2}
QUEUE = ('lag_steps', 'episode', 'pending', 'pending_valid', 'issued_tick', 'due_tick',
         'applied', 'applied_valid', 'applied_issue_tick', 'first_apply_tick', 'last_submit_tick', 'last_apply_tick')
ROLES = ('ENV_ROWS_WITNESS', 'ENV_IDS_FULL', 'TERMINAL_BOOL_FULL', 'QUEUE_GROUP_FULL')
INT_DTYPES = {'torch.' + prefix + str(bits): ((0, 2**bits-1) if prefix == 'uint' else (-2**(bits-1), 2**(bits-1)-1))
              for prefix in ('int', 'uint') for bits in (8, 16, 32, 64)}
FLOAT_DTYPES = ('torch.float16', 'torch.bfloat16', 'torch.float32', 'torch.float64')
Missing = original.Missing
need = original.require
same = original.typed_equal
integer = original.integer


def get(obj, key):
    if type(obj) is not dict or key not in obj:
        raise Missing('missing field: ' + key)
    value = obj[key]
    if (type(value) is str and value.startswith('UNKNOWN')) or (type(value) is dict and value.get('status') == 'UNKNOWN'):
        raise Missing('explicit UNKNOWN: ' + key)
    return value


def builtins(value, depth=0):
    need(depth <= 64, 'decoded nesting exceeds 64')
    if value is None or type(value) in (str, int, bool):
        return
    if type(value) is float:
        need(math.isfinite(value), 'nonfinite decoded scalar')
    elif type(value) is list:
        for item in value:
            builtins(item, depth+1)
    elif type(value) is dict:
        need(all(type(key) is str for key in value), 'decoded keys must be exact strings')
        for item in value.values():
            builtins(item, depth+1)
    else:
        raise ValueError('only exact decoded JSON builtins')


digest = original.digest  # Whole original helper; canonical JSON uses its unchanged default ensure_ascii=True.


def clock(value):
    original.clock(value)  # Complete original B4 record clock; no coercion or repair.
    return value


def metadata_clock(value):
    need(type(value) is dict, 'original typed metadata clock dictionary required')
    for key in ('physics_tick', 'feedback_tick', 'common_control_counter', 'reset_depth'):
        integer(get(value, key), 0)
    need(type(get(value, 'phase')) is str, 'original metadata clock phase required')
    if 'sim_time_us' in value:
        need(integer(value['sim_time_us'], 0) == value['physics_tick']*2500, 'retained derived sim time differs')
    return value  # No sim_time_us/control_slot added when the producer did not retain them.


def adoption_clock(value):
    metadata_clock(value)
    need(value['phase'] == 'outside_scene_update' and value['reset_depth'] == 0
         and value.get('control_slot') == 'UNKNOWN' and value.get('is_original_100hz_slot') is False,
         'current SOURCE stored outside adoption clock differs; not an original event clock')
    return value


def _clock_equal(left, right):
    return all(same(left.get(key), right.get(key)) for key in
               ('physics_tick', 'feedback_tick', 'common_control_counter', 'phase', 'reset_depth',
                'sim_time_us', 'control_slot', 'is_original_100hz_slot'))


def _shape_values(value, shape, dtype):
    if shape:
        need(type(value) is list and len(value) == shape[0], 'retained values/shape mismatch')
        for item in value:
            _shape_values(item, shape[1:], dtype)
    elif dtype == 'torch.bool':
        need(type(value) is bool, 'original bool tensor became non-bool JSON scalar')
    elif dtype in INT_DTYPES:
        low, high = INT_DTYPES[dtype]
        need(type(value) is int and low <= value <= high, 'original integer dtype/value mismatch')
    elif dtype in FLOAT_DTYPES:
        need(type(value) is float and math.isfinite(value), 'original floating tensor needs finite float JSON values')
    else:
        raise Missing('unsupported original dtype: ' + str(dtype))


def tensor(envelope, *, role=None, shape=None, dtypes=None, witness=None, group=None, source_clock=None):
    need(type(envelope) is dict and envelope.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1',
         'explicit typed tensor envelope required; no bare-list fallback')
    semantic = get(envelope, 'semantic_role')
    need(type(semantic) is str and semantic in ROLES, 'unknown tensor semantic role')
    if role is not None:
        need(semantic == role, 'tensor role differs from explicit field contract')
    for key in ('source_ref', 'source_pin_ref', 'source_field', 'original_device', 'original_dtype'):
        need(type(get(envelope, key)) is str and bool(envelope[key]), 'nonempty tensor source metadata: ' + key)
    need(envelope['source_ref'] == envelope['source_pin_ref'], 'tensor source reference aliases differ')
    need(envelope.get('evidence_level') == 'OWNED_TENSOR_SNAPSHOT_NOT_SDK_PROVENANCE_QUALIFICATION', 'tensor scope label differs')
    src, kept = get(envelope, 'original_shape'), get(envelope, 'retained_shape')
    need(type(src) is list and type(kept) is list, 'original/retained shape lists required')
    for dimension in src + kept:
        integer(dimension, 0)
    if shape is not None:
        need(same(src, shape), 'original source shape differs')
    dtype = envelope['original_dtype']
    if dtypes is not None:
        need(dtype in dtypes, 'original field dtype differs')
    mapping = get(envelope, 'row_mapping')
    need(type(mapping) is dict, 'explicit original row mapping required')
    axis = get(envelope, 'source_env_axis')
    if semantic == 'ENV_IDS_FULL':
        need(axis is None and len(src) == 1 and src[0] <= 80 and same(src, kept) and dtype in INT_DTYPES,
             'full IDs are entire integer K0..80 argument, not an env-axis witness')
        need(mapping.get('kind') == 'VALUES_ARE_ENV_IDS_NOT_ENV_AXIS' and mapping.get('preserve_entire_argument') is True,
             'entire original ID argument mapping required')
        need(envelope.get('group') is None, 'IDs are not queue groups')
    else:
        integer(axis, 0)
        need(axis < len(src) and src[axis] == 80, 'explicit original env axis must be N80')
        ids = get(mapping, 'env_ids')
        need(type(ids) is list and all(type(i) is int and 0 <= i < 80 for i in ids)
             and len(set(ids)) == len(ids), 'explicit unique exact-int environment IDs required')
        need(type(mapping.get('env_axis')) is int and mapping['env_axis'] == axis, 'row mapping env axis differs')
        expected = list(src)
        if semantic == 'ENV_ROWS_WITNESS':
            need(1 <= len(ids) <= 8 and mapping.get('kind') == 'EXPLICIT_ORIGINAL_ENV_ROWS'
                 and mapping.get('index_binding') == 'CALLER_DECLARED_INDEX_BINDING_NOT_READBACK', 'witness mapping/scope differs')
            expected[axis] = len(ids)
            if witness is not None:
                need(same(ids, witness), 'explicit witness mapping changed')
            need(envelope.get('ownership') == 'OWNED_BY_INDEX_SELECT' and envelope.get('group') is None,
                 'witness ownership/group differs')
        else:
            need(same(ids, list(range(80))) and mapping.get('kind') == 'ALL_ENV_ROWS_IN_ORIGINAL_ORDER', 'full80 original-order mapping required')
            if semantic == 'TERMINAL_BOOL_FULL':
                need(src == [80] and axis == 0 and dtype == 'torch.bool' and envelope.get('group') is None, 'original bool[80] masks required')
            else:
                need(envelope.get('group') in GROUPS, 'full queue has explicit legs/wheels group')
                if group is not None:
                    need(envelope['group'] == group, 'full queue group differs')
        need(same(kept, expected), 'retained shape differs from explicit semantic role')
    if semantic != 'ENV_ROWS_WITNESS':
        need(envelope.get('ownership') == 'OWNED_BY_DETACH_CLONE', 'full semantic exception ownership differs')
    selection = 'ROWS_FROM_EXPLICIT_ROLE_NOT_SHAPE_INFERENCE' if semantic == 'ENV_ROWS_WITNESS' else 'FULL_SEMANTIC_EXCEPTION'
    need(envelope.get('selection') == selection, 'selection provenance differs')
    c = metadata_clock(get(envelope, 'source_clock'))
    if source_clock is not None:
        need(_clock_equal(c, source_clock), 'owned source clock differs from original record clock')
    values = get(envelope, 'values')
    _shape_values(values, kept, dtype)
    return values


def tree(value, stats):
    if type(value) is dict:
        if value.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1':
            tensor(value)
            key = value['semantic_role']
            stats[key] = stats.get(key, 0) + 1
            stats.setdefault('original_dtypes', set()).add(value['original_dtype'])
            if key == 'ENV_ROWS_WITNESS':
                stats.setdefault('witness_mappings', set()).add(tuple(value['row_mapping']['env_ids']))
            return
        for item in value.values():
            tree(item, stats)
    elif type(value) is list:
        for item in value:
            tree(item, stats)


def typed_metadata(*documents, expected_witness=None):
    stats = {}
    for doc in documents:
        tree(doc, stats)
    if not any(stats.get(role, 0) for role in ROLES):
        raise Missing('no original typed envelopes retained; projection is not a typed capture')
    mappings = stats.pop('witness_mappings', set())
    need(len(mappings) <= 1, 'ambiguous/mixed explicit witness row mappings')
    if expected_witness is not None:
        need(mappings == {tuple(expected_witness)}, 'current published producer declares witness IDs0..7; metadata differs')
    stats['witness_env_ids'] = list(next(iter(mappings))) if mappings else None
    stats['original_dtypes'] = sorted(stats.pop('original_dtypes', set()))
    stats['row_binding'] = 'DECLARED_INDEX_BINDING_NOT_READBACK'
    stats['tensor_bits_or_runtime_source_authenticated'] = False
    return stats


def rows(envelope, width=None, *, witness=None, source_clock=None, integer_values=False):
    shape = [80] if width is None else [80, width]
    types = tuple(INT_DTYPES) if integer_values else (FLOAT_DTYPES if width is not None else ('torch.bool',))
    return tensor(envelope, role='ENV_ROWS_WITNESS', shape=shape, dtypes=types,
                  witness=witness, source_clock=source_clock)


def _delay_cache(cache, width, witness):
    return {key: rows(get(cache, key), None if key in ('last', 'sample_tick', 'ready') else width,
                      witness=witness, integer_values=key in ('last', 'sample_tick'))
            for key in ('last', 'sample_tick', 'ready', 'cur', 'out')}


def feedback_record(record, memo):
    key, c = get(record, 'key'), clock(get(record, 'clock'))
    need(key in CHANNELS, 'five original feedback channels only')
    width = CHANNELS[key]
    clean_envelope = get(record, 'clean')
    clean = rows(clean_envelope, width, source_clock=c)
    ids = clean_envelope['row_mapping']['env_ids']
    n = len(ids)
    s, d = get(record, 'sensor_stage'), get(record, 'delay_stage')
    need(record.get('exception') is None, 'original feedback RAISED')
    need(record.get('full_clean35') == 'UNKNOWN_NOT_COMPUTED', 'clean16 was relabeled full clean35')
    episode = rows(get(s, 'episode'), witness=ids, integer_values=True, source_clock=c)
    before = get(s, 'before')
    need(same(rows(get(before, 'episode'), witness=ids, integer_values=True, source_clock=c), episode), 'sensor episode changed inside original apply')
    noisy_envelope = get(s, 'actual_noisy_return')
    noisy = rows(noisy_envelope, width, witness=ids, source_clock=c)
    profile = get(s, 'profile')
    repeated = 0
    if profile == 'off':
        need(same(noisy, clean), 'profile-off original value identity')
    else:
        need(profile == 'noise_bias_mild_v1', 'original sensor profile differs')
        noise_envelope = get(s, 'noise_used')
        noise = rows(noise_envelope, width, witness=ids, source_clock=c)
        bias_envelope = get(s, 'leg_bias_used') if key == 'leg_pos' else None
        bias = rows(bias_envelope, width, witness=ids, source_clock=c) if bias_envelope is not None else [[0.]*width for _ in ids]
        participants = [clean_envelope, noisy_envelope, noise_envelope] + ([bias_envelope] if bias_envelope is not None else [])
        if any(item['original_dtype'] != 'torch.float32' for item in participants) or s.get('dtype') != 'torch.float32':
            raise Missing('original dtypes retained; only source float32 left-associated arithmetic supported')
        last = rows(get(s, 'noise_cache_last'), witness=ids, source_clock=c, integer_values=True)
        need(same(last, [c['feedback_tick']]*n), 'noise cache tick differs')
        for i, env_id in enumerate(ids):
            expected = [original.f32(original.f32(a+b)+z) for a, b, z in zip(clean[i], noise[i], bias[i])]
            need(same(noisy[i], expected), 'float32 (clean+used_noise)+bias mismatch')
            identity = (key, env_id, episode[i], c['feedback_tick'])
            if identity in memo:
                repeated += 1
                need(same(memo[identity], noise[i]), 'same episode/tick noise changed')
            memo[identity] = noise[i]
    delay_input = rows(get(record, 'delay_actual_input'), width, witness=ids, source_clock=c)
    returned = rows(get(record, 'return'), width, witness=ids, source_clock=c)
    need(same(delay_input, noisy), 'original delay input differs from original noisy return')
    need(same(rows(get(d, 'actual_return'), width, witness=ids, source_clock=c), returned), 'original feedback/delay return mismatch')
    pre, post = get(d, 'before'), get(d, 'after')
    for state in (pre, post):
        need(same(rows(get(state, 'episode'), witness=ids, source_clock=c, integer_values=True), episode), 'sensor/delay episode differs')
    enabled = get(post, 'enabled')
    need(type(enabled) is bool and same(pre.get('enabled'), enabled), 'original delay enabled metadata differs')
    warmup = same_tick = 0
    if not enabled:
        need(same(returned, noisy), 'disabled delay changed original return')
    else:
        lag = rows(get(post, 'delay_steps'), witness=ids, source_clock=c, integer_values=True)
        need(same(lag, rows(get(pre, 'delay_steps'), witness=ids, source_clock=c, integer_values=True)) and all(x in (0, 1) for x in lag), 'original feedback delay0/1 changed')
        after = _delay_cache(get(post, 'cache'), width, ids)
        old_cache = pre.get('cache')
        absent = type(old_cache) is str and old_cache.startswith('UNKNOWN')
        old = ({'last': [-1]*n, 'sample_tick': [-1]*n, 'ready': [False]*n, 'cur': noisy, 'out': noisy}
               if absent else _delay_cache(get(pre, 'cache'), width, ids))
        need(same(returned, after['out']), 'original returned delayed selection differs')
        for i in range(n):
            last, fb = old['last'][i], c['feedback_tick']
            integer(last, -1)
            need(type(after['ready'][i]) is bool and type(old['ready'][i]) is bool, 'cache ready needs bool')
            if last == fb:
                same_tick += 1
                need(all(same(after[k][i], old[k][i]) for k in old), 'sameTick delay cache changed')
            else:
                need(last < 0 or last == fb-1, 'skipped/reversed feedback clock')
                warmup += int(last < 0)
                delayed = lag[i] == 1 and last >= 0
                need(same(after['cur'][i], noisy[i]) and type(after['last'][i]) is int and after['last'][i] == fb, 'fresh delay cache/input differs')
                need(same(after['out'][i], old['cur'][i] if delayed else noisy[i]), 'original cur/out selection differs')
                need(type(after['sample_tick'][i]) is int and after['sample_tick'][i] == (last if delayed else fb)
                     and after['ready'][i] is (last >= 0), 'original warmup/sample_tick/ready differs')
    return dict(channel=key, physics_tick=c['physics_tick'], feedback_tick=c['feedback_tick'],
                witness_rows=n, warmup_rows=warmup, sameTick_cache_rows=same_tick, sameTick_noise_rows=repeated)


def ledger_counts(ledger):
    need(ledger.get('kind') == 'BOUNDED_TYPED_CONTROL_LEDGER_V1', 'original ledger kind differs')
    need(type(get(ledger, 'run_id')) is str and bool(ledger['run_id']), 'original run identity required')
    requested = integer(get(ledger, 'requested_controls'))
    need(requested in (64, 128), 'original controls must be64/128')
    controls = get(ledger, 'controls')
    need(type(controls) is list and len(controls) <= requested, 'control packs exceed original request')
    need(integer(get(ledger, 'recorded_controls'), 0) == len(controls), 'recorded controls/count mismatch')
    need(type(ledger.get('all_controls_observed')) is bool and ledger['all_controls_observed'] is (len(controls) == requested), 'all-controls count claim differs')
    need(integer(get(ledger, 'control_cap')) == 128 and integer(get(ledger, 'normal_record_cap')) == 1280, 'published original ledger caps differ')
    normal_count = 0
    for index, pack in enumerate(controls):
        need(integer(get(pack, 'worker_control_index'), 0) == index, 'control packs are not original index0..C-1')
        normal = get(pack, 'normal_samples')
        need(type(normal) is dict and set(normal) == {'mid', 'end'}, 'original MID/END dictionaries required')
        for slot in ('mid', 'end'):
            need(type(normal[slot]) is dict and set(normal[slot]) <= set(CHANNELS), 'unknown normal slot/channel')
            normal_count += len(normal[slot])
        need(pack.get('retention_status') in ('EXPECTED_FIELDS_RETAINED', 'INCOMPLETE') and type(pack.get('missing')) is list,
             'original retention classification required')
        need(pack.get('event_ids_are_clock') is False, 'event identity was promoted to physics clock')
    need(integer(get(ledger, 'normal_channel_records'), 0) == normal_count <= 1280, 'normal channel record count differs')
    need(ledger.get('Gate1') == 'UNKNOWN' and ledger.get('stage2_GO') is False, 'ledger retention promoted to admission')
    return dict(requested_controls=requested, retained_controls=len(controls), normal_channel_records=normal_count,
                expected_normal_channel_records=10*requested, all_controls_retained=len(controls) == requested,
                full_clean16_scalar_width=16, counter_scope='COUNTS_NOT_SCIENCE_OR_ADMISSION')


def normal_science(ledger):
    memo, checked, missing = {}, 0, []
    warmup = same_tick = repeated = 0
    pairs = 0
    for pack in get(ledger, 'controls'):
        index = integer(get(pack, 'worker_control_index'), 0)
        begin = clock(get(pack, 'begin_clock'))
        normal = get(pack, 'normal_samples')
        slot_clocks = {}
        for slot in ('mid', 'end'):
            for key in CHANNELS:
                if key not in normal[slot]:
                    missing.append('normal:' + str(index) + ':' + slot + ':' + key)
                    continue
                record = normal[slot][key]
                c = clock(get(record, 'clock'))
                need(c['phase'] == 'scene_update' and c['reset_depth'] == 0 and c['is_original_100hz_slot'] is True
                     and c['control_slot'] == slot, 'reset-internal/non-normal call mislabeled MID/END')
                need(c['physics_tick'] == begin['physics_tick'] + (4 if slot == 'mid' else 8), 'original control/MID/END physics binding differs')
                if slot in slot_clocks:
                    need(_clock_equal(c, slot_clocks[slot]), 'five channels do not share original slot clock')
                slot_clocks[slot] = c
                payload = get(record, 'payload')
                need(payload.get('key') == key and _clock_equal(clock(get(payload, 'clock')), c), 'original channel payload identity/clock differs')
                integer(get(payload, 'call_id'), 1)
                actual = dict(payload, clean=get(record, 'clean'))
                try:
                    facts = feedback_record(actual, memo)
                except Missing as error:
                    missing.append(str(error))
                    continue
                checked += 1
                warmup += facts['warmup_rows']
                same_tick += facts['sameTick_cache_rows']
                repeated += facts['sameTick_noise_rows']
        if set(slot_clocks) == {'mid', 'end'}:
            need(slot_clocks['end']['physics_tick']-slot_clocks['mid']['physics_tick'] == 4
                 and slot_clocks['end']['feedback_tick']-slot_clocks['mid']['feedback_tick'] == 1, 'original normal pair not4physics/1feedback ticks')
            pairs += 1
    return dict(_status='UNKNOWN' if missing else 'CONSISTENT', checked_channel_records=checked, control_MID_END_pairs=pairs,
                warmup_witness_rows=warmup, sameTick_cache_witness_rows=same_tick, sameTick_noise_witness_rows=repeated,
                sameTick_edge='OBSERVED' if same_tick or repeated else 'NOT_OBSERVED',
                missing_count=len(missing), first_missing=missing[:8],
                arithmetic='ORIGINAL_FLOAT32_LEFT_ASSOCIATED_(clean+noise)+bias_DECODED_VALUES_NOT_BITS',
                no_full_clean35_or_MID19_inferred=True)


def _reset_episode_state(before, after, ids):
    witness = get(get(before, 'sensor_episode'), 'row_mapping')['env_ids']
    for key in ('sensor_episode', 'delay_episode'):
        old = rows(get(before, key), witness=witness, integer_values=True)
        new = rows(get(after, key), witness=witness, integer_values=True)
        need(same(new, [value + int(env_id in ids) for value, env_id in zip(old, witness)]), 'partial reset episode/witness membership differs')
    before_cache, after_cache = get(before, 'queue'), get(after, 'queue')
    need(type(before_cache) is dict and type(after_cache) is dict and set(before_cache) == set(after_cache), 'reset feedback cache key set differs')
    for key, old_cache in before_cache.items():
        need(key in CHANNELS, 'unknown reset feedback channel')
        old = _delay_cache(old_cache, CHANNELS[key], witness)
        new = _delay_cache(after_cache[key], CHANNELS[key], witness)
        for field in old:
            for i, env_id in enumerate(witness):
                expected = ((-1 if field in ('last', 'sample_tick') else False)
                            if env_id in ids and field in ('last', 'sample_tick', 'ready') else old[field][i])
                need(same(new[field][i], expected), 'partial reset changed unselected/stale feedback state')


def boundaries(ledger, pending=None):
    counts = dict(pre_physical_endpoints=0, post_return_actor_END=0, observed_reset_callbacks=0,
                  no_reset_callbacks=0, observed_metadata_failed=0, raised_reset_callbacks=0,
                  joined_reset_edges=0, late_or_unjoined=0, natural_preterminal_env_rows=0)
    missing = []
    for pack in get(ledger, 'controls'):
        c = clock(get(pack, 'begin_clock'))
        expected_end = c['physics_tick']+8
        pre, reset, post = pack.get('pre_reset'), get(pack, 'reset'), pack.get('post_return')
        provenance = get(pack, 'b3_callback_provenance')
        terminal_calls = integer(get(provenance, 'original_terminal_callbacks'), 0)
        reset_calls = integer(get(provenance, 'original_reset_callbacks'), 0)
        errors = integer(get(provenance, 'observer_error_count'), 0)
        observation = get(provenance, 'reset_observation')
        need(observation in ('NOT_OBSERVED', 'OBSERVED_WITH_OWNED_IDS', 'OBSERVED_METADATA_FAILED'), 'unknown original callback observation class')
        need((reset_calls == 0) is (observation == 'NOT_OBSERVED'), 'no callback confused with metadata failure')
        if errors or terminal_calls != 1 or reset_calls > 1:
            missing.append('original callback count/metadata incomplete')
        flags = None
        if pre is None:
            missing.append('pre-reset original physical S1/flags NOT_OBSERVED')
        else:
            pc = clock(get(pre, 'clock'))
            need(pc['physics_tick'] == expected_end and pc['phase'] == 'outside_scene_update' and pc['reset_depth'] == 0, 'prephysical endpoint is not original before-reset END clock')
            term = tensor(get(pre, 'term'), role='TERMINAL_BOOL_FULL', source_clock=pc)
            trunc = tensor(get(pre, 'trunc'), role='TERMINAL_BOOL_FULL', source_clock=pc)
            flags = [a or b for a, b in zip(term, trunc)]
            state = rows(get(get(pre, 'payload'), 'state'), 73, source_clock=pc)
            need(len(state) >= 1, 'prephysical S1 witness absent')
            counts['pre_physical_endpoints'] += 1
            counts['natural_preterminal_env_rows'] += sum(flags)
        status = reset.get('callback_status')
        need(status in ('NOT_OBSERVED', 'OBSERVED'), 'unknown ledger reset callback status')
        if observation == 'NOT_OBSERVED':
            counts['no_reset_callbacks'] += 1
            need(status == 'NOT_OBSERVED' and reset.get('ids') is None, 'no callback was fabricated as empty reset IDs')
        elif observation == 'OBSERVED_METADATA_FAILED':
            counts['observed_metadata_failed'] += 1
            missing.append('original reset callback OBSERVED_METADATA_FAILED')
        else:
            counts['observed_reset_callbacks'] += 1
            need(reset_calls == 1 and status == 'OBSERVED', 'owned reset callback not retained')
            rc = clock(get(reset, 'clock'))
            ids = tensor(get(reset, 'ids'), role='ENV_IDS_FULL', source_clock=rc)
            need(len(ids) == len(set(ids)) and all(type(i) is int and 0 <= i < 80 for i in ids), 'original reset IDs values/range/uniqueness differ')
            outcome = get(reset, 'outcome')
            need(outcome in ('RETURNED', 'RAISED'), 'original reset outcome required')
            if outcome == 'RAISED':
                counts['raised_reset_callbacks'] += 1
                missing.append('original reset RAISED; remaining partial state not completed reset')
            elif pre is None or reset.get('prior_termination_event_id') != pre.get('event_id'):
                counts['late_or_unjoined'] += 1
                missing.append('reset prior termination absent/late; not repaired')
            else:
                pc = pre['clock']
                if (rc['physics_tick'], rc['feedback_tick']) != (pc['physics_tick'], pc['feedback_tick']):
                    counts['late_or_unjoined'] += 1
                    missing.append('original termination/reset clocks unjoined')
                else:
                    need(set(ids) == {i for i, flag in enumerate(flags) if flag}, 'full80 original preflags/reset IDs disagree')
                    _reset_episode_state(get(reset, 'before'), get(reset, 'after'), set(ids))
                    counts['joined_reset_edges'] += 1
        if post is None:
            missing.append('original post-return END NOT_OBSERVED')
        else:
            pc = clock(get(post, 'clock'))
            need(pc['physics_tick'] == expected_end and pc['control_slot'] == 'end' and pc['phase'] == 'outside_scene_update' and pc['reset_depth'] == 0, 'returned actor/flags are not original END')
            tensor(get(post, 'term'), role='TERMINAL_BOOL_FULL', source_clock=pc)
            tensor(get(post, 'trunc'), role='TERMINAL_BOOL_FULL', source_clock=pc)
            try:
                rows(get(post, 'actor35_original_buffer'), 35, source_clock=pc)
                counts['post_return_actor_END'] += 1
            except Missing as error:
                missing.append(str(error))
        if missing and pack.get('retention_status') == 'EXPECTED_FIELDS_RETAINED':
            local_problems = errors or terminal_calls != 1 or reset_calls > 1 or observation == 'OBSERVED_METADATA_FAILED'
            need(not local_problems, 'producer claimed complete while original callback metadata failed')
    if pending is not None:
        need(type(pending) is dict and pending.get('kind') == 'B3_INCOMPLETE_OWNED_CONTROL' and pending.get('retention_status') == 'INCOMPLETE', 'original incomplete-current-control contract differs')
        missing.append('open/END-missing original control retained separately, not synthesized')
    return dict(_status='UNKNOWN' if missing else 'CONSISTENT', **counts, missing_count=len(missing), first_missing=missing[:8],
                natural_reset_edge='OBSERVED' if counts['joined_reset_edges'] and counts['natural_preterminal_env_rows'] else 'NOT_OBSERVED',
                post_flags_not_replaced_by_pre_flags=True, MID19='UNKNOWN_NOT_SAMPLED_AT_MID',
                untapped_actor_counterfactual='UNKNOWN')


def _arg(event, index, name):
    args = event.get('args')
    if type(args) is list and len(args) > index:
        return args[index]
    return get(get(event, 'kwargs'), name)


def _queue(event_state, group, adoption_clock):
    width = GROUPS[group]
    values = {}
    for field in QUEUE:
        shape = [80, width] if field in ('pending', 'applied') else [80]
        dtype = 'torch.float32' if len(shape) == 2 else 'torch.bool' if field.endswith('valid') else 'torch.int64'
        values[field] = tensor(get(event_state, field), role='QUEUE_GROUP_FULL', shape=shape,
                               dtypes=(dtype,), group=group, source_clock=adoption_clock)
    need(all(x in (0, 1, 2) for x in values['lag_steps']), 'original physics lag must be0/1/2')
    need(all(x >= 0 for x in values['episode']), 'queue episode negative')
    for field in QUEUE:
        if field not in ('lag_steps', 'episode', 'pending', 'applied', 'pending_valid', 'applied_valid'):
            need(all(x >= -1 for x in values[field]), 'queue tick metadata below original -1 sentinel')
    return values


def _windows(actuation, controls):
    need(get(actuation, 'capture_schema') == 'PHASE1_TYPED_C2_EVENT_WINDOWS_V1', 'published typed C2 container capture_schema differs')
    trace = get(actuation, 'windows')
    need(get(trace, 'retention') == 'ORIGINAL_FIRST2_LAST2_NOT_ALL_C2_WINDOWS' and
         trace.get('middle_windows') == 'UNKNOWN_UNRETAINED', 'original bounded C2 retention claim differs')
    need(integer(get(trace, 'control_windows_seen'), 0) == controls and integer(get(trace, 'retained_window_bound')) == 4,
         'typed C2 retention counters differ')
    windows = {}
    for name in ('first', 'last'):
        items = get(trace, name)
        need(type(items) is list and len(items) <= 2, 'C2 first2/last2 bound differs')
        for item in items:
            idx = integer(get(item, 'control_index'), 0)
            need(idx < controls, 'typed window control index out of range')
            need(idx not in windows or same(windows[idx], item), 'duplicate retained window differs')
            windows[idx] = item
    if not windows:
        raise Missing('no retained C2 window')
    return windows


def actuation_domains(actuation, controls):
    windows = _windows(actuation, controls)
    physics = nonterm = mismatch = context = raised = 0
    for window in windows.values():
        adoption = adoption_clock(get(window, 'adoption_clock'))
        need(adoption['phase'] == 'outside_scene_update' and adoption['reset_depth'] == 0, 'C2 adoption clock must be CONTROL-OUTSIDE, not event physics clock')
        events = get(window, 'events')
        need(type(events) is list and len(events) <= 8192, 'C2 original event list/cap8192 required')
        seqs = [integer(get(e, 'seq'), 0) for e in events]
        need(seqs == sorted(set(seqs)), 'C2 original sequence must be sorted unique exact ints')
        terms = {e['seq']: e for e in events if e.get('kind') == 'term_apply'}
        for event in events:
            need(event.get('capture_schema') == 'ACTUATION_CLOCK_SCOPE_V2_SOURCE_DISABLED', 'unmodified C2 core source tag differs')
            kind = get(event, 'kind')
            need(kind in ('issue', 'queue_submit', 'queue_apply', 'term_apply', 'target_write'), 'unknown original C2 event kind')
            need(same(adoption_clock(get(event, 'adoption_clock')), adoption), 'event outside adoption clock differs from window, not a physics substitute')
            if kind != 'target_write':
                expected_source = ('original_queue_argument_UNVALIDATED' if kind in ('queue_submit', 'queue_apply') else
                                   'original_term_entry_stored_counter_minus_one_UNVALIDATED' if kind == 'term_apply' else 'stored_counter')
                need(get(event, 'clock_source') == expected_source and event.get('write_scope') == 'NOT_A_SETTER', 'original physics clock source/scope differs')
            need(event.get('outcome') in ('RETURNED', 'RAISED'), 'original C2 outcome missing')
            raised += int(event['outcome'] == 'RAISED')
            if kind == 'target_write':
                scope = get(event, 'write_scope')
                setter = get(event, 'setter')
                need(type(get(setter, 'method')) is str and setter.get('joint_ids_source') in
                     ('kwargs.joint_ids', 'positional[1]_UNQUALIFIED_SDK_SIGNATURE', 'OMITTED'), 'original setter provenance required')
                if scope in ('NON_TERM_SETTER', 'ACTIVE_TERM_ASSET_MISMATCH'):
                    tick = event.get('tick')
                    expected = 'NOT_APPLICABLE' if scope == 'NON_TERM_SETTER' else 'UNKNOWN'
                    need(type(tick) is dict and tick.get('status') == expected and event.get('parent_term_apply_seq') is None,
                         'unparented/mismatched setter cannot claim physics tick or parent')
                    need(type(event.get('group')) is dict and event['group'].get('status') == 'UNKNOWN'
                         and event.get('clock_source') == 'NO_QUALIFIED_PHYSICS_CLOCK', 'unparented setter cannot claim queue group')
                    need('raw_stored_counter' in event, 'unparented raw counter lost')
                    nonterm += int(scope == 'NON_TERM_SETTER')
                    mismatch += int(scope == 'ACTIVE_TERM_ASSET_MISMATCH')
                    continue  # Different declared domain; no synthetic counter-1 and no event deletion.
                need(scope == 'SAME_ASSET_TERM_APPLY_CONTEXT' and event.get('clock_source') == 'original_parent_term_context', 'unknown original setter clock scope/source')
                parent_seq = integer(get(event, 'parent_term_apply_seq'), 0)
                if parent_seq not in terms:
                    raise Missing('qualified setter parent not retained')
                parent = terms[parent_seq]
                need(parent_seq < event['seq'] and same(event.get('group'), parent.get('group'))
                     and same(event.get('tick'), parent.get('tick')), 'original dynamic parent scope differs')
                active = get(event, 'active_term_context')
                need(same(active, {key: parent[key] for key in ('seq', 'group', 'tick')}), 'stored active term context differs')
                context += 1
            tick = integer(get(event, 'tick'), 0)  # Every actual physics domain remains strict.
            group = get(event, 'group')
            need(type(group) is str and group in GROUPS, 'original physics group differs')
            if kind in ('issue', 'term_apply'):
                counter = integer(get(event, 'raw_stored_counter'), 0)
                need(counter == tick + int(kind == 'term_apply'), 'stored counter/event clock source differs')
            if kind in ('queue_submit', 'queue_apply'):
                need(type(_arg(event, 0, 'key')) is str and _arg(event, 0, 'key') == group, 'original queue key differs')
                arg_tick = integer(_arg(event, 2 if kind == 'queue_submit' else 1, 'tick'), 0)
                need(arg_tick == tick, 'original queue argument tick differs')
            physics += 1
    return dict(_status='UNKNOWN' if raised else 'CONSISTENT', retained_control_indices=sorted(windows),
                actual_physics_clock_records=physics, NON_TERM_SETTER_records=nonterm,
                ACTIVE_TERM_ASSET_MISMATCH_records=mismatch, SAME_ASSET_TERM_APPLY_CONTEXT_records=context,
                raised_original_callbacks=raised, source_clock='OUTSIDE_ADOPTION_METADATA_NOT_EVENT_PHYSICS_CLOCK',
                DOF_target_join='UNKNOWN_MISSING_ORIGINAL_TERM_JOINT_IDS_AND_ACTUAL_SETTER_BINDING',
                records_filtered_or_clock_repaired=0, physical_readback='UNKNOWN')


def queue_science(actuation, controls, ledger):
    status = get(actuation, 'status')
    need(integer(get(status, 'dropped_events'), 0) == 0 and integer(get(status, 'observer_errors'), 0) == 0
         and get(status, 'missing_hooks') == [] and get(status, 'restore_conflicts') == [], 'original C2 capture loss/error')
    windows = _windows(actuation, controls)
    endpoints, latency, ages = {}, {g: set() for g in GROUPS}, {g: [] for g in GROUPS}
    context_values_equal = context_values_other = 0
    for idx, window in sorted(windows.items()):
        adoption, events = adoption_clock(get(window, 'adoption_clock')), get(window, 'events')
        for event in events:
            if event.get('outcome') == 'RAISED':
                raise Missing('original C2 callback RAISED; state is partial, not a completed transition')
        for group, width in GROUPS.items():
            es = [e for e in events if e.get('group') == group]
            issues = [e for e in es if e.get('kind') == 'issue']
            submits = [e for e in es if e.get('kind') == 'queue_submit']
            if len(issues) != 1 or len(submits) != 1:
                raise Missing('one original issue and submit per retained group/window required')
            issue, submit = issues[0], submits[0]
            start = integer(get(submit, 'tick'), 0)
            need(integer(get(issue, 'tick'), 0) == start and integer(get(issue, 'seq'), 0) < integer(get(submit, 'seq'), 0), 'original process/submit scope differs')
            packs = get(ledger, 'controls')
            if idx < len(packs):
                need(start == clock(get(packs[idx], 'begin_clock'))['physics_tick'], 'retained C2 submit/typed control begin clocks differ')
            before = _queue(get(submit, 'pre'), group, adoption)
            after = _queue(get(submit, 'post'), group, adoption)
            target = tensor(_arg(submit, 1, 'x'), role='QUEUE_GROUP_FULL', shape=[80, width],
                            dtypes=('torch.float32',), group=group, source_clock=adoption)
            for row in range(80):
                need(before['last_submit_tick'][row] < 0 or start-before['last_submit_tick'][row] == 8, '20ms original submit clock')
                need(before['last_apply_tick'][row] < start and before['pending_valid'][row] is False, 'submit after apply/unconsumed original command')
                expected = {key: before[key][row] for key in QUEUE}
                expected.update(pending=target[row], pending_valid=True, issued_tick=start,
                                due_tick=start+before['lag_steps'][row], last_submit_tick=start)
                need(all(same(after[key][row], expected[key]) for key in QUEUE), 'full80 original submit transition differs')
            need(same(_queue(get(issue, 'post'), group, adoption), after), 'original issue does not enclose original submit')
            applies = sorted((e for e in es if e.get('kind') == 'queue_apply'), key=lambda e: integer(get(e, 'tick'), 0))
            if [e['tick'] for e in applies] != list(range(start, start+8)):
                raise Missing('exactly eight natural retained apply ticks required; not synthesized')
            previous = after
            for apply in applies:
                tick = integer(get(apply, 'tick'), 0)
                before, after = _queue(get(apply, 'pre'), group, adoption), _queue(get(apply, 'post'), group, adoption)
                need(same(before, previous), 'original submit/apply chain discontinuity')
                previous = after
                selected = tensor(get(apply, 'selected_target'), role='QUEUE_GROUP_FULL', shape=[80, width],
                                  dtypes=('torch.float32',), group=group, source_clock=adoption)
                need(same(selected, after['applied']), 'original selected_target differs from stored applied')
                terms = [e for e in es if e.get('kind') == 'term_apply' and same(e.get('tick'), tick)]
                if len(terms) != 1:
                    raise Missing('one retained original term context per natural apply tick required')
                term = terms[0]
                need(integer(get(term, 'seq'), 0) < integer(get(apply, 'seq'), 0)
                     and same(_queue(get(term, 'pre'), group, adoption), before)
                     and same(_queue(get(term, 'post'), group, adoption), after), 'original term context does not enclose queue transition')
                for writer in (e for e in es if e.get('kind') == 'target_write' and same(e.get('parent_term_apply_seq'), term['seq'])):
                    # No DOF binding: auxiliary same-asset setters remain ambiguous rather than being reclassified as physical writes.
                    arg = _arg(writer, 0, 'target')
                    if (type(arg) is dict and arg.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1'
                            and same(arg.get('original_shape'), [80, width])):
                        actual = tensor(arg, role='QUEUE_GROUP_FULL', group=group, source_clock=adoption)
                        context_values_equal += int(same(actual, selected))
                        context_values_other += int(not same(actual, selected))
                    else:
                        context_values_other += 1
                for row in range(80):
                    need(before['last_apply_tick'][row] < 0 or before['last_apply_tick'][row] == tick-1, '400Hz original natural apply clock')
                    select = before['pending_valid'][row] and before['due_tick'][row] <= tick
                    expected = {key: before[key][row] for key in QUEUE}
                    expected['last_apply_tick'] = tick
                    if select:
                        need(before['due_tick'][row] == tick, 'original late first application')
                        expected.update(applied=before['pending'][row], applied_valid=True,
                                        applied_issue_tick=before['issued_tick'][row], first_apply_tick=tick, pending_valid=False)
                    need(all(same(after[key][row], expected[key]) for key in QUEUE), 'full80 original apply/held transition differs')
                    if after['applied_valid'][row]:
                        first = after['first_apply_tick'][row]-after['applied_issue_tick'][row]
                        age = tick-after['applied_issue_tick'][row]
                        need(first == after['lag_steps'][row] and age >= first, 'first latency confused with held command age')
                        latency[group].add(first*2500)
                        ages[group].append(age*2500)
            endpoints[idx, group] = (_queue(get(submit, 'pre'), group, adoption), previous)
    reset_rows = 0
    for idx in sorted(windows):
        if idx+1 not in windows:
            continue
        for group in GROUPS:
            old, new = endpoints[idx, group][1], endpoints[idx+1, group][0]
            for row in range(80):
                delta = new['episode'][row]-old['episode'][row]
                if delta == 0:
                    need(all(same(new[key][row], old[key][row]) for key in QUEUE), 'unselected original queue row changed across adjacent edge')
                elif delta == 1:
                    reset_rows += 1
                    need(new['pending_valid'][row] is False and new['applied_valid'][row] is False, 'original partial reset retained stale validity')
                    need(all(new[key][row] == -1 for key in ('issued_tick', 'due_tick', 'applied_issue_tick', 'first_apply_tick', 'last_submit_tick'))
                         and new['last_apply_tick'][row] == old['last_apply_tick'][row], 'original reset rebased clock/stale issue metadata')
                else:
                    raise Missing('unobserved/multiple queue episode transitions')
    return dict(retained_control_indices=sorted(windows), not_all_controls_retained=len(windows) < controls,
                middle_control_windows='UNKNOWN_NOT_RETAINED', full80_group_widths=dict(GROUPS),
                first_transition_latency_us={g: sorted(v) for g, v in latency.items()},
                max_held_age_us={g: max(v) if v else None for g, v in ages.items()}, adjacent_queue_reset_rows=reset_rows,
                context_argument_value_equal_observations=context_values_equal,
                other_ambiguous_context_argument_observations=context_values_other,
                DOF_target_join='UNKNOWN_NOT_ESTABLISHED_BY_CONTEXT_OR_ARGUMENT_VALUE_EQUALITY',
                physical_readback='UNKNOWN', private_global_RNG='UNKNOWN')


ABI = 'PHASE1_TYPED_NATIVE_PRODUCER_ABI_V1'
INTEGRATION = 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1'
TASK_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_TASK_V1'
FINAL_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_FINAL_V1'
CONSUMER_SCHEMA = 'PHASE1_TYPED_CAPTURE_CONSUMER_SOURCE_V1'


def task_contract(task):
    expected = dict(kind=TASK_KIND, purpose=original.PURPOSE, batch_purpose=original.PURPOSE,
                    integration=INTEGRATION, typed_producer_schema=ABI, policy_variant=original.POLICY, role='E3', requested_roles=['E3'],
                    role_catalog=original.ROLES, num_envs=80, seed=20260928, model_PT_reads=0,
                    synthetic_action=[0., 0., 0., 0., 0., 0.], train=False, quality_evaluation=False,
                    full_clean35='UNKNOWN', physics=original.PHYSICS,
                    asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',
                    contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755')
    for key, value in expected.items():
        need(same(get(task, key) if value != 'UNKNOWN' else task.get(key), value), 'typed task differs: ' + key)
    count = integer(get(task, 'controls'))
    need(count in (64, 128), 'typed task controls64/128')
    need(all(task.get(k) is None for k in ('overall_eight_pass_rate', 'comparison')), 'no task skill promotion')
    need(not any(k in task for k in ('teacher_path', 'source_path', 'checkpoint', 'a1_producer')), 'no model fallback')
    need(type(get(task, 'group_id')) is str and bool(task['group_id']) and type(get(task, 'GPU_UUID')) is str, 'original task group/GPU strings')
    original.number(get(task, 'absolute_worker_deadline_epoch'))
    return dict(controls=count, N=80, seed=20260928, runtime_source_authentication='UNKNOWN')


def final_contract(final, task):
    expected = dict(kind=FINAL_KIND, purpose=original.PURPOSE, integration=INTEGRATION,
                    typed_producer_schema=ABI, role='E3', num_envs=80, policy_variant=original.POLICY,
                    actor35_source='ORIGINAL_RETURNED_POLICY_BUFFER', clean16_only=True, full_clean35='UNKNOWN',
                    model_PT_reads=0, training_updates=0, optimizer_updates=0, learner_created=False,
                    replay_created=False, teacher_created=False, gate1='UNKNOWN', exact=False,
                    capture_interface_passed=False, paper_ready=False, stage2_GO=False)
    for key, value in expected.items():
        need(same(final.get(key), value), 'typed FINAL source/scope field: ' + key)
    for key in ('sensor', 'actuation', 'boundary', 'coverage', 'rng_counts', 'restore', 'original_setup', 'inconclusive_reasons'):
        get(final, key)
    need(all(final.get(key) is None for key in ('skill_success_rate', 'overall_eight_pass_rate', 'reference_comparison')), 'no FINAL skill promotion')
    need(type(get(final, 'passed_execution')) is bool, 'exact bool original execution claim')
    sensor = get(final, 'sensor')
    need(sensor.get('kind') == 'PASSIVE_SENSOR_CAPTURE_V3' and sensor.get('native_enabled') is False
         and sensor.get('exact') is False and sensor.get('metadata_retention_is_not_native_admission') is True,
         'original B4 report/source labels were replaced')
    ledger = get(sensor, 'control_ledger')
    need(integer(get(final, 'controls'), 0) == integer(get(ledger, 'recorded_controls'), 0)
         and integer(get(final, 'requested_controls')) == integer(get(ledger, 'requested_controls')), 'original worker/ledger count binding differs')
    pending = sensor.get('incomplete_current_control')
    if 'typed_pending_control' in final:
        need(same(final['typed_pending_control'], pending), 'typed pending alias differs from original B4 pending object')
    if task is None:
        raise Missing('whole original new TASK absent; FINAL/task identity UNKNOWN')
    need(final.get('group_id') == task.get('group_id') and final.get('GPU_UUID') == task.get('GPU_UUID'), 'original FINAL/task identity differs')
    need(get(ledger, 'run_id') == task['group_id']+':E3', 'whole original ledger run_id binding differs')
    return dict(schema=ABI, original_B4_pending_preserved=True, active_runtime_binding='UNKNOWN')


def provenance_contract(provenance, documents):
    records = get(provenance, 'whole_documents')
    for name, value in documents.items():
        pin = get(records, name)
        integer(get(pin, 'original_bytes'), 1)
        need(original.hexsha(get(pin, 'original_SHA256')), 'original-byte SHA256 syntax: ' + name)
        need(get(pin, 'decoded_canonical_SHA256') == digest(value), 'decoded canonical whole-document digest differs: ' + name)
    claims = provenance.get('schema_source_pins', provenance.get('reported_source_pins'))
    if claims is not None:
        need(type(claims) is dict, 'reported source pin mapping required')
        for name, pin in claims.items():
            need(type(name) is str and type(pin) is dict, 'reported source pin shape')
            integer(get(pin, 'bytes'), 1)
            need(original.hexsha(get(pin, 'SHA256')), 'reported source SHA syntax')
    return dict(documents=sorted(documents), source_pin_claims=0 if claims is None else len(claims),
                original_byte_proofs='CALLER_SUPPLIED_IDENTITIES_NOT_RECOMPUTED_OR_AUTHENTICATED',
                decoded_canonical='UNCHANGED_ORIGINAL_DIGEST_HELPER_NOT_ORIGINAL_BYTE_SHA',
                reported_pins_runtime_source_authentication='UNKNOWN_EXTERNAL_EXACT_SOURCE_AND_BYTE_BINDING',
                tensor_source_ref_resolution='UNKNOWN_CALLER_CLAIMS_NOT_AUTOMATICALLY_AUTHENTICATED')


def lifecycle_contract(lifecycle, task, final, provenance):
    gf, scope, grade = (get(lifecycle, k) for k in ('group_final', 'parent_exit_scope', 'source_grade'))
    need(gf.get('kind') == 'PHASE1_TYPED_NATIVE_CAPTURE_GROUP_FINAL_V1' and gf.get('purpose') == original.PURPOSE
         and gf.get('integration') == INTEGRATION, 'new typed group FINAL source differs')
    need(gf.get('group_id') == task.get('group_id') and gf.get('requested_roles') == ['E3']
         and gf.get('deferred_roles') == original.ROLES[1:] and gf.get('passed_execution') is True, 'typed group membership/execution differs')
    terminal = get(gf, 'terminal')
    need(type(terminal) is list and len(terminal) == 1, 'whole group has one original terminal')
    row = terminal[0]
    pid = integer(get(row, 'pid'), 1)
    need(row.get('role') == 'E3' and row.get('GPU_UUID') == task.get('GPU_UUID')
         and integer(get(row, 'returncode')) == 0 and row.get('actual_waited') is True, 'original child waited identity differs')
    need(all(row.get(k) is True for k in ('ready', 'started', 'pre_close', 'passed_execution')) and row.get('error') is None, 'original child closure incomplete')
    need(same(get(row, 'data'), final), 'whole original terminal.data differs from whole worker FINAL; projection rejected')
    semantic = get(row, 'semantic')
    need(semantic.get('kind') == 'PHASE1_TYPED_NATIVE_WAITED_EXECUTION_SEMANTICS_V1'
         and semantic.get('purpose') == original.PURPOSE and semantic.get('passed_execution') is True
         and semantic.get('errors') == [] and semantic.get('actual_wait_call_attested_by_caller') is True, 'new typed child wait semantics differs')
    waited_epoch = original.number(get(semantic, 'waited_return_observed_epoch'))
    need(scope.get('all_own_children_waited') is True and scope.get('original_single_GPU_private_EX_released') is True
         and scope.get('original_global_finite_EX_released') is True and scope.get('no_foreign_scope_touched') is True
         and integer(get(scope, 'canonical_writes')) == 0 and scope.get('errors') == [], 'original waits/EX/finally incomplete')
    waits = get(scope, 'child_waits')
    need(type(waits) is list and len(waits) == 1, 'one original finally child wait')
    need(waits[0].get('role') == 'E3' and same(waits[0].get('pid'), pid)
         and integer(get(waits[0], 'returncode')) == 0 and waits[0].get('actual_waited') is True, 'original finally wait linkage differs')
    need(grade.get('kind') == 'PHASE1_TYPED_NATIVE_CLOSED_SOURCE_GRADE_V1' and grade.get('purpose') == original.PURPOSE
         and grade.get('passed_closed_capture_execution') is True and grade.get('errors') == [], 'new typed closed source grade differs')
    for doc in (gf, grade):
        need(doc.get('gate1') == 'UNKNOWN' and doc.get('exact') is False and doc.get('stage2_GO') is False
             and doc.get('capture_interface_passed') is False, 'lifecycle was promoted to interface/admission')
    go, ready, started = (get(lifecycle, k) for k in ('common_go', 'worker_ready', 'worker_started'))
    need(go.get('kind') == 'PHASE1_TYPED_NATIVE_CAPTURE_COMMON_START_V1' and go.get('purpose') == original.PURPOSE
         and go.get('group_id') == task.get('group_id') and go.get('members') == ['E3'] and go.get('stage2_GO') is False, 'new typed common GO differs')
    for doc in (ready, started):
        need(doc.get('kind') == INTEGRATION and doc.get('role') == 'E3', 'new typed ready/start integration differs')
    setup = get(final, 'original_setup')
    epochs = [original.number(get(setup, 'started_epoch')), original.number(get(ready, 'epoch')),
              original.number(get(go, 'epoch')), original.number(get(started, 'epoch')),
              original.number(get(setup, 'first_control_epoch')), original.number(get(setup, 'last_control_epoch')),
              waited_epoch, original.number(get(gf, 'terminal_epoch')), original.number(get(scope, 'epoch'))]
    need(epochs == sorted(epochs), 'original closure timestamp order differs')
    for doc in (started, setup, gf):
        need(same(doc.get('GO_epoch'), go['epoch']), 'original common GO timestamp differs')
    need(get(get(lifecycle, 'env_close'), 'closed') is True, 'original env close did not return')
    binding = get(lifecycle, 'app_close_binding')
    need(type(get(binding, 'fast_shutdown')) is bool, 'exact original App close mode required')
    if binding['fast_shutdown']:
        intent = get(lifecycle, 'app_fast_intent')
        pin = get(get(provenance, 'whole_documents'), 'worker_final')
        need(intent.get('kind') == 'PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1' and same(intent.get('binding'), binding)
             and intent.get('original_env_close_returned') is True, 'original pinned fast close intent differs')
        need(same(intent.get('final_bytes'), get(pin, 'original_bytes')) and intent.get('final_SHA') == get(pin, 'original_SHA256'),
             'fast intent must bind original bytes, not decoded canonical SHA')
    else:
        returned = get(lifecycle, 'app_close_returned')
        need(returned.get('returned') is True and same(returned.get('binding'), binding), 'original actual App close return differs')
    need(not lifecycle.get('worker_error') and not lifecycle.get('parent_error'), 'published original worker/parent error')
    return dict(child_waits=1, two_EX_released=True, original_env_close_returned=True,
                closure_scope='DECODED_PUBLISHED_ORIGINAL_LIFECYCLE_NOT_RUNTIME_AUTHENTICATION',
                App_binding_full_SDK_provenance='UNKNOWN')


def _check(name, fn):
    try:
        detail = fn()
        status = detail.pop('_status', 'CONSISTENT') if type(detail) is dict else 'CONSISTENT'
        return dict(check=name, status=status, detail=detail)
    except Missing as error:
        return dict(check=name, status='UNKNOWN', detail=str(error)[:320])
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError, original.struct.error) as error:
        return dict(check=name, status='CONTRADICTED', detail=str(error)[:320])


def verify_typed_capture(worker_final, task=None, lifecycle=None, provenance=None):
    """Complete caller-decoded documents only; all I/O and runtime qualification are external.

    lifecycle holds whole original documents using legacy alias names; provenance.whole_documents
    holds worker_final, task and each non-None lifecycle alias. No projection or repair is done.
    """
    inputs = dict(worker_final=worker_final, task=task, lifecycle=lifecycle, provenance=provenance)
    report = dict(kind=CONSUMER_SCHEMA, producer_ABI=ABI, status='INCONCLUSIVE', source_only=True,
                  native_worker_bound=False, Gate1='UNKNOWN', exact=False, Stage2=False, stage2_GO=False,
                  capture_interface_passed=False, skill_success_rate=None, overall_eight_pass_rate=None,
                  quality_or_causal_claim=False, checks=[],
                  permanent_unknowns=['actual source/byte/runtime provenance', 'DOF/target join and physical readback',
                                      'private/global RNG parity', 'untapped bitwise actor counterfactual',
                                      'MID remaining19/fullclean35', 'unretained C2 middle windows', 'skill quality'])
    try:
        builtins(inputs)
        before = digest(inputs)
    except (ValueError, TypeError, RecursionError) as error:
        report.update(status='CONTRADICTED', input_domain=str(error), input_canonical_before=None,
                      input_canonical_after=None, input_unchanged=None, execution_value=None)
        return report
    report['input_canonical_before'] = before
    documents = {}
    if worker_final is not None:
        documents['worker_final'] = worker_final
    if task is not None:
        documents['task'] = task
    if type(lifecycle) is dict:
        documents.update({name: doc for name, doc in lifecycle.items() if doc is not None})
    add = lambda name, fn: report['checks'].append(_check(name, fn))
    add('whole_document_byte_claims_vs_decoded_canonical', lambda: provenance_contract(provenance, documents))
    if worker_final is None or (type(worker_final) is dict and worker_final.get('kind') == 'PHASE1_TYPED_NATIVE_CAPTURE_INCOMPLETE_V1'):
        report.update(status='NOT_EVALUABLE', capture_evaluability='NOT_EVALUABLE', execution_value=None, missing_successful_FINAL=True)
    else:
        add('new_typed_task_source_contract', lambda: task_contract(task))
        add('new_typed_FINAL_source_contract', lambda: final_contract(worker_final, task))
        add('published_worker_execution_counts', lambda: original.execution(worker_final, task))
        add('published_original_outer_parent_wait', lambda: original.outer_wait_contract(lifecycle, task))
        add('published_new_typed_lifecycle', lambda: lifecycle_contract(lifecycle, task, worker_final, provenance))
        add('all_typed_metadata', lambda: typed_metadata(worker_final, expected_witness=range(8)))
        ledger = lambda: get(get(worker_final, 'sensor'), 'control_ledger')
        act = lambda: get(worker_final, 'actuation')
        count = lambda: integer(get(worker_final, 'controls'), 0)
        add('original_complete_control_ledger_counts', lambda: ledger_counts(ledger()))
        add('original_normal_MID_END_clock_noise_delay_arithmetic', lambda: normal_science(ledger()))
        add('original_prephysical_reset_post_return_boundaries', lambda: boundaries(ledger(), get(worker_final, 'sensor').get('incomplete_current_control')))
        add('C2_typed_clock_domains_all_retained_events', lambda: actuation_domains(act(), count()))
        add('full80_original_queue_submit_apply_arithmetic', lambda: queue_science(act(), count(), ledger()))
        if any(row['status'] == 'CONTRADICTED' for row in report['checks']):
            report['status'] = 'CONTRADICTED'
        closure = ('published_worker_execution_counts', 'published_original_outer_parent_wait', 'published_new_typed_lifecycle')
        rows_by_name = {row['check']: row for row in report['checks']}
        closed = all(rows_by_name[name]['status'] == 'CONSISTENT' for name in closure)
        if closed:
            closed = rows_by_name['published_original_outer_parent_wait']['detail']['successful_closed_execution']
        report['execution_value'] = True if closed else None
        report['execution_value_scope'] = 'PUBLISHED_COUNTERS_AND_WAIT_CLOSURE_ONLY_NOT_INTERFACE_OR_QUALITY'
        finite = report['checks'][-4:]
        report['finite_science_status'] = ('CONTRADICTED' if any(row['status'] == 'CONTRADICTED' for row in finite) else
                                           'UNKNOWN' if any(row['status'] == 'UNKNOWN' for row in finite) else
                                           'CONSISTENT_WITHIN_RETAINED_DECODED_CONSTRAINTS')
    if any(row['status'] == 'CONTRADICTED' for row in report['checks']):
        report['status'] = 'CONTRADICTED'  # Also preserve byte-claim contradictions when no successful FINAL exists.
    after = digest(inputs)
    report.update(input_canonical_after=after, input_unchanged=before == after)
    if before != after:
        report['status'] = 'CONTRADICTED'
        report['input_mutation'] = 'DETECTED_NO_REPAIR'
    return report
