# SPDX-License-Identifier: MIT
"""Compare high-stance jump checkpoints in the actual WASD player."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

import probe_jump_prepare as player
from play_repaired import load_jump_expert
from verify_wasd import Case, run_case


def cases_for_screen(held=False):
    step = [Case(f'step_{index}', target=height, speed=speed, yaw=yaw, offset=offset,
                 mode='jump_step', duration=5., jump_distance_m=distance)
            for index, (height, speed, yaw, offset, distance) in enumerate([
                (.36, .92, 2., -.03, .66), (.42, .90, 0., 0., .66), (.42, .83, 0., .03, .66),
                (.38, .95, -2., -.035, .66), (.42, 1.01, 3., .02, .66),
                (.35, .90, 0., -.02, .61), (.39, .87, 0., .02, .71), (.415, .96, -2., -.05, .63),
            ])]
    flat = [Case(f'flat_{round(height*1000)}', target=height, speed=speed, mode='jump_moving', duration=5.)
            for height, speed in ((.36,.9),(.40,.90),(.42,.9))]
    if held:
        step += [Case(f'held_step_{index}', target=height, speed=speed, yaw=yaw, offset=offset,
                      mode='jump_step', duration=5.8, drive_at_s=wait, jump_distance_m=distance)
                 for index, (height, speed, yaw, offset, wait, distance) in enumerate([
                     (.34, .85, -3.5, .03, 1.30, .65), (.38, .91, 4., .065, 1.25, .63),
                     (.42, .89, -3., -.04, 1.45, .70), (.42, .98, 1.5, .025, 1.30, .62),
                     (.42, .84, -1.8, -.06, 1.40, .59), (.36, .95, 0., -.012, 1.15, .72),
                 ])]
        step.append(Case('low_standard_step', mode='jump_step', duration=5.))
        flat.extend([Case('low_standard_flat', mode='jump_moving', duration=5.),
                     Case('tall_stationary', target=.42, mode='jump_idle', duration=5.)])
    return step + flat


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
    direct_step = None
    peak_e1_to_hold = None
    face_before_takeoff = None
    if step is not None:
        first_dual = step['first_dual_support_s']
        hold = step['first_held_from_s']
        if hold is not None:
            verify = (control[:, 0] >= jump['requested_at_s'] - 1.e-6) & (control[:, 0] <= hold + .40 + 1.e-6)
            peak_e1_to_hold = float(control[verify, 5].max(initial=0.))
        face = step['hit']
        takeoff = None if principal is None else jump['requested_at_s'] + principal['from_key_s']
        face_before_takeoff = takeoff is not None and face is not None and face['t'] < takeoff
        # A later period of stable E0 support is allowed. E2 must land both
        # tires while active, and E1 must contribute nothing before the hold.
        direct_step = bool(physical_pass and takeoff is not None and first_dual is not None and
                           takeoff < first_dual <= float(last) + .02001 and
                           peak_e1_to_hold is not None and peak_e1_to_hold <= 1.e-6)
    return dict(e2_from_key_s=float(start - jump['requested_at_s']), events=events, principal=principal,
                physical_step_pass=physical_pass, direct_step_pass=direct_step,
                peak_e1_until_stable_hold=peak_e1_to_hold, face_before_takeoff=face_before_takeoff)


def initialize(manifest, landing_guard=0):
    player.initialize(manifest, None)
    if not landing_guard:
        return
    actor = player.SIM.unified
    original = actor.act

    def act(obs):
        permit = actor.allow_stair
        if obs[30] < .5 and any(row[30] > .5 for row in list(actor.restart_history)[-landing_guard:]):
            actor.allow_stair = False
        try:
            return original(obs)
        finally:
            actor.allow_stair = permit

    actor.act = act


@lru_cache(maxsize=1)
def load_moving(checkpoint):
    saved = torch.load(checkpoint, map_location='cpu', weights_only=True)
    return load_jump_expert(saved, player.SIM.unified.stair.e0.state_dict())


def execute(job):
    case, output, checkpoint = job
    actor = player.SIM.unified
    old = actor.high_moving_jump, actor.high_moving_jump_history_frames, actor.high_moving_jump_frames
    if checkpoint is not None:
        if old[0] is None:
            raise ValueError('Supply a manifest with high_moving_jump enabled before comparing its checkpoints')
        (actor.high_moving_jump, actor.high_moving_jump_history_frames,
         actor.high_moving_jump_frames) = load_moving(checkpoint)
    try:
        row = run_case(player.SIM, case, output)
        evidence = flight_evidence(row, output / f'{case.name}.npz')
        if case.target >= .32 and case.mode in ('jump_step', 'jump_moving') and actor.high_moving_jump is not None:
            if not actor.use_high_moving_jump:
                raise RuntimeError(f'{case.name} did not select the high-stance jump checkpoint')
        return row | {'flight': evidence}
    finally:
        (actor.high_moving_jump, actor.high_moving_jump_history_frames,
         actor.high_moving_jump_frames) = old


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--landing-guard-frames', type=int, default=0)
    parser.add_argument('--held', action='store_true')
    parser.add_argument('checkpoint', type=Path, nargs='*')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    summaries = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(), args.landing_guard_frames)) as pool:
        for index, file in enumerate((None, *args.checkpoint)):
            folder = args.out / f'{index:02d}_{file.stem if file else "player"}'
            folder.mkdir()
            rows = list(pool.map(execute, [(case, folder, file.resolve() if file else None) for case in cases_for_screen(args.held)]))
            summaries.append({'checkpoint': str(file.resolve()) if file else None,
                              'checkpoint_sha256': hashlib.sha256(file.read_bytes()).hexdigest() if file else None,
                              'results': rows})
            (args.out / 'RESULTS.json').write_text(json.dumps(summaries, indent=2, allow_nan=False)+'\n', encoding='utf8')
            print(None if file is None else file.name,
                  [(r['name'], r['flight']['direct_step_pass'], round(r['jump']['max_backtrack_m'],3),
                    round((r['flight']['principal'] or {}).get('rim_peak_m',0.),3),
                    round(r['jump']['landing_peak_pitch_deg'] or 0.,1), r['fell']) for r in rows], flush=True)


if __name__ == '__main__':
    main()
