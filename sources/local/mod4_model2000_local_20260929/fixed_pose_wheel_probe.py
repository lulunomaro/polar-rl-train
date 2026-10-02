"""Open-loop fixed leg targets / fixed wheel speed plant sweep for MATLAB audit."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import sys

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from probe_model2000_mujoco import contact_load  # noqa: E402
sys.path.insert(0, str(ROOT / "mod4-onnx-mujoco-launcher"))
from sim_runtime import Mod4Sim, RuntimeConfig  # noqa: E402
sys.path.insert(0, str(ROOT / "chassis_mod4"))
from kinematics import leg_configuration  # noqa: E402


def main():
    contract = json.loads((HERE / "contract_rm2025_later.json").read_text(encoding="utf-8"))
    geometry = json.loads((ROOT / "matlab_mod4_wbr_20260917" / "mod4_extracted_parameters.json").read_text(encoding="utf-8"))
    cfg = RuntimeConfig(leg_kp=contract["leg_kp"], leg_kd=contract["leg_kd"], wheel_kd=contract["wheel_kd"],
                        crank_scale=.5, hip_scale=.5, wheel_scale=10.0)
    sim = Mod4Sim(ROOT / "mod4-onnx-mujoco-launcher" / "model" / "rm_training_arena_headless.xml",
                  HERE / "model_2000.onnx", cfg)
    floor = mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_GEOM, "arena_floor")
    tires = [mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_GEOM, n) for n in ("left_tire", "right_tire")]
    guides = {mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_GEOM, f"guide_roller_collision_{i}") for i in range(8)}
    chassis = {i for i in range(sim.model.ngeom) if mujoco.mj_id2name(sim.model, mujoco.mjtObj.mjOBJ_GEOM, i).startswith("chassis_")}
    wheel_radius = float(contract["wheel_radius"])
    mass = float(sim.model.body_mass.sum())
    rows = []
    # A fixed-wheel-speed robot has no pitch feedback and falls like an inverted
    # pendulum.  Apply a *pure chassis moment* to isolate tire traction from that
    # separate balancing task; the moment is reported and is not a robot motor.
    pitch_kp, pitch_kd, pitch_moment_limit = 100.0, 20.0, 30.0
    for pose_idx in (0, 4, 8, 12, 16, 20, 23):
        pose = geometry["poses"][pose_idx]
        sim.reset(x=-8.0)
        sim.data.qpos[2] = pose["root_height_m"]
        # Initialize every passive link from the closed-chain inverse geometry.
        # Setting only the four motor coordinates makes the equality solver
        # start from a broken linkage and can eject the robot on the first step.
        for side in ("left", "right"):
            values, _ = leg_configuration(pose["hip_rad"], pose["difference_rad"], side)
            for short_name, q in values.items():
                name = f"{side}_{short_name}"
                j = mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_JOINT, name)
                sim.data.qpos[sim.model.jnt_qposadr[j]] = float(q)
        mujoco.mj_forward(sim.model, sim.data)
        if sim.closure_error() > 1e-4:
            raise RuntimeError(f"pose {pose_idx} does not close: {sim.closure_error():g} m")
        legs = np.array([pose["crank_rad"], pose["hip_rad"], pose["crank_rad"], pose["hip_rad"]]) / .5
        for phase, wheel_target, seconds in (("settle", 0.0, 2.0), ("drive", 8.0, 3.0)):
            action = np.concatenate([legs, [wheel_target / 10.0] * 2])
            samples = []
            for tick in range(round(seconds * cfg.policy_hz)):
                old_x = float(sim.data.qpos[0])
                sim.last_action[:] = action
                for _ in range(sim.decimation):
                    R = sim.data.xmat[sim.chassis_id].reshape(3, 3)
                    pitch_rad = math.atan2(-R[2, 0], R[2, 2])
                    pitch_rate = float(sim.data.sensor("base_gyro").data[1])
                    stabilizer_moment = float(np.clip(-pitch_kp * pitch_rad - pitch_kd * pitch_rate,
                                                      -pitch_moment_limit, pitch_moment_limit))
                    sim.data.xfrc_applied[sim.chassis_id, 3:6] = (0.0, stabilizer_moment, 0.0)
                    sim.data.ctrl[:] = sim.action_to_torque(action)
                    mujoco.mj_step(sim.model, sim.data)
                v = (float(sim.data.qpos[0]) - old_x) * cfg.policy_hz
                qd = np.array([sim.data.qvel[sim.qvel[n]] for n in ("left_wheel_spin", "right_wheel_spin")])
                load = [contact_load(sim, floor, {gid}) for gid in tires]
                gas = []
                for n in ("left_gas_slide", "right_gas_slide"):
                    j = mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_JOINT, n)
                    gas.append(float(sim.data.qfrc_spring[sim.model.jnt_dofadr[j]]))
                R = sim.data.xmat[sim.chassis_id].reshape(3, 3)
                qleg = np.array([sim.data.qpos[sim.qpos[n]] for n in ("left_crank", "left_hip", "right_crank", "right_hip")])
                samples.append({
                    "root_z_m": float(sim.data.qpos[2]), "vx_m_s": v,
                    "wheel_speed_mean_rad_s": float(np.mean(qd)),
                    "wheel_peripheral_m_s": float(np.mean(qd) * wheel_radius),
                    "left_wheel_normal_n": load[0], "right_wheel_normal_n": load[1],
                    "guide_normal_n": contact_load(sim, floor, guides),
                    "chassis_normal_n": contact_load(sim, floor, chassis),
                    "pitch_deg": math.degrees(math.atan2(-R[2, 0], R[2, 2])),
                    "gas_force_mean_n": float(np.mean(gas)),
                    "wheel_torque_mean_nm": float(np.mean([sim.data.ctrl[sim.actuator[n]] for n in ("left_wheel_spin_motor", "right_wheel_spin_motor")])),
                    "leg_torque_max_abs_nm": float(np.max(np.abs([sim.data.ctrl[sim.actuator[n]] for n in ("left_crank_motor", "left_hip_motor", "right_crank_motor", "right_hip_motor")]))),
                    "leg_target_error_rms_rad": float(np.sqrt(np.mean((qleg - np.array([pose["crank_rad"], pose["hip_rad"], pose["crank_rad"], pose["hip_rad"]]))**2))),
                    "external_pitch_stabilizer_nm": stabilizer_moment,
                    "closure_m": sim.closure_error(),
                })
            # Last one second of each phase, after the command transient.
            stable = samples[-round(cfg.policy_hz):]
            result = {"pose_idx": pose_idx, "phase": phase,
                      "geometric_height_m": pose["root_height_m"],
                      "hip_target_rad": pose["hip_rad"], "crank_target_rad": pose["crank_rad"],
                      "wheel_target_rad_s": wheel_target, "mass_kg": mass}
            result.update({key: float(np.mean([s[key] for s in stable])) for key in stable[0]})
            result["both_wheels_loaded_fraction"] = float(np.mean([s["left_wheel_normal_n"] > 1 and s["right_wheel_normal_n"] > 1 for s in stable]))
            result["slip_ratio"] = max(0.0, (result["wheel_peripheral_m_s"] - result["vx_m_s"]) / max(abs(result["wheel_peripheral_m_s"]), .1)) if phase == "drive" else 0.0
            rows.append(result)
            print(pose_idx, phase, "z", round(result["root_z_m"], 3), "v", round(result["vx_m_s"], 3),
                  "wheelN", round(result["left_wheel_normal_n"] + result["right_wheel_normal_n"], 1),
                  "guideN", round(result["guide_normal_n"], 1), "slip", round(result["slip_ratio"], 3), flush=True)
    out = HERE / "fixed_pose_wheel_probe.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(out)


if __name__ == "__main__":
    main()
