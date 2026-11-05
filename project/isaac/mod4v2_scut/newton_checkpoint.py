"""Full learner and random-stream continuation across the explicit backend switch."""
from pathlib import Path
import hashlib
import os
import random

import numpy as np
import torch

COMPONENTS=('_sensor_mild','_feedback_delay_mild','_physics_action_delay',
            '_spring_pressure','_gas_damping','_chassis_com','_explicit_pd')
FORMAT='MOD4V2_FUDAN_NEWTON_FULL_V1'
SOURCE_FORMAT='MOD4V2_SCUT_HW300N60_FULL_V1'


def restore(runner,env,path,expected_sha):
    with Path(path).open('rb')as f:
        assert hashlib.file_digest(f,'sha256').hexdigest()==expected_sha
    data=torch.load(path,map_location='cpu',weights_only=False)
    assert data['format']in (SOURCE_FORMAT,FORMAT)
    assert data['num_envs']==env.num_envs and data['actor_dim']==35 and data['critic_dim']==78
    assert data['reward_family']=='FUDAN_JUMP'
    assert data['contract_SHA']=='00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e'
    runner.alg.load(data,load_cfg=None,strict=True)
    runner.current_learning_iteration=data['iter']
    runner.alg.learning_rate=data['learning_rate']
    for group in runner.alg.optimizer.param_groups:group['lr']=data['learning_rate']
    for name in COMPONENTS:getattr(env,name).load_state_dict(data['components'][name])
    fields=data['command_fields']
    for name,value in fields.items():
        target=getattr(env.command,name)
        assert target.shape==value.shape,(name,target.shape,value.shape)
        target.copy_(value.to(target.device))
    env.command.set_training_iteration(data['iter'])
    streams=data['physical_rng']
    env.rng.set_state(streams['generator'].cpu())
    env.cpu_generator.set_state(streams['cpu_generator'].cpu())
    for key,name in [('factor','mass_factor'),('nominal','nominal'),('mu','friction'),('reset_count','reset_count')]:
        getattr(env,name).copy_(data['physical_episode'][key].to(env.device))
    env.motor_gain.copy_(torch.cat([data['motor_episode_gain'][k]for k in ('legs','wheels')],-1).to(env.device))
    torch.set_rng_state(data['cpu_rng'].cpu())
    torch.cuda.set_rng_state_all([s.cpu()for s in data['cuda_rng']])
    random.setstate(data['python_rng']);np.random.set_state(data['numpy_rng'])
    for key,value in data['source_global_counters'].items():setattr(env.reward,key,int(value))
    for group in env._physics_action_delay.groups.values():group['last_apply_tick'].fill_(-1)
    env.reset(torch.arange(env.num_envs,device=env.device))
    env._last_observations=None
    steps=[int(s['step'])for s in runner.alg.optimizer.state.values()]
    assert len(steps)==17 and min(steps)==max(steps)==data['iter']*20
    return dict(source_path=str(path),source_SHA=expected_sha,source_iteration=data['iter'],
        optimizer_entries=17,optimizer_steps=min(steps),learning_rate=data['learning_rate'],
        actor_critic_STD_Adam_LR_restored=True,all7_components_and_RNG_queues_restored=True,
        command_fields_restored=list(fields),source_backend=data.get('physics_backend','PhysX_TGS32_4'),
        target_backend='Newton/SolverMuJoCo/MuJoCo-Warp',backend_changed=data['format']!=FORMAT,
        new_constructor_nominals_retained=True,fresh_physical_reset=True,physical_state_restored=False)


def save(runner,env,path):
    from .config import ACTION_INTERFACE,TARGET_INTERFACE,USD_SHA,CONTRACT_SHA
    value=dict(**runner.alg.save(),iter=runner.current_learning_iteration,
        learning_rate=runner.alg.learning_rate,format=FORMAT,
        interface='actor35_critic78__MOD4V2_FUDAN_NEWTON',action_clip=6.,
        action_interface=ACTION_INTERFACE,target_interface=TARGET_INTERFACE,
        usd_SHA=USD_SHA,contract_SHA=CONTRACT_SHA,
        profile='jump200',num_envs=env.num_envs,actor_dim=35,critic_dim=78,
        reward_family='FUDAN_JUMP',reward_source_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',
        physics_backend='Newton/SolverMuJoCo/MuJoCo-Warp',
        components={k:getattr(env,k).state_dict()for k in COMPONENTS},
        command_rng={},command_fields={k:v.clone()for k,v in vars(env.command).items()if torch.is_tensor(v)},
        physical_rng=dict(generator=env.rng.get_state(),cpu_generator=env.cpu_generator.get_state()),
        physical_episode=dict(factor=env.mass_factor.clone(),nominal=env.nominal.clone(),
                              mu=env.friction.clone(),reset_count=env.reset_count.clone()),
        motor_episode_gain=dict(legs=env.motor_gain[:,:4].clone(),wheels=env.motor_gain[:,4:].clone()),
        cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
        python_rng=random.getstate(),numpy_rng=np.random.get_state(),
        source_reward_state={k:v.clone()for k,v in vars(env.reward).items()if torch.is_tensor(v)},
        source_reward_dicts={key:{k:v.clone()for k,v in getattr(env.reward,key,{}).items()}
                             for key in ('_episode_sums','_last_reward_terms')},
        source_global_counters={k:int(getattr(env.reward,k))for k in ('_value_debug_step','common_step_counter')},
        physics_ticks=env.physics_ticks,newton_source=env.plant.receipt,
        resume_scope='Full PPO/DR/RNG/queue continuation, then one fresh physical episode')
    path=Path(path);tmp=path.with_name(path.name+'.partial')
    with tmp.open('wb')as f:torch.save(value,f);f.flush();os.fsync(f.fileno())
    with tmp.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    os.replace(tmp,path)
    return dict(path=str(path),bytes=path.stat().st_size,SHA=digest,format=FORMAT,
                iteration=runner.current_learning_iteration,physics_ticks=env.physics_ticks)
