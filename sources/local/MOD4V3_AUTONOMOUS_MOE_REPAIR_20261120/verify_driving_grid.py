# SPDX-License-Identifier: MIT
"""Run the driving cases that expose height-dependent routing and restart regressions."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path

from play_repaired import HERE, RepairedSimulation, load_manifest, maps, read_candidate
from verify_wasd import Case, run_case

SIM = None
RELEASE = None
PARK_THRESHOLD = None


def mid_stance_release(height, base, minimum):
    # A taper keeps the established low- and high-stance routes intact.
    effect = max(0., 1. - max(0., abs(height - .36) - .005) / .018)
    return base + effect * (minimum - base)


def initialize(manifest):
    global SIM, RELEASE, PARK_THRESHOLD
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'driving_grid_{os.getpid()}'
    policy, _, prep = load_manifest(manifest)
    SIM = RepairedSimulation(policy, policy.runtime_sha, show_viewer=False, jump_stance_prep=prep)
    RELEASE = policy.stair_release_per_tick
    PARK_THRESHOLD = getattr(policy, 'parked_restart_threshold', .76)


def execute(item):
    case, out, release, parked_threshold = item
    control = SIM.unified
    act = control.act
    parked = control.parked_restart_router

    def with_release(obs):
        control.stair_release_per_tick = mid_stance_release(float(obs[3]) / 5., RELEASE, release)
        return act(obs)

    if release is not None:
        control.act = with_release
    if parked_threshold is not None:
        # Keep the module registered and substitute only this worker's evaluation.
        orig_evaluate = parked.evaluate
        def calibrated(history):
            context, prob, delta = orig_evaluate(history)
            return context, prob + PARK_THRESHOLD - parked_threshold, delta
        parked.evaluate = calibrated
    try:
        result = run_case(SIM, case, out)
        return result | {'case': case.__dict__, 'mid_stance_release': release,
                         'parked_restart_threshold': parked_threshold}
    finally:
        control.act = act
        control.stair_release_per_tick = RELEASE
        if parked_threshold is not None:
            parked.evaluate = orig_evaluate


def held_profiles():
    cases = [Case(f'h{round(h * 100)}_offset{offset:+03}', target=h, offset=offset / 1000)
             for h in (.36, .40) for offset in (-60, -30, 0, 30, 60)]
    cases += [Case(f'rise_h42_offset{offset:+03}', target=.42, offset=offset / 1000, raise_while_moving=True)
              for offset in (-60, -30, 30, 60)]
    cases += [Case(f'stop_repeat_h{round(h * 100)}_x{mm:+03}', target=h, offset=mm / 1000,
                   speed=speed, mode='stop', duration=9., cancel_delay_s=.10, restart_delay_s=delay)
              for h in (.28, .31, .32, .34) for mm, speed, delay in ((-45, .88, .76), (45, .93, 1.04))]
    cases += [Case(f'wall45_h{round(h * 100)}', target=h, map_height=45, mode='wall', duration=5.)
              for h in (.28, .32, .36, .40, .42)]
    return cases


def profiles(suite):
    held = held_profiles()
    if suite == 'held':
        return held
    if suite == 'restart':
        return [case for case in held if case.mode in ('stop', 'wall') and case.target <= .34]
    if suite == 'mid':
        mid = [case for case in held if case.target == .36]
        return mid + [Case('rise_h36', target=.36, raise_while_moving=True),
                      Case('wall50_h36', target=.36, map_height=50, mode='wall', duration=5.),
                      Case('cancel_h36', target=.36, mode='stop', duration=5., cancel_delay_s=.63)]
    if suite == 'late-rise':
        return [Case(f'late_rise_h42_x{mm:+03}', target=.42, offset=mm / 1000,
                     raise_while_moving=True, raise_at_s=.95) for mm in (-60, -30, 0, 30, 60)]
    if suite == 'slow':
        return [Case(f'slow_h42_{mm:+03}', target=.42, speed=.47, offset=mm / 1000,
                     duration=10.) for mm in (-60, -30, 0, 30, 60)]
    raise ValueError(suite)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--suite', choices=('held', 'restart', 'mid', 'slow', 'late-rise'), default='held')
    parser.add_argument('--release', type=float, nargs='+')
    parser.add_argument('--park-threshold', type=float, nargs='+')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = profiles(args.suite)
    jobs = [(case, args.out.resolve() if release is None and park is None else None, release, park)
            for release in args.release or [None] for park in args.park_threshold or [None] for case in cases]
    manifest, _ = read_candidate(args.candidate)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(),)) as pool:
        for result in pool.map(execute, jobs):
            results.append(result)
            step = result['steps'][0]
            print(result['name'], result['mid_stance_release'], result['parked_restart_threshold'],
                  result['fell'], step['both_top_s'], round(step['backtrack_m'] or 0., 4),
                  result.get('wall_gate_after_one_second'), flush=True)
            (args.out / 'WASD.json').write_text(json.dumps({'candidate_manifest': str(args.candidate.resolve()),
                'runtime_sha256': manifest.get('runtime_sha256'), 'results': results}, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
