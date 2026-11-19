# SPDX-License-Identifier: MIT
"""Evaluate low-speed approach and capture from the graduated neural stair expert."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path
import sys

import numpy as np
import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, maps
from verify_wasd import Case, run_case

GRADUATE = HERE.parent / 'MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118'
SIM = None
CONFIG = None


def initialize(manifest, approach_only):
    global SIM
    sys.path.insert(0, str(GRADUATE))
    from history_eval_hooks import ReplayHistoryActor

    maps.CACHE_DIR = HERE / 'runtime_cache' / f'graduate_capture_{os.getpid()}'
    model, hashes, prep = load_manifest(manifest)
    raw = torch.load(GRADUATE / 'weights/model_rl_stair_best.pt', map_location='cpu', weights_only=False)
    learned = ReplayHistoryActor().load_checkpoint(raw).eval()
    SIM = RepairedSimulation(model, hashes['package'], show_viewer=False, jump_stance_prep=prep)
    route_native = model.act
    clear_native = model.reset_history
    original_stair_outputs = model.stair_outputs
    skill = learned.mlp.e1
    mode = torch.tensor([0., 1., 0., 0., 0., 1., 0.])

    def reset():
        learned.reset_history()
        clear_native()

    @torch.inference_mode()
    def route(observation):
        action, route = route_native(observation)
        x = torch.from_numpy(observation)[None].clone()
        x[:, 28:] = mode
        # Map the command to this expert's trained stance. Keep the real driver
        # speed, joint motion, attitude and executed action in the history.
        x[:, 3] = .4091 * 5.
        history = learned.queue.append(x)
        if not model.allow_stair:
            return action, route
        normal_x = torch.from_numpy(observation)[None].clone()
        normal_x[:, 3] = .4091 * 5.
        gate = float(skill.gate_prob(history).item())
        approach = skill.approach_base(normal_x)[0].numpy()
        known_stair = skill(x, history)[0].numpy()
        history_features = skill.encoder(history)[0].numpy()
        # A bounded residual runs on estimated fore-aft velocity and body tilt.
        # State/geometry used to grade an episode never enters inference.
        body_speed = float(history_features[0])
        wheel_speed = float(np.mean(observation[20:22])) * .625
        estimated_vx = float(np.clip(body_speed, -.9, 1.3))
        excess = np.clip((.55 * wheel_speed + .45 * estimated_vx) - float(observation[0]), -.30, .80)
        tilt = float(np.tanh(6. * observation[7] + .75 * observation[5]))
        front, rear, climb_trim, wheel_trim, normal_trim, corroboration = CONFIG
        if corroboration > 0.:
            agree = min(1., float(route['g_prob']) / corroboration)
            known_stair = approach + agree * (known_stair - approach)
            gate *= agree
        adjustment = np.array([front * tilt, rear * tilt, front * tilt, rear * tilt,
                               climb_trim - wheel_trim * excess, climb_trim - wheel_trim * excess])
        known_stair = known_stair + gate * adjustment
        known_stair[4:6] -= (1. - gate) * normal_trim * max(0., excess - .08)
        return np.clip(known_stair, -6., 6.), {'e0': 1. - gate, 'e1': gate, 'e2': 0., 'g_prob': gate}

    model.reset_history = reset
    if approach_only:
        @torch.inference_mode()
        def calibrated_approach(current, history):
            blended = original_stair_outputs(current, history)
            if not model.allow_stair:
                return blended
            x = current.clone()
            x[:, 3] = .4091 * 5.
            approach = skill.approach_base(x)
            ratio, _, v_scale, _, _, _ = CONFIG
            blended['a_e0'] = torch.lerp(blended['a_e0'], approach, ratio)
            # Keep changes to the normal bridge and the native skill output
            # separate so the active stair head remains independently testable.
            if v_scale:
                guide = current.clone()
                guide[:, 0] = blended['v_virt']
                guide[:, 3] = blended['h_virt'] * 5.
                before = model.stair.e0(guide)
                guide[:, 0] = guide[:, 0].clamp(max=.55)
                blended['a_stair'] += v_scale * (model.stair.e0(guide) - before)
            return blended
        model.stair_outputs = calibrated_approach
    else:
        model.act = route


def evaluate(item):
    global CONFIG
    profile, CONFIG = item
    return run_case(SIM, profile, None) | {'profile': list(CONFIG)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=5)
    parser.add_argument('--approach-only', action='store_true')
    args = parser.parse_args()
    standard = [Case(f'slow_h42_{mm:+03}', target=.42, speed=.47, offset=mm / 1000., duration=9.)
                for mm in (-60, -30, 0, 30, 60)]
    negative = [Case('slow_wall_h42', target=.42, speed=.47, mode='wall', map_height=50, duration=6.7),
                replace(standard[2], name='slow_release_h42', mode='stop', duration=7.)]
    configurations = [(0., 0., 0., 0., 0., 0.), (0., 0., 0., 0., .9, 0.),
                      (0., 0., 0., 0., .45, 0.), (.08, -.06, -.05, .27, .35, 0.),
                      (0., 0., -.03, .20, .65, 0.), (0., 0., 0., 0., 0., .50),
                      (0., 0., -.04, .25, .35, .50), (-.06, .12, -.11, .38, .6, 0.)]
    if args.approach_only:
        configurations = [(ratio, 0., trim, 0., 0., 0.)
                          for ratio,trim in ((1.,0.),(.75,0.),(.50,0.),(1.,.45),(.75,.45),(.50,.45))]
    records = []
    count = len(standard) + len(negative)
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize, initargs=(args.candidate.resolve(), args.approach_only)) as pool:
        for row in pool.map(evaluate, [(profile, cfg) for cfg in configurations for profile in standard + negative]):
            records.append(row)
            if len(records) % count == 0:
                print(row['profile'], [(r['name'], r['steps'][0]['both_top_s'], r['fell'],
                                        round(r['peak_vx_m_s'], 3), round(r['steps'][0]['backtrack_m'], 3),
                                        r.get('wall_gate_after_one_second')) for r in records[-count:]], flush=True)
                args.out.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
