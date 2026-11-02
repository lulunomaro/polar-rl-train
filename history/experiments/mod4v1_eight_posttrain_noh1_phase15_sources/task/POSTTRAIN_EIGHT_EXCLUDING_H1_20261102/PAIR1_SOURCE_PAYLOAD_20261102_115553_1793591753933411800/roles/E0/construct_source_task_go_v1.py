"""Pure stdlib Task/GO dictionary constructor, NOT an admission/GO issuer.

The original parent owns real evidence, locks, budget, JSON publication and its
original C ledger. This module accepts those joins as parameters and performs no
I/O in build_task_go(). main() writes ONLY one clearly MOCK source example,
with an expired epoch and an invalid owner PID; no TASK/GO/Ready/admission file.
"""
from pathlib import Path, PurePosixPath
import json
import math
from posttrain_fullstate_common_v1 import (EXPERTS, POSTTRAIN_KIND, USD_SHA, CONTRACT_SHA,
    CANONICAL_PATH, CANONICAL_GENERATION, require)


def build_task_go(role, *, job_root, run_id, role_key, GPU_UUID,
                  worker_SHA, common_SHA, descriptor_SHA, manifest_SHA,
                  root_admission_SHA, owner_parent_pid, learning_started_epoch,
                  max_additional_updates=20, max_parent_seconds=3900,
                  save_after_seconds=3600, exit_headroom_seconds=300,
                  manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json'):
    """Return dicts only; no file I/O, SDK/GPU/model read, budget check or GO issuance.

    Every SHA/UUID/owner/time input must come from the ORIGINAL parent's actual
    new job. Function output is not evidence that admission or budget passed.
    The runtime worker independently joins its actual parent admission and GO.
    """
    require(role in EXPERTS, 'Only E0/E2/E3; H1 excluded')
    cfg = EXPERTS[role]
    require(type(max_additional_updates) is int and 1 <= max_additional_updates <= 20, '1..20 actual finite cap')
    require(max_parent_seconds == save_after_seconds + exit_headroom_seconds
            and 0 < max_parent_seconds <= 3900 and save_after_seconds > 0 and exit_headroom_seconds >= 300,
            'Original finite save/exit window')
    require(type(learning_started_epoch) in (int, float) and math.isfinite(learning_started_epoch), 'Explicit original owner start epoch')
    root = PurePosixPath(job_root)
    require(root.is_absolute() and '..' not in root.parts, 'Declared absolute NEW remote job root')
    source_fields = ('source_SHA', 'source_bytes', 'source_iteration', 'source_Adam_step', 'source_LR',
                     'source_prior_new_PPO_updates', 'model_path')
    task = {key: cfg[key] for key in source_fields}
    task.update(kind=cfg['original_kind'], run_id=run_id, role_key=role_key, num_envs=20000,
        seed=20260928, steps_per_env=24, posttrain_kind=POSTTRAIN_KIND,
        source_read_purpose_label='NEW_POSTTRAIN_' + role + '_' + run_id,
        source_read_purpose=dict(physical_byte_opens=1, decodes=1, source_bytes=cfg['source_bytes']),
        max_additional_updates=max_additional_updates, asset_USD_SHA=USD_SHA, asset_contract_SHA=CONTRACT_SHA,
        closure_episode_m=.01, mimic_rad=.01, original_canonical_generation=CANONICAL_GENERATION,
        canonical_path=CANONICAL_PATH, GPU_UUID=GPU_UUID, asset_dir=str(root / 'runtime/assets'),
        worker_SHA=worker_SHA, posttrain_worker_file='worker_posttrain_' + role.lower() + '_v1.py',
        posttrain_common_SHA=common_SHA, posttrain_descriptor_file=role + '_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json',
        posttrain_descriptor_SHA=descriptor_SHA, manifest_file=manifest_file,
        root_admission_file='ROOT_ADMISSION_ACTUAL.json', root_admission_SHA=root_admission_SHA,
        max_parent_seconds=max_parent_seconds, save_after_seconds=save_after_seconds,
        exit_headroom_seconds=exit_headroom_seconds)
    go = dict(run_id=run_id, role_key=role_key, GPU_UUID=GPU_UUID, one_original_writer=True,
        source_model_SHA=cfg['source_SHA'], source_iteration=cfg['source_iteration'], input_Adam=cfg['source_Adam_step'],
        source_LR=cfg['source_LR'], source_qualification_kind=cfg['original_kind'],
        num_envs=20000, seed=20260928, steps_per_env=24, actor_obs=35, critic_obs=38, action_dim=6,
        physics_dt=.0025, TGS=[32, 4], policy_hz=50, feedback_hz=100,
        asset_USD_SHA=USD_SHA, asset_contract_SHA=CONTRACT_SHA,
        max_parent_seconds=max_parent_seconds, exit_headroom_seconds=exit_headroom_seconds,
        learning_started_epoch=learning_started_epoch, save_deadline=learning_started_epoch + save_after_seconds,
        nominal_end_epoch=learning_started_epoch + max_parent_seconds, original_owner_pid=owner_parent_pid,
        manifest_SHA=manifest_SHA, root_admission_SHA=root_admission_SHA,
        posttrain_kind=POSTTRAIN_KIND, posttrain_descriptor_SHA=descriptor_SHA,
        max_additional_updates=max_additional_updates)
    return task, go


def mock_examples():
    examples = {}
    for role in EXPERTS:
        task, go = build_task_go(role, job_root='/MOCK_SOURCE_ONLY_NOT_AN_ACTUAL_JOB/' + role,
            run_id='MOCK_NOT_ADMISSION_NOT_EXECUTABLE', role_key=role.lower() + '_MOCK_ONLY',
            GPU_UUID='MOCK_NOT_A_GPU', worker_SHA='0' * 64, common_SHA='0' * 64,
            descriptor_SHA='0' * 64, manifest_SHA='0' * 64, root_admission_SHA='0' * 64,
            owner_parent_pid=-1, learning_started_epoch=0.)
        examples[role] = dict(status='MOCK_SOURCE_DICTIONARIES_NOT_PUBLISHED_TASK_OR_GO', task_dictionary=task, go_dictionary=go)
    return dict(status='MOCK_SOURCE_CONSTRUCTION_EXAMPLE_NOT_ADMISSION_NOT_GO_NOT_READY',
        actual_original_owner_admission=False, actual_budget_check=False, actual_GPU_check=False,
        actual_SDK_or_model_or_PPO=False, published_Task_GO_or_Ready_files=False,
        expired_epoch_and_invalid_owner_PID_intentional=True, H1_excluded=True, roles=examples)


if __name__ == '__main__':
    target = Path(__file__).resolve().parent / 'MOCK_SOURCE_CONSTRUCTION_EXAMPLE_V1.json'
    with target.open('x', encoding='utf-8') as f:
        json.dump(mock_examples(), f, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps(dict(status='MOCK_SOURCE_EXAMPLE_ONLY_CREATED', path=str(target), actual_GO=False), indent=2))
