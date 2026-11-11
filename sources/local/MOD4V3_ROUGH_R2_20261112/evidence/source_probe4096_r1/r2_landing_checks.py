"""Bounded, frozen-weight physical probes for the new low-drop reset."""
import time
import torch
from tensordict import TensorDict
from .scut_flat_env import tensor


def run_probe(env, algorithm):
    start = time.time()
    if env.num_envs < 1024:
        # Isolate low-drop dynamics on a real flat tile, with both DR groups.
        env.terrain.terrain_levels.zero_()
        env.terrain.terrain_types.fill_(69)
        env.terrain_family = env.terrain.r1_column_families[env.terrain.terrain_types]
        env.flat_terrain_mask.fill_(True)
        env.r2_force_air = True
    env.reset()
    env.command_timer.fill_(10000.)
    initial = env.r2_summary()
    obs = env._get_observations()
    assert obs['policy'].shape == (env.num_envs,35)
    assert obs['critic'].shape == (env.num_envs,78)
    assert env.cfg.sim.dt == .0025 and env.cfg.decimation == 8
    assert env.enforce_closure_reset
    assert not env.reward.cfg.ctrl_mode_obs_enabled
    assert env.reward.cfg.rewards['track_lin_vel_xy_square'] == -1.5
    assert env.reward.cfg.rewards['track_lin_vel_xy'] == 1.2
    steps = 175 if env.num_envs < 1024 else 64
    actor = algorithm.get_policy()
    peak_velocity = 0.; peak_closure = 0.; action_error = 0.; mode_error = 0.
    for _ in range(steps):
        with torch.inference_mode():
            action = actor(TensorDict(obs,batch_size=[env.num_envs]),stochastic_output=False)
            obs,reward,term,timeout,extra = env.step(action)
        assert all(bool(torch.isfinite(v).all()) for v in obs.values())
        assert bool(torch.isfinite(reward).all())
        clean = env._encode()['policy']
        action_error = max(action_error,float((clean[:,22:28]-env.actions).abs().max()))
        expected = torch.zeros_like(clean[:,28:35]); expected[:,0]=1.
        mode_error = max(mode_error,float((clean[:,28:35]-expected).abs().max()))
        peak_velocity = max(peak_velocity,float(tensor(env.robot.data.joint_vel)[:,env.active_ids].abs().max()))
        peak_closure = max(peak_closure,float(env.closure_error.max()))
    final = env.r2_summary()
    result = dict(no_optimizer_update=True,num_envs=env.num_envs,steps=steps,elapsed_seconds=time.time()-start,initial=initial,final=final,done_totals=dict(env.done_totals),joint_velocity_peak=peak_velocity,closure_peak_m=peak_closure,raw_action_slot_error=action_error,constant_mode_slot_error=mode_error,terrain=env.terrain_summary())
    counts = env.r2_counts.sum(0)
    assert int(counts[0]) > 0 and int(counts[1]) > 0 and int(counts[2]) > 0, str(result)
    assert final['airborne_state_env_step_samples'] > 0, str(result)
    assert action_error < 1e-6 and mode_error < 1e-6, str(result)
    if env.done_totals['numerical']:
        raise ValueError('R2 fixed-weight physics probe numerical failure: '+str(result))
    return result

