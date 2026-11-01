"""NEW E2/mod4v1 contract. Metadata-only validation; never issues GO or budget writes."""
from pathlib import Path
import hashlib
import json
import math
import os
import time

KIND = 'MOD4V1_E2_SELECTED42822_FULLD0D7_WORLD_SIGNED4_V1'
SOURCE_SHA = 'b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
SOURCE_BYTES = 14615089
ITER, ADAM, PRIOR_UPDATES = 42822, 859300, 92
LR = .00022500000000000002
CPU_SHA = 'd741414f54c22bff910541560e3af689f0c36afa507fb416e7beb7dd632468bb'
SOURCE_MODEL = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2/adaptation/final_valid_update92.pt'
USD_SHA = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT_SHA = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
CANONICAL = '/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GENERATION = 'MOD4_SINGLE_WRITER72_20261026'


def require(value, message):
    if not value:
        raise ValueError(message)


def read_json(path):
    p = Path(path)
    require(p.suffix == '.json' and not p.name.endswith(('.partial', '.active')), 'Complete metadata JSON required')
    raw = p.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def job_json(job, relative):
    p = (Path(job) / relative).resolve()
    require(p.is_relative_to(Path(job).resolve()), 'Metadata file must be inside this NEW job')
    return read_json(p)


def validate_new_job(task, go, args, job):
    """All passed facts below must come from ROOT actual receipts, not this source generator."""
    job = Path(job).resolve()
    require(args.mode == 'train' and args.num_envs == 20000, 'Original full 20k scope, no slice/repeat')
    require(args.out.resolve() == job / 'production', 'Own NEW production output only')
    require(args.run_id == task['run_id'] == go['run_id'], 'Original owner/run join')
    expected = dict(kind=KIND, num_envs=20000, source_SHA=SOURCE_SHA, source_bytes=SOURCE_BYTES,
                    source_iteration=ITER, source_Adam_step=ADAM, source_LR=LR,
                    source_prior_new_PPO_updates=PRIOR_UPDATES, model_path=SOURCE_MODEL,
                    saved_source_CPU_proof_SHA=CPU_SHA, asset_USD_SHA=USD_SHA,
                    asset_contract_SHA=CONTRACT_SHA, closure_episode_m=.01, mimic_rad=.01,
                    original_canonical_generation=GENERATION, canonical_path=CANONICAL,
                    source_read_purpose={'physical_byte_opens': 1, 'decodes': 1, 'source_bytes': SOURCE_BYTES})
    for key, value in expected.items():
        require(task[key] == value, 'NEW Task identity: ' + key)
    require(task['role_key'] == go['role_key'], 'ROOT actual role key join')
    require(go['one_original_writer'] is True and go['source_model_SHA'] == SOURCE_SHA, 'Original sole-writer GO')
    require(go['source_iteration'] == ITER and go['input_Adam'] == ADAM, 'GO selected source counters')
    require(go['source_qualification_kind'] == KIND, 'Never reuse old four-scalar Ready kind')
    for key, value in dict(num_envs=20000, actor_obs=35, critic_obs=38, action_dim=6,
                           physics_dt=.0025, TGS=[32, 4], policy_hz=50, feedback_hz=100,
                           asset_USD_SHA=USD_SHA, asset_contract_SHA=CONTRACT_SHA).items():
        require(go[key] == value, 'GO target scope: ' + key)
    require(os.environ.get('CUDA_VISIBLE_DEVICES') == task['GPU_UUID'], 'Actual parent-assigned GPU UUID')
    require(go['GPU_UUID'] == task['GPU_UUID'], 'GO/GPU identity; no historical GPU hardcode')
    parent, save, headroom = (task[k] for k in ('max_parent_seconds', 'save_after_seconds', 'exit_headroom_seconds'))
    require(all(type(x) in (float, int) and math.isfinite(x) and x > 0 for x in (parent, save, headroom)),
            'ROOT must supply a positive finite window')
    require(parent == save + headroom and parent <= 3900 and headroom >= 300,
            'No expansion beyond original one-hour/save-exit finite cap')
    require(go['max_parent_seconds'] == parent, 'Original parent finite cap join')
    require(go['save_deadline'] == go['learning_started_epoch'] + save, 'Actual owner save deadline')
    require(go['nominal_end_epoch'] == go['learning_started_epoch'] + parent, 'Actual owner terminal deadline')
    require(time.time() < go['save_deadline'], 'Expired GO is not reusable')

    evidence, eh = job_json(job, task['root_admission_file'])
    require(eh == task['root_admission_SHA'] == go['root_admission_SHA'], 'Actual ROOT admission hash join')
    require(evidence['kind'] == 'ROOT_MOD4V1_E2_ACTUAL_ADMISSION_V1', 'Explicit NEW evidence purpose')
    require(evidence['run_id'] == task['run_id'] and evidence['role_key'] == task['role_key'], 'Actual admission owner/role')
    require(evidence['asset_USD_SHA'] == USD_SHA and evidence['asset_contract_SHA'] == CONTRACT_SHA,
            'New asset was really probed, not historical 400N layer')
    for fact in ('new_asset_native0PT_passed', 'actual_target_source_and_SDK_admitted',
                 'actual_private_GPU_EX_held_by_original_parent', 'actual_original_shared_finite_env_SH_held',
                 'actual_fresh_GPU_and_host_resources_admitted',
                 'historical_E2_world_signed4_reset_command_and_DR_scope_exactly_reused',
                 'actual_current_canonical_owner_and_budget_admission_passed'):
        require(evidence[fact] is True, 'ROOT actual evidence required: ' + fact)
    require(evidence['GPU_UUID'] == task['GPU_UUID'], 'Actual resource UUID')
    canonical = evidence['canonical_binding']
    require(canonical['path'] == CANONICAL and canonical['generation'] == GENERATION, 'Original canonical only')
    require(canonical['owner_run_id'] == task['run_id'] and canonical['one_original_writer'] is True,
            'Other live writer must not be adopted by a new run')
    for key in ('actual_canonical_read_receipt_SHA', 'actual_lock_and_resource_receipt_SHA',
                'new_asset_native0PT_receipt_SHA', 'target_source_SDK_receipt_SHA',
                'historical_E2_world_signed4_scope_reuse_receipt_SHA'):
        value = evidence[key]
        require(isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value),
                'Actual receipt identity missing: ' + key)
    manifest, mh = job_json(job, task['manifest_file'])
    require(mh == go['manifest_SHA'], 'Original owner signs the complete NEW install manifest')
    require(manifest['kind'] == 'MOD4V1_E2_INSTALL_ACTUAL_V1', 'NEW install manifest kind')
    require(manifest['source_model_metadata']['SHA'] == SOURCE_SHA, 'Selected source metadata binding')
    require(manifest['asset_USD_SHA'] == USD_SHA and manifest['asset_contract_SHA'] == CONTRACT_SHA,
            'Installed asset metadata binding')
    ready, _ = job_json(job, task['ready_file'])
    ready_sha = hashlib.sha256(json.dumps(ready, indent=2).encode()).hexdigest()
    require(go['source_CPU_SHA'] == ready_sha, 'Original owner convention: hash of actual NEW Ready, not saved CPU proof')
    for key, value in dict(passed=True, kind=KIND, source_SHA=SOURCE_SHA,
                           source_iteration=ITER, Adam_step=ADAM, source_LR=LR,
                           saved_source_CPU_proof_SHA=CPU_SHA, asset_USD_SHA=USD_SHA,
                           asset_contract_SHA=CONTRACT_SHA, root_admission_SHA=eh, manifest_SHA=mh).items():
        require(ready[key] == value, 'ROOT actual NEW Ready binding: ' + key)
    require(all(not row['relative'].endswith(('.pt', '.partial', '.active')) for row in manifest['files']),
            'Source manifest must not masquerade a PT as copied source')
    index, ih = job_json(job, 'MOD4V1_DERIVATION_INDEX.json')
    require(ih == task['derivation_index_SHA'] == manifest['derivation_index_SHA'], 'Frozen derivation index join')
    require(index['kind'] == 'MOD4V1_E2_REVIEWABLE_SOURCE_ONLY_V1', 'Wrong source derivation kind')
    require(index['source_model_metadata']['SHA'] == SOURCE_SHA, 'Derivation selected source')
    for row in index['outputs']:
        if row['relative'].endswith(('.py', '.json', '.md', '.patch')):
            path = (job / row['relative']).resolve()
            require(path.is_relative_to(job), 'Derived source path escaped job')
            raw = path.read_bytes()
            require(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['SHA'],
                    'Derived source bytes changed after review: ' + row['relative'])
    return evidence


