"""Neural jump/drive mixture seeded with the complete R2 actor and critic."""
from pathlib import Path

import torch
from torch import nn

from jump360_scene import StatefulMoEJumpActor
from moe_jump_model import ACT_DIM, HIST_DIM, OBS_DIM, MoEJumpActorCritic, MoEJumpBody

MODEL_TYPE = "MOD4v3_MovingJump360_R3"


class R3Body(MoEJumpBody):
    def __init__(self):
        super().__init__()
        self.mode_head = nn.Sequential(
            nn.Linear(OBS_DIM + HIST_DIM, 96), nn.ELU(),
            nn.Linear(96, 64), nn.ELU(), nn.Linear(64, 1),
        )
        self.drive_head = nn.Sequential(
            nn.Linear(OBS_DIM + 64, 128), nn.ELU(), nn.Linear(128, 64), nn.ELU(), nn.Linear(64, ACT_DIM),
        )
        nn.init.zeros_(self.drive_head[-1].weight)
        nn.init.zeros_(self.drive_head[-1].bias)

    def components(self, obs, history):
        expert = self.e_jump
        normal_obs = obs.clone()
        normal_obs[..., 28:35] = normal_obs.new_tensor([1., 0., 0., 0., 0., 0., 0.])
        with torch.no_grad():
            drive_base = self.e0(normal_obs)
            jump_base = expert.loco_base(normal_obs)
        obs_normalized = expert.encoder.normalize_obs(obs)
        past = expert.encoder.normalize_obs(history.unflatten(-1, (12, OBS_DIM))).flatten(-2)
        mode = self.mode_head(torch.cat((obs_normalized, past), dim=-1)).squeeze(-1)
        features = torch.cat((obs_normalized, expert.encoder(history)), dim=-1)
        jump = jump_base + expert.delta_head(features)
        drive = drive_base + self.drive_head(features)
        return mode, jump, drive

    def forward(self, obs, hist):
        mode, jump, drive = self.components(obs, hist)
        return torch.lerp(drive, jump, mode.sigmoid().unsqueeze(-1))


class R3ActorCritic(MoEJumpActorCritic):
    def __init__(self):
        super().__init__()
        self.actor_body = R3Body()

    @classmethod
    def warm_from_r2(cls, checkpoint):
        model = cls()
        payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
        missing, extra = model.load_state_dict(payload["state_dict"], strict=False)
        introduced = ("actor_body.mode_head.", "actor_body.drive_head.")
        if extra or set(missing) != {name for name in model.state_dict() if name.startswith(introduced)}:
            raise RuntimeError(f"R2/R3 checkpoint mismatch: {missing}, {extra}")
        model.verify_zero_e0_drift()
        return model


def load_policy(path: Path, device="cpu"):
    payload = torch.load(path, map_location=device, weights_only=False)
    if payload["model_type"] == MODEL_TYPE:
        model = R3ActorCritic()
    else:
        model = MoEJumpActorCritic()
    model.load_state_dict(payload["state_dict"])
    model.verify_zero_e0_drift()
    return model.to(device).eval()


class R3Control:
    def __init__(self, core):
        self.actor = StatefulMoEJumpActor(core)

    def reset_history(self):
        self.actor.reset_history()

    def __call__(self, plant, observation):
        return self.actor(torch.from_numpy(observation[None]))[0].numpy()

