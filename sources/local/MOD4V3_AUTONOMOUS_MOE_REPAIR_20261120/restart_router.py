# SPDX-License-Identifier: MIT
"""Learn a stair-routing correction from proprioception after driving is resumed."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

LAGS = (0, 2, 4, 7, 10, 16, 24, 34, 46, 58, 72, 88, 106, 127, 143, 159)
WINDOW = LAGS[-1] + 1
FEATURES = (0, 2, 3, 5, 6, 7, 9, 11, 13, 15, 17, 20, 21)


class RestartRouter(nn.Module):
    def __init__(self):
        super().__init__()
        dimensions = 35 + len(LAGS) * len(FEATURES)
        self.register_buffer('obs_mean', torch.zeros(dimensions))
        self.register_buffer('obs_scale', torch.ones(dimensions))
        self.context_head = nn.Sequential(nn.Linear(len(LAGS), 48), nn.SiLU(), nn.Linear(48, 24), nn.SiLU(), nn.Linear(24, 1))
        self.route_head = nn.Sequential(nn.Linear(dimensions, 192), nn.SiLU(), nn.Linear(192, 96), nn.SiLU(), nn.Linear(96, 1))

    def forward(self, features):
        samples = features[:, 35:].reshape(-1, len(LAGS), len(FEATURES))
        context = self.context_head(samples[..., 0] * 3.).squeeze(-1)
        normalized = ((features - self.obs_mean) / self.obs_scale).clamp(-7., 7.)
        return context, self.route_head(normalized).squeeze(-1)

    @torch.inference_mode()
    def probability(self, history):
        obs = np.stack(history).astype(np.float32, copy=False)
        frame = np.maximum(len(obs) - 1 - np.asarray(LAGS), 0)
        features = np.concatenate((obs[-1], obs[frame][:, FEATURES].reshape(-1)))
        context, route = self(torch.from_numpy(features)[None])
        return float(context.sigmoid()[0]), float(route.sigmoid()[0])


class RestartSkillRouter(RestartRouter):
    """Predict a bounded symmetric action adjustment along with the restart gate."""

    def __init__(self):
        super().__init__()
        self.action_head = nn.Sequential(nn.Linear(len(self.obs_mean), 96), nn.SiLU(), nn.Linear(96, 3))

    def correction(self, features):
        normalized = ((features - self.obs_mean) / self.obs_scale).clamp(-7., 7.)
        return self.action_head(normalized).tanh() * 1.4

    @torch.inference_mode()
    def evaluate(self, history):
        obs = np.stack(history).astype(np.float32, copy=False)
        frame = np.maximum(len(obs) - 1 - np.asarray(LAGS), 0)
        features = torch.from_numpy(np.concatenate((obs[-1], obs[frame][:, FEATURES].reshape(-1))))[None]
        context, route = self(features)
        correction = self.correction(features)[0].numpy()
        return float(context.sigmoid()[0]), float(route.sigmoid()[0]), correction


def feature_rows(obs):
    indices = np.maximum(np.arange(len(obs))[:, None] - np.asarray(LAGS), 0)
    return np.concatenate((obs, obs[indices][:, :, FEATURES].reshape(len(obs), -1)), axis=1)


def dataset(folders):
    values = []
    sources = []
    for folder in folders:
        collection = folder / 'COLLECTION.json'
        if collection.is_file():
            entries = json.loads(collection.read_text('utf-8'))['all_rollouts']
        else:
            collection = folder / 'WASD.json'
            entries = json.loads(collection.read_text('utf-8'))['results']
        accepted = count = 0
        for entry in entries:
            restart = entry.get('restart')
            is_wall = entry.get('map_height_cm', 20) >= 45
            matched = restart is not None
            if matched and not is_wall and (not entry['admitted'] or entry['steps'][0]['first_held_from_s'] < restart['t']):
                continue
            if not matched and (entry['mode'] not in ('climb', 'flat', 'wall') or entry['fell']):
                continue
            if matched:
                # Failed wall trials say little about a safe zero-weight response.
                if entry['fell']:
                    continue
                accepted += 1
            path = folder / (entry['name'] + '.npz')
            with np.load(path, allow_pickle=False) as payload:
                obs = payload['obs'].astype(np.float32)
                u = payload['control'].astype(np.float32)
            near = np.zeros(len(obs), dtype=bool)
            labels = np.zeros(len(obs), dtype=np.float32)
            if matched:
                elapsed = u[:, 0] - restart['t']
                near = (elapsed >= -1e-4) & (elapsed <= 2.15) & (u[:, 13] > .5)
                labels = (u[:, 5] >= .72).astype(np.float32)
                if is_wall:
                    labels[elapsed >= .20] = 0.
            take = near | (np.arange(len(obs)) % 5 == 0)
            values.append((feature_rows(obs)[take], near[take], labels[take]))
            count += int(near.sum())
        sources.append({'file': str(collection), 'sha256': hashlib.sha256(collection.read_bytes()).hexdigest(),
                        'accepted_restarts': accepted, 'restart_frames': count})
    return tuple(torch.from_numpy(np.concatenate(v)) for v in zip(*values, strict=True)), sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', nargs='+', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--steps', type=int, default=2400)
    args = parser.parse_args()
    torch.manual_seed(21112026)
    torch.set_num_threads(1)
    (x, context, gate), sources = dataset(args.sources)
    context_positive = torch.where(context)[0]
    context_negative = torch.where(~context)[0]
    active = torch.where(context & (gate > .5))[0]
    inactive = torch.where(context & (gate <= .5))[0]
    model = RestartRouter()
    model.obs_mean.copy_(x.mean(0))
    model.obs_scale.copy_(x.std(0).clamp_min(.04))
    opt = torch.optim.AdamW(model.parameters(), lr=.0011, weight_decay=.01)

    def sample(ids, count):
        return ids[torch.randint(len(ids), (count,))]

    loss = None
    for _ in range(args.steps):
        selection = torch.cat((sample(active, 128), sample(inactive, 128), sample(context_positive, 128), sample(context_negative, 256)))
        score, route = model(x[selection])
        truth = context[selection].float()
        context_loss = F.binary_cross_entropy_with_logits(score, truth, weight=1. + 1.5 * (1. - truth))
        route_loss = F.binary_cross_entropy_with_logits(route[:256], gate[selection[:256]])
        loss = context_loss + route_loss
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    with torch.no_grad():
        decision, route = model(x)
        record = {'sources': sources, 'frames': len(x), 'context_positive': len(context_positive),
                  'active': len(active), 'steps': args.steps, 'final_loss': float(loss),
                  'context_false_active': int(((decision.sigmoid() > .75) & ~context).sum()),
                  'context_seen_restart_recall': float((decision[context].sigmoid() > .75).float().mean()),
                  'seen_restart_gate_accuracy': float(((route[context] > 0.) == (gate[context] > .5)).float().mean())}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'state_dict':model.state_dict(), 'fit':record}, args.out)
    record['sha256'] = hashlib.sha256(args.out.read_bytes()).hexdigest()
    args.out.with_suffix('.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf8')
    print(json.dumps(record), flush=True)


if __name__=='__main__':
    main()
