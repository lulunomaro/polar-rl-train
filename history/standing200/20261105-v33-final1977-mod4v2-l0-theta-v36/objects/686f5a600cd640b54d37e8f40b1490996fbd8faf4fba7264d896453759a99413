"""One full checkpoint write; restore learning and streams, then ONE fresh reset.

Original physical nominals belong to the new USD constructor and are never
overwritten by saved mass/COM/inertia. PhysX itself is explicitly not resumed.
"""
import os
import hashlib
import random
import io
from pathlib import Path
import numpy as np
import torch

from .config import USD_SHA, CONTRACT_SHA

COMPONENTS = ('_sensor_mild', '_feedback_delay_mild', '_physics_action_delay',
              '_spring_pressure', '_gas_damping', '_chassis_com', '_explicit_pd')
FORMAT = 'MOD4V1_SCUT_FULL_V2'
INTERFACE = 'actor28_mode7__critic28_velocity3_height1_mode7_priv39__scut_done_command_v2'


def named_rngs(obj):
    return {key: value.get_state().clone() for key, value in vars(obj).items()
            if isinstance(value, torch.Generator)}


def restore_named(obj, states):
    actual = {key: value for key, value in vars(obj).items() if isinstance(value, torch.Generator)}
    if set(actual) != set(states):
        raise ValueError('Named RNG schema mismatch')
    for key, value in actual.items():
        value.set_state(states[key].cpu())


def learning_state(runner):
    return dict(**runner.alg.save(), iter=runner.current_learning_iteration,
                learning_rate=runner.alg.learning_rate)


def tensor_fields(obj):
    return {key: value.clone() for key, value in vars(obj).items() if torch.is_tensor(value)}


def save(runner, env, bridge, path, profile):
    data = learning_state(runner)
    data.update(format=FORMAT, interface=INTERFACE, usd_SHA=USD_SHA, contract_SHA=CONTRACT_SHA,
                profile=profile, num_envs=env.num_envs, actor_dim=35, critic_dim=78,
                components={key: getattr(env, key).state_dict() for key in COMPONENTS},
                command_rng=named_rngs(env.command_manager.get_term('twist')),
                command_fields=tensor_fields(env.command_manager.get_term('twist')),
                physical_rng=named_rngs(env._mild_dr),
                physical_episode={key: getattr(env._mild_dr, key).clone()
                                  for key in ('factor', 'nominal', 'mu', 'reset_count')},
                motor_episode_gain={key: value.clone() for key, value in env._mild_dr.output.items()},
                cpu_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state_all(),
                python_rng=random.getstate(), numpy_rng=np.random.get_state(),
                source_reward_state={key: value.clone() for key, value in vars(bridge.reward).items()
                                     if torch.is_tensor(value)},
                source_reward_dicts={key: {k:v.clone() for k,v in getattr(bridge.reward,key,{}).items()}
                                     for key in ('_episode_sums', '_last_reward_terms')},
                resume_scope='Complete learning/DR streams then one fresh physical episode; not PhysX state',
                physics_ticks=bridge.physics_ticks)
    output = Path(path)
    temporary = output.with_name(output.name+'.partial')
    torch.save(data, temporary)
    with temporary.open('rb') as stream:
        digest = hashlib.file_digest(stream,'sha256').hexdigest()
    size = temporary.stat().st_size
    os.replace(temporary, output)
    return dict(path=str(output),bytes=size,SHA=digest,format=FORMAT,
                iteration=runner.current_learning_iteration,physics_ticks=bridge.physics_ticks)


def restore(runner, env, bridge, path, profile):
    data = torch.load(path, map_location='cpu', weights_only=False)
    if (data.get('format') != FORMAT or data.get('interface') != INTERFACE or data['usd_SHA'] != USD_SHA
            or data['contract_SHA'] != CONTRACT_SHA or data['profile'] != profile
            or data['num_envs'] != env.num_envs or data['actor_dim'] != 35 or data['critic_dim'] != 78):
        raise ValueError('Checkpoint is not this MOD4v1 SCUT interface; no automatic input expansion')
    runner.alg.load(data, load_cfg=None, strict=True)
    runner.current_learning_iteration = data['iter']
    runner.alg.learning_rate = data['learning_rate']
    for group in runner.alg.optimizer.param_groups:
        group['lr'] = data['learning_rate']
    for key in COMPONENTS:
        getattr(env, key).load_state_dict(data['components'][key])
    restore_named(env.command_manager.get_term('twist'), data['command_rng'])
    command = env.command_manager.get_term('twist')
    for key, value in data['command_fields'].items():
        current = getattr(command, key)
        if current.shape != value.shape:
            raise ValueError('Command tensor schema mismatch: '+key)
        current.copy_(value)
    if hasattr(command, 'set_training_iteration'):
        command.set_training_iteration(runner.current_learning_iteration)
    restore_named(env._mild_dr, data['physical_rng'])
    for key, value in data['physical_episode'].items():
        getattr(env._mild_dr, key).copy_(value)
    for key, value in data['motor_episode_gain'].items():
        env._mild_dr.output[key].copy_(value)
    torch.set_rng_state(data['cpu_rng'])
    torch.cuda.set_rng_state_all(data['cuda_rng'])
    random.setstate(data['python_rng'])
    np.random.set_state(data['numpy_rng'])
    # Full queue restoration is complete before a new-scene clock rebase.
    for group in env._physics_action_delay.queue.groups.values():
        group['last_apply_tick'].fill_(-1)
    # Do not restore old contact/state windows into the fresh physical episode.
    return env.reset()


def restore_resized_learning(runner,path,expected_sha,expected_bytes,profile,new_envs):
    """Keep complete PPO state; population-dependent DR queues start fresh.

    A new population cannot restore80 rows into20000 actors. The old full file
    remains intact, and this boundary is explicitly recorded as fresh physical
    DR/queues, not exact simulator or per-environment random-stream continuation.
    """
    raw=Path(path).read_bytes()
    if len(raw)!=expected_bytes or hashlib.sha256(raw).hexdigest()!=expected_sha:
        raise ValueError('Resized learning source identity mismatch')
    data=torch.load(io.BytesIO(raw),map_location=runner.device,weights_only=False)
    if (data.get('format')!=FORMAT or data.get('interface')!=INTERFACE or data['profile']!=profile
        or data['usd_SHA']!=USD_SHA or data['contract_SHA']!=CONTRACT_SHA):
        raise ValueError('Resized continuation interface mismatch')
    runner.alg.load(data,load_cfg=None,strict=True)
    runner.current_learning_iteration=data['iter'];runner.alg.learning_rate=data['learning_rate']
    for group in runner.alg.optimizer.param_groups:group['lr']=data['learning_rate']
    torch.set_rng_state(data['cpu_rng'].cpu());torch.cuda.set_rng_state_all([r.cpu() for r in data['cuda_rng']])
    random.setstate(data['python_rng']);np.random.set_state(data['numpy_rng'])
    return dict(kind='FULL_PPO_RESIZED_POPULATION_FRESH_PHYSICS',source_path=str(path),source_SHA=expected_sha,
        source_bytes=len(raw),source_model_decodes=1,source_envs=data['num_envs'],new_envs=new_envs,
        actor_critic_STD_Adam_LR_iteration_restored=True,source_iteration=data['iter'],
        optimizer_state_entries=len(runner.alg.optimizer.state),global_RNG_restored=True,
        per_environment_DR_queues_fresh=True,per_environment_DR_RNG_same_stream=False,old_full_checkpoint_preserved=True)
