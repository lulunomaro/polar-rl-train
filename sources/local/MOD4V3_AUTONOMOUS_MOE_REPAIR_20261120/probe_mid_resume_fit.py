# SPDX-License-Identifier: MIT
"""Screen the learned mid-stance restart gate on held-out WASD pauses and walls."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path

import numpy as np
import torch

import verify_driving_grid as grid
from restart_router import RestartSkillRouter
from screen_neutral_restart import profiles
from verify_wasd import run_case

ROUTER = None


def initialize(candidate, weight):
    global ROUTER
    torch.set_num_threads(1)
    grid.initialize(candidate)
    state = torch.load(weight, map_location='cpu', weights_only=True)
    ROUTER = RestartSkillRouter()
    ROUTER.load_state_dict(state['state_dict'], strict=True)
    ROUTER.eval().requires_grad_(False)


def evaluate(job):
    case, strength = job
    policy = grid.SIM.unified
    original = policy.adjust_parked_resume

    def adjust(height, outputs, release):
        base = original(height, outputs, release)
        if not strength or not .328 < height < .352:
            return base
        weight = strength * (1. - abs(height - .34) / .012)
        history = np.asarray(policy.restart_history)
        command = history[:, 0]
        neutral = np.flatnonzero(np.abs(command) <= .04)
        if np.any(command[-104:] < -.10) or not len(neutral):
            return base
        resume = int(neutral[-1]) + 1
        if (resume < 13 or not 0 < len(command) - resume < 95
                or np.any(np.abs(command[resume - 12:resume]) > .04)
                or not np.any(command[:resume - 12] > .32)):
            return base
        tread = float(history[resume - 7:resume, 20:22].mean()) * .625
        weight *= float(np.clip((.025 - tread) / .19, 0., 1.))
        if weight <= 0.:
            return base
        context, probability, correction = ROUTER.evaluate(policy.restart_history)
        gate = float(np.clip(.5 + (probability - .76) / .10, 0., 1.))
        context0, gate0, correction0, release0 = base
        return (context0 + weight * (context - context0), gate0 + weight * (gate - gate0),
                correction0 + weight * (.75 * correction - correction0), release0 + weight * (.10 - release0))

    policy.adjust_parked_resume = adjust
    try:
        return run_case(grid.SIM, case, None)
    finally:
        policy.adjust_parked_resume = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--weight', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    cases = [case for case in profiles(True) if .325 <= case.target <= .355]
    results = []
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(), args.weight.resolve())) as pool:
        for strength in (0., .26, .50, .72, 1.):
            rows = list(pool.map(evaluate, [(case, strength) for case in cases]))
            results.append(dict(strength=strength, cases=[vars(case) for case in cases], results=rows))
            args.out.write_text(json.dumps(results, indent=2, allow_nan=False)+'\n', encoding='utf8')
            print(strength, [(row['name'], row['steps'][0]['both_top_s'], row['fell']) for row in rows], flush=True)


if __name__ == '__main__':
    main()
