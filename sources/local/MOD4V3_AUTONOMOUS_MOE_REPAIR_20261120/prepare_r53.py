# SPDX-License-Identifier: MIT
"""Stage low-guide-contact, post-jump recognition, and moving-jump follow-up jobs."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
import torch

from play_repaired import read_candidate, stair
from prepare_r52 import subset
import remote_repair as remote

BATCH = 'r53_wasd_contact'


def landing_negatives(trace_directory, destination):
    records, obs_rows, hist_rows = [], [], []
    for path in sorted(trace_directory.glob('jump_moving_h*.npz')):
        with np.load(path, allow_pickle=False) as trace:
            obs = trace['obs'].astype(np.float32)
            controls = trace['control']
        if not np.allclose(obs[1:, 22:28], controls[:-1, 7:13], atol=1e-6):
            raise ValueError(f'Executed-action history mismatch in {path.name}')
        jump_ticks = np.flatnonzero(controls[:, 6] > .5)
        if not len(jump_ticks):
            continue
        last = jump_ticks[-1]
        ticks = np.arange(len(obs)) - last
        indices = np.flatnonzero((ticks > 0) & (ticks <= 26) & (controls[:, 13] == 1)
                                & ((ticks <= 12) | (controls[:, 4] >= .012)))
        padded = np.concatenate((np.repeat(obs[:1], stair.HIST_LEN - 1, axis=0), obs))
        obs_rows.extend(obs[indices])
        hist_rows.extend(padded[i:i + stair.HIST_LEN] for i in indices)
        records.append({'trace': path.name, 'sha256': remote.digest(path), 'frames': len(indices),
                        'above_gate_floor_frames': int(np.count_nonzero(controls[indices, 4] >= .05))})
    if len(obs_rows) < 10 or sum(row['frames'] > 0 for row in records) < 2:
        raise ValueError('Expected two or more flat landing traces with recognition false positives')
    obs = stair.canonicalize_normal_obs(torch.tensor(np.asarray(obs_rows)))
    hist = stair.canonicalize_normal_obs(torch.tensor(np.asarray(hist_rows))).flatten(1)
    native = len(obs)
    obs = torch.cat((obs, stair.mirror_obs_35(obs)))
    hist = torch.cat((hist, stair.mirror_hist_1400(hist)))
    if not torch.equal(obs, hist[:, -stair.OBS_DIM:]):
        raise ValueError('The last history frame must match the action observation')
    torch.save({'obs': obs, 'hist': hist}, destination)
    return {'frames': len(obs), 'native_frames': native, 'trace_records': records, 'sha256': remote.digest(destination)}


def low_contact_anchor(source, dest):
    data = torch.load(source, map_location='cpu', weights_only=True, mmap=True)
    height = data['obs'][:, 3] / 5.
    positive = data['gate'] > .5
    masks = ((height < .302) & positive, (height >= .302) & (height <= .35) & positive, ~positive)
    generator = torch.Generator().manual_seed(20261153)
    selected = []
    for mask, limit in zip(masks, (2800, 1600, 1800), strict=True):
        pool = torch.where(mask)[0]
        selected.append(pool[torch.randperm(len(pool), generator=generator)[:limit]])
    ids = torch.cat(selected)
    anchor = {key: value[ids] for key, value in data.items() if isinstance(value, torch.Tensor) and len(value) == len(height)}
    if not all(len(group) for group in selected) or not torch.equal(anchor['obs'], anchor['hist'][:, -35:]):
        raise ValueError('Invalid low-contact anchor')
    torch.save(anchor, dest)
    return {'parent_sha256': remote.digest(source), 'sha256': remote.digest(dest),
            'groups': [len(group) for group in selected], 'frames': len(ids)}


def save_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n', encoding='utf8')


def prepare(trace_directory, jump_seed):
    torch.set_num_threads(1)
    folder = remote.HERE / 'evidence' / BATCH
    folder.mkdir(exist_ok=True)
    if (folder / 'train_plan.json').is_file():
        raise FileExistsError(f'Keep the prepared batch: {folder}')
    evidence = folder.parent
    blueprint, files = read_candidate(remote.HERE / 'CANDIDATE_R52_SCOPED.json')
    bank = json.loads(files['stair_height_bank'].read_text(encoding='utf8'))
    assert bank[0]['height_m'] == .28
    parents = {
        'stair': (files['stair_height_bank'].parent / bank[0]['path']).resolve(),
        'router': files['high_router'],
        'deployed_router': files['router'],
        'jump': jump_seed.resolve(),
    }
    provenance = {}
    for role, src in parents.items():
        shutil.copyfile(src, folder / f'start_{role}.pt')
        provenance[role] = {'file': src.name, 'sha256': remote.digest(src)}
    for role, key in [('stair','stair_height_0.280'),('router','high_router'),('deployed_router','router')]:
        if provenance[role]['sha256'] != blueprint['sha256'][key]:
            raise ValueError(f'Unexpected parent for {role}')
    anchors = {'stair': low_contact_anchor(evidence / 'r32_low_stair/stair_anchor.pt', folder / 'stair_anchor.pt'),
               'router': subset(evidence / 'r49_mid_resume/router_anchor.pt', folder / 'router_anchor.pt', slow_stair=False),
               'landing_negatives': landing_negatives(trace_directory, folder / 'router_negatives.pt')}
    common = dict(stair_low_stance_focus=True, stair_restart_focus=True, parked_retake_focus=True,
                  wasd_restart_focus=True, dr_0_updates=45, dr_partial_updates=24)
    jump_plan = json.loads((evidence / 'r42_airborne_apex/train_plan.json').read_text(encoding='utf8'))['jump']
    plan = {
        'stair': dict(common, anchor_steps=64, actor_lr=8.e-6, anchor_weight=8.),
        'router': dict(common, anchor_steps=180, actor_lr=7.e-6, anchor_weight=6., stair_recovery_focus=True),
        'jump': dict(jump_plan, actor_lr=7.e-6, dr_0_updates=45, dr_partial_updates=24, anchor_weight=3., min_landing_apex=.22),
    }
    for name, payload in [('PARENTS', provenance), ('ANCHORS', anchors), ('train_plan', plan)]:
        save_json(folder / f'{name}.json', payload)
    print({'datasets': anchors, 'parents': provenance}, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare_probe', 'launch', 'fetch'))
    parser.add_argument('--scratch', type=Path)
    parser.add_argument('--seconds', type=int, default=540)
    parser.add_argument('--iters', type=int, default=108)
    options = parser.parse_args()
    with ThreadPoolExecutor(max_workers=3) as pool:
        if options.action == 'prepare_probe':
            if options.scratch is None:
                parser.error('Pass the directory containing the WASD traces and screened jump checkpoint')
            scratch = options.scratch.resolve()
            prepare(scratch / 'scoped/guard', scratch / 'moving_tuck/model_apex_04.pt')
            remote.archive = lambda batch: scratch / f'{batch}_bundle.tar.gz'
            remote.pack(BATCH)
            stages = [pool.submit(remote.stage, host, BATCH) for host in remote.HOSTS]
            for stage in stages:
                stage.result()
            jobs = [pool.submit(remote.launch, role, BATCH, 180, options.iters, True) for role in remote.ASSIGN]
        elif options.action == 'launch':
            for role in remote.ASSIGN:
                path = remote.HERE / 'evidence' / BATCH / f'{role}_probe/STATUS.json'
                probe = json.loads(path.read_text(encoding='utf8')).get('PROBE.json', {})
                if not (probe.get('zero_updates') and probe.get('finite') and probe.get('frames') == 700
                        and probe.get('frozen_E0') == 0.0):
                    raise ValueError(f'{role} training requires a successful zero-update probe')
            jobs = [pool.submit(remote.launch, role, BATCH, options.seconds, options.iters) for role in remote.ASSIGN]
        else:
            jobs = [pool.submit(remote.status, role, BATCH, False, True) for role in remote.ASSIGN]
        for job in jobs:
            job.result()


if __name__ == '__main__':
    main()
