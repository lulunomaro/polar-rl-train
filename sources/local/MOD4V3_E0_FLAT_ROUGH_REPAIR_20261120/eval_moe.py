"""Same R63 WASD ramp, routing, and 400 Hz contact tests with candidate E0 only."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import json
import os
from pathlib import Path

os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np
from play_e0_candidate import player, load_candidate
from verify_wasd import Case, run_case, takeover_cases, restart_cases
from verify_raised_stair import near_slow_cases

SIMULATION = None
RUNTIME_SHA = None


def profiles(quick):
    if quick:
        return [Case(f'formal_h42_x{mm:+03}', target=.42, speed=.47, offset=mm/1000., drive_at_s=1.45,
            retained_height_at_reset=True, duration=10.) for mm in (-60, -30, 0, 30, 60)] + [
            Case(f'normal_h{cm}', target=cm/100., retained_height_at_reset=True, drive_at_s=1.45)
            for cm in (28, 34, 42)] + [Case('rise_h42', target=.42, raise_while_moving=True, raise_at_s=.10),
            Case('direct_jump_h42', target=.42, mode='jump_step', jump_distance_m=.67, speed=.90, duration=5.8)]
    cases = profiles(True)
    cases.extend(Case(f'normal_h{cm}', target=cm/100., retained_height_at_reset=True, drive_at_s=1.45)
                 for cm in (32,36,40))
    cases.extend(Case(f'h42_takeover_{mode}', target=.42, mode=mode, duration=6., cancel_delay_s=.12,
                      drive_at_s=1.45, retained_height_at_reset=True) for mode in ('stop','reverse','turn_w'))
    cases.extend(near_slow_cases())
    cases.extend([Case('jump_idle', mode='jump_idle', duration=3.4),
                  Case('jump_moving', mode='jump_moving', duration=4.),
                  Case('double_h42', target=.42, duration=12., double=True),
                  Case('wall_h42', map_height=50, target=.42, duration=5., mode='wall')])
    cases.extend(takeover_cases())
    cases.extend(restart_cases())
    return cases


def initialize(manifest, output, baseline):
    global SIMULATION, RUNTIME_SHA
    player.maps.CACHE_DIR = output/'scene_cache'/str(os.getpid())
    if baseline:
        policy, _, prep = player.load_manifest(manifest)
    else:
        policy, _, prep = load_candidate(manifest)
    RUNTIME_SHA = policy.runtime_sha
    SIMULATION = player.RepairedSimulation(policy, RUNTIME_SHA, show_viewer=False, jump_stance_prep=prep)


def evaluate(item):
    case, output = item
    row = run_case(SIMULATION, case, output)
    with np.load(output / (case.name + '.npz'), allow_pickle=False) as trace:
        physical = trace['physical']
        control = trace['control']
        speed = np.linalg.norm(physical[:,4:6], axis=1)
        row['peak_horizontal_speed_m_s'] = float(speed.max(initial=0.))
        row['max_e1_weight'] = float(control[:,5].max(initial=0.))
        row['max_e2_weight'] = float(control[:,6].max(initial=0.))
    interval = row['steps'][-1] if row['steps'] else None
    row['physical_pass'] = bool(interval and interval['both_top_s'] >= .4 and not row['fell'] and not interval['slid_back'])
    row['formal_speed_pass'] = bool(row['physical_pass'] and row['peak_horizontal_speed_m_s'] <= .60 + 1e-9)
    row['runtime_sha256'] = RUNTIME_SHA
    return row


def main():
    parser = ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--cases', nargs='+', help='Match only cases with these name prefixes.')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    args.out.mkdir(parents=True)
    cases = profiles(args.quick)
    if args.cases:
        cases = [case for case in cases if any(case.name.startswith(prefix) for prefix in args.cases)]
        if not cases:
            parser.error('No cases matched --cases')
    rows = []
    with ProcessPoolExecutor(args.workers, initializer=initialize,
                             initargs=(args.manifest, args.out, args.baseline)) as pool:
        for row in pool.map(evaluate, [(case, args.out) for case in cases]):
            rows.append(row)
            print(row['name'], row['physical_pass'], row['fell'],
                  round(row['peak_horizontal_speed_m_s'],3), flush=True)
    (args.out/'RESULTS.json').write_text(json.dumps(dict(manifest=str(args.manifest), cases=list(map(asdict, cases)),
        rows=rows), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
