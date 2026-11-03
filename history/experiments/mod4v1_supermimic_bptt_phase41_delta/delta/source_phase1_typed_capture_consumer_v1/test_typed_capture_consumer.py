"""Fourteen SOURCE-only stdlib synthetic cases; no target/Torch/SDK import or real capture."""
import ast
import copy
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'source_phase1_capture_evidence_verifier_v1')]
import typed_capture_consumer as c

WITNESS = list(range(8))  # Current producer ABI; standalone boundary case also remaps explicitly.


def clock(tick, phase='outside_scene_update', depth=0):
    return dict(physics_tick=tick, sim_time_us=tick*2500, feedback_tick=tick//4,
                common_control_counter=900+tick//8, phase=phase, reset_depth=depth,
                control_slot='mid' if tick%8 == 4 else 'end' if tick and tick%8 == 0 else 'UNKNOWN',
                is_original_100hz_slot=phase == 'scene_update' and depth == 0 and tick%4 == 0)


def envelope(values, role, source_clock, *, width=None, dtype='torch.float32', group=None):
    if role == 'ENV_IDS_FULL':
        shape, axis = [len(values)], None
        mapping = dict(kind='VALUES_ARE_ENV_IDS_NOT_ENV_AXIS', preserve_entire_argument=True)
    else:
        axis = 0
        shape = [80] if width is None else [80, width]
        mapping = dict(kind='EXPLICIT_ORIGINAL_ENV_ROWS' if role == 'ENV_ROWS_WITNESS' else 'ALL_ENV_ROWS_IN_ORIGINAL_ORDER',
                       env_axis=0, env_ids=list(WITNESS) if role == 'ENV_ROWS_WITNESS' else list(range(80)))
        if role == 'ENV_ROWS_WITNESS':
            mapping['index_binding'] = 'CALLER_DECLARED_INDEX_BINDING_NOT_READBACK'
    return dict(envelope_kind='TYPED_SOURCE_TENSOR_V1', semantic_role=role, source_ref='SYNTHETIC_SOURCE_CLAIM',
                source_pin_ref='SYNTHETIC_SOURCE_CLAIM', source_field='SYNTHETIC_FIELD', original_shape=shape,
                original_dtype=dtype, original_device='synthetic-device', source_env_axis=axis,
                retained_shape=([len(WITNESS)]+shape[1:] if role == 'ENV_ROWS_WITNESS' else list(shape)),
                row_mapping=mapping, source_clock=copy.deepcopy(source_clock), group=group,
                ownership='OWNED_BY_INDEX_SELECT' if role == 'ENV_ROWS_WITNESS' else 'OWNED_BY_DETACH_CLONE',
                selection='ROWS_FROM_EXPLICIT_ROLE_NOT_SHAPE_INFERENCE' if role == 'ENV_ROWS_WITNESS' else 'FULL_SEMANTIC_EXCEPTION',
                evidence_level='OWNED_TENSOR_SNAPSHOT_NOT_SDK_PROVENANCE_QUALIFICATION', values=copy.deepcopy(values))


def row(values, cc, width=None, dtype='torch.float32'):
    return envelope(values, 'ENV_ROWS_WITNESS', cc, width=width, dtype=dtype)


def mask(values, cc):
    return envelope(values, 'TERMINAL_BOOL_FULL', cc, dtype='torch.bool')


def cache_envelopes(cache, cc, width):
    return {key: row(value, cc, None if key in ('last', 'sample_tick', 'ready') else width,
                     'torch.int64' if key in ('last', 'sample_tick') else 'torch.bool' if key == 'ready' else 'torch.float32')
            for key, value in cache.items()}


