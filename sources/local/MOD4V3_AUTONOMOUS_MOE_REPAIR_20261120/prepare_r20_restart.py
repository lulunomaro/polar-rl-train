# SPDX-License-Identifier: MIT
"""Build separate actor and gate anchors for the renewed-W training batch."""
from __future__ import annotations

import json
import shutil

import torch

import prepare_r15_stairs as anchors

EVIDENCE = anchors.EVIDENCE
OUT = EVIDENCE / 'r20restart'


def collect(folder, *, assisted):
    name, key = ('COLLECTION.json', 'all_rollouts') if assisted else ('WASD.json', 'results')
    rows = json.loads((folder / name).read_text(encoding='utf8'))[key]
    positive = {}
    negative = {}
    for row in rows:
        if not row.get('restart') or row['fell'] or not row['steps']:
            continue
        step = row['steps'][0]
        contact = step['hit']
        if contact is None:
            continue
        restart = row['restart']
        delay = restart['first_dual_hold_delay_s']
        if assisted:
            case = row['name'].rsplit('_', 1)[0]
        else:
            case = row['name']
        wall = row.get('map_height_cm', 50 if 'wall' in case else 20) > 20
        if wall:
            negative.setdefault(case, (folder, row, False, 6))
            continue
        if (delay is None or step['both_top_s'] < .4 or step['slid_back']
                or restart['backtrack_m'] > .18 or row['peak_pitch_deg'] > 34.):
            continue
        score = (restart['backtrack_m'], row['peak_pitch_deg'], delay)
        if case not in positive or score < positive[case][0]:
            positive[case] = (score, (folder, row, True, 7 if assisted else 10))
    return [pair for _, pair in positive.values()], list(negative.values())


def main():
    torch.set_num_threads(1)
    OUT.mkdir(exist_ok=False)
    anchors.OUT = OUT
    positive, negative = [], []
    for name, assisted in (('r19_rising/full', False), ('r16/varied_stop_dagger', True),
                           ('r17_high_restart_dagger', True)):
        samples, walls = collect(EVIDENCE / name, assisted=assisted)
        positive.extend(samples)
        negative.extend(walls)
    if len(positive) < 20 or len(negative) < 8:
        raise RuntimeError('Fewer qualified restart or wall rollouts than expected')
    parents = {'stair': EVIDENCE / 'r6/stair/model_warm.pt',
               'router': EVIDENCE / 'r4/router/model_final.pt'}
    reports = {}
    for role, parent in parents.items():
        shutil.copyfile(parent, OUT / f'start_{role}.pt')
        samples = positive + (negative if role == 'router' else [])
        reports[role] = anchors.build(role, EVIDENCE/'r17mid'/f'{role}_anchor.pt', samples,
                                      renewed_drive=True)
    plans = {
        'stair': dict(anchor_steps=1800, anchor_weight=7., actor_lr=1.15e-5,
                      dr_0_updates=44, dr_partial_updates=24, stair_restart_focus=True),
        'router': dict(anchor_steps=2000, anchor_weight=5., actor_lr=1.e-5,
                       dr_0_updates=40, dr_partial_updates=20, fit_router_encoder=True,
                       stair_restart_focus=True),
    }
    manifest = {role: {'path': path.relative_to(anchors.HERE).as_posix(), 'sha256': anchors.digest(path)}
                for role, path in parents.items()}
    for name, values in (('ANCHORS', reports), ('train_plan', plans), ('PARENTS', manifest)):
        (OUT / f'{name}.json').write_text(json.dumps(values, indent=2) + '\n', encoding='utf8')
    print(f'{len(positive)} qualified restarts, {len(negative)} wall negatives')
    print({role: (report['frames'], report['positive']) for role, report in reports.items()})


if __name__ == '__main__':
    main()
