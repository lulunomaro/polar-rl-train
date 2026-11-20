# SPDX-License-Identifier: MIT
"""Prepare exact-player DAgger anchors for mid-height contact and renewed forward drive."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

import torch

from prepare_r20_restart import anchors, collect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collection', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    out = args.out.resolve()
    data = out / 'dwell_pairs'
    src = args.collection.resolve()
    cases = json.loads((src / 'CASES.json').read_text(encoding='utf8'))
    table = json.loads((src / 'COLLECTION.json').read_text(encoding='utf8'))['all_rollouts']
    if len({row['name'].rsplit('_', 1)[0] for row in table}) != len(cases):
        raise ValueError('Wait for all paired collection cases')
    shutil.copytree(src, data)
    positives, walls = collect(data, assisted=True)
    if len(positives) < 12 or len(walls) < 12:
        raise ValueError(f'Insufficient usable pairs: {len(positives)} stair, {len(walls)} wall')
    renewed = [(folder, row, good, 5) for folder, row, good, _ in positives]
    negatives = [(folder, row, good, 4) for folder, row, good, _ in walls]
    evidence = anchors.EVIDENCE
    start = {'stair': evidence / 'r5/stair/model_final.pt',
             'router': evidence / 'r7/router/model_final.pt'}
    common = dict(anchor_steps=650, dr_0_updates=44, dr_partial_updates=28,
                  stair_restart_focus=True, stair_low_stance_focus=True, parked_retake_focus=True,
                  wasd_restart_focus=True)
    plan = {'stair': dict(common, actor_lr=1.05e-5, anchor_weight=8.),
            'router': dict(common, actor_lr=9e-6, anchor_weight=10., fit_router_encoder=True)}
    anchors.OUT = out
    reports = {}
    for role, parent in start.items():
        shutil.copyfile(parent, out / f'start_{role}.pt')
        tail = negatives if role == 'router' else []
        reports[role] = anchors.build(role, evidence / f'r32_low_stair/{role}_anchor.pt', renewed + tail, renewed_drive=True)
    parents = {role: {'path': path.relative_to(anchors.HERE).as_posix(), 'sha256': anchors.digest(path)}
               for role, path in start.items()}
    for name, payload in (('train_plan', plan), ('ANCHORS', reports), ('PARENTS', parents)):
        (out / f'{name}.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf8')
    print({role: (report['frames'], report['positive'], len(report['added'])) for role, report in reports.items()})


if __name__ == '__main__':
    main()
