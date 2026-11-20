# SPDX-License-Identifier: MIT
"""Compare high-stance jump checkpoints in the actual WASD player."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import json
from pathlib import Path

import numpy as np
import torch

import probe_jump_prepare as player
from play_repaired import load_jump_expert
from verify_wasd import Case


def cases_for_screen():
    step = [Case(f'step_{index}', target=height, speed=speed, yaw=yaw, offset=offset,
                 mode='jump_step', duration=5., jump_distance_m=distance)
            for index, (height, speed, yaw, offset, distance) in enumerate([
                (.36, .92, 2., -.03, .66), (.42, .90, 0., 0., .66), (.42, .83, 0., .03, .66),
                (.38, .95, -2., -.035, .66), (.42, 1.01, 3., .02, .66),
                (.35, .90, 0., -.02, .61), (.39, .87, 0., .02, .71), (.415, .96, -2., -.05, .63),
            ])]
    return step + [Case(f'flat_{round(height*1000)}', target=height, speed=speed, mode='jump_moving', duration=5.)
                   for height, speed in ((.36,.9),(.40,.90),(.42,.9))]


def flight_evidence(row, path):
    with np.load(path, allow_pickle=False) as saved:
        physical, control = saved['physical'], saved['control']
    jump = row['jump']
    start, last = control[control[:, 6] > .5, 0][[0, -1]]
    flight_samples = physical[(physical[:, 0] >= start - 1.e-6) & (physical[:, 0] <= last + .02001)]
    timestep = float(np.median(np.diff(physical[:, 0])))
    clear_air = (flight_samples[:, 9] > .018) & (flight_samples[:, 11:13] <= 2.).all(1)
    delimiters = np.flatnonzero(np.diff(np.r_[False, clear_air, False]))
    events = []
    for begin, end in zip(delimiters[::2], delimiters[1::2], strict=True):
        segment = flight_samples[begin:end]
        duration = len(segment) * timestep
        if duration < .014:
            continue
        events.append(dict(from_key_s=float(segment[0, 0]) - jump['requested_at_s'], duration_s=duration,
                           rim_peak_m=float(segment[:, 9].max()), departure_vx_m_s=float(segment[0, 4]),
                           pitch_deg=float(np.abs(segment[:, 7]).max())))
    principal = max((event for event in events if event['duration_s'] >= .12),
                    key=lambda event: event['rim_peak_m'], default=None)
    step = row['steps'][0] if row['steps'] else None
    physical_pass = (step['both_top_s'] >= .4 and not step['slid_back'] and not row['fell']) if step else None
    direct_step = (physical_pass and step['first_held_from_s'] is not None
                   and step['first_held_from_s'] <= float(last) + .12) if step else None
    return dict(e2_from_key_s=float(start - jump['requested_at_s']), events=events, principal=principal,
                physical_step_pass=physical_pass, direct_step_pass=direct_step)


def initialize(manifest):
    player.initialize(manifest, None)


@lru_cache(maxsize=1)
def load_moving(checkpoint):
    saved = torch.load(checkpoint, map_location='cpu', weights_only=True)
    return load_jump_expert(saved, player.SIM.unified.stair.e0.state_dict())


def execute(job):
    case, output, checkpoint = job
    actor = player.SIM.unified
    old = actor.moving_jump, actor.moving_jump_history_frames, actor.moving_jump_frames
    if checkpoint is not None:
        actor.moving_jump, actor.moving_jump_history_frames, actor.moving_jump_frames = load_moving(checkpoint)
    try:
        row = player.trial((case, 'direct' if checkpoint else None, output))
        return row | {'flight': flight_evidence(row, output / f'{case.name}.npz')}
    finally:
        actor.moving_jump, actor.moving_jump_history_frames, actor.moving_jump_frames = old


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('checkpoint', type=Path, nargs='+')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    summaries = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(),)) as pool:
        for index, file in enumerate((None, *args.checkpoint)):
            folder = args.out / f'{index:02d}_{file.stem if file else "player"}'
            folder.mkdir()
            rows = list(pool.map(execute, [(case, folder, file.resolve() if file else None) for case in cases_for_screen()]))
            summaries.append({'checkpoint': str(file) if file else None, 'results': rows})
            (args.out / 'RESULTS.json').write_text(json.dumps(summaries, indent=2, allow_nan=False)+'\n', encoding='utf8')
            print(None if file is None else file.name,
                  [(r['name'], r['flight']['direct_step_pass'], round(r['jump']['max_backtrack_m'],3),
                    round((r['flight']['principal'] or {}).get('rim_peak_m',0.),3),
                    round(r['jump']['landing_peak_pitch_deg'] or 0.,1), r['fell']) for r in rows], flush=True)


if __name__ == '__main__':
    main()
