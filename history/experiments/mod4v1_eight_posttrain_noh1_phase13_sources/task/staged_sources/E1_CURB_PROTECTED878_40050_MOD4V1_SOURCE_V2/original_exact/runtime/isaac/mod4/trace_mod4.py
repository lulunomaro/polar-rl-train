r"""MOD4 轨迹录制器 —— 华南虎 (SCUT wheeled-legged_RL) velocity_trace 的 MOD4 移植。

对一份 checkpoint 跑一段无头仿真，按固定采样周期把
    指令 vs 实际速度 / 高度 / 姿态 / 闭链 / 每一项奖励
写进 CSV，并每隔 1 秒重写一次交互式 HTML（曲线 + 奖励热力图），
录制过程中直接用浏览器打开就能看。对应开源实现：

    refs/wheeled-legged_RL-main/scripts/utils/velocity_trace_html.py        (MIT, SCUTRobotLab)
    refs/wheeled-legged_RL-main/source/agent_tasks/.../wheelbipe_V14/env.py   (_record_velocity_trace)

用法（训练在跑时建议用 runs3060/flat_scratch_v1/trace/run_trace.ps1，它会先挂起训练）：

    .venv-isaaclab\Scripts\python.exe isaac\mod4\trace_mod4.py ^
        --checkpoint runs3060\...\model_1450.pt --profile vel --duration 40

离线把旧 CSV 重新渲染成 HTML：

    python scripts\utils\export_velocity_trace_html.py <csv> -o <html>
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "utils"))

DEFAULT_USD = Path(os.environ.get("RM_MOD4_USD", str(ROOT / "incoming" / "_from_target_20260928" / "robot.usd")))
DEFAULT_TRACE_ROOT = Path(os.environ.get("RM_TRACE_ROOT",
                                       str(ROOT / "runs3060" / "flat_scratch_v1" / "traces")))

# --------------------------------------------------------------------------- #
# 命令行
# --------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--checkpoint", required=True, help="要录制的 rsl_rl checkpoint (.pt)")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--env_id", type=int, default=0, help="录制哪个环境（默认 0）")
parser.add_argument("--duration", type=float, default=40.0, help="录制多少仿真秒")
parser.add_argument("--sample_dt", type=float, default=0.02, help="CSV 采样周期（秒），默认 50 Hz")
parser.add_argument("--html_interval", type=float, default=1.0, help="每隔多少仿真秒重写一次 HTML")
parser.add_argument("--profile", choices=("vel", "height", "random"), default="vel",
                    help="vel: 速度阶梯; height: 高度阶梯; random: 用训练时的随机指令")
parser.add_argument("--vx", type=float, default=None, help="固定前向速度（覆盖 profile）")
parser.add_argument("--vy", type=float, default=None, help="固定侧向速度（覆盖 profile）")
parser.add_argument("--wz", type=float, default=None, help="固定偏航角速度（覆盖 profile）")
parser.add_argument("--height-cmd", type=float, default=None, help="固定高度指令（覆盖 profile）")
parser.add_argument("--csv", type=Path, default=None)
parser.add_argument("--html", type=Path, default=None)

from isaaclab.app import AppLauncher

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# --------------------------------------------------------------------------- #
# 环境变量（与探针一致：名义模型、平地、闭链门禁不变）
# --------------------------------------------------------------------------- #
os.environ.setdefault("RM_MOD4_USD", str(DEFAULT_USD))
os.environ.setdefault("RM_DR_OFF", "1")
os.environ.setdefault("RM_MOD4_TERRAIN", "flat")
os.environ.setdefault("RM_ROUTE_KINDS", "")
os.environ.setdefault("RM_ROUTE_WEIGHTS", "")
os.environ.setdefault("RM_CMD_VX_MIN", "0.0")
os.environ.setdefault("RM_CMD_VX_MAX", "1.0")
os.environ.setdefault("RM_CMD_WZ_MIN", "0.0")
os.environ.setdefault("RM_CMD_WZ_MAX", "0.0")
os.environ.setdefault("RM_HEIGHT_MIN", "0.22")
os.environ.setdefault("RM_HEIGHT_MAX", "0.27")
os.environ.setdefault("RM_EPISODE_S", str(args.duration + 5.0))

app = AppLauncher(args).app

import torch  # noqa: E402

sys.path.insert(0, str(ROOT / "isaac" / "mod4"))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402
from importlib import metadata  # noqa: E402

from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlOnPolicyRunnerCfg,
    RslRlPpoActorCriticCfg,
    RslRlPpoAlgorithmCfg,
    RslRlVecEnvWrapper,
    handle_deprecated_rsl_rl_cfg,
)
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from velocity_trace_html import build_reward_signs, build_velocity_trace_html  # noqa: E402

# --------------------------------------------------------------------------- #
# 指令 profile
# --------------------------------------------------------------------------- #
_VEL_LADDER = (
    (5.0, 0.0, 0.0, 0.0),
    (10.0, 0.3, 0.0, 0.0),
    (15.0, 0.6, 0.0, 0.0),
    (20.0, 1.0, 0.0, 0.0),
    (23.0, 0.0, 0.0, 0.0),
    (27.0, 0.0, 0.0, 1.0),
    (31.0, 0.0, 0.0, -1.0),
    (32.0, 0.0, 0.0, 0.0),
)
_HEIGHT_LADDER = ((8.0, 0.22), (16.0, 0.24), (24.0, 0.27))


def _segments(profile, t):
    """返回 (vx, vy, wz, height)；height=None 表示用 RM_HEIGHT band 中点。"""
    if profile == "vel":
        tt = t % _VEL_LADDER[-1][0]
        for t_end, vx, vy, wz in _VEL_LADDER:
            if tt < t_end:
                return vx, vy, wz, None
        return 0.0, 0.0, 0.0, None
    tt = t % _HEIGHT_LADDER[-1][0]
    for t_end, h in _HEIGHT_LADDER:
        if tt < t_end:
            return 0.5, 0.0, 0.0, h
    return 0.5, 0.0, 0.0, 0.24


def _active_profile():
    return "height" if args.profile == "height" else "vel"


def _command_for(t):
    """返回本时刻要写入的 (vx, vy, wz)。"""
    vx, vy, wz, _h = _segments(_active_profile(), t)
    if args.vx is not None:
        vx = args.vx
    if args.vy is not None:
        vy = args.vy
    if args.wz is not None:
        wz = args.wz
    return vx, vy, wz


def _height_for(t):
    if args.height_cmd is not None:
        return args.height_cmd
    _vx, _vy, _wz, h = _segments(_active_profile(), t)
    if h is not None:
        return h
    lo = float(os.environ.get("RM_HEIGHT_MIN", "0.22"))
    hi = float(os.environ.get("RM_HEIGHT_MAX", "0.27"))
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------- #
# 环境 + 策略
# --------------------------------------------------------------------------- #
cfg = mod4_task.Mod4EnvCfg()
cfg.scene.num_envs = args.num_envs
cfg.scene.guide_contact.prim_path = "{ENV_REGEX_NS}/Robot/links/guide_roller_.*"
cfg.scene.wheel_contact.prim_path = "{ENV_REGEX_NS}/Robot/links/(left|right)_wheel"
env = Mod4Env(cfg=cfg)
vec = RslRlVecEnvWrapper(env, clip_actions=6.0)

rcfg = RslRlOnPolicyRunnerCfg(
    seed=0, device="cuda:0", num_steps_per_env=24, max_iterations=1, save_interval=1,
    experiment_name="trace", run_name="trace", clip_actions=6.0, check_for_nan=False,
    policy=RslRlPpoActorCriticCfg(init_noise_std=0.3, actor_hidden_dims=[256, 128, 64],
                                  critic_hidden_dims=[256, 128, 64], activation="elu"),
    algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2,
                                   entropy_coef=0.005, num_learning_epochs=5, num_mini_batches=4,
                                   learning_rate=1e-4, schedule="fixed", gamma=0.99, lam=0.95,
                                   desired_kl=0.01, max_grad_norm=1.0),
)
rcfg = handle_deprecated_rsl_rl_cfg(rcfg, metadata.version("rsl-rl-lib"))
runner = OnPolicyRunner(vec, rcfg.to_dict(), log_dir=None, device=rcfg.device)
runner.load(args.checkpoint)
policy = runner.get_inference_policy(device=env.device)

robot = env.scene["robot"]
term = env.command_manager.get_term("twist")
reward_manager = env.reward_manager
reward_names = list(reward_manager.active_terms)
scales = {}
try:
    for name, tcfg in zip(reward_names, reward_manager._term_cfgs):
        scales[name] = float(getattr(tcfg, "weight", 0.0))
except Exception:
    scales = {}
reward_signs = build_reward_signs(scales)

# --------------------------------------------------------------------------- #
# 输出路径
# --------------------------------------------------------------------------- #
ckpt = Path(args.checkpoint).resolve()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
stem = f"{ckpt.stem}_{args.profile}_{stamp}"
csv_path = Path(args.csv) if args.csv else DEFAULT_TRACE_ROOT / f"{stem}.csv"
html_path = Path(args.html) if args.html else csv_path.with_suffix(".html")
csv_path.parent.mkdir(parents=True, exist_ok=True)
html_path.parent.mkdir(parents=True, exist_ok=True)

fieldnames = [
    "sim_time_s", "episode_time_s", "env_id", "terrain",
    "cmd_x", "cmd_y", "cmd_yaw",
    "vel_x_b", "vel_y_b", "yaw_rate_b",
    "height_cmd", "height_obs", "height_relative", "height_reward_ref", "airborne",
    "tilt_deg", "closure_err_mm", "both_wheels",
    "reward_total",
] + [f"reward_{name}" for name in reward_names]

fh = csv_path.open("w", newline="")
writer = csv.DictWriter(fh, fieldnames=fieldnames)
writer.writeheader()
fh.flush()
print(f"[VelocityTrace] CSV:  {csv_path}")
print(f"[VelocityTrace] HTML: {html_path}")
print(f"[VelocityTrace] checkpoint={ckpt.name}  profile={args.profile}  "
      f"duration={args.duration}s  envs={args.num_envs}  record env={args.env_id}")

rows = []
step_dt = float(env.step_dt)
n_steps = max(1, int(round(args.duration / step_dt)))
eid = args.env_id
last_sample = -1e9
last_html = -1e9
resets = 0
_env_samples_commands = (
    args.profile == "random" and args.vx is None and args.vy is None and args.wz is None
)


def gather_row(t_sim: float):
    cmd = term.command[eid]
    ground = getattr(env, "_mod4_ground_z", None)
    z_abs = float(robot.data.root_pos_w[eid, 2].item())
    z_rel = z_abs - (float(ground[eid].item()) if ground is not None else 0.0)
    gz = float(robot.data.projected_gravity_b[eid, 2].item())
    tilt = math.degrees(math.acos(max(-1.0, min(1.0, -gz))))
    try:
        closures = mod4_task.closure_errors(env)
        closure_mm = max(float(v[eid].item()) for v in closures.values()) * 1000.0
    except Exception:
        closure_mm = float("nan")
    try:
        f = env.scene.sensors["wheel_contact"].data.net_forces_w
        if hasattr(f, "torch"):
            f = f.torch
        both = float((f[eid].norm(dim=-1) > 1.0).all().item())
    except Exception:
        both = float("nan")
    rewards = {}
    step_reward = getattr(reward_manager, "_step_reward", None)
    if step_reward is not None:
        vals = step_reward[eid] * step_dt
        for i, name in enumerate(reward_names):
            rewards[name] = float(vals[i].item())
    row = {
        "sim_time_s": round(t_sim, 4),
        "episode_time_s": round(float(env.episode_length_buf[eid].item()) * step_dt, 4),
        "env_id": int(eid),
        "terrain": os.environ.get("RM_MOD4_TERRAIN", "flat"),
        "cmd_x": float(cmd[0].item()),
        "cmd_y": float(cmd[1].item()),
        "cmd_yaw": float(cmd[2].item()),
        "vel_x_b": float(robot.data.root_lin_vel_b[eid, 0].item()),
        "vel_y_b": float(robot.data.root_lin_vel_b[eid, 1].item()),
        "yaw_rate_b": float(robot.data.root_ang_vel_b[eid, 2].item()),
        "height_cmd": float(mod4_task.height_cmd(env)[eid, 0].item()),
        "height_obs": z_rel,
        "height_relative": z_rel,
        "height_reward_ref": z_rel,
        "airborne": 0,
        "tilt_deg": tilt,
        "closure_err_mm": closure_mm,
        "both_wheels": both,
        "reward_total": float(sum(rewards.values())),
    }
    for name, value in rewards.items():
        row[f"reward_{name}"] = value
    return row


def write_html():
    html = build_velocity_trace_html(rows, reward_signs)
    html_path.write_text(html, encoding="utf-8")


env.reset()
obs = vec.get_observations()
print("[VelocityTrace] recording ...")

for step in range(n_steps):
    t_sim = step * step_dt
    if not _env_samples_commands:
        vx, vy, wz = _command_for(t_sim)
        term.command[:, 0] = vx
        term.command[:, 1] = vy
        term.command[:, 2] = wz
    h = _height_for(t_sim)
    mod4_task.height_cmd(env)[:] = h
    with torch.inference_mode():
        actions = policy(obs)
    obs, _rew, dones, _extras = vec.step(actions)
    policy.reset(dones)
    if bool(dones[eid].item()):
        resets += 1
        print(f"[VelocityTrace] t={t_sim:6.2f}s  env{eid} episode reset (#{resets})")
    t_next = float(env.common_step_counter) * step_dt
    if t_next - last_sample + 1e-9 >= args.sample_dt:
        row = gather_row(t_next)
        rows.append(row)
        writer.writerow(row)
        fh.flush()
        last_sample = t_next
        if t_next - last_html + 1e-9 >= args.html_interval:
            write_html()
            last_html = t_next

write_html()
fh.flush()
fh.close()

manifest = {
    "checkpoint": str(ckpt),
    "checkpoint_sha256": hashlib.sha256(ckpt.read_bytes()).hexdigest(),
    "profile": args.profile,
    "duration_s": args.duration,
    "num_envs": args.num_envs,
    "env_id": eid,
    "sample_dt": args.sample_dt,
    "policy_hz": round(1.0 / step_dt, 3),
    "rows": len(rows),
    "episode_resets": resets,
    "csv": str(csv_path),
    "html": str(html_path),
    "reward_scales": scales,
    "env": {k: v for k, v in os.environ.items() if k.startswith("RM_")},
}
(csv_path.with_suffix(".manifest.json")).write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

if rows:
    tail = rows[-max(1, len(rows) // 3):]
    err_x = sum(abs(r["cmd_x"] - r["vel_x_b"]) for r in tail) / len(tail)
    err_h = sum(abs(r["height_cmd"] - r["height_obs"]) for r in tail) / len(tail)
    tilt = sum(r["tilt_deg"] for r in tail) / len(tail)
    print(f"[VelocityTrace] rows={len(rows)}  resets={resets}  "
          f"|cmd_x-vel_x|={err_x:.3f} m/s  |cmd_h-h|={err_h:.3f} m  tilt={tilt:.2f} deg")
print(f"[VelocityTrace] done -> {html_path}")

env.close()
app.close()
