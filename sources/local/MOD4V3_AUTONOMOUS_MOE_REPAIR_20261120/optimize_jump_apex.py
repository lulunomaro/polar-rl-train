# SPDX-License-Identifier: MIT
"""Tune the jump expert's final layer against physical WASD takeoff and landing."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path

os.environ.setdefault('MUJOCO_GL', 'disable')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, read_candidate, maps
from verify_wasd import Case, run_case

SIM = None
LAYER = None
BASE = None
CASES = None


def profiles(moving):
    if moving:
        return [Case('train_move_medium', mode='jump_moving', target=.28, speed=.80, duration=3.5),
                Case('train_move_tall', mode='jump_moving', target=.42, speed=.94, duration=4.6),
                Case('train_jump_20', mode='jump_step', target=.28, speed=.90, duration=4.)]
    return [Case(f'train_still_{height:.2f}', mode='jump_idle', target=height, duration=4.7)
            for height in (.28, .34, .39)]


def prepare(candidate, moving):
    global SIM, LAYER, BASE, CASES
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'jump_apex_{os.getpid()}'
    model, checks, prep = load_manifest(candidate)
    SIM = RepairedSimulation(model, checks['package'], show_viewer=False, jump_stance_prep=prep)
    LAYER = (model.moving_jump if moving else model.jump).delta_head[-1]
    BASE = {name: v.detach().clone() for name,v in LAYER.state_dict().items()}
    CASES = profiles(moving)


def revised_last_layer(base, params):
    scale, bias = torch.as_tensor(params, dtype=base['bias'].dtype).reshape(2,3)
    channels = [0, 1, 0, 1, 2, 2]
    return {'weight': base['weight'] * (1. + scale[channels, None]),
            'bias': base['bias'] * (1. + scale[channels]) + bias[channels]}


def candidate_score(params):
    LAYER.load_state_dict(revised_last_layer(BASE, params))
    measurements = []
    for case in CASES:
        report = run_case(SIM, case, out=None)
        jump = report['jump']
        hold = report['steps'][0]['both_top_s'] if case.mode=='jump_step' else None
        measurements.append({'profile': case.name, 'height': jump['clearance_m'], 'backtrack':jump['max_backtrack_m'],
                             'air_pitch':jump['air_peak_pitch_deg'], 'land_pitch':jump['landing_peak_pitch_deg'],
                             'hold':hold,'fell':report['fell']})
    heights = [row['height'] for row in measurements]
    score = 95. * np.mean(heights) + 55. * min(heights)
    for row in measurements:
        flight, landing = row['air_pitch'], row['land_pitch']
        score -= 40. * row['backtrack']
        if flight is None or landing is None or row['fell']:
            score -= 35.
            continue
        score -= .28 * max(0., flight - 12.) + .34 * max(0., landing - 8.5)
        if row['hold'] is not None:
            score -= 26. * max(0., .40 - row['hold'])
    return float(score), measurements


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--moving',action='store_true')
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--generations',type=int,default=4)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    _, paths=read_candidate(args.candidate)
    src=paths['moving_jump' if args.moving else 'jump']
    raw=torch.load(src,map_location='cpu',weights_only=True)
    state=raw.get('state_dict',raw.get('model_state_dict'))
    weight_key=next(k for k in reversed(list(state)) if k.startswith('actor_body.e_jump.delta_head.') and k.endswith('.weight'))
    bias_key=weight_key.removesuffix('.weight')+'.bias'
    base={'weight':state[weight_key].clone(),'bias':state[bias_key].clone()}
    rng=np.random.default_rng(20261120 if args.moving else 20261121)
    mean=np.zeros(6)
    spread=np.array([.078,.074,.067,.14,.15,.12])
    bounds=np.array([.24,.24,.22,.44,.44,.36])
    ranked=[]
    with ProcessPoolExecutor(max_workers=args.workers,initializer=prepare,initargs=(args.candidate,args.moving)) as pool:
        for generation in range(args.generations):
            params=[np.zeros(6),mean]+list(np.clip(rng.normal(mean,spread,(18,6)),-bounds,bounds))
            for vector,(score,metrics) in zip(params,pool.map(candidate_score,params),strict=True):
                ranked.append({'generation':generation,'params':vector.tolist(),'score':score,'measurements':metrics})
            ranked.sort(key=lambda row:row['score'],reverse=True)
            leader=ranked[0]
            elites=np.array([r['params'] for r in ranked[:6]])
            mean=elites.mean(0)
            spread=np.maximum([.014,.014,.014,.025,.025,.025],.90 * elites.std(0))
            report={'candidate':str(args.candidate),'weight_source':str(src),'moving':args.moving,'evaluated':len(ranked),'scores':ranked}
            (args.out/'SEARCH.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(generation,leader,flush=True)
    for i, ranked_row in enumerate(ranked[:8]):
        new=revised_last_layer(base,ranked_row['params'])
        state[weight_key]=new['weight']
        state[bias_key]=new['bias']
        raw['apex_fit']=ranked_row
        torch.save(raw,args.out/f'model_apex_{i:02}.pt')


if __name__=='__main__':
    main()
