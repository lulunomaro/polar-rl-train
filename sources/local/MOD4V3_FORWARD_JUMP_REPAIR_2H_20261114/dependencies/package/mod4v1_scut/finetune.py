"""Explicit MOD4 E0 weights-only initialization, matching SCUT's finetune mode.

This is a new task, not a full-state continuation. The source file is immutable.
Critic38 columns are mapped by meaning into critic78; new privilege columns start
at zero. Adam and iteration remain fresh, as in the pinned SCUT finetune entry.
"""
import hashlib
import io
import os
from pathlib import Path
import torch


def migrate_weights(runner, saved):
    """Load either SCUT's packed model_state_dict or MOD4's split E0 schema."""
    if 'model_state_dict' in saved and 'actor_state_dict' not in saved:
        packed = saved['model_state_dict']
        actor = {}
        critic = {}
        for key, value in packed.items():
            if key == 'std':
                actor['distribution.std_param'] = value
            elif key.startswith('actor.'):
                actor['mlp.'+key[len('actor.'):]] = value
            elif key.startswith('critic.'):
                critic['mlp.'+key[len('critic.'):]] = value
        if not actor or not critic:
            raise ValueError('Packed SCUT checkpoint has no actor/critic tensors')
        runner.alg.actor.load_state_dict(actor, strict=True)
        runner.alg.critic.load_state_dict(critic, strict=True)
        if runner.alg.optimizer.state:
            raise ValueError('Weights-only initialization requires a fresh Adam')
        runner.current_learning_iteration = 0
        return dict(kind='SCUT_PACKED_WEIGHTS_ONLY_FINETUNE',
            actor35_strict=True, critic78_strict=True,
            actor_interface_scope='SCUT 35/78/6 schema mapped into RSL5 MLPModel',
            source_optimizer_loaded=False, source_iteration_loaded=False,
            new_Adam_states=len(runner.alg.optimizer.state), new_iteration=0,
            source_STD_preserved=True, source_checkpoint_unchanged=True)
    actor = saved['actor_state_dict']
    source_std = actor.get('distribution.std_param', torch.empty(0))
    runner.alg.actor.load_state_dict(actor, strict=True)
    source = saved['critic_state_dict']
    target = runner.alg.critic.state_dict()
    first = [k for k,v in source.items() if v.ndim == 2 and v.shape[1] == 38
             and k in target and target[k].shape == (v.shape[0],78)]
    if len(first) != 1:
        raise ValueError('Expected exactly one known critic38 input matrix')
    name = first[0]
    # target: base28, velocity3(raw m/s), height1, mode7, privilege39.
    # E0 source: cmd/height/omega7, velocity3(*.5), remaining base21, mode7.
    columns = [(i,i,1.) for i in range(7)]
    columns += [(i,28+i-7,.5) for i in range(7,10)]
    columns += [(i,i-3,1.) for i in range(10,31)]
    columns += [(i,i+1,.2 if i==36 else 1.) for i in range(31,38)]
    for key,value in source.items():
        if key == name:
            mapped = torch.zeros_like(target[key])
            for old,new,scale in columns:
                mapped[:,new] = value[:,old] * scale
            target[key] = mapped
        elif key not in target or value.shape != target[key].shape:
            raise ValueError('Unexpected E0 critic tensor: '+key)
        else:
            target[key] = value
    if set(source) != set(target):
        raise ValueError('Unexpected E0 critic state schema')
    runner.alg.critic.load_state_dict(target, strict=True)
    if runner.alg.optimizer.state:
        raise ValueError('Weights-only initialization requires a fresh Adam')
    runner.current_learning_iteration = 0
    # Deterministic CPU algebra check; no random stream advance or physical step.
    x = torch.linspace(-.4,.4,78,device=target[name].device).repeat(3,1)
    original = torch.zeros(3,38,device=x.device)
    for old,new,scale in columns:
        original[:,old] = x[:,new]*scale
    error = (original @ source[name].to(x.device).T - x @ target[name].T).abs().max().item()
    if error > 2.e-5:
        raise ValueError('Critic input mapping changed preactivation')
    result = dict(kind='SCUT_STYLE_WEIGHTS_ONLY_FINETUNE',actor35_strict=True,
        actor_interface_scope='Shared base28 locomotion; source E0 mode onehot and SCUT mode auxiliaries differ explicitly',
        critic38_to78_named_columns=columns,critic_new_columns_zero=True,
        critic_preactivation_max_error=error,source_STD_preserved=True,
        source_optimizer_loaded=False,source_iteration_loaded=False,
        new_Adam_states=len(runner.alg.optimizer.state),new_iteration=0,
        source_checkpoint_unchanged=True)
    reset_std = os.environ.get('E0_RESET_STD', '').strip()
    if reset_std:
        value = float(reset_std)
        with torch.no_grad():
            runner.alg.actor.distribution.std_param.fill_(value)
        result.update(source_STD_preserved=False, reset_std=value,
                      original_STD=[float(x) for x in source_std.detach().cpu().reshape(-1)])
    return result


def initialize(runner, path, expected_sha, expected_bytes):
    raw = Path(path).read_bytes()
    if len(raw) != expected_bytes or hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError('Pinned enhanced MOD4v1 E0 checkpoint identity mismatch')
    saved = torch.load(io.BytesIO(raw), map_location=runner.device, weights_only=False)
    result = migrate_weights(runner,saved)
    result.update(source_path=str(path),source_SHA=expected_sha,source_bytes=len(raw),
                  source_file_opens=1,source_model_decodes=1)
    return result
