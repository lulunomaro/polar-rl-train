# SPDX-License-Identifier: MIT
"""Run the matched high-stance jump, slow stair and contact-recognition follow-up."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import os
from pathlib import Path
import shutil

import remote_repair as remote
from play_repaired import read_candidate

BATCH = 'r54_matched_wasd_r2'
FOLDER = remote.HERE / 'evidence' / BATCH


def prepare():
    FOLDER.mkdir(parents=True, exist_ok=False)
    base = FOLDER.parent
    manifest, installed = read_candidate(remote.HERE / 'CANDIDATE_R53_HIGH_TUCK.json')
    r52 = base / 'r52_contact_energy'
    r53 = base / 'r53_wasd_contact'
    parents = {
        'start_stair': r52 / 'stair/model_final.pt',
        'start_deployed_router': installed['high_router'],
        'start_router': installed['high_router'],
        'start_jump': installed['high_moving_jump'],
        'stair_anchor': r52 / 'stair_anchor.pt',
        'router_anchor': r52 / 'router_anchor.pt',
        'router_negatives': r53 / 'router_negatives.pt',
    }
    sources = {key: {'path': source.relative_to(remote.HERE).as_posix(), 'sha256': remote.digest(source)}
               for key, source in parents.items()}
    for key, manifest_key in [('start_deployed_router', 'high_router'), ('start_jump', 'high_moving_jump')]:
        if sources[key]['sha256'] != manifest['sha256'][manifest_key]:
            raise ValueError(f'Unexpected initial weights for {key}')
    for key, src in parents.items():
        shutil.copyfile(src, FOLDER / (key + '.pt'))
    earlier = json.loads((r52 / 'train_plan.json').read_text(encoding='utf8'))
    plan = {
        'stair': dict(earlier['stair'], dr_0_updates=48, dr_partial_updates=26, anchor_steps=48,
                      anchor_weight=6.0, actor_lr=7.e-6),
        # The high router is already strong on the standard stairs. Leave its encoder fixed.
        'router': dict(earlier['router'], dr_0_updates=44, dr_partial_updates=28, anchor_steps=96,
                       anchor_weight=8.5, actor_lr=4.e-6, fit_router_encoder=False),
        'jump': dict(earlier['jump'], dr_0_updates=48, dr_partial_updates=26, wasd_crouch_speed=.55,
                     anchor_weight=3.0, actor_lr=8.e-6, min_landing_apex=.22, jump_launch_energy=False),
    }
    for file, value in [('PARENTS.json', sources), ('train_plan.json', plan)]:
        (FOLDER / file).write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('stage', 'probe', 'launch', 'fetch'))
    args = parser.parse_args()
    storage = Path(os.environ.get('LOCALAPPDATA') or remote.HERE) / 'MOD4v3_Repair_Archive' / 'r54'
    storage.mkdir(parents=True, exist_ok=True)
    remote.archive = lambda batch: storage / f'{batch}-worker-bundle.tar.gz'
    with ThreadPoolExecutor(max_workers=3) as pool:
        if args.action == 'stage':
            if not (FOLDER / 'train_plan.json').exists():
                prepare()
            remote.pack(BATCH)
            jobs = [pool.submit(remote.stage, host, BATCH) for host in remote.HOSTS]
        elif args.action in ('probe','launch'):
            probe = args.action == 'probe'
            if not probe:
                for role in remote.ASSIGN:
                    info = remote.status(role, BATCH, probe=True)
                    report = info.get('PROBE.json', {})
                    if info.get('live') or not (report.get('zero_updates') and report.get('finite') and
                                               report.get('frames') == 700 and report.get('frozen_E0') == 0.):
                        raise RuntimeError(f'{role} probe has not finished successfully')
            jobs = [pool.submit(remote.launch, role, BATCH, 180 if probe else 620, 120, probe)
                    for role in remote.ASSIGN]
        else:
            jobs = [pool.submit(remote.status, role, BATCH, False, True) for role in remote.ASSIGN]
        for job in jobs:
            job.result()


if __name__ == '__main__':
    main()
