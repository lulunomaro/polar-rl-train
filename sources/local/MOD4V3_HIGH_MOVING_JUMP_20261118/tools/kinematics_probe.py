"""Read-only kinematics and plant probe for MOD4v3 HW300N60_R3 + c874."""
from __future__ import annotations

import hashlib
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

EXPECTED_XML_SHA = "77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f"
EXPECTED_CKPT_SHA = "c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617"

sys.path.insert(0, str(OLD_DELIVERY / "runtime/core"))
from play_mod4v3 import Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime  # noqa: E402
from play_ppo_flatv1 import ActorMLP, _map  # noqa: E402


def main():
    xml_sha = hashlib.sha256(XML_PATH.read_bytes()).hexdigest()
    ckpt_sha = hashlib.sha256(CKPT_PATH.read_bytes()).hexdigest()
    assert xml_sha == EXPECTED_XML_SHA, f"XML SHA mismatch: {xml_sha}"
    assert ckpt_sha == EXPECTED_CKPT_SHA, f"CKPT SHA mismatch: {ckpt_sha}"

    import imageio
    import PIL
    print(f"Packages OK: mujoco={mujoco.__version__}, torch={torch.__version__}, imageio={imageio.__version__}, PIL={PIL.__version__}")

    ck = torch.load(CKPT_PATH, map_location="cpu", weights_only=False)
    template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    spec = RobotSpec(**template["spec"])
    runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    semantics = json.loads(SEMANTICS_PATH.read_text(encoding="utf-8"))
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    default_q = _q_from_runtime(runtime, spec.joint_names)
    bank_q, bank_z = _q_from_bank(bank, semantics, spec.joint_names)

    print("spec.joint_names:", spec.joint_names)
    print("default_q:", {n: round(float(v), 5) for n, v in zip(spec.joint_names, default_q)})
    print("bank_z:", bank_z, "bank_q:", {n: round(float(v), 5) for n, v in zip(spec.joint_names, bank_q)})

    # Check all poses in reset_bank!
    poses = bank.get("poses", [])
    print(f"Reset bank has {len(poses)} poses; root_height_m range: "
          f"{min(p['root_height_m'] for p in poses):.4f} .. {max(p['root_height_m'] for p in poses):.4f}")
    rows = semantics["coordinates"]["native_from_v2"]
    for target_h in [0.18, 0.20, 0.22, 0.26, 0.30, 0.36, 0.40, 0.44]:
        p = min(poses, key=lambda x: abs(float(x["root_height_m"]) - target_h))
        native = {n: float(p["joint_pos"].get(row["source"], 0.0)) + float(row["offset_si"])
                  for n, row in rows.items()}
        lf, lr = native["left_front1_joint"], native["left_rear1_joint"]
        delta = lf - lr
        mean = 0.5 * (lf + lr)
        sp2 = native.get("left_spring2_joint", 0.0)
        print(f"  bank h={p['root_height_m']:.4f}m: LF={lf:+.4f}, LR={lr:+.4f}, delta={delta:.4f}, mean={mean:+.4f}, spring2={sp2:+.4f}")

    env = Mod4v3Mujoco(str(XML_PATH), spec, default_q, bank_q, bank_z, device="cpu", action_clip=6.0)
    m, d = env.m, env.d
    total_mass = float(m.body_mass.sum())
    print(f"Total robot mass: {total_mass:.4f} kg")

    # Check chassis & guide wheel clearance vs root height when pitch=0
    base_id = env.base_id
    guides = [i for i in range(m.ngeom) if m.geom(i).name.startswith("guide_wheel_")]
    chassis_geoms = [i for i in range(m.ngeom) if m.geom_bodyid[i] == base_id and m.geom_contype[i] != 0]
    d.qpos[:3] = [0.0, 0.0, 0.30]
    d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
    mujoco.mj_forward(m, d)
    print("At root z = 0.300m, pitch=0:")
    for gid in chassis_geoms + guides:
        gname = m.geom(gid).name
        pos = d.geom_xpos[gid]
        sz = m.geom_size[gid]
        gtype = m.geom_type[gid]
        # cylinder for guide wheels rotated by 90 deg around x -> radius is sz[0]=0.015
        bottom = pos[2] - (sz[0] if "guide" in gname else sz[2])
        print(f"  geom {gname:20s}: center_z={pos[2]:.4f}, bottom_z={bottom:.4f} (offset from root_z: {bottom - 0.30:.4f}m)")


if __name__ == "__main__":
    main()
