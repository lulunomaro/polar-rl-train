#!/usr/bin/env python
"""Deterministic acceptance gate for the RM2025 later no-gimbal closed-chain policy.

This is the executable form of ``docs/ACCEPTANCE_RM2025_LATER.md``.  It runs on the
training host because mjlab needs CUDA (MuJoCo-Warp):

  cd /home/egde/fangzhen_linux
  export PYTHONPATH="$PWD/train/rmvehicle/src:$PWD/third_party/rc_mjlab/mjlab/src"
  PY=third_party/rc_mjlab/.venv/bin/python
  $PY train/verify_acceptance_later.py \
      --checkpoint train/logs/rsl_rl/rm2025_later_cc_v1/<run>/model_200.pt \
      --num-envs 128 --device cuda:0 --seed 0

Exit code 0 iff every gate passes.  Always writes JSON (train/deploy/) and a Markdown
report (docs/).  The script never mutates the checkpoint or the training run.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

import rmvehicle  # noqa: E402,F401  (registers the tasks)
from rmvehicle import robot_cfg as RC  # noqa: E402
from rmvehicle.mdp import rewards as rm_rewards  # noqa: E402
from rmvehicle.names import RM2025_LATER  # noqa: E402
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper  # noqa: E402
from mjlab.tasks.registry import (  # noqa: E402
    load_env_cfg,
    load_rl_cfg,
    load_runner_cls,
)

FLAT_TASK = "RM2025-Later-CC-Flat-v0"
FIELD_TASK = "RM2025-Later-CC-Field-v0"

# Keep in lockstep with docs/ACCEPTANCE_RM2025_LATER.md section 1.
THRESHOLDS = {
    "survival_seconds": 20.0,
    "survival_rate_min": 0.95,
    "survival_alive_frac_min_for_other_tests": 0.90,
    "speed_cmds_m_s": (1.5, 2.0, 2.8),
    "speed_tol_m_s": {1.5: 0.30, 2.0: 0.30, 2.8: 0.50},
    "speed_ramp_s": 2.0,
    "speed_measure_s": 3.0,
    "gyro_cmd_rad_s": 2.0 * math.pi * 2.0,  # 12.566..., 2 rev/s
    "gyro_min_abs_rad_s": 10.0,
    "gyro_tilt_max_deg": 30.0,
    "gyro_ramp_s": 1.5,
    "gyro_measure_s": 6.0,
    "height_cmd_m": 0.22,
    "height_tol_m": 0.05,
    "height_ramp_s": 2.0,
    "height_measure_s": 3.0,
    "jump_target_m": 0.08,
    "jump_hold_s": 1.2,
    "jump_observe_s": 1.5,
    "jump_peak_min_m": 0.05,
    "jump_peak_max_m": 0.11,
    "jump_upright_min_frac": 0.90,
    "tilt_upright_max_deg": 30.0,
    "nan_events_max": 0,
}

# Domain-randomization / disturbance events removed for the deterministic `nominal`
# condition.  Missing names are ignored, so this stays valid if the training config
# grows new events.
DR_EVENTS = (
    "push_robot",
    "push_impulse",
    "wheel_friction",
    "wheel_torsion_friction",
    "wheel_rolling_friction",
    "base_mass",
    "base_com",
    "leg_stiffness",
    "leg_damping",
    "leg_effort_scale",
    "wheel_effort_scale",
    "leg_encoder_bias",
    "leg_armature",
    "leg_frictionloss",
    "wheel_armature",
    "wheel_frictionloss",
    "limb_pseudo_inertia",
    "wheel_pseudo_inertia",
    "gas_spring_stiffness",
    "gas_spring_damping",
    "gas_spring_friction",
    "reset_base",
)

TZ = timezone(timedelta(hours=8))


def log(msg: str) -> None:
    print(msg, flush=True)


def seed_all(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def finite_all(x: torch.Tensor) -> bool:
    return bool(torch.isfinite(x).all().item())


def percentile(x: torch.Tensor, q: float) -> float:
    if x.numel() == 0:
        return float("nan")
    return float(torch.quantile(x.float().reshape(-1), q).item())


class EvalEnv:
    """One mjlab task + one loaded inference policy, with deterministic settings."""

    def __init__(
        self,
        task: str,
        checkpoint: str,
        num_envs: int,
        device: str,
        seed: int,
        *,
        keep_jump_schedule: bool,
        freeze_commands: bool,
        condition: str,
    ) -> None:
        seed_all(seed)
        cfg = load_env_cfg(task, play=True)
        cfg.scene.num_envs = num_envs
        cfg.episode_length_s = 1e9
        cfg.auto_reset = True
        cfg.observations["actor"].enable_corruption = False

        # HARD GUARD (2026-09-10): this harness used to build the later env WITHOUT the
        # launcher's RM_WHEEL_SCALE=10, so it evaluated every wheel command 5.5x too large
        # and reported 0.8% flat survival for a policy whose training log said 19.5 s
        # episodes.  The trained wheel unit now lives in names.RM2025_LATER and the deploy
        # contract; if the env we just built disagrees with the contract, refuse to run.
        contract_path = ROOT / "train" / "deploy" / "contract_rm2025_later.json"
        if contract_path.exists() and task in (FLAT_TASK, FIELD_TASK):
            contract = json.loads(contract_path.read_text(encoding="utf8"))
            want_scale = float(contract["wheel_action_scale"])
            got_scale = float(cfg.actions["wheel_joint_vel"].scale)
            log("[contract] wheel_action_scale env=%.6g contract=%.6g" % (got_scale, want_scale))
            if abs(got_scale - want_scale) > 1e-9:
                raise SystemExit(
                    "ACCEPTANCE REFUSED: env wheel action scale %.6g != deploy contract %.6g "
                    "(RM_WHEEL_SCALE / names.wheel_action_scale_override drift)"
                    % (got_scale, want_scale)
                )

        if condition == "nominal":
            for name in DR_EVENTS:
                cfg.events.pop(name, None)
            rh = cfg.events.get("reset_height")
            if rh is not None:
                rh.params["range"] = (
                    THRESHOLDS["height_cmd_m"],
                    THRESHOLDS["height_cmd_m"],
                )
        elif condition != "as-trained":
            raise SystemExit(f"unknown condition {condition!r}")

        if not keep_jump_schedule:
            cfg.events.pop("jump_schedule", None)

        if freeze_commands:
            tw = cfg.commands.get("twist")
            if tw is not None:
                tw.resampling_time_range = (1e9, 1e9)

        self.task = task
        self.condition = condition
        self.cfg = cfg
        self.agent_cfg = load_rl_cfg(task)
        self.device = device
        self.env = ManagerBasedRlEnv(cfg=cfg, device=device)
        self.env = RslRlVecEnvWrapper(
            self.env, clip_actions=self.agent_cfg.clip_actions
        )
        runner_cls = load_runner_cls(task) or MjlabOnPolicyRunner
        self.runner = runner_cls(self.env, asdict(self.agent_cfg), device=device)
        self.runner.load(
            checkpoint, load_cfg={"actor": True}, strict=True, map_location=device
        )
        self.policy = self.runner.get_inference_policy(device=device)

        self.E = self.env.unwrapped
        self.robot = self.E.scene["robot"]
        self.N = int(self.E.num_envs)
        self.dt = float(self.E.step_dt)
        self.contract = RC.contract(RM2025_LATER)

        joint_names = list(self.robot.joint_names)
        wheel_pats = [p.strip("^$") for p in RM2025_LATER.wheel_joints]
        self.wheel_joint_ids = [
            i
            for i, n in enumerate(joint_names)
            if any(re.fullmatch(p, n) for p in wheel_pats)
        ]
        assert len(self.wheel_joint_ids) == 2, joint_names
        actuator_names = list(self.robot.actuator_names)
        self.wheel_act_ids = [
            i for i, n in enumerate(actuator_names) if "wheel" in n
        ]
        assert len(self.wheel_act_ids) == 2, actuator_names
        self.wheel_effort = float(RC.wheel_effort_for(RM2025_LATER))
        self.wheel_per_yaw = float(
            self.contract["half_track"] / self.contract["wheel_radius"]
        )

        self.alive = torch.ones(self.N, dtype=torch.bool, device=device)
        self.term_counts: dict[str, int] = {}
        self.nan_action_envs = 0
        self.nan_obs_envs = 0

    # ------------------------------------------------------------------ state
    def reset(self, height: float | None = None) -> None:
        self.E.reset()
        self.alive[:] = True
        self.term_counts = {}
        self.nan_action_envs = 0
        self.nan_obs_envs = 0
        self.set_cmd(0.0, 0.0, THRESHOLDS["height_cmd_m"] if height is None else height)
        self.set_jump(0.0, 0.0)

    def set_cmd(self, vx: float, wz: float, height: float | None = None) -> None:
        cmd = self.E.command_manager.get_term("twist").command
        cmd[:, 0] = float(vx)
        cmd[:, 1] = 0.0
        cmd[:, 2] = float(wz)
        if height is not None:
            h = getattr(self.E, "_rm_height_cmd", None)
            if h is None:
                h = torch.full(
                    (self.N, 1), float(height), device=self.device
                )
                self.E._rm_height_cmd = h
            h[:] = float(height)

    def set_jump(self, flag: float, rise: float = 0.0) -> None:
        if not hasattr(self.E, "_rm_jump_flag"):
            self.E._rm_jump_flag = torch.zeros(self.N, 1, device=self.device)
            self.E._rm_jump_target = torch.zeros(self.N, 1, device=self.device)
        self.E._rm_jump_flag[:] = float(flag)
        self.E._rm_jump_target[:] = float(rise) if flag else 0.0

    # ------------------------------------------------------------------ sensors
    def tilt_deg(self) -> torch.Tensor:
        g = self.robot.data.projected_gravity_b
        return torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0)))

    def vx(self) -> torch.Tensor:
        return self.robot.data.root_link_lin_vel_b[:, 0]

    def wz(self) -> torch.Tensor:
        return self.robot.data.root_link_ang_vel_b[:, 2]

    def measured_height(self) -> torch.Tensor:
        body_names = (
            RM2025_LATER.thigh_bodies[0],
            RM2025_LATER.wheel_bodies[0],
            RM2025_LATER.thigh_bodies[1],
            RM2025_LATER.wheel_bodies[1],
        )
        return rm_rewards.measured_height(
            self.E, body_names=body_names
        ).reshape(-1)

    def wheel_speed_abs_mean(self) -> torch.Tensor:
        return self.robot.data.joint_vel[:, self.wheel_joint_ids].abs().mean(dim=1)

    def wheel_torque_abs_mean(self) -> torch.Tensor:
        force = getattr(self.robot.data, "actuator_force", None)
        if force is None:
            return torch.zeros(self.N, device=self.device)
        return force[:, self.wheel_act_ids].abs().mean(dim=1)

    def wheel_torque_sat_frac(self) -> torch.Tensor:
        force = getattr(self.robot.data, "actuator_force", None)
        if force is None:
            return torch.zeros(self.N, device=self.device)
        sat = (
            force[:, self.wheel_act_ids].abs()
            > 0.985 * self.wheel_effort
        ).float()
        return sat.mean(dim=1)

    def airborne(self) -> torch.Tensor:
        sensor = self.E.scene["wheel_contact"]
        found = sensor.data.found
        touching = (found > 0).float().reshape(self.N, -1).max(dim=1).values
        return 1.0 - touching

    # ------------------------------------------------------------------ stepping
    def act(self) -> torch.Tensor:
        with torch.no_grad():
            return self.policy(self.E.obs_buf)

    def step_once(self) -> None:
        prev = self.alive.clone()
        action = self.act()
        if not finite_all(action):
            bad = ~torch.isfinite(action).all(dim=-1)
            self.nan_action_envs += int(bad.sum().item())
        self.env.step(action)
        term = self.E.reset_terminated.bool()
        for name in self.E.termination_manager.active_terms:
            hit = self.E.termination_manager.get_term(name).bool() & prev
            n = int(hit.sum().item())
            if n:
                self.term_counts[name] = self.term_counts.get(name, 0) + n
        self.alive &= ~term
        obs = self.E.obs_buf
        if isinstance(obs, dict):
            obs = obs.get("actor", obs.get("policy"))
        if obs is not None and not finite_all(obs):
            bad = ~torch.isfinite(obs).all(dim=-1)
            self.nan_obs_envs += int(bad.sum().item())

    def advance(
        self,
        seconds: float,
        *,
        collect=None,
        sample_period: float = 0.05,
    ):
        """Run `seconds`; return [(alive_mask, collected_dict), ...]."""
        steps = int(round(float(seconds) / self.dt))
        every = max(1, int(round(float(sample_period) / self.dt)))
        rows = []
        for k in range(steps):
            self.step_once()
            if collect is not None and k % every == 0:
                rows.append((self.alive.clone(), collect()))
        return rows

    def close(self) -> None:
        try:
            self.env.close()
        except Exception:
            pass


# ---------------------------------------------------------------------- helpers
def flatten_rows(rows, key: str) -> tuple[torch.Tensor, torch.Tensor]:
    if not rows:
        dev = "cpu"
        return torch.zeros(0, device=dev), torch.zeros(0, dtype=torch.bool, device=dev)
    vals = torch.cat([r[1][key].reshape(-1) for r in rows])
    masks = torch.cat([r[0].reshape(-1) for r in rows])
    return vals[masks], masks


def stats(rows, key: str) -> dict:
    vals, _ = flatten_rows(rows, key)
    if vals.numel() == 0:
        return {"n": 0, "mean": None, "p50": None, "p95": None, "max": None}
    return {
        "n": int(vals.numel()),
        "mean": float(vals.mean().item()),
        "p50": float(vals.median().item()),
        "p95": percentile(vals, 0.95),
        "max": float(vals.max().item()),
    }


def per_env_mean(rows, key: str, n_envs: int) -> torch.Tensor:
    sums = torch.zeros(n_envs)
    counts = torch.zeros(n_envs)
    for mask, data in rows:
        v = data[key].reshape(-1).detach().cpu().float()
        m = mask.reshape(-1).detach().cpu().float()
        sums += torch.where(m > 0, v, torch.zeros_like(v))
        counts += m
    return (sums / counts.clamp(min=1.0))[counts > 0]


def alive_frac(rows, n_envs: int) -> float:
    if not rows:
        return 1.0
    masks = torch.cat([r[0].reshape(-1).detach().cpu() for r in rows])
    return float(masks.float().mean().item())


def fmt(x, nd: int = 3) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return "n/a"
    return f"{x:.{nd}f}"


def _placeholder_survival(task: str) -> dict:
    return {
        "task": task,
        "seconds": THRESHOLDS["survival_seconds"],
        "num_envs": 0,
        "survival_rate": 0.0,
        "upright_rate": 0.0,
        "tilt_deg": {"n": 0, "mean": None, "p50": None, "p95": None, "max": None},
        "terminations": {},
        "nan_action_envs": 0,
        "nan_obs_envs": 0,
        "pass": False,
        "error": "not run",
    }


def _placeholder_gyro() -> dict:
    return {
        "cmd_rad_s": THRESHOLDS["gyro_cmd_rad_s"],
        "achieved_mean_rad_s": None,
        "achieved_abs_rad_s": 0.0,
        "achieved_rev_s": 0.0,
        "min_abs_rad_s": THRESHOLDS["gyro_min_abs_rad_s"],
        "tilt_deg": {"n": 0, "mean": None, "p50": None, "p95": None, "max": None},
        "wheel_speed_rad_s": {"n": 0, "mean": None},
        "wheel_tau_nm": {"n": 0, "mean": None},
        "wheel_tau_sat_frac": {"n": 0, "mean": None},
        "alive_frac": 0.0,
        "nan_action_envs": 0,
        "nan_obs_envs": 0,
        "pass": False,
        "error": "not run",
    }


def _placeholder_height() -> dict:
    return {
        "cmd_m": THRESHOLDS["height_cmd_m"],
        "measured_mean_m": None,
        "err_mean_m": None,
        "err_p95_m": None,
        "err_max_m": None,
        "tol_m": THRESHOLDS["height_tol_m"],
        "alive_frac": 0.0,
        "nan_action_envs": 0,
        "nan_obs_envs": 0,
        "pass": False,
        "error": "not run",
    }


def _placeholder_jump() -> dict:
    return {
        "target_m": THRESHOLDS["jump_target_m"],
        "hold_s": THRESHOLDS["jump_hold_s"],
        "observe_s": THRESHOLDS["jump_observe_s"],
        "valid_envs": 0,
        "num_envs": 0,
        "peak_median_m": 0.0,
        "peak_p50_m": 0.0,
        "peak_p95_m": None,
        "peak_max_m": None,
        "peak_in_window_frac": 0.0,
        "air_time_median_s": 0.0,
        "landed_upright_frac": 0.0,
        "final_tilt_deg": {"n": 0, "mean": None, "p50": None, "p95": None, "max": None},
        "terminations": {},
        "nan_action_envs": 0,
        "nan_obs_envs": 0,
        "pass": False,
        "error": "not run",
    }


def checkpoint_iteration(path: Path) -> int | None:
    m = re.search(r"model_(\d+)\.pt$", path.name)
    return int(m.group(1)) if m else None


def run_identity_gate(task: str, device: str, out_path: Path) -> dict:
    script = ROOT / "scripts" / "check_model_identity.py"
    if not script.exists():
        return {"pass": False, "detail": f"missing {script}"}
    env = os.environ.copy()
    pp = [
        str(ROOT / "train" / "rmvehicle" / "src"),
        str(ROOT / "third_party" / "rc_mjlab" / "mjlab" / "src"),
    ]
    if env.get("PYTHONPATH"):
        pp.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pp)
    cmd = [
        sys.executable,
        str(script),
        "--task",
        task,
        "--model",
        "later",
        "--num-envs",
        "4",
        "--device",
        device,
        "--json-out",
        str(out_path),
    ]
    log(f"[identity] {' '.join(cmd)}")
    proc = subprocess.run(
        cmd, cwd=str(ROOT), env=env, capture_output=True, text=True
    )
    detail = {
        "pass": proc.returncode == 0,
        "returncode": int(proc.returncode),
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-2000:],
    }
    if out_path.exists():
        try:
            detail["json"] = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            detail["json_error"] = str(exc)
    return detail


# ---------------------------------------------------------------------- tests
def test_survival(
    task: str,
    checkpoint: str,
    args,
    label: str,
) -> dict:
    log(f"[{label}] building env ({task}) ...")
    ev = EvalEnv(
        task,
        checkpoint,
        args.num_envs,
        args.device,
        args.seed,
        keep_jump_schedule=True,
        freeze_commands=False,
        condition=args.condition,
    )
    try:
        ev.reset()
        seconds = THRESHOLDS["survival_seconds"]
        log(f"[{label}] running {seconds:.0f} s with the task command distribution ...")
        t0 = time.time()
        rows = ev.advance(
            seconds,
            collect=lambda: {"tilt": ev.tilt_deg()},
            sample_period=0.25,
        )
        final_tilt = ev.tilt_deg()
        survival_rate = float(ev.alive.float().mean().item())
        upright_rate = float(
            ((ev.alive) & (final_tilt < THRESHOLDS["tilt_upright_max_deg"]))
            .float()
            .mean()
            .item()
        )
        tilt_stats = stats(rows, "tilt")
        result = {
            "task": task,
            "seconds": seconds,
            "num_envs": ev.N,
            "survival_rate": survival_rate,
            "upright_rate": upright_rate,
            "tilt_deg": tilt_stats,
            "terminations": dict(sorted(ev.term_counts.items())),
            "nan_action_envs": ev.nan_action_envs,
            "nan_obs_envs": ev.nan_obs_envs,
            "wall_s": round(time.time() - t0, 2),
            "pass": survival_rate >= THRESHOLDS["survival_rate_min"]
            and ev.nan_action_envs == 0
            and ev.nan_obs_envs == 0
            and ev.term_counts.get("nan_detection", 0) == 0,
        }
        log(
            f"[{label}] survival {100 * survival_rate:.1f}%  "
            f"upright {100 * upright_rate:.1f}%  "
            f"tilt mean {fmt(tilt_stats['mean'], 1)}°  "
            f"terms {result['terminations']}"
        )
        return result
    finally:
        ev.close()


def test_controlled_flat(checkpoint: str, args) -> dict:
    """Speed / gyro / height on one deterministic flat env."""
    log(f"[flat] building controlled env ({FLAT_TASK}) ...")
    ev = EvalEnv(
        FLAT_TASK,
        checkpoint,
        args.num_envs,
        args.device,
        args.seed,
        keep_jump_schedule=False,
        freeze_commands=True,
        condition=args.condition,
    )
    out = {"speed": [], "gyro": None, "height": None}
    try:
        # ---------------------------------------------------------- speed
        for cmd in THRESHOLDS["speed_cmds_m_s"]:
            ev.reset()
            ev.set_cmd(vx=cmd, wz=0.0, height=THRESHOLDS["height_cmd_m"])
            ev.advance(THRESHOLDS["speed_ramp_s"])
            rows = ev.advance(
                THRESHOLDS["speed_measure_s"],
                collect=lambda: {"vx": ev.vx(), "tilt": ev.tilt_deg()},
                sample_period=0.05,
            )
            vx_stats = stats(rows, "vx")
            per_env = per_env_mean(rows, "vx", ev.N)
            err = (
                abs(float(vx_stats["mean"]) - cmd)
                if vx_stats["mean"] is not None
                else None
            )
            row = {
                "cmd_m_s": cmd,
                "achieved_mean_m_s": vx_stats["mean"],
                "achieved_p50_env_m_s": (
                    float(per_env.median().item()) if per_env.numel() else None
                ),
                "err_m_s": err,
                "tol_m_s": THRESHOLDS["speed_tol_m_s"][cmd],
                "alive_frac": alive_frac(rows, ev.N),
                "tilt_deg": stats(rows, "tilt"),
                "nan_action_envs": ev.nan_action_envs,
                "nan_obs_envs": ev.nan_obs_envs,
            }
            row["pass"] = (
                err is not None
                and err <= row["tol_m_s"]
                and row["alive_frac"]
                >= THRESHOLDS["survival_alive_frac_min_for_other_tests"]
                and row["nan_action_envs"] == 0
                and row["nan_obs_envs"] == 0
            )
            out["speed"].append(row)
            log(
                f"[speed] cmd {cmd:.2f} -> {fmt(row['achieved_mean_m_s'], 2)} m/s "
                f"(err {fmt(err, 2)} / tol {row['tol_m_s']:.2f}, "
                f"alive {100 * row['alive_frac']:.0f}%) "
                f"{'PASS' if row['pass'] else 'FAIL'}"
            )

        # ---------------------------------------------------------- gyro
        wz_cmd = THRESHOLDS["gyro_cmd_rad_s"]
        ev.reset()
        ev.set_cmd(vx=0.0, wz=wz_cmd, height=THRESHOLDS["height_cmd_m"])
        ev.advance(THRESHOLDS["gyro_ramp_s"])
        rows = ev.advance(
            THRESHOLDS["gyro_measure_s"],
            collect=lambda: {
                "wz": ev.wz(),
                "tilt": ev.tilt_deg(),
                "wheel_speed": ev.wheel_speed_abs_mean(),
                "wheel_tau": ev.wheel_torque_abs_mean(),
                "wheel_sat": ev.wheel_torque_sat_frac(),
            },
            sample_period=0.05,
        )
        wz_stats = stats(rows, "wz")
        tilt_stats = stats(rows, "tilt")
        wheel_stats = stats(rows, "wheel_speed")
        tau_stats = stats(rows, "wheel_tau")
        sat_stats = stats(rows, "wheel_sat")
        achieved_abs = (
            abs(float(wz_stats["mean"])) if wz_stats["mean"] is not None else 0.0
        )
        tilt_p95 = tilt_stats["p95"]
        tilt_mean = tilt_stats["mean"]
        gyro_pass = (
            achieved_abs >= THRESHOLDS["gyro_min_abs_rad_s"]
            and tilt_p95 is not None
            and tilt_p95 < THRESHOLDS["gyro_tilt_max_deg"]
            and tilt_mean is not None
            and tilt_mean < THRESHOLDS["gyro_tilt_max_deg"]
            and alive_frac(rows, ev.N)
            >= THRESHOLDS["survival_alive_frac_min_for_other_tests"]
            and ev.nan_action_envs == 0
            and ev.nan_obs_envs == 0
        )
        out["gyro"] = {
            "cmd_rad_s": wz_cmd,
            "achieved_mean_rad_s": wz_stats["mean"],
            "achieved_abs_rad_s": achieved_abs,
            "achieved_rev_s": achieved_abs / (2.0 * math.pi),
            "min_abs_rad_s": THRESHOLDS["gyro_min_abs_rad_s"],
            "tilt_deg": tilt_stats,
            "wheel_speed_rad_s": wheel_stats,
            "wheel_tau_nm": tau_stats,
            "wheel_tau_sat_frac": sat_stats,
            "alive_frac": alive_frac(rows, ev.N),
            "nan_action_envs": ev.nan_action_envs,
            "nan_obs_envs": ev.nan_obs_envs,
            "pass": gyro_pass,
        }
        log(
            f"[gyro] cmd {wz_cmd:.2f} -> |wz| {fmt(achieved_abs, 2)} rad/s "
            f"({fmt(achieved_abs / (2 * math.pi), 2)} rev/s), "
            f"tilt mean {fmt(tilt_stats['mean'], 1)}° p95 {fmt(tilt_stats['p95'], 1)}°, "
            f"wheel {fmt(wheel_stats['mean'], 1)} rad/s "
            f"tau {fmt(tau_stats['mean'], 2)} Nm sat {fmt(100 * (sat_stats['mean'] or 0), 1)}% "
            f"{'PASS' if gyro_pass else 'FAIL'}"
        )

        # ---------------------------------------------------------- height
        h_cmd = THRESHOLDS["height_cmd_m"]
        ev.reset(height=h_cmd)
        ev.set_cmd(vx=0.0, wz=0.0, height=h_cmd)
        ev.advance(THRESHOLDS["height_ramp_s"])

        def _h_err():
            return (ev.measured_height() - h_cmd).abs()

        rows = ev.advance(
            THRESHOLDS["height_measure_s"],
            collect=lambda: {
                "h_err": _h_err(),
                "height": ev.measured_height(),
                "tilt": ev.tilt_deg(),
            },
            sample_period=0.05,
        )
        h_stats = stats(rows, "h_err")
        height_stats = stats(rows, "height")
        h_err_mean = h_stats["mean"]
        height_pass = (
            h_err_mean is not None
            and h_err_mean <= THRESHOLDS["height_tol_m"]
            and alive_frac(rows, ev.N)
            >= THRESHOLDS["survival_alive_frac_min_for_other_tests"]
            and ev.nan_action_envs == 0
            and ev.nan_obs_envs == 0
        )
        out["height"] = {
            "cmd_m": h_cmd,
            "measured_mean_m": height_stats["mean"],
            "err_mean_m": h_stats["mean"],
            "err_p95_m": h_stats["p95"],
            "err_max_m": h_stats["max"],
            "tol_m": THRESHOLDS["height_tol_m"],
            "alive_frac": alive_frac(rows, ev.N),
            "nan_action_envs": ev.nan_action_envs,
            "nan_obs_envs": ev.nan_obs_envs,
            "pass": height_pass,
        }
        log(
            f"[height] cmd {h_cmd:.2f} -> measured {fmt(height_stats['mean'], 3)} m, "
            f"|err| mean {fmt(h_stats['mean'], 3)} p95 {fmt(h_stats['p95'], 3)} "
            f"(tol {THRESHOLDS['height_tol_m']:.2f}) "
            f"{'PASS' if height_pass else 'FAIL'}"
        )
        return out
    finally:
        ev.close()


def test_jump(checkpoint: str, args) -> dict:
    log(f"[jump] building env ({FLAT_TASK}) ...")
    ev = EvalEnv(
        FLAT_TASK,
        checkpoint,
        args.num_envs,
        args.device,
        args.seed,
        keep_jump_schedule=False,
        freeze_commands=True,
        condition=args.condition,
    )
    try:
        ev.reset()
        ev.set_cmd(vx=0.0, wz=0.0, height=THRESHOLDS["height_cmd_m"])
        ev.advance(2.0)
        z0 = ev.robot.data.root_link_pos_w[:, 2].clone()
        ev.set_jump(1.0, THRESHOLDS["jump_target_m"])

        peaks = torch.full((ev.N,), -1e9, device=ev.device)
        air = torch.zeros(ev.N, device=ev.device)
        upright = torch.ones(ev.N, dtype=torch.bool, device=ev.device)
        steps = int(
            round(
                (THRESHOLDS["jump_hold_s"] + THRESHOLDS["jump_observe_s"]) / ev.dt
            )
        )
        hold_steps = int(round(THRESHOLDS["jump_hold_s"] / ev.dt))
        for k in range(steps):
            if k == hold_steps:
                ev.set_jump(0.0, 0.0)
            ev.step_once()
            tilt = ev.tilt_deg()
            up = tilt < THRESHOLDS["tilt_upright_max_deg"]
            alive = ev.alive
            dz = ev.robot.data.root_link_pos_w[:, 2] - z0
            good = up & alive
            peaks = torch.where(
                good, torch.maximum(peaks, dz), peaks
            )
            air += ev.airborne() * good.float() * ev.dt
            upright &= up | ~alive

        valid = ev.alive & (peaks > -1e8)
        peak_vals = peaks[valid]
        air_vals = air[valid]
        median_peak = (
            float(peak_vals.median().item()) if peak_vals.numel() else 0.0
        )
        median_air = float(air_vals.median().item()) if air_vals.numel() else 0.0
        in_window = (
            ((peak_vals >= THRESHOLDS["jump_peak_min_m"])
             & (peak_vals <= THRESHOLDS["jump_peak_max_m"]))
            .float()
            .mean()
            .item()
            if peak_vals.numel()
            else 0.0
        )
        final_tilt = ev.tilt_deg()
        landed_upright = float(
            (
                ev.alive
                & upright
                & (final_tilt < THRESHOLDS["tilt_upright_max_deg"])
            )
            .float()
            .mean()
            .item()
        )
        jump_pass = (
            THRESHOLDS["jump_peak_min_m"]
            <= median_peak
            <= THRESHOLDS["jump_peak_max_m"]
            and landed_upright >= THRESHOLDS["jump_upright_min_frac"]
            and ev.nan_action_envs == 0
            and ev.nan_obs_envs == 0
            and ev.term_counts.get("nan_detection", 0) == 0
        )
        result = {
            "target_m": THRESHOLDS["jump_target_m"],
            "hold_s": THRESHOLDS["jump_hold_s"],
            "observe_s": THRESHOLDS["jump_observe_s"],
            "valid_envs": int(valid.sum().item()),
            "num_envs": ev.N,
            "peak_median_m": median_peak,
            "peak_p50_m": median_peak,
            "peak_p95_m": (
                percentile(peak_vals, 0.95) if peak_vals.numel() else None
            ),
            "peak_max_m": (
                float(peak_vals.max().item()) if peak_vals.numel() else None
            ),
            "peak_in_window_frac": float(in_window),
            "air_time_median_s": median_air,
            "landed_upright_frac": landed_upright,
            "final_tilt_deg": stats(
                [(ev.alive.clone(), {"tilt": final_tilt})], "tilt"
            ),
            "terminations": dict(sorted(ev.term_counts.items())),
            "nan_action_envs": ev.nan_action_envs,
            "nan_obs_envs": ev.nan_obs_envs,
            "pass": jump_pass,
        }
        log(
            f"[jump] peak median {fmt(100 * median_peak, 1)} cm "
            f"(window {100 * in_window:.0f}% of envs), "
            f"air {fmt(median_air, 2)} s, upright {100 * landed_upright:.0f}% "
            f"{'PASS' if jump_pass else 'FAIL'}"
        )
        return result
    finally:
        ev.close()


# ---------------------------------------------------------------------- report
def render_markdown(result: dict) -> str:
    meta = result["meta"]
    th = result["thresholds"]
    c = result["criteria"]
    lines = [
        f"# RM2025 后期闭链模型验收报告 — {meta['checkpoint_name']}",
        "",
        f"- 判定：**{result['verdict']}**",
        f"- 检查点：`{meta['checkpoint']}`（iteration {meta['iteration']}）",
        f"- 任务：`{meta['task_flat']}` / `{meta['task_field']}`",
        f"- 条件：`{meta['condition']}`，{meta['num_envs']} 环境，seed {meta['seed']}，{meta['device']}",
        f"- 时间：{meta['timestamp']}（Asia/Shanghai），耗时 "
        f"{result.get('wall_s', 0.0):.1f} s",
        "",
        "## 总表",
        "",
        "| 条目 | 结果 | 实测 | 门槛 |",
        "|---|---|---|---|",
    ]

    def row(name: str, item: dict, measured: str, threshold: str) -> None:
        lines.append(
            f"| {name} | {'PASS' if item.get('pass') else 'FAIL'} | {measured} | {threshold} |"
        )

    row(
        "物理身份门禁",
        c["identity"],
        f"returncode {c['identity'].get('returncode', 'n/a')}",
        "退出码 0",
    )
    row(
        "数值健康（NaN）",
        c["no_nan"],
        f"action {c['no_nan']['nan_action_envs']} / obs {c['no_nan']['nan_obs_envs']}",
        f"≤ {th['nan_events_max']}",
    )
    for key, label in (("survival_flat", "平地存活"), ("survival_field", "场地存活")):
        item = c[key]
        row(
            label,
            item,
            f"{100 * item['survival_rate']:.1f}%",
            f"≥ {100 * th['survival_rate_min']:.0f}% / {th['survival_seconds']:.0f} s",
        )
    speed_rows = c["speed_tracking"]["rows"]
    speed_ok = bool(speed_rows) and all(r["pass"] for r in speed_rows)
    speed_measured = "; ".join(
        f"{r['cmd_m_s']:.1f}→{fmt(r['achieved_mean_m_s'], 2)} (err {fmt(r['err_m_s'], 2)})"
        for r in c["speed_tracking"]["rows"]
    )
    lines.append(
        f"| 速度跟踪 | {'PASS' if speed_ok else 'FAIL'} | {speed_measured} | "
        f"err ≤ 0.30/0.30/0.50 m/s |"
    )
    g = c["gyro"]
    row(
        "小陀螺",
        g,
        f"|wz| {fmt(g['achieved_abs_rad_s'], 2)} rad/s "
        f"({fmt(g['achieved_rev_s'], 2)} rev/s), tilt p95 {fmt(g['tilt_deg']['p95'], 1)}°",
        f"≥ {th['gyro_min_abs_rad_s']:.1f} rad/s，tilt < {th['gyro_tilt_max_deg']:.0f}°",
    )
    h = c["height"]
    row(
        "高度跟踪",
        h,
        f"|err| mean {fmt(h['err_mean_m'], 3)} m",
        f"≤ {th['height_tol_m']:.2f} m",
    )
    j = c["jump"]
    row(
        "跳跃",
        j,
        f"peak {100 * j['peak_median_m']:.1f} cm, upright {100 * j['landed_upright_frac']:.0f}%",
        f"{100 * th['jump_peak_min_m']:.0f}–{100 * th['jump_peak_max_m']:.0f} cm，"
        f"upright ≥ {100 * th['jump_upright_min_frac']:.0f}%",
    )

    lines += ["", "## 细节", ""]
    lines.append("### 存活")
    lines.append("")
    for key, label in (("survival_flat", "平地"), ("survival_field", "场地")):
        s = c[key]
        lines.append(
            f"- **{label}**：存活 {100 * s['survival_rate']:.1f}%，"
            f"直立 {100 * s['upright_rate']:.1f}%，"
            f"tilt mean {fmt(s['tilt_deg']['mean'], 1)}° / p95 {fmt(s['tilt_deg']['p95'], 1)}°，"
            f"终止 {s['terminations'] or '无'}，NaN action {s['nan_action_envs']} / obs {s['nan_obs_envs']}"
        )
    lines += ["", "### 速度跟踪", ""]
    lines.append("| cmd m/s | achieved mean | err | tol | alive | tilt p95 | 判定 |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in c["speed_tracking"]["rows"]:
        lines.append(
            f"| {r['cmd_m_s']:.1f} | {fmt(r['achieved_mean_m_s'], 3)} | "
            f"{fmt(r['err_m_s'], 3)} | {r['tol_m_s']:.2f} | "
            f"{100 * r['alive_frac']:.0f}% | {fmt(r['tilt_deg']['p95'], 1)}° | "
            f"{'PASS' if r['pass'] else 'FAIL'} |"
        )
    lines += ["", "### 小陀螺 / 高度 / 跳跃", ""]
    lines.append(
        f"- 小陀螺：wheel {fmt(g['wheel_speed_rad_s']['mean'], 1)} rad/s，"
        f"tau {fmt(g['wheel_tau_nm']['mean'], 2)} N·m，"
        f"饱和比例 {100 * (g['wheel_tau_sat_frac']['mean'] or 0):.1f}%，"
        f"alive {100 * g['alive_frac']:.0f}%"
    )
    lines.append(
        f"- 高度：measured {fmt(h['measured_mean_m'], 3)} m，"
        f"err mean {fmt(h['err_mean_m'], 3)} / p95 {fmt(h['err_p95_m'], 3)} m，"
        f"alive {100 * h['alive_frac']:.0f}%"
    )
    lines.append(
        f"- 跳跃：valid {j['valid_envs']}/{j['num_envs']} envs，"
        f"peak median {100 * j['peak_median_m']:.1f} cm / p95 {100 * (j['peak_p95_m'] or 0):.1f} cm，"
        f"在 5–11 cm 窗口内 {100 * j['peak_in_window_frac']:.0f}%，"
        f"air {fmt(j['air_time_median_s'], 2)} s，"
        f"落地直立 {100 * j['landed_upright_frac']:.0f}%，"
        f"终止 {j['terminations'] or '无'}"
    )

    lines += ["", "## 失败项", ""]
    if result["failures"]:
        for f in result["failures"]:
            lines.append(f"- {f}")
    else:
        lines.append("无。")

    lines += [
        "",
        "## 说明",
        "",
        "- 本报告由 `train/verify_acceptance_later.py` 自动生成；门槛见 "
        "`docs/ACCEPTANCE_RM2025_LATER.md`。",
        "- `nominal` 条件关闭了 plant/执行器域随机化、观测噪声、push/脉冲扰动，"
        "用于可复现的行为门禁；鲁棒性回归应另跑 `--condition as-trained`。",
        "- 真机放行还需要轮胎外径、轮电机台架曲线、轮端惯量、编码器零位/CAN 延迟实测。",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--num-envs", type=int, default=128)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--condition",
        choices=("nominal", "as-trained"),
        default="nominal",
        help="nominal = strip DR/noise/pushes; as-trained = keep the task DR",
    )
    ap.add_argument(
        "--identity",
        choices=("auto", "skip"),
        default="auto",
        help="run scripts/check_model_identity.py first (auto) or skip it",
    )
    ap.add_argument("--out-json", default="")
    ap.add_argument("--out-md", default="")
    ap.add_argument(
        "--smoke",
        action="store_true",
        help="short windows (4 s survival etc.) for plumbing checks only",
    )
    args = ap.parse_args()

    t0 = time.time()
    if args.smoke:
        if args.num_envs == 128:
            args.num_envs = 16
        THRESHOLDS.update(
            {
                "survival_seconds": 4.0,
                "speed_ramp_s": 1.0,
                "speed_measure_s": 1.5,
                "gyro_ramp_s": 1.0,
                "gyro_measure_s": 2.0,
                "height_ramp_s": 1.0,
                "height_measure_s": 1.5,
                "jump_hold_s": 0.8,
                "jump_observe_s": 1.0,
            }
        )
    ckpt = Path(args.checkpoint).resolve()
    if not ckpt.exists():
        raise SystemExit(f"checkpoint not found: {ckpt}")
    iteration = checkpoint_iteration(ckpt)
    tag = f"model_{iteration}" if iteration is not None else ckpt.stem
    out_json = Path(
        args.out_json
        or ROOT / "train" / "deploy" / f"acceptance_rm2025_later_{tag}.json"
    )
    out_md = Path(
        args.out_md
        or ROOT / "docs" / f"ACCEPTANCE_REPORT_RM2025_LATER_{tag}.md"
    )
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    meta = {
        "checkpoint": str(ckpt),
        "checkpoint_name": ckpt.name,
        "iteration": iteration,
        "task_flat": FLAT_TASK,
        "task_field": FIELD_TASK,
        "num_envs": args.num_envs,
        "seed": args.seed,
        "condition": args.condition,
        "device": args.device,
        "smoke": bool(args.smoke),
        "timestamp": datetime.now(TZ).isoformat(timespec="seconds"),
        "host": os.uname().nodename if hasattr(os, "uname") else os.environ.get("COMPUTERNAME", "?"),
    }
    log("=" * 78)
    log(f"acceptance gate: {ckpt}")
    log(
        f"task={FLAT_TASK} / {FIELD_TASK}  envs={args.num_envs}  "
        f"device={args.device}  condition={args.condition}  seed={args.seed}"
    )
    log("=" * 78)

    criteria: dict[str, dict] = {}
    failures: list[str] = []

    if args.identity == "auto":
        identity = run_identity_gate(
            FLAT_TASK, args.device, ROOT / "train" / "deploy" / "_identity_later.json"
        )
    else:
        identity = {"pass": True, "detail": "skipped by --identity skip"}
    criteria["identity"] = identity
    if not identity.get("pass"):
        failures.append("identity: physical identity gate failed")
    log(
        f"[identity] {'PASS' if identity.get('pass') else 'FAIL'}"
    )

    import traceback

    def run_one(key, fn, placeholder, *a, **kw):
        try:
            criteria[key] = fn(*a, **kw)
        except Exception as exc:
            failures.append(f"{key}: runtime {type(exc).__name__}: {exc}")
            traceback.print_exc()
            criteria[key] = placeholder()

    run_one(
        "survival_flat",
        test_survival,
        lambda: _placeholder_survival(FLAT_TASK),
        FLAT_TASK,
        str(ckpt),
        args,
        "survival_flat",
    )
    run_one(
        "survival_field",
        test_survival,
        lambda: _placeholder_survival(FIELD_TASK),
        FIELD_TASK,
        str(ckpt),
        args,
        "survival_field",
    )
    try:
        controlled = test_controlled_flat(str(ckpt), args)
        criteria["speed_tracking"] = {"rows": controlled["speed"]}
        criteria["gyro"] = controlled["gyro"]
        criteria["height"] = controlled["height"]
    except Exception as exc:
        failures.append(
            f"speed/gyro/height: runtime {type(exc).__name__}: {exc}"
        )
        traceback.print_exc()
        criteria.setdefault("speed_tracking", {"rows": []})
        criteria.setdefault("gyro", _placeholder_gyro())
        criteria.setdefault("height", _placeholder_height())
    run_one("jump", test_jump, _placeholder_jump, str(ckpt), args)

    # Make the report renderable even if an early test aborted.
    criteria.setdefault("survival_flat", _placeholder_survival(FLAT_TASK))
    criteria.setdefault("survival_field", _placeholder_survival(FIELD_TASK))
    criteria.setdefault("speed_tracking", {"rows": []})
    criteria.setdefault("gyro", _placeholder_gyro())
    criteria.setdefault("height", _placeholder_height())
    criteria.setdefault("jump", _placeholder_jump())

    # Aggregate NaN gate across every behavior test.
    nan_action = sum(
        int(criteria.get(k, {}).get("nan_action_envs", 0))
        for k in ("survival_flat", "survival_field")
    )
    nan_obs = sum(
        int(criteria.get(k, {}).get("nan_obs_envs", 0))
        for k in ("survival_flat", "survival_field")
    )
    for k in ("gyro", "height", "jump"):
        item = criteria.get(k) or {}
        nan_action += int(item.get("nan_action_envs", 0))
        nan_obs += int(item.get("nan_obs_envs", 0))
    for row in criteria.get("speed_tracking", {}).get("rows", []):
        nan_action += int(row.get("nan_action_envs", 0))
        nan_obs += int(row.get("nan_obs_envs", 0))
    criteria["no_nan"] = {
        "nan_action_envs": nan_action,
        "nan_obs_envs": nan_obs,
        "pass": nan_action <= THRESHOLDS["nan_events_max"]
        and nan_obs <= THRESHOLDS["nan_events_max"],
    }
    if not criteria["no_nan"]["pass"]:
        failures.append(
            f"no_nan: action {nan_action} / obs {nan_obs} > {THRESHOLDS['nan_events_max']}"
        )

    for key, label in (
        ("survival_flat", "survival_flat"),
        ("survival_field", "survival_field"),
        ("gyro", "gyro"),
        ("height", "height"),
        ("jump", "jump"),
    ):
        item = criteria.get(key) or {}
        if not item.get("pass"):
            failures.append(f"{label}: gate failed (see report)")
    speed_rows = criteria.get("speed_tracking", {}).get("rows", [])
    if not speed_rows or not all(r.get("pass") for r in speed_rows):
        failures.append("speed_tracking: at least one command missed its tolerance")

    result = {
        "meta": meta,
        "thresholds": THRESHOLDS,
        "criteria": criteria,
        "verdict": "PASS" if not failures else "FAIL",
        "failures": failures,
        "wall_s": round(time.time() - t0, 2),
    }
    out_json.write_text(
        json.dumps(
            result, indent=2, ensure_ascii=False, default=str, allow_nan=False
        ),
        encoding="utf-8",
    )
    out_md.write_text(render_markdown(result), encoding="utf-8")
    log("=" * 78)
    log(f"VERDICT: {result['verdict']}  ({len(failures)} failure(s))")
    for f in failures:
        log("  - " + f)
    log(f"wrote {out_json}")
    log(f"wrote {out_md}")
    log("=" * 78)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