def sensor_ledger(controls=64):
    packs, caches = [], {}
    for index in range(controls):
        normal = {'mid': {}, 'end': {}}
        for slot, tick in (('mid', index*8+4), ('end', index*8+8)):
            cc, fb = clock(tick, 'scene_update'), tick//4
            for number, (key, width) in enumerate(c.CHANNELS.items()):
                clean = [[c.original.f32((fb*17+i+j)/64.) for j in range(width)] for i in range(len(WITNESS))]
                noise = [[.125 if fb%2 else -.125]*width for _ in range(len(WITNESS))]
                bias = [[.0625]*width for _ in range(len(WITNESS))] if key == 'leg_pos' else [[0.]*width for _ in range(len(WITNESS))]
                noisy = [[c.original.f32(c.original.f32(a+b)+z) for a, b, z in zip(x, y, q)]
                         for x, y, q in zip(clean, noise, bias)]
                old = copy.deepcopy(caches.get(key))
                before = 'UNKNOWN' if old is None else cache_envelopes(old, cc, width)
                if old is None:
                    old = dict(last=[-1]*len(WITNESS), sample_tick=[-1]*len(WITNESS), ready=[False]*len(WITNESS), cur=noisy, out=noisy)
                lag = [env_id%2 for env_id in WITNESS]
                out = [copy.deepcopy(old['cur'][i] if lag[i] and old['last'][i] >= 0 else noisy[i]) for i in range(len(WITNESS))]
                current = dict(last=[fb]*len(WITNESS), sample_tick=[old['last'][i] if lag[i] and old['last'][i] >= 0 else fb for i in range(len(WITNESS))],
                               ready=[v >= 0 for v in old['last']], cur=copy.deepcopy(noisy), out=out)
                caches[key] = current
                ep = row([0]*len(WITNESS), cc, dtype='torch.int64')
                state = lambda cache: dict(enabled=True, delay_steps=row(lag, cc, dtype='torch.int64'),
                                           episode=copy.deepcopy(ep), cache=cache)
                sensor = dict(profile='noise_bias_mild_v1', before=dict(episode=copy.deepcopy(ep)), episode=copy.deepcopy(ep),
                              noise_used=row(noise, cc, width), noise_cache_last=row([fb]*len(WITNESS), cc, dtype='torch.int64'),
                              leg_bias_used=row(bias, cc, width) if key == 'leg_pos' else 'UNKNOWN',
                              actual_noisy_return=row(noisy, cc, width), dtype='torch.float32')
                payload = dict(call_id=(2*index+int(slot == 'end'))*5+number+1, key=key, clock=copy.deepcopy(cc),
                               full_clean35='UNKNOWN_NOT_COMPUTED', exception=None, sensor_stage=sensor,
                               delay_actual_input=row(noisy, cc, width), return_value_unused='NOT_A_CHANNEL',
                               delay_stage=dict(before=state(before), after=state(cache_envelopes(current, cc, width)),
                                                actual_return=row(out, cc, width)))
                payload['return'] = row(out, cc, width)
                normal[slot][key] = dict(clock=copy.deepcopy(cc), clean=row(clean, cc, width), payload=payload)
        end = clock((index+1)*8)
        boundary = dict(sensor_episode=row([0]*len(WITNESS), end, dtype='torch.int64'),
                        delay_episode=row([0]*len(WITNESS), end, dtype='torch.int64'),
                        queue={key: cache_envelopes(cache, end, c.CHANNELS[key]) for key, cache in caches.items()})
        packs.append(dict(worker_control_index=index, begin_clock=clock(index*8), normal_samples=normal,
            pre_reset=dict(event_id='terminal:'+str(index), clock=copy.deepcopy(end), term=mask([False]*80, end),
                           trunc=mask([False]*80, end), payload=dict(state=row([[0.]*73]*len(WITNESS), end, 73), boundary=boundary)),
            reset=dict(callback_status='NOT_OBSERVED', ids=None),
            post_return=dict(clock=copy.deepcopy(end), term=mask([False]*80, end), trunc=mask([False]*80, end),
                             actor35_original_buffer=row([[0.]*35]*len(WITNESS), end, 35)),
            retention_status='EXPECTED_FIELDS_RETAINED', missing=[], event_ids_are_clock=False,
            b3_callback_provenance=dict(original_terminal_callbacks=1, original_reset_callbacks=0,
                                       observer_error_count=0, reset_observation='NOT_OBSERVED'),
            unknowns=dict(mid_remaining19='UNKNOWN_NOT_SAMPLED_AT_MID', mid_full_clean35='UNKNOWN_NOT_COMPUTED',
                          mid_actor35='UNKNOWN_50HZ_ONLY', terminal_clean35='UNKNOWN_NOT_COMPUTED',
                          nonwitness_episodes='UNKNOWN', untapped_bitwise_actor='UNKNOWN', private_global_rng_states='UNKNOWN')))
    return dict(kind='BOUNDED_TYPED_CONTROL_LEDGER_V1', run_id='SYNTHETIC_GROUP:E3', requested_controls=controls,
                recorded_controls=controls, control_cap=128, normal_channel_records=controls*10,
                normal_record_cap=1280, all_controls_observed=True, controls=packs,
                scope='METADATA_RETENTION_NOT_INTERFACE_QUALIFICATION', Gate1='UNKNOWN', stage2_GO=False)


