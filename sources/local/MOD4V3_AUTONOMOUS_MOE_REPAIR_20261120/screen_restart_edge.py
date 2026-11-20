# SPDX-License-Identifier: MIT
"""Measure a learned parked-restart replacement in the exact WASD plant."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import torch

import verify_driving_grid as grid
from probe_retake_model import profiles
from restart_router import RestartSkillRouter
from verify_wasd import Case, run_case


ROUTER = None


def initialize(manifest, checkpoint):
    global ROUTER
    grid.initialize(manifest)
    ROUTER = RestartSkillRouter().eval().requires_grad_(False)
    raw = torch.load(checkpoint, map_location='cpu', weights_only=True)
    ROUTER.load_state_dict(raw['state_dict'])


def evaluate(job):
    case, setting, *trace_dir = job
    policy = grid.SIM.unified
    original = policy.parked_restart_outputs

    def evaluate_restart(height, baseline):
        upper, amount, threshold, correction_gain = setting
        influence = amount * float(np.clip((upper - height) / .020, 0., 1.))
        if influence == 0. or any(float(row[0]) < -.10 for row in list(policy.restart_history)[-104:]):
            return original(height, baseline)
        last_context, last_mix, last_delta = original(height, baseline)
        context, probability, residual = ROUTER.evaluate(policy.restart_history)
        mix = float(np.clip(.5 + (probability - threshold) / .10, 0., 1.))
        return ((1. - influence) * last_context + influence * context,
                (1. - influence) * last_mix + influence * mix,
                (1. - influence) * last_delta + influence * correction_gain * residual)

    config = setting if isinstance(setting, tuple) and len(setting) == 3 else None
    prior = policy.restart_release_per_tick

    def evaluate_calibration(height, baseline):
        low_shape, front, rear, wheel, mid_blend, mid_threshold, mid_rate, *park_guard = setting
        last_context, last_mix, last_delta = original(height, baseline)
        history = policy.restart_history
        if any(float(row[0]) < -.10 for row in list(history)[-104:]):
            return last_context, last_mix, last_delta
        low = float(np.clip((.307 - height) / .020, 0., 1.))
        if low > 0.:
            if park_guard:
                cutoff = park_guard[0]
                samples = [obs[20:22] for obs in list(history)[-20:] if abs(obs[0]) < .08][-7:]
                rolling = abs(float(np.mean(samples))) * .625 if samples else cutoff
                low *= float(np.clip((cutoff - rolling) / .04, 0., 1.))
            drive = float(np.clip(history[-1][0] / policy.stair_driver_speed, 0., 1.))
            early = np.clip((.86 - drive) / .68, 0., 1.)
            last_mix *= (1. - low * low_shape * early)
            last_delta = last_delta + low * early * np.array([front, rear, wheel], dtype=np.float32)
        mid = mid_blend * max(0., 1. - abs(height - .34) / .012)
        if mid > 0.:
            context, probability, delta = ROUTER.evaluate(history)
            gate = float(np.clip(.5 + (probability - mid_threshold) / .10, 0., 1.))
            last_context = (1. - mid) * last_context + mid * context
            last_mix = (1. - mid) * last_mix + mid * gate
            last_delta = (1. - mid) * last_delta + .75 * mid * delta
        taper = max(0., 1. - abs(height - .34) / .010)
        policy.restart_release_per_tick = (1. - taper) * prior + taper * mid_rate
        return last_context, last_mix, last_delta

    def evaluate_ramp(height, baseline):
        ready, rate, widen = config
        context, mix, delta = original(height, baseline)
        if height <= .30:
            commanded = float(policy.restart_history[-1][0])
            fraction = commanded / policy.stair_driver_speed
            ramp = float(np.clip((fraction - ready) / .12, 0., 1.))
            mix *= ramp
            delta = delta * ramp
        if .324 <= height <= .350 and widen:
            raw_context, raw_prob, _ = policy.parked_recovery_router.evaluate(policy.restart_history)
            activation = float(np.clip(.5 + (raw_prob - .72) / .10, 0., 1.))
            if not any(float(row[0]) < -.10 for row in list(policy.restart_history)[-104:]):
                fraction = float(np.clip((.350 - height) / .010, 0., 1.))
                context = (1. - fraction) * context + fraction * raw_context
                mix = (1. - fraction) * mix + fraction * activation
        policy.restart_release_per_tick = rate if .324 <= height <= .350 else prior
        return context, mix, delta

    if setting is not None and len(setting) >= 7:
        policy.parked_restart_outputs = evaluate_calibration
    elif config is not None:
        policy.parked_restart_outputs = evaluate_ramp
    elif setting is not None:
        policy.parked_restart_outputs = evaluate_restart
    try:
        row = run_case(grid.SIM, case, trace_dir[0] if trace_dir else None)
        return row | {'case': vars(case)}
    finally:
        policy.parked_restart_outputs = original
        policy.restart_release_per_tick = prior


def search_settings(pool, args, cases):
    train = []
    for name in ('restart_stop_h28', 'stop_repeat_h28_x-45', 'stop_repeat_h28_x+45',
                 'stop_repeat_h34_x-45', 'stop_repeat_h34_x+45', 'stop_repeat_h34_x-45_wall',
                 'stop_repeat_h34_x+45_wall', 'stop_repeat_h32_x+45'):
        train.append(next(c for c in cases if c.name == name))
    generator = np.random.default_rng(20261120)
    default = np.array([0., 0., 0., 0., 0., .76, .19])
    center = np.array([.5, 0., 0., 0., .44, .76, .13])
    deviation = np.array([.27, .35, .43, .35, .30, .05, .05])
    lower = [0., -.9, -1.1, -.85, 0., .68, .06]
    upper = [1., .9, 1.1, .85, 1., .88, .24]
    ranked = []
    for generation in range(3):
        samples = [default, center] + list(np.clip(generator.normal(center, deviation, (12, len(center))), lower, upper))
        jobs = [(case, tuple(params)) for params in samples for case in train]
        outputs = list(pool.map(evaluate, jobs))
        for index, sample in enumerate(samples):
            rows = outputs[index * len(train):(index + 1) * len(train)]
            score = 0.
            for row in rows:
                step = row['steps'][0]
                restart = row.get('restart') or {}
                score -= 8. * bool(row['fell']) + 4. * bool(step['slid_back'])
                score -= 3.5 * min(1., restart.get('backtrack_m', 1.))
                if row['case']['map_height'] > 20:
                    score -= 7. * restart.get('peak_e1_after_one_s', 1.)
                else:
                    held = step['both_top_s']
                    score += 5. * (held >= .40 and not row['fell'] and not step['slid_back'])
                    score += .8 * min(.4, held)
            ranked.append({'setting': sample.tolist(), 'score': score, 'results': rows})
        ranked.sort(key=lambda item: item['score'], reverse=True)
        elite = np.asarray([row['setting'] for row in ranked[:5]])
        center = elite.mean(0)
        deviation = np.maximum(deviation * .58, elite.std(0))
        (args.out / 'SEARCH.json').write_text(json.dumps(ranked, indent=2, allow_nan=False)+'\n', encoding='utf8')
        print(generation, ranked[0]['score'], ranked[0]['setting'], flush=True)
    return [None] + [tuple(row['setting']) for row in ranked[:4]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--checkpoint', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--ramp', action='store_true', help='Test forward-command slew before park takeover.')
    parser.add_argument('--optimize', action='store_true', help='Tune restart calibration in closed-loop MuJoCo.')
    parser.add_argument('--selective', type=Path, help='Replay an existing closed-loop calibration with a neutral rolling check.')
    args = parser.parse_args()
    cases = [case for case in profiles('held') if case.target <= .36]
    paired = [c for c in cases if c.name.startswith(('stop_repeat_h28', 'stop_repeat_h34'))]
    cases += [replace(case, name=case.name+'_wall', map_height=45 + 5 * (i % 2), duration=6.5)
              for i, case in enumerate(paired)]
    # Include the two opposite endpoints at an ordinary, uninterrupted approach.
    cases += [c for c in grid.held_profiles() if c.mode == 'climb' and c.target == .36][:2]
    if args.optimize or args.selective:
        cases += [Case(f'novel_park_h{int(h*100):02}_{index}', target=h, speed=s, yaw=yaw, offset=x, mode='stop',
                       duration=8.4, cancel_delay_s=cancel, restart_delay_s=wait)
                  for h in (.28, .34) for index, (s, yaw, x, cancel, wait) in enumerate([
                      (.87, 2.8, -.055, .08, .91), (.96, -1.9, .042, .14, .67), (.91, 0., -.015, .09, 1.19)])]
    args.out.mkdir(parents=True, exist_ok=False)
    results = []
    settings = (None, (.35, .75, .76, .6), (.365, .75, .76, .6), (.365, 1., .76, .6),
                (.365, 1., .82, .6), (.365, 1., .72, 1.))
    if args.ramp:
        settings = ((.55, .19, False), (.67, .075, False), (.76, .11, False),
                    (.63, .12, True), (.73, .065, True))
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(), args.checkpoint.resolve())) as pool:
        if args.optimize:
            settings = search_settings(pool, args, cases)
        if args.selective:
            ranked = json.loads(args.selective.read_text(encoding='utf-8'))
            low = ranked[0]['setting'][:4]
            mid = ranked[1]['setting'][4:]
            settings = [None]
            for threshold in (.055, .085):
                settings += [tuple(low + [0., .76, .19, threshold]), tuple(low + mid + [threshold])]
        for setting in settings:
            rows = list(pool.map(evaluate, [(case, setting) for case in cases]))
            results.append({'settings': setting, 'results': rows})
            (args.out / 'RESULTS.json').write_text(json.dumps(results, allow_nan=False, indent=2)+'\n', encoding='utf8')
            print(setting, [(r['name'], r['fell'], r['steps'][0]['both_top_s'],
                             round((r.get('restart') or {}).get('backtrack_m', 0.), 3),
                             round((r.get('restart') or {}).get('peak_e1_after_one_s', 0.), 3))
                            for r in rows], flush=True)


if __name__ == '__main__':
    main()
