"""Unified 3-Expert Pure-Neural MoE Merger, Zero-Interference Verifier, and Continuous All-Skills Course Showcase
for MOD4v3-Family Wheel-Leg Robots (`MOD4V3_POST_TRAINING_RECIPES_20261118`).

Combines into a single pure-neural `(obs 35D, obs_history 420D) -> action 6D` model:
  - E0 (`mode=[1,0,0,0,0,0,0]`): Frozen `c874` full-DR flat/rough/slope/descent locomotion
  - E1 (`obs[29] > 0.5`):        Best RL Anti-Cheat Single-Step (200mm) Climb + Dead-Stop Park Expert
  - E2 (`obs[30] > 0.5`):        Best RL COD-Style Forward Leap (`跳扑`) & Direct Jump-Onto-Step Expert
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import imageio.v2 as imageio
import mujoco as mj
import numpy as np
import torch
from torch import nn

RECIPES_DIR = Path(__file__).resolve().parents[1]
REPO = RECIPES_DIR.parents[2]
C874_PATH = REPO / "deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt"
D_BEST = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
PLANT = D_BEST / "plant/MOD4v3_HW300N60_R3"
E_TEACH = REPO / "sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1"

STAIR_RL_DIR = REPO / "sources/local/MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118"
FORWARD_LEAP_DIR = REPO / "sources/local/MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118"

for p_s in [str(D_BEST / "runtime/core"), str(E_TEACH), str(E_TEACH / "sim"), str(E_TEACH.parent)]:
    if p_s not in sys.path:
        sys.path.insert(0, p_s)

from mod4_retarget import Mod4Retarget
from play_mod4v3 import Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime

PPO_TO_NATIVE = np.array([0, 2, 1, 3, 4, 5])
NAMES = [
    "left_front1_joint",
    "right_front1_joint",
    "left_rear1_joint",
    "right_rear1_joint",
    "left_wheel_joint",
    "right_wheel_joint",
]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class UnifiedThreeExpertMoE(nn.Module):
    """Single pure-neural deployment module routing E0 (locomotion), E1 (stair climb), and E2 (COD forward leap / step jump)."""

    def __init__(self, stair_common_mod, jump_mod):
        super().__init__()
        self.e0 = stair_common_mod.action_mlp(35)
        self.e0.requires_grad_(False)
        self.e1_stair = stair_common_mod.StairExpert()
        self.e2_jump = jump_mod.PureNeuralForwardLeapExpert(latent_dim=64)
        self.history = stair_common_mod.HistoryQueue()

    def reset_history(self):
        self.history.buffer = None

    @torch.inference_mode()
    def forward_with_history(self, obs: torch.Tensor, hist: torch.Tensor) -> torch.Tensor:
        is_stair = obs[..., 29:30] > 0.5
        is_jump = (obs[..., 30:31] > 0.5) & (~is_stair)

        normal_obs = obs.clone()
        normal_obs[..., 28:35] = normal_obs.new_tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        out = self.e0(normal_obs)
        if bool(is_stair.any()):
            out = torch.where(is_stair, self.e1_stair(obs, hist), out)
        if bool(is_jump.any()):
            out = torch.where(is_jump, self.e2_jump(obs, hist), out)
        return out.clamp(-6.0, 6.0)

    @torch.inference_mode()
    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        hist = self.history.append(obs)
        return self.forward_with_history(obs, hist)


def render_unified_course_video(unified: UnifiedThreeExpertMoE, out_mp4: Path) -> dict:
    """Run one continuous episode: E0 Stand -> E2 COD Forward Dolphin-Dive -> E1 Approach + 200mm Stair Climb + Top Park."""
    original = PLANT / "mjcf/scene.xml"
    tree = ET.parse(original)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(original.parent / "assets"))
    step_edge = 2.75
    step_h = 0.20
    half_len = 1.60
    # Add visual hurdle marker for E2 dive zone + 200mm step platform at x=2.75m for E1 stair climb!
    wb = root.find("worldbody")
    ET.SubElement(wb, "geom", name="dive_marker", type="box", pos="0.55 0 0.002", size="0.03 0.8 0.002", contype="0", conaffinity="0", rgba="0.1 0.8 1.0 0.9")
    ET.SubElement(
        wb,
        "geom",
        name="course_step200",
        type="box",
        pos=f"{step_edge + half_len} 0 {step_h / 2}",
        size=f"{half_len} 1.8 {step_h / 2}",
        contype="1",
        conaffinity="2",
        friction=".9 .005 .0001",
        rgba="0.28 0.36 0.46 1.0",
    )
    tmp_dir = Path(tempfile.mkdtemp(prefix="mod4v3_unified_course_"))
    xml_path = tmp_dir / "scene.xml"
    tree.write(xml_path, encoding="utf8", xml_declaration=True)

    spec = RobotSpec(**json.loads((D_BEST / "runtime/core/template_spec.json").read_text(encoding="utf8"))["spec"])
    runtime = json.loads((PLANT / "runtime_config.json").read_text(encoding="utf8"))
    default = _q_from_runtime(runtime, spec.joint_names)
    bank = json.loads((D_BEST / "plant/reset_bank.json").read_text(encoding="utf8"))
    sem = json.loads((PLANT / "semantics.json").read_text(encoding="utf8"))
    bq, bz = _q_from_bank(bank, sem, spec.joint_names)

    env = Mod4v3Mujoco(str(xml_path), spec, default, bq, bz, action_clip=6.0)
    m, d = env.m, env.d
    m.opt.timestep = 0.0025

    ik = Mod4Retarget()
    init_len = 0.28 - 0.0625
    d.qpos[:] = ik.fit(np.sqrt(init_len ** 2 + ik.lateral_offset ** 2), 0.0)["qpos"]
    d.qpos[:3] = [0.0, 0.0, 0.28 + 0.001]
    d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
    d.qvel[:] = 0.0
    mj.mj_forward(m, d)

    qa = np.array([m.jnt_qposadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
    va = np.array([m.jnt_dofadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
    baseline = np.r_[env.default_q[env.leg_ids].numpy(), [0.0, 0.0]][PPO_TO_NATIVE]
    tire = np.array([m.geom(s + "_tire").id for s in ["left", "right"]])
    bodies = m.geom_bodyid[tire]
    platform = m.geom("course_step200").id

    unified.reset_history()
    prev_a = np.zeros(6, np.float32)
    landed_step = False
    stop_step = False
    hold_s = 0.0
    peak_rim_dive = 0.0
    dive_end_x = 0.0
    states = []

    for k in range(720):
        t_s = k * 0.02
        # 0..0.8s: E0 stand -> 0.8..2.70s: E2 Level-Chassis COD Forward Leap -> 2.70..3.70s: E0 smooth standup to 0.4091m -> 3.70s..end: E1 200mm Stair Climb + Top Park!
        if t_s < 0.80:
            v_cmd, h_cmd, mode = 0.0, 0.28, [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        elif t_s < 2.70:
            v_cmd, h_cmd, mode = 0.0, 0.28, [1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        elif t_s < 3.70:
            alpha_h = min(1.0, (t_s - 2.70) / 0.65)
            v_cmd, h_cmd, mode = 0.0, 0.28 + alpha_h * (0.4091 - 0.28), [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            if abs(t_s - 3.70) < 1e-6:
                dive_end_x = float(d.qpos[0])
                unified.reset_history()
            v_cmd = 0.0 if stop_step else (0.0 if t_s < 4.70 else 0.47)
            h_cmd = 0.20 if landed_step else 0.4091
            mode = [0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0]

        rot = d.xmat[env.base_id].reshape(3, 3)
        yaw_now = math.atan2(float(rot[1, 0]), float(rot[0, 0]))
        wz_cmd = float(np.clip(-2.0 * yaw_now, -0.5, 0.5)) if (2.70 <= t_s < 3.70) else 0.0
        q = d.qpos[qa] - baseline
        q[4:] = 0.0
        obs = np.r_[[v_cmd, 0.0, wz_cmd, h_cmd * 5.0], d.qvel[3:6] * 0.5, rot.T @ np.array([0.0, 0.0, -1.0]), q, d.qvel[va] * 0.1, prev_a, mode].astype(np.float32)
        a = unified(torch.from_numpy(obs).reshape(1, 35))[0].numpy()
        a_t = torch.from_numpy(a[PPO_TO_NATIVE]).reshape(1, 6)
        for j in range(8):
            tau = env._torque(a_t).numpy().reshape(-1)
            if j % 4 == 0:
                d.ctrl[env.act_ids[:4]] = tau[:4]
            d.ctrl[env.act_ids[4:]] = tau[4:]
            mj.mj_step(m, d)
        prev_a = a

        wheel = d.geom_xpos[tire]
        if 0.80 <= t_s < 2.70:
            peak_rim_dive = max(peak_rim_dive, float(np.min(wheel[:, 2]) - 0.0625))

        top = np.zeros(2, bool)
        for i in range(d.ncon):
            c = d.contact[i]
            g1, g2 = int(c.geom1), int(c.geom2)
            if platform not in (g1, g2):
                continue
            f = np.zeros(6)
            mj.mj_contactForce(m, d, i, f)
            other = g2 if g1 == platform else g1
            body = m.geom_bodyid[other]
            for side, b in enumerate(bodies):
                if body == b and f[0] > 5.0 and abs(float(c.pos[2]) - step_h) < 0.012:
                    top[side] = True
        crossed = bool(top.all() and d.qpos[0] > step_edge + 0.03 and np.all(wheel[:, 0] > step_edge + 0.025))
        landed_step |= crossed
        if crossed and float(np.linalg.norm(d.qvel[:2])) <= 0.60:
            hold_s += 0.02
            if hold_s >= 0.40:
                stop_step = True
        states.append(d.qpos.copy())

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    renderer = mj.Renderer(m, height=720, width=1280)
    cam = mj.MjvCamera()
    cam.azimuth = 96.0
    cam.elevation = -15.0
    cam.distance = 2.45
    with imageio.get_writer(str(out_mp4), fps=25, codec="libx264", quality=7) as writer:
        for i in range(0, len(states), 2):
            d.qpos[:] = states[i]
            mj.mj_forward(m, d)
            cam.lookat[:] = [float(d.qpos[0]) + 0.25, 0.0, float(d.qpos[2])]
            renderer.update_scene(d, camera=cam)
            writer.append_data(renderer.render())
    renderer.close()

    return {
        "video_path": str(out_mp4),
        "dive_net_x_m": round(dive_end_x, 4),
        "dive_peak_rim_clearance_cm": round(peak_rim_dive * 100.0, 2),
        "stair_200mm_mounted_and_parked": bool(landed_step and stop_step),
        "final_x_m": round(float(d.qpos[0]), 4),
        "final_z_m": round(float(d.qpos[2]), 4),
        "final_vx_m_s": round(float(d.qvel[0]), 4),
    }


def build_and_verify_unified_moe(stair_ckpt_path: Path, jump_ckpt_path: Path, out_ckpt_path: Path) -> dict:
    stair_rc = _load_module("stair_rc", STAIR_RL_DIR / "support/mod4v3_ppo_v1/route2_common.py")
    jump_mod = _load_module("jump_mod", FORWARD_LEAP_DIR / "moe_forward_leap_model.py")

    c874 = torch.load(C874_PATH, map_location="cpu", weights_only=False)
    stair_ck = torch.load(stair_ckpt_path, map_location="cpu", weights_only=False)
    jump_ck = torch.load(jump_ckpt_path, map_location="cpu", weights_only=False)

    unified = UnifiedThreeExpertMoE(stair_rc, jump_mod)
    e0_sd = {k.removeprefix("mlp."): v.clone() for k, v in c874["actor_state_dict"].items() if k.startswith("mlp.")}
    unified.e0.load_state_dict(e0_sd, strict=True)
    e1_sd = {k.removeprefix("mlp.e1."): v.clone() for k, v in stair_ck["actor_state_dict"].items() if k.startswith("mlp.e1.")}
    unified.e1_stair.load_state_dict(e1_sd, strict=True)
    j_state = jump_ck["state_dict"]
    e2_sd = {k.removeprefix("actor_body.e_jump."): v.clone() for k, v in j_state.items() if k.startswith("actor_body.e_jump.")}
    unified.e2_jump.load_state_dict(e2_sd, strict=True)
    unified.eval()

    torch.manual_seed(20261118)
    obs_test = torch.randn(64, 35)
    hist_test = torch.randn(64, 420)

    obs_e0 = obs_test.clone()
    obs_e0[:, 28:35] = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    obs_e1 = obs_test.clone()
    obs_e1[:, 28:35] = torch.tensor([0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    obs_e2 = obs_test.clone()
    obs_e2[:, 28:35] = torch.tensor([1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])

    ref_stair = stair_rc.LocalRoute2Actor().load_checkpoint(stair_ck).eval()
    ref_jump = jump_mod.MoEForwardLeapActorCritic()
    ref_jump.load_state_dict(j_state, strict=True)
    ref_jump.eval()

    err_e0 = float((unified.forward_with_history(obs_e0, hist_test) - ref_stair(obs_e0, hist_test).clamp(-6, 6)).abs().max())
    err_e1 = float((unified.forward_with_history(obs_e1, hist_test) - ref_stair(obs_e1, hist_test).clamp(-6, 6)).abs().max())
    err_e2 = float((unified.forward_with_history(obs_e2, hist_test) - ref_jump.act_deterministic(obs_e2, hist_test)).abs().max())
    assert err_e0 == 0.0 and err_e1 == 0.0 and err_e2 == 0.0, (err_e0, err_e1, err_e2)

    showcase = render_unified_course_video(unified, RECIPES_DIR / "media/UNIFIED_ALL_SKILLS_COURSE_1X.mp4")

    out_ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": "MOD4V3_UNIFIED_3EXPERT_MOE_V2_FORWARD_LEAP",
        "c874_sha256": hashlib.sha256(C874_PATH.read_bytes()).hexdigest(),
        "stair_source": str(stair_ckpt_path),
        "stair_sha256": hashlib.sha256(stair_ckpt_path.read_bytes()).hexdigest(),
        "jump_source": str(jump_ckpt_path),
        "jump_sha256": hashlib.sha256(jump_ckpt_path.read_bytes()).hexdigest(),
        "zero_interference_max_abs_error": {"E0": err_e0, "E1_stair": err_e1, "E2_forward_leap": err_e2},
        "course_showcase": showcase,
        "state_dict": unified.state_dict(),
    }
    torch.save(payload, out_ckpt_path)
    u_sha = hashlib.sha256(out_ckpt_path.read_bytes()).hexdigest()
    return {
        "unified_checkpoint": str(out_ckpt_path),
        "unified_sha256": u_sha,
        "c874_sha256": payload["c874_sha256"],
        "stair_sha256": payload["stair_sha256"],
        "jump_sha256": payload["jump_sha256"],
        "zero_interference_verified": True,
        "max_abs_errors": payload["zero_interference_max_abs_error"],
        "course_showcase": showcase,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stair-ckpt", type=Path, default=STAIR_RL_DIR / "weights/model_rl_stair_best.pt")
    p.add_argument("--jump-ckpt", type=Path, default=FORWARD_LEAP_DIR / "weights/model_rl_forward_leap_best.pt")
    p.add_argument("--out", type=Path, default=RECIPES_DIR / "weights/model_unified_3expert_moe.pt")
    args = p.parse_args()
    info = build_and_verify_unified_moe(args.stair_ckpt, args.jump_ckpt, args.out)
    (RECIPES_DIR / "UNIFIED_MOE_VERIFICATION.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
