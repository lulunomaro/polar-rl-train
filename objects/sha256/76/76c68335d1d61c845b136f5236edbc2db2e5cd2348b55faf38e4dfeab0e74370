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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._contact_eager5ms_enabled = os.environ.get("RM_CONTACT_EAGER5MS", "0") == "1"
        integrated = os.environ.get("RM_CONTACT_INTEGRATED", "0") == "1"
        if self._contact_eager5ms_enabled or integrated:
            self._install_contact_eager5ms()
        if integrated:
            from contact_capture import IntegratedWheelContact
            self._integrated_contact = IntegratedWheelContact(self)
            original_update = self.scene.update
            def integrated_update(dt):
                original_update(dt)
                self._integrated_contact.capture(dt)
            self.scene.update = integrated_update
            import json
            print("CONTACT_INTEGRATED_CONFIG " + json.dumps(self._contact_capture_metadata), flush=True)

    def _install_contact_eager5ms(self):
        """Consume only the SCUT history sensor at its configured physics cadence.

        Physics, sensor threshold, history length and force formula are unchanged.
        Other lazy sensors stay untouched. A batched/decimated physics backend
        without substep callbacks is deliberately rejected.
        """
        if self._physics_handles_decimation:
            raise RuntimeError("5 ms contact capture requires physical substep scene updates")
        sensor = self.scene.sensors["wheel_contact_scut"]
        period = float(sensor.cfg.update_period)
        stride = int(round(period / float(self.physics_dt)))
        if abs(period - 0.005) > 1e-9 or stride < 1 or abs(stride * self.physics_dt - period) > 1e-9:
            raise RuntimeError("Contact cadence contract is not 5 ms / integer physics ticks")
        if int(sensor.cfg.history_length) != 3:
            raise RuntimeError("Contact history must preserve three samples")
        _ = sensor.data  # align an initial read; reset history remains sensor-owned
        original_update = self.scene.update
        self._contact_physics_tick = 0

        def update_with_contact_capture(dt):
            if abs(float(dt) - float(self.physics_dt)) > 1e-9:
                raise RuntimeError("Contact capture received a decimated update")
            original_update(dt)
            self._contact_physics_tick += 1
            if self._contact_physics_tick % stride == 0:
                _ = sensor.data

        self.scene.update = update_with_contact_capture
        self._contact_capture_metadata = {"enabled": True, "period_s": period,
            "physics_dt": float(self.physics_dt), "stride": stride, "history_length": 3,
            "semantics": "instantaneous sensor force at 5 ms endpoints; not accumulated impulses or continuous contact"}
        import json
        print("CONTACT_CAPTURE_CONFIG " + json.dumps(self._contact_capture_metadata), flush=True)

    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        if hasattr(self, "_integrated_contact"):
            self._integrated_contact.reset(env_ids)

    def step(self, action):
        if hasattr(self, "_integrated_contact"):
            self._integrated_contact.begin_control()
        action = _scripted_jump_actions(self, action)
        if "step" in self.event_manager.available_modes:
            self.event_manager.apply(mode="step", dt=self.step_dt)
        result = super().step(action)
        if self.common_step_counter % 2400 == 1:
            import json
            term = self.command_manager.get_term('twist')
            yaw = term.command[:, 2]
            audit = {'control_step': int(self.common_step_counter),
                     'gyro_curriculum_enabled': os.environ.get('RM_GYRO_CURRICULUM','1') != '0',
                     'configured_yaw_range': list(term.cfg.ranges.ang_vel_z),
                     'actual_command_yaw_abs_max': float(yaw.abs().max()),
                     'actual_command_yaw_abs_mean': float(yaw.abs().mean()),
                     'actual_command_vx_min': float(term.command[:,0].min()),
                     'actual_command_vx_max': float(term.command[:,0].max())}
            if os.environ.get('RM_SPIN_STAGE') in ('pure_yaw_v1', 'directional_spin_v1'):
                from spin_commands import audit as audit_spin
                audit['spin_command_audit'] = audit_spin(self)
            if os.environ.get('RM_GYRO_CURRICULUM','1') == '0' and os.environ.get('RM_SPIN_STAGE') not in ('pure_yaw_v1', 'directional_spin_v1') and audit['actual_command_yaw_abs_max'] > 1e-6:
                raise RuntimeError('Straight-speed contract violated: nonzero yaw command')
            print('COMMAND_AUDIT ' + json.dumps(audit), flush=True)
        return result
