"""MOD4 environment: ``ManagerBasedRLEnv`` plus the per-step event hook this Isaac build lacks.

Isaac Lab 3.0.0-beta2's ``ManagerBasedRLEnv`` only applies the event modes
``prestartup`` / ``startup`` / ``interval`` / ``reset`` -- there is no ``"step"`` mode anywhere
in the package, so every term registered with ``mode="step"`` was silently dead.  In MOD4 that
meant four things never ran:

* ``gas_spring_preload``: the delivered MJCF gas springs are PRELOADED
  (``springref`` / ``target_position_m`` = 0.2206 m, ~770 N of leg extension).  Without it the
  legs carry no preload and the root sags 0.34 -> 0.20 m within half a second
  (``probe_gas_preload.py`` A/B), which also destroys the meaning of "crouch below the 250 mm
  beam" -- the robot is already low.
* ``air_state``: sets ``env._mod4_just_landed``, which ``landing_recovery`` reads.  Never
  updated => the landing reward was identically zero in every log line.
* ``push_wrench``: the SCUT sustained-disturbance randomisation (10 N / 1 N.m, 0.1-0.3 s every
  5-10 s).
* ``leg_effort_noise`` / ``wheel_effort_noise``: per-step actuator gain noise (+-3% / +-2%).

Calling ``event_manager.apply(mode="step")`` once per control step -- before ``super().step()``
so the writes land in the same physics write as the actions -- restores exactly the semantics
the task config intended.  Nothing else changes.
"""
from __future__ import annotations

import os

import torch

from isaaclab.envs import ManagerBasedRLEnv


def _scripted_jump_actions(env, action):
    """Structured exploration for the jump skill (audit P2 / SCUT's phase-based state machine).

    Measured 2026-09-11 21:30: a crouch-and-release is a *coordinated, sustained* action pattern
    that per-joint Gaussian noise (sigma ~0.28) essentially never samples.  With
    RM_JUMP_SCRIPT_PROB > 0 a jump-route environment occasionally replays the exact pattern
    `probe_jump_reward.py --sweep` measured to produce a clean 4.6 cm hop (+0.6 on all four leg
    joints for RM_JUMP_SCRIPT_HOLD steps, then -0.6 for RM_JUMP_SCRIPT_RELEASE, then a cooldown),
    so PPO can learn FROM a hop instead of waiting for one to appear at random.

    This only injects exploration -- it changes no reward and no dynamics, and it is off by
    default (RM_JUMP_SCRIPT_PROB=0).  The manifest records the value that was used.
    """
    prob = float(os.environ.get("RM_JUMP_SCRIPT_PROB", "0.0"))
    is_jump = getattr(env, "_mod4_is_jump", None)
    if prob <= 0.0 or is_jump is None:
        return action
    n, dev = env.num_envs, env.device
    hold = int(os.environ.get("RM_JUMP_SCRIPT_HOLD", "40"))
    rel = int(os.environ.get("RM_JUMP_SCRIPT_RELEASE", "3"))
    cool = int(os.environ.get("RM_JUMP_SCRIPT_COOLDOWN", "40"))
    amp = float(os.environ.get("RM_JUMP_SCRIPT_AMP", "0.6"))
    if not hasattr(env, "_mod4_script_phase"):
        env._mod4_script_phase = torch.zeros(n, dtype=torch.long, device=dev)
        env._mod4_script_t = torch.zeros(n, dtype=torch.long, device=dev)
    phase, t = env._mod4_script_phase, env._mod4_script_t
    start = (phase == 0) & (torch.rand(n, device=dev) < prob) & is_jump.to(dev).bool()
    t = torch.where(start, torch.zeros_like(t), t + 1)
    phase = torch.where(start, torch.ones_like(phase), phase)
    phase = torch.where((phase == 1) & (t >= hold + rel + cool),
                        torch.zeros_like(phase), phase)
    in_hold = (phase == 1) & (t < hold)
    in_rel = (phase == 1) & (t >= hold) & (t < hold + rel)
    env._mod4_script_phase, env._mod4_script_t = phase, t
    leg = torch.where(in_hold, torch.full_like(t, 0).float() + amp,
                      torch.where(in_rel, torch.full_like(t, 0).float() - amp,
                                  torch.zeros_like(t).float()))
    mask = (in_hold | in_rel).unsqueeze(1)
    out = action.clone()
    out[:, :4] = torch.where(mask, leg.unsqueeze(1), out[:, :4])
    return out


class Mod4Env(ManagerBasedRLEnv):
    """ManagerBasedRLEnv that actually applies the ``"step"`` event mode."""

    def step(self, action):
        action = _scripted_jump_actions(self, action)
        if "step" in self.event_manager.available_modes:
            self.event_manager.apply(mode="step", dt=self.step_dt)
        return super().step(action)
