# SPDX-License-Identifier: MIT
"""Closed-loop calibration of learned parked-restart routing on the WASD plant."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path

import numpy as np
import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, maps
from restart_router import RestartSkillRouter
from verify_wasd import restart_cases, run_case

SIM = None
CALIBRATION = None


def initialize(manifest, low_mixed, low_stopped):
    global SIM
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'parked_restart_{os.getpid()}'
    policy, hashes, prep = load_manifest(manifest)
    simulators = []
    for model_path in (low_mixed, low_stopped):
        model = RestartSkillRouter().eval()
        model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True)['state_dict'])
        simulators.append(model)
    native = policy.restart_outputs

    def calibrated(router):
        baseline = native(router)
        if router is not policy.restart_router:
            return baseline
        history = list(policy.restart_history)
        height = float(history[-1][3]) / 5.
        scope = float(np.clip((.35 - height) / .021, 0., 1.))
        if not scope or any(float(x[0]) < -.10 for x in history[-104:]):
            return baseline
        config = CALIBRATION
        model = simulators[int(height > config['split_height'])]
        context, probability, residual = model.evaluate(history)
        if config['probability_band'] > 0.:
            width = config['probability_band']
            active = (probability - config['probability_threshold']) / width
            probability = float(np.clip(.5 + active, 0., 1.))
        residual = config['residual_scale'] * residual
        return tuple(a + scope * (b - a) for a, b in zip(baseline, (context, probability, residual), strict=True))

    policy.restart_outputs = calibrated
    SIM = RepairedSimulation(policy, hashes['package'], show_viewer=False, jump_stance_prep=prep)


def evaluate(item):
    global CALIBRATION
    profile, CALIBRATION = item
    return run_case(SIM, profile, None) | {'calibration': CALIBRATION}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    profiles = [c for c in restart_cases() if c.name in ('restart_stop_h28', 'restart_stop_h32', 'restart_wall_h28')]
    profiles += [replace(profiles[1], name='restart_wall_h32', mode='stop', map_height=50, duration=6.5)]
    configurations = [dict(zip(('split_height', 'probability_band', 'probability_threshold', 'residual_scale'), values, strict=True))
                      for values in ((.30, .0, .55, 1.), (.30, .24, .55, 1.), (.30, .12, .62, 1.),
                                     (.30, .08, .64, 0.), (.30, .05, .71, 0.), (.34, .20, .61, 1.),
                                     (.34, .10, .76, 0.), (.30, .18, .51, .5), (.30, .12, .54, 0.))]
    records = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(), HERE / 'evidence/r14/restart_skill/restart_skill.pt',
                                       HERE / 'evidence/r14/stop_only_skill/restart_skill.pt')) as pool:
        for r in pool.map(evaluate, [(p, cfg) for cfg in configurations for p in profiles]):
            records.append(r)
            if len(records) % len(profiles) == 0:
                print(r['calibration'], [(z['name'], z['steps'][0]['both_top_s'], z['fell'],
                                           round(z['restart']['backtrack_m'], 3), round(z['restart']['peak_e1_after_one_s'], 2))
                                          for z in records[-len(profiles):]], flush=True)
                args.out.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
