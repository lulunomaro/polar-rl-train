# SPDX-License-Identifier: MIT
"""Build the active climb and background gate anchor from qualified closed loops."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch


HISTORY = 40


def save_anchor(dirs: list[Path], output: Path) -> dict:
    data = {key: [] for key in ('obs', 'hist', 'act', 'gate', 'cmd', 'impact')}
    records = []
    for directory in dirs:
        for file in sorted(directory.glob('h*.npz')):
            entry = json.loads(file.with_suffix('.json').read_text(encoding='utf8'))
            if not entry['qualified']:
                continue
            with np.load(file, allow_pickle=False) as payload:
                obs = payload['obs'].astype(np.float32)
                executed = payload['act'].astype(np.float32)
                act = payload['teacher_act'].astype(np.float32) if 'teacher_act' in payload else executed
                gate = payload['gate'].astype(np.float32)
                cmd = payload['latent_cmd'][:, [0, 3]].astype(np.float32) if 'latent_cmd' in payload else obs[:, [0, 3]].copy()
            cmd[:, 1] /= 5.
            if not np.allclose(obs[1:, 22:28], executed[:-1], atol=1e-6):
                raise ValueError(f'Previous action does not match the real action in {file}')
            h = np.concatenate((np.repeat(obs[:1], HISTORY - 1, axis=0), obs))
            hist = np.stack([h[i:i + HISTORY].reshape(-1) for i in range(len(obs))])
            impact = np.zeros(len(obs), dtype=bool)
            if entry.get('selected_from') == 'trained teacher impact search':
                impact_start = np.flatnonzero(gate > .5)[0]
                impact[impact_start:impact_start + 19] = True
            values = {'obs': obs, 'hist': hist, 'act': act, 'gate': gate, 'cmd': cmd, 'impact': impact}
            for name, source in values.items():
                data[name].append(source)
            records.append({'source': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                            'height_m': entry['height_cmd'], 'frames': len(gate), 'active': int(gate.sum()),
                            'backtrack_m': entry['backtrack_m'], 'hold_frame': entry['hold_frame']})
    if not records:
        raise ValueError('No qualified records were collected')
    output.parent.mkdir(parents=True, exist_ok=True)
    tensors = {key: torch.from_numpy(np.concatenate(values)) for key, values in data.items()}
    torch.save(tensors, output)
    record = {'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'rollouts': len(records),
              'frames': len(tensors['obs']), 'active': int(tensors['gate'].sum()),
              'impact_frames': int(tensors['impact'].sum()), 'records': records}
    output.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('sources', type=Path, nargs='+')
    args = parser.parse_args()
    result = save_anchor(args.sources, args.out)
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}))


if __name__ == '__main__':
    main()
