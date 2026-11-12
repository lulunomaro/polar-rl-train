"""Bounded no-optimizer R1 spawn/physics/observation probe."""
import time
import torch
from tensordict import TensorDict
from .scut_flat_env import tensor

def run_probe(env,algorithm):
    start=time.time();steps=200 if env.num_envs<1024 else 48
    policy=algorithm.get_policy();obs=env._get_observations()
    assert obs['policy'].shape==(env.num_envs,35)
    assert obs['critic'].shape==(env.num_envs,78)
    assert env.cfg.sim.dt==.0025 and env.cfg.decimation==8
    assert env.enforce_closure_reset and float(env.reward.cfg.lin_vel_xy_square_sigma)==1.
    assert float(env.reward.cfg.rewards['track_lin_vel_xy_square'])==-1.5
    initial=env.terrain_summary()
    assert len(initial["families"])==9 and initial["groups"]["nominal_flat"]+initial["groups"]["nominal_rough"]==int(env.full_dr.nominal_env_mask.sum())
    assert bool((env.terrain.terrain_levels==0).all())
    peak_velocity=0.;peak_closure=0.;peak_action_error=0.;term=0;timeout=0
    for _ in range(steps):
        with torch.inference_mode():
            action=policy(TensorDict(obs,batch_size=[env.num_envs]),stochastic_output=False)
            obs,reward,terminated,truncated,extra=env.step(action)
        assert all(bool(torch.isfinite(v).all()) for v in obs.values())
        assert bool(torch.isfinite(reward).all())
        peak_action_error=max(peak_action_error,float((env._encode()['policy'][:,22:28]-env.actions).abs().max()))
        peak_velocity=max(peak_velocity,float(tensor(env.robot.data.joint_vel)[:,env.active_ids].abs().max()))
        peak_closure=max(peak_closure,float(env.closure_error.max()))
        term+=int(terminated.sum());timeout+=int(truncated.sum())
    result=dict(no_optimizer_update=True,steps=steps,num_envs=env.num_envs,elapsed_seconds=time.time()-start,initial=initial,final=env.terrain_summary(),done_totals=env.done_totals,term_events=term,timeout_events=timeout,joint_velocity_peak=peak_velocity,closure_peak_m=peak_closure,raw_action_slot_error=peak_action_error,nominal_DR_group_mask_matches=bool(torch.equal(env.terrain.r1_nominal_mask,env.full_dr.nominal_env_mask)),physics_dt_s=env.cfg.sim.dt,policy_dt_s=env.cfg.sim.dt*env.cfg.decimation)
    if env.done_totals['numerical'] or not peak_action_error<1e-6:raise ValueError('R1 no-update physics/input probe failed: '+str(result))
    return result
