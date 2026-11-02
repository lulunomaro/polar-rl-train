"""Replay a MOD4 checkpoint against its recorded Isaac Lab training contract.

Install this file as ``<repo>/isaac/mod4/replay_mod4.py``.  It never starts PPO.
The run manifest, robot asset and training source hashes are checked before Isaac
Sim is launched, so a playback cannot silently use a different plant.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts" / "utils"))

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--checkpoint", type=Path, required=True)
parser.add_argument("--manifest", type=Path)
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--env_id", type=int, default=0)
parser.add_argument("--seconds", type=float, default=15.0)
parser.add_argument("--sample_dt", type=float, default=0.02)
parser.add_argument("--html_interval", type=float, default=1.0)
parser.add_argument("--profile", choices=("hold", "vel", "height"), default="hold")
parser.add_argument("--vx", type=float, default=0.0)
parser.add_argument("--wz", type=float, default=0.0)
parser.add_argument("--height_cmd", type=float)
parser.add_argument("--keyboard", action="store_true", help="W/S drive, A/D yaw, Z/X height, space stop")
parser.add_argument("--keyboard_vx", type=float, default=1.0)
parser.add_argument("--keyboard_wz", type=float, default=1.0)
parser.add_argument("--keyboard_height_rate", type=float, default=0.08)
parser.add_argument("--allow_height_extrapolation", action="store_true")
parser.add_argument("--allow_code_drift", action="store_true")
parser.add_argument("--preflight", action="store_true", help="verify checkpoint/asset/source only; do not launch Isaac")
parser.add_argument("--output_dir", type=Path)

# Check the checkpoint and training contract before importing the heavy Isaac Kit
# launcher.  This makes a wrong checkpoint/height fail immediately without GPU use.
args, _launcher_args = parser.parse_known_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_contract():
    ckpt = args.checkpoint.resolve(strict=True)
    manifest_path = (args.manifest or ckpt.parent / "run_manifest.json").resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    for name, expected in manifest.get("src_sha256", {}).items():
        if name in ("robot.usd", "import_contract.json"):
            continue
        path = HERE / name
        if not path.is_file() or sha256(path) != expected:
            errors.append(f"source drift: {path}")
    usd = Path(manifest.get("robot_usd") or manifest.get("env", {}).get("RM_MOD4_USD", ""))
    if not usd.is_file() or sha256(usd) != manifest.get("robot_usd_sha256"):
        errors.append(f"USD drift: {usd}")
    contract = usd.parent / "import_contract.json"
    if not contract.is_file() or sha256(contract) != manifest.get("import_contract_sha256"):
        errors.append(f"import contract drift: {contract}")
    if errors and not args.allow_code_drift:
        raise SystemExit("Playback refused; training contract mismatch:\n" + "\n".join(errors))
    for error in errors:
        print("[replay] WARNING", error, flush=True)
    for key, value in manifest.get("env", {}).items():
        if key.startswith("RM_") and isinstance(value, (str, int, float, bool)):
            os.environ[key] = str(value)
    os.environ["RM_MOD4_USD"] = str(usd)
    os.environ["RM_JUMP_SCRIPT_PROB"] = "0"
    return ckpt, manifest_path, manifest, usd


CHECKPOINT, MANIFEST_PATH, MANIFEST, USD = load_contract()
if args.num_envs < 1 or not 0 <= args.env_id < args.num_envs:
    raise SystemExit("env_id must be within num_envs")

height_min = float(os.environ.get("RM_HEIGHT_MIN", "0.22"))
height_max = float(os.environ.get("RM_HEIGHT_MAX", "0.27"))
if height_min > height_max:
    raise SystemExit("invalid training height interval")
height = float(args.height_cmd if args.height_cmd is not None else 0.5 * (height_min + height_max))
if not args.allow_height_extrapolation and not height_min <= height <= height_max:
    raise SystemExit(
        f"height {height:.3f} m lies outside training [{height_min:.3f}, {height_max:.3f}] m; "
        "use --allow_height_extrapolation to measure this explicitly"
    )
if args.allow_height_extrapolation:
    print("[replay] HEIGHT EXTRAPOLATION ENABLED; this is outside the trained height command band")
if args.preflight:
    import torch
    checkpoint_data = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    actor = checkpoint_data.get("actor_state_dict", {})
    first = actor.get("mlp.0.weight")
    last = actor.get("mlp.6.weight")
    if first is None or last is None or tuple(first.shape)[1] != 35 or tuple(last.shape)[0] != 6:
        raise SystemExit("checkpoint actor shape is not the expected current 35→6 MOD4 MLP")
    print(f"[replay] PREFLIGHT PASS checkpoint={CHECKPOINT.name} "
          f"iter={checkpoint_data.get('iter')} actor=35→6 USD={sha256(USD)[:12]} "
          f"height={height:.3f}m")
    raise SystemExit(0)

from isaaclab.app import AppLauncher

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.keyboard and args.headless:
    raise SystemExit("--keyboard needs a visible Isaac Sim window")

app = AppLauncher(args).app

import torch  # noqa: E402
from importlib import metadata  # noqa: E402
from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg,
    RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg,
)
from rsl_rl.runners import OnPolicyRunner  # noqa: E402
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402
from velocity_trace_html import build_reward_signs, build_velocity_trace_html  # noqa: E402


class Keyboard:
    """SCUT-style held-key control; callbacks only collect state, no simulation writes."""

    def __init__(self):
        import carb.input
        import omni.appwindow

        self.carb = carb.input
        self.interface = carb.input.acquire_input_interface()
        self.keyboard = omni.appwindow.get_default_app_window().get_keyboard()
        self.pressed = set()

        def on_event(event, *unused):
            key = event.input
            if event.type == self.carb.KeyboardEventType.KEY_PRESS:
                self.pressed.add(key)
            elif event.type == self.carb.KeyboardEventType.KEY_RELEASE:
                self.pressed.discard(key)
            return True

        self.subscription = self.interface.subscribe_to_keyboard_events(self.keyboard, on_event)
        self.keys = self.carb.KeyboardInput

    def commands(self, dt: float, current_height: float):
        p, k = self.pressed, self.keys
        vx = args.keyboard_vx * (int(k.W in p) - int(k.S in p))
        wz = args.keyboard_wz * (int(k.A in p) - int(k.D in p))
        if k.SPACE in p:
            vx = wz = 0.0
        low, high = ((0.15, 0.40) if args.allow_height_extrapolation
                     else (height_min, height_max))
        current_height += args.keyboard_height_rate * dt * (int(k.Z in p) - int(k.X in p))
        return vx, wz, min(high, max(low, current_height))

    def close(self):
        self.interface.unsubscribe_to_keyboard_events(self.keyboard, self.subscription)


def profile_command(t: float):
    if args.profile == "vel":
        vx = (0.0 if t < 3 or t >= 13 else 0.3 if t < 6 else 0.6 if t < 9 else 1.0)
        return vx, 0.0, height
    if args.profile == "height":
        fraction = min(1.0, max(0.0, int(t // 5) / 2))
        return args.vx, args.wz, height_min + fraction * (height_max - height_min)
    return args.vx, args.wz, height


def make_runner(vec):
    cfg = RslRlOnPolicyRunnerCfg(
        seed=0, device=(getattr(args, "device", None) or "cuda:0"), num_steps_per_env=24,
        max_iterations=1, save_interval=1, experiment_name="mod4_replay",
        run_name="mod4_replay", clip_actions=6.0, check_for_nan=True,
        obs_groups={"actor": ["policy"], "critic": ["critic"]},
        policy=RslRlPpoActorCriticCfg(
            init_noise_std=0.3, actor_hidden_dims=[256, 128, 64],
            critic_hidden_dims=[256, 128, 64], activation="elu"),
        algorithm=RslRlPpoAlgorithmCfg(
            value_loss_coef=1.0, use_clipped_value_loss=True,
            clip_param=0.2, entropy_coef=0.005, num_learning_epochs=5,
            num_mini_batches=4, learning_rate=1e-4, schedule="fixed",
            gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0),
    )
    cfg = handle_deprecated_rsl_rl_cfg(cfg, metadata.version("rsl-rl-lib"))
    runner = OnPolicyRunner(vec, cfg.to_dict(), log_dir=None, device=cfg.device)
    runner.load(str(CHECKPOINT))
    return runner.get_inference_policy(device=vec.unwrapped.device)


def main():
    current_height = height
    env_cfg = mod4_task.Mod4EnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    env = Mod4Env(cfg=env_cfg)
    vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
    policy = make_runner(vec)
    env.reset()
    keyboard = Keyboard() if args.keyboard else None
    term = env.command_manager.get_term("twist")
    if hasattr(term, "time_left"):
        term.time_left[:] = 1.0e9
    if hasattr(term, "is_standing_env"):
        term.is_standing_env[:] = False

    run_name = MANIFEST.get("run_name", CHECKPOINT.parent.name)
    output_dir = (args.output_dir or ROOT / "replays" / run_name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{CHECKPOINT.stem}_{datetime.now():%Y%m%d_%H%M%S}"
    csv_path = output_dir / f"{stem}.csv"
    html_path = output_dir / f"{stem}.html"
    meta_path = output_dir / f"{stem}.json"
    reward_manager = env.reward_manager
    robot = env.scene["robot"]
    joint_lookup = {name: i for i, name in enumerate(robot.joint_names)}
    leg_indices = [joint_lookup[name] for name in mod4_task.LEG_ORDER if name in joint_lookup]
    wheel_indices = [joint_lookup[name] for name in mod4_task.WHEEL_ORDER if name in joint_lookup]
    gas_springs = mod4_task.CONTRACT.get("gas_springs", {})
    reward_names = list(reward_manager.active_terms)
    scales = {}
    try:
        scales = {name: float(getattr(cfg, "weight", 0.0))
                  for name, cfg in zip(reward_names, reward_manager._term_cfgs)}
    except Exception:
        pass
    fields = [
        "sim_time_s", "episode_time_s", "env_id", "terrain", "reset", "cmd_x", "cmd_yaw",
        "vel_x_b", "yaw_rate_b", "height_cmd", "height_obs", "height_relative", "height_reward_ref",
        "tilt_deg", "closure_err_mm", "mimic_err_rad", "both_wheels",
        "leg_torque_max_Nm", "wheel_torque_max_Nm",
        "spring_force_est_left_N", "spring_force_est_right_N",
        "action_delta", "reward_total",
    ] + [f"reward_{name}" for name in reward_names]
    rows = []
    resets = 0
    step_dt = float(env.step_dt)
    steps = max(1, math.ceil(args.seconds / step_dt))
    sample_steps = max(1, round(args.sample_dt / step_dt))
    html_steps = max(1, round(args.html_interval / step_dt))
    last_action = None
    obs = vec.get_observations()
    print(f"[replay] checkpoint={CHECKPOINT} manifest={MANIFEST_PATH}")
    print(f"[replay] USD={USD} height_band=[{height_min:.3f},{height_max:.3f}] ")
    print(f"[replay] CSV={csv_path} HTML={html_path}")
    if keyboard:
        print("[replay] click Isaac window; W/S drive, A/D yaw, Z/X height, SPACE stop")

    try:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for step in range(steps):
                t = step * step_dt
                if keyboard:
                    vx, wz, current_height = keyboard.commands(step_dt, current_height)
                    height_now = current_height
                else:
                    vx, wz, height_now = profile_command(t)
                term.command[:, 0] = vx
                term.command[:, 1] = 0.0
                term.command[:, 2] = wz
                mod4_task.height_cmd(env)[:] = height_now
                # Fresh policy observation after changing command/height; the previous
                # step's returned obs still contains the previous command.
                obs = vec.get_observations()
                with torch.inference_mode():
                    actions = policy(obs)
                    obs, reward, dones, _ = vec.step(actions)
                if hasattr(policy, "reset"):
                    policy.reset(dones)
                eid = args.env_id
                if bool(dones[eid].item()):
                    resets += 1
                delta = (float((actions[eid] - last_action).abs().mean().item())
                         if last_action is not None else 0.0)
                last_action = actions[eid].clone()
                if step % sample_steps:
                    continue
                ground = getattr(env, "_mod4_ground_z", None)
                root_z = float(robot.data.root_pos_w[eid, 2].item())
                root_h = root_z - (float(ground[eid].item()) if ground is not None else 0.0)
                gz = float(robot.data.projected_gravity_b[eid, 2].item())
                tilt = math.degrees(math.acos(min(1.0, max(-1.0, -gz))))
                try:
                    closure = max(float(v[eid].item()) for v in mod4_task.closure_errors(env).values()) * 1000
                except Exception:
                    closure = float("nan")
                try:
                    mimic = max(float(v[eid].item()) for v in mod4_task.mimic_errors(env).values())
                except Exception:
                    mimic = float("nan")
                try:
                    forces = env.scene.sensors["wheel_contact"].data.net_forces_w[eid]
                    both = int(bool((forces.norm(dim=-1) > 1.0).all().item()))
                except Exception:
                    both = -1
                torques = robot.data.applied_torque[eid]
                leg_torque = (float(torques[leg_indices].abs().max().item())
                              if leg_indices else float("nan"))
                wheel_torque = (float(torques[wheel_indices].abs().max().item())
                                if wheel_indices else float("nan"))
                spring_forces = {}
                for joint_name, spring in gas_springs.items():
                    idx = joint_lookup.get(joint_name)
                    if idx is not None:
                        spring_forces[joint_name] = (
                            float(spring["stiffness_n_m"]) *
                            (float(spring["target_position_m"]) - float(robot.data.joint_pos[eid, idx].item()))
                            - float(spring["damping_n_s_m"]) * float(robot.data.joint_vel[eid, idx].item())
                        )
                row = {
                    "sim_time_s": round((step + 1) * step_dt, 4),
                    "episode_time_s": round(float(env.episode_length_buf[eid].item()) * step_dt, 4),
                    "env_id": eid, "terrain": os.environ.get("RM_MOD4_TERRAIN", "flat"),
                    "reset": int(bool(dones[eid].item())),
                    "cmd_x": float(term.command[eid, 0].item()),
                    "cmd_yaw": float(term.command[eid, 2].item()),
                    "vel_x_b": float(robot.data.root_lin_vel_b[eid, 0].item()),
                    "yaw_rate_b": float(robot.data.root_ang_vel_b[eid, 2].item()),
                    "height_cmd": float(mod4_task.height_cmd(env)[eid, 0].item()),
                    "height_obs": root_h, "height_relative": root_h, "height_reward_ref": root_h,
                    "tilt_deg": tilt, "closure_err_mm": closure,
                    "mimic_err_rad": mimic, "both_wheels": both,
                    "leg_torque_max_Nm": leg_torque, "wheel_torque_max_Nm": wheel_torque,
                    "spring_force_est_left_N": spring_forces.get("left_gas_slide"),
                    "spring_force_est_right_N": spring_forces.get("right_gas_slide"),
                    "action_delta": delta, "reward_total": float(reward[eid].item()),
                }
                step_reward = getattr(reward_manager, "_step_reward", None)
                if step_reward is not None and getattr(step_reward, "ndim", 0) == 2:
                    if step_reward.shape[1] == len(reward_names):
                        row.update({f"reward_{name}": float(step_reward[eid, i].item()) * step_dt
                                    for i, name in enumerate(reward_names)})
                writer.writerow(row)
                f.flush()
                rows.append(row)
                if step % html_steps == 0:
                    html_path.write_text(build_velocity_trace_html(rows, build_reward_signs(scales, rows)),
                                         encoding="utf-8")
                if step % max(1, round(1.0 / step_dt)) == 0:
                    print(f"[replay] t={t:.1f}s vx={row['vel_x_b']:.2f} h={root_h:.3f} "
                          f"tilt={tilt:.1f} wheels={both} closure={closure:.3f}mm", flush=True)
    finally:
        if keyboard:
            keyboard.close()
        if rows:
            html_path.write_text(build_velocity_trace_html(rows, build_reward_signs(scales, rows)),
                                 encoding="utf-8")
        meta = {
            "checkpoint": str(CHECKPOINT), "checkpoint_sha256": sha256(CHECKPOINT),
            "manifest": str(MANIFEST_PATH), "usd_sha256": sha256(USD),
            "rows": len(rows), "resets": resets, "height_training_band_m": [height_min, height_max],
            "height_extrapolation": args.allow_height_extrapolation,
            "csv": str(csv_path), "html": str(html_path),
        }
        if rows:
            clean = [r for r in rows if not r["reset"]]
            if clean:
                valid_contacts = [r["both_wheels"] for r in clean if r["both_wheels"] >= 0]
                valid_closure = [r["closure_err_mm"] for r in clean if math.isfinite(r["closure_err_mm"])]
                valid_mimic = [r["mimic_err_rad"] for r in clean if math.isfinite(r["mimic_err_rad"])]
                meta["single_env_summary"] = {
                    "survived_full_window": resets == 0,
                    "velocity_error_mean_m_s": sum(abs(r["cmd_x"] - r["vel_x_b"]) for r in clean) / len(clean),
                    "height_error_mean_m": sum(abs(r["height_cmd"] - r["height_obs"]) for r in clean) / len(clean),
                    "tilt_mean_deg": sum(r["tilt_deg"] for r in clean) / len(clean),
                    "both_wheels_fraction": (sum(valid_contacts) / len(valid_contacts)
                                             if valid_contacts else None),
                    "closure_max_mm": max(valid_closure) if valid_closure else None,
                    "mimic_max_rad": max(valid_mimic) if valid_mimic else None,
                    "action_delta_mean": sum(r["action_delta"] for r in clean) / len(clean),
                }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        env.close()
        app.close()
    print(f"[replay] complete rows={len(rows)} resets={resets} -> {html_path}")


if __name__ == "__main__":
    main()
