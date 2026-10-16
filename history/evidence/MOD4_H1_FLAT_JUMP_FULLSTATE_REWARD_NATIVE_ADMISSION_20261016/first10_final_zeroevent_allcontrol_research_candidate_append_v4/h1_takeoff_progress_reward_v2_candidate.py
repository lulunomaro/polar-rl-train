"""One added prelaunch proxy term; inherited V1 masks and every original cost unchanged."""
import torch
from h1_reward_scope_v1 import configure as configure_original_h1
from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
def prelaunch_progress_rate(env):
 p=getattr(env,'h1_phase',None)
 return torch.zeros(env.num_envs,device=env.device) if p is None else p.progress_control/float(env.step_dt)
def configure(cfg):
 from isaaclab.managers import RewardTermCfg
 configure_original_h1(cfg);cfg.rewards.h1_prelaunch_progress=RewardTermCfg(func=prelaunch_progress_rate,weight=1.);return cfg
