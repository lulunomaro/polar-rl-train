# SPDX-License-Identifier: MIT
"""Construct independent low-speed E1 and contact-router training anchors."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import torch

from build_stair_anchor import HISTORY

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence'
OUT = EVIDENCE / 'r15stairs'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frames(folder, row, good, *, renewed_drive=False):
    trace = folder / (row['name'] + '.npz')
    with np.load(trace, allow_pickle=False) as data:
        obs = data['obs'].astype(np.float32)
        control = data['control'].astype(np.float32)
    if not np.allclose(obs[1:, 22:28], control[:-1, 7:13], atol=1e-6):
        raise ValueError(f'Previous executed action differs in {trace.name}')
    sequence = np.concatenate((np.repeat(obs[:1], HISTORY - 1, axis=0), obs))
    idx = np.flatnonzero((control[:, 0] >= .4) & (control[:, 13] > .5))
    step = row['steps'][0]
    active = control[:, 5] >= .55
    if good:
        hit = step['hit']['t']
        held = step['first_held_from_s']
        active &= (control[:, 0] >= hit - .02) & (control[:, 0] <= held + .65)
        # Do not anchor a later pull-back or overspeed after recovering support.
        idx = idx[control[idx, 0] <= held + .52]
    else:
        late = step['hit']['t'] + .26 if step['hit'] else 0.
        idx = idx[control[idx, 0] >= late]
        active[:] = False
    if renewed_drive:
        request = row['restart']['t']
        idx = idx[control[idx, 0] >= request - 1.e-4]
    idx = idx[active[idx] | (idx % 3 == 0)]
    active_idx = idx[active[idx]]
    impact_start = step['hit']['t'] if step['hit'] else -5.
    if renewed_drive and len(active_idx):
        impact_start = control[active_idx[0], 0]
    cmd = obs[idx][:, [0, 3]].copy()
    cmd[:, 1] /= 5.
    record = {'trace': trace.relative_to(HERE).as_posix(), 'sha256': digest(trace),
              'active_frames': int(active[idx].sum()), 'frames': len(idx)}
    fields = {'obs': obs[idx], 'hist': np.stack([sequence[k:k+HISTORY].reshape(-1) for k in idx]),
              'act': control[idx, 7:13], 'cmd': cmd, 'gate': active[idx].astype(np.float32),
              'hard': np.full(len(idx), not good), 'impact': active[idx] & (control[idx, 0] < impact_start + .35)}
    return {key: torch.from_numpy(value) for key, value in fields.items()}, record


def build(role, background, new, *, renewed_drive=False):
    raw = torch.load(background, map_location='cpu', weights_only=True)
    gen = torch.Generator().manual_seed(20261120)
    pos, neg = [(raw['gate'] > .5).nonzero().flatten(), (raw['gate'] <= .5).nonzero().flatten()]
    selection = torch.cat([group[torch.randperm(len(group), generator=gen)[:limit]]
                           for group, limit in ((pos, 4200), (neg, 4800))])
    parts, additions = [dict()], []
    for key in ('obs', 'hist', 'act', 'cmd', 'gate', 'hard', 'impact'):
        parts[0][key] = raw[key][selection] if key in raw else torch.zeros(len(selection), dtype=torch.bool)
    for folder, row, good, repeat in new:
        payload, report = frames(folder, row, good, renewed_drive=renewed_drive)
        if not len(payload['obs']):
            raise ValueError(f'No retained frames in {report["trace"]}')
        parts.extend([payload] * repeat)
        additions.append(report | {'weight': repeat})
    anchor = {key: torch.cat([part[key] for part in parts]) for key in parts[0]}
    if not torch.equal(anchor['obs'], anchor['hist'][:, -35:]):
        raise ValueError('A history does not end with its current observation')
    path = OUT / f'{role}_anchor.pt'
    torch.save(anchor, path)
    return {'source': background.relative_to(HERE).as_posix(), 'parent_sha256': digest(background),
            'sha256': digest(path), 'frames': len(anchor['obs']), 'positive': int(anchor['gate'].sum()), 'added': additions}


def main():
    torch.set_num_threads(1)
    OUT.mkdir(exist_ok=False)
    parents = {'stair': EVIDENCE/'r10/stair/model_warm.pt', 'router': EVIDENCE/'r7/router/model_final.pt'}
    for role, path in parents.items():
        shutil.copyfile(path, OUT / f'start_{role}.pt')
    legacy = EVIDENCE/'r13/legacy_stair_actor'
    # Each trace here was rerun in the same WASD plant. Remove the -30 mm
    # overspeed draw and truncate the others at the verified holding window.
    picked = []
    for row in json.loads((legacy/'EVAL.json').read_text(encoding='utf-8')):
        if row['name'] == 'legacy_stair_-0.03' or row['fell'] or row['steps'][0]['both_top_s'] < .4:
            continue
        picked.append((legacy, row, True, 6))
    visual = EVIDENCE/'r14/parked_video_glfw'
    found = json.loads((visual/'WASD.json').read_text(encoding='utf-8'))['results']
    positives = [row for row in found if row['name'] in ('restart_stop_h28', 'restart_stop_h32')
                 and not row['fell'] and row['steps'][0]['both_top_s'] >= .4]
    reference = EVIDENCE/'r13/player_full'
    negatives = [row for row in json.loads((reference/'WASD.json').read_text(encoding='utf-8'))['results']
                 if row['mode'] == 'wall' and not row['fell']]
    reports = {'stair': build('stair', EVIDENCE/'r10/stair_anchor.pt', picked),
               'router': build('router', EVIDENCE/'r11/router_anchor.pt',
                               [(visual, row, True, 4) for row in positives]
                               + [(reference, row, False, 2) for row in negatives])}
    plan = {'stair': dict(anchor_steps=1800, anchor_weight=8., actor_lr=1.25e-5, dr_0_updates=44,
                          dr_partial_updates=24, stair_high_slow_focus=True),
            'router': dict(anchor_steps=2200, anchor_weight=4.0, actor_lr=1.e-5, dr_0_updates=34,
                           dr_partial_updates=16, fit_router_encoder=True, stair_restart_focus=True)}
    for name, payload in (('train_plan',plan), ('ANCHORS', reports), ('PARENTS', {
            role: {'path': path.relative_to(HERE).as_posix(), 'sha256': digest(path)} for role, path in parents.items()})):
        (OUT / (name + '.json')).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print({role: (r['frames'], r['positive'], len(r['added'])) for role, r in reports.items()}, flush=True)


if __name__ == '__main__':
    main()
