"""Injection-only synthetic CPU fixture; SOURCE preparation never invokes it."""
import json
import random


def run_fixture(torch_module, codec_module):
    t, m = torch_module, codec_module
    assert t.__name__ == 'torch'
    assert m.CHANNEL_WIDTHS == {'base_ang_vel': 3, 'projected_gravity': 3, 'leg_pos': 4, 'leg_vel': 4, 'wheel_vel': 2}
    rng0, python0 = t.get_rng_state().clone(), random.getstate()
    sources, expected_refs = [], []
    index = t.arange(8, dtype=t.int64, device='cpu')
    index_before = index.clone()
    codec = m.CaptureCodec(t.Tensor, witness_index=index, witness_env_ids=list(range(8)))

    def clock(control, slot='post'):
        normal = slot in ('mid', 'end')
        tick = control * 8 + (4 if slot == 'mid' else 0 if slot == 'begin' else 8)
        return dict(physics_tick=tick, feedback_tick=tick // 4, sim_time_us=tick * 2500,
                    common_control_counter=control if normal or slot == 'begin' else control + 1,
                    phase='scene_update' if normal else 'outside_scene_update', reset_depth=0,
                    control_slot=slot, is_original_100hz_slot=normal)

    def owned(x, role='ENV_ROWS_WITNESS', *, clk=None, axis=0, group=None, field='synthetic.input'):
        before = x.clone()
        e = codec.capture(x, role=role, source_ref='SYNTHETIC_CPU_NOT_SDK', source_field=field,
                          clock=clock(0) if clk is None else clk, env_axis=axis, group=group)
        assert e['original_shape'] == list(x.shape) and e['original_dtype'] == str(x.dtype)
        assert e['original_device'] == str(x.device) == 'cpu' and e['source_env_axis'] == axis
        shape = list(x.shape)
        if role == 'ENV_ROWS_WITNESS':
            shape[axis] = 8
            assert e['row_mapping']['env_ids'] == list(range(8))
        assert e['retained_shape'] == shape and list(e['values'].shape) == shape
        assert e['values'].dtype == x.dtype and e['values'].device == x.device
        assert e['values'] is not x and t.equal(x, before)
        expected = before.narrow(axis, 0, 8) if role == 'ENV_ROWS_WITNESS' else before
        assert t.equal(e['values'], expected)
        if x.numel():
            assert e['values'].untyped_storage().data_ptr() != x.untyped_storage().data_ptr()
        sources.append((x, before))
        return e

    def negative(call):
        try:
            call()
        except m.CaptureError:
            return
        raise AssertionError('expected CaptureError, no fallback')

    raw = t.arange(240, dtype=t.float32, device='cpu').reshape(80, 3)
    term, trunc = t.zeros(80, dtype=t.bool, device='cpu'), t.zeros(80, dtype=t.bool, device='cpu')
    term[79], trunc[78] = True, True
    ids = {k: t.arange(k, dtype=t.int32, device='cpu') for k in (0, 1, 79, 80)}
    probes = [owned(raw), owned(term, 'TERMINAL_BOOL_FULL'), owned(trunc, 'TERMINAL_BOOL_FULL')]
    probes += [owned(x, 'ENV_IDS_FULL', axis=None) for x in ids.values()]
    for group, width in (('legs', 4), ('wheels', 2)):
        probes.append(owned(t.full((80, width), 3.25, dtype=t.float64, device='cpu'), 'QUEUE_GROUP_FULL', group=group))
    full_masks = codec.materialize({'term': probes[1], 'trunc': probes[2]})
    assert len(full_masks['term']['values']) == 80 and full_masks['term']['values'][79] is True
    assert len(full_masks['trunc']['values']) == 80 and full_masks['trunc']['values'][78] is True
    for k, e in zip(ids, probes[3:7]):
        assert e['retained_shape'] == [k] and e['original_dtype'] == 'torch.int32'
        assert codec.materialize(e)['values'] == list(range(k))
    for e in probes:
        e['values'].fill_(False if e['values'].dtype == t.bool else -123)
    assert all(t.equal(x, before) for x, before in sources)
    big = 2 ** 60 + 7
    large = owned(t.full((80,), big, dtype=t.int64, device='cpu'))
    packed = json.loads(json.dumps(codec.materialize(large), allow_nan=False))
    assert packed['values'] == [big] * 8 and all(type(v) is int for v in packed['values'])
    assert packed['original_dtype'] == 'torch.int64'
    bad_float = t.zeros(80, dtype=t.float32, device='cpu')
    bad_mask, bad_ids = t.zeros(79, dtype=t.bool, device='cpu'), t.arange(81, dtype=t.int32, device='cpu')
    sources += [(x, x.clone()) for x in (bad_float, bad_mask, bad_ids)]
    for role, x, axis, group in (
        ('AUTO_FROM_SHAPE', raw, 0, None), ('ENV_ROWS_WITNESS', raw, None, None),
        ('ENV_ROWS_WITNESS', raw, 1, None), ('ENV_IDS_FULL', raw, None, None),
        ('ENV_IDS_FULL', term, None, None), ('TERMINAL_BOOL_FULL', ids[80], 0, None),
        ('QUEUE_GROUP_FULL', raw, 0, None), ('QUEUE_GROUP_FULL', raw[:8], 0, 'legs'),
        ('ENV_IDS_FULL', bad_float, None, None), ('ENV_IDS_FULL', bad_ids, None, None),
        ('TERMINAL_BOOL_FULL', bad_mask, 0, None)):
        negative(lambda: codec.capture(x, role=role, source_ref='S', source_field='negative', clock=clock(0), env_axis=axis, group=group))
    negative(lambda: m.CaptureCodec(t.Tensor, witness_index=index, witness_env_ids=list(range(9))))
    ledger = m.ControlLedger(codec, controls=64, run_id='SYNTHETIC_CPU_64_NOT_SDK')
    empty = t.zeros(80, dtype=t.bool, device='cpu')
    actor = t.zeros((80, 35), dtype=t.float32, device='cpu')
    reset_ids = t.arange(78, 80, dtype=t.int32, device='cpu')
    for control in range(64):
        ledger.begin(control, clock=clock(control, 'begin'))
        for slot in ('mid', 'end'):
            clk = clock(control, slot)
            for channel, width in m.CHANNEL_WIDTHS.items():
                clean = owned(t.full((80, width), control + .25, dtype=t.float32, device='cpu'), clk=clk, field=channel)
                payload = {'synthetic_existing_owned': clean}
                ledger.normal_sample(channel, slot, clean, clock=clk, payload=payload)
                expected_refs.append((control, slot, channel, clean, payload, clean['values'].data_ptr()))
        clk = clock(control)
        tf, xf = (term, trunc) if control == 37 else (empty, empty)
        pre_t, pre_x = owned(tf, 'TERMINAL_BOOL_FULL', clk=clk), owned(xf, 'TERMINAL_BOOL_FULL', clk=clk)
        ledger.pre_reset(pre_t, pre_x, clock=clk, event_id='pre:' + str(control))
        if control == 37:
            edge_ids = owned(reset_ids, 'ENV_IDS_FULL', clk=clk, axis=None)
            ledger.reset(edge_ids, clock=clk, event_id='reset:37', before={'stage': 'before'}, after={'stage': 'after'})
        post_t, post_x = owned(tf, 'TERMINAL_BOOL_FULL', clk=clk), owned(xf, 'TERMINAL_BOOL_FULL', clk=clk)
        out = ledger.end(post_term=post_t, post_trunc=post_x, clock=clk, actor=owned(actor, clk=clk))
        assert out['pre_reset']['term'] is pre_t and out['post_return']['term'] is post_t
        assert out['retention_status'] == 'EXPECTED_FIELDS_RETAINED'
    result = ledger.finish()
    assert result['recorded_controls'] == 64 and result['normal_channel_records'] == 640
    for control, slot, channel, clean, payload, pointer in expected_refs:
        stored = result['controls'][control]['normal_samples'][slot][channel]
        assert stored['clean'] is clean and stored['payload'] is payload and stored['clean']['values'].data_ptr() == pointer
    materialized = codec.materialize(result)
    edge, no_callback = materialized['controls'][37], materialized['controls'][0]['reset']
    assert edge['reset']['prior_termination_event_id'] == 'pre:37' and edge['reset']['ids']['values'] == [78, 79]
    assert edge['pre_reset']['term']['values'][79] and edge['pre_reset']['trunc']['values'][78]
    assert no_callback['callback_status'] == 'NOT_OBSERVED' and no_callback['ids'] is None
    extra = m.ControlLedger(codec, controls=64, run_id='SYNTHETIC_EDGE_ORDER_ONLY')
    extra.begin(0, clock=clock(0, 'begin'))
    t0, x0 = owned(term, 'TERMINAL_BOOL_FULL'), owned(trunc, 'TERMINAL_BOOL_FULL')
    id0 = owned(ids[0], 'ENV_IDS_FULL', axis=None)
    extra.reset(id0, clock=clock(0), event_id='early', outcome='RAISED', before={'kept': True})
    extra.pre_reset(t0, x0, clock=clock(0), event_id='late')
    partial = extra.end(post_term=t0, post_trunc=x0, clock=clock(0))
    assert partial['reset']['callback_status'] == 'OBSERVED'
    assert partial['reset']['ids'] is id0 and partial['reset']['ids']['retained_shape'] == [0]
    assert partial['reset']['before'] == {'kept': True} and partial['reset']['prior_termination_event_id'] is None
    assert 'ORIGINAL_RESET_RAISED' in partial['missing'] and 'RESET_WITHOUT_PRIOR_RETAINED_TERMINATION' in partial['missing']
    assert all(t.equal(x, before) for x, before in sources) and t.equal(index, index_before)
    assert t.equal(rng0, t.get_rng_state()) and python0 == random.getstate()
    return dict(kind='INJECTED_CODEC_CPU_SYNTHETIC_FIXTURE_V1', result='PASS', N=80, controls=64,
                normal_channel_records=640, reset_control=37, negative_cases=12, roles=list(m.ROLES),
                source_inputs_unchanged=True, owned_storage_separate=True, ledger_references_identical=True,
                TorchCPU_rng_unchanged=True, Python_rng_unchanged=True, CUDA_calls=0,
                SDK_calls=0, physical_or_natural_reset_proof=False, Gate1='UNKNOWN', stage2_GO=False)
