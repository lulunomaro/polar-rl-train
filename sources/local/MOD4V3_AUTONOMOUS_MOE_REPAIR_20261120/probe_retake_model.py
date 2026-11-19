# SPDX-License-Identifier: MIT
"""Compare trained retake actions and contact routing in the WASD loop."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
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
PARENT_ROUTERS = None
VARIANTS = None
SCOPE = None
MODELS = None
SLEW = None
RETAKE_BYPASS = None


def network(path, actor):
    if path not in MODELS:
        weights = torch.load(path, map_location='cpu', weights_only=True)['moe_state_dict']
        frozen = actor.stair.e0.state_dict()
        same_locomotion(frozen, weights, 'e0.')
        same_locomotion(frozen, weights, 'e1_stair.loco_base.')
        candidate = stair.AutonomousStairMoE()
        candidate.load_state_dict(weights, strict=True)
        MODELS[path] = candidate.eval().requires_grad_(False)
    return MODELS[path]


def retake_weight(actor, height):
    context, _, _ = actor.restart_outputs(actor.restart_router)
    weight = float(np.clip((context - .76) / .20, 0., 1.))
    if SCOPE == 'high':
        weight *= float(np.clip((height - .37) / .03, 0., 1.))
    elif SCOPE == 'low':
        weight *= float(np.clip((.37 - height) / .027, 0., 1.))
    return weight


def initialize(manifest):
    global SIM, PARENT_ROUTERS, MODELS
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'retake_{os.getpid()}'
    actor, _, prep = load_manifest(manifest)
    SIM = RepairedSimulation(actor, actor.runtime_sha, show_viewer=False, jump_stance_prep=prep)
    PARENT_ROUTERS = (actor.router_weights, actor.high_router_weights)
    MODELS = {}
    native = actor.stair_outputs
    native_act = actor.act
    primary_parked = actor.parked_restart_outputs
    primary_restart = actor.restart_outputs

    def bypass_weight(height):
        if RETAKE_BYPASS is None:
            return 0.
        if SCOPE == 'high':
            return RETAKE_BYPASS * float(np.clip((height - .37) / .03, 0., 1.))
        if SCOPE == 'low':
            return RETAKE_BYPASS * float(np.clip((.37 - height) / .027, 0., 1.))
        return RETAKE_BYPASS

    def restart_outputs(router):
        context, probability, correction = primary_restart(router)
        # Only change authority, so the learned prediction itself is identical.
        height = float(actor.restart_history[-1][3]) / 5.
        context *= 1. - bypass_weight(height)
        return context, probability, correction

    def parked_outputs(height, baseline):
        context, probability, correction = primary_parked(height, baseline)
        context *= 1. - bypass_weight(height)
        return context, probability, correction

    @torch.inference_mode()
    def with_retake(current, history):
        out = native(current, history)
        extra = VARIANTS['stair']
        if extra is None or not actor.allow_stair:
            return out
        weight = retake_weight(actor, float(current[0, 3]) / 5.)
        if weight == 0.:
            return out
        alternate = extra.compute_all_heads(current, history)
        for name in ('a_stair', 'h_virt', 'v_virt'):
            out[name] = torch.lerp(out[name], alternate[name], weight)
        return out

    def bounded_retake(obs):
        action, route = native_act(obs)
        if SLEW is None or route['e1'] <= .0:
            return action, route
        weight = route['e1'] * retake_weight(actor, float(obs[3]) / 5.)
        if weight > 0.:
            limits = np.array([*SLEW[:2], *SLEW[:2], SLEW[-1], SLEW[-1]])
            delta = action - obs[22:28]
            action = action + weight * (np.clip(delta, -limits, limits) - delta)
        return action, route

    actor.stair_outputs = with_retake
    actor.act = bounded_retake
    actor.restart_outputs = restart_outputs
    actor.parked_restart_outputs = parked_outputs


def evaluate(task):
    global VARIANTS, SCOPE, SLEW, RETAKE_BYPASS
    case, stair_path, router_path, SCOPE, SLEW, RETAKE_BYPASS = task
    control = SIM.unified
    VARIANTS = {role: network(path, control) if path else None
                for role, path in (('stair', stair_path), ('router', router_path))}
    control.router_weights, control.high_router_weights = PARENT_ROUTERS
    if VARIANTS['router'] is not None:
        if SCOPE != 'high':
            control.router_weights = VARIANTS['router']
        if SCOPE != 'low':
            control.high_router_weights = VARIANTS['router']
    row = run_case(SIM, case, None)
    return row | {'scope': SCOPE, 'retake_stair': stair_path, 'contact_router': router_path,
                  'parent_runtime_sha256': control.runtime_sha, 'slew': SLEW, 'retake_bypass': RETAKE_BYPASS}


def profiles(suite):
    standard = restart_cases()[:13]
    varied = [row for row in held_profiles() if row.mode == 'stop']
    if suite == 'screen':
        preferred = {'restart_reverse_h42', 'restart_stop_h40', 'restart_stop_h28', 'restart_stop_h32',
                     'restart_wall_h42', 'restart_wall_h28', 'stop_repeat_h28_x-45',
                     'stop_repeat_h32_x-45', 'stop_repeat_h34_x+45'}
        return [row for row in standard + varied if row.name in preferred]
    # Offset, speed and duration combinations absent from the training anchor pool.
    varied.extend(Case(f'held_{mode}_{round(h*100)}_{index}', target=h, speed=speed, yaw=yaw,
                       mode=mode, offset=offset, duration=9., cancel_delay_s=cancel, restart_delay_s=wait)
                  for index, (h, speed, yaw, offset, cancel, wait) in enumerate((
                      (.28,.91,3.,-.063,.12,.82), (.33,.96,-3.,.02,.07,1.16),
                      (.40,.86,-4.,.057,.06,.71), (.42,.88,4.,-.04,.14,1.11)))
                  for mode in ('stop','reverse'))
    return standard + varied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--suite', choices=('screen','held'), default='screen')
    parser.add_argument('--stair', type=Path, nargs='+', default=[])
    parser.add_argument('--router', type=Path, nargs='+', default=[])
    parser.add_argument('--scope', nargs='+', choices=('all','low','high'), default=['all'])
    parser.add_argument('--slew', type=float, nargs=3, action='append', metavar=('FRONT', 'REAR', 'WHEEL'), default=[])
    parser.add_argument('--retake-bypass', type=float, nargs='+', default=[])
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    cases = profiles(args.suite)
    files = lambda paths: [str(path.resolve()) for path in paths]
    combinations = [(None, None, 'all')]
    for scope in args.scope:
        combinations += [(path, None, scope) for path in files(args.stair)]
        combinations += [(None, path, scope) for path in files(args.router)]
        if args.stair and args.router:
            combinations.append((files(args.stair)[-1], files(args.router)[-1], scope))
    jobs = [(row, a, b, scope, None, None) for a, b, scope in combinations for row in cases]
    jobs += [(row, None, None, scope, limits, None) for scope in args.scope for limits in args.slew for row in cases]
    jobs += [(row, None, None, scope, None, bypass) for scope in args.scope
             for bypass in args.retake_bypass for row in cases]
    unique_paths = {path for actor, router, _ in combinations for path in (actor, router) if path}
    report = {'sha256': {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in sorted(unique_paths)},
              'results': []}
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(),)) as pool:
        for row in pool.map(evaluate, jobs):
            report['results'].append(row)
            if len(report['results']) % len(cases) != 0:
                continue
            recent = report['results'][-len(cases):]
            print(row['scope'], row['retake_stair'], row['contact_router'], row['slew'], row['retake_bypass'], [
                (r['name'], r['fell'], r['steps'][0]['both_top_s'],
                 round(r.get('restart', {}).get('backtrack_m', 0.), 3),
                 round(r.get('restart', {}).get('peak_e1_after_one_s', 0.), 3))
                for r in recent], flush=True)
            args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
