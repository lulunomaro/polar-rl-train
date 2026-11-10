from __future__ import annotations
import argparse, json, math, random, sys
from pathlib import Path
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from play_ppo_flatv1_control import Simulation

ROOT = Path(r"D:\claude2\fangzhen")
XML = ROOT / r"tmp\mod4v3_r3_extract_20261107\MOD4v3_HW300N60_R3\mjcf\scene.xml"
RUNTIME = ROOT / r"tmp\mod4v3_r3_extract_20261107\MOD4v3_HW300N60_R3\runtime_config.json"
SEMANTICS = ROOT / r"tmp\mod4v3_r3_extract_20261107\MOD4v3_HW300N60_R3\semantics.json"
BANK = ROOT / r"tmp\mod4v3_asset\reset_bank.json"
TEMPLATE = HERE / "ckpt_013000.pt"

def args_for(ckpt: str):
    return argparse.Namespace(
        ckpt=ckpt, template=str(TEMPLATE), xml=str(XML), runtime=str(RUNTIME),
        semantics=str(SEMANTICS), bank=str(BANK), device="cpu",
        height=0.28, vx=0.9, vy=0.0, wz=1.2, term_height=0.18,
        fall_interval=7.0, drop_height=1.0, drop_tilt=0.75,
        action_ema=0.0, start_fall=False, auto_fall=False,
        headless=True, steps=0, log_every=100,
    )

def actual_yaw_rate(sim):
    with torch.no_grad():
        return float(sim.env.state()[3][0, 2])

def run_case(sim, name, *, vx=0.0, reverse=False, wz=0.0, height=0.28, steps=260, settle=100):
    sim.reset_standing()
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
        "action_abs_max": float(np.abs(a).max()),
        "terminations": int(sim.tracker.failed - failed0),
        "fall_count": int(sim.tracker.falls),
    }

def run_drop(sim, trial):
    random.seed(1000 + trial)
    sim.reset_standing()
    sim.tracker.reset()
    sim.trigger_random_fall()
    failed0 = sim.tracker.failed
    min_z = 999.0
    for _ in range(500):
        t = sim.step(set())
        min_z = min(min_z, float(t["z"]))
    return {
        "trial": trial,
        "recovered": int(sim.tracker.recovered),
        "failed": int(sim.tracker.failed - failed0),
        "active": bool(sim.tracker.active),
        "min_z": float(min_z),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    random.seed(0)
    sim = Simulation(args_for(a.ckpt))
    result = {"checkpoint": str(Path(a.ckpt).resolve()), "format": "FLAT_V2_FINAL_LOCAL_EVAL_V1", "cases": []}
    try:
        for s in [2.0, 2.2, 2.4, 2.5, 2.6, 2.7]:
            result["cases"].append(run_case(sim, f"forward_{s:.1f}", vx=s, steps=300, settle=120))
        result["cases"].append(run_case(sim, "backward_1.5", vx=1.5, reverse=True, steps=300, settle=120))
        for wz in [2*math.pi, 10.210176, 14.137167]:
            result["cases"].append(run_case(sim, f"yaw_{wz:.2f}", wz=wz, steps=300, settle=120))
        for h in [0.20, 0.40]:
            result["cases"].append(run_case(sim, f"height_{h:.2f}", height=h, steps=260, settle=100))
        result["jitter"] = run_case(sim, "jitter_600", vx=0.9, wz=1.2, height=0.28, steps=600, settle=300)
        result["drop_tests"] = [run_drop(sim, i) for i in range(3)]
    finally:
        sim.close()
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
