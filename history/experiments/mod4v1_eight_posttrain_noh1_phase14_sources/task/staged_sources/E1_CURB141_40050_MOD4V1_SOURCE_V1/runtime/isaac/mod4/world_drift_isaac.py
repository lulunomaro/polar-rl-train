"""Stateful reward adapter; Isaac RewardManager resets it on episode reset."""
import torch
from isaaclab.managers import ManagerTermBase
from world_drift_reward import CycleCrossDrift, VERSION


class WorldCycleCrossReward(ManagerTermBase):
    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        self.tracker = CycleCrossDrift(env.num_envs, env.device)
        self.cached_step = None
        self.cached_cost = torch.zeros(env.num_envs, device=env.device)
        self.updates = 0

    def reset(self, env_ids=None):
        self.tracker.reset(env_ids)
        ids = slice(None) if env_ids is None else env_ids
        self.cached_cost[ids] = 0

    def __call__(self, env, command_name='twist', scale=.10, max_cost=4.):
        step = env.common_step_counter
        if self.cached_step != step:
            cmd = env.command_manager.get_term(command_name)
            robot = env.scene['robot']
            heading = robot.data.heading_w.torch
            active = cmd.is_moving_spin & ~cmd.is_standing_env
            goal = torch.full_like(heading, cmd.progress_goal)
            self.tracker.update(robot.data.root_pos_w.torch[:, :2], heading,
                                cmd.world_direction, cmd.signed_yaw, goal,
                                active, cmd.phase_elapsed, env.step_dt)
            self.cached_cost = self.tracker.cost(scale, max_cost)
            self.cached_step = step
            self.updates += 1
        return self.cached_cost.clone()
