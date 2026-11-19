# SPDX-License-Identifier: MIT
"""Fit a small sagittal damping correction in the WASD simulator at driver takeover."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import json
from pathlib import Path

import mujoco as mj
import numpy as np
import torch

from play_repaired import CONTROL_DT, HERE, RepairedSimulation, load_manifest, maps, stair
from verify_wasd import Case, ContactTrace, load_case


@dataclass(frozen=True)
class TakeoverCase:
    height: float
    mode: str
    delay: float = .04
    offset: float = 0.
    yaw: float = 0.
    speed: float = .90


_SNAPSHOTS = []
_SPEC = mj.mjtState.mjSTATE_INTEGRATION
_KEYS = {'stop': set(), 'reverse': {'s'}, 'turn': {'a'}, 'turn_w': {'w', 'a'}}


def capture(sim, case):
    scene = Case(case.mode, target=case.height, speed=case.speed, offset=case.offset, yaw=case.yaw)
    trace = ContactTrace(sim, load_case(sim, scene))
    native_step = mj.mj_step

    def monitor(m, d):
        native_step(m, d)
        trace.add(m, d)

    mj.mj_step = monitor
    try:
        for index in range(200):
            now = index * CONTROL_DT
            if trace.hits[0] and now >= trace.hits[0]['t'] + case.delay:
                break
            sim.step({'w'} if now >= .40 else set())
        else:
            raise ValueError(f'Approach did not contact the step in {case}')
    finally:
        mj.mj_step = native_step
    mj.mj_forward(sim.m, sim.d)
    state = np.empty(mj.mj_stateSize(sim.m, _SPEC))
    mj.mj_getState(sim.m, sim.d, state, _SPEC)
    return state, sim.cmd_vx, sim.cmd_wz, sim.target_h, sim.prev_a.copy(), sim.steps, sim.unified.stair_mix


def initialize(candidate, scenarios, handoff_duration):
    import os
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'takeover_{os.getpid()}'
    model, hashes, prep = load_manifest(candidate)
    model.handoff_duration = handoff_duration
    # All profiles use the same single-step XML. Keep one MjData arena per worker.
    sim = RepairedSimulation(model, hashes['package'], show_viewer=False, jump_stance_prep=prep)
    for case in scenarios:
        snapshot = capture(sim, case)
        _SNAPSHOTS.append((case, sim, snapshot))


def run(sim, case, snapshot, gains):
    state, cmd_x, cmd_w, height, prev_a, tick, authority = snapshot
    mj.mj_setState(sim.m, sim.d, state, _SPEC)
    mj.mj_forward(sim.m, sim.d)
    sim.cmd_vx, sim.cmd_wz, sim.target_h, sim.prev_a, sim.steps = cmd_x, cmd_w, height, prev_a.copy(), tick
    policy = sim.unified
    policy.stair_mix = authority
    policy.handoff_mix = 0.0
    policy.set_handoff_gains(gains)
    x0 = float(sim.d.qpos[0])
    keys = _KEYS[case.mode]
    rows = []

    @torch.inference_mode()
    def normal_action(obs):
        x = stair.canonicalize_normal_obs(torch.from_numpy(obs)[None])
        action = policy.stair.e0(x)[0].numpy()
        previous_mix = policy.stair_mix
        policy.stair_mix = 0.0
        action = policy.handoff_action(obs, action, previous_mix, False)
        return np.clip(action, -6., 6.), {'e0': 1., 'e1': 0., 'e2': 0.}

    policy.act = normal_action
    for _ in range(104):
        before = float(sim.d.time)
        sim.step(keys)
        r = sim.d.xmat[sim.env.base_id].reshape(3, 3)
        pitch = np.degrees(np.arcsin(np.clip(-r[2, 0], -1., 1.)))
        forward = float(sim.d.qvel[:3] @ r[:, 0])
        rows.append([float(sim.d.qpos[0]) - x0, forward, pitch, float(sim.d.qvel[5]), float(sim.d.qpos[2])])
        if sim.d.time < before or abs(pitch) > 50. or sim.d.qpos[2] < .12:
            return {'fall': True, 'cost': 40., 'peak_pitch': abs(float(pitch))}
    x, v, pitch, wz, z = np.asarray(rows).T
    peak_pitch = float(np.abs(pitch).max())
    squat = float(np.maximum(case.height - .043 - z, 0.).max())
    cost = 22. * squat + .06 * peak_pitch + .05 * float(np.maximum(np.abs(pitch[:45]) - 10., 0.).mean())
    if case.mode == 'reverse':
        cost += 2.5 * max(0., .8 + float(x[-1]))
        cost += .65 * abs(float(v[-20:].mean()) + .60)
        cost += 2.0 * max(0., float(x.max()) - .17)
    elif case.mode == 'turn_w':
        cost += .4 * abs(float(v[-20:].mean()) - .5)
        cost += 1.8 * max(0., -float(x.min()))
        cost += .15 * abs(float(wz[-20:].mean()) - sim.cmd_wz)
    else:
        cost += 4.0 * float(np.abs(x).max()) + .45 * float(np.abs(v).max())
        cost += 3.0 * float(np.abs(v[-20:]).mean()) + 1.4 * abs(float(x[-1]))
        if case.mode == 'turn':
            cost += .15 * abs(float(wz[-20:].mean()) - sim.cmd_wz)
    return {'fall': False, 'cost': cost, 'peak_pitch': peak_pitch, 'max_abs_displacement': float(np.abs(x).max()),
            'last_x': float(x[-1]), 'last_v': float(v[-20:].mean()), 'min_v': float(v.min()),
            'minimum_body_height_m': float(z.min())}


def evaluate(gains):
    details = [run(sim, case, snap, gains) for case, sim, snap in _SNAPSHOTS]
    costs = np.array([d['cost'] for d in details])
    return float(costs.mean() + .25 * costs.max()), details


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--candidate', default=HERE / 'CANDIDATE.json', type=Path)
    ap.add_argument('--workers', default=4, type=int)
    ap.add_argument('--generations', default=6, type=int)
    ap.add_argument('--handoff-seconds', default=.94, type=float)
    ap.add_argument('--low-stance', action='store_true')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = [TakeoverCase(h, mode, delay=delay, offset=x, speed=v, yaw=yaw) for h, mode, delay, x, v, yaw in (
        (.42, 'stop', .04, 0., .90, 0.), (.42, 'stop', .30, 0., .90, 0.),
        (.42, 'stop', .26, -.06, .90, 0.), (.40, 'stop', .15, 0., .90, 8.),
        (.36, 'stop', .10, .03, .90, 0.), (.28, 'stop', .20, .06, .90, 0.),
        (.42, 'reverse', .04, 0., .90, 0.), (.39, 'reverse', .12, .03, .86, -8.),
        (.42, 'turn_w', .30, 0., .90, 0.), (.42, 'turn', .13, -.03, .74, 5.),
    )]
    if args.low_stance:
        cases = [TakeoverCase(h, mode, delay=delay, offset=x, speed=v, yaw=yaw)
                 for h, mode, delay, x, v, yaw in (
                     (.28, 'stop', .08, 0., .90, 0.), (.28, 'stop', .16, -.045, .84, 0.),
                     (.28, 'turn_w', .16, .04, .94, 6.), (.28, 'reverse', .11, 0., .90, 0.),
                     (.32, 'stop', .08, 0., .90, 0.), (.32, 'stop', .18, .045, .83, -6.),
                     (.32, 'reverse', .15, -.035, .90, 4.), (.34, 'stop', .12, -.025, .86, 0.),
                 )]
    rng = np.random.default_rng(311729)
    manifest = json.loads(args.candidate.read_text(encoding='utf-8'))
    seed = manifest['settings'].get('handoff_gains', [0.] * 6)
    mean = np.pad(seed, (0, 12-len(seed)))
    spread = np.array([1., 1.2, 1.4] * 4)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate, cases, args.handoff_seconds)) as executor:
        for generation in range(args.generations):
            controls = [np.zeros_like(mean), .5 * mean, -mean] if generation == 0 else []
            candidates = [mean, *controls, *(r['gains'] for r in results[:2]), *np.clip(
                rng.normal(mean, spread, size=(27, 12)), -3.8, 3.8)]
            for coeffs, (rank, metrics) in zip(candidates, executor.map(evaluate, candidates), strict=True):
                results.append({'generation': generation, 'gains': list(coeffs), 'score': rank, 'metrics': metrics})
            results.sort(key=lambda row: row['score'])
            leaders = np.asarray([row['gains'] for row in results[:7]])
            mean = leaders.mean(0)
            spread = np.maximum(.14, .88 * leaders.std(0))
            report = {'profiles': [vars(c) for c in cases], 'handoff_seconds': args.handoff_seconds, 'results': results}
            (args.out / 'SEARCH.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf8')
            print(generation, results[0], flush=True)


if __name__ == '__main__':
    main()
