"""R6 actor with a frozen c874 drive prior and a proprioceptive jump mixture."""
from argparse import ArgumentParser
from pathlib import Path

import torch
from torch import nn

from jump360_r3_policy import R3ActorCritic
from jump360_scene import HERE, sha
from moe_jump_model import mirror_action_6, mirror_obs_35

RUN = HERE / "evidence/jump380_r6"
INITIAL = RUN / "initial/model_init.pt"
JUMP_PARENT = HERE / "evidence/jump360_r2/model_final.pt"
MODE_PARENT = HERE / "evidence/jump380_r4/ppo/model_008m.pt"
JUMP_SHA = "78519d2b8c2f8f5c6c1e804069d55e331c19cb07a62229a61d6cca7ada687187"
MODE_SHA = "9bcb9af89b88a9a7009d75a7f7686f29cf5d5756d4ed662f563efb7961f23655"
MODEL_TYPE = "MOD4v3_MovingJump380_R6"


def drive_observation(obs):
    normal = obs.clone()
    normal[..., 28:35] = normal.new_tensor([1., 0., 0., 0., 0., 0., 0.])
    return normal


class R6ActorCritic(R3ActorCritic):
    def drive_base(self, obs):
        with torch.no_grad():
            e0 = self.actor_body.e0
            normal = drive_observation(obs)
            # Enforce left/right equivariance with the same frozen c874 weights.
            mirror = mirror_action_6(e0(mirror_obs_35(normal)))
            return (.5 * (e0(normal) + mirror)).clamp(-6., 6.)

    def action_and_phase(self, obs, history):
        body = self.actor_body
        expert = body.e_jump
        normalized = expert.encoder.normalize_obs(obs)
        past = expert.encoder.normalize_obs(history.unflatten(-1, (12, 35))).flatten(-2)
        mode = body.mode_head(torch.cat((normalized, past), dim=-1)).squeeze(-1)
        features = torch.cat((normalized, expert.encoder(history)), dim=-1)
        base = self.drive_base(obs)
        with torch.no_grad():
            jump_base = expert.loco_base(drive_observation(obs))
        jump = jump_base + expert.delta_head(features)
        drive = base + body.drive_head(features)
        recent_key = (obs[..., 30] > .5) | (history[..., 30::35].amax(-1) > .5)
        weight = mode.sigmoid()
        # After a short tap, current proprioception can still indicate active flight.
        late_weight = (2. * weight - 1.).clamp_min(0.)
        weight = torch.where(recent_key, weight, late_weight)
        drive = torch.where(recent_key[..., None], drive, base)
        return torch.lerp(drive, jump, weight[..., None]).clamp(-6., 6.), mode

    def act_deterministic(self, obs, hist):
        return self.action_and_phase(obs, hist)[0]


def load_policy(path: Path, device="cpu"):
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if payload["model_type"] != MODEL_TYPE:
        raise ValueError("Expected an R6 checkpoint")
    model = R6ActorCritic()
    model.load_state_dict(payload["state_dict"])
    model.verify_zero_e0_drift()
    return model.to(device).eval()


def initialize():
    if sha(JUMP_PARENT) != JUMP_SHA or sha(MODE_PARENT) != MODE_SHA:
        raise ValueError("R6 parent checksums do not match the archived weights")
    torch.set_num_threads(1)
    torch.manual_seed(38006)
    model = R6ActorCritic()
    r2 = torch.load(JUMP_PARENT, map_location="cpu", weights_only=False)["state_dict"]
    r4 = torch.load(MODE_PARENT, map_location="cpu", weights_only=False)["state_dict"]
    mode = {key: value for key, value in r4.items() if key.startswith("actor_body.mode_head.")}
    missing, unexpected = model.load_state_dict({**r2, **mode}, strict=False)
    if unexpected or set(missing) != {key for key in model.state_dict()
                                     if key.startswith("actor_body.drive_head.")}:
        raise ValueError(f"R6 parent architecture mismatch: {missing}, {unexpected}")
    nn.init.zeros_(model.actor_body.drive_head[-1].weight)
    nn.init.zeros_(model.actor_body.drive_head[-1].bias)
    model.verify_zero_e0_drift()
    INITIAL.parent.mkdir(parents=True, exist_ok=True)
    torch.save(dict(model_type=MODEL_TYPE, obs_dim=35, hist_dim=420, action_dim=6, hist_len=12,
                    jump_mode_bit_index=30, state_dict=model.state_dict(),
                    jump_parent_sha256=JUMP_SHA, mode_parent_sha256=MODE_SHA), INITIAL)
    print(f"R6 initial SHA-256 {sha(INITIAL)}", flush=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.parse_args()
    initialize()
