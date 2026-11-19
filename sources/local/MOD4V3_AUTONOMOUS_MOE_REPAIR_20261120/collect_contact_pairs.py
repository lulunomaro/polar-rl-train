# SPDX-License-Identifier: MIT
"""Collect matching stair and wall histories after a shared contact response."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path

os.environ.setdefault('MUJOCO_GL', 'disable')

import numpy as np
import torch

from play_repaired import HERE, AutonomousMapSimulation, RepairedSimulation, load_candidate, load_manifest, maps, stair
from verify_wasd import Case, run_case


SIM = None


class LabeledPolicy:
    """Training collector only; the deployed policy never receives the labels."""
    def __init__(self, model):
        self.model = model
        self.mix = 0.0

    def reset_history(self):
        self.model.reset_history()
        self.mix = 0.0

    @torch.inference_mode()
    def act(self, obs):
        x = torch.from_numpy(obs)[None]
        history = self.model.history.append(x)
        out = self.model.stair_outputs(x, history)
        action = torch.lerp(out['a_e0'], out['a_stair'], self.mix)[0].clamp(-6., 6.)
        return action.numpy(), {'e0': 1.0 - self.mix, 'e1': self.mix, 'e2': 0.0, 'g_prob': self.mix}


def initialize(expert, router, bank, manifest):
    global SIM
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'pair_contact_{os.getpid()}'
    if manifest is None:
        model, hashes = load_candidate(expert, router, stair_height_bank=bank)
        SIM = AutonomousMapSimulation(LabeledPolicy(model), hashes['package'], show_viewer=False)
        return
    model, hashes, prep = load_manifest(manifest)
    native_act = model.act
    model.oracle_mix = None

    @torch.inference_mode()
    def paired_act(obs):
        if model.oracle_mix is None or not model.allow_stair:
            return native_act(obs)
        current = stair.canonicalize_normal_obs(torch.from_numpy(obs)[None])
        history = model.history.append(current)
        outputs = model.stair_outputs(current, history)
        previous = model.stair_mix
        model.stair_mix = float(model.oracle_mix)
        action = torch.lerp(outputs['a_e0'], outputs['a_stair'], model.stair_mix)[0].numpy()
        action = np.clip(model.handoff_action(obs, action, previous, True), -6., 6.)
        return action, {'e0': 1. - model.stair_mix, 'e1': model.stair_mix,
                        'e2': 0., 'g_prob': model.stair_mix}

    model.act = paired_act
    SIM = RepairedSimulation(model, hashes['package'], show_viewer=False, jump_stance_prep=prep)


def record(task):
    case, out, level, low_probe_seconds, resume_delay, on_policy = task
    top_ticks = 0
    gate_off = False

    def label(sim, trace, now, keys):
        nonlocal top_ticks, gate_off
        mix = 0.
        first_hit = trace.hits[0] if trace.hits else None
        if first_hit is not None:
            if level is None:
                sim.unified.oracle_mix = None
                return
            elapsed = now - first_hit['t']
            if on_policy and resume_delay and elapsed < .08 + resume_delay:
                sim.unified.oracle_mix = None
                return
            if resume_delay and .08 <= elapsed < .08 + resume_delay:
                keys.discard('w')
                top_ticks = 0
            if resume_delay and elapsed >= .08 + resume_delay:
                elapsed -= resume_delay + .08
            if 'w' in keys:
                if case.mode == 'wall':
                    probe_time = low_probe_seconds if sim.target_h <= .365 else .35 if sim.target_h < .395 else 0.
                    mix = level if elapsed < probe_time else 0.
                else:
                    if len(trace.rows) >= 8:
                        support = np.asarray(trace.rows[-8:])[:, 13:15].mean(axis=0)
                        top_ticks = top_ticks + 1 if (support >= 5.).all() else 0
                        gate_off |= top_ticks >= 14
                    mix = level if not gate_off and elapsed < 2.35 else 0.
        if on_policy:
            sim.unified.oracle_mix = mix if first_hit is not None and level is not None else None
        else:
            sim.unified.mix = mix

    if on_policy:
        SIM.unified.oracle_mix = None
    result = run_case(SIM, case, out, before_step=label)
    result['probe_mix'] = level
    result['map_height_cm'] = case.map_height
    result['resume_delay_s'] = resume_delay
    result['on_policy_prefix'] = on_policy
    result['admitted'] = (case.map_height != 20 or
                          (result['steps'][0]['both_top_s'] >= .4 and not result['fell'] and
                           not result['steps'][0]['slid_back'] and
                           (result.get('restart', {}).get('backtrack_m', result['steps'][0]['backtrack_m']) or 0.)
                           <= (.32 if resume_delay else .14)))
    return result


def pool(out, results):
    grouped = {name: [] for name in ('obs', 'hist', 'gate', 'act', 'cmd', 'hard')}
    used = []
    for result in results:
        if not result['admitted']:
            continue
        file = out / (result['name'] + '.npz')
        with np.load(file, allow_pickle=False) as data:
            obs = data['obs'].astype(np.float32)
            u = data['control'].astype(np.float32)
        hit = result['steps'][0]['hit'] if result['steps'] else None
        ids = np.flatnonzero((u[:, 0] >= .32) & (u[:, 1] > .05))
        if hit:
            # Before-contact acceleration and late-wall frames are frequent distractors.
            pre = ids[u[ids, 0] < hit['t'] - .04][::4]
            near = ids[(u[ids, 0] >= hit['t'] - .04) &
                       (u[ids, 0] <= hit['t'] + 2.7 + result['resume_delay_s'])]
            ids = np.concatenate((pre, near))
        else:
            ids = ids[::4]
        h = np.concatenate((np.repeat(obs[:1], stair.HIST_LEN - 1, axis=0), obs))
        label = (u[ids, 5] > 0.5).astype(np.float32)
        hard = (hit is not None) & (result.get('map_height_cm', 20) >= 45) & (u[ids, 0] > (hit['t'] if hit else 0.)) & (label == 0.)
        if result['on_policy_prefix'] and result['map_height_cm'] >= 45 and 'restart' in result:
            after_resume = u[ids, 0] >= result['restart']['t'] + .24
            label[after_resume] = 0.
            hard |= after_resume
        values = dict(obs=obs[ids], hist=np.stack([h[i:i + stair.HIST_LEN].reshape(-1) for i in ids]),
                      gate=label, act=u[ids, 7:13], cmd=obs[ids][:, [0, 3]].copy(), hard=hard)
        values['cmd'][:, 1] /= 5.
        for name, value in values.items():
            grouped[name].append(value)
        used.append(dict(name=result['name'], map_height_cm=result['map_height_cm'],
                         class_name=result['mode'], frames=len(ids), active=int(label.sum())))
    packed = {name: torch.from_numpy(np.concatenate(segments)) for name, segments in grouped.items()}
    torch.save(packed, out / 'router_pairs.pt')
    return {'rollouts': used, 'frames': len(packed['obs']), 'positive_frames': int(packed['gate'].sum()),
            'hard_negative_frames': int(packed['hard'].sum())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stair', type=Path)
    parser.add_argument('--candidate', type=Path, help='Use the runtime handoff through the stop interval.')
    parser.add_argument('--router', type=Path)
    parser.add_argument('--stair-height-bank', type=Path)
    parser.add_argument('--expanded', action='store_true')
    parser.add_argument('--low-speed-pair', action='store_true')
    parser.add_argument('--resume-after-contact', type=float, default=0., metavar='SECONDS')
    parser.add_argument('--heights', type=float, nargs='+')
    parser.add_argument('--low-probe-seconds', type=float, default=.90)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    if args.candidate is None and args.stair is None and args.stair_height_bank is None:
        parser.error('Choose a stair expert, a height bank, or a player candidate')
    if args.candidate is not None and args.resume_after_contact <= 0:
        parser.error('The player candidate is for collecting post-cancel restarts')
    args.out.mkdir(parents=True, exist_ok=False)
    common_profiles = ((.90, 0., 0., False), (.76, -.05, 6., False), (.94, .04, -6., True), (.64, .05, 0., False))
    tasks = []
    heights = args.heights or ((.28, .32, .34, .36, .38, .39, .40, .42) if args.expanded else (.28, .32, .36, .38, .40, .42))
    if args.expanded:
        common_profiles += ((.90, -.06, 0., False), (.90, .06, 0., False), (.88, 0., -10., False), (.89, 0., 10., False))
    if args.low_speed_pair:
        common_profiles += ((.47, 0., 0., False), (.52, -.035, 4., True))
    for height in heights:
        for speed, offset, yaw, rise in common_profiles:
            on_policy = args.candidate is not None
            for size, mode in ((20, 'climb'), (45, 'wall'), (50, 'wall')):
                if on_policy:
                    levels = (None, 1., .68) if size == 20 else (None,)
                else:
                    levels = (1., .68) if size == 20 else (1.,)
                for level in levels:
                    route = 'auto' if level is None else f'{level:.2f}'
                    name = f'm{size}_h{height:.2f}_v{speed:.2f}_x{offset * 1000:+04.0f}_yaw{yaw:+.0f}_r{int(rise)}_g{route}'
                    tasks.append((Case(name, target=height, yaw=yaw, offset=offset, speed=speed, map_height=size,
                                       raise_while_moving=rise, mode='stop' if on_policy else mode,
                                       duration=7.0 + args.resume_after_contact if on_policy else 5.0 + args.resume_after_contact,
                                       cancel_delay_s=.08, restart_delay_s=args.resume_after_contact if on_policy else None),
                                  args.out, level, args.low_probe_seconds, args.resume_after_contact, on_policy))
    if len({task[0].name for task in tasks}) != len(tasks):
        raise ValueError('Each paired capture must have its own trace file')
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize,
                                     initargs=(args.stair, args.router, args.stair_height_bank, args.candidate)) as workers:
        results = list(workers.map(record, tasks, chunksize=1))
    final = pool(args.out, results)
    final['all_rollouts'] = results
    (args.out / 'COLLECTION.json').write_text(json.dumps(final, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print({k: v for k, v in final.items() if k.endswith('frames')}, flush=True)


if __name__ == '__main__':
    main()
