# SPDX-License-Identifier: MIT
"""Compare contact handoff while relinquishing all stair action on the driver tick."""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path

import torch

from play_repaired import HERE, RepairedSimulation, load_manifest, stair
from verify_wasd import cases, run_case


class HandoffTrial(RepairedSimulation):
    def __init__(self, *args, **kwargs):
        self.handoff = 0.
        self.handoff_height = .42
        self.decay_s = .45
        self.direct_stop = False
        super().__init__(*args, **kwargs)
        original_action = self.unified.act

        @torch.inference_mode()
        def act(obs):
            prior_stair_weight = self.unified.stair_mix
            action, route = original_action(obs)
            if self.unified.allow_stair or route['e2']:
                self.handoff = 0.
                return action, route
            self.handoff = max(0., self.handoff - .02 / self.decay_s, prior_stair_weight)
            if self.handoff > 0. and 5. * self.handoff_height < obs[3]:
                current = stair.canonicalize_normal_obs(torch.from_numpy(obs)[None]).clone()
                current[:, 3] += self.handoff * (5. * self.handoff_height - current[:, 3])
                action = self.unified.stair.e0(current).clamp(-stair.ACTION_CLIP, stair.ACTION_CLIP)[0].numpy()
            return action, route

        self.unified.act = act

    def reset_at_spawn(self, spawn_idx=None):
        self.handoff = 0.
        return super().reset_at_spawn(spawn_idx)

    def step(self, pressed):
        if self.direct_stop and not self.paused and not pressed & {'w', 's'} and self.unified.stair_mix > .05:
            self.cmd_vx = 0.
        super().step(pressed)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--near-height', type=float, nargs='+', default=[.42])
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    policy, hashes, prep = load_manifest(HERE / 'CANDIDATE.json')
    sim = HandoffTrial(policy, hashes['package'], show_viewer=False, jump_stance_prep=prep)
    records = []
    profiles = [(.42, .45, False), (.42, .45, True), (.36, .38, True),
                (.34, .48, False), (.32, .40, True), (.32, .52, False)]
    for height, decay_s, direct_stop in profiles:
        sim.handoff_height, sim.decay_s, sim.direct_stop = height, decay_s, direct_stop
        for test in cases(quick=True):
            if test.mode not in ('stop', 'reverse', 'turn', 'turn_w'):
                continue
            for target in args.near_height:
                name = f'{test.name}_h{target:.2f}_ref{height:.2f}_d{decay_s:.2f}_s{int(direct_stop)}'
                stats = run_case(sim, replace(test, name=name, target=target), args.out)
                stats.update(ref_height=height, decay_s=decay_s, direct_stop=direct_stop)
                print(json.dumps(dict(name=name, override=stats.get('override'))), flush=True)
                records.append(stats)
                (args.out/'HANDOFF.json').write_text(json.dumps({'sha256': hashes, 'results': records}, indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    main()
