"""Unified 3-Expert Interactive Playground (`E0` Cruise + `E1` Stair Climb/Park + `E2` COD Forward Leap / Jump-Onto-Step).

Controls:
- W / S : Forward / Backward velocity command
- A / D : Yaw turn command
- SPACE : Trigger COD Forward Dolphin-Dive / Jump-Onto-Step (`E2`, `obs[30]=1` for 1.60s)
- E     : Toggle Smooth Wheel-Leg Stair-Climb Mode (`E1`, `obs[29]=1, obs[33]=1`)
- P     : Toggle Low-Posture Top Park (`v=0, h=0.20m`)
- R     : Reset at X = 0.0 m
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import mujoco as mj
import mujoco.viewer
import numpy as np
import torch

RECIPES_DIR = Path(__file__).resolve().parents[1]
REPO = RECIPES_DIR.parents[2]
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


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    umod = _load_mod("unified_moe", RECIPES_DIR / "scripts/unified_all_skills_moe.py")
    stair_rc = _load_mod("stair_rc", STAIR_RL_DIR / "support/mod4v3_ppo_v1/route2_common.py")
    jump_mod = _load_mod("jump_mod", FORWARD_LEAP_DIR / "moe_forward_leap_model.py")

    unified = umod.UnifiedThreeExpertMoE(stair_rc, jump_mod)
    ck = torch.load(RECIPES_DIR / "weights/model_unified_3expert_moe.pt", map_location="cpu", weights_only=False)
    unified.load_state_dict(ck["state_dict"], strict=True)
    unified.eval()

    original = PLANT / "mjcf/scene.xml"
    tree = ET.parse(original)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(original.parent / "assets"))
    wb = root.find("worldbody")
    ET.SubElement(wb, "geom", name="step1_20cm", type="box", pos="2.80 0 0.10", size="1.0 1.2 0.10", contype="1", conaffinity="2", friction=".9 .005 .0001", rgba="0.28 0.36 0.46 1.0")
    ET.SubElement(wb, "geom", name="step2_40cm", type="box", pos="4.60 0 0.20", size="0.9 1.2 0.20", contype="1", conaffinity="2", friction=".9 .005 .0001", rgba="0.34 0.44 0.54 1.0")
    tmp_dir = Path(tempfile.mkdtemp(prefix="mod4v3_unified_play_"))
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
    init_len = 0.25 - 0.0625
    fit_q = ik.fit(np.sqrt(init_len ** 2 + ik.lateral_offset ** 2), 0.0)["qpos"]

    qa = np.array([m.jnt_qposadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
    va = np.array([m.jnt_dofadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
    baseline = np.r_[env.default_q[env.leg_ids].numpy(), [0.0, 0.0]][PPO_TO_NATIVE]

    st = {"v": 0.0, "wz": 0.0, "stair": False, "park": False, "jump_rem": 0, "reset": True}

    def on_key(keycode: int):
        if keycode == 32:  # SPACE
            st["jump_rem"] = 95
            st["stair"] = False
        ch = chr(keycode).upper() if 32 < keycode < 127 else ""
        if ch == "W":
            st["v"] = min(1.0, st["v"] + 0.25)
        elif ch == "S":
            st["v"] = max(-0.4, st["v"] - 0.25)
        elif ch == "A":
            st["wz"] = 0.6
        elif ch == "D":
            st["wz"] = -0.6
        elif ch == "E":
            st["stair"] = not st["stair"]
            st["park"] = False
        elif ch == "P":
            st["park"] = not st["park"]
            if st["park"]:
                st["v"] = 0.0
        elif ch == "R":
            st["reset"] = True

    prev_a = np.zeros(6, np.float32)
    with mujoco.viewer.launch_passive(m, d, key_callback=on_key) as viewer:
        viewer.cam.azimuth = 95.0
        viewer.cam.elevation = -15.0
        viewer.cam.distance = 2.4
        while viewer.is_running():
            t0 = time.perf_counter()
            if st["reset"]:
                st["reset"] = False
                st["v"] = 0.0
                st["wz"] = 0.0
                st["jump_rem"] = 0
                mj.mj_resetData(m, d)
                d.qpos[:] = fit_q
                d.qpos[:3] = [0.0, 0.0, 0.251]
                d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
                d.qvel[:] = 0.0
                mj.mj_forward(m, d)
                unified.reset_history()
                prev_a[:] = 0.0

            if st["jump_rem"] > 0:
                st["jump_rem"] -= 1
                mode = [1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
                h_cmd = 0.28
                v_c = max(0.0, st["v"])
            elif st["stair"]:
                mode = [0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                h_cmd = 0.20 if st["park"] else 0.4091
                v_c = 0.0 if st["park"] else 0.47
            else:
                mode = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                h_cmd = 0.20 if st["park"] else 0.28
                v_c = st["v"]

            rot = d.xmat[env.base_id].reshape(3, 3)
            q = d.qpos[qa] - baseline
            q[4:] = 0.0
            obs = np.r_[[v_c, 0.0, st["wz"], h_cmd * 5.0], d.qvel[3:6] * 0.5, rot.T @ np.array([0.0, 0.0, -1.0]), q, d.qvel[va] * 0.1, prev_a, mode].astype(np.float32)
            st["wz"] *= 0.85
            a = unified(torch.from_numpy(obs).reshape(1, 35))[0].numpy()
            a_t = torch.from_numpy(a[PPO_TO_NATIVE]).reshape(1, 6)
            for j in range(8):
                tau = env._torque(a_t).numpy().reshape(-1)
                if j % 4 == 0:
                    d.ctrl[env.act_ids[:4]] = tau[:4]
                d.ctrl[env.act_ids[4:]] = tau[4:]
                mj.mj_step(m, d)
            prev_a = a
            viewer.cam.lookat[:] = [float(d.qpos[0]) + 0.2, float(d.qpos[1]), float(d.qpos[2])]
            viewer.sync()
            dt = 0.02 - (time.perf_counter() - t0)
            if dt > 0:
                time.sleep(dt)


if __name__ == "__main__":
    main()
