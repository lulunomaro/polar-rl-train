# SPDX-License-Identifier: MIT
"""Measure the learned restart gate across release rates in the actual WASD player."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path

import numpy as np

from play_repaired import HERE, RepairedSimulation, load_manifest, maps
from verify_wasd import Case, restart_cases, run_case

SIM = None


def init(manifest):
    global SIM
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'release_probe_{os.getpid()}'
    policy, provenance, prep = load_manifest(manifest)
    SIM = RepairedSimulation(policy, provenance['package'], show_viewer=False, jump_stance_prep=prep)


def probe(spec):
    case, rate, gate_bias = spec
    model = SIM.unified
    model.restart_release_per_tick = rate
    router = model.restart_router
    original = router.evaluate

    def calibrated(history):
        ctx, gate, correction = original(history)
        value = np.clip(gate, 1.e-6, 1. - 1.e-6)
        calibrated_gate = 1. / (1. + np.exp(-gate_bias) * (1. - value) / value)
        return ctx, float(calibrated_gate), correction

    router.evaluate = calibrated
    try:
        result = run_case(SIM, case, None)
    finally:
        router.evaluate = original
    return result | {'release':rate,'gate_bias':gate_bias}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    cases=restart_cases()[:13]
    points=((.10,0.),(.065,0.),(.04,0.),(.08,1.),(.055,1.),(.13,-.65),(.09,-.65))
    pending=[(case,setting,bias) for setting,bias in points for case in cases]
    all_rows=[]
    with ProcessPoolExecutor(max_workers=args.workers,initializer=init,initargs=(args.candidate.resolve(),)) as pool:
        for result in pool.map(probe,pending):
            all_rows.append(result)
            if len(all_rows)%len(cases)==0:
                print(result['release'],result['gate_bias'],[
                    (r['name'],r['steps'][0]['both_top_s'],r['fell'],
                     round(r.get('restart',{}).get('peak_e1_after_one_s',0.),2)) for r in all_rows[-len(cases):]],flush=True)
                args.out.write_text(json.dumps(all_rows,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':
    main()