# Descriptions/types only. This is NOT an instantiated Task, GO or passed receipt.
REQUIRED_ROOT_INPUTS = {
    'status': 'SOURCE_ONLY_PARENT_MUST_JOIN_REAL_OWNER_RESOURCE_CANONICAL_AND_SDK_EVIDENCE',
    'Task_required': list(('run_id', 'role_key', 'asset_dir', 'GPU_UUID', 'worker_SHA', 'manifest_file', 'ready_file',
                           'root_admission_file', 'root_admission_SHA', 'derivation_index_SHA',
                           'max_parent_seconds', 'save_after_seconds', 'exit_headroom_seconds')),
    'Task_identity_checked_by_validate_new_job': 'kind/source counters/model path/CPU proof/asset SHA/clock/interface/canonical are the constants above',
    'GO_required': list(('run_id', 'role_key', 'GPU_UUID', 'one_original_writer', 'source_model_SHA',
                         'source_iteration', 'input_Adam', 'source_qualification_kind',
                         'manifest_SHA', 'root_admission_SHA', 'source_CPU_SHA', 'num_envs', 'actor_obs', 'critic_obs',
                         'action_dim', 'physics_dt', 'TGS', 'policy_hz', 'feedback_hz',
                         'asset_USD_SHA', 'asset_contract_SHA', 'learning_started_epoch',
                         'max_parent_seconds', 'save_deadline', 'nominal_end_epoch')),
    'ROOT_actual_receipt_required': list(('kind', 'run_id', 'role_key', 'GPU_UUID', 'asset_USD_SHA',
         'asset_contract_SHA', 'new_asset_native0PT_passed', 'actual_target_source_and_SDK_admitted',
         'actual_private_GPU_EX_held_by_original_parent', 'actual_original_shared_finite_env_SH_held',
         'actual_fresh_GPU_and_host_resources_admitted',
         'historical_E2_world_signed4_reset_command_and_DR_scope_exactly_reused',
         'actual_current_canonical_owner_and_budget_admission_passed', 'canonical_binding',
         'actual_canonical_read_receipt_SHA', 'actual_lock_and_resource_receipt_SHA',
         'new_asset_native0PT_receipt_SHA', 'target_source_SDK_receipt_SHA',
         'historical_E2_world_signed4_scope_reuse_receipt_SHA')),
    'NEW_Ready_required': ['passed', 'kind', 'source_SHA', 'source_iteration', 'Adam_step', 'source_LR',
                           'saved_source_CPU_proof_SHA', 'asset_USD_SHA', 'asset_contract_SHA',
                           'root_admission_SHA', 'manifest_SHA'],
    'canonical_binding_required': ['path', 'generation', 'owner_run_id', 'one_original_writer'],
    'not_generated': ['TASK.json', 'GO_PRODUCTION.json', 'ROOT actual receipt', 'canonical copy or write'],
}
