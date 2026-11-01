"""Fresh in-memory tensors/fictional IDs only. No modules/models/optimizer steps."""
from pathlib import Path
from copy import deepcopy
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import ast
import hashlib
import json
import time
import traceback

N = Path(__file__).resolve().parent
R = N / 'reports'
purpose = json.loads((R / 'FROZEN277_NEW_ZERO_INPUT_BOUND_ADAM_SYNTHETIC_CPU_PURPOSE.json').read_bytes())
with (R / 'CONSUMED277_NEW_ZERO_INPUT_BOUND_ADAM_CPU_ONCE.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), purpose_ID=purpose['purpose_ID'], real_models_raw_SDK_GPU_remote_Git=0), f)
groups, refused = [], []
try:
    for row in purpose['source_files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['SHA']
    for p in N.glob('*.py'):
        ast.parse(p.read_text(encoding='utf8'))
    import torch
    import torch.nn.functional as F
    torch.set_num_threads(2)
    import zero_input_bound_adam277 as m
    rng = torch.get_rng_state().clone()
    generator = torch.Generator().manual_seed(277)

    def weights(scope, width):
        out = {k: torch.randn(shape, generator=generator) * .05 for k, shape in m.expected_shapes(scope, width).items()}
        if scope == 'actor':
            out['distribution.std_param'] = torch.rand(6, generator=generator) * .1 + .5
        return out
    actor, critic = weights('actor', 35), weights('critic', 38)
    actor_before, critic_before = deepcopy(actor), deepcopy(critic)
    names = [m.qualified(s, k) for s, keys in (('actor', m.ACTOR_KEYS), ('critic', m.CRITIC_KEYS)) for k in keys]
    order = [16, 2, 10, 0, 8, 14, 4, 11, 1, 13, 6, 3, 15, 5, 9, 7, 12]
    labels = [901, 17, 300, 41, 802, 9, 555, 63, 101, 1003, 77, 246, 12, 4001, 5, 88, 700]
    ordered = [names[i] for i in order]
    name_id = dict(zip(ordered, labels))
    groups_source = []
    records = []
    slots = {}
    for gi, selected in enumerate((ordered[:9], ordered[9:])):
        groups_source.append(dict(params=[name_id[name] for name in selected], param_names=list(selected),
            lr=.0019461950683593758, betas=(.9, .999), eps=1e-8 if gi == 0 else 1e-7,
            weight_decay=.001, amsgrad=True, maximize=False, foreach=None))
        for pos, name in enumerate(selected):
            scope, key = name.split(':', 1)
            source = (actor if scope == 'actor' else critic)[key]
            records.append(dict(scope=scope, state_key=key, optimizer_id=name_id[name],
                group_index=gi, group_position=pos, shape=list(source.shape), parameter_name=name))
            scale = (gi * 9 + pos + 1) / 100.
            slots[name_id[name]] = dict(step=torch.tensor(42940.), exp_avg=torch.full_like(source, scale),
                exp_avg_sq=torch.full_like(source, scale + 1.), max_exp_avg_sq=torch.full_like(source, scale + 2.))
    source_adam = dict(state=slots, param_groups=groups_source)
    original_adam = deepcopy(source_adam)
    witness = dict(kind='SYNTHETIC_SOURCE_ADAM_NAME_ID_BINDING_ONLY', identity_receipt_SHA='a'*64,
        source_teacher_SHA=m.SOURCE_TEACHER_SHA, source_iteration=2135, source_Adam_step=42940,
        saved_group_order_identity_verified=True, source_fullstate_CPU_receipt_SHA='b'*64,
        parameter_bindings=records)
    plan = m.prepare_split_plan(actor, critic, source_adam, witness, synthetic_CPU_test=True)
    a44, c47 = plan['actor44_state_dict'], plan['critic47_state_dict']
    assert len(a44) == 9 and len(c47) == 8
    for old, new in ((actor, a44), (critic, c47)):
        for key, value in old.items():
            if key == 'mlp.0.weight':
                assert new[key].shape[1] == value.shape[1] + 9
                assert torch.equal(new[key][:, :value.shape[1]], value)
                assert torch.count_nonzero(new[key][:, value.shape[1]:]) == 0
            else:
                assert torch.equal(new[key], value)
            assert new[key].data_ptr() != value.data_ptr()
    x35 = torch.randn(17, 35, generator=generator)
    x38 = torch.randn(17, 38, generator=generator)
    depth = torch.randn(17, 9, generator=generator) * 25.
    def mean(state, x):
        for i in (0, 2, 4, 6):
            x = F.linear(x, state[f'mlp.{i}.weight'], state[f'mlp.{i}.bias'])
            if i != 6:
                x = F.elu(x)
        return x
    with torch.no_grad():
        actor_error = float((mean(actor, x35) - mean(a44, torch.cat((x35, depth), -1))).abs().max())
        critic_error = float((mean(critic, x38) - mean(c47, torch.cat((x38, depth), -1))).abs().max())
    assert actor_error <= 1e-6 and critic_error <= 1e-6
    assert torch.equal(a44['distribution.std_param'], actor['distribution.std_param'])
    groups.append(dict(name='fresh_ELU_actor_mean_critic_value_equivalence_zero_suffix_original17_tensors', passed=True,
        actor_max_abs_error=actor_error, critic_max_abs_error=critic_error,
        numerical_scope='synthetic float32 function equivalence; not physical bitwise/skill gate'))

    for scope, part in plan['split_adam_plans'].items():
        for name, state in part['states_by_name'].items():
            key = name.split(':', 1)[1]
            original = source_adam['state'][name_id[name]]
            assert torch.equal(state['step'], original['step'])
            for field in ('exp_avg', 'exp_avg_sq', 'max_exp_avg_sq'):
                value = original[field]
                if key == 'mlp.0.weight':
                    assert torch.equal(state[field][:, :value.shape[1]], value)
                    assert torch.count_nonzero(state[field][:, value.shape[1]:]) == 0
                else:
                    assert torch.equal(state[field], value)
                assert state[field].data_ptr() != value.data_ptr()
    assert len(plan['split_adam_plans']['actor']['states_by_name']) == 9
    assert len(plan['split_adam_plans']['critic']['states_by_name']) == 8
    assert plan['metadata']['WM_optimizer_received_or_copied'] is False
    groups.append(dict(name='all17_Adam_slots_partition_once_Pi9_Critic8_3moments_zero_expand_step42940_preserved',
        passed=True, sparse_nonordered_source_IDs=True, WM_optimizer_copies=0))

    def target(scope):
        target_groups, target_records = [], []
        part = plan['split_adam_plans'][scope]
        offset, stride = (10005, 29) if scope == 'actor' else (20003, 31)
        count = 0
        for gi, group in enumerate(part['groups']):
            ids = []
            for pos, name in enumerate(group['names']):
                _, key = name.split(':', 1)
                pid = offset + count * stride
                count += 1
                ids.append(pid)
                target_records.append(dict(scope=scope, state_key=key, optimizer_id=pid,
                    group_index=gi, group_position=pos, shape=list((a44 if scope == 'actor' else c47)[key].shape),
                    parameter_name=name))
            target_groups.append(dict(deepcopy(group['options']), params=ids, param_names=list(group['names'])))
        return dict(state={}, param_groups=target_groups), dict(
            kind='SYNTHETIC_TARGET_ADAM_NAME_ID_BINDING_ONLY', identity_receipt_SHA=('c' if scope == 'actor' else 'd')*64,
            source_identity_receipt_SHA=witness['identity_receipt_SHA'], optimizer_scope=scope, parameter_bindings=target_records)
    pi_empty, pi_witness = target('actor')
    critic_empty, critic_witness = target('critic')
    pi_state = m.bind_target_optimizer(plan, 'actor', pi_empty, pi_witness, synthetic_CPU_test=True)
    critic_state = m.bind_target_optimizer(plan, 'critic', critic_empty, critic_witness, synthetic_CPU_test=True)
    assert len(pi_state['state']) == 9 and len(critic_state['state']) == 8
    for scope, result, tw in (('actor', pi_state, pi_witness), ('critic', critic_state, critic_witness)):
        for record in tw['parameter_bindings']:
            name = m.qualified(scope, record['state_key'])
            assert result['state'][record['optimizer_id']] is plan['split_adam_plans'][scope]['states_by_name'][name]
        assert all(g['lr'] == .0019461950683593758 for g in result['param_groups'])
    groups.append(dict(name='independent_explicit_target_ID_binding_without_17state_triplication_or_optimizer_step',
        passed=True, target_Pi_slots=9, target_critic_slots=8, actual_migration=False))

    def reject(name, fn):
        try:
            fn()
        except (ValueError, TypeError, KeyError):
            refused.append(name)
        else:
            raise AssertionError('Missing/incorrect identity accepted: ' + name)
    reject('missing_source_ID_witness', lambda: m.prepare_split_plan(actor, critic, source_adam, None, synthetic_CPU_test=True))
    reject('synthetic_witness_not_actual', lambda: m.prepare_split_plan(actor, critic, source_adam, witness))
    duplicate = deepcopy(witness)
    duplicate['parameter_bindings'][1]['optimizer_id'] = duplicate['parameter_bindings'][0]['optimizer_id']
    reject('duplicate_source_ID', lambda: m.prepare_split_plan(actor, critic, source_adam, duplicate, synthetic_CPU_test=True))
    missing_std = dict(actor)
    del missing_std['distribution.std_param']
    reject('STD_missing_or_reset_not_silent', lambda: m.expand_weights(missing_std, critic))
    reject('missing_target_ID_witness', lambda: m.bind_target_optimizer(plan, 'actor', pi_empty, None, synthetic_CPU_test=True))
    changed_lr = deepcopy(pi_empty)
    changed_lr['param_groups'][0]['lr'] = .0001
    reject('target_LR_cannot_reset', lambda: m.bind_target_optimizer(plan, 'actor', changed_lr, pi_witness, synthetic_CPU_test=True))
    learned_target = deepcopy(pi_empty)
    learned_target['state'][next(iter(pi_state['state']))] = {}
    reject('existing_target_moments_not_overwritten', lambda: m.bind_target_optimizer(plan, 'actor', learned_target, pi_witness, synthetic_CPU_test=True))
    changed_step = deepcopy(source_adam)
    changed_step['state'][labels[0]]['step'] = torch.tensor(42941.)
    reject('source_Adam_step_not_changed', lambda: m.prepare_split_plan(actor, critic, changed_step, witness, synthetic_CPU_test=True))
    wrong_position = deepcopy(witness)
    wrong_position['parameter_bindings'][0]['group_position'] = 1
    reject('shape_or_position_is_not_identity', lambda: m.prepare_split_plan(actor, critic, source_adam, wrong_position, synthetic_CPU_test=True))
    missing_max = deepcopy(source_adam)
    del missing_max['state'][labels[0]]['max_exp_avg_sq']
    reject('AMSGrad_state_missing', lambda: m.prepare_split_plan(actor, critic, missing_max, witness, synthetic_CPU_test=True))
    reject('wrong_target_scope', lambda: m.bind_target_optimizer(plan, 'actor', pi_empty,
        dict(pi_witness, optimizer_scope='critic'), synthetic_CPU_test=True))
    unproved = dict(witness, saved_group_order_identity_verified=False)
    reject('group_order_evidence_pending', lambda: m.prepare_split_plan(actor, critic, source_adam, unproved, synthetic_CPU_test=True))
    assert len(refused) == 12
    for old, current in ((actor_before, actor), (critic_before, critic)):
        assert all(torch.equal(v, current[k]) for k, v in old.items())
    for pid in original_adam['state']:
        assert all(torch.equal(v, source_adam['state'][pid][k]) for k, v in original_adam['state'][pid].items())
    assert torch.equal(rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
    groups.append(dict(name='new_identity_scope_refusals_original_tensors_slots_RNG_unchanged', passed=True, refusals=refused))
    report = dict(passed=True, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        refusals=len(refused), synthetic_tensor_only=True, optimizer_instances_or_steps=0,
        actual_models_raw_assets_SDK_GPU_remote_Git_GO=0, old_fixtures_replayed=0,
        actual_migration_Pi_gradient_admission=False, WM_optimizer_touched=False, CUDA_initialized=False)
except BaseException:
    report = dict(passed=False, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        error=traceback.format_exc(), scope='NEW277 synthetic tensor/ID source only, no actual model case')
    raise
finally:
    with (R / 'ACTUAL277_NEW_ZERO_INPUT_BOUND_ADAM_CPU_RETURNED.json').open('x', encoding='utf8') as f:
        json.dump(report, f, indent=2, allow_nan=False)
print(json.dumps(dict(passed=report['passed'], groups=len(groups), refusals=len(refused), actual_migration=False)))
