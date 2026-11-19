# SPDX-License-Identifier: MIT
"""Prepare exact-player mid-stance climb and wall anchors for separate experts."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import torch

import prepare_r15_stairs as anchors

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence'
OUT = EVIDENCE / 'r17mid'


def main():
    torch.set_num_threads(1)
    OUT.mkdir(exist_ok=False)
    anchors.OUT = OUT
    base = EVIDENCE / 'r14' / 'parked_full'
    held = EVIDENCE / 'r14' / 'held_out_driving'
    parent_models = {
        'stair': EVIDENCE / 'r6' / 'stair' / 'model_warm.pt',
        'router': EVIDENCE / 'r4' / 'router' / 'model_final.pt',
    }
    sources = []
    walls = []
    for folder in (base, held):
        report = json.loads((folder / 'WASD.json').read_text(encoding='utf-8'))
        for row in report['results']:
            if not row['steps'] or row['fell']:
                continue
            step = row['steps'][0]
            if not step['hit']:
                continue
            middle = .34 <= row['height_cmd_m'] <= .38
            if row['mode'] == 'climb' and middle and step['both_top_s'] >= .4 and not step['slid_back']:
                if step['backtrack_m'] < .10:
                    sources.append((folder, row, True, 16 if row['height_cmd_m'] == .36 else 9))
            elif row['mode'] == 'wall':
                walls.append((folder, row, False, 6 if middle else 2))
    if len(sources) < 6 or len(walls) < 6:
        raise ValueError('Expected physical successes and wall negatives in the exact-player runs')
    reports = {}
    for role, parent in parent_models.items():
        shutil.copyfile(parent, OUT / f'start_{role}.pt')
        reports[role] = anchors.build(role, EVIDENCE/'r11'/f'{role}_anchor.pt',
                                      sources + (walls if role == 'router' else []))
    parents = {role: {'path': parent.relative_to(HERE).as_posix(), 'sha256': anchors.digest(parent)}
               for role, parent in parent_models.items()}
    plans = {
        'stair': dict(anchor_steps=1600, anchor_weight=7., actor_lr=1.15e-5,
                      dr_0_updates=40, dr_partial_updates=20, stair_mid_stance_focus=True),
        'router': dict(anchor_steps=2000, anchor_weight=5., actor_lr=1.e-5,
                       dr_0_updates=35, dr_partial_updates=20, fit_router_encoder=True,
                       stair_mid_stance_focus=True, stair_restart_focus=True),
    }
    for name, payload in (('ANCHORS', reports), ('PARENTS', parents), ('train_plan', plans)):
        (OUT / f'{name}.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf8')
    print({role: (report['frames'], report['positive'], len(report['added']))
           for role, report in reports.items()}, flush=True)


if __name__ == '__main__':
    main()
