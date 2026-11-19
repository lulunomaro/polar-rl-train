# SPDX-License-Identifier: MIT
"""Pin R11 parents and assemble the paired runtime and uninterrupted-climb anchors."""
from pathlib import Path
import json
import shutil

import numpy as np
import torch

from build_stair_anchor import HISTORY
from remote_repair import digest

HERE = Path(__file__).resolve().parent
E = HERE / 'evidence'
R11 = E / 'r11'
KEYS = ('obs', 'hist', 'act', 'gate', 'cmd', 'hard')


def reference_rows(folder):
    reference = folder / 'WASD.json'
    entries = json.loads(reference.read_text('utf-8'))['results']
    parts = []
    for row in entries:
        if row['mode'] not in ('climb', 'flat', 'wall') or row['fell'] or 'offset' in row['name'] and row['name'].startswith('low_speed'):
            continue
        step = row['steps'][0] if row['steps'] else None
        if row['mode'] == 'climb' and (step['both_top_s'] < .4 or step['slid_back']):
            continue
        with np.load(folder / (row['name'] + '.npz'), allow_pickle=False) as f:
            obs = f['obs'].astype(np.float32)
            control = f['control'].astype(np.float32)
        indices = np.flatnonzero((control[:, 0] >= .4) & (control[:, 1] > .05))
        hit = step['hit']['t'] if step and step['hit'] else None
        if hit is None:
            indices = indices[::4]
        else:
            frame_t = control[indices, 0]
            focus = (frame_t >= hit - .20) & (frame_t <= hit + 1.8)
            indices = np.sort(np.concatenate((indices[~focus][::4], indices[focus])))
        if not len(indices):
            continue
        seq = np.concatenate((np.repeat(obs[:1], HISTORY - 1, axis=0), obs))
        hard = (row['mode'] == 'wall') & (control[indices, 5] < .05)
        cmd = obs[indices][:, [0, 3]].copy()
        cmd[:, 1] /= 5.
        fields = {'obs': obs[indices], 'hist': np.stack([seq[i:i + HISTORY].reshape(-1) for i in indices]),
                  'gate': (control[indices, 5] > .5).astype(np.float32), 'act': control[indices, 7:13],
                  'cmd': cmd, 'hard': hard}
        parts.append({name: torch.from_numpy(value) for name, value in fields.items()})
    return {name: torch.cat([part[name] for part in parts]) for name in KEYS}


def main():
    inputs = {'stair': E/'r10/stair/model_warm.pt', 'router': E/'r10/router/model_final.pt', 'jump': E/'r10/jump/model_0032.pt'}
    parents = {}
    for role, source in inputs.items():
        shutil.copyfile(source, R11 / f'start_{role}.pt')
        parents[role] = {'path': str(source.relative_to(HERE)), 'sha256': digest(source)}
    paired = R11 / 'restart_runtime_pairs/router_pairs.pt'
    nominal = E / 'r9/wasd_full'
    r10_path = E / 'r10/router_anchor.pt'
    parts = [torch.load(path, map_location='cpu', weights_only=True) for path in (r10_path, paired)]
    parts.append(reference_rows(nominal))
    anchor = {name: torch.cat([part[name] for part in parts]) for name in KEYS}
    if not torch.equal(anchor['hist'][:, -35:], anchor['obs']):
        raise ValueError('Latest router observations differ from the history tail')
    router = R11 / 'router_anchor.pt'
    torch.save(anchor, router)
    record = [{'source': str(path.relative_to(HERE)), 'sha256': digest(path), 'frames': len(part['obs']),
               'positive': int(part['gate'].sum()), 'hard_negative': int(part['hard'].sum())}
              for path, part in zip((r10_path, paired, nominal/'WASD.json'), parts, strict=True)]
    (R11 / 'router_anchor.json').write_text(json.dumps({'source': record, 'sha256': digest(router)}, indent=2)+'\n', encoding='utf8')
    # The slow stair branch keeps its height/speed-specific DAgger pool. The restarted
    # taller profiles improve the router without asking the slow head to imitate 0.9 m/s.
    shutil.copyfile(E / 'r10/stair_anchor.pt', R11 / 'stair_anchor.pt')
    plan = {
        'stair': dict(anchor_steps=1500, anchor_weight=15., actor_lr=9.e-6, dr_0_updates=38, dr_partial_updates=26,
                      stair_high_slow_focus=True),
        'router': dict(anchor_steps=4800, anchor_weight=4.4, actor_lr=1.2e-5, dr_0_updates=36, dr_partial_updates=18,
                       fit_router_encoder=True, stair_restart_focus=True),
        'jump': dict(actor_lr=2.e-5, dr_0_updates=36, dr_partial_updates=24,
                     stance_dr=1, instant_moving_focus=True, jump_top_support=True),
    }
    (R11/'train_plan.json').write_text(json.dumps(plan, indent=2)+'\n', encoding='utf8')
    (R11/'PARENTS.json').write_text(json.dumps(parents, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'parents': parents, 'router_anchor': record}), flush=True)


if __name__ == '__main__':
    torch.set_num_threads(1)
    main()
