"""Isolated SCUT-style MOD4 action/contact/spring runtime contract probe."""
from __future__ import annotations

import argparse
import json
import math

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--report", required=True)
parser.add_argument("--steps", type=int, default=50)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args).app

import torch  # noqa: E402
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def main():
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = 7
    cfg.seed = 20260926
    env = Mod4Env(cfg=cfg)
    try:
        env.reset(seed=20260926)
        robot = env.scene["robot"]
        expected = mod4_task.ACTION_ORDER
        terms = env.action_manager._terms
        resolved = [*terms["legs"]._joint_names, *terms["wheels"]._joint_names]
        if resolved != expected or env.action_manager.total_action_dim != 6:
            raise AssertionError(f"action map mismatch: {resolved} != {expected}")
        wheel_sensor = env.scene.sensors["wheel_contact"]
        guide_sensor = env.scene.sensors["guide_contact"]
        if set(wheel_sensor.body_names) != {"left_wheel", "right_wheel"}:
            raise AssertionError(f"wheel-contact bodies {wheel_sensor.body_names}")
        if len(guide_sensor.body_names) != 8:
            raise AssertionError(f"guide-contact bodies {guide_sensor.body_names}")
        actions = torch.zeros((7, 6), device=env.device)
        actions[1:, :] = torch.eye(6, device=env.device) * 0.25
        joint_ids = [robot.joint_names.index(name) for name in expected]
        start_pos = robot.data.joint_pos[:, joint_ids].clone()
        max_closure = max_mimic = 0.0
        max_wheel_force = max_guide_force = 0.0
        min_gas, max_gas = math.inf, -math.inf
        target_diag = None
        for step in range(args.steps):
            _, _, _, _, _ = env.step(actions)
            if step == 0:
                processed = [terms["legs"].processed_actions,
                             terms["wheels"].processed_actions]
                target_diag = torch.cat(processed, dim=1).detach().cpu().tolist()
            wf = wheel_sensor.data.net_forces_w.norm(dim=-1)
            gf = guide_sensor.data.net_forces_w.norm(dim=-1)
            max_wheel_force = max(max_wheel_force, float(wf.max()))
            max_guide_force = max(max_guide_force, float(gf.max()))
            gas = getattr(env, "_mod4_gas_force_ref_realized_n", None)
            if gas is not None:
                min_gas = min(min_gas, float(gas.min()))
                max_gas = max(max_gas, float(gas.max()))
            max_closure = max(max_closure, float(getattr(env, "_mod4_max_closure", 0.0)))
            max_mimic = max(max_mimic, float(getattr(env, "_mod4_max_mimic", 0.0)))
        target = torch.tensor(target_diag)
        # A single pulse must affect just its assigned command channel.  This checks
        # the action interface itself, independently of coupled physical motion.
        offdiag = target[1:] - torch.diag(torch.diag(target[1:]))
        if float(offdiag.abs().max()) > 1e-5:
            raise AssertionError(f"action target crosstalk: {offdiag}")
        if not bool((torch.diag(target[1:]) > 0).all()):
            raise AssertionError(f"action target sign/scale invalid: {target}")
        if not 400.0 <= min_gas <= max_gas <= 600.0:
            raise AssertionError(f"500 N spring reference not realized: {min_gas}, {max_gas}")
        if max_closure > 0.002 or max_mimic > 0.01:
            raise AssertionError(f"closure/mimic error: {max_closure}, {max_mimic}")
        if max_wheel_force <= 1.0:
            raise AssertionError("no main-wheel contact force")
        report = {
            "status": "PASS", "action_order": expected,
            "action_target_per_env": target_diag,
            "joint_delta_rad": (robot.data.joint_pos[:, joint_ids] - start_pos).detach().cpu().tolist(),
            "wheel_contact_bodies": list(wheel_sensor.body_names),
            "guide_contact_bodies": list(guide_sensor.body_names),
            "max_wheel_force_n": max_wheel_force,
            "max_guide_force_n": max_guide_force,
            "gas_reference_force_n": [min_gas, max_gas],
            "max_closure_m": max_closure,
            "max_mimic_rad": max_mimic,
        }
        with open(args.report, "w", encoding="utf8") as file:
            json.dump(report, file, indent=2)
        print("[scut-mapping] " + json.dumps(report), flush=True)
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        app.close()