def actuation(controls=64):
    states = {}
    for group, width in c.GROUPS.items():
        states[group] = {key: ([[0.]*width for _ in range(80)] if key in ('pending', 'applied') else
                             [False]*80 if key.endswith('valid') else [i%3 for i in range(80)] if key == 'lag_steps' else
                             [0]*80 if key == 'episode' else [-1]*80) for key in c.QUEUE}
    windows, sequence = [], 0
    for index in range(controls):
        keep = index in (0, 1, controls-2, controls-1)
        adoption = clock((index+1)*8)
        events = []
        def packed(state, group):
            return {key: envelope(value, 'QUEUE_GROUP_FULL', adoption,
                    width=c.GROUPS[group] if key in ('pending', 'applied') else None,
                    dtype='torch.float32' if key in ('pending', 'applied') else 'torch.bool' if key.endswith('valid') else 'torch.int64',
                    group=group) for key, value in state.items()}
        def event(kind, group, tick, raw, pre, post, args, **extra):
            nonlocal sequence
            seq = sequence
            sequence += 1
            if not keep:
                return seq
            value = dict(capture_schema='ACTUATION_CLOCK_SCOPE_V2_SOURCE_DISABLED', seq=seq, kind=kind, group=group,
                         tick=tick, raw_stored_counter=raw, write_scope='NOT_A_SETTER', clock_source='SYNTHETIC_CLOCK_SOURCE',
                         args=copy.deepcopy(args), kwargs={}, pre=packed(pre, group), post=packed(post, group), outcome='RETURNED')
            value.update(copy.deepcopy(extra))
            events.append(value)
            return seq
        if index == 0:
            events.append(dict(capture_schema='ACTUATION_CLOCK_SCOPE_V2_SOURCE_DISABLED', seq=sequence,
                kind='target_write', group=dict(status='UNKNOWN'), tick=dict(status='NOT_APPLICABLE'),
                raw_stored_counter=0, write_scope='NON_TERM_SETTER', clock_source='NO_QUALIFIED_PHYSICS_CLOCK',
                args=[{'status': 'UNKNOWN'}], kwargs={}, pre={'status': 'UNKNOWN'}, post={'status': 'UNKNOWN'},
                parent_term_apply_seq=None, active_term_context={'status': 'UNKNOWN'}, physical_readback={'status': 'UNKNOWN'},
                setter=dict(method='set_joint_position_target', joint_ids_source='OMITTED', joint_ids={'status': 'UNKNOWN'}),
                outcome='RETURNED'))
            sequence += 1
        for group, width in c.GROUPS.items():
            old = copy.deepcopy(states[group])
            target = [[float(index+1+j) for j in range(width)] for _ in range(80)]
            current = copy.deepcopy(old)
            start = index*8
            for row_id in range(80):
                for key, value in dict(pending=target[row_id], pending_valid=True, issued_tick=start,
                                       due_tick=start+old['lag_steps'][row_id], last_submit_tick=start).items():
                    current[key][row_id] = copy.deepcopy(value)
            target_envelope = envelope(target, 'QUEUE_GROUP_FULL', adoption, width=width, group=group) if keep else None
            event('issue', group, start, start, old, current, [dict(status='UNKNOWN')])
            event('queue_submit', group, start, start, old, current, [group, target_envelope, start])
            states[group] = current
        for tick in range(index*8, index*8+8):
            for group, width in c.GROUPS.items():
                old, current = copy.deepcopy(states[group]), copy.deepcopy(states[group])
                for row_id in range(80):
                    if old['pending_valid'][row_id] and old['due_tick'][row_id] <= tick:
                        for key, value in dict(applied=old['pending'][row_id], applied_valid=True,
                            applied_issue_tick=old['issued_tick'][row_id], first_apply_tick=tick, pending_valid=False).items():
                            current[key][row_id] = copy.deepcopy(value)
                    current['last_apply_tick'][row_id] = tick
                selected = envelope(current['applied'], 'QUEUE_GROUP_FULL', adoption, width=width, group=group) if keep else None
                term_seq = event('term_apply', group, tick, tick+1, old, current, [])
                event('queue_apply', group, tick, tick+1, old, current, [group, tick], selected_target=selected)
                ids = [3, 7, 12, 29] if group == 'legs' else [31, 33]
                event('target_write', group, tick, tick+1, current, current, [selected, ids],
                    write_scope='SAME_ASSET_TERM_APPLY_CONTEXT', clock_source='original_parent_term_context',
                    parent_term_apply_seq=term_seq, active_term_context=dict(seq=term_seq, group=group, tick=tick),
                    setter=dict(method='set_joint_position_target' if group == 'legs' else 'set_joint_velocity_target',
                                joint_ids_source='positional[1]_UNQUALIFIED_SDK_SIGNATURE', joint_ids=ids))
                states[group] = current
        if keep:
            windows.append(dict(control_index=index, adoption_clock=adoption, events=events))
    return dict(status=dict(dropped_events=0, observer_errors=0, missing_hooks=[], restore_conflicts=[]),
                windows=dict(control_windows_seen=controls, retained_window_bound=4, first=windows[:2], last=windows[-2:]))


