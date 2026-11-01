"""Source-only35->44/38->47 input migration, with explicit optimizer identities.

No checkpoint/raw/SDK loader, live-model update or optimizer construction/step.
No implicit source/target parameter-ID order or shape-based ownership inference.
"""
from copy import deepcopy
import torch

SOURCE_TEACHER_SHA = '0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'
ACTOR_KEYS = tuple(f'mlp.{i}.{p}' for i in (0, 2, 4, 6) for p in ('weight', 'bias')) + ('distribution.std_param',)
CRITIC_KEYS = tuple(f'mlp.{i}.{p}' for i in (0, 2, 4, 6) for p in ('weight', 'bias'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def qualified(scope, key):
    return scope + ':' + key


def expected_shapes(scope, input_width):
    output = 6 if scope == 'actor' else 1
    shapes = {}
    for i, (a, b) in zip((0, 2, 4, 6), ((input_width, 128), (128, 64), (64, 32), (32, output))):
        shapes[f'mlp.{i}.weight'] = (b, a)
        shapes[f'mlp.{i}.bias'] = (b,)
    if scope == 'actor':
        shapes['distribution.std_param'] = (6,)
    return shapes


def validate_weights(state, scope, width):
    shapes = expected_shapes(scope, width)
    require(isinstance(state, dict) and set(state) == set(shapes), 'Explicit original8MLP+STD/8critic keys required')
    for key, shape in shapes.items():
        value = state[key]
        require(torch.is_tensor(value) and value.shape == shape and value.dtype == torch.float32
            and bool(torch.isfinite(value).all()), 'Wrong/nonfinite weight ' + qualified(scope, key))
    if scope == 'actor':
        require(bool((state['distribution.std_param'] > 0).all()), 'Preserve valid learned STD6, never reset it')


def append9_zero_columns(value):
    require(torch.is_tensor(value) and value.ndim == 2 and value.shape[1] in (35, 38), 'Explicit first-layer35/38 matrix required')
    out = value.new_zeros((value.shape[0], value.shape[1] + 9))
    out[:, :value.shape[1]].copy_(value.detach())
    return out


@torch.no_grad()
def expand_weights(actor35, critic38):
    """Only the two first matrices change shape; all original values are copied."""
    validate_weights(actor35, 'actor', 35)
    validate_weights(critic38, 'critic', 38)
    actor44 = {k: v.detach().clone() for k, v in actor35.items()}
    critic47 = {k: v.detach().clone() for k, v in critic38.items()}
    actor44['mlp.0.weight'] = append9_zero_columns(actor35['mlp.0.weight'])
    critic47['mlp.0.weight'] = append9_zero_columns(critic38['mlp.0.weight'])
    return actor44, critic47


def _bindings(witness, expected_kind, expected_names, optimizer):
    require(isinstance(witness, dict) and witness.get('kind') == expected_kind
        and sha(witness.get('identity_receipt_SHA')), 'PENDING actual bound parameter-ID identity witness')
    records = witness.get('parameter_bindings')
    require(isinstance(records, list) and len(records) == len(expected_names), 'Complete named parameter bindings required')
    by_name, seen_ids = {}, set()
    for r in records:
        require(isinstance(r, dict) and r.get('scope') in ('actor', 'critic'), 'Explicit actor/critic scope required')
        name = qualified(r['scope'], r.get('state_key', ''))
        require(name in expected_names and name not in by_name, 'Duplicate/unknown canonical parameter name')
        pid, gi, pos = r.get('optimizer_id'), r.get('group_index'), r.get('group_position')
        require(type(pid) is int and pid >= 0 and pid not in seen_ids
            and type(gi) is int and 0 <= gi < len(optimizer['param_groups']), 'Duplicate/invalid optimizer ID or group')
        ids = optimizer['param_groups'][gi]['params']
        require(type(pos) is int and 0 <= pos < len(ids) and ids[pos] == pid, 'Witness does not bind actual saved group position')
        if 'param_names' in optimizer['param_groups'][gi]:
            require(r.get('parameter_name') == optimizer['param_groups'][gi]['param_names'][pos],
                    'Named optimizer group contradicts identity witness')
        by_name[name] = r
        seen_ids.add(pid)
    require(set(by_name) == set(expected_names), 'Incomplete named ownership')
    actual_ids = [pid for g in optimizer['param_groups'] for pid in g['params']]
    require(len(actual_ids) == len(set(actual_ids)) == len(expected_names) and set(actual_ids) == seen_ids,
            'Optimizer param_groups differ from explicit identity witness')
    return by_name


@torch.no_grad()
def prepare_split_plan(actor35, critic38, source_adam, source_witness, *, synthetic_CPU_test=False):
    """Partition17 once intoPi9/Critic8, after a real source-ID witness.

    The witness must be produced later by ROOT's actual restored object identity,
    original constructor/group-order evidence and cached source-state comparisons.
    A hash/kind/shape declaration alone is NOT evidence generated by this helper.
    """
    actor44, critic47 = expand_weights(actor35, critic38)
    states = {'actor': actor35, 'critic': critic38}
    names = [qualified(s, k) for s, keys in (('actor', ACTOR_KEYS), ('critic', CRITIC_KEYS)) for k in keys]
    require(isinstance(source_adam, dict) and set(source_adam) == {'state', 'param_groups'}, 'Original Adam state_dict required')
    kind = 'SYNTHETIC_SOURCE_ADAM_NAME_ID_BINDING_ONLY' if synthetic_CPU_test else 'ACTUAL_SOURCE_ADAM_NAME_ID_OBJECT_BINDING'
    bound = _bindings(source_witness, kind, names, source_adam)
    require(source_witness.get('source_teacher_SHA') == SOURCE_TEACHER_SHA
        and source_witness.get('source_iteration') == 2135 and source_witness.get('source_Adam_step') == 42940,
        'Qualified frozen teacher2135/42940 binding required')
    require(source_witness.get('saved_group_order_identity_verified') is True,
            'PENDING actual original group-order/object identity evidence; never infer from shape')
    require(sha(source_witness.get('source_fullstate_CPU_receipt_SHA')), 'Qualified fullstate source receipt required separately')
    ids = {r['optimizer_id'] for r in bound.values()}
    require(set(source_adam['state']) == ids and len(ids) == 17, 'All17 original Adam states required')
    plans = {s: dict(states_by_name={}, groups=[]) for s in ('actor', 'critic')}
    inverse = {r['optimizer_id']: name for name, r in bound.items()}
    for name, r in bound.items():
        source = states[r['scope']][r['state_key']]
        require(r.get('shape') == list(source.shape), 'Source witness shape mismatch')
        old = source_adam['state'][r['optimizer_id']]
        require(set(old) <= {'step', 'exp_avg', 'exp_avg_sq', 'max_exp_avg_sq'}
            and {'step', 'exp_avg', 'exp_avg_sq'} <= set(old), 'Unsupported/incomplete original Adam slot')
        step = old['step']
        require((torch.is_tensor(step) and step.numel() == 1 and bool(torch.isfinite(step).all())
                and float(step) == 42940) or (type(step) in (int, float) and step == 42940), 'Original Adam step must be retained42940')
        copied = {'step': step.detach().clone() if torch.is_tensor(step) else step}
        for key in ('exp_avg', 'exp_avg_sq', 'max_exp_avg_sq'):
            if key not in old:
                continue
            value = old[key]
            require(torch.is_tensor(value) and value.shape == source.shape and value.dtype == source.dtype
                    and value.device == source.device and bool(torch.isfinite(value).all()), 'Moment does not match bound parameter ' + name)
            if key != 'exp_avg':
                require(bool((value >= 0).all()), 'Adam second moment cannot be negative')
            copied[key] = append9_zero_columns(value) if r['state_key'] == 'mlp.0.weight' else value.detach().clone()
        if source_adam['param_groups'][r['group_index']].get('amsgrad'):
            require('max_exp_avg_sq' in copied, 'Original AMSGrad slot missing')
        plans[r['scope']]['states_by_name'][name] = copied
    for gi, group in enumerate(source_adam['param_groups']):
        if 'param_names' in group:
            require(len(group['param_names']) == len(group['params']), 'Original param_names/group mismatch')
        for scope in ('actor', 'critic'):
            selected = [(pos, inverse[pid]) for pos, pid in enumerate(group['params']) if bound[inverse[pid]]['scope'] == scope]
            if not selected:
                continue
            options = deepcopy({k: v for k, v in group.items() if k not in ('params', 'param_names')})
            require(options.get('lr') == .0019461950683593758, 'Preserve actual frozen source LR')
            plans[scope]['groups'].append(dict(source_group_index=gi,
                names=[name for _, name in selected], options=options,
                source_param_names=([group['param_names'][i] for i, _ in selected] if 'param_names' in group else None)))
    require(len(plans['actor']['states_by_name']) == 9 and len(plans['critic']['states_by_name']) == 8,
            'Partition must bePi9/Critic8, not three copies of17')
    return dict(actor44_state_dict=actor44, critic47_state_dict=critic47, split_adam_plans=plans,
        source_identity_receipt_SHA=source_witness['identity_receipt_SHA'], synthetic_CPU_test=synthetic_CPU_test,
        source_fullstate_CPU_receipt_SHA=source_witness['source_fullstate_CPU_receipt_SHA'],
        metadata=dict(actor35_to44=True, critic38_to47=True, zero_suffix_columns=9,
            original_actor8_STD6_critic8_preserved=True, source_states_partitioned_once=17,
            Pi_states=9, critic_states=8, WM_optimizer_received_or_copied=False,
            actual_migration_admission=False, Pi_gradient_admission=False, complete_three_optimizer_conversion=False))


@torch.no_grad()
def bind_target_optimizer(plan, scope, target_adam, target_witness, *, synthetic_CPU_test=False):
    """Create loadable numeric-ID state only after actual target identity binding.

    ROOT constructs its target Adam groups from plan.group names/options, then
    records actual named objects and target state_dict IDs. No guessed IDs here.
    WM warm Adam is inherited separately; it is not an argument to this function.
    """
    require(scope in ('actor', 'critic') and plan['synthetic_CPU_test'] == synthetic_CPU_test, 'Wrong optimizer scope/mode')
    part = plan['split_adam_plans'][scope]
    require(isinstance(target_adam, dict) and set(target_adam) == {'state', 'param_groups'} and not target_adam['state'],
            'Fresh target optimizer identity needed; do not overwrite learned target moments')
    kind = 'SYNTHETIC_TARGET_ADAM_NAME_ID_BINDING_ONLY' if synthetic_CPU_test else 'ACTUAL_TARGET_ADAM_NAME_ID_OBJECT_BINDING'
    bound = _bindings(target_witness, kind, part['states_by_name'], target_adam)
    require(target_witness.get('source_identity_receipt_SHA') == plan['source_identity_receipt_SHA'], 'Source/target witness scope mismatch')
    require(target_witness.get('optimizer_scope') == scope, 'Target Pi/Critic identity differs')
    require(len(target_adam['param_groups']) == len(part['groups']), 'Target group partition differs')
    weights = plan['actor44_state_dict'] if scope == 'actor' else plan['critic47_state_dict']
    out_groups = []
    for gi, (group, expected) in enumerate(zip(target_adam['param_groups'], part['groups'])):
        options = {k: v for k, v in group.items() if k not in ('params', 'param_names')}
        require(options == expected['options'], 'Target Adam hyperparameters/LR changed')
        actual_names = [None] * len(group['params'])
        for name, r in bound.items():
            require(r.get('shape') == list(weights[r['state_key']].shape), 'Target parameter shape mismatch')
            if r['group_index'] == gi:
                actual_names[r['group_position']] = name
        require(actual_names == expected['names'], 'Target group/order differs from explicit split plan')
        out_groups.append(deepcopy(group))
    # Each original slot appears in exactly one scope. No full17 state is copied
    # into both outputs, and source/WM dictionaries are not nested in either.
    return dict(state={bound[name]['optimizer_id']: values for name, values in part['states_by_name'].items()},
                param_groups=out_groups)
