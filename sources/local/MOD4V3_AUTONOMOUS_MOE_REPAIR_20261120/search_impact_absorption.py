# SPDX-License-Identifier: MIT
"""Search short impact responses in the original plant for reusable training demonstrations."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
from pathlib import Path

import numpy as np

from search_stair_demo import CaseSearch, Parameters


def search(job):
    height, speed, offset, yaw, count, ref, out = job
    r = np.random.default_rng(7419 + round(height * 1000) + round(speed * 100) + round(offset * 1000))
    trial = CaseSearch(height, speed, offset, yaw)
    bounds = np.array([[-2.2, -2.2, -2.4, .06], [2.2, 2.2, 2.4, .33]])
    starts = [Parameters(**params) for params in ref]
    best = None
    sampled = []
    for i in range(count):
        if i < len(starts):
            params = starts[i]
        else:
            span = .30 if i < count * .65 else .14
            if i % 4 == 0 or not sampled:
                origin = starts[i % len(starts)]
                impulses = r.uniform(*bounds)
            else:
                origin, _ = sampled[int(r.integers(min(len(sampled), 8)))]
                prior = np.array([origin.contact_front, origin.contact_rear,
                                  origin.contact_wheel, origin.contact_settle])
                impulses = np.clip(prior + r.normal(size=4) * (bounds[1] - bounds[0]) * span, *bounds)
            params = replace(origin, contact_front=impulses[0], contact_rear=impulses[1],
                             contact_wheel=impulses[2], contact_settle=impulses[3],
                             push_speed=float(np.clip(origin.push_speed + r.normal(scale=.12), .24, 1.65)))
        result = trial.trial(params)
        result['eligible'] = (bool(result['hold_frame']) and not result['lost'] and result['pitch_peak_deg'] <= 25.)
        result['rank'] = (int(result['eligible']), round(-result['backtrack_m'], 4), result['score'])
        sampled.append((params, result))
        sampled.sort(key=lambda it: it[1]['rank'], reverse=True)
        if best is None or result['rank'] > best[1]['rank']:
            best = params, result
    params, _ = best
    result, trace = trial.trial(params, keep=True)
    stem = f'h{round(height*100):02}_v{round(speed*100):02}_x{round(offset*1000):+04}_y{round(yaw):+03}'
    result |= {'height_cmd': height, 'speed': speed, 'offset_m': offset, 'yaw_deg': yaw, 'trials': count,
               'selected_from': 'trained teacher impact search'}
    np.savez_compressed(out / (stem + '.npz'), **trace)
    (out / (stem + '.json')).write_text(json.dumps(result | {'candidates': [x for _, x in sampled]}, indent=2) + '\n', encoding='utf8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--refs', required=True, type=Path)
    parser.add_argument('--trials', type=int, default=96)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--target', type=float, action='append', nargs=4, metavar=('H_M', 'VX', 'OFFSET_M', 'YAW_DEG'))
    args = parser.parse_args()
    data = json.loads(args.refs.read_text(encoding='utf8'))
    args.out.mkdir(parents=True, exist_ok=False)
    profiles = args.target or [(h, v, x, yaw) for h in (.28, .32, .36)
        for v, x, yaw in ((.90, 0., 0.), (.90, -.06, 0.), (.90, .06, 0.), (.66, -.03, 5.))]
    jobs = []
    for height, speed, offset, yaw in profiles:
        same_height = [entry for entry in data if entry['height_cmd'] == height and entry['hold_frame']]
        nearest = sorted((entry for entry in data if entry['hold_frame']), key=lambda entry:
                         8. * abs(entry['height_cmd'] - height) + .2 * abs(entry['speed'] - speed)
                         + .003 * abs(entry['yaw_deg'] - yaw))
        refs = [entry['parameters'] for entry in (same_height or nearest[:5])]
        if not refs:
            raise ValueError(f'No closed-loop references for {height=}')
        jobs.append((height, speed, offset, yaw, args.trials, refs, args.out.resolve()))
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as workers:
        for item in workers.map(search, jobs, chunksize=1):
            results.append(item)
            print({k: item[k] for k in ('height_cmd', 'speed', 'offset_m', 'backtrack_m', 'hold_frame')}, flush=True)
            (args.out / 'SEARCH.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
