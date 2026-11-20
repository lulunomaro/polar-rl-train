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
HIGH_DIRECT = False
APEX_PROJECTION = None
JOINT_FLIGHT = False


def profiles(moving, high_direct, joint_flight=False):
    if high_direct:
        steps = [Case(f'direct_high_{i}', target=height, speed=speed, yaw=yaw,
                      offset=offset, mode='jump_step', duration=4.1, jump_distance_m=distance)
                 for i, (height, speed, yaw, offset, distance) in enumerate((
                     (.34,.88,-1.5,.025,.65),(.375,.96,2.,-.045,.625),(.405,.86,-2.5,.042,.69),(.42,.93,1.,-.055,.68)))]
        short_runups = [Case(f'direct_high_short_{i}', target=h, speed=speed, yaw=yaw, offset=x,
                        mode='jump_step', duration=5., drive_at_s=wait, jump_distance_m=distance)
                        for i, (h, speed, yaw, x, wait, distance) in enumerate((
                            (.409, .90, 2.8, .036, 1.35, .69), (.365, .97, -1.5, .027, 1.32, .71)))]
        flat = [Case('direct_high_flat', target=.40, speed=.92, mode='jump_moving', duration=3.6)]
        if joint_flight:
            flat += [Case('direct_tall_flat', target=.42, speed=.86, mode='jump_moving', duration=3.6)]
        return steps + short_runups + flat
    if moving:
        return [Case('train_move_medium', mode='jump_moving', target=.28, speed=.80, duration=3.5),
                Case('train_move_tall', mode='jump_moving', target=.42, speed=.94, duration=4.6),
                Case('train_jump_20', mode='jump_step', target=.28, speed=.90, duration=4.)]
    return [Case(f'train_still_{height:.2f}', mode='jump_idle', target=height, duration=4.7)
            for height in (.28, .34, .39)]


def prepare(candidate, moving, high_direct, projection=None, joint_flight=False):
    global SIM, LAYER, BASE, CASES, HIGH_DIRECT, APEX_PROJECTION, JOINT_FLIGHT
    HIGH_DIRECT = high_direct
    JOINT_FLIGHT = joint_flight
    APEX_PROJECTION = projection
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'jump_apex_{os.getpid()}'
    model, checks, prep = load_manifest(candidate)
    SIM = RepairedSimulation(model, checks['package'], show_viewer=False, jump_stance_prep=prep and not high_direct)
    expert = model.high_moving_jump if high_direct else model.moving_jump if moving else model.jump
    if expert is None:
        raise ValueError('The manifest must enable the jump head being optimized')
    LAYER = expert.delta_head[-1]
    BASE = {name: v.detach().clone() for name,v in LAYER.state_dict().items()}
    CASES = profiles(moving, high_direct, joint_flight)


def fit_apex_projection(candidate, high_direct, joint_flight=False, early_tuck=False):
    """Fit takeoff and tuck signals from the existing actor's hidden features."""
    prepare(candidate, moving=True, high_direct=high_direct, joint_flight=joint_flight)
    features = []
    targets = []
    weights = []
    for case in CASES:
        times = []
        activations = []

        def capture(_module, inputs):
            times.append(float(SIM.d.time))
            activations.append(inputs[0].detach().cpu().numpy().ravel())

        hook = LAYER.register_forward_pre_hook(capture)
        try:
            summary = run_case(SIM, case, None)['jump']
        finally:
            hook.remove()
        flight = summary['main_flight']
        if not flight or flight['duration_s'] < .18:
            continue
        # Rise after liftoff, peak before the apex, and fade before landing.
        phase = np.asarray(times) - summary['requested_at_s'] - flight['takeoff_s']
        if early_tuck:
            # The measured rim apex follows the body apex. Start the retraction
            # near the end of the extension and peak before the body descends.
            target = np.minimum(np.clip((phase + .065) / .068, 0., 1.),
                                np.clip((.145 - phase) / .075, 0., 1.))
        else:
            target = np.minimum(np.clip((phase - .01) / .05, 0., 1.), np.clip((.22 - phase) / .08, 0., 1.))
        if joint_flight:
            push = np.minimum(np.clip((phase + .14) / .07, 0., 1.), np.clip((-.008 - phase) / .045, 0., 1.))
            target = np.column_stack((target, push))
        hidden = np.asarray(activations, dtype=np.float64)
        features.append(np.column_stack((hidden, np.ones(len(hidden)))))
        targets.append(target)
        weights.append(np.where(phase < 0., 2.5, 1.))
    x, y, mask_weight = map(np.concatenate, (features, targets, weights))
    regularization = np.eye(x.shape[-1]) * .25
    weighted_targets = mask_weight[:, None] * y.reshape(len(y), -1)
    regression = np.linalg.solve(x.T @ (mask_weight[:, None] * x) + regularization, x.T @ weighted_targets)
    return regression.T.astype(np.float32)


