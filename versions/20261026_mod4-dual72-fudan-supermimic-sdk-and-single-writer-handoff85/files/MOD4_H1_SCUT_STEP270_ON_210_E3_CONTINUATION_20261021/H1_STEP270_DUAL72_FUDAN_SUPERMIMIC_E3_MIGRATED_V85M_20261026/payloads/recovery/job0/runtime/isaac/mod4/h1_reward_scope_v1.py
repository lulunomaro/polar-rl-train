"""Explicit H1 reward axis; source guards and all energy/action-rate costs unchanged."""
import torch
MASKED=('height','height_tight','height_both_wheels','height_square','height_deficit','height_error_l1','lin_vel_z')
def request_masked_original(env,original_func,original_params):
 value=original_func(env,**original_params);phase=getattr(env,'h1_phase',None)
 return value if phase is None else torch.where(phase.request_for_action,torch.zeros_like(value),value)
def h1_control_event_rate(env):
 phase=getattr(env,'h1_phase',None)
 return torch.zeros(env.num_envs,device=env.device) if phase is None else phase.event_control/float(env.step_dt)
def configure(cfg):
 from isaaclab.managers import RewardTermCfg
 declaration=[]
 for name in MASKED:
  term=getattr(cfg.rewards,name,None)
  if term is None:continue
  original=term.func;params=dict(term.params);declaration.append(dict(name=name,original_module=original.__module__,original_name=original.__qualname__,weight=term.weight,params=repr(params)));term.func=request_masked_original;term.params=dict(original_func=original,original_params=params)
 cfg.rewards.h1_control_events=RewardTermCfg(func=h1_control_event_rate,weight=1.)
 cfg._h1_reward_axis=declaration
 return cfg
def isolated_actual_SDK_dt_probe(env):
 from isaaclab.managers import RewardManager,RewardTermCfg
 def constant_event_rate(e):return torch.ones(e.num_envs,device=e.device)/float(e.step_dt)
 # Separate manager, not inserted into the live training manager or trajectory.
 original_cpu=torch.get_rng_state().clone();probe=RewardManager({'known_one_event':RewardTermCfg(func=constant_event_rate,weight=1.)},env);out=probe.compute(float(env.step_dt));err=float((out-1).abs().amax());assert err<=1e-6 and torch.equal(original_cpu,torch.get_rng_state());step=probe._step_reward[:,0]
 if torch.allclose(step,out/float(env.step_dt),atol=1e-5,rtol=0):scale=float(env.step_dt)
 elif torch.allclose(step,out,atol=1e-6,rtol=0):scale=1.
 else:raise ValueError('Actual SDK per-term exposure neither rate nor control contribution')
 env.h1_reward_readout_scale=scale
 return dict(actual_SDK_type=type(probe).__module__+'.'+type(probe).__name__,dt=float(env.step_dt),known_one_event_output_maxabs=err,actual_perterm_readout_multiplier=scale,isolated_from_live_reward_manager=True,no_trajectory_reward_injected=True)
