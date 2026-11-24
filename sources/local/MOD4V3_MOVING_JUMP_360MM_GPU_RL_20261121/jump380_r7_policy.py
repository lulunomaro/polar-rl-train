"""Bilateral R7 policy and correlated PPO exploration."""
from argparse import ArgumentParser
import math
from pathlib import Path

import torch

from jump360_r3_policy import R3ActorCritic
from jump360_scene import HERE, sha
from jump380_r6_policy import MODEL_TYPE as PARENT_TYPE, drive_observation as jump_observation
from moe_jump_model import mirror_action_6, mirror_history_420, mirror_obs_35

RUN = HERE / "evidence/jump380_r7"
INITIAL = RUN / "initial/model_init.pt"
PARENT = HERE / "evidence/jump380_r6/ppo/model_003m.pt"
PARENT_SHA = "f9169f4b80f161710fe21229151bd10edc107a8cb540027769747f97c02c2413"
MODEL_TYPE = "MOD4v3_MovingJump380_R7"
HEIGHT_CAP = .39
RECOVERY_LOGIT = math.log(3.)
SYMMETRIC_VARIANCE = .90
PAIR_VARIANCE = 1. + SYMMETRIC_VARIANCE
DIFFERENCE_VARIANCE = 1. - SYMMETRIC_VARIANCE


def cruise_observation(obs):
    normal = jump_observation(obs)
    height = normal[..., 3].clamp_max(5.*HEIGHT_CAP)
    # Invert the measured c874 forward-speed curve u + k(h)*u**2.
    excess = (height*.2 - .31).clamp_min(0.)
    gain = excess*(1.10 + 30.*excess)
    demand = normal[..., 0]
    normal[..., 0] = 2.*demand/(1. + (1. + 4.*gain*demand.abs()).sqrt())
    normal[..., 3] = height
    return normal


class R7ActorCritic(R3ActorCritic):
    def drive_base(self, obs):
        with torch.no_grad():
            e0 = self.actor_body.e0
            direct = e0(cruise_observation(obs))
            mirrored = e0(cruise_observation(mirror_obs_35(obs)))
            return (.5*(direct + mirror_action_6(mirrored))).clamp(-6., 6.)

    def raw_action_and_phase(self, obs, history, recent_key):
        body = self.actor_body
        expert = body.e_jump
        normalized = expert.encoder.normalize_obs(obs)
        past = expert.encoder.normalize_obs(history.unflatten(-1, (12, 35))).flatten(-2)
        mode = body.mode_head(torch.cat((normalized, past), dim=-1)).squeeze(-1)
        features = torch.cat((normalized, expert.encoder(history)), dim=-1)
        with torch.no_grad():
            base = body.e0(cruise_observation(obs))
            jump_base = expert.loco_base(jump_observation(obs))
        jump = jump_base + expert.delta_head(features)
        drive = torch.where(recent_key[..., None], base + body.drive_head(features), base)
        weight = mode.sigmoid()
        weight = torch.where(recent_key, weight, (2.*weight - 1.).clamp_min(0.))
        return torch.lerp(drive, jump, weight[..., None]).clamp(-6., 6.), mode, base

    def action_phase_and_base(self, obs, history):
        recent_key = (obs[..., 30] > .5) | (history[..., 30::35].amax(-1) > .5)
        # Batch both reflections through the same network in one forward pass.
        mirrored_obs = torch.cat((obs, mirror_obs_35(obs)), dim=0)
        mirrored_hist = torch.cat((history, mirror_history_420(history)), dim=0)
        keys = torch.cat((recent_key, recent_key), dim=0)
        raw, logits, bases = self.raw_action_and_phase(mirrored_obs, mirrored_hist, keys)
        action, mirrored = raw.chunk(2, dim=0)
        mode, mirrored_mode = logits.chunk(2, dim=0)
        base, mirrored_base = bases.chunk(2, dim=0)
        action = .5*(action + mirror_action_6(mirrored))
        mode = .5*(mode + mirrored_mode)
        base = (.5*(base + mirror_action_6(mirrored_base))).clamp(-6., 6.)
        active = recent_key | (mode >= RECOVERY_LOGIT)
        return torch.where(active[..., None], action, base), mode, base

    def action_and_phase(self, obs, history):
        action, mode, _ = self.action_phase_and_base(obs, history)
        return action, mode

    def act_deterministic(self, obs, hist):
        return self.action_and_phase(obs, hist)[0]


def sample_action(mean, scale):
    white = torch.randn_like(mean)
    symmetric = .5*(white + mirror_action_6(white))
    return mean + scale[..., None]*(math.sqrt(PAIR_VARIANCE)*symmetric
                                    + math.sqrt(DIFFERENCE_VARIANCE)*(white - symmetric))


def action_log_prob(action, mean, scale):
    residual = (action - mean)/scale[..., None]
    symmetric = .5*(residual + mirror_action_6(residual))
    quadratic = symmetric.square()/PAIR_VARIANCE + (residual - symmetric).square()/DIFFERENCE_VARIANCE
    normalizer = 3.*math.log(2.*math.pi) + 1.5*math.log(PAIR_VARIANCE*DIFFERENCE_VARIANCE)
    return -.5*quadratic.sum(-1) - 6.*scale.log() - normalizer


def load_policy(path: Path, device="cpu"):
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if payload["model_type"] != MODEL_TYPE:
        raise ValueError("Expected an R7 checkpoint")
    model = R7ActorCritic()
    model.load_state_dict(payload["state_dict"])
    model.verify_zero_e0_drift()
    return model.to(device).eval()


def initialize():
    if sha(PARENT) != PARENT_SHA:
        raise ValueError("R7 requires the pinned R6 3-minute checkpoint")
    torch.set_num_threads(1)
    parent = torch.load(PARENT, map_location="cpu", weights_only=False)
    if parent["model_type"] != PARENT_TYPE:
        raise ValueError("Unexpected R6 parent architecture")
    model = R7ActorCritic()
    model.load_state_dict(parent["state_dict"])
    model.verify_zero_e0_drift()
    INITIAL.parent.mkdir(parents=True, exist_ok=True)
    torch.save(dict(model_type=MODEL_TYPE, obs_dim=35, hist_dim=420, action_dim=6, hist_len=12,
                    jump_mode_bit_index=30, state_dict=model.state_dict(), parent_sha256=PARENT_SHA), INITIAL)
    print(f"R7 initial SHA-256 {sha(INITIAL)}", flush=True)


if __name__ == "__main__":
    ArgumentParser(description=__doc__).parse_args()
    initialize()
