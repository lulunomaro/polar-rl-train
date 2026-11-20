# SPDX-License-Identifier: MIT
"""Build independent stair and router starts from matched WASD restart trials."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import torch

import prepare_r20_restart as restart


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    anchors = restart.anchors
    evidence = anchors.EVIDENCE
    paired = evidence / 'r25_parked/paired_dagger'
    good, walls = restart.collect(paired, assisted=True)
    if len(good) < 7 or len(walls) < 8:
        raise ValueError(f'Need paired data. Got {len(good)} successful step cases and {len(walls)} wall cases.')
    args.out.mkdir(parents=True, exist_ok=False)
    anchors.OUT = args.out
    archive = json.loads((paired/'COLLECTION.json').read_text(encoding='utf8'))['all_rollouts']
    used_names = {info[1]['name'] for info in good + walls}
    (args.out/'SELECTED_TRIALS.json').write_text(json.dumps([r for r in archive if r['name'] in used_names],
                                                           indent=2)+'\n', encoding='utf8')
    older_good, older_walls = restart.collect(evidence / 'r16/varied_stop_dagger', assisted=True)
    unique_ok = [sample for sample in older_good if sample[1]['height_cmd_m'] < .345]
    positive = good + [(folder, row, label, 3) for folder, row, label, _ in unique_ok]
    negative = walls + [(folder, row, label, 3) for folder, row, label, _ in older_walls]
    parents = {'stair': evidence / 'r6/stair/model_0032.pt',
               'router': evidence / 'r7/router/model_final.pt'}
    for role, source in parents.items():
        shutil.copyfile(source, args.out / f'start_{role}.pt')
    reports = {
        'stair': anchors.build('stair', evidence/'r17mid/stair_anchor.pt', positive, renewed_drive=True),
        'router': anchors.build('router', evidence/'r17mid/router_anchor.pt', positive + negative, renewed_drive=True),
    }
    plans = {
        'stair': dict(anchor_steps=1800, anchor_weight=10., actor_lr=1.25e-5, dr_0_updates=40,
                      dr_partial_updates=24, stair_low_stance_focus=True, stair_restart_focus=True),
        'router': dict(anchor_steps=1800, anchor_weight=8., actor_lr=1.15e-5, dr_0_updates=44,
                       dr_partial_updates=20, stair_low_stance_focus=True, stair_restart_focus=True, fit_router_encoder=True),
    }
    data = {
        'ANCHORS': reports,
        'train_plan': plans,
        'PARENTS': {role: dict(path=source.relative_to(anchors.HERE).as_posix(), sha256=anchors.digest(source))
                    for role, source in parents.items()},
    }
    for label, contents in data.items():
        (args.out / f'{label}.json').write_text(json.dumps(contents, indent=2)+'\n', encoding='utf8')
    print({role: (record['frames'], record['positive']) for role,record in reports.items()}, flush=True)


if __name__ == '__main__':
    main()
