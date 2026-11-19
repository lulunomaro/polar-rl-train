# SPDX-License-Identifier: MIT
"""Build a hash-pinned WASD manifest next to the independent experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import os

from play_repaired import HERE, load_manifest, read_candidate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--set-model', action='append', default=[], metavar='EXPERT=PATH')
    parser.add_argument('--set', action='append', default=[], metavar='NAME=JSON')
    parser.add_argument('--label', required=True)
    parser.add_argument('--evidence', type=Path, action='append', default=[])
    args = parser.parse_args()
    if args.out.resolve().parent != HERE or args.out.exists():
        parser.error('Use a new manifest in the experiment directory')
    config, paths = read_candidate(args.base)
    config['label'] = args.label
    for item in args.set_model:
        role,sep,value = item.partition('=')
        if not sep or role not in ('stair', 'router', 'high_router', 'slow_stair', 'jump', 'moving_jump', 'restart_router', 'high_restart_router'):
            parser.error(f'Invalid model assignment {item!r}')
        path = Path(value).resolve()
        paths[role] = path
        config['sha256'][role] = digest(path)
    for item in args.set:
        name,sep,value = item.partition('=')
        if not sep:
            parser.error(f'Invalid setting {item!r}')
        config['settings'][name] = json.loads(value)
    config['checkpoints'] = {role:Path(os.path.relpath(path,HERE)).as_posix() for role,path in paths.items()}
    config['player_sha256'] = digest(HERE/'play_repaired.py')
    config['wasd_evidence'] = [Path(os.path.relpath(path.resolve(),HERE)).as_posix() for path in args.evidence]
    tmp = args.out.with_suffix('.tmp')
    tmp.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    try:
        policy, hashes, _ = load_manifest(tmp)
        config['runtime_sha256'] = policy.runtime_sha
        config['sha256'] = hashes
        tmp.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        tmp.replace(args.out)
    finally:
        tmp.unlink(missing_ok=True)
    print(config['runtime_sha256'],flush=True)


if __name__ == '__main__':
    main()
