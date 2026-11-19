# SPDX-License-Identifier: MIT
"""Closed-loop low-speed reference check with the installed MOD4v3 WASD plant."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
from pathlib import Path
import os

import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, maps
from verify_wasd import Case, run_case

SIM, CONTROL = None, None


def init(manifest):
    global SIM, CONTROL
    maps.CACHE_DIR = HERE/'runtime_cache'/f'speed_probe_{os.getpid()}'
    policy, sha, prep = load_manifest(manifest)
    SIM = RepairedSimulation(policy, sha['package'], show_viewer=False, jump_stance_prep=prep)
    CONTROL = {'scale':1., 'residual_scale':1.}
    original = policy.stair_outputs

    @torch.inference_mode()
    def calibrated(current, history):
        output = original(current, history)
        if not policy.allow_stair:
            return output
        goal = current.clone()
        goal[0, 0] *= CONTROL['scale']
        output['a_e0'] = policy.stair.e0(goal)
        if CONTROL['residual_scale'] != 1.:
            # Scale the virtual forward command while preserving the learned leg and wheel residual.
            virtual = current.clone()
            virtual[:, 0] = output['v_virt']
            virtual[:, 3] = 5. * output['h_virt']
            before = policy.stair.e0(virtual)
            virtual[:, 0] *= CONTROL['residual_scale']
            output['a_stair'] += policy.stair.e0(virtual) - before
        return output

    policy.stair_outputs = calibrated


def test(row):
    case, scale, residual_scale = row
    CONTROL.update(scale=scale,residual_scale=residual_scale)
    result = run_case(SIM, case, None)
    return result | {'approach_scale':scale,'virtual_speed_scale':residual_scale,'driver_speed':case.speed}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workers',type=int,default=3)
    args=p.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    cases=[Case(f'slow_h42_{mm:+03}mm',target=.42,speed=.47,offset=mm/1000,duration=10.) for mm in (-60,-30,0,30,60)]
    jobs=[(case,scale,residual_scale) for scale,residual_scale in
          ((1.,1.),(.70,1.),(.76,1.),(.80,1.),(.86,1.),(.72,.92),(.72,.84),(.78,.84),(.78,.72),(.85,.85))
          for case in cases]
    records=[]
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init, initargs=(args.candidate.resolve(),)) as pool:
        for result in pool.map(test,jobs):
            records.append(result)
            args.out.write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
            if len(records)%5==0:
                print([(r['name'],r['fell'],r['steps'][0]['both_top_s'],round(r['peak_vx_m_s'],3)) for r in records[-5:]],flush=True)

if __name__=='__main__':
    main()
