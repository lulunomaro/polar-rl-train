"""Repeatable, per-episode MuJoCo robustness and sim-to-sim test."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from sim_runtime import ActionDelay, Mod4Sim, RuntimeConfig  # noqa: E402


SCENARIOS = {
    "flat_forward": {"spawn": (-4.0, 0.0, 0.0, 0.0), "cmd": (.60, 0.0), "seconds": 6.0},
    "flat_reverse": {"spawn": (-2.5, 1.1, math.pi, 0.0), "cmd": (-.40, 0.0), "seconds": 5.0},
    "turn": {"spawn": (-4.0, 1.8, 0.0, 0.0), "cmd": (0.0, 1.5), "seconds": 5.0,
             "auto_mode": False, "mode": 3, "height": .32},
    "rough": {"spawn": (-5.3, 4.8, 0.0, 0.0), "cmd": (.60, 0.0), "seconds": 7.0},
    "stairs": {"spawn": (-2.8, -2.5, 0.0, 0.0), "cmd": (.45, 0.0), "seconds": 7.0},
    "tunnel": {"spawn": (.25, 0.0, 0.0, 0.0), "cmd": (.35, 0.0), "seconds": 8.0},
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def yaw_from_quat(q):
    w, x, y, z = q
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


def angle_delta(a, b):
    return math.atan2(math.sin(a - b), math.cos(a - b))


def contact_with(sim, geom_name):
    gid = mujoco.mj_name2id(sim.model, mujoco.mjtObj.mjOBJ_GEOM, geom_name)
    if gid < 0:
        return False
    return any(sim.data.contact[i].geom1 == gid or sim.data.contact[i].geom2 == gid
               for i in range(sim.data.ncon))


def run_episode(sim, name, spec, seed, randomized):
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    x, y, yaw, ground = spec["spawn"]
    sim.restore_nominal_parameters()
    params = sim.randomize(rng, mild=True) if randomized else {
        "mass_scale": 1.0, "inertia_scale": 1.0, "friction_scale": 1.0}
    # mj_setConst(), required after changing body inertias, also refreshes data from qpos0.
    # Apply the scenario pose afterwards so every randomized episode starts in the right lane.
    sim.reset(x, y, yaw, ground)
    sim.command.vx, sim.command.wz = spec["cmd"]
    sim.command.auto_mode = bool(spec.get("auto_mode", True))
    sim.command.mode = int(spec.get("mode", 0))
    sim.command.height = float(spec.get("height", .34))
    delay_steps = int(rng.integers(0, 3)) if randomized else 0
    delay = ActionDelay(delay_steps)
    obs_noise = float(rng.uniform(0.0, 0.01)) if randomized else 0.0
    steps = int(round(spec["seconds"] * sim.cfg.policy_hz))
    start_pos = sim.base_position.copy()
    start_yaw = yaw_from_quat(sim.data.qpos[3:7])
    roof_hits = 0
    integrated_yaw = 0.0
    finite = True
    try:
        for i in range(steps):
            if randomized and i == int(2.0 * sim.cfg.policy_hz):
                sign = -1.0 if seed % 2 else 1.0
                sim.push((0.0, sign * 10.0, 0.0), float(rng.uniform(.10, .30)))
            sim.step_control(obs_noise, delay)
            roof_hits += int(contact_with(sim, "tunnel_roof"))
            integrated_yaw += float(sim.data.sensor("base_gyro").data[2]) / sim.cfg.policy_hz
    except FloatingPointError:
        finite = False
    end_pos = sim.base_position.copy()
    end_yaw = yaw_from_quat(sim.data.qpos[3:7])
    health = sim.health()
    dx_world, dy_world = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
    forward = math.cos(start_yaw) * dx_world + math.sin(start_yaw) * dy_world
    lateral = -math.sin(start_yaw) * dx_world + math.cos(start_yaw) * dy_world
    yaw_change = angle_delta(end_yaw, start_yaw)
    plant_ok = finite and sim.max_closure_error < .002 and sim.max_mimic_error < .01
    upright = health["upright_cos"] > .50 and end_pos[2] > .075
    if name == "flat_forward":
        task_ok = forward > 1.0 and abs(lateral) < 1.5
    elif name == "flat_reverse":
        task_ok = forward < -.55
    elif name == "turn":
        task_ok = abs(integrated_yaw) > 1.2 and float(np.linalg.norm(end_pos[:2] - start_pos[:2])) < 1.0
    elif name == "rough":
        task_ok = end_pos[0] > -1.0 and abs(end_pos[1] - 4.8) < .70
    elif name == "stairs":
        task_ok = end_pos[0] > 0.0 and abs(end_pos[1] + 2.5) < .70
    elif name == "tunnel":
        task_ok = end_pos[0] > 1.95 and abs(end_pos[1]) < .40 and roof_hits == 0
    else:
        task_ok = False
    return {
        "scenario": name, "seed": seed, "randomized": randomized, **params,
        "action_delay_steps": delay_steps, "observation_noise_std": obs_noise,
        "finite": finite, "plant_ok": plant_ok, "upright": upright, "task_ok": task_ok,
        "forward_displacement_m": forward, "lateral_displacement_m": lateral,
        "yaw_change_rad_wrapped": yaw_change, "integrated_yaw_rad": integrated_yaw,
        "roof_contact_control_steps": roof_hits,
        "final_base_xyz": end_pos.tolist(), "final_upright_cos": health["upright_cos"],
        "max_closure_error_m": sim.max_closure_error,
        "max_mimic_error_rad": sim.max_mimic_error,
        "final_mimic_error_rad": health["mimic_error_rad"],
        "max_abs_torque_nm_actuator_order": health["max_abs_torque_nm_actuator_order"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=ROOT / "policies" / "mod4_extended_800.onnx")
    parser.add_argument("--random-seeds", type=int, default=5)
    parser.add_argument("--yaw-assist", type=float, default=0.0,
                        help="extra differential-wheel yaw feedback gain; 0 tests the raw policy adapter")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "robustness_report.json")
    args = parser.parse_args()
    xml = ROOT / "model" / "rm_training_arena_headless.xml"
    sim = Mod4Sim(xml, args.policy, RuntimeConfig(yaw_assist_gain=args.yaw_assist))
    started = time.perf_counter()
    episodes = []
    for name, spec in SCENARIOS.items():
        episodes.append(run_episode(sim, name, spec, 20260913, False))
        for j in range(args.random_seeds):
            episodes.append(run_episode(sim, name, spec, 1000 * list(SCENARIOS).index(name) + j, True))
        print(name, sum(e["task_ok"] for e in episodes if e["scenario"] == name), "/",
              sum(e["scenario"] == name for e in episodes), flush=True)
    summary = {}
    for name in SCENARIOS:
        rows = [e for e in episodes if e["scenario"] == name]
        rr = [e for e in rows if e["randomized"]]
        summary[name] = {
            "nominal_task_ok": rows[0]["task_ok"],
            "randomized_task_success_rate": sum(e["task_ok"] for e in rr) / len(rr),
            "randomized_upright_rate": sum(e["upright"] for e in rr) / len(rr),
            "randomized_plant_ok_rate": sum(e["plant_ok"] for e in rr) / len(rr),
            "worst_closure_error_m": max(e["max_closure_error_m"] for e in rows),
            "max_abs_lateral_displacement_m": max(abs(e["lateral_displacement_m"]) for e in rows),
        }
    randomized_rows = [e for e in episodes if e["randomized"]]
    report = {
        "status": "MEASURED_SIM_TO_SIM_ONLY",
        "policy": str(args.policy.resolve()), "policy_sha256": sha256(args.policy),
        "mjcf": str(xml.resolve()), "mjcf_sha256": sha256(xml),
        "test_contract": {
            "nominal_episodes_per_scenario": 1,
            "randomized_episodes_per_scenario": args.random_seeds,
            "yaw_assist_gain": args.yaw_assist,
            "randomization": "mass/inertia +/-10%, friction x0.8..1.2, damping x0.85..1.2, observation noise 0..0.01, action delay 0..2 control steps, lateral 10 N push for 0.1..0.3 s",
            "plant_gate": "finite AND closure<2mm AND mimic<0.01rad",
            "scope": "MuJoCo sim-to-sim stress test; it does not certify real-robot robustness",
        },
        "overall_randomized": {
            "episodes": len(randomized_rows),
            "plant_ok_rate": sum(e["plant_ok"] for e in randomized_rows) / len(randomized_rows),
            "upright_rate": sum(e["upright"] for e in randomized_rows) / len(randomized_rows),
            "task_success_rate": sum(e["task_ok"] for e in randomized_rows) / len(randomized_rows),
            "worst_closure_error_m": max(e["max_closure_error_m"] for e in randomized_rows),
        },
        "by_scenario": summary, "episodes": episodes,
        "elapsed_s": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    def _json_default(value):
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return float(value)
        raise TypeError(type(value).__name__)

    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False,
                                      default=_json_default) + "\n", encoding="utf-8")
    print(json.dumps(report["overall_randomized"], indent=2, ensure_ascii=False))
    print(args.output.resolve())


if __name__ == "__main__":
    main()
