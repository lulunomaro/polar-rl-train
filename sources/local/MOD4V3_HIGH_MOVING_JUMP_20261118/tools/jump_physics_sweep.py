"""Explore 4-bar kinematics (delta -> neutral mean & leg length) and high-jump physics on MOD4v3 + c874."""
from __future__ import annotations

import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
TASK_DIR = HERE.parent
REPO = TASK_DIR.parents[2]

OLD_DELIVERY = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
LOW_PITCH_DELIVERY = REPO / "deliveries/MOD4V3_LOW_PITCH_20261116"

XML_PATH = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/mjcf/scene.xml"
RUNTIME_PATH = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/runtime_config.json"
SEMANTICS_PATH = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/semantics.json"
BANK_PATH = OLD_DELIVERY / "plant/reset_bank.json"
TEMPLATE_PATH = OLD_DELIVERY / "runtime/core/template_spec.json"
CKPT_PATH = LOW_PITCH_DELIVERY / "model_full_ppo.pt"

sys.path.insert(0, str(OLD_DELIVERY / "runtime/core"))
from play_mod4v3 import LEG_DELTA_BOUNDS, Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime  # noqa: E402
from play_ppo_flatv1 import ActorMLP, _map  # noqa: E402


def build_env():
    ck = torch.load(CKPT_PATH, map_location="cpu", weights_only=False)
    template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    spec = RobotSpec(**template["spec"])
    runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    semantics = json.loads(SEMANTICS_PATH.read_text(encoding="utf-8"))
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    default_q = _q_from_runtime(runtime, spec.joint_names)
    bank_q, bank_z = _q_from_bank(bank, semantics, spec.joint_names)
    actor = ActorMLP()
    actor.load_state_dict(ck["actor_state_dict"], strict=False)
    actor.eval()
    env = Mod4v3Mujoco(str(XML_PATH), spec, default_q, bank_q, bank_z, device="cpu", action_clip=6.0)
    return env, actor, spec, default_q


def map_4bar_kinematics():
    """Hold base_link fixed in air and sweep delta & mean by letting MuJoCo relax the 4-bar loop."""
    env, _, spec, default_q = build_env()
    m, d = env.m, env.d
    # Freeze base in air at z=0.80 so wheels don't touch ground
    wheel_ids = [m.body("left_wheel_link").id, m.body("right_wheel_link").id]
    pairs = [(m.site(e.get("site1")).id, m.site(e.get("site2")).id)
             for e in ET.parse(XML_PATH).getroot().findall("equality/connect")]
    sp_qadr = m.joint("left_spring2_joint").qposadr[0]

    print("=== 4-Bar Neutral Mean Lookup (wheel_x == com_x at pitch=0) ===")
    table = []
    for delta in np.linspace(0.18, 1.75, 18):
        best_mean = 0.2
        # Quick Newton/secant search on mean so wheel_x == subtree_com_x
        for mean_try in np.linspace(-0.25, 0.55, 17):
            env.reset()
            for step in range(40):
                d.qpos[:3] = [0.0, 0.0, 0.80]
                d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
                d.qvel[:6] = 0.0
                # Apply strong PD to reach (mean_try, delta)
                lf_t = mean_try + 0.5 * delta
                lr_t = mean_try - 0.5 * delta
                a_env = torch.zeros(1, 6)
                a_env[0, 0] = 2.0 * (lf_t - float(default_q[env.leg_ids[0]]))
                a_env[0, 1] = 2.0 * (lf_t - float(default_q[env.leg_ids[1]]))
                a_env[0, 2] = 2.0 * (lr_t - float(default_q[env.leg_ids[2]]))
                a_env[0, 3] = 2.0 * (lr_t - float(default_q[env.leg_ids[3]]))
                d.ctrl[env.act_ids] = env._torque(a_env).detach().numpy().ravel()
                mujoco.mj_step(m, d)
            wx = float(d.xpos[wheel_ids[0], 0])
            cx = float(d.subtree_com[env.base_id, 0])
            if abs(wx - cx) < abs(best_mean - 999):
                pass
        # Refine with bisection
        lo, hi = -0.30, 0.60
        for _ in range(14):
            mid = 0.5 * (lo + hi)
            env.reset()
            for _s in range(60):
                d.qpos[:3] = [0.0, 0.0, 0.80]
                d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
                d.qvel[:6] = 0.0
                lf_t = mid + 0.5 * delta
                lr_t = mid - 0.5 * delta
                a_env = torch.zeros(1, 6)
                a_env[0, 0] = a_env[0, 1] = 2.0 * (lf_t - float(default_q[env.leg_ids[0]]))
                a_env[0, 2] = a_env[0, 3] = 2.0 * (lr_t - float(default_q[env.leg_ids[2]]))
                d.ctrl[env.act_ids] = env._torque(a_env).detach().numpy().ravel()
                mujoco.mj_step(m, d)
            wx = float(d.xpos[wheel_ids[0], 0])
            cx = float(d.subtree_com[env.base_id, 0])
            # Check sign: increasing mean rotates both front & rear positive (+y axis rotation: x -> -z or +z?)
            if wx > cx:
                lo = mid
            else:
                hi = mid
        # Check direction first!
        wx_z = float(d.xpos[wheel_ids[0], 2])
        stand_root_z = 0.80 - (wx_z - 0.0625)
        cl = max(float(np.linalg.norm(d.site_xpos[u] - d.site_xpos[v])) for u, v in pairs)
        sp_f = 2000.0 * (0.17063944 - float(d.qpos[sp_qadr]))
        q_lf = float(d.qpos[env.qadr_all[env.leg_ids[0]]])
        q_lr = float(d.qpos[env.qadr_all[env.leg_ids[2]]])
        table.append((delta, q_lf - q_lr, 0.5 * (q_lf + q_lr), wx - cx, stand_root_z, sp_f, cl * 1000))
        print(f"  cmd_delta={delta:.3f} -> actual_delta={q_lf-q_lr:.3f}, mean={0.5*(q_lf+q_lr):+.4f}, "
              f"wx-cx={wx-cx:+.4f}m, flat_root_z={stand_root_z:.4f}m, gasF={sp_f:.1f}N, closure={cl*1e3:.3f}mm")


if __name__ == "__main__":
    map_4bar_kinematics()
