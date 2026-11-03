"""Inspect saved H1 evaluation motion after the attitude reward repair.

Reads existing pose/contact records only. No policy load, inference or physics.
The frozen production and evaluation packages are never changed.
"""
import argparse
import csv
import json
from pathlib import Path
import time

import numpy as np

from analyze_h1_saved_route import identity, load_case, read, reconstruct


def single(folder, pattern):
    paths = list(folder.glob(pattern))
    if len(paths) != 1:
        raise ValueError(f'Expected one {pattern} in {folder}; found {len(paths)}')
    return paths[0]


def inspect(args):
    reports = args.evaluation/'reports'
    source = single(reports, 'ROOT*_EVALUATION_FULL_RETURNED.json')
    replay_path = single(reports, 'ROOT*_SELECTED_REPLAY_TRANSFERS.json')
    full, receipt = read(source), read(replay_path)
    result = full['result']
    assert result['passed'] and receipt['passed']
    assert result['model_SHA'] == receipt['model_SHA']
    traces = [row for row in full['full_UTF8']
              if Path(row['path']).name.endswith('_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json')]
    assert len(traces) == 1
    manifold = json.loads(traces[0]['UTF8'])
    baseline = read(args.baseline_report)
    prior = {row['env']: row for row in baseline['detailed_cases']}
    shared = args.task_root/'RL455_FINAL_INDEPENDENT_EVAL_V456_20261102'
    with np.load(shared/'reference389.npz', allow_pickle=False) as packet:
        reference = {key: packet[key].copy() for key in packet.files}
    commands = np.asarray(read(shared/'feedforward389.json')['commands'])
    contract = read(args.task_root/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/assets/import_contract.json')
    hips = np.asarray([contract['joints'][side+'_hip']['local_pos0'] for side in ('left', 'right')])
    curves, cases, csv_rows = {}, [], []
    for row in receipt['cases']:
        env = row['env']
        packet = load_case(row)
        curve = reconstruct(packet, row, reference, commands, hips)
        if args.rotation == 'geodesic':
            replacement = (curve['geodesic']/args.attitude_scale)**2
            curve['cost'] += .5*(replacement-curve['terms']['rotation'])
            curve['terms']['rotation'] = replacement
            curve['reward'] = np.exp(-curve['cost']/5)
        if args.wheel_height:
            height = ((curve['wheel'][:, :, 2]-curve['wheel_reference'][:, :, 2])/.05)**2
            curve['terms']['wheel_world_height'] = height.mean(-1)
            curve['cost'] += curve['terms']['wheel_world_height']
            curve['reward'] = np.exp(-curve['cost']/5)
        if args.wheel_planar:
            planar = ((curve['wheel'][:,:,:2]-curve['wheel_reference'][:,:,:2])/.1)**2
            curve['terms']['wheel_world_planar'] = planar.sum(-1).mean(-1)
            curve['cost'] += curve['terms']['wheel_world_planar']
            curve['reward'] = np.exp(-curve['cost']/5)
        if args.target_limit:
            target = packet['motor_pos_target'][:, [1, 0, 4, 3]]
            lower, upper = np.asarray([-1.2, -.5, -1.2, -.5]), np.asarray([.9, .5, .9, .5])
            excess = np.maximum(lower-target, 0)+np.maximum(target-upper, 0)
            curve['terms']['leg_target_limit'] = (excess/.1)**2
            curve['terms']['leg_target_limit'] = curve['terms']['leg_target_limit'].mean(-1)
            curve['cost'] += curve['terms']['leg_target_limit']
        if args.reward_map == 'reciprocal':
            curve['reward'] = 1./(1.+curve['cost']/5.)
        errors = {key: float(value.mean()-row['result']['tracking_components'][key])
                  for key, value in curve['terms'].items()}
        assert max(map(abs, errors.values())) < .001, errors
        assert abs(float(curve['cost'].mean())-row['result']['tracking_cost_mean']) < .001
        assert abs(float(curve['reward'].mean())-row['result']['tracking_reward_mean']) < .001
        active_rows = [entry for entry in manifold['rows'] if entry['active'][env]]
        flight = [entry for entry in active_rows if entry['current_flight_id'][env] > 0]
        first_tick = flight[0]['tick'] if flight else None
        ground = [entry for entry in active_rows if first_tick is not None
                  and entry['tick'] > first_tick and max(entry['ground_force_N'][env]) > 1]
        ground_tick = ground[0]['tick'] if ground else None
        window = np.zeros(len(curve['t']), dtype=bool)
        if first_tick is not None:
            window = curve['t'] >= first_tick*.0025
            if ground_tick is not None:
                window &= curve['t'] < ground_tick*.0025
        bottom = (curve['wheel'][:, :, 2]-.0637).min(-1)
        i = min(19, len(curve['t'])-1)
        case = dict(env=env, controls=row['controls'], actual_lifetime_s=row['seconds'],
                    sample_seconds=float(curve['t'][i]),
                    yaw04_deg=float(np.rad2deg(curve['rpy'][i, 2])),
                    pitch04_deg=float(np.rad2deg(curve['rpy'][i, 1])),
                    geodesic04_rad=float(curve['geodesic'][i]),
                    first20_wheel_residual_rad_s=(curve['residual'][:20, 4:].mean(0)*10).tolist(),
                    first_air_predicate_s=first_tick*.0025 if first_tick is not None else None,
                    first_any_wheel_ground_force_over1N_after_air_s=ground_tick*.0025 if ground_tick is not None else None,
                    lower_wheel_bottom_peak_before_ground_m=float(bottom[window].max()) if window.any() else None,
                    forwardmost_wheel_center_before_ground_m=float(curve['wheel'][window, :, 0].max()) if window.any() else None,
                    reward_at_sample=float(curve['reward'][i]),
                    reward_reconstruction_error=errors,
                    baseline455=prior.get(env), actual_result=row['result'])
        curves[env] = curve
        cases.append(case)
        for k, seconds in enumerate(curve['t']):
            csv_rows.append([env, seconds, *curve['pos'][k], *curve['rpy'][k],
                             *curve['residual'][k, 4:]*10, bottom[k], curve['reward'][k]])
    summary = dict(first_episodes=result['first_episodes'], strict=result['strict_successes'],
                   wholeclear=sum(r['first_flight_whole_footprint_clear'] for r in result['results']),
                   leadingcross=sum(r['first_flight_both_cross'] for r in result['results']),
                   full8s=sum(r['full_window'] for r in result['results']),
                   terminations=result['terminations'],
                   mean_seconds=float(np.mean([r['seconds'] for r in result['results']])),
                   single_wheel_top_active_ticks=sum(bool(a and max(f)>1) for r in manifold['rows'] for a, f in zip(r['active'], r['top_force_N'])),
                   both_wheels_top_active_ticks=sum(bool(a and min(f)>1) for r in manifold['rows'] for a, f in zip(r['active'], r['top_force_N'])))
    args.output.mkdir(parents=True, exist_ok=False)
    csv_path = args.output/'motion_curves.csv'
    with csv_path.open('x', newline='', encoding='utf8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['env', 'seconds', 'root_x', 'root_y', 'root_z', 'roll_rad', 'pitch_rad', 'yaw_rad',
                         'wheel_L_residual_rad_s', 'wheel_R_residual_rad_s', 'lower_wheel_bottom_estimate_m', 'reward'])
        writer.writerows(csv_rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 2, figsize=(12, 11))
    prior_curves = np.genfromtxt(args.baseline_report.parent/'phase_aligned456_curves.csv', delimiter=',', names=True)
    for env, curve in curves.items():
        old = prior_curves[prior_curves['env'] == env]
        color = axes[0, 0].plot(curve['t'], np.rad2deg(curve['rpy'][:, 2]), label=f'env{env}')[0].get_color()
        axes[0, 0].plot(old['seconds'], np.rad2deg(old['yaw_rad']), '--', color=color, alpha=.5)
        axes[0, 1].plot(curve['t'], np.rad2deg(curve['rpy'][:, 1]), color=color, label=f'env{env}')
        axes[0, 1].plot(old['seconds'], np.rad2deg(old['pitch_rad']), '--', color=color, alpha=.5)
        axes[1, 0].plot(curve['t'], curve['residual'][:, 5]*10-curve['residual'][:, 4]*10, color=color, label=f'env{env}')
        axes[1, 0].plot(old['seconds'], old['wheel_R_residual_rad_s']-old['wheel_L_residual_rad_s'], '--', color=color, alpha=.5)
        axes[1, 1].plot(curve['t'], (curve['wheel'][:, :, 2]-.0637).min(-1), color=color, label=f'env{env}')
        axes[1, 1].plot(old['seconds'], old['lower_wheel_bottom_m'], '--', color=color, alpha=.5)
        axes[2, 0].plot(curve['pos'][:, 0], curve['pos'][:, 1], color=color, label=f'env{env}')
        axes[2, 0].plot(old['root_x'], old['root_y'], '--', color=color, alpha=.5)
        axes[2, 1].plot(curve['t'], curve['reward'], color=color, label=f'env{env}')
        axes[2, 1].plot(old['seconds'], old['original_reward'], '--', color=color, alpha=.5)
    axes[0, 0].axhline(np.rad2deg(.2), c='black', ls='--')
    axes[0, 0].axhline(-np.rad2deg(.2), c='black', ls='--')
    axes[1, 1].axhline(.27, c='black', ls='--')
    axes[2, 0].axvline(.8, c='black', ls='--')
    for ax, title in zip(axes.flat, ['Yaw (deg)', 'Pitch (deg)', 'Wheel residual R-L (rad/s)', 'Lower wheel bottom estimate (m)', 'Root route x/y (m)', 'Reward (different reward definitions)']):
        ax.set_title(title)
        ax.grid(alpha=.2)
        ax.legend()
        if ax is not axes[2, 0]:
            ax.set_xlim(0, 1.5)
            ax.set_xlabel('Time (s)')
    fig.suptitle(f"Saved actual RL: {summary['strict']}/{summary['first_episodes']} strict; dashed=prior455 (not paired DR causal proof)")
    fig.tight_layout()
    plot = args.output/'motion_curves.png'
    fig.savefig(plot, dpi=150)
    plt.close(fig)
    report = dict(epoch=time.time(), model_SHA=result['model_SHA'], rotation=args.rotation, attitude_scale=args.attitude_scale, wheel_height=args.wheel_height,
                  reward_map=args.reward_map, wheel_planar=args.wheel_planar, target_limit=args.target_limit,
                  source_result=identity(source), source_replay_receipt=identity(replay_path),
                  baseline_report=identity(args.baseline_report), baseline_csv=identity(args.baseline_report.parent/'phase_aligned456_curves.csv'), actual_all80=summary,
                  detailed_cases=cases, artifacts=[identity(csv_path), identity(plot)],
                  limits='Saved selected cases; not paired DR causal proof. Wheel center minus radius estimates do not replace actual footprint/manifold acceptance. Full nonwheel manifold was not recorded.',
                  operations=dict(model_reads=0, NN_inference=0, SDK=0, physics_steps=0, network=0))
    with (args.output/'analysis.json').open('x', encoding='utf8') as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps(dict(summary=summary, cases=cases, output=str(args.output)), ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evaluation', type=Path, required=True)
    parser.add_argument('--task-root', type=Path, required=True)
    parser.add_argument('--baseline-report', type=Path, required=True)
    parser.add_argument('--rotation', choices=['matrix', 'geodesic'], default='geodesic')
    parser.add_argument('--attitude-scale', type=float, default=.2)
    parser.add_argument('--wheel-height', action='store_true')
    parser.add_argument('--wheel-planar', action='store_true')
    parser.add_argument('--target-limit', action='store_true')
    parser.add_argument('--reward-map', choices=['exponential', 'reciprocal'], default='exponential')
    parser.add_argument('--output', type=Path, required=True)
    inspect(parser.parse_args())
