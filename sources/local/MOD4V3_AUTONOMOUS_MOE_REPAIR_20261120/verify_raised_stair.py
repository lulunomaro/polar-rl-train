# SPDX-License-Identifier: MIT
"""High-stance checks through the interactive MOD4v3 policy and plant."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
import json
from pathlib import Path

import numpy as np

from play_repaired import HERE, RepairedSimulation, load_manifest
from verify_wasd import Case, run_case


def raised_cases():
    parked = Case('pair_7_step', target=.42, offset=-.027, yaw=-2.1, speed=.88,
                  mode='stop', cancel_delay_s=.10, restart_delay_s=1.04, duration=8.5)
    return [
        parked,
        replace(parked, name='pair_7_wall', map_height=50),
        Case('w_after_raise', target=.42, raise_while_moving=True, raise_at_s=0., drive_at_s=1.7),
        Case('near_w_after_raise', target=.42, offset=.75, yaw=-3., raise_while_moving=True,
             raise_at_s=0., drive_at_s=1.7),
        Case('near_center', target=.42, offset=.88, drive_at_s=1.65),
        Case('near_slow', target=.42, offset=.82, yaw=1.3, speed=.47, drive_at_s=1.60),
        Case('raised_reverse', target=.42, offset=.034, yaw=-3.5, speed=.87,
             mode='reverse', cancel_delay_s=.08, restart_delay_s=.7, duration=8.),
        Case('raised_stop_left', target=.42, offset=-.058, yaw=3.0, speed=.90,
             mode='stop', cancel_delay_s=.06, restart_delay_s=.74, duration=8.),
        Case('raised_stop_right', target=.42, offset=.052, yaw=-3., speed=.92,
             mode='stop', cancel_delay_s=.09, restart_delay_s=1.2, duration=8.),
        Case('raised_wall_retake', target=.42, offset=-.044, yaw=3.2, speed=.9,
             mode='stop', map_height=50, cancel_delay_s=.075, restart_delay_s=.76, duration=7.),
        Case('near_wall', target=.42, offset=.80, yaw=-3., raise_while_moving=True,
             raise_at_s=0., drive_at_s=1.7, mode='wall', map_height=50),
    ]


def holdout_cases():
    approaches = ((-.056, 0., .91, 1.62), (.048, 0., .89, 1.88), (-.027, 1.2, .93, 1.56),
                  (.039, -1.8, .88, 1.75), (.735, 0., .87, 1.73), (.685, 2.1, .91, 1.63),
                  (.775, -2.2, .89, 1.89), (.810, 2.4, .89, 1.80), (.720, 3.2, .94, 1.85),
                  (.700, -4., .94, 1.82))
    return [Case(f'ready_{idx}', target=.42, offset=offset, yaw=yaw, speed=speed, raise_while_moving=True,
                 raise_at_s=0., drive_at_s=drive, duration=7.)
            for idx, (offset, yaw, speed, drive) in enumerate(approaches)]


def manual_cases():
    # HUD key 4 sets .50 m/s. Test it and the normal .90 m/s gear after
    # standing up with E, including a short run-up and a skewed approach.
    matrix = [Case(f'gear4_x{mm:+03}', target=.42, speed=.50, offset=mm / 1000.,
                   raise_while_moving=True, raise_at_s=0., drive_at_s=1.75, duration=9.)
              for mm in (-60, -30, 0, 30, 60)]
    for speed in (.50, .90):
        gear = 4 if speed == .50 else 5
        matrix += [Case(f'gear{gear}_yaw{yaw:+03}', target=.42, yaw=yaw, speed=speed,
                        raise_while_moving=True, raise_at_s=0., drive_at_s=1.75, duration=9.)
                   for yaw in (-20, -10, 10, 20)]
        matrix += [Case(f'gear{gear}_near', target=.42, yaw=1.3, speed=speed, offset=.82,
                        raise_while_moving=True, raise_at_s=0., drive_at_s=1.75, duration=9.)]
    return matrix


def slider_cases():
    # The slider sends .42 immediately. The plant must settle while W is
    # released, unlike the gradual E-key standing-up sequence.
    return [Case(f'slider_gear{gear}_x{mm:+03}', target=.42, speed=speed, offset=mm / 1000.,
                 drive_at_s=1.5 + (mm + 60) / 150., duration=8.5)
            for gear, speed in ((4, .50), (5, .90)) for mm in (-60, -30, 0, 30, 60)]


def initialize(manifest):
    global sim
    policy, _, jump_prep = load_manifest(manifest)
    sim = RepairedSimulation(policy, policy.runtime_sha, show_viewer=False, jump_stance_prep=jump_prep)


def run(item):
    case, directory, videos = item
    result = run_case(sim, case, directory, video=case.name in videos)
    result['runtime_sha256'] = sim.unified.runtime_sha
    with np.load(directory / f'{case.name}.npz', allow_pickle=False) as data:
        physical = data['physical']
        controls = data['control']
    result['peak_horizontal_speed_m_s'] = float(np.linalg.norm(physical[:, 4:6], axis=1).max())
    hit = result['steps'][0]['hit']
    if hit is not None:
        before = physical[np.searchsorted(physical[:, 0], hit['t']) - 1]
        result['at_approach'] = dict(height_m=float(before[3]), vx_m_s=float(before[4]),
                                     pitch_deg=float(before[7]), yaw_deg=float(before[8]))
    if case.map_height > 24:
        interest_start = max(result['steps'][0]['hit']['t'] if result['steps'][0]['hit'] else 0.,
                             (result.get('restart') or {}).get('t', 0.)) + 1.
        result['late_wall_e1_peak'] = float(controls[controls[:, 0] >= interest_start, 5].max(initial=0.))
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=HERE / 'CANDIDATE.json')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case', nargs='+')
    parser.add_argument('--video', nargs='*', default=())
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--slow', action='store_true')
    parser.add_argument('--holdout', action='store_true')
    parser.add_argument('--manual', action='store_true')
    parser.add_argument('--slider', action='store_true')
    options = parser.parse_args()
    matrix = raised_cases() + [
        Case(f'held_h42_{mm:+03}', target=.42, offset=mm / 1000.) for mm in (-60, -30, 0, 30, 60)
    ]
    if options.slow:
        matrix += [Case(f'slow_h42_{mm:+03}', target=.42, speed=.47, offset=mm / 1000., duration=10.)
                   for mm in (-60, -30, 0, 30, 60)]
        matrix += [replace(case, name=f'{case.name}_slow', speed=.47, duration=10.)
                   for case in raised_cases() if case.mode in ('stop', 'reverse') and case.map_height == 20]
    if options.holdout:
        matrix += holdout_cases()
    if options.manual:
        matrix += manual_cases()
    if options.slider:
        matrix += slider_cases()
    if options.case:
        matrix = [case for case in matrix if case.name in options.case]
        if len(matrix) != len(options.case):
            parser.error('Each --case must match exactly one case name')
    directory = options.out.resolve()
    directory.mkdir(parents=True)
    results = []
    with ProcessPoolExecutor(options.workers, initializer=initialize,
                             initargs=(options.candidate.resolve(),)) as workers:
        for result in workers.map(run, ((case, directory, options.video) for case in matrix)):
            results.append(result)
            step = result['steps'][0]
            print(result['name'], 'support', step['both_top_s'], 'peak_vx', round(result['peak_vx_m_s'], 3),
                  'fell', result['fell'], 'slide', step['slid_back'], 'backtrack', round(step['backtrack_m'] or 0., 3),
                  'wall_gate', result.get('late_wall_e1_peak'), flush=True)
    report = dict(candidate=str(options.candidate.resolve()), cases=[asdict(case) for case in matrix], rows=results)
    (directory / 'RESULTS.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
