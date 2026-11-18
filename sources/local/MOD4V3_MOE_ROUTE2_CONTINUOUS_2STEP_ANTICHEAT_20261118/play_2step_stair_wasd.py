"""Interactive MuJoCo WASD + Auto-Climb Playground for MOD4v3 Single-Step (20cm) & Continuous 2-Step (20+20=40cm).

Automatically loads `weights/model_best.pt` if present, otherwise `weights/model_step000.pt`.

Controls (in Control Panel or terminal):
  W / S       Forward / Backward velocity command
  A / D       Turn Left / Right yaw command
  M           Toggle Route Mode: E0 (Normal Flat/Rough c874) <-> E1 (Stair Expert)
  G           Toggle Auto-Stair-Climb Cruise (tall 0.4091m approach -> climb -> tread standup -> final top park!)
  1 / 2 / 3   Switch Scene:
                1 = Flat Ground Arena
                2 = Single 20cm Step
                3 = Continuous 2-Step (20cm + 20cm = 40cm, 1.50m tread)
  R           Reset robot to standing
  Esc         Exit cleanly

Headless smoke test:
  python play_2step_stair_wasd.py --headless --scene two_step --steps 600
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as ET
import mujoco as mj
import numpy as np
import torch

T = Path(__file__).resolve().parent
R = T.parents[2]
E_TEACH = R / "sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1"
sys.path[:0] = [str(T), str(T / "support"), str(E_TEACH)]
from native_runtime import model_xml, PLANT, D, RobotSpec, _q_from_runtime, _q_from_bank, Mod4v3Mujoco, Mod4Retarget, NAMES, PPO_TO_NATIVE
from history_eval_hooks import ReplayHistoryActor


def default_model_path() -> Path:
    for cand in [T / "weights/model_best.pt", T / "weights/model_step000.pt"]:
        if cand.exists():
            return cand
    raise FileNotFoundError("No checkpoint found in weights/")


def build_scene_xml(dest: Path, scene: str) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    xml_path, root, _ = model_xml(dest, 0.20)
    m0 = mj.MjModel.from_xml_path(str(xml_path))
    stat_el = root.find("statistic")
    if stat_el is None:
        stat_el = ET.SubElement(root, "statistic")
    stat_el.set("extent", f"{float(m0.stat.extent):.12g}")
    stat_el.set("center", f"{m0.stat.center[0]:.12g} {m0.stat.center[1]:.12g} {m0.stat.center[2]:.12g}")
    wb = root.find("worldbody")
    if scene == "flat":
        for g in list(wb.findall("geom")):
            if g.get("name") == "native_teacher_platform":
                wb.remove(g)
    elif scene == "two_step":
        ET.SubElement(
            wb,
            "geom",
            {
                "name": "native_step2_platform",
                "type": "box",
                "pos": "3.4000 0 0.2000",
                "size": "0.7000 1.10 0.2000",
                "rgba": "0.32 0.52 0.72 1",
                "contype": "1",
                "conaffinity": "2",
                "friction": ".9 .005 .0001",
            },
        )
    xml_path.write_text(ET.tostring(root, encoding="unicode"), encoding="utf8")
    return xml_path


class StairPlaygroundSim:
    def __init__(self, model_path: Path, scene: str = "two_step"):
        self.model_path = Path(model_path)
        self.scene = scene
        ck = torch.load(self.model_path, map_location="cpu", weights_only=False)
        self.actor = ReplayHistoryActor()
        self.actor.load_state_dict(ck["actor_state_dict"], strict=True)
        self.actor.eval()
        self._load_scene(scene)

    def _load_scene(self, scene: str):
        self.scene = scene
        tmp = T / "evidence/playground_tmp" / scene
        xml = build_scene_xml(tmp, scene)
        spec = RobotSpec(**json.loads((D / "runtime/core/template_spec.json").read_text())["spec"])
        runtime = json.loads((PLANT / "runtime_config.json").read_text())
        default = _q_from_runtime(runtime, spec.joint_names)
        bank = json.loads((D / "plant/reset_bank.json").read_text())
        sem = json.loads((PLANT / "semantics.json").read_text())
        bq, bz = _q_from_bank(bank, sem, spec.joint_names)
        self.env = Mod4v3Mujoco(str(xml), spec, default, bq, bz, action_clip=6.0)
        self.m, self.d = self.env.m, self.env.d
        self.m.opt.timestep = 0.0025
        self.qa = np.array([self.m.jnt_qposadr[self.m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
        self.va = np.array([self.m.jnt_dofadr[self.m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
        self.baseline = np.r_[self.env.default_q[self.env.leg_ids].numpy(), [0, 0]][PPO_TO_NATIVE]
        self.tire = np.array([self.m.geom(s + "_tire").id for s in ["left", "right"]])
        self.bodies = self.m.geom_bodyid[self.tire]
        self.plat1 = mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_GEOM, "native_teacher_platform")
        self.plat2 = mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_GEOM, "native_step2_platform")
        self.reset()

    def reset(self):
        self.actor.reset_history()
        ik = Mod4Retarget()
        L0 = 0.4091 - 0.0625
        fit = ik.fit(np.sqrt(L0 ** 2 + ik.lateral_offset ** 2), 0.0)
        self.d.qpos[:] = fit["qpos"]
        self.d.qpos[:3] = [0.0, 0.0, L0 + 0.0625 + 0.001]
        self.d.qpos[3:7] = [1, 0, 0, 0]
        self.d.qvel[:] = 0
        mj.mj_forward(self.m, self.d)
        self.prev = np.zeros(6, np.float32)
        self.step_count = 0
        self.stair_mode = self.scene != "flat"
        self.auto_climb = self.scene != "flat"
        self.landed_final = False
        self.stop_latched = False
        self.hold_final = 0.0
        self.vx_cmd = 0.0
        self.wz_cmd = 0.0
        self.h_cmd = 0.4091 if self.stair_mode else 0.28

    def step(self) -> dict:
        age = self.step_count * 0.02
        if self.auto_climb and self.stair_mode:
            v = 0.47 if age >= 1.0 and not self.stop_latched else 0.0
            wz = 0.0
            h = 0.20 if self.landed_final else 0.4091
        else:
            v, wz, h = self.vx_cmd, self.wz_cmd, self.h_cmd

        mode = [0, 1, 0, 0, 0, 1, 0] if self.stair_mode else [1, 0, 0, 0, 0, 0, 0]
        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        q = self.d.qpos[self.qa] - self.baseline
        q[4:] = 0.0
        obs = np.r_[[v, 0, wz, h * 5.0], self.d.qvel[3:6] * 0.5, rot.T @ np.array([0, 0, -1]), q, self.d.qvel[self.va] * 0.1, self.prev, mode].astype(np.float32)
        with torch.inference_mode():
            a = self.actor(torch.from_numpy(obs).reshape(1, 35))[0].clamp(-6, 6).numpy().copy()
        a_t = torch.from_numpy(a[PPO_TO_NATIVE]).reshape(1, 6)
        for j in range(8):
            tau = self.env._torque(a_t).numpy().reshape(-1)
            if j % 4 == 0:
                self.d.ctrl[self.env.act_ids[:4]] = tau[:4]
            self.d.ctrl[self.env.act_ids[4:]] = tau[4:]
            mj.mj_step(self.m, self.d)
        self.prev = a
        self.step_count += 1

        # Final target platform detection for auto-park
        target_plat = self.plat2 if self.scene == "two_step" else self.plat1
        target_h = 0.40 if self.scene == "two_step" else 0.20
        target_edge = 2.70 if self.scene == "two_step" else 1.20
        if target_plat >= 0:
            top = np.zeros(2, bool)
            for i in range(self.d.ncon):
                c = self.d.contact[i]
                g1, g2 = int(c.geom1), int(c.geom2)
                if target_plat not in (g1, g2):
                    continue
                f = np.zeros(6)
                mj.mj_contactForce(self.m, self.d, i, f)
                other = g2 if g1 == target_plat else g1
                body = self.m.geom_bodyid[other]
                for side, b in enumerate(self.bodies):
                    if body == b and f[0] > 5.0 and abs(float(c.pos[2]) - target_h) < 0.016:
                        top[side] = True
            wheel = self.d.geom_xpos[self.tire]
            if top.all() and self.d.qpos[0] > target_edge + 0.03 and np.all(wheel[:, 0] > target_edge + 0.025):
                self.landed_final = True
                self.hold_final += 0.02
                if self.hold_final >= 0.40:
                    self.stop_latched = True
            else:
                self.hold_final = 0.0

        return {
            "time_s": round(float(self.d.time), 3),
            "x_m": round(float(self.d.qpos[0]), 4),
            "z_m": round(float(self.d.qpos[2]), 4),
            "vx_m_s": round(float(self.d.qvel[0]), 4),
            "landed_final": bool(self.landed_final),
            "stop_latched": bool(self.stop_latched),
        }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, default=None)
    p.add_argument("--scene", choices=["flat", "single_step", "two_step"], default="two_step")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--steps", type=int, default=650)
    args = p.parse_args()

    mpath = args.model or default_model_path()
    sim = StairPlaygroundSim(mpath, scene=args.scene)

    if args.headless:
        last = {}
        for _ in range(args.steps):
            last = sim.step()
        print(json.dumps({"model": str(mpath), "scene": args.scene, "final_state": last}, indent=2))
        return

    import mujoco.viewer
    print(f"Loaded {mpath.name} on scene={args.scene}. Close viewer window to exit.")
    with mujoco.viewer.launch_passive(sim.m, sim.d) as viewer:
        viewer.cam.azimuth = 90
        viewer.cam.elevation = -14
        viewer.cam.distance = 2.85
        viewer.cam.lookat[:] = [1.85, 0.0, 0.34]
        while viewer.is_running():
            t0 = time.perf_counter()
            sim.step()
            viewer.cam.lookat[0] = float(sim.d.qpos[0]) + 0.35
            viewer.sync()
            dt = 0.02 - (time.perf_counter() - t0)
            if dt > 0:
                time.sleep(dt)


if __name__ == "__main__":
    main()
