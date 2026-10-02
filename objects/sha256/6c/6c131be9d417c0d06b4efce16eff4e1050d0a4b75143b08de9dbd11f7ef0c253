"""CPU-only deterministic MOD4 checkpoint probe; never connects to training host."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
LAUNCHER = HERE.parent / "mod4-onnx-mujoco-launcher"
sys.path.insert(0, str(LAUNCHER))
from sim_runtime import Mod4Sim, RuntimeConfig  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def contact_load(sim: Mod4Sim, floor_id: int, geom_ids: set[int]) -> float:
    load = 0.0
    force = np.zeros(6)
    for i in range(sim.data.ncon):
        c = sim.data.contact[i]
        if c.geom1 == floor_id and c.geom2 in geom_ids or c.geom2 == floor_id and c.geom1 in geom_ids:
            mujoco.mj_contactForce(sim.model, sim.data, i, force)
            load += max(0.0, float(force[0]))
    return load


def run(sim: Mod4Sim, name: str, commands: list[tuple[float, float]], duration_s: float) -> dict:
    sim.restore_nominal_parameters()
    sim.reset(x=-8.0)
    sim.command.auto_mode = False
    sim.command.mode = 0
    sim.command.height = 0.245
    floor = mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_GEOM, "arena_floor")
    wheels = {mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_GEOM, n) for n in ("left_tire", "right_tire")}
    guides = {mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_GEOM, f"guide_roller_collision_{i}") for i in range(8)}
    chassis = {i for i in range(sim.model.ngeom) if mujoco.mj_id2name(sim.model, mujoco.mjtObj.mjOBJ_GEOM, i).startswith("chassis_")}
    prev_action = np.zeros(6)
    prev_delta = np.zeros(6)
    prev_x = float(sim.base_position[0])
    rows = []
    error = None
    for step in range(round(duration_s * sim.cfg.policy_hz)):
        t = step / sim.cfg.policy_hz
        vx = next(v for end, v in commands if t < end)
        sim.command.vx = vx
        try:
            sim.step_control()
        except (FloatingPointError, mujoco.FatalError) as exc:
            error = f"{type(exc).__name__}: {exc}"
            break
        R = sim.data.xmat[sim.chassis_id].reshape(3, 3)
        tilt = math.degrees(math.acos(float(np.clip(R[2, 2], -1.0, 1.0))))
        pitch = math.degrees(math.atan2(-R[2, 0], R[2, 2]))
        x = float(sim.base_position[0])
        speed = (x - prev_x) * sim.cfg.policy_hz
        prev_x = x
        delta = sim.last_action - prev_action
        d2 = delta - prev_delta
        prev_action = sim.last_action.copy()
        prev_delta = delta
        left, right = (contact_load(sim, floor, {gid}) for gid in wheels)
        wheel_speed = float(np.mean([sim.data.qvel[sim.qvel[n]] for n in ("left_wheel_spin", "right_wheel_spin")]))
        row = {
            "time_s": round(float(sim.data.time), 3),
            "command_vx_m_s": vx,
            "actual_vx_m_s": speed,
            "wheel_action_mean": float(np.mean(sim.last_action[4:])),
            "wheel_speed_mean_rad_s": wheel_speed,
            "wheel_peripheral_m_s": wheel_speed * .0625,
            "base_x_m": x,
            "base_z_m": float(sim.base_position[2]),
            "tilt_deg": tilt,
            "pitch_deg": pitch,
            "left_wheel_load_n": left,
            "right_wheel_load_n": right,
            "guide_load_n": contact_load(sim, floor, guides),
            "chassis_load_n": contact_load(sim, floor, chassis),
            "action_delta_rms": float(np.sqrt(np.mean(delta**2))),
            "action_d2_rms": float(np.sqrt(np.mean(d2**2))),
            "closure_m": sim.closure_error(),
            "mimic_rad": sim.mimic_error(),
        }
        rows.append(row)
        if not np.isfinite(list(row.values())).all():
            error = "non-finite metric"
            break
    trace = HERE / f"probe_{name}.csv"
    with trace.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["time_s"])
        writer.writeheader()
        writer.writerows(rows)
    steady = [r for r in rows if r["time_s"] >= 2.0]
    def avg(key):
        return float(np.mean([r[key] for r in steady])) if steady else None
    summary = {
        "name": name,
        "steps_completed": len(rows),
        "seconds_completed": len(rows) / sim.cfg.policy_hz,
        "error": error,
        "duration_s": duration_s,
        "final_base_x_m": rows[-1]["base_x_m"] if rows else None,
        "final_base_z_m": rows[-1]["base_z_m"] if rows else None,
        "mean_speed_error_m_s": float(np.mean([abs(r["actual_vx_m_s"] - r["command_vx_m_s"]) for r in steady])) if steady else None,
        "mean_base_z_m": avg("base_z_m"),
        "min_base_z_m": min((r["base_z_m"] for r in rows), default=None),
        "mean_tilt_deg": avg("tilt_deg"),
        "max_tilt_deg": max((r["tilt_deg"] for r in rows), default=None),
        "mean_pitch_deg": avg("pitch_deg"),
        "both_wheels_loaded_fraction": float(np.mean([r["left_wheel_load_n"] > 1 and r["right_wheel_load_n"] > 1 for r in steady])) if steady else None,
        "mean_guide_load_n": avg("guide_load_n"),
        "mean_chassis_load_n": avg("chassis_load_n"),
        "mean_action_delta_rms": avg("action_delta_rms"),
        "mean_action_d2_rms": avg("action_d2_rms"),
        "max_closure_m": sim.max_closure_error,
        "max_mimic_rad": sim.max_mimic_error,
        "max_abs_torque_nm_actuator_order": sim.max_abs_torque.tolist(),
        "trace_csv": str(trace),
    }
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return summary


def main():
    contract = json.loads((HERE / "contract_rm2025_later.json").read_text(encoding="utf-8"))
    xml = LAUNCHER / "model" / "rm_training_arena_headless.xml"
    onnx = HERE / "model_2000.onnx"
    cfg = RuntimeConfig(
        leg_kp=contract["leg_kp"], leg_kd=contract["leg_kd"],
        wheel_kd=contract["wheel_kd"],
        crank_scale=contract["leg_action_scale"], hip_scale=contract["leg_action_scale"],
        wheel_scale=contract["wheel_action_scale"],
        leg_effort=contract["leg_effort"], leg_stall=contract["leg_voltage_line_intercept"],
        leg_no_load=contract["leg_no_load"], wheel_effort=contract["wheel_effort"],
        wheel_stall=contract["wheel_voltage_line_intercept"], wheel_no_load=contract["wheel_no_load"],
    )
    sim = Mod4Sim(xml, onnx, cfg)
    results = [
        run(sim, "flat_stand_5s", [(5.0, 0.0)], 5.0),
        run(sim, "flat_profile_15s", [(3, 0.0), (6, 0.3), (9, 0.6), (13, 1.0), (15, 0.0)], 15.0),
    ]
    report = {
        "scope": "local CPU MuJoCo sim-to-sim, not Isaac Lab replay or real-hardware certification",
        "checkpoint_sha256": sha256(HERE / "model_2000.pt"),
        "onnx_sha256": sha256(onnx),
        "mjcf_sha256": sha256(xml),
        "usd_sha256": sha256(HERE / "src_snapshot" / "robot.usd"),
        "observation_width": 35,
        "action_width": 6,
        "target_height_m": 0.245,
        "control": vars(cfg),
        "results": results,
    }
    out = HERE / "model2000_mujoco_probe.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out, flush=True)


if __name__ == "__main__":
    main()