def task(controls=64):
    return dict(kind=c.TASK_KIND, purpose=c.original.PURPOSE, batch_purpose=c.original.PURPOSE,
        integration=c.INTEGRATION, policy_variant=c.original.POLICY, role='E3', requested_roles=['E3'],
        role_catalog=copy.deepcopy(c.original.ROLES), num_envs=80, seed=20260928, model_PT_reads=0,
        synthetic_action=[0.]*6, train=False, quality_evaluation=False, full_clean35='UNKNOWN',
        physics=copy.deepcopy(c.original.PHYSICS), asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',
        contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',
        controls=controls, group_id='SYNTHETIC_GROUP', GPU_UUID='SYNTHETIC_NOT_GPU', absolute_worker_deadline_epoch=1000.)


def final(ledger, act):
    n = ledger['requested_controls']
    return dict(kind=c.FINAL_KIND, purpose=c.original.PURPOSE, integration=c.INTEGRATION, typed_producer_schema=c.ABI,
        role='E3', num_envs=80, policy_variant=c.original.POLICY, actor35_source='ORIGINAL_RETURNED_POLICY_BUFFER',
        clean16_only=True, full_clean35='UNKNOWN', model_PT_reads=0, training_updates=0, optimizer_updates=0,
        learner_created=False, replay_created=False, teacher_created=False, gate1='UNKNOWN', exact=False,
        capture_interface_passed=False, paper_ready=False, stage2_GO=False, group_id='SYNTHETIC_GROUP', GPU_UUID='SYNTHETIC_NOT_GPU',
        sensor=dict(kind='PASSIVE_SENSOR_CAPTURE_V3', control_ledger=ledger, incomplete_current_control=None,
                    native_enabled=False, exact=False, metadata_retention_is_not_native_admission=True),
        actuation=act, boundary=dict(actions=n, original_step_transitions=n, pending_original_step=False), coverage={}, rng_counts={},
        restore=dict(ok=True, order=['actuation', 'sensor', 'bridge'], errors=[]),
        original_setup=dict(started_epoch=1., GO_epoch=3., first_control_epoch=5., last_control_epoch=6.),
        inconclusive_reasons=['SYNTHETIC_ONLY'], passed_execution=True, controls=n, requested_controls=n,
        physics_callbacks=8*n, feedback_samples=2*n, delay_calls=dict(legs=8*n, wheels=8*n))


