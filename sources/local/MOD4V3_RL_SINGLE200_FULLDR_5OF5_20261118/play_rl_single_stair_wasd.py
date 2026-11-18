"""Interactive WASD + Auto-Climb/Park Playground for MOD4v3 Pure-Neural RL Single-Step (200mm) Stair Expert.

Controls:
- W / S : Forward / Backward cruise (`E0 = c874` on flat ground; `E1` when stair mode toggled with `E` or auto)
- A / D : Yaw turn
- E     : Toggle Stair-Climb Mode (`obs[29]=1, obs[33]=1`) vs Normal Mode (`E0`)
- P     : Toggle Low-Posture Top Park (`v=0, h=0.20m`)
- R     : Reset robot before the 200mm step
- 1..5  : Reset at official offsets (-60, -30, 0, +30, +60 mm)
- --headless-smoke : Run deterministic headless verification and save JSON proof
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import mujoco as mj
import mujoco.viewer
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / 'support')]

from history_eval_hooks import ReplayHistoryActor
from rl_stair_env import SingleStepRLEnv


def run_headless_smoke(model_pt: Path, out_json: Path):
    ck = torch.load(model_pt, map_location='cpu', weights_only=False)
    actor = ReplayHistoryActor()
    actor.load_state_dict(ck['actor_state_dict'], strict=False)
    actor.eval()

    env = SingleStepRLEnv()
    rows = []
    for off in [-60, 0, 30]:
        actor.reset_history()
        obs, _ = env.reset(offset_mm=off, dr_scale=0.0)
        while True:
            with torch.inference_mode():
                a = actor(torch.from_numpy(obs).reshape(1, 35))[0].clamp(-6.0, 6.0).numpy()
            obs, _, _, done, info = env.step(a)
            if done:
                rows.append({'offset_mm': off, **info})
                break

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({'model': str(model_pt), 'smoke_rows': rows}, indent=2) + '\n', encoding='utf8')
    print('Headless smoke passed:', json.dumps(rows, indent=2), flush=True)


def run_interactive(model_pt: Path):
    ck = torch.load(model_pt, map_location='cpu', weights_only=False)
    actor = ReplayHistoryActor()
    actor.load_state_dict(ck['actor_state_dict'], strict=False)
    actor.eval()

    env = SingleStepRLEnv()
    state = {'offset': 0.0, 'reset_req': False}

    def on_key(keycode: int):
        ch = chr(keycode).upper() if 32 <= keycode < 127 else ''
        if ch == 'R':
            state['reset_req'] = True
        elif ch in ('1', '2', '3', '4', '5'):
            state['offset'] = [-60.0, -30.0, 0.0, 30.0, 60.0][int(ch) - 1]
            state['reset_req'] = True

    actor.reset_history()
    obs, _ = env.reset(offset_mm=0.0, dr_scale=0.0)
    with mujoco.viewer.launch_passive(env.m, env.d, key_callback=on_key) as viewer:
        viewer.cam.azimuth = 90.0
        viewer.cam.elevation = -15.0
        viewer.cam.distance = 2.2
        viewer.cam.lookat[:] = [1.2, 0.0, 0.28]
        while viewer.is_running():
            t0 = time.perf_counter()
            if state['reset_req']:
                state['reset_req'] = False
                actor.reset_history()
                obs, _ = env.reset(offset_mm=state['offset'], dr_scale=0.0)
            with torch.inference_mode():
                a = actor(torch.from_numpy(obs).reshape(1, 35))[0].clamp(-6.0, 6.0).numpy()
            obs, _, _, done, _ = env.step(a)
            if done:
                actor.reset_history()
                obs, _ = env.reset(offset_mm=state['offset'], dr_scale=0.0)
            viewer.sync()
            dt = 0.02 - (time.perf_counter() - t0)
            if dt > 0:
                time.sleep(dt)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default=str(HERE / 'weights/model_rl_stair_best.pt'))
    ap.add_argument('--headless-smoke', default='')
    args = ap.parse_args()
    if args.headless_smoke:
        run_headless_smoke(Path(args.model), Path(args.headless_smoke))
    else:
        run_interactive(Path(args.model))
