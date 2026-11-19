# SPDX-License-Identifier: MIT
"""Collect real WASD false-positive histories for stair-router supervision."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path

os.environ.setdefault('MUJOCO_GL', 'disable')

import numpy as np
import torch

from play_repaired import HERE, AutonomousMapSimulation, RepairedSimulation, load_candidate, maps
from search_stair_demo import DemoPolicy
from verify_wasd import Case, run_case


SIM = None
ROLE = None


def initialize(stair, router):
    global SIM, ROLE
    model, hashes = load_candidate(stair, router)
    identity = hashes['package']
    SIM = RepairedSimulation(model, identity, show_viewer=False)
    ROLE = AutonomousMapSimulation(DemoPolicy(model.stair.e0), identity, show_viewer=False)
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'router_neg_{os.getpid()}'


def rollout(task):
    case, out, with_gate = task
    sim = SIM if with_gate else ROLE
    return run_case(sim, case, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stair', type=Path, required=True)
    parser.add_argument('--router', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    tasks = []
    for with_gate in (False, True):
        for height in (.28, .32, .36, .40, .42):
            for speed, yaw, offset, wall in ((.65, -5., -.04, 45), (.9, 0., 0., 50), (1.12, 5., .04, 50)):
                for rise in (False, True):
                    name = f'g{int(with_gate)}_wall{wall}_h{height:.2f}_v{speed:.2f}_r{int(rise)}'
                    case = Case(name, target=height, yaw=yaw, offset=offset, speed=speed,
                                map_height=wall, raise_while_moving=rise, mode='wall', duration=4.0)
                    tasks.append((case, args.out, with_gate))
            for rise in (False, True):
                name = f'g{int(with_gate)}_flat_h{height:.2f}_r{int(rise)}'
                case = Case(name, target=height, raise_while_moving=rise, mode='flat', duration=3.5)
                tasks.append((case, args.out, with_gate))
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.stair, args.router)) as pool:
        results = list(pool.map(rollout, tasks, chunksize=1))

    observations, histories = [], []
    for result in results:
        with np.load(args.out / (result['name'] + '.npz'), allow_pickle=False) as data:
            obs = data['obs'].astype(np.float32)
            control = data['control']
        if result['mode'] == 'wall':
            hit = result['steps'][0]['hit']
            if hit is None:
                continue
            # Keep the first seconds of pushing and the actual false activations. Geometry is used only for labels.
            t = control[:, 0]
            ids = np.flatnonzero((t >= hit['t'] - .02) & ((t < hit['t'] + 1.10) | (control[:, 5] > .2)))
        else:
            ids = np.flatnonzero(control[:, 1] > .1)[::3]
        if not len(ids):
            continue
        prefix = np.concatenate((np.repeat(obs[:1], 39, axis=0), obs))
        observations.append(obs[ids])
        histories.append(np.stack([prefix[i:i + 40].reshape(-1) for i in ids]))
    payload = dict(obs=torch.from_numpy(np.concatenate(observations)),
                   hist=torch.from_numpy(np.concatenate(histories)))
    output = args.out / 'router_negatives.pt'
    torch.save(payload, output)
    report = {'frames': len(payload['obs']), 'episodes': len(results), 'rollouts': results}
    (args.out / 'COLLECTION.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps({k: v for k, v in report.items() if k != 'rollouts'}), flush=True)


if __name__ == '__main__':
    main()
