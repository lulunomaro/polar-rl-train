# SPDX-License-Identifier: MIT
"""Train a restart gate and bounded action correction from qualified exact-player rollouts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from restart_router import RestartSkillRouter, feature_rows


def select_corrections(records, modes, min_height, max_height):
    """Keep a single corrective target per initial state and operator sequence."""
    selected = {}
    for row in records:
        height = row['height_cmd_m']
        if (row['mode'] not in modes or not min_height <= height <= max_height
                or row['fell'] or not row.get('restart')):
            continue
        wall = row.get('map_height_cm', 20) > 20
        if not wall and not row['admitted']:
            continue
        name = row['name'].rsplit('_', 1)[0]
        backtrack = row['restart']['backtrack_m']
        delay = row['profile'][0]
        excess_pitch = max(row['peak_pitch_deg'] - 24., 0.)
        cost = backtrack + .06 * delay + .008 * excess_pitch
        if name not in selected or cost < selected[name][0]:
            selected[name] = (cost, row)
    return [row for _, row in selected.values()]


def read_data(candidate_folders, replay_folders, *, stop_only=False, high_restart=False, mid_stop=False):
    collected = []
    manifest = []
    for paired, folders in ((True, candidate_folders), (False, replay_folders)):
        for folder in folders:
            index = folder / ('COLLECTION.json' if paired else 'WASD.json')
            records = json.loads(index.read_text('utf8'))['all_rollouts' if paired else 'results']
            positives = walls = frames = 0
            if paired:
                if stop_only:
                    records = select_corrections(records, {'stop'}, .0, .34)
                if high_restart:
                    records = select_corrections(records, {'stop', 'reverse'}, .39, .43)
                if mid_stop:
                    records = select_corrections(records, {'stop'}, .33, .35)
            for row in records:
                restart = row.get('restart')
                wall = paired and row.get('map_height_cm', 20) > 20
                if paired and (not restart or row['fell'] or not (wall or row['admitted'])):
                    continue
                background_modes = ('climb', 'flat', 'wall', 'reverse', 'turn', 'turn_w') if stop_only or high_restart or mid_stop else ('climb', 'flat', 'wall')
                if not paired and (row['mode'] not in background_modes or row['fell']):
                    continue
                with np.load(folder / (row['name'] + '.npz'), allow_pickle=False) as trajectory:
                    obs = trajectory['obs'].astype(np.float32)
                    steps = trajectory['control'].astype(np.float32)
                if not np.allclose(obs[1:, 22:28], steps[:-1, 7:13], atol=1.e-6):
                    raise ValueError(f'Previous executed action mismatch: {row["name"]}')
                ctx = np.zeros(len(obs), dtype=bool)
                g = np.zeros(len(obs), dtype=np.float32)
                delta = np.zeros((len(obs), 3), dtype=np.float32)
                if paired:
                    delay, limit, mix, front, rear, wheel = row['profile']
                    t = steps[:, 0] - restart['t']
                    ctx = (t >= -1.e-5) & (t <= 3.2) & (steps[:, 13] > .5)
                    g[ctx] = steps[ctx, 5]
                    if wall:
                        walls += 1
                        # A short push was shared with the positive trajectories to make the
                        # later wall response observable. End the skill after the shared probe.
                        g[t >= min(delay + limit, .19) - 1.e-5] = 0.
                    else:
                        positives += 1
                        fit_action = ctx & (g >= .4) & (t >= delay - 1.e-5) & (t < delay + limit - 1.e-5)
                        fade = np.clip(1. - (t[fit_action] - delay) / .24, 0., 1.)
                        delta[fit_action] = fade[:, None] * np.array([front, rear, wheel], np.float32)
                take = ctx | (np.arange(len(ctx)) % 4 == 0)
                collected.append((feature_rows(obs)[take], ctx[take], g[take], delta[take]))
                frames += int(take.sum())
            manifest.append({'source':str(index), 'sha256':hashlib.sha256(index.read_bytes()).hexdigest(),
                             'qualified_restarts':positives,'wall_restarts':walls,'frames':frames,
                             'selected_rollouts': [row['name'] for row in records] if paired and (stop_only or high_restart or mid_stop) else None})
    data = tuple(torch.from_numpy(np.concatenate(values)) for values in zip(*collected, strict=True))
    return data, manifest


def train(data, device, steps):
    x, ctx, g, action = (t.to(device) for t in data)
    groups = [torch.where(ctx & (g >= .45))[0], torch.where(ctx & (g < .45))[0], torch.where(~ctx)[0]]
    if not all(len(ids) for ids in groups):
        raise ValueError('Need both active and inactive restart examples and ordinary cruising')
    model = RestartSkillRouter().to(device)
    model.obs_mean.copy_(x.mean(0))
    model.obs_scale.copy_(x.std(0).clamp_min(.04))
    opt = torch.optim.AdamW(model.parameters(), lr=.00095, weight_decay=.009)
    training_log = []
    for i in range(steps):
        indices = torch.cat([group[torch.randint(len(group), (n,), device=device)]
                             for group,n in zip(groups,(128,128,256),strict=True)])
        noisy = x[indices].clone()
        noisy[:, :28] += torch.randn_like(noisy[:, :28]) * .008 * model.obs_scale[:28]
        confidence, gate = model(noisy)
        residual = model.correction(noisy)
        truth = ctx[indices].float()
        ctx_loss = F.binary_cross_entropy_with_logits(confidence, truth, weight=2.0 - truth)
        gate_loss = F.binary_cross_entropy_with_logits(gate[:256], g[indices[:256]])
        action_loss = F.smooth_l1_loss(residual[:128],action[indices[:128]],beta=.12)
        loss = ctx_loss + gate_loss + action_loss
        if not torch.isfinite(loss):
            raise ValueError('Non-finite restart optimizer loss')
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1., error_if_nonfinite=True)
        opt.step()
        if i in (0, steps-1) or (i+1)%500==0:
            training_log.append({'optimizer_step':i+1,'loss':float(loss.detach())})
            print(training_log[-1],flush=True)
    with torch.no_grad():
        pred, gate = model(x)
        report = {'optimizer_steps':steps, 'batch_loss':training_log, 'rows':len(x),
                  'active':len(groups[0]), 'inactive':len(groups[1]), 'background':len(groups[2]),
                  'seen_context_recall':float((pred[ctx].sigmoid() >= .75).float().mean()),
                  'seen_false_context':int((pred[~ctx].sigmoid() >= .75).sum()),
                  'seen_gate_l1':float((gate[ctx].sigmoid()-g[ctx]).abs().mean())}
    return model.cpu(), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=Path, nargs='+', required=True)
    parser.add_argument('--background', type=Path, nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--steps', type=int, default=2600)
    parser.add_argument('--device', choices=('cpu','cuda'), default='cpu')
    focus = parser.add_mutually_exclusive_group()
    focus.add_argument('--stop-only', action='store_true', help='Fit renewed W after a low-stance stop.')
    focus.add_argument('--high-restart', action='store_true', help='Fit high-stance stops and reverse restarts.')
    focus.add_argument('--mid-stop', action='store_true', help='Fit paused mid-stance re-entry with paired tall walls.')
    args = parser.parse_args()
    torch.set_num_threads(1)
    torch.manual_seed(20261122)
    args.out.mkdir(parents=True, exist_ok=False)
    data, rows = read_data(args.pairs, args.background, stop_only=args.stop_only, high_restart=args.high_restart, mid_stop=args.mid_stop)
    model, report = train(data,args.device,args.steps)
    report['sources'] = rows
    target = args.out / 'restart_skill.pt'
    torch.save({'restart_action':True,'state_dict':model.state_dict(),'fit':report},target)
    report['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    (args.out / 'FIT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
