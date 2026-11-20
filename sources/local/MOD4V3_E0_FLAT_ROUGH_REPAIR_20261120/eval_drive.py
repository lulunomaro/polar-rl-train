"""Matched MuJoCo E0 drive tests using the released MOD4v3 plant and SCUT tile meshes."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from types import MethodType
import gc
import hashlib
import importlib.util
import json
import os
import shutil

os.environ.setdefault('MUJOCO_GL', 'disable')
import mujoco
import numpy as np
import torch

REPO = Path(__file__).resolve().parents[3]
DELIVERY = REPO / 'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
FAMILIES = {'flat': ('plane_for_rm', 0), 'rough': ('random_uniform_for_rm', 9)}
COLUMNS = ['t', 'command', 'vx', 'height', 'pitch_deg', 'roll_deg', 'x', 'y', 'closure_m']
BASELINES = {
    'c874': ('deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt', 'c874a1af'),
    'flat979': ('sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/weights/selected_flat_speed_candidate.pt', '979e355a'),
    'old010': ('sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116/weights/model_010m.pt', '37dbe178'),
}


def load_showcase(output, checkpoint):
    source = DELIVERY / 'viewer/showcase.py'
    spec = importlib.util.spec_from_file_location('e0_drive_showcase', source)
    show = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(show)
    show.B = output / 'scene_assets'
    (show.B / 'tiles').mkdir(parents=True)
    for family, level in FAMILIES.values():
        name = f'r{level:02d}_c{show.COLS[family]:02d}'
        shutil.copy2(DELIVERY / 'viewer/tiles' / f'{name}.npz', show.B / 'tiles')
        cached_field = DELIVERY / 'viewer' / f'{name}_hf_v2.npz'
        if cached_field.is_file():
            shutil.copy2(cached_field, show.B)
    show.CKPT = checkpoint
    show.EXPECTED = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    return show


def install_diagnostic_physics(simulation):
    env = simulation.env
    model, data = env.m, env.d
    simulation.closure_peak_m = 0.

    def physics(owner, action):
        action = action.clamp(-owner.action_clip, owner.action_clip)
        for substep in range(owner.decim):
            effort = owner._torque(action).detach().cpu().numpy().reshape(-1)
            if substep % 4 == 0:
                data.ctrl[owner.act_ids[:4]] = effort[:4]
            data.ctrl[owner.act_ids[4:]] = effort[4:]
            mujoco.mj_step(model, data)
            if not (np.isfinite(data.qpos).all() and np.isfinite(data.qvel).all()):
                raise show.SafetyStop('nonfinite')
            simulation.closure = max(np.linalg.norm(data.site_xpos[a] - data.site_xpos[b])
                                     for a, b in simulation.pairs)
            simulation.closure_peak_m = max(simulation.closure_peak_m, simulation.closure)
            if simulation.closure > 1.:
                raise show.SafetyStop('closure >1m')
        owner.a_prev = action.detach().to(owner.device)
        return owner.state()

    env.step = MethodType(physics, env)


def run_case(show, terrain, height, profile, initial, segments, simulation=None):
    owned = simulation is None
    if owned:
        family, level = FAMILIES[terrain]
        simulation = show.Replay(level=level, family=family)
    env = simulation.env
    model, data = env.m, env.d
    if not owned:
        mujoco.mj_resetData(model, data)
        simulation.reset_standing()
        simulation.reason = ''
        simulation.closure = 0.
    simulation.set_height(height)
    start_x, start_y = initial
    data.qpos[:3] = [start_x, start_y, simulation.ground(start_x, start_y) + env.bank_z]
    data.qpos[3:7] = [1., 0., 0., 0.]
    data.qvel[:] = 0.
    mujoco.mj_forward(model, data)
    env.state()
    install_diagnostic_physics(simulation)
    trace, metrics = [], []
    reset_at_start = simulation.reset_count
    try:
        for duration, command in segments:
            begin = len(trace)
            simulation.args.vx = abs(command) or .5
            keys = {'w'} if command > 0 else {'s'} if command < 0 else set()
            for _ in range(round(duration * 50)):
                simulation.cmd_vx = command
                simulation.cmd_vy = simulation.cmd_wz = 0.
                simulation.step(keys)
                if simulation.reset_count != reset_at_start:
                    break
                rotation = data.xmat[env.base_id].reshape(3, 3)
                heading = rotation[:2, 0] / np.linalg.norm(rotation[:2, 0])
                pitch = np.degrees(np.arcsin(np.clip(-rotation[2, 0], -1., 1.)))
                roll = np.degrees(np.arctan2(rotation[2, 1], rotation[2, 2]))
                trace.append([(len(trace) + 1) / 50., command, data.qvel[:2] @ heading,
                              simulation.z, pitch, roll, *data.qpos[:2], simulation.closure])
            if len(trace) == begin:
                break
            values = np.asarray(trace[begin:])
            tail = values[-min(len(values), 50):]
            metrics.append(dict(command=command, samples=len(values), tail_vx=float(tail[:, 2].mean()),
                                tail_abs_error=float(np.abs(tail[:, 2] - command).mean()),
                                tail_height=float(tail[:, 3].mean()), tail_x_change=float(tail[-1, 6]-tail[0, 6]),
                                x_change=float(values[-1, 6]-values[0, 6]),
                                peak_pitch_deg=float(np.abs(values[:, 4]).max()),
                                first_08s_peak_pitch_deg=float(np.abs(values[:40, 4]).max())))
            if simulation.reset_count != reset_at_start:
                break
    finally:
        # The bound override captures the player and keeps its native allocations alive.
        del env.step
        if owned:
            simulation.close()
    return dict(terrain=terrain, height=height, profile=profile, segments=metrics,
                complete=len(trace) == sum(round(duration * 50) for duration, _ in segments),
                completed_seconds=len(trace)/50., reason=simulation.reason or None,
                closure_peak_m=float(simulation.closure_peak_m)), np.asarray(trace).reshape(-1, len(COLUMNS))


def cases():
    for terrain in FAMILIES:
        for height in (.40, .42):
            for sign in (-1, 1):
                yield terrain, height, f'low_{sign:+d}', (-.8, -.14 if sign > 0 else .12), (
                    (4., 0.), (3., .50*sign), (2., 0.), (3., -.50*sign), (2., 0.))
        for height in (.28, .40):
            for speed in (1.2, 2.2):
                yield terrain, height, f'brake_{speed:g}', (-.8, -.10 if speed == 1.2 else .10), (
                    (2., 0.), (1., speed), (2., 0.), (1., -speed), (2., 0.), (1., speed), (2., 0.))
        if terrain == 'rough':
            for sign in (-1, 1):
                yield terrain, .28, f'traverse_{sign:+d}', (-1.9*sign, .32*sign), (
                    (2., 0.), (3., 1.2*sign), (1.5, 0.))


def evaluate(args):
    name, path, prefix, output = args
    torch.set_num_threads(1)
    output.mkdir()
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if not sha.startswith(prefix):
        raise ValueError(f'{name} SHA mismatch: {sha}')
    show = load_showcase(output, path)
    rows, traces = [], {}
    for case in cases():
        row, trace = run_case(show, *case)
        gc.collect()
        rows.append(row)
        key = f'{case[0]}_{case[1]:.2f}_{case[2]}'
        traces[key] = trace
        print(name, key, row['completed_seconds'], row['reason'], flush=True)
    np.savez_compressed(output / 'rollouts.npz', **traces)
    (output / 'RESULT.json').write_text(json.dumps(dict(model=name, checkpoint=str(path), sha256=sha,
        trace_columns=COLUMNS, rows=rows), indent=2) + '\n', encoding='utf-8')


def main():
    parser = ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--baseline', action='append', choices=BASELINES, default=[])
    parser.add_argument('--model', action='append', type=Path, default=[])
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    args.out.mkdir(parents=True)
    models = [(name, REPO / BASELINES[name][0], BASELINES[name][1]) for name in args.baseline]
    models.extend((path.stem, path.resolve(), '') for path in args.model)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(evaluate, [(*row, args.out / row[0]) for row in models]))


if __name__ == '__main__':
    main()
