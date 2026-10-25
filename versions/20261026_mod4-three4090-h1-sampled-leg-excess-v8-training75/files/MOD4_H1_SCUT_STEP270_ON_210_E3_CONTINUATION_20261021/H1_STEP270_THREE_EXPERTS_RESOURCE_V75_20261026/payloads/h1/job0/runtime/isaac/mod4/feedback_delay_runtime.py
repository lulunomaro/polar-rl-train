"""Isolated D3 actor feedback adapter. No plant, critic, action or trainer changes."""
import os
import torch
from isaaclab.managers import EventTermCfg, SceneEntityCfg
from mod4_env import Mod4Env
import mod4_task as task
from sensor_a0_runtime import configure_sensor, state as sensor_state
from feedback_delay_mild import FeedbackDelay, WIDTHS


def delay_state(env):
    if not hasattr(env, '_feedback_delay_mild'):
        env._feedback_delay_mild = FeedbackDelay(
            env.num_envs, env.device, env.cfg.seed, env.cfg.feedback_delay_enabled)
    return env._feedback_delay_mild


def reset_feedback(env, env_ids):
    ids = torch.arange(env.num_envs, device=env.device) if env_ids is None else env_ids
    sensor_state(env).reset(ids)
    delay_state(env).reset(ids)


def feedback(env, key, raw):
    tick = env.common_step_counter
    noisy = sensor_state(env).apply(key, raw, tick)
    return delay_state(env).apply(key, noisy, tick)


def base_ang_vel(env, asset_cfg=SceneEntityCfg('robot')):
    return feedback(env, 'base_ang_vel', task.mdp_obs.base_ang_vel(env, asset_cfg=asset_cfg))


def projected_gravity(env, asset_cfg=SceneEntityCfg('robot')):
    return feedback(env, 'projected_gravity', task.mdp_obs.projected_gravity(env, asset_cfg=asset_cfg))


def leg_pos(env, asset_cfg, bias_key):
    assert bias_key == '_mod4_leg_bias' and task.OBS_DELAY_MAX == 0
    assert getattr(env, bias_key, None) is None
    return feedback(env, 'leg_pos', task.mdp_obs.joint_pos_rel(env, asset_cfg=asset_cfg))


def joint_vel(env, asset_cfg, key):
    return feedback(env, key, task.mdp_obs.joint_vel_rel(env, asset_cfg=asset_cfg))


def configure_feedback(cfg, enabled):
    configure_sensor(cfg, os.environ.get('RM_SENSOR_PROFILE', 'noise_bias_mild_v1'))
    assert task.DR_OFF and task.OBS_DELAY_MAX == task.ACTION_DELAY_MAX == 0
    cfg.feedback_delay_enabled = bool(enabled)
    p = cfg.observations.policy
    p.base_ang_vel.func = base_ang_vel
    p.projected_gravity.func = projected_gravity
    p.leg_pos.func = leg_pos
    p.leg_vel.func = joint_vel
    p.wheel_vel.func = joint_vel
    # Replace the single existing bias-reset event; never reset its stream twice.
    cfg.events.sensor_mild_episode_bias = EventTermCfg(func=reset_feedback, mode='reset')


class DelaySensorMod4Env(Mod4Env):
    def __init__(self, *args, **kwargs):
        assert not args and 'cfg' in kwargs
        profile = os.environ.get('RM_FEEDBACK_DELAY_PROFILE', 'off')
        assert profile in ('off', 'control_0_10ms_v1')
        configure_feedback(kwargs['cfg'], profile == 'control_0_10ms_v1')
        super().__init__(**kwargs)
        assert sum(self.observation_manager.group_obs_dim['policy']) == 35
        assert sum(self.observation_manager.group_obs_dim['critic']) == 38

    def clean_policy(self):
        sensor, delay = sensor_state(self), delay_state(self)
        old_profile, old_enabled = sensor.profile, delay.enabled
        sensor.profile, delay.enabled = 'off', False
        try:
            return self.observation_manager.compute_group('policy').clone()
        finally:
            sensor.profile, delay.enabled = old_profile, old_enabled

    def feedback_delay_recipe(self):
        d = delay_state(self)
        return dict(profile='control_0_10ms_v1' if d.enabled else 'off',
                    actor_feedback_channels=list(WIDTHS), control_period_us=10000,
                    requested_delay_us=[0, 10000], sample_before_original_manager_scale=True,
                    noise_and_episode_bias_before_queue=True, clean_critic=True,
                    commands_last_action_height_mode_wheel_position_not_delayed=True,
                    BODY_components_kept_in_sample_frame_no_apply_frame_rotation=True,
                    reset_warmup_actual_age_us=0, no_50Hz_sampling_claimed=True,
                    action_delay_us=0, engineering_pressure_not_hardware_calibration=True)

    def sensor_sdk_audit(self):
        """Actual manager output against actual queued samples, not clean current truth."""
        sensor, delay = sensor_state(self), delay_state(self)
        tick = int(self.common_step_counter)
        actor = self.observation_manager.compute_group('policy').clone()
        critic = self.observation_manager.compute_group('critic').clone()
        counts, rng = dict(sensor.draw_counts), delay.rng.get_state().clone()
        actor2 = self.observation_manager.compute_group('policy')
        assert torch.equal(actor, actor2) and counts == sensor.draw_counts
        assert torch.equal(rng, delay.rng.get_state())
        clean = self.clean_policy()
        assert torch.equal(critic, self.observation_manager.compute_group('critic'))
        expected, offset, receipts = clean.clone(), 0, {}
        for name, dims in zip(self.observation_manager.active_terms['policy'],
                              self.observation_manager.group_obs_term_dim['policy']):
            width = int(dims[0])
            if name in WIDTHS:
                scale = .5 if name == 'base_ang_vel' else .1 if name in ('leg_vel', 'wheel_vel') else 1.
                if delay.enabled:
                    assert bool((delay.cache[name]['last'] == tick).all())
                    expected[:, offset:offset + width] = delay.cache[name]['out'] * scale
                    r = delay.receipt(name, tick)
                    receipts[name] = {k: (v.cpu().tolist() if torch.is_tensor(v) else v)
                                      for k, v in r.items()}
                elif sensor.profile != 'off':
                    last, noise = sensor.cache[name]
                    assert bool((last == tick).all())
                    expected[:, offset:offset + width] += (noise + (sensor.bias if name == 'leg_pos' else 0.)) * scale
            offset += width
        error = float((actor - expected).abs().max())
        assert error <= 2e-6, error
        assert torch.equal(actor[:, :4], clean[:, :4])
        assert torch.equal(actor[:, 14:16], clean[:, 14:16])
        assert torch.equal(actor[:, 22:], clean[:, 22:])
        return dict(tick=tick, actor35=True, critic38_clean=True,
                    command_lastaction_mode_wheel_slots_exact=True,
                    formula_max_error=error, same_tick_draws_unchanged=True,
                    actual_feedback_sample_apply=receipts,
                    delay_recipe=self.feedback_delay_recipe(),
                    SDK_is_feedback_readback_not_skill_graduation=True)
