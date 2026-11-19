# SPDX-License-Identifier: MIT
"""Prepare the targeted high-stance climb, restart routing, and moving-jump seeds."""
from pathlib import Path
import json
import shutil

import torch

from build_stair_anchor import save_anchor
from remote_repair import LOCAL, digest

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence'
R10 = EVIDENCE / 'r10'


def prepare():
    files = {
        'stair': (EVIDENCE / 'r9/stair/model_warm.pt', 'b167bf22'),
        'router': (EVIDENCE / 'r7/router/model_final.pt', 'b78ae650'),
        'jump': (LOCAL / 'MOD4V3_AUTONOMOUS_MOE_ALL_MAPS_20261120/weights/model_instant_jump_best.pt', 'e2d83657'),
    }
    inputs = {}
    for role, (source, prefix) in files.items():
        sha = digest(source)
        if not sha.startswith(prefix):
            raise ValueError(f'Unexpected {role} parent SHA {sha}')
        dest = R10 / f'start_{role}.pt'
        shutil.copyfile(source, dest)
        inputs[role] = {'source': str(source.relative_to(LOCAL)), 'sha256': sha}

    skill = save_anchor([EVIDENCE / 'r9/high_slow_teacher', R10 / 'high_slow_on_policy'], R10 / 'stair_anchor.pt')
    source_paths = [EVIDENCE / 'r7/router_anchor.pt', R10 / 'restart_pairs/router_pairs.pt']
    parts = [torch.load(path, map_location='cpu', weights_only=True) for path in source_paths]
    keys = ('obs', 'hist', 'act', 'gate', 'cmd', 'hard')
    anchor = {}
    for key in keys:
        anchor[key] = torch.cat([part[key] if key in part else torch.zeros_like(part['gate'], dtype=torch.bool)
                                 for part in parts])
    if not torch.equal(anchor['obs'], anchor['hist'][:, -35:]):
        raise ValueError('Router observations must match the latest frame in each history')
    router_file = R10 / 'router_anchor.pt'
    torch.save(anchor, router_file)
    summary = {
        'sources': [{'path': str(path.relative_to(HERE)), 'sha256': digest(path), 'frames': len(part['gate']),
                     'positive': int(part['gate'].sum()),
                     'hard_negative': int(part['hard'].sum()) if 'hard' in part else 0}
                    for path, part in zip(source_paths, parts, strict=True)],
        'frames': len(anchor['gate']), 'positive': int(anchor['gate'].sum()),
        'hard_negative': int(anchor['hard'].sum()), 'sha256': digest(router_file),
    }
    (R10 / 'router_anchor.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    plan = {
        'stair': dict(anchor_steps=3200, anchor_weight=10., actor_lr=1.4e-5,
                      dr_0_updates=38, dr_partial_updates=28, stair_high_slow_focus=True, stair_restart_focus=True),
        'router': dict(anchor_steps=3500, anchor_weight=2.8, actor_lr=1.8e-5,
                       fit_router_encoder=True, stair_restart_focus=True),
        'jump': dict(actor_lr=1.8e-5, dr_0_updates=34, dr_partial_updates=28,
                     stance_dr=1, instant_moving_focus=True),
    }
    (R10 / 'train_plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    (R10 / 'PARENTS.json').write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'stair': {k: v for k, v in skill.items() if k != 'records'}, 'router': summary, 'parents': inputs}))


if __name__ == '__main__':
    torch.set_num_threads(1)
    prepare()
