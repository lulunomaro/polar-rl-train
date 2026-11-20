# SPDX-License-Identifier: MIT
"""Fit parked restart calibration with the live WASD key sequence and wall controls."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
from pathlib import Path

import numpy as np

import screen_restart_edge as edge
import verify_driving_grid as grid
from verify_wasd import Case, restart_cases, run_case


# A small symmetric calibration fitted in r28; checked here on a parent with updated routing.
CALIBRATION = np.array([.5054901435, .2985283467, -.7631071286, .4708167033], np.float32)


def parked_w_strength(history, driver_speed, cutoff):
    if driver_speed is None or driver_speed <= .1:
        return 0.
    observations = np.asarray(list(history))
    fraction = float(observations[-1, 0]) / driver_speed
    if not 0. < fraction < .86:
        return 0.
    stationary = np.flatnonzero(np.abs(observations[:, 0]) <= .04)
    if stationary.size == 0:
        return 0.
    stop = stationary[-1] + 1
    if (stop < 13 or len(observations) - stop > 18
            or np.any(np.abs(observations[stop - 12:stop, 0]) > .04)
            or not np.any(observations[:stop - 12, 0] > .32)):
        return 0.
    wheel_speed = float(np.sqrt(np.mean(observations[stop - 7:stop, 20:22] ** 2))) * .625
    steady = float(np.clip((cutoff - wheel_speed) / .04, 0., 1.))
    return steady * float(np.clip((.86 - fraction) / .68, 0., 1.))


def execute(job):
    case, settings, output = job
    if settings is None:
        return edge.evaluate((case, None, output) if output else (case, None))
    cutoff, steering, transition, mid, scale = settings
    policy = grid.SIM.unified
    original = policy.parked_restart_outputs
    release = policy.restart_release_per_tick

    def parked(height, baseline):
        context, mix, action = original(height, baseline)
        history = policy.restart_history
        if any(float(row[0]) < -.10 for row in list(history)[-104:]):
            return context, mix, action
        scope = float(np.clip((.308 - height) / .024, 0., 1.))
        correction = scope * parked_w_strength(history, policy.stair_driver_speed, cutoff) if scope > 0. else 0.
        if correction > 0.:
            # NumPy's float32 promotion can change an otherwise untouched gate.
            # The original outputs must be returned verbatim outside the correction scope.
            mix *= 1. - steering * float(CALIBRATION[0]) * correction
            action = action + correction * CALIBRATION[1:] * scale
        if mid > 0.:
            weight = mid * max(0., 1. - abs(height - .34) / .012)
            if weight > 0.:
                learned_context, prob, delta = edge.ROUTER.evaluate(history)
                context += weight * (learned_context - context)
                mix += weight * (float(np.clip(.5 + (prob - .791) / .10, 0., 1.)) - mix)
                action += weight * (.75 * delta - action)
                policy.restart_release_per_tick = release + weight / mid * (transition - release)
            else:
                policy.restart_release_per_tick = release

        return context, mix, action

    policy.parked_restart_outputs = parked
    try:
        return run_case(grid.SIM, case, output)
    finally:
        policy.parked_restart_outputs = original
        policy.restart_release_per_tick = release


def profiles(held=False):
    parked = [c for c in grid.held_profiles() if c.mode == 'stop']
    corners = [c for c in parked if c.target in (.28, .34)]
    base = [c for c in restart_cases() if c.name in ('restart_stop_h28', 'restart_wall_h28')]
    novel = [Case(f'novel_park_h28_{index}', target=.28, speed=s, yaw=yaw, offset=x, mode='stop',
                  duration=8.4, cancel_delay_s=cancel, restart_delay_s=wait)
             for index, (s,yaw,x,cancel,wait) in enumerate([(.87,2.8,-.055,.08,.91),
                     (.96,-1.9,.042,.14,.67),(.91,0.,-.015,.09,1.19)])]
    if not held:
        return corners + base + novel
    new_parked = [replace(c, name=c.name.replace('stop_repeat', 'park_holdout'), offset=c.offset * -.78,
                          speed=c.speed + .037, cancel_delay_s=c.cancel_delay_s + .018,
                          restart_delay_s=c.restart_delay_s + .095, yaw=(-3.5 if c.offset < 0 else 3.5)) for c in corners]
    walls = [replace(c, name=c.name+'_wall', map_height=45+5*(i%2), duration=7.0) for i, c in enumerate(corners)]
    return parked + novel + new_parked + walls + restart_cases() + [
        Case('approach_h28', target=.28), Case('approach_h34', target=.34),
        Case('approach_h42', target=.42), Case('late_rise_h42', target=.42, raise_while_moving=True, raise_at_s=.95),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--router', type=Path)
    parser.add_argument('--manifest-settings', action='store_true')
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--workers', default=2, type=int)
    parser.add_argument('--held', action='store_true')
    parser.add_argument('--config', type=float, nargs=5, action='append', dest='configs')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = profiles(args.held)
    configs = args.configs or [(.102,1.,.085,.414,1.), (.116,1.,.085,.414,1.), (.090,1.1,.085,.414,1.3),
                               (.110,.8,.085,.414,1.15), (.104,.95,.19,0.,1.35), (.095,1.2,.085,.414,1.25)]
    if args.manifest_settings:
        init, initargs, options = grid.initialize, (args.candidate.resolve(),), [None]
    else:
        if args.router is None:
            parser.error('--router is required when screening a calibration')
        init, initargs, options = edge.initialize, (args.candidate.resolve(), args.router.resolve()), [None, *configs]
    compare = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init, initargs=initargs) as pool:
        for index, config in enumerate(options):
            directory = None
            if args.held:
                directory = args.out / f'config_{index:02}'
                directory.mkdir()
            rows = list(pool.map(execute, [(case, config, directory) for case in cases]))
            compare.append({'config':config, 'cases':[vars(case) for case in cases], 'results': rows})
            (args.out/'RESULTS.json').write_text(json.dumps(compare, indent=2, allow_nan=False)+'\n',encoding='utf8')
            print(config, [(r['name'], r['steps'][0]['both_top_s'] >= .4 and not r['steps'][0]['slid_back'] and not r['fell'],
                           r['fell'], round((r.get('restart') or {}).get('backtrack_m',0.), 3)) for r in rows], flush=True)


if __name__ == '__main__':
    main()
