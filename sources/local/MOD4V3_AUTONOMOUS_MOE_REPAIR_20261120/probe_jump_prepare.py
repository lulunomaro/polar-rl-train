# SPDX-License-Identifier: MIT
"""Replay high-stance jump requests while shaping the crouch approach speed."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import json
import os
from pathlib import Path

from play_repaired import CONTROL_DT, HERE, RepairedSimulation, load_jump_expert, load_manifest, maps
from verify_wasd import Case, run_case
import torch

SIM = None
VARIANT = None


def initialize(manifest, jump_checkpoint):
    global SIM
    torch.set_num_threads(1)
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'jump_prepare_{os.getpid()}'
    actor, hashes, prep = load_manifest(manifest)
    if jump_checkpoint is not None:
        saved = torch.load(jump_checkpoint, map_location='cpu', weights_only=True)
        actor.moving_jump, actor.moving_jump_history_frames, actor.moving_jump_frames = load_jump_expert(saved, actor.stair.e0.state_dict())
    SIM = RepairedSimulation(actor, hashes['package'], show_viewer=False, jump_stance_prep=prep)
    original_step = SIM.step
    original_update = SIM.update_jump_height
    original_act = actor.act

    def act(obs):
        if isinstance(VARIANT, list) and obs[30] > .5:
            obs = obs.copy()
            obs[3] = 5. * VARIANT[0]
        return original_act(obs)

    actor.act = act

    def step(keys):
        if not isinstance(VARIANT, tuple) or not SIM.jump_pending or not ('w' in keys and not keys.intersection({'s','a','d'})):
            return original_step(keys)
        speed, _, _ = VARIANT
        requested_speed = SIM.max_vx
        try:
            SIM.max_vx = min(requested_speed, speed)
            original_step(keys)
        finally:
            SIM.max_vx = requested_speed

    def update(pressed):
        if (not SIM.jump_pending or 'w' not in pressed or pressed.intersection({'s', 'a', 'd'})
                or not isinstance(VARIANT, (tuple, dict))):
            return original_update(pressed)
        if isinstance(VARIANT, dict):
            floor, crouch_rate, hold = VARIANT['floor'], VARIANT['rate'], VARIANT['hold']
            floor = min(SIM.target_h, floor)
        else:
            _, crouch_rate, hold = VARIANT
            floor = .28
        SIM.jump_height = max(floor, SIM.jump_height - crouch_rate * CONTROL_DT)
        if SIM.jump_height <= floor + 1.e-6:
            SIM.jump_prepare_frames += 1
            if SIM.jump_prepare_frames >= hold:
                SIM.jump_pending = False
                SIM.start_jump()

    SIM.step = step
    SIM.update_jump_height = update


def trial(task):
    global VARIANT
    case, VARIANT, out = task
    prior = SIM.jump_stance_prep
    if VARIANT == 'direct' or isinstance(VARIANT, list):
        SIM.jump_stance_prep = False
    try:
        return run_case(SIM, case, out)
    finally:
        SIM.jump_stance_prep = prior


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--moving-jump', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--workers', type=int, default=4)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--direct', action='store_true', help='Compare no crouch preparation at the original keypress')
    mode.add_argument('--short-prep', action='store_true')
    mode.add_argument('--direct-height', type=float, nargs='+', help='Direct takeoff with this virtual jump-only height input')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = [Case(f'jump_step_h{round(h*100)}_{i}', target=h, speed=s, yaw=y, offset=x, mode='jump_step', duration=5.)
             for i,(h,s,y,x) in enumerate(((.36,.92,2.,-.03),(.42,.90,0.,0.),(.42,.83,0.,.03),(.38,.95,-2.,-.035),(.42,1.01,3.,.02)))]
    cases += [Case(f'jump_flat_h{round(h*100)}', target=h, speed=s, mode='jump_moving', duration=5.)
              for h,s in ((.36,.9),(.40,.9),(.42,.90))]
    variants = [None, 'direct'] if args.direct else [None] + [(speed, rate, hold) for speed,(rate,hold) in product((.32,.43,.54,.66),((.28,10),(.52,6)))]
    if args.direct_height:
        variants = [None, 'direct'] + [[h] for h in args.direct_height]
    if args.short_prep:
        variants = [None, 'direct'] + [dict(floor=floor, rate=rate, hold=hold) for floor,rate,hold in
                   ((.33,.55,1),(.315,.63,1),(.295,.75,1),(.32,1.1,2),(.305,1.15,2),(.28,.95,1))]
    records = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(), None if args.moving_jump is None else args.moving_jump.resolve())) as pool:
        for i,params in enumerate(variants):
            folder = args.out / f'variant_{i:02d}'
            folder.mkdir()
            rows = list(pool.map(trial, [(c, params, folder) for c in cases]))
            records.append({'params':params,'results':rows})
            (args.out/'RESULTS.json').write_text(json.dumps(records,indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(i,params,[(r['name'], r['fell'], r['steps'][0]['both_top_s'] if r['steps'] else None,
                            round(r['jump']['clearance_m'],3), round(r['jump']['max_backtrack_m'],3),
                            round(r['jump']['landing_peak_pitch_deg'] or 0.,1)) for r in rows], flush=True)


if __name__=='__main__':
    main()
