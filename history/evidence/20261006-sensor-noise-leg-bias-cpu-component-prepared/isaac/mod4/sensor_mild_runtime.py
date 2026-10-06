"""Isolated mild noise/episode leg zero-bias component on the retained mix.

This module is not a deployed training entry. Critic truth, wheel zero slots,
commands, plant, rewards, hardware and existing physical DR stay unchanged.
"""
import torch
from isaaclab.managers import EventTermCfg,SceneEntityCfg
from retention_mix_runtime import RetentionMixEnv,configure_retention
from sensor_mild_math import SensorCorruption,CHANNELS,PROFILES
import mod4_task as task

def state(env):
    if not hasattr(env,'_sensor_mild'):
        env._sensor_mild=SensorCorruption(env.num_envs,env.device,env.cfg.seed,env.cfg.sensor_mild_profile)
    return env._sensor_mild

def reset_sensor(env,env_ids):
    ids=torch.arange(env.num_envs,device=env.device) if env_ids is None else env_ids
    state(env).reset(ids)

def base_ang_vel(env,asset_cfg=SceneEntityCfg('robot')):
    return state(env).apply('base_ang_vel',task.mdp_obs.base_ang_vel(env,asset_cfg=asset_cfg),env.common_step_counter)

def projected_gravity(env,asset_cfg=SceneEntityCfg('robot')):
    return state(env).apply('projected_gravity',task.mdp_obs.projected_gravity(env,asset_cfg=asset_cfg),env.common_step_counter)

def leg_pos(env,asset_cfg,bias_key):
    assert bias_key=='_mod4_leg_bias' and task.OBS_DELAY_MAX==0
    assert getattr(env,bias_key,None) is None,'Legacy bias must remain disabled'
    return state(env).apply('leg_pos',task.mdp_obs.joint_pos_rel(env,asset_cfg=asset_cfg),env.common_step_counter)

def joint_vel(env,asset_cfg,key):
    return state(env).apply(key,task.mdp_obs.joint_vel_rel(env,asset_cfg=asset_cfg),env.common_step_counter)

def configure_sensor(cfg,profile):
    assert profile in PROFILES and task.DR_OFF and task.OBS_DELAY_MAX==task.ACTION_DELAY_MAX==0
    recipe=configure_retention(cfg);cfg.sensor_mild_profile=profile
    policy=cfg.observations.policy
    policy.base_ang_vel.func=base_ang_vel;policy.projected_gravity.func=projected_gravity
    policy.leg_pos.func=leg_pos;policy.leg_vel.func=joint_vel;policy.wheel_vel.func=joint_vel
    for key in CHANNELS:assert getattr(policy,key).noise is None
    cfg.events.sensor_mild_episode_bias=EventTermCfg(func=reset_sensor,mode='reset')
    recipe.update(sensor_profile=profile,raw_noise_bounds={k:v[1] for k,v in CHANNELS.items()},
        encoder_bias_scope='Four actor leg-position channels only; wheel position slots remain zero',
        critic_clean=True,physical_state_reward_command_unmodified=True,noise_and_bias_RNG_independent=True,
        observation_delay_action_delay_steps=0,component_only_not_training_deployment=True)
    return recipe

class SensorRetentionEnv(RetentionMixEnv):
    pass