def revised_last_layer(base, params, projection=None):
    parameters = torch.as_tensor(params, dtype=base['bias'].dtype)
    scale, bias = parameters[:6].reshape(2, 3)
    channels = [0, 1, 0, 1, 2, 2]
    weight = base['weight'] * (1. + scale[channels, None])
    offset = base['bias'] * (1. + scale[channels]) + bias[channels]
    if projection is not None:
        phase = torch.as_tensor(projection, dtype=weight.dtype).reshape(-1, weight.shape[1] + 1)
        residual = parameters[6:].reshape(-1, 3)[:, channels].T @ phase
        weight = weight + residual[:, :-1]
        offset = offset + residual[:, -1]
    return {'weight': weight, 'bias': offset}


def candidate_score(params):
    LAYER.load_state_dict(revised_last_layer(BASE, params, APEX_PROJECTION))
    measurements = []
    for case in CASES:
        report = run_case(SIM, case, out=None)
        jump = report['jump']
        step = report['steps'][0] if case.mode == 'jump_step' else None
        hold = step['both_top_s'] if step else None
        main = jump['main_flight'] or {}
        direct = None
        face = None if step is None else step['hit']
        if step is not None and JOINT_FLIGHT:
            takeoff = jump['requested_at_s'] + main['takeoff_s'] if main else None
            landing = step['first_dual_support_s']
            held = step['first_held_from_s']
            e2_end = jump['e2_last_at_s']
            e1_start = step['first_activation_s']
            direct = bool(takeoff is not None and e2_end is not None and landing is not None
                          and takeoff < landing <= e2_end + .02001 and hold >= .4 and not step['slid_back']
                          and (e1_start is None or e1_start > held + .40001))
            if takeoff is not None and face is not None and face['t'] >= takeoff:
                face = None
        measurements.append({'profile': case.name, 'height': main.get('clearance_m', 0.) if HIGH_DIRECT else jump['clearance_m'],
                             'backtrack': jump['max_backtrack_m'], 'face_hit': face, 'direct': direct,
                             'delay': main.get('takeoff_s'), 'slid': bool(step and step['slid_back']),
                             'air_pitch': main.get('peak_pitch_deg') if HIGH_DIRECT else jump['air_peak_pitch_deg'],
                             'land_pitch': jump['landing_peak_pitch_deg'], 'hold': hold, 'fell': report['fell']})
    heights = [row['height'] for row in measurements]
    score = (190. if JOINT_FLIGHT else 95.) * np.mean(heights) + 55. * min(heights)
    for row in measurements:
        flight, landing = row['air_pitch'], row['land_pitch']
        score -= 40. * row['backtrack']
        if flight is None or landing is None or row['fell']:
            score -= 35.
            continue
        score -= .28 * max(0., flight - 12.) + .34 * max(0., landing - 8.5)
        if row['hold'] is not None:
            score -= 26. * max(0., .40 - row['hold'])
        if JOINT_FLIGHT:
            score += 35. if row['direct'] else -32. if row['direct'] is False else 0.
            score -= .12 * max(0., flight - 13.) ** 2
        if HIGH_DIRECT:
            score -= 8. * max(0., (row['delay'] or .6) - .28)
            score -= 8. * bool(row['face_hit']) + 20. * row['slid']
            if row['hold'] is not None and row['hold'] >= .4 and not row['slid']:
                score += 18.
    return float(score), measurements


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--moving',action='store_true')
    parser.add_argument('--high-direct', action='store_true')
    parser.add_argument('--apex-tuck', action='store_true', help='Fit a flight-conditioned residual in the last layer.')
    parser.add_argument('--joint-flight', action='store_true', help='Fit the loaded push and preserve verified direct landing.')
    parser.add_argument('--early-tuck', action='store_true', help='Fit retraction at the end of the loaded extension.')
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--generations',type=int,default=4)
    parser.add_argument('--samples', type=int, default=18)
    args=parser.parse_args()
    if args.early_tuck and not args.joint_flight:
        parser.error('--early-tuck requires --joint-flight')
    if args.joint_flight and not args.apex_tuck:
        parser.error('--joint-flight requires --apex-tuck')
    if args.apex_tuck and not args.moving:
        parser.error('--apex-tuck requires --moving')
    if args.high_direct and not args.moving:
        parser.error('--high-direct requires --moving')
    args.out.mkdir(parents=True,exist_ok=False)
    _, paths=read_candidate(args.candidate)
    src=paths['high_moving_jump' if args.high_direct else 'moving_jump' if args.moving else 'jump']
    raw=torch.load(src,map_location='cpu',weights_only=True)
    state=raw.get('state_dict',raw.get('model_state_dict'))
    weight_key=next(k for k in reversed(list(state)) if k.startswith('actor_body.e_jump.delta_head.') and k.endswith('.weight'))
    bias_key=weight_key.removesuffix('.weight')+'.bias'
    base={'weight':state[weight_key].clone(),'bias':state[bias_key].clone()}
    rng=np.random.default_rng(20261120 if args.moving else 20261121)
    projection = fit_apex_projection(args.candidate, args.high_direct, args.joint_flight, args.early_tuck) if args.apex_tuck else None
    spread = np.array([.078, .074, .067, .14, .15, .12])
    bounds = np.array([.24, .24, .22, .44, .44, .36])
    minimum = np.array([.014, .014, .014, .025, .025, .025])
    if projection is not None:
        spread = np.r_[spread * .55, .28, .28, .13]
        bounds = np.r_[bounds * .55, .8, .8, .4]
        minimum = np.r_[minimum, .05, .05, .025]
        if args.joint_flight:
            spread = np.r_[spread, .29, .29, .10]
            bounds = np.r_[bounds, .80, .80, .30]
            minimum = np.r_[minimum, .05, .05, .018]
    mean = np.zeros(len(spread))
    ranked = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=prepare,
                             initargs=(args.candidate, args.moving, args.high_direct, projection, args.joint_flight)) as pool:
        for generation in range(args.generations):
            samples = rng.normal(mean, spread, (args.samples, len(spread)))
            params = [np.zeros(len(spread)), mean] + list(np.clip(samples, -bounds, bounds))
            if generation == 0 and args.early_tuck:
                for amount in (.25, .45, .65):
                    earlier = np.zeros(len(spread))
                    earlier[6:9] = (-amount, amount, 0.)
                    params.append(earlier)
            for vector,(score,metrics) in zip(params,pool.map(candidate_score,params),strict=True):
                ranked.append({'generation':generation,'params':vector.tolist(),'score':score,'measurements':metrics})
            ranked.sort(key=lambda row:row['score'],reverse=True)
            leader=ranked[0]
            elites=np.array([r['params'] for r in ranked[:6]])
            mean=elites.mean(0)
            spread = np.maximum(minimum, .90 * elites.std(0))
            report = {'candidate': str(args.candidate), 'weight_source': str(src), 'moving': args.moving,
                      'high_direct': args.high_direct, 'apex_tuck': args.apex_tuck, 'joint_flight': args.joint_flight,
                      'early_tuck': args.early_tuck,
                      'evaluated': len(ranked), 'scores': ranked}
            (args.out/'SEARCH.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(generation,leader,flush=True)
    for i, ranked_row in enumerate(ranked[:8]):
        new = revised_last_layer(base, ranked_row['params'], projection)
        state[weight_key]=new['weight']
        state[bias_key]=new['bias']
        raw['apex_fit']=ranked_row
        torch.save(raw,args.out/f'model_apex_{i:02}.pt')


if __name__=='__main__':
    main()
