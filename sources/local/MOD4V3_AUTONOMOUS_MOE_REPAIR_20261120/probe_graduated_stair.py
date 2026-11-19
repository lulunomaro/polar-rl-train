# SPDX-License-Identifier: MIT
"""Evaluate the fixed-200 stair graduate against the autonomous WASD plant."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
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


def init(player_manifest):
    global SIM, CONFIG
    sys.path.insert(0, str(GRADUATE))
    from history_eval_hooks import ReplayHistoryActor

    maps.CACHE_DIR = HERE / 'runtime_cache' / f'graduate_stair_{os.getpid()}'
    model, sha, prep = load_manifest(player_manifest)
    reference = torch.load(GRADUATE / 'weights/model_rl_stair_best.pt', map_location='cpu', weights_only=False)
    learner = ReplayHistoryActor().load_checkpoint(reference).eval()
    SIM = RepairedSimulation(model, sha['package'], show_viewer=False, jump_stance_prep=prep)
    route = model.act
    clear = model.reset_history
    CONFIG = (.4091, 1., 0.)
    mode = torch.tensor([0.,1.,0.,0.,0.,1.,0.])

    def reset():
        clear()
        learner.reset_history()

    @torch.inference_mode()
    def action(obs):
        normal_action, _ = route(obs)
        h_ref, v_scale, damping = CONFIG
        x = torch.from_numpy(obs)[None].clone()
        x[:,28:] = mode
        x[:,3] = h_ref * 5.
        x[:,0] *= v_scale
        history = learner.queue.append(x)
        if not model.allow_stair:
            return normal_action, {'e0':1., 'e1':0., 'e2':0., 'g_prob':0.}
        e1 = learner.mlp.e1
        gate = float(e1.gate_prob(history).item())
        a = e1(x, history)[0].clone()
        # Reserve this comparison for the training analysis. It measures if a
        # purely proprioceptive wheel-speed term can curb the landing burst.
        if damping:
            wheel_vx_est = float(np.mean(obs[20:22]) * .625)
            excess = max(0., wheel_vx_est - .49)
            a[4:6] -= damping * excess
        return a.clamp(-6.,6.).numpy(), {'e0':1.-gate, 'e1':gate, 'e2':0., 'g_prob':gate}

    model.act = action
    model.reset_history = reset


def compare(test):
    global CONFIG
    case, config = test
    CONFIG = config
    result = run_case(SIM, case, out=None)
    return result | {'height_reference_m':config[0], 'speed_scale':config[1], 'wheel_speed_damping':config[2]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    profiles = [Case(f'graduate_h42_x{mm:+03}', target=.42, speed=.47, offset=mm/1000,duration=10.)
                for mm in (-60,-30,0,30,60)]
    configurations=[(.4091,1.,0.),(.416,1.,0.),(.42,1.,0.),(.405,1.,0.),
                    (.4091,.95,0.),(.4091,.90,0.),(.4091,1.,.10),(.4091,1.,.25),(.4091,1.,.45)]
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers,initializer=init,initargs=(args.candidate.resolve(),)) as pool:
        for result in pool.map(compare,[(case,cfg) for cfg in configurations for case in profiles]):
            results.append(result)
            if len(results)%len(profiles)==0:
                group=results[-len(profiles):]
                metrics=[(r['name'],r['steps'][0]['both_top_s'],round(r['peak_vx_m_s'],3),r['fell']) for r in group]
                print(len(results),metrics,flush=True)
                args.out.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
