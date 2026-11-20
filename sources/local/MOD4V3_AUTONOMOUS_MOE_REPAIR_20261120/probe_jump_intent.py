# SPDX-License-Identifier: MIT
"""Replay a jump hotkey on the same tick as release, reverse, or renewed W."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mujoco as mj
import numpy as np
import torch

from play_repaired import RepairedSimulation, load_manifest
from verify_wasd import Case, ContactTrace, load_case


def run(sim, height, profile):
    names = load_case(sim, Case(profile, target=height, mode='jump_idle'))
    trace = ContactTrace(sim, names)
    original_step = mj.mj_step
    sim_ticks = []
    key_tick = 53
    requested = None

    def collect(model, data):
        original_step(model, data)
        trace.add(model, data)

    mj.mj_step = collect
    try:
        for tick in range(225):
            if 20 <= tick < key_tick or profile == 'reverse_held' and key_tick <= tick < 78:
                keys = {'s'}
            elif profile == 'forward_after_reverse' and tick >= key_tick:
                keys = {'w'}
            else:
                keys = set()
            if tick == key_tick:
                requested = sim.request_jump()
            sim.step(keys)
            sim_ticks.append([tick * .02, sim.cmd_vx, sim.route['e2'], float('s' in keys), float('w' in keys)])
    finally:
        mj.mj_step = original_step
    control, physics = np.asarray(sim_ticks), np.asarray(trace.rows)
    airborne = (physics[:, 9] > .018) & (physics[:, 11:13] <= 2.).all(1)
    first_e2 = np.flatnonzero(control[:, 2] > .5)
    active = (physics[:, 0] >= control[first_e2[0], 0] - 1e-6) if len(first_e2) else np.zeros(len(physics), bool)
    main_height = 0.
    # Ignore brief toe-off and settle oscillations.
    same_flight = np.flatnonzero(np.diff(np.r_[False, active & airborne, False]))
    for start, end in zip(same_flight[::2], same_flight[1::2], strict=True):
        if end - start >= 48:
            main_height = max(main_height, float(physics[start:end, 9].max()))
    track = physics[active, 1]
    return dict(height_m=height, profile=profile, key_accepted=requested,
                cmd_before_key_m_s=float(control[key_tick-1, 1]),
                first_e2_delay_s=float(control[first_e2[0],0] - key_tick*.02) if len(first_e2) else None,
                backwards_during_jump_m=float((np.maximum.accumulate(track) - track).max()) if len(track) else 0.,
                e2_ticks_with_reverse=int(np.count_nonzero((control[:,2] > .5) & (control[:,3] > .5))),
                main_clearance_m=main_height, fell=bool(physics[:,3].min() < .13 or np.abs(physics[:,7]).max() > 44.))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    policy, _, prepare = load_manifest(args.candidate)
    sim = RepairedSimulation(policy, policy.runtime_sha, show_viewer=False, jump_stance_prep=prepare)
    results = [run(sim, h, profile) for h in (.28,.42)
               for profile in ('reverse_release', 'reverse_held', 'forward_after_reverse')]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({'runtime_sha256':policy.runtime_sha, 'results':results}, indent=2)+'\n', encoding='utf8')
    for row in results:
        print(row)


if __name__ == '__main__':
    main()
