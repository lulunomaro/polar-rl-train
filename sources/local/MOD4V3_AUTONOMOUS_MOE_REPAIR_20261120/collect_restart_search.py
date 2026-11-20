# SPDX-License-Identifier: MIT
"""Find restart demonstrations in the exact WASD plant with an oracle used only for collection."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path

import numpy as np
import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, maps, stair
from verify_wasd import restart_cases, run_case

SIM = None


def initialize(manifest):
    global SIM
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'restart_search_{os.getpid()}'
    policy, hashes, prep = load_manifest(manifest)
    SIM = RepairedSimulation(policy, hashes['package'], show_viewer=False, jump_stance_prep=prep)
    native = policy.act
    policy.intervention = None

    @torch.inference_mode()
    def intervene(obs):
        action, route = native(obs)
        if policy.intervention is None or not policy.allow_stair:
            return action, route
        weight, strength, front, rear, wheel = policy.intervention
        current = stair.canonicalize_normal_obs(torch.from_numpy(obs)[None])
        hist = stair.canonicalize_normal_obs(policy.history.buffer)
        heads = policy.stair_outputs(current, hist.flatten(1))
        skilled = heads['a_stair'][0].numpy().copy()
        skilled += strength * np.asarray([front, rear, front, rear, wheel, wheel])
        action = (1. - weight) * heads['a_e0'][0].numpy() + weight * skilled
        policy.stair_mix = weight
        return np.clip(action, -6., 6.), route | {'e0': 1. - weight, 'e1': weight, 'g_prob': weight}

    policy.act = intervene


def record(case, profile, output=None, *, native_prefix=False):
    delay, limit, mix, front, rear, wheel = profile
    cancel_at = None
    resumed_at = None
    loaded = 0
    complete = False

    def gate(sim, trace, now, keys):
        nonlocal cancel_at, resumed_at, loaded, complete
        hit = trace.hits[0]
        sim.unified.intervention = None
        if hit is None:
            return
        if cancel_at is None and 'w' not in keys and now >= hit['t'] + case.cancel_delay_s:
            cancel_at = now
        if cancel_at is None or 'w' not in keys:
            return
        if resumed_at is None:
            resumed_at = now
        elapsed = now - resumed_at
        if elapsed >= delay + limit or complete or (native_prefix and elapsed < delay):
            return
        if case.map_height == 20:
            support = np.asarray(trace.rows[-8:])[:, 13:15].mean(axis=0)
            loaded = loaded + 1 if (support >= 5.).all() else 0
            if loaded >= 23:
                complete = True
                return
        weight = mix if elapsed >= delay else 0.
        strength = float(np.clip(1. - (elapsed - delay) / .24, 0., 1.))
        sim.unified.intervention = weight, strength, front, rear, wheel

    SIM.unified.intervention = None
    row = run_case(SIM, case, output, before_step=gate)
    step = row['steps'][0]
    restart = row.get('restart')
    reverse = restart['backtrack_m'] if restart else 3.
    hold = step['both_top_s']
    passed = (restart is not None and step['first_held_from_s'] is not None
              and step['first_held_from_s'] >= restart['t'] and hold >= .4
              and not row['fell'] and not step['slid_back'])
    row.update(map_height_cm=case.map_height, admitted=bool(passed and reverse <= .22), profile=list(profile),
               native_prefix=native_prefix)
    score = (int(row['admitted']), int(passed), int(not row['fell']), -reverse, hold)
    return score, row


def search(job):
    case, count, out, native_prefix = job
    seed = 9553 + round(case.target * 1000) + round(case.speed * 1000) + round(case.offset * 1000)
    rng = np.random.default_rng(seed)
    if case.map_height > 20:
        candidates = [(0., .18, .90, 0., 0., 0.), (0., .06, .75, 0., 0., 0.)]
        if native_prefix:
            candidates += [(.22, .16, .85, 0., 0., 0.), (.52, .12, .72, 0., 0., 0.)]
        return [record(replace(case, name=f'{case.name}_{i:02}'), p, out, native_prefix=native_prefix)[1]
                for i,p in enumerate(candidates)]
    seeds = [(d, span, mix, 0., 0., 0.) for span in (.82, 1.65, 2.1)
             for d in (0., .22, .54, .82) for mix in (1., .68)]
    if native_prefix:
        seeds = [(d, span, mix, 0., 0., 0.) for span in (1.35, 2.10)
                 for d in (.18, .34, .52, .74, .94) for mix in (1., .74)]
    population = []
    for i in range(count):
        if i < len(seeds):
            param = seeds[i]
        else:
            incumbent = population[rng.integers(min(5, len(population)))][1]['profile']
            step = rng.normal(size=6) * [.19, .30, .14, .33, .42, .43]
            param = tuple(np.clip(incumbent + step, [0., .50, .42, -1.2, -1.4, -1.4],
                                 [1.10, 2.3, 1., 1.2, 1.4, 1.4]))
        outcome = record(case, param, native_prefix=native_prefix)
        population.append(outcome)
        population.sort(key=lambda item: item[0], reverse=True)
    (out / f'{case.name}_search.json').write_text(json.dumps([row for _, row in population], indent=2) + '\n', encoding='utf8')
    options = [row['profile'] for _, row in population[:3] if row['admitted']] or [population[0][1]['profile']]
    return [record(replace(case, name=f'{case.name}_{i:02}'), p, out, native_prefix=native_prefix)[1]
            for i,p in enumerate(options)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--trials', type=int, default=30)
    focus = parser.add_mutually_exclusive_group()
    focus.add_argument('--low-stop-focus', action='store_true')
    focus.add_argument('--varied-stop-focus', action='store_true')
    focus.add_argument('--high-restart-focus', action='store_true')
    focus.add_argument('--paired-park-focus', action='store_true')
    focus.add_argument('--edge-stance-park-focus', action='store_true',
                       help='Renew forward motion at the 0.28 m and 0.34 m restart failure cases.')
    focus.add_argument('--mid-reverse-tread-focus', action='store_true',
                       help='Collect neutral-release states around .34 m with varied dwell and matched walls.')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cases = restart_cases()
    cases += [replace(c, name=c.name+'_variant', offset=.03 if c.mode=='reverse' else -.03,
                      restart_delay_s=.72 if c.mode=='reverse' else 1.1)
              for c in cases[:10] if c.target in (.28, .36, .42)]
    if args.low_stop_focus:
        template = cases[0]
        cases = [replace(template, name=f'repair_stop_h{round(h*100):02}_{i:02}', target=h,
                         offset=offset, restart_delay_s=delay, speed=speed, map_height=level)
                 for h in (.28, .32) for i,(offset,delay,speed,level) in enumerate(
                     ((0.,.92,.90,20),(-.03,.67,.85,20),(.03,1.15,.94,20),(0.,.92,.90,50),(.03,.67,.85,45)))]
    if args.varied_stop_focus:
        base = cases[0]
        rng = np.random.default_rng(202611201)
        cases = [replace(base, name=f'dagger_vary_h{round(h*1000):03}_{i:02}', target=h,
                         offset=float(rng.uniform(-.069,.069)), speed=float(rng.uniform(.84,.97)),
                         cancel_delay_s=float(rng.uniform(.055,.13)), restart_delay_s=float(rng.uniform(.61,1.22)),
                         yaw=float(rng.uniform(-2.0,2.0)), map_height=20)
                 for h in (.28, .295, .31, .325, .34) for i in range(4)]
        cases += [replace(base, name=f'dagger_vary_wall_h{round(h*1000):03}_{height}', target=h,
                          offset=float(rng.uniform(-.06,.06)), speed=float(rng.uniform(.82,.99)),
                          cancel_delay_s=float(rng.uniform(.055,.13)), restart_delay_s=float(rng.uniform(.61,1.22)),
                          yaw=float(rng.uniform(-2.5,2.5)), map_height=height)
                  for h in (.28, .31, .34) for height in (45,50)]
    if args.high_restart_focus:
        focus_cases = [c for c in cases[:10] if c.target in (.40, .42)]
        for c in focus_cases.copy():
            focus_cases.extend(replace(c, name=c.name + f'_var{i}', offset=offset, speed=speed,
                                       cancel_delay_s=cancel, restart_delay_s=resume, yaw=yaw)
                               for i, (offset, speed, cancel, resume, yaw) in enumerate(
                                   ((-.045, .86, .10, .76, -2.), (.045, .94, .12, 1.04, 2.))))
        cases = focus_cases + [replace(c, map_height=height, name=f'{c.name}_wall{height}')
                               for c in focus_cases[:4] for height in (45, 50)]
    if args.paired_park_focus:
        template = restart_cases()[0]
        # Match the driver inputs across the climbable step and the tall wall. Keep
        # the original test offsets, waits and steering conditions held out.
        cases = []
        for height in (.28, .305, .325, .344):
            for i, (offset, wait, speed, yaw) in enumerate(((-.067,.69,.867,1.1),(-.024,.96,.901,-1.4),
                                                           (.018,1.13,.943,1.5),(.061,.87,.916,-1.0))):
                key = f'park_pair_h{round(height * 1000):03}_{i}'
                step = replace(template, name=key, target=height, offset=offset, speed=speed, yaw=yaw,
                               cancel_delay_s=.09 if i % 2 else .13, restart_delay_s=wait)
                cases.extend((step, replace(step, name=f'{key}_wall', map_height=45 if i % 2 else 50)))
    if args.edge_stance_park_focus:
        template = restart_cases()[0]
        cases = []
        approaches = ((-.082, .73, .859, -1.2), (-.018, 1.04, .931, 1.8),
                      (.027, .86, .869, 2.2), (.071, 1.21, .949, -1.9))
        for height in (.28, .34):
            for index, (offset, wait, speed, yaw) in enumerate(approaches):
                name = f'park_edge_h{round(1000 * height):03}_{index}'
                step = replace(template, name=name, target=height, offset=offset, speed=speed, yaw=yaw,
                               cancel_delay_s=.07 if index % 2 else .12, restart_delay_s=wait)
                wall = replace(step, name=f'{name}_wall', map_height=45 if index % 2 else 50)
                cases.extend((step, wall))
    if args.mid_reverse_tread_focus:
        template = restart_cases()[0]
        cases = []
        setups = ((-.067, .67, .88, .10, 1.4), (-.044, .84, .91, .10, 0.),
                  (-.028, 1.16, .91, .13, -1.2), (.017, .79, .85, .09, 1.7),
                  (.046, 1.13, .94, .11, 0.), (.067, .96, .97, .14, -1.8))
        for height in (.332, .340, .348):
            for index, (offset, wait, speed, cancel, yaw) in enumerate(setups):
                name = f'mid_dwell_h{round(1000 * height)}_{index}'
                step = replace(template, name=name, target=height, offset=offset, speed=speed, yaw=yaw,
                               cancel_delay_s=cancel, restart_delay_s=wait)
                cases.extend((step, replace(step, name=f'{name}_wall', map_height=(45, 50)[index % 2])))
    if args.paired_park_focus or args.edge_stance_park_focus or args.mid_reverse_tread_focus:
        (args.out / 'CASES.json').write_text(json.dumps([vars(case) for case in cases], indent=2)+'\n', encoding='utf8')
    native_prefix = (args.low_stop_focus or args.varied_stop_focus or args.high_restart_focus or args.paired_park_focus)
    jobs = [(case, args.trials, args.out.resolve(), native_prefix) for case in cases]
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                             initargs=(args.candidate.resolve(),)) as pool:
        rows = []
        for group in pool.map(search, jobs):
            rows.extend(group)
            print([(row['name'], row['admitted'], round(row['steps'][0]['both_top_s'], 2),
                    row.get('restart', {}).get('backtrack_m')) for row in group], flush=True)
            (args.out / 'COLLECTION.json').write_text(json.dumps({'all_rollouts':rows}, indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    main()
