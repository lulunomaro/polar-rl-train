"""Cumulative material DR plus native SCUT interval root-velocity pushes."""
import torch
from isaaclab.managers import EventTermCfg, SceneEntityCfg
from isaaclab.utils import configclass
from isaaclab.envs.mdp.events import push_by_setting_velocity
from .scut_flat_env import tensor
from .scut_flat_material_env import ScutMaterialDR, ScutFlatMaterialEnv


def recorded_velocity_push(env, env_ids, velocity_range, asset_cfg):
    ids = torch.as_tensor(env_ids, device=env.device, dtype=torch.long).flatten()
    before = tensor(env.robot.data.root_vel_w)[ids].clone()
    push_by_setting_velocity(env, ids, velocity_range, asset_cfg)
    after = tensor(env.robot.data.root_vel_w)[ids].clone()
    env.velocity_push_count[ids] += 1
    env.velocity_push_last_pre[ids] = before
    env.velocity_push_last_post[ids] = after
    env.velocity_push_last_delta[ids] = after - before
    env.velocity_push_last_tick[ids] = int(env._sim_step_counter)


@configclass
class VelocityPushEvents:
    velocity_push = EventTermCfg(
        func=recorded_velocity_push, mode="interval", interval_range_s=(5.0, 10.0), is_global_time=False,
        params={"velocity_range": {"x": (-0.25, 0.25), "y": (-0.25, 0.25)},
                "asset_cfg": SceneEntityCfg("robot")})


class ScutVelocityPushDR(ScutMaterialDR):
    def summary(self):
        row = super().summary()
        env = self.env
        counts = getattr(env, "velocity_push_count", None)
        row.update(profile="step7_mass_effort_material_velocity_push_v1", velocity_push={
            "world_xy_velocity_delta_range_m_s": [-0.25, 0.25], "interval_s": [5.0, 10.0],
            "per_environment": True, "is_global_time": False,
            "sampling": "native EventManager interval; timer resampled on reset",
            "function": "target installed isaaclab.envs.mdp.events.push_by_setting_velocity",
            "semantics": "add delta to world XY velocity; z and angular unchanged",
            "phase": "native post-step interval before observations",
            "total_events": int(counts.sum()) if counts is not None else 0},
            missing_dr=["full_SCUT_COM_and_other_remaining_ranges"])
        return row


class ScutFlatVelocityPushEnv(ScutFlatMaterialEnv):
    body_mass_dr_class = ScutVelocityPushDR

    def __init__(self, cfg, meta, bank):
        cfg.events = VelocityPushEvents()
        self._velocity_push_ready = False
        super().__init__(cfg, meta, bank)
        self.velocity_push_count = torch.zeros(self.num_envs, device=self.device, dtype=torch.long)
        self.velocity_push_last_pre = torch.zeros((self.num_envs, 6), device=self.device)
        self.velocity_push_last_post = torch.zeros_like(self.velocity_push_last_pre)
        self.velocity_push_last_delta = torch.zeros_like(self.velocity_push_last_pre)
        self.velocity_push_last_tick = torch.full((self.num_envs,), -1, device=self.device, dtype=torch.long)
        self._velocity_push_ready = True

    @property
    def velocity_push_time_left(self):
        return self.event_manager._interval_term_time_left[0]

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        if self._velocity_push_ready:
            # Match ManagerBasedRLEnv._reset_idx; DirectRLEnv does not call manager.reset.
            self.event_manager.reset(env_ids=ids)
