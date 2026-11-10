from __future__ import annotations
import argparse, json, math, random, sys
from pathlib import Path
import mujoco
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eval_flatv2_final import args_for, actual_yaw_rate
from play_ppo_flatv1_control import Simulation, _quat_from_euler_xyz


def qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw,
    ], dtype=np.float64)


def reset_perturbed(sim, seed):
    sim.reset_standing()
    rng = np.random.default_rng(seed)
    d = sim.env.d
    d.qpos[0] += rng.uniform(-0.02, 0.02)
    d.qpos[1] += rng.uniform(-0.02, 0.02)
    d.qpos[2] += rng.uniform(-0.005, 0.005)
    qp = _quat_from_euler_xyz(
        rng.uniform(-0.02, 0.02),
        rng.uniform(-0.02, 0.02),
        rng.uniform(-0.05, 0.05),
    )
    d.qpos[3:7] = qmul(qp, np.asarray(d.qpos[3:7], dtype=np.float64))
    d.qvel[:6] += rng.uniform(-0.05, 0.05, 6)
    mujoco.mj_forward(sim.env.m, sim.env.d)
    sim.a_prev.zero_()
    sim._action_filter = None
    sim.tracker.reset()
    sim.z = float(sim.env.z)
    sim.cos_tilt = float(sim.env.cos_tilt)


def run_case(sim, seed, name, *, vx=0.0, reverse=False, wz=0.0, height=0.28, steps=300, settle=120):
    reset_perturbed(sim, seed)
    sim.args.vx = abs(float(vx))
    sim.args.wz = abs(float(wz))
    sim.args.height = float(height)
    sim.height = float(height)
    keys = set()
    if vx:
        keys.add("s" if reverse else "w")
    if wz:
        keys.add("a")
    vxs, wzs, zs, cs, acts = [], [], [], [], []
    failed0 = sim.tracker.failed
    for _ in range(steps):
        t = sim.step(keys)
        vxs.append(float(t["vx"]))
        wzs.append(actual_yaw_rate(sim))
        zs.append(float(t["z"]))
        cs.append(float(t["cos_tilt"]))
        acts.append(sim.a_prev.detach().cpu().numpy().reshape(-1).copy())
    sl = slice(max(0, steps - settle), steps)
    v = np.asarray(vxs[sl]); w = np.asarray(wzs[sl]); z = np.asarray(zs[sl]); c = np.asarray(cs[sl])
    a = np.asarray(acts[sl])
    da = np.linalg.norm(np.diff(a, axis=0), axis=1) if len(a) > 1 else np.asarray([0.0])
    return {
        "seed": int(seed),
        "name": name,
        "cmd_vx": float(vx) * (-1 if reverse else 1),
        "actual_vx_mean": float(v.mean()),
        "vx_abs_err": float(abs(v.mean() - (float(vx) * (-1 if reverse else 1)))),
        "cmd_wz": float(wz),
        "actual_wz_mean": float(w.mean()),
        "wz_abs_err": float(abs(w.mean() - float(wz))),
        "height_cmd": float(height),
        "height_mean": float(z.mean()),
        "height_abs_err": float(abs(z.mean() - float(height))),
        "z_std": float(z.std()),
        "cos_min": float(c.min()),
        "action_delta_mean": float(da.mean()),
        "terminations": int(sim.tracker.failed - failed0),
        "fall_count": int(sim.tracker.falls),
    }


def summarize(rows):
    keys = ["actual_vx_mean", "vx_abs_err", "actual_wz_mean", "wz_abs_err", "height_mean", "height_abs_err", "z_std", "cos_min", "action_delta_mean", "terminations", "fall_count"]
    out = {"n": len(rows), "rows": rows}
    for key in keys:
        vals = np.asarray([r[key] for r in rows], dtype=float)
        out[key] = {"mean": float(vals.mean()), "std": float(vals.std()), "min": float(vals.min()), "max": float(vals.max())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=10)
    a = ap.parse_args()
    sim = Simulation(args_for(a.ckpt))
    result = {"checkpoint": str(Path(a.ckpt).resolve()), "format": "FLAT_V2_MULTI_ENV_EVAL_V1", "seeds": a.seeds, "cases": {}}
    cases = [
        ("forward_2.0", dict(vx=2.0)),
        ("forward_2.2", dict(vx=2.2)),
        ("backward_1.5", dict(vx=1.5, reverse=True)),
        ("yaw_14.14", dict(wz=14.137167)),
        ("jitter_0.9_1.2", dict(vx=0.9, wz=1.2, steps=600, settle=300)),
        ("height_0.20", dict(height=0.20, steps=260, settle=100)),
        ("height_0.40", dict(height=0.40, steps=260, settle=100)),
    ]
    try:
        for name, kwargs in cases:
            rows = [run_case(sim, seed, name, **kwargs) for seed in range(a.seeds)]
            result["cases"][name] = summarize(rows)
        drops = []
        for seed in range(a.seeds):
            random.seed(1000 + seed)
            sim.reset_standing()
            sim.tracker.reset()
            sim.trigger_random_fall()
            failed0 = sim.tracker.failed
            min_z = 999.0
            for _ in range(500):
                t = sim.step(set())
                min_z = min(min_z, float(t["z"]))
            drops.append({"seed": seed, "recovered": int(sim.tracker.recovered), "failed": int(sim.tracker.failed - failed0), "active": bool(sim.tracker.active), "min_z": float(min_z)})
        result["drop_tests"] = drops
    finally:
        sim.close()
    text = json.dumps(result, indent=2, ensure_ascii=False)
    Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
