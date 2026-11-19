# SPDX-License-Identifier: MIT
"""Compare revised MOD4v3 experts in the independent WASD runtime."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path

import torch

from play_repaired import HERE, RepairedSimulation, load_jump_expert, load_manifest, maps, same_locomotion, stair
from verify_wasd import Case, cases, run_case

SIM = None
BANK = None
IDENTITY = None


def initialize(manifest):
    global SIM, BANK, IDENTITY
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'expert_grid_{os.getpid()}'
    model, sha, prep = load_manifest(manifest)
    SIM = RepairedSimulation(model, model.runtime_sha, show_viewer=False, jump_stance_prep=prep)
    BANK = model.stair_height_bank
    IDENTITY = model.runtime_sha


def run(item):
    profile, weights, role, stance = item
    model = SIM.unified
    if weights is not None:
        state = torch.load(weights, map_location='cpu', weights_only=True)
        new_sha = hashlib.sha256(weights.read_bytes()).hexdigest()
        frozen = model.stair.e0.state_dict()
        if role in ('jump','moving_jump'):
            net, history, ticks = load_jump_expert(state, frozen)
            setattr(model, role, net.eval())
            setattr(model, role + '_history_frames', history)
            setattr(model, role + '_frames', ticks)
        else:
            state = state['moe_state_dict']
            same_locomotion(frozen,state,'e0.')
            same_locomotion(frozen,state,'e1_stair.loco_base.')
            net = stair.AutonomousStairMoE()
            net.load_state_dict(state, strict=True)
            net.eval()
            if role == 'bank':
                model.stair_height_bank = tuple((h, net if abs(h-stance)<1e-6 else original) for h,original in BANK)
            elif role == 'slow_stair':
                model.slow_stair = net
            else:
                setattr(model, role + '_weights', net)
    else:
        new_sha = None
        model.stair_height_bank = BANK
    result = run_case(SIM, profile, None)
    return result | {'parent_runtime_sha256': IDENTITY, 'checkpoint_override': str(weights) if weights else None,
                     'override_sha256': new_sha, 'role': role, 'bank_height': stance}


def profiles(role, height, driving_grid='default'):
    if driving_grid == 'late-rise':
        return [Case(f'late_h42_x{mm:+03}', target=.42, offset=mm/1000., raise_while_moving=True,
                     raise_at_s=.95) for mm in (-60, -30, 0, 30, 60)]
    suite = cases(False)
    if role == 'jump':
        return [p for p in suite if p.mode == 'jump_idle']
    if role == 'moving_jump':
        return [p for p in suite if p.mode in ('jump_moving','jump_step')]
    if role in ('bank','slow_stair'):
        speed = .47 if role == 'slow_stair' else .90
        p = [Case(f'h{round(100*height)}_x{mm:+03}', target=height, speed=speed, offset=mm/1000,
                  duration=10. if speed < .6 else 7.5) for mm in (-60,-30,0,30,60)]
        if role == 'bank':
            p += [Case(f'rise_h{round(100*height)}', target=height, speed=speed, raise_while_moving=True)]
        return p
    return [p for p in suite if ('wall_h' in p.name or p.name in ('h28','h32','h36','h42','rise_h42','flat_rise','stop_at_step'))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--role', choices=('bank','slow_stair','router','high_router','jump','moving_jump'), required=True)
    parser.add_argument('--height', type=float, default=.42)
    parser.add_argument('--driving-grid', choices=('default','late-rise'), default='default')
    parser.add_argument('--workers', type=int, default=5)
    parser.add_argument('weights', type=Path, nargs='+')
    args = parser.parse_args()
    cases = profiles(args.role,args.height,args.driving_grid)
    if args.out.exists():
        raise FileExistsError(args.out)
    grid = [(p,w.resolve(),args.role,args.height) for w in args.weights for p in cases]
    records = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize, initargs=(args.candidate.resolve(),)) as pool:
        for r in pool.map(run,grid):
            records.append(r)
            if len(records) % len(cases) == 0:
                summary = []
                for z in records[-len(cases):]:
                    if 'jump' in z:
                        j = z['jump']
                        summary.append((z['name'], z['fell'], round(j['clearance_m'],4), round(j['max_backtrack_m'],4),
                                        round(j['landing_peak_pitch_deg'] or 0.,2)))
                    elif z['steps']:
                        s = z['steps'][0]
                        summary.append((z['name'],z['fell'],s['both_top_s'],round(s['backtrack_m'],4),
                                        round(z['peak_vx_m_s'],3),z.get('wall_gate_after_one_second')))
                print(Path(r['checkpoint_override']).name,summary,flush=True)
                args.out.write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