def lifecycle(f):
    t = task()
    identity = dict(controller=dict(pid=10, linux_start_ticks='100'), parent=dict(pid=20, linux_start_ticks='200'))
    dispatch = dict(kind='ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION', group_id=t['group_id'],
        actual_native_parent_Popen_calls=1, parent_source_SHA='a'*64, epoch=.5, **copy.deepcopy(identity))
    started = dict(kind='OWN_PHASE1_CAPTURE_PARENT_ACTUAL_WAIT_CONTROLLER_V1', parent_source_SHA='a'*64,
        epoch=.1, controller=copy.deepcopy(identity['controller']), controller_resource_SDK_model_C_lock_or_signal_operations=0)
    waited = dict(dispatch, kind='ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1', epoch=10., returncode=0,
        actual_parent_p_wait_returned=True, original_parent_resource_close_wait_not_replaced=True, controller_errors=[],
        controller_resource_SDK_model_C_lock_or_signal_operations=0, wall_seconds=9.9)
    semantic = dict(kind='PHASE1_TYPED_NATIVE_WAITED_EXECUTION_SEMANTICS_V1', purpose=c.original.PURPOSE,
                    passed_execution=True, errors=[], actual_wait_call_attested_by_caller=True, waited_return_observed_epoch=7.)
    terminal = dict(role='E3', GPU_UUID=t['GPU_UUID'], pid=30, returncode=0, actual_waited=True,
                    ready=True, started=True, pre_close=True, passed_execution=True, error=None, data=f, semantic=semantic)
    gate = dict(gate1='UNKNOWN', exact=False, stage2_GO=False, capture_interface_passed=False)
    return dict(parent_dispatch=dispatch, outer_parent_wait=waited, controller_started=started,
        parent_started=dict(pid=20, kind='ONEGPU_PHASE1_PASSIVE_CAPTURE_E3_ONLY_PARENT_V1'),
        group_final=dict(kind='PHASE1_TYPED_NATIVE_CAPTURE_GROUP_FINAL_V1', purpose=c.original.PURPOSE,
            integration=c.INTEGRATION, group_id=t['group_id'], requested_roles=['E3'], deferred_roles=c.original.ROLES[1:],
            passed_execution=True, terminal=[terminal], terminal_epoch=8., GO_epoch=3., **gate),
        parent_exit_scope=dict(all_own_children_waited=True, original_single_GPU_private_EX_released=True,
            original_global_finite_EX_released=True, no_foreign_scope_touched=True, canonical_writes=0, errors=[], epoch=9.,
            child_waits=[dict(role='E3', pid=30, returncode=0, actual_waited=True)]),
        source_grade=dict(kind='PHASE1_TYPED_NATIVE_CLOSED_SOURCE_GRADE_V1', purpose=c.original.PURPOSE,
                          passed_closed_capture_execution=True, errors=[], **gate),
        common_go=dict(kind='PHASE1_TYPED_NATIVE_CAPTURE_COMMON_START_V1', purpose=c.original.PURPOSE,
                       group_id=t['group_id'], members=['E3'], stage2_GO=False, epoch=3.),
        worker_ready=dict(kind=c.INTEGRATION, role='E3', epoch=2.), worker_started=dict(kind=c.INTEGRATION, role='E3', epoch=4., GO_epoch=3.),
        env_close=dict(closed=True), app_close_binding=dict(fast_shutdown=False),
        app_close_returned=dict(returned=True, binding=dict(fast_shutdown=False)))


def proof(f, t, life):
    docs = dict(worker_final=f, task=t, **life)
    return dict(whole_documents={key: dict(original_bytes=1, original_SHA256='b'*64, decoded_canonical_SHA256=c.digest(doc))
                                 for key, doc in docs.items()}, reported_source_pins=dict(synthetic=dict(bytes=1, SHA256='c'*64)))


def reset_pack(base, ids):
    pack = copy.deepcopy(base)
    end = pack['pre_reset']['clock']
    flags = [i in ids for i in range(80)]
    pack['pre_reset']['term'] = mask(flags, end)
    before = copy.deepcopy(pack['pre_reset']['payload']['boundary'])
    after = copy.deepcopy(before)
    def update_clock(value):
        if type(value) is dict:
            if value.get('envelope_kind') == 'TYPED_SOURCE_TENSOR_V1':
                value['source_clock'] = clock(end['physics_tick'], 'inside_reset', 1)
            else:
                for item in value.values(): update_clock(item)
    update_clock(after)
    for key in ('sensor_episode', 'delay_episode'):
        after[key]['values'] = [v+int(env in ids) for env, v in zip(WITNESS, before[key]['values'])]
    for cache in after['queue'].values():
        for field in ('last', 'sample_tick', 'ready'):
            for i, env in enumerate(WITNESS):
                if env in ids:
                    cache[field]['values'][i] = False if field == 'ready' else -1
    pack['reset'] = dict(callback_status='OBSERVED', event_id='reset:0', clock=copy.deepcopy(end),
        prior_termination_event_id=pack['pre_reset']['event_id'], ids=envelope(list(ids), 'ENV_IDS_FULL', end, dtype='torch.int64'),
        before=before, after=after, outcome='RETURNED')
    pack['b3_callback_provenance'].update(original_reset_callbacks=1, reset_observation='OBSERVED_WITH_OWNED_IDS')
    return pack


class TypedCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = sensor_ledger()
        cls.act = actuation()
        cls.pack = cls.ledger['controls'][0]

    def test_01_whole64_public_consistent_constraints_still_not_admission(self):
        f, t = final(self.ledger, self.act), task()
        life = lifecycle(f)
        p = proof(f, t, life)
        result = c.verify_typed_capture(f, t, life, p)
        self.assertEqual(result['status'], 'INCONCLUSIVE', result['checks'])
        self.assertTrue(all(x['status'] == 'CONSISTENT' for x in result['checks']), result['checks'])
        self.assertTrue(result['execution_value'])
        self.assertTrue(result['input_unchanged'])
        self.assertEqual(result['Gate1'], 'UNKNOWN')
        self.assertFalse(result['Stage2'])
        self.assertFalse(result['capture_interface_passed'])
        self.assertIsNone(result['skill_success_rate'])
        q = result['checks'][-1]['detail']
        self.assertEqual(q['first_transition_latency_us']['legs'], [0, 2500, 5000])
        self.assertEqual(q['max_held_age_us']['wheels'], 22500)  # Previous issue held into next control's lag2.
        self.assertEqual(q['retained_control_indices'], [0, 1, 62, 63])
        self.assertEqual(q['physical_readback'], 'UNKNOWN')

    def test_02_helpers_are_original_complete_module_and_no_runtime_IO(self):
        self.assertIs(c.integer, c.original.integer)
        self.assertIs(c.same, c.original.typed_equal)
        self.assertIs(c.digest, c.original.digest)
        source = ast.parse((HERE/'typed_capture_consumer.py').read_text(encoding='utf8'))
        forbidden_imports = {'torch', 'paramiko', 'subprocess', 'socket', 'requests', 'pathlib', 'os'}
        self.assertFalse(any(isinstance(node, ast.Import) and any(x.name.split('.')[0] in forbidden_imports for x in node.names) for node in ast.walk(source)))
        forbidden_calls = {'open', 'eval', 'exec', 'compile', 'getattr', 'setattr', 'write', 'read_text', 'read_bytes'}
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbidden_calls for node in ast.walk(source)))
        self.assertNotIn('torch', sys.modules)

    def test_03_full_ID_K0_K9_K80_and_bool80_no_witness_cut(self):
        for count in (0, 9, 80):
            x = envelope(list(range(count)), 'ENV_IDS_FULL', clock(8), dtype='torch.int64')
            self.assertEqual(c.tensor(x, role='ENV_IDS_FULL'), list(range(count)))
        self.assertEqual(len(c.tensor(mask([False]*79+[True], clock(8)))), 80)
        bad = mask([False]*80, clock(8)); bad['values'][79] = 0
        self.assertEqual(c._check('bool', lambda: c.tensor(bad))['status'], 'CONTRADICTED')
        bad = envelope(list(range(80)), 'ENV_IDS_FULL', clock(8), dtype='torch.int64'); bad['values'] = bad['values'][:8]
        self.assertEqual(c._check('IDs', lambda: c.tensor(bad))['status'], 'CONTRADICTED')

    def test_04_explicit_dtype_shape_axis_mapping_and_source_alias(self):
        base = self.pack['normal_samples']['mid']['leg_pos']['clean']
        for path, value in ((('original_shape',), [80., 4]), (('source_env_axis',), False),
                            (('original_dtype',), 'torch.int64'), (('row_mapping', 'env_ids'), [False, 79]),
                            (('source_pin_ref',), 'OTHER_CLAIM')):
            bad = copy.deepcopy(base); dest = bad
            for key in path[:-1]: dest = dest[key]
            dest[path[-1]] = value
            self.assertEqual(c._check('typed', lambda: c.tensor(bad))['status'], 'CONTRADICTED', path)

    def test_05_float32_left_association_and_other_dtype_unknown(self):
        record = copy.deepcopy(self.pack['normal_samples']['mid']['leg_pos'])
        payload = record['payload']
        for key, val in ((record['clean'], 1e8), (payload['sensor_stage']['noise_used'], -1e8),
                         (payload['sensor_stage']['leg_bias_used'], 1.), (payload['sensor_stage']['actual_noisy_return'], 1.),
                         (payload['delay_actual_input'], 1.), (payload['delay_stage']['actual_return'], 1.), (payload['return'], 1.)):
            key['values'] = [[val]*4]*len(WITNESS)
        payload['delay_stage']['before']['enabled'] = payload['delay_stage']['after']['enabled'] = False
        actual = dict(payload, clean=record['clean'])
        self.assertEqual(c._check('f32', lambda: c.feedback_record(actual, {}))['status'], 'CONSISTENT')
        self.assertEqual(c.original.f32(1e8+c.original.f32(-1e8+1.)), 0.)
        actual['clean']['original_dtype'] = 'torch.float64'
        self.assertEqual(c._check('dtype', lambda: c.feedback_record(actual, {}))['status'], 'UNKNOWN')

    def test_06_warmup_and_real_sameTick_cache_not_fresh(self):
        record = copy.deepcopy(self.pack['normal_samples']['mid']['leg_pos'])
        actual = dict(record['payload'], clean=record['clean'])
        memo = {}
        self.assertEqual(c.feedback_record(actual, memo)['warmup_rows'], 2)
        actual['delay_stage']['before'] = copy.deepcopy(actual['delay_stage']['after'])
        metrics = c.feedback_record(actual, memo)
        self.assertEqual(metrics['sameTick_cache_rows'], 2)
        self.assertEqual(metrics['sameTick_noise_rows'], 2)
        actual['sensor_stage']['noise_used']['values'][0][0] += 1.
        self.assertEqual(c._check('sameTick', lambda: c.feedback_record(actual, memo))['status'], 'CONTRADICTED')

    def test_07_original_clocks_and_no_MID19_or_bool_as_counter(self):
        ledger = dict(controls=[copy.deepcopy(self.pack)])
        sample = ledger['controls'][0]['normal_samples']['mid']['base_ang_vel']
        sample['clock']['physics_tick'] = False
        self.assertEqual(c._check('clock', lambda: c.normal_science(ledger))['status'], 'CONTRADICTED')
        ledger = dict(controls=[copy.deepcopy(self.pack)])
        ledger['controls'][0]['normal_samples']['mid']['base_ang_vel']['payload']['full_clean35'] = 'FABRICATED35'
        self.assertEqual(c._check('MID', lambda: c.normal_science(ledger))['status'], 'CONTRADICTED')
        self.assertEqual(c.ledger_counts(self.ledger)['normal_channel_records'], 640)
        ledger128 = copy.deepcopy(self.ledger)
        ledger128.update(requested_controls=128, recorded_controls=128, normal_channel_records=1280)
        extra = copy.deepcopy(ledger128['controls'])
        for i, pack in enumerate(extra, 64): pack['worker_control_index'] = i
        ledger128['controls'].extend(extra)
        self.assertEqual(c.ledger_counts(ledger128)['normal_channel_records'], 1280)
        ledger128['normal_channel_records'] = 1280.
        self.assertEqual(c._check('count', lambda: c.ledger_counts(ledger128))['status'], 'CONTRADICTED')

    def test_08_noncontiguous_witness_partial_reset_and_full80_reset(self):
        for ids in ([79], list(range(80)), []):
            pack = reset_pack(self.pack, ids)
            result = c.boundaries(dict(controls=[pack]))
            self.assertEqual(result['_status'], 'CONSISTENT', result)
            self.assertEqual(result['joined_reset_edges'], 1)
            self.assertEqual(result['natural_preterminal_env_rows'], len(ids))
            self.assertEqual(pack['post_return']['term']['values'], [False]*80)
            self.assertEqual(pack['reset']['after']['sensor_episode']['source_clock']['phase'], 'inside_reset')

    def test_09_no_callback_vs_metadata_failed_vs_raised_vs_late(self):
        no = c.boundaries(dict(controls=[self.pack]))
        self.assertEqual(no['no_reset_callbacks'], 1)
        bad = copy.deepcopy(self.pack)
        bad.update(retention_status='INCOMPLETE', missing=['B3_OBSERVER_METADATA_ERRORS'])
        bad['b3_callback_provenance'].update(original_reset_callbacks=1, observer_error_count=1, reset_observation='OBSERVED_METADATA_FAILED')
        out = c.boundaries(dict(controls=[bad]))
        self.assertEqual((out['_status'], out['observed_metadata_failed'], out['no_reset_callbacks']), ('UNKNOWN', 1, 0))
        raised = reset_pack(self.pack, [79]); raised['reset']['outcome'] = 'RAISED'; raised['retention_status'] = 'INCOMPLETE'
        self.assertEqual(c.boundaries(dict(controls=[raised]))['raised_reset_callbacks'], 1)
        late = reset_pack(self.pack, [79]); late['reset']['prior_termination_event_id'] = None; late['retention_status'] = 'INCOMPLETE'
        self.assertEqual(c.boundaries(dict(controls=[late]))['late_or_unjoined'], 1)

    def test_10_END_missing_pending_and_no_successful_FINAL(self):
        pending = dict(kind='B3_INCOMPLETE_OWNED_CONTROL', retention_status='INCOMPLETE', original_post_return='NOT_OBSERVED',
                       provenance=dict(original_terminal_callbacks=0, original_reset_callbacks=0), owned_partial_control={})
        result = c.boundaries(dict(controls=[]), pending)
        self.assertEqual(result['_status'], 'UNKNOWN')
        for f in (None, dict(kind='PHASE1_TYPED_NATIVE_CAPTURE_INCOMPLETE_V1')):
            result = c.verify_typed_capture(f)
            self.assertEqual(result['status'], 'NOT_EVALUABLE')
            self.assertIsNone(result['execution_value'])
            self.assertTrue(result['input_unchanged'])

    def test_11_C2_unparented_zero_counter_domain_not_minus1_physics(self):
        result = c.actuation_domains(self.act, 64)
        self.assertEqual(result['NON_TERM_SETTER_records'], 1)
        self.assertEqual(result['records_filtered_or_clock_repaired'], 0)
        bad = copy.deepcopy(self.act['windows']['first'][0])
        bad['events'][0]['tick'] = -1
        act = dict(windows=dict(control_windows_seen=64, retained_window_bound=4, first=[bad], last=[]))
        self.assertEqual(c._check('scope', lambda: c.actuation_domains(act, 64))['status'], 'CONTRADICTED')
        for value in (-1, False, 0.):
            bad = copy.deepcopy(self.act['windows']['first'][0])
            next(e for e in bad['events'] if e['kind'] == 'queue_apply')['tick'] = value
            act['windows']['first'] = [bad]
            self.assertEqual(c._check('physics', lambda: c.actuation_domains(act, 64))['status'], 'CONTRADICTED', value)

    def test_12_full_queue_corruption_row79_and_group4plus2(self):
        first = self.act['windows']['first'][0]
        for group, width in c.GROUPS.items():
            sub = next(e for e in first['events'] if e['kind'] == 'queue_submit' and e['group'] == group)
            self.assertEqual(c._queue(sub['post'], group, first['adoption_clock'])['pending'][79], [float(1+j) for j in range(width)])
        bad = copy.deepcopy(first)
        e = next(e for e in bad['events'] if e['kind'] == 'queue_apply')
        e['post']['applied']['values'][79][0] += 3.
        act = dict(status=self.act['status'], windows=dict(control_windows_seen=64, retained_window_bound=4, first=[bad], last=[]))
        self.assertEqual(c._check('queue', lambda: c.queue_science(act, 64, self.ledger))['status'], 'CONTRADICTED')
        e['pre']['due_tick']['original_dtype'] = 'torch.float64'
        self.assertEqual(c._check('dtype', lambda: c._queue(e['pre'], e['group'], first['adoption_clock']))['status'], 'CONTRADICTED')

    def test_13_context_not_DOF_and_adoption_not_event_clock(self):
        first = copy.deepcopy(self.act['windows']['first'][0])
        writer = next(e for e in first['events'] if e['kind'] == 'target_write' and e['write_scope'] == 'SAME_ASSET_TERM_APPLY_CONTEXT')
        writer['setter']['method'] = 'set_joint_velocity_target'  # A name does not reassign a group.
        writer['args'][0]['values'][0][0] += 9.
        act = dict(status=self.act['status'], windows=dict(control_windows_seen=64, retained_window_bound=4, first=[first], last=[]))
        result = c.queue_science(act, 64, self.ledger)
        self.assertGreater(result['other_ambiguous_context_argument_observations'], 0)
        self.assertTrue(result['DOF_target_join'].startswith('UNKNOWN'))
        self.assertNotEqual(writer['tick'], writer['args'][0]['source_clock']['physics_tick'])
        self.assertEqual(c.actuation_domains(act, 64)['_status'], 'CONSISTENT')

    def test_14_original_bytes_vs_canonical_and_whole_group_not_projection(self):
        doc = {'full': 'synthetic', 'data': [1, False, 1.]}
        records = dict(worker_final=dict(original_bytes=123, original_SHA256='0'*64, decoded_canonical_SHA256=c.digest(doc)))
        result = c.provenance_contract(dict(whole_documents=records, reported_source_pins={}), dict(worker_final=doc))
        self.assertIn('NOT_RECOMPUTED', result['original_byte_proofs'])
        self.assertNotEqual(records['worker_final']['original_SHA256'], records['worker_final']['decoded_canonical_SHA256'])
        records['worker_final']['decoded_canonical_SHA256'] = '0'*64
        self.assertEqual(c._check('digest', lambda: c.provenance_contract(dict(whole_documents=records), dict(worker_final=doc)))['status'], 'CONTRADICTED')
        f = final(self.ledger, self.act); life = lifecycle(f)
        life['group_final']['terminal'][0]['data'] = {'kind': f['kind']}
        self.assertEqual(c._check('whole', lambda: c.lifecycle_contract(life, task(), f, {}))['status'], 'CONTRADICTED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
