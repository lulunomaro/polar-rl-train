# SPDX-License-Identifier: MIT
"""Collect closed-loop corrections from a student and qualified stair teachers."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import json
from pathlib import Path

import torch
import numpy as np

from search_stair_demo import CaseSearch, Parameters


STUDENT = None


def collect(task):
    height, speed, offset, yaw, rise, references, checkpoint, output, mixes = task
    global STUDENT
    student = CaseSearch(height, speed, offset, yaw, rise=rise)
    if STUDENT is None:
        from autonomous_three_expert import stair
        STUDENT = stair.AutonomousStairMoE()
        weights = torch.load(checkpoint, map_location='cpu', weights_only=True)
        STUDENT.load_state_dict(weights['moe_state_dict'], strict=True)
        STUDENT.eval().requires_grad_(False)
    student.ctrl.student = STUDENT
    params = sorted(references, key=lambda info: 6. * abs(info['height_cmd'] - height)
                    + .2 * abs(info['speed'] - speed) + .003 * abs(info['yaw_deg'] - yaw)
                    + .15 * info['backtrack_m'])[:7]
    unique = {}
    for record in params:
        param = Parameters(**record['parameters'])
        unique[param] = None
    results = []
    for mix in mixes:
        student.ctrl.student_mix = mix
        best_param = None
        best_score = -float('inf')
        for param in unique:
            result = student.trial(param)
            # The low-stance floor allows the initial physical rebound, while all
            # teacher forward commands remain positive. Report its actual distance.
            retreat_limit = .103 if height < .30 else .075
            acceptable = (result['hold_frame'] is not None and result['backtrack_m'] <= retreat_limit
                          and not result['lost'] and result['pitch_peak_deg'] <= 30.)
            if acceptable and result['score'] > best_score:
                best_score = result['score']
                best_param = param
        if best_param is None:
            continue
        result, episode = student.trial(best_param, keep=True)
        name = f'h{round(100*height):02}_v{round(speed*100):02}_x{round(offset*1000):+04}_y{round(yaw):+03}_r{int(rise)}_m{round(100*mix):02}'
        summary = dict(**(result | {'qualified': True}), height_cmd=height, speed=speed,
                       offset_m=offset, yaw_deg=yaw, rise=rise, student_fraction=mix)
        (output / (name + '.json')).write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
        np.savez_compressed(output / (name + '.npz'), **episode)
        results.append(summary)
    return {'height_cmd': height, 'speed': speed, 'offset_m': offset, 'yaw_deg': yaw,
            'rise': rise, 'accepted': len(results), 'selected': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--student', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--heights', type=float, nargs='+', default=[.28, .36, .40, .42])
    parser.add_argument('--speeds', type=float, nargs='+', default=[.78, .90])
    parser.add_argument('--include-center', action='store_true')
    parser.add_argument('--mixes', type=float, nargs='+', default=[.18, .33, 0.])
    parser.add_argument('reference', type=Path, nargs='+')
    args = parser.parse_args()
    refs = []
    for result in args.reference:
        for row in json.loads(result.read_text(encoding='utf8')):
            if row['qualified'] or (row['height_cmd'] == .28 and row['hold_frame'] is not None
                                     and not row['lost'] and row['backtrack_m'] < .10):
                refs.append(row)
    pose = [(-.06, 0., False), (.06, 0., False), (-.03, 8., False), (.03, -8., False),
            (0., 0., True), (.045, 5., True), (-.045, -5., True)]
    if args.include_center:
        pose.insert(0, (0., 0., False))
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    tasks = [(*profile, refs, args.student.resolve(), output, args.mixes) for profile in
             [(h, v, x, y, r) for h in args.heights for v in args.speeds for x, y, r in pose]]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = []
        for record in pool.map(collect, tasks):
            results.append(record)
            print(json.dumps({k:v for k,v in record.items() if k != 'selected'}), flush=True)
            (output/'COLLECTION.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
