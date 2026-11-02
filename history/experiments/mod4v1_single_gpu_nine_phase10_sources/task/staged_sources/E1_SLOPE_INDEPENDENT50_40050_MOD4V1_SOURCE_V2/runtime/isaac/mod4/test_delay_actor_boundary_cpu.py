"""CPU integration fixture for the real adapter and original sensor/queue modules."""
import sys
import types
import json
import torch
from types import SimpleNamespace as NS

torch.set_num_threads(1)
assert not torch.cuda.is_initialized()
manager = types.ModuleType('isaaclab.managers')
manager.EventTermCfg = lambda **kwargs: NS(**kwargs)
manager.SceneEntityCfg = lambda *args, **kwargs: NS(args=args, **kwargs)
sys.modules['isaaclab'] = types.ModuleType('isaaclab')
sys.modules['isaaclab.managers'] = manager
mod4 = types.ModuleType('mod4_env');mod4.Mod4Env = object
sys.modules['mod4_env'] = mod4
task = types.ModuleType('mod4_task')
task.DR_OFF = True;task.OBS_DELAY_MAX = task.ACTION_DELAY_MAX = 0
task.mdp_obs = NS()
sys.modules['mod4_task'] = task
import feedback_delay_runtime as actual
from sensor_mild_math import SensorCorruption, CHANNELS
from feedback_delay_mild import FeedbackDelay, WIDTHS

n = 12
env = NS(num_envs=n, device='cpu', cfg=NS(seed=19, sensor_mild_profile='noise_bias_mild_v1', feedback_delay_enabled=True), common_step_counter=0)
passed = []
before = torch.random.get_rng_state().clone()
actual.reset_feedback(env, torch.arange(n))
assert torch.equal(before, torch.random.get_rng_state())
sensor, delay = actual.sensor_state(env), actual.delay_state(env)
delay.delay[:6] = 0;delay.delay[6:] = 1
past = {}
for tick in range(5):
    env.common_step_counter = tick
    for name, width in WIDTHS.items():
        raw = torch.arange(n * width).reshape(n, width).float() / 100 + tick
        saved = raw.clone()
        out = actual.feedback(env, name, raw)
        noisy = sensor.apply(name, raw, tick)
        expected = noisy.clone()
        if tick:
            expected[6:] = past[name][6:]
        assert torch.equal(out, expected) and torch.equal(raw, saved)
        past[name] = noisy.clone()
        counts = dict(sensor.draw_counts);rng = delay.rng.get_state().clone()
        assert torch.equal(out, actual.feedback(env, name, raw + 999))
        assert counts == sensor.draw_counts and torch.equal(rng, delay.rng.get_state())
passed += ['actual_sensor_noise_bias_then_queue_order', 'all_five_channels_zero_or_10000us',
           'raw_plant_input_unchanged', 'manager_same_tick_recompute_does_not_redraw_or_advance']

snap = delay.state_dict();bias = sensor.bias.clone();episode = sensor.episode.clone()
ids = torch.tensor([1, 7]);other = torch.tensor([i for i in range(n) if i not in [1, 7]])
actual.reset_feedback(env, ids)
for name, width in WIDTHS.items():
    raw = torch.full((n, width), 90.)
    actual.feedback(env, name, raw)
    assert all(torch.equal(delay.cache[name][k][other], v[other]) for k, v in snap['cache'][name].items())
    assert bool((delay.receipt(name, 4)['actual_age_us'][ids] == 0).all())
assert torch.equal(bias[other], sensor.bias[other]) and torch.equal(episode[other], sensor.episode[other])
assert torch.equal(sensor.episode[ids], episode[ids] + 1)
passed += ['selected_reset_other_rows_and_sensor_streams_exact', 'warmup_uses_new_episode_current_sample',
           'single_combined_event_resets_bias_once']

# Real adapter manager layout/scale boundary, with a CPU fake plant only.
terms = [('commands', 3), ('height_command', 1), ('base_ang_vel', 3), ('projected_gravity', 3),
         ('leg_pos', 4), ('wheel_pos_slots', 2), ('leg_vel', 4), ('wheel_vel', 2),
         ('last_action', 6), ('mode_onehot', 7)]
class FixtureManager:
    active_terms = {'policy': [x[0] for x in terms]}
    group_obs_term_dim = {'policy': [(x[1],) for x in terms]}
    def compute_group(self, group):
        if group == 'critic':return torch.arange(n * 38).reshape(n, 38).float()
        rows = []
        for name, width in terms:
            raw = torch.full((n, width), .25 + env.common_step_counter / 100.)
            if name in WIDTHS:
                raw = actual.feedback(env, name, raw)
                raw = raw * (.5 if name == 'base_ang_vel' else .1 if name in ('leg_vel', 'wheel_vel') else 1.)
            rows.append(raw)
        return torch.cat(rows, dim=1)
env.observation_manager = FixtureManager()
env.clean_policy = types.MethodType(actual.DelaySensorMod4Env.clean_policy, env)
env.feedback_delay_recipe = types.MethodType(actual.DelaySensorMod4Env.feedback_delay_recipe, env)
env.common_step_counter = 5
audit = actual.DelaySensorMod4Env.sensor_sdk_audit(env)
assert audit['formula_max_error'] <= 2e-6 and audit['critic38_clean']
passed += ['manager_original_scale_after_queue', 'clean_critic_and_unaffected_actor_slots',
           'clean_policy_query_does_not_advance_corruption_or_delay']

cfg = NS(observations=NS(policy=NS(**{k:NS(noise=None) for k in CHANNELS})), events=NS())
actual.configure_feedback(cfg, True)
assert cfg.events.sensor_mild_episode_bias.func is actual.reset_feedback
assert cfg.feedback_delay_enabled and cfg.sensor_mild_profile == 'noise_bias_mild_v1'
passed.append('actual_config_replaces_existing_event_without_duplicate_reset')

delay.enabled = False
env.common_step_counter = 6
for name, width in WIDTHS.items():
    raw = torch.randn(n, width)
    expected = sensor.apply(name, raw, 6)
    assert torch.equal(expected, actual.feedback(env, name, raw))
passed.append('delay_off_exact_original_noise_bias_actor')
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True, contracts=passed, count=len(passed), no_CUDA_initialized=True,
                      actual_SDK=False, PPO_deployed=False, plant_fixture_only=True)))
