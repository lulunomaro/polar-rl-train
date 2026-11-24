"""R10 policy with calibrated forward commands for frozen c874 cruise."""

from pathlib import Path

import torch

from jump360_scene import HERE, sha
from jump380_r7_policy import MODEL_TYPE as PARENT_TYPE
from jump380_r7_policy import R7ActorCritic, cruise_observation, jump_observation

EXPERIMENT = "jump380_r10"
RUN = HERE / "evidence" / EXPERIMENT
PARENT = HERE / "evidence/jump380_r8/ppo/model_012m.pt"
PARENT_SHA = "4958dc3830f5bee87810a16d17dcec6afc9088953a2670997e875efdcd98ba93"
MODEL_TYPE = "MOD4v3_MovingJump380_R10"

MIN_SPEED = 1.0
MAX_SPEED = 3.0
SPEED_GRID = (1.2, 1.6, 2.0, 2.4, 2.8)
STANCE_GRID = (.24, .32, .42)
TRAIN_SPEED_GRID = (MIN_SPEED, *SPEED_GRID, MAX_SPEED)
CALIBRATION_KEY = "CRUISE.json"

# Corrections to the demand entering the R7 inverse curve, in m/s. Each
# column is fitted from the steady tail of the 400 Hz c874 cruise sweeps.
CRUISE_SPEEDS = (1.8, 2.0, 2.4, 2.8, 3.0)
CRUISE_HEIGHTS = (.24, .28, .32, .35, .38, .39)
DEMAND_CORRECTION = (
    (0., .155, .368, .559, .650),
    (0., -.019, .060, .194, .246),
    (0., -.092, -.088, -.001, .044),
    (0., .053, .065, .208, .282),
    (0., .127, .107, .098, .138),
    (0., .125, .093, .046, .032),
)


class R10ActorCritic(R7ActorCritic):
    def __init__(self):
        super().__init__()
        self.register_buffer("cruise_speeds", torch.tensor(CRUISE_SPEEDS), persistent=False)
        self.register_buffer("cruise_heights", torch.tensor(CRUISE_HEIGHTS), persistent=False)
        self.register_buffer("demand_correction", torch.tensor(DEMAND_CORRECTION), persistent=False)

    def calibrated_command(self, obs):
        def bracket(value, grid):
            value = value.clamp(grid[0], grid[-1]).contiguous()
            left = (torch.searchsorted(grid, value) - 1).clamp(0, len(grid) - 2)
            fraction = (value - grid[left])/(grid[left + 1] - grid[left])
            return left, fraction

        speed, blend_speed = bracket(obs[..., 0], self.cruise_speeds)
        height, blend_height = bracket(obs[..., 3]*.2, self.cruise_heights)
        corrections = self.demand_correction
        low = torch.lerp(corrections[height, speed], corrections[height, speed + 1], blend_speed)
        high = torch.lerp(corrections[height + 1, speed], corrections[height + 1, speed + 1], blend_speed)
        calibrated = obs.clone()
        calibrated[..., 0] += torch.lerp(low, high, blend_height)
        return calibrated

    def drive_base(self, obs):
        return super().drive_base(self.calibrated_command(obs))

    def raw_action_and_phase(self, obs, history, recent_key):
        body = self.actor_body
        expert = body.e_jump
        normalized = expert.encoder.normalize_obs(obs)
        past = expert.encoder.normalize_obs(history.unflatten(-1, (12, 35))).flatten(-2)
        mode = body.mode_head(torch.cat((normalized, past), dim=-1)).squeeze(-1)
        features = torch.cat((normalized, expert.encoder(history)), dim=-1)
        with torch.no_grad():
            base = body.e0(cruise_observation(self.calibrated_command(obs)))
            jump_base = expert.loco_base(jump_observation(obs))
        jump = jump_base + expert.delta_head(features)
        drive = torch.where(recent_key[..., None], base + body.drive_head(features), base)
        weight = mode.sigmoid()
        weight = torch.where(recent_key, weight, (2.*weight - 1.).clamp_min(0.))
        return torch.lerp(drive, jump, weight[..., None]).clamp(-6., 6.), mode, base


def load_policy(path: Path, device="cpu"):
    payload = torch.load(path, map_location="cpu", weights_only=False)
    model_type = payload["model_type"]
    if model_type != MODEL_TYPE and (model_type != PARENT_TYPE or sha(path) != PARENT_SHA):
        raise ValueError("Expected an R10 checkpoint or the pinned R8 parent")
    model = R10ActorCritic()
    model.load_state_dict(payload["state_dict"])
    model.verify_zero_e0_drift()
    return model.to(device).eval()
