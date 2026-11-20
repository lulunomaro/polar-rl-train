# SPDX-License-Identifier: MIT
"""Compare low-stance actor and router weights in the WASD player."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, maps, same_locomotion, stair
from verify_driving_grid import held_profiles
from verify_wasd import Case, restart_cases, run_case

SIM = None
VARIANT = None
LOADED = {}


def profiles(suite):
    centers = [Case(f'low28_offset{mm:+03}', offset=mm * .001) for mm in (-60, -30, 0, 30, 60)]
    oblique = [Case(f'low28_yaw{yaw:+03}', yaw=yaw) for yaw in (-20, -10, 10, 20)]
    restarts = [row for row in restart_cases() if row.target in (.28, .32, .36) and row.speed == .90]
    varied = [row for row in held_profiles() if row.mode == 'stop' and row.target in (.28, .34)]
    if suite == 'screen':
        walls = [replace(varied[i], name=f'wall_{height}_{varied[i].name}', map_height=height, duration=7.)
                 for i, height in ((0, 45), (2, 50))]
        return centers + oblique + restarts[:3] + varied + walls
    speeds = [Case(f'held_low{round(height*100)}_{index}', target=height, yaw=yaw, offset=offset, speed=speed)
              for index, (height, yaw, offset, speed) in enumerate((
                  (.28, -4., -.043, .84), (.28, 4., .051, .96), (.29, -7., .039, .92),
                  (.30, 8., -.035, .86), (.32, -5., -.033, .94), (.34, 5., .038, .88)))]
    dwell = [replace(row, name=f'retake_{row.name}', mode=mode, duration=9., cancel_delay_s=cancel, restart_delay_s=wait)
             for row, mode, cancel, wait in zip(speeds, ('stop','stop','reverse','stop','reverse','stop'),
                                                  (.08,.12,.15,.08,.14,.09), (.71,.98,.85,1.18,1.09,.81), strict=True)]
    walls = [replace(row, name=f'wall_{height}_{row.name}', map_height=height, duration=7.)
             for row, height in zip(dwell, (50,45,50,45,50,45), strict=True)]
    return centers + oblique + restarts + varied + speeds + dwell + walls


def initialize(manifest):
    global SIM
    torch.set_num_threads(1)
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'low_stair_screen_{os.getpid()}'
    policy, _, prep = load_manifest(manifest)
    SIM = RepairedSimulation(policy, policy.runtime_sha, show_viewer=False, jump_stance_prep=prep)
    original = policy.stair_outputs

    def network(path):
        if path not in LOADED:
            saved = torch.load(path, map_location='cpu', weights_only=True)['moe_state_dict']
            for prefix in ('e0.', 'e1_stair.loco_base.'):
                same_locomotion(policy.stair.e0.state_dict(), saved, prefix)
            actor = stair.AutonomousStairMoE()
            actor.load_state_dict(saved, strict=True)
            LOADED[path] = actor.eval().requires_grad_(False)
        return LOADED[path]

    @torch.inference_mode()
    def low_outputs(current, history):
        out = original(current, history)
        action_path, _, reflect, _, influence = VARIANT
        if not policy.allow_stair or float(current[0, 3]) / 5. >= .35:
            return out
        blend = min(1., max(0., (.35 - float(current[0, 3]) / 5.) / .04))
        specialist = network(action_path) if action_path else None
        if specialist is not None:
            blend *= influence
            altered = specialist.compute_all_heads(current, history)
            for k in ('a_stair', 'h_virt', 'v_virt'):
                out[k] = torch.lerp(out[k], altered[k], blend)
        if reflect:
            mirrored_current = stair.mirror_obs_35(current)
            mirrored_history = stair.mirror_hist_1400(history)
            mirrored = original(mirrored_current, mirrored_history)
            out['a_stair'] = torch.lerp(out['a_stair'], stair.mirror_action_6(mirrored['a_stair']), .5 * blend)
        return out

    policy.stair_outputs = low_outputs
    policy.load_screen_network = network
    original_act = policy.act

    def act(obs):
        action, route = original_act(obs)
        _, _, _, damping, _ = VARIANT
        if damping and route['e1'] > 0. and policy.allow_stair:
            height_weight = float(np.clip((.35 - float(obs[3]) / 5.) / .055, 0., 1.))
            wheel_back = float(np.clip(-obs[20:22].mean() / .25, 0., 1.))
            reverse_request = max(0., -float(action[4:6].mean()))
            correction = damping * height_weight * route['e1'] * wheel_back * reverse_request
            action[4:6] = np.clip(action[4:6] + correction, -6., 6.)
        return action, route

    policy.act = act


def measure(job):
    global VARIANT
    case, VARIANT = job
    _, router_path, _, _, _ = VARIANT
    policy = SIM.unified
    original = policy.router_weights
    if router_path is not None:
        policy.router_weights = policy.load_screen_network(router_path)
    try:
        return run_case(SIM, case, None)
    finally:
        policy.router_weights = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--stair', type=Path, nargs='*', default=())
    parser.add_argument('--stair-strength', type=float, nargs='+', default=(1.,))
    parser.add_argument('--router', type=Path, nargs='*', default=())
    parser.add_argument('--reflect', action='store_true')
    parser.add_argument('--forward-damping', type=float, nargs='*', default=())
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--suite', choices=('screen', 'held'), default='screen')
    args = parser.parse_args()
    if any(not 0. < value <= 1. for value in args.stair_strength):
        parser.error('Stair strength is a fraction in (0, 1]')
    options = [(None, None, False, 0., 1.)]
    if any(not 0. <= value <= 1. for value in args.forward_damping):
        parser.error('Forward damping is a fraction in [0, 1]')
    options += [(None, None, False, value, 1.) for value in args.forward_damping]
    if args.reflect:
        options.append((None, None, True, 0., 1.))
    options.extend((str(path.resolve()), None, False, 0., strength)
                   for path in args.stair for strength in args.stair_strength)
    options.extend((None, str(path.resolve()), False, 0., 1.) for path in args.router)
    if len(args.stair) == 1 and len(args.router) == 1:
        options.append((str(args.stair[0].resolve()), str(args.router[0].resolve()), False, 0., args.stair_strength[-1]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cases = profiles(args.suite)
    report = {'cases': [vars(case) for case in cases], 'variants': []}
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize, initargs=(args.candidate.resolve(),)) as pool:
        for variant in options:
            results = list(pool.map(measure, [(case, variant) for case in cases]))
            checks = {key: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                      for key, path in zip(('stair', 'router'), variant[:2], strict=True) if path is not None}
            report['variants'].append({'stair': variant[0], 'router': variant[1], 'reflect': variant[2],
                                       'forward_damping': variant[3], 'stair_strength': variant[4],
                                       'sha256': checks, 'results': results})
            with args.out.open('w' if len(report['variants']) > 1 else 'x', encoding='utf-8') as file:
                json.dump(report, file, indent=2, allow_nan=False)
            print(variant, [(row['name'], row['steps'][0]['both_top_s'], row['fell'],
                             round(row.get('restart', row['steps'][0]).get('backtrack_m') or 0., 3)) for row in results], flush=True)


if __name__ == '__main__':
    main()
