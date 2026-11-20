# SPDX-License-Identifier: MIT
"""Measure learned parked restart routing with the existing player."""
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
from probe_retake_model import profiles
from restart_router import RestartSkillRouter
from verify_wasd import run_case

SIM = None
ROUTER = None
SETUP = None


def initialize(manifest, checkpoint):
    global SIM, ROUTER
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'parked_screen_{os.getpid()}'
    model, _, prep = load_manifest(manifest)
    ROUTER = RestartSkillRouter().eval().requires_grad_(False)
    raw = torch.load(checkpoint, map_location='cpu', weights_only=True)
    ROUTER.load_state_dict(raw['state_dict'], strict=True)
    SIM = RepairedSimulation(model, model.runtime_sha, show_viewer=False, jump_stance_prep=prep)
    original = model.parked_restart_outputs
    incumbent = model.parked_restart_router.evaluate

    def with_router(height, baseline):
        if SETUP is None:
            return original(height, baseline)
        minimum, mix, residual = SETUP
        replace_weight = mix * float(np.clip((height - minimum) / .006, 0., 1.))
        if replace_weight <= 0.:
            return original(height, baseline)
        obs = model.restart_history
        old_context, old_probability, _ = incumbent(obs)
        context, probability, action = ROUTER.evaluate(obs)
        model.parked_restart_router.evaluate = lambda _hist: (old_context + replace_weight * (context - old_context),
                                                               old_probability + replace_weight * (probability - old_probability), action)
        try:
            context, probability, correction = original(height, baseline)
        finally:
            model.parked_restart_router.evaluate = incumbent
        if residual:
            parked_weight = float(np.clip((.35 - height) / .021, 0., 1.))
            recent_reverse = any(float(row[0]) < -.10 for row in list(obs)[-104:])
            if not recent_reverse:
                correction = correction + residual * parked_weight * replace_weight * action
        return context, probability, correction

    model.parked_restart_outputs = with_router


def test(job):
    global SETUP
    case, SETUP = job
    row = run_case(SIM, case, None)
    stair = row['steps'][0]
    return dict(name=case.name, map_height=case.map_height, fell=row['fell'],
                hold_s=stair['both_top_s'], slid=stair['slid_back'], peak_pitch_deg=row['peak_pitch_deg'],
                complete=stair['both_top_s'] >= .4 and not stair['slid_back'] and not row['fell'],
                restart=row.get('restart'), override=row.get('override'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = [case for case in profiles('held') if case.target < .35]
    # Same driving command and pose at the start, with 45/50 cm wall counterexamples.
    cases += [replace(case, name=f'{case.name}_wall', duration=6.5, map_height=height)
              for case,height in ((cases[0],45), (cases[2],50),
              (next(c for c in cases if c.name=='stop_repeat_h32_x-45'),45))]
    configs = [None, (.292, 1., 0.), (.292, 1., .6), (.265, 1., 1.), (.265, .65, .6), (.265, .5, 0.)]
    observations = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(), args.checkpoint.resolve())) as pool:
        for config in configs:
            result = list(pool.map(test, [(case, config) for case in cases]))
            observations.append({'config':config,'results':result})
            (args.out/'RESULTS.json').write_text(json.dumps(observations, indent=2, allow_nan=False)+'\n', encoding='utf8')
            print(config, [(r['name'],r['complete'],r['fell'],round((r['restart'] or {}).get('backtrack_m',0.),3),
                            round((r['restart'] or {}).get('peak_e1_after_one_s',0.),2)) for r in result], flush=True)


if __name__ == '__main__':
    main()
