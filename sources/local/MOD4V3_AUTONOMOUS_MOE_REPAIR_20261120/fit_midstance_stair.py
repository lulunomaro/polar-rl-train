# SPDX-License-Identifier: MIT
"""Fit a stair expert output bias against first-touch continuations in the WASD fixture."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path

os.environ.setdefault('MUJOCO_GL', 'disable')

import mujoco as mj
import numpy as np
import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, read_candidate, maps
from verify_wasd import CONTROL_DT, Case, ContactTrace, load_case

_STATE = mj.mjtState.mjSTATE_INTEGRATION
_WORKER = None


def initialize(candidate, height, speed, offsets, slow_expert):
    global _WORKER
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'midstance_fit_{os.getpid()}'
    policy, hashes, prep = load_manifest(candidate)
    sim = RepairedSimulation(policy, hashes['package'], show_viewer=False, jump_stance_prep=prep)
    expert = policy.slow_stair if slow_expert else next(
        expert for h, expert in policy.stair_height_bank if abs(h - height) < 1.e-6
    )
    if expert is None:
        raise ValueError('The candidate needs a slow stair checkpoint')
    bias = expert.e1_stair.head[-1].bias
    snapshots = []
    for offset in offsets:
        names = load_case(sim, Case('fit', target=height, speed=speed, offset=offset))
        trace = ContactTrace(sim, names)
        physical_step = mj.mj_step

        def detect(m, d):
            physical_step(m, d)
            trace.add(m, d)

        mj.mj_step = detect
        try:
            for k in range(180):
                sim.step({'w'} if k * CONTROL_DT >= .40 else set())
                if trace.hits[0] is not None:
                    break
            else:
                raise ValueError(f'No first contact for {offset=}')
        finally:
            mj.mj_step = physical_step
        state = np.empty(mj.mj_stateSize(sim.m, _STATE))
        mj.mj_getState(sim.m, sim.d, state, _STATE)
        snapshots.append((offset, names, state, sim.cmd_vx, sim.cmd_wz, sim.prev_a.copy(), sim.steps,
                          policy.history.buffer.clone(), policy.stair_mix))
    _WORKER = (sim, policy, bias, bias.detach().clone(), snapshots, height, speed)


def expanded(p):
    v, h, crank, hip, wheel = p
    return [v, h, crank, hip, crank, hip, wheel, wheel]


@torch.inference_mode()
def score(coefficients):
    sim, policy, bias, original, snapshots, height, speed = _WORKER
    bias.copy_(original + bias.new_tensor(expanded(coefficients)))
    metrics = []
    for offset, names, state, cv, cw, prev, steps, hist, mix in snapshots:
        mj.mj_setState(sim.m, sim.d, state, _STATE)
        mj.mj_forward(sim.m, sim.d)
        sim.cmd_vx, sim.cmd_wz, sim.target_h, sim.prev_a, sim.steps = cv, cw, height, prev.copy(), steps
        policy.history.buffer, policy.stair_mix, policy.handoff_mix = hist.clone(), mix, 0.
        trace = ContactTrace(sim, names)
        _, edge, _ = next(iter(trace.top.values()))
        peak_x = float(sim.d.qpos[0])
        retreat = pitch = peak_speed = 0.
        consecutive = 0
        supported = False
        failed = False
        native_step = mj.mj_step

        def monitor(m, d):
            native_step(m, d)
            trace.add(m, d)

        mj.mj_step = monitor
        try:
            for k in range(165 if speed < .66 else 135):
                before = float(sim.d.time)
                sim.step({'w'})
                batch = np.asarray(trace.rows[-sim.env.decim:])
                peak_x = max(peak_x, float(batch[:, 1].max()))
                retreat = max(retreat, peak_x - float(batch[:, 1].min()))
                pitch = max(pitch, float(np.abs(batch[:, 7]).max()))
                peak_speed = max(peak_speed, float(np.linalg.norm(batch[:, 4:6], axis=1).max()))
                failed = (sim.d.time < before or pitch > 45. or sim.d.qpos[2] < .13)
                if failed:
                    break
                good = (batch[:, 13:15].mean(0) >= 5.).all() and batch[-1, 10] > edge + .004
                consecutive = consecutive + 1 if good else 0
                if consecutive >= 20:
                    supported = True
                    break
        finally:
            mj.mj_step = native_step
        lateral = float(abs(sim.d.qpos[1]))
        quality = 8.0 * supported - 19. * retreat - .055 * max(0., pitch - 12.)
        quality -= 5. * failed + .003 * (k + 1) + .4 * lateral
        if speed < .66:
            quality -= 1.8 * max(0., peak_speed - .60)**2
        metrics.append({'offset_m': offset, 'held': bool(supported), 'fell': bool(failed), 'backtrack_m': retreat,
                        'pitch_deg': pitch, 'postimpact_peak_speed_m_s': peak_speed, 'quality': float(quality)})
    vals = np.asarray([r['quality'] for r in metrics])
    return float(vals.mean() + .4 * vals.min()), metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--height', type=float, default=.32)
    parser.add_argument('--speed', type=float, default=.90)
    parser.add_argument('--offsets', type=float, nargs='+', default=[-.03, 0., .03])
    parser.add_argument('--slow-expert', action='store_true')
    parser.add_argument('--generations', type=int, default=3)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(3192)
    results = []
    center = np.zeros(5)
    spread = np.array([.10, .12, .16, .22, .14]) * (1.8 if args.slow_expert else 1.)
    inputs = (args.candidate, args.height, args.speed, args.offsets, args.slow_expert)
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize, initargs=inputs) as workers:
        for generation in range(args.generations):
            proposals = [center, *np.clip(rng.normal(center, spread, (18, 5)), -.65, .65)]
            for gains, (value, metrics) in zip(proposals, workers.map(score, proposals), strict=True):
                results.append({'generation': generation, 'bias_delta': list(gains), 'score': value, 'metrics': metrics})
            results.sort(key=lambda r: r['score'], reverse=True)
            top = np.array([r['bias_delta'] for r in results[:6]])
            center = top.mean(0)
            spread = np.maximum(.035, .90 * top.std(0))
            (args.out/'FIT.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n', encoding='utf8')
            print(results[0], flush=True)
    info, paths = read_candidate(args.candidate)
    expert_field = f'stair_height_{args.height:.3f}'
    if args.slow_expert:
        expert_field = 'slow_stair'
        parent = paths[expert_field]
    else:
        bank_path = paths['stair_height_bank']
        plan = json.loads(bank_path.read_text(encoding='utf8'))
        row = next(row for row in plan if abs(row['height_m'] - args.height) < 1.e-6)
        parent = (bank_path.parent / row['path']).resolve()
    old = torch.load(parent, weights_only=True, map_location='cpu')
    key = 'e1_stair.head.9.bias'
    weights = old['moe_state_dict']
    if key not in weights:
        key = next(k for k, v in weights.items() if k.startswith('e1_stair.head.') and v.shape == (8,))
    weights[key] = weights[key] + weights[key].new_tensor(expanded(results[0]['bias_delta']))
    torch.save({'moe_state_dict': weights, 'parent_sha': info['sha256'][expert_field],
                'bias_delta': results[0]['bias_delta']}, args.out / 'model_fit.pt')


if __name__ == '__main__':
    main()
