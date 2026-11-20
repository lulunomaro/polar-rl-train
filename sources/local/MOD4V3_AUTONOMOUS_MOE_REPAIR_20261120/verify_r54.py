# SPDX-License-Identifier: MIT
"""Verify the live MOD4v3 player on its stair, driver handoff and jump regressions."""
from concurrent.futures import ProcessPoolExecutor
import argparse
import json
from pathlib import Path

import torch

from play_repaired import RepairedSimulation, load_manifest
from probe_jump_intent import run as probe_intent
from screen_r25_high_jump import flight_evidence
from verify_wasd import Case, restart_cases, run_case, takeover_cases
from verify_driving_grid import profiles


def jump_cases():
    steps = [Case(f'jump_step_{i}', target=h/100., offset=x/1000., yaw=y, speed=v, jump_distance_m=d/100.,
                  mode='jump_step', duration=5.8, drive_at_s=drive)
             for i, (h,d,x,y,v,drive) in enumerate(((28,67,-24,2,.88,.40),(28,70,15,-1,.93,.46),
                  (32,77,0,0,.89,.40),(34,83,0,0,.90,.40),(34,86,-14,1.5,.91,.43),(36,86,0,0,.86,.40),
                  (38,95,-23,-1,.88,.45),(40,97,0,0,.90,.40),(42,93,0,0,.93,.40),(42,99,18,2,.90,.43))) ]
    held = [Case(f'close_h{round(h*1000)}', target=h, speed=.855, mode='jump_step', drive_at_s=.39,
                 jump_distance_m=.598, offset=-.041, yaw=1.8, duration=5.) for h in (.31,.33,.35,.365)]
    held.append(Case('close_h340', target=.34, speed=.91, mode='jump_step', drive_at_s=.52,
                     jump_distance_m=.65, offset=.016, yaw=-2.4, duration=5.))
    moving = [Case(f'move_h{h}', target=h/100., mode='jump_moving', speed=v, drive_at_s=drive, duration=4.5)
              for h,v,drive in ((28,.89,.44),(32,.89,.42),(36,.84,.49),(38,.93,.44),(40,.90,.4),(42,.92,.46))]
    moving.append(Case('move_h412', target=.412, speed=.99, mode='jump_moving', drive_at_s=.48, duration=4.4))
    return steps + held + moving + [Case('default_jump20', mode='jump_step', duration=5.)]


def stair_cases():
    fixed = [Case(f'fixed_h{round(h * 100)}_x{x:+03}', target=h, offset=x/1000., duration=6.5)
             for h in (.28,.32,.36,.40,.42) for x in (-60,-30,0,30,60)]
    return fixed + profiles('late-rise') + takeover_cases()


def initialize(manifest):
    global SIM
    torch.set_num_threads(1)
    policy, _, prep = load_manifest(manifest)
    SIM = RepairedSimulation(policy, policy.runtime_sha, show_viewer=False, jump_stance_prep=prep)


def execute(job):
    case, out, videos = job
    result = run_case(SIM, case, out, video=case.name in videos)
    if isinstance(result.get('jump'),dict) and result['jump']['e2_first_at_s'] is not None:
        result['flight'] = flight_evidence(result, out/(case.name+'.npz'))
    return result


def probe(args):
    return probe_intent(SIM, *args)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--group',choices=('jump','stair','slow','examples'),required=True)
    p.add_argument('--case',action='append',default=[])
    p.add_argument('--video',action='append',default=[])
    p.add_argument('--workers',type=int,default=2)
    a = p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    match a.group:
        case 'jump':
            cases = jump_cases()
        case 'stair':
            cases = stair_cases()
        case 'slow':
            cases = profiles('slow') + [case for case in restart_cases() if case.name.startswith('restart_stop_h42_v47')]
            cases += [Case(f'slow_wall{h}', target=h/100, speed=.47, mode='wall', map_height=45, duration=5.5) for h in (40,42)]
        case 'examples':
            cases = [Case('h42', target=.42), Case('jump_moving_h42', target=.42, mode='jump_moving')]
            cases.extend(c for c in jump_cases() if c.name in ('close_h340', 'default_jump20','jump_step_3'))
    if a.case:
        cases = [c for c in cases if c.name in a.case]
        if len(cases) != len(a.case):
            p.error('--case must name a case in the specified group')
    results = []
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.candidate.resolve(),)) as pool:
        for row in pool.map(execute,[(c,a.out.resolve(),a.video) for c in cases],chunksize=1):
            results.append(row)
            s = row['steps'][0] if row['steps'] else {}
            fl = row.get('flight', {})
            principal = fl.get('principal') or {}
            j = row.get('jump') or {}
            print(row['name'], 'support',s.get('both_top_s'), 'fall',row['fell'], 'direct',fl.get('direct_step_pass'),
                  'back',round((j.get('max_backtrack_m') or s.get('backtrack_m') or 0.)*100.,2),
                  'rise',round(principal.get('rim_peak_m',0.)*100.,2),flush=True)
        intent = []
        if a.group == 'jump' and not a.case:
            keys = [(h,k) for h in (.28,.34,.42) for k in ('w_from_rest','forward_after_reverse','w_tap_cancel')]
            intent = list(pool.map(probe,keys,chunksize=1))
    result = {'candidate': str(a.candidate.resolve()),'cases':[vars(c) for c in cases],'rows':results,'intent':intent}
    (a.out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')


if __name__ == '__main__':
    main()
