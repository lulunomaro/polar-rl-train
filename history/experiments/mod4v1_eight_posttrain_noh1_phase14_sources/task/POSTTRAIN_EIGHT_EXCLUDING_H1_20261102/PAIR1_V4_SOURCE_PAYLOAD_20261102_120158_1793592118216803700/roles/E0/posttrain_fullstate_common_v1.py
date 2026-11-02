"""SOURCE-ONLY preparation: original E0/E2/E3 PPO, bounded <=20 new updates.

Importing this module uses stdlib only. main() is for a NEW parent-owned remote
job AFTER its original canonical owner has issued actual admission and GO.
No owner/ledger/GO implementation, SSH, GPU discovery, capacity tuning or SDK
substitute is supplied here. H1 has no entry. Local checks never call main().
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import os
import runpy
import sys
import time
import traceback

USD_SHA = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT_SHA = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
POSTTRAIN_KIND = 'MOD4V1_E0_E2_E3_ORIGINAL_PPO_FINITE20_FULLSTATE_SOURCE_V1'
ADMISSION_KIND = 'ROOT_MOD4V1_EIGHT_POSTTRAIN_ACTUAL_ADMISSION_V1'
CANONICAL_PATH = '/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
CANONICAL_GENERATION = 'MOD4_SINGLE_WRITER72_20261026'
EXPERTS = {
    'E0': dict(source_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',
               source_bytes=14031973, source_iteration=31984, source_Adam_step=641200,
               source_LR=.00038443359375000017, source_prior_new_PPO_updates=82,
               model_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt',
               original_manifest_SHA='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1',
               original_kind='MOD4V1_E0_SELECTED31984_FULLD0D7_FLAT_V1', command_kind=None),
    'E2': dict(source_SHA='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1',
               source_bytes=14615089, source_iteration=42822, source_Adam_step=859300,
               source_LR=.00022500000000000002, source_prior_new_PPO_updates=92,
               model_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2/adaptation/final_valid_update92.pt',
               original_manifest_SHA='ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f',
               original_kind='MOD4V1_E2_SELECTED42822_FULLD0D7_WORLD_SIGNED4_V1', command_kind='E2_WORLD_MOVING_SIGNED4'),
    'E3': dict(source_SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8',
               source_bytes=14715029, source_iteration=43090, source_Adam_step=866060,
               source_LR=.0002562890625000001, source_prior_new_PPO_updates=87,
               model_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt',
               original_manifest_SHA='ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f',
               original_kind='MOD4V1_E3_SELECTED43090_FULLD0D7_RECOVERY13_V1', command_kind='E3_PUBLIC_RECOVERY'),
}
COMMON_RECEIPTS = ('SENSOR_RESUME_STARTUP_VERIFIED.json', 'DELAY_RESUME_STARTUP_VERIFIED.json',
                   'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json', 'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json',
                   'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json', 'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json')
LIVE_KEYS = ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict', 'iter',
             'sensor_DR_state', 'sensor_recipe', 'sensor_global_rng_state',
             'sensor_command_DR_rng_state', 'sensor_physical_DR_rng_state',
             'feedback_delay_state', 'feedback_delay_recipe',
             'physical_action_delay_state', 'physical_action_delay_recipe',
             'spring_pressure_state', 'spring_pressure_recipe',
             'gas_damping_state', 'gas_damping_recipe', 'chassis_PD_state', 'chassis_PD_recipe')


def require(value, message):
    if not value:
        raise ValueError(message)


def read_json(path):
    p = Path(path)
    require(p.suffix == '.json', 'Complete JSON metadata only')
    return json.loads(p.read_bytes())


def nonmodel_hash(path):
    p = Path(path)
    require(p.suffix.lower() not in ('.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.partial'),
            'Metadata/source helper does not inspect model artifacts')
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inside(root, path):
    p = Path(path).resolve()
    require(p.is_relative_to(Path(root).resolve()), 'Owned output/metadata path escaped new job')
    return p


def put(path, value):
    p = Path(path)
    temporary = p.with_suffix(p.suffix + '.partial')
    with temporary.open('w', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    temporary.replace(p)


def merge_preserving_omitted(source, live):
    """Non-mutating recursive dictionary union; LIVE leaves always win.

    Lists/tuples/tensors are atomic leaves, never sliced/repeated. Unknown root
    and unknown nested dictionary entries survive. Known live cache/state roots
    must exist in the original save output BEFORE this union (validated below).
    This is preservation, NOT restoration of old physical episode histories over
    the current environment, and NOT a synthetic live-critic/optimizer restore.
    """
    if isinstance(source, dict) and isinstance(live, dict):
        result = dict(source)
        for key, value in live.items():
            result[key] = merge_preserving_omitted(source[key], value) if key in source else value
        return result
    return live


def omitted_paths(source, live, prefix=()):
    if isinstance(source, dict) and isinstance(live, dict):
        for key, value in source.items():
            if key not in live:
                yield prefix + (key,), value
            else:
                yield from omitted_paths(value, live[key], prefix + (key,))


def get_path(value, path):
    for key in path:
        value = value[key]
    return value


class FiniteStop(Exception):
    pass


class FiniteWindow:
    """Pure stdlib counter; never performs a PPO/optimizer operation itself."""
    def __init__(self, limit, deadline, stop_requested, clock=time.time):
        require(type(limit) is int and 1 <= limit <= 20, 'Original finite window: 1..20 additional updates')
        require(type(deadline) in (int, float) and math.isfinite(deadline), 'Finite owner save deadline')
        self.limit, self.deadline = limit, deadline
        self.stop_requested, self.clock = stop_requested, clock
        self.completed = self.optimizer_steps = self.controls = self.logged = 0
        self.update_in_progress = False

    def reason(self):
        if self.completed >= self.limit:
            return 'MAX_ADDITIONAL_UPDATES'
        if self.stop_requested():
            return 'ORIGINAL_OWNER_OR_HEALTH_SAVE_STOP'
        if self.clock() >= self.deadline:
            return 'ORIGINAL_OWNER_SAVE_DEADLINE'
        return None

    def before_update(self):
        # Original rescue policy finishes an already collected rollout/update and
        # stops at a COMPLETE save boundary; no new mid-update deadline policy.
        if self.completed >= self.limit:
            raise FiniteStop('MAX_ADDITIONAL_UPDATES')
        require(not self.update_in_progress, 'Nested original PPO update')
        self.update_in_progress = True

    def optimizer_step_returned(self):
        require(self.update_in_progress, 'Optimizer step outside original PPO update')
        self.optimizer_steps += 1

    def update_returned(self):
        require(self.update_in_progress, 'Missing original PPO update entry')
        self.completed += 1
        self.update_in_progress = False
        require(self.optimizer_steps == 20 * self.completed, 'Original 5 epochs x4 minibatches changed')
        require(self.completed <= self.limit, 'Finite update cap exceeded')

    def receipt(self):
        return dict(max_additional_updates=self.limit, actual_new_PPO_updates=self.completed,
                    actual_optimizer_step_calls=self.optimizer_steps, actual_training_controls=self.controls,
                    unfinished_rollout_controls=self.controls - 24 * self.completed,
                    original_20k_transitions=self.controls * 20000,
                    original_update_active_at_save=self.update_in_progress)


def validate_parent_join(role, task, go, descriptor, now):
    """Source identity contract only, not an owner/admission/GO issuer.

    main() ALSO checks actual EIGHT parent-admission/GO/install metadata below.
    Old role-specific admission protocols remain sealed/read-only; their old
    Ready kinds are NOT fabricated for this new eight-role purpose. Neither
    routine reads or writes the canonical ledger itself.
    """
    require(role in EXPERTS, 'Only E0/E2/E3 are implemented; H1 is excluded')
    cfg = EXPERTS[role]
    require(descriptor['status'] == 'SOURCE_ONLY_NOT_ADMISSION_NOT_GO', 'Source descriptor only')
    require(descriptor['expert'] == role and descriptor['posttrain_kind'] == POSTTRAIN_KIND, 'Role descriptor join')
    require(descriptor['pinned_source'] == cfg, 'Pinned complete source identity drift')
    require(task['kind'] == cfg['original_kind'], 'Unchanged original role protocol kind')
    require(task['posttrain_kind'] == go['posttrain_kind'] == POSTTRAIN_KIND, 'Explicit new posttraining purpose')
    require(task['source_read_purpose_label'].startswith('NEW_POSTTRAIN_' + role + '_'), 'New source read purpose')
    limit = task['max_additional_updates']
    require(type(limit) is int and 1 <= limit <= 20 and go['max_additional_updates'] == limit,
            'Original owner must issue finite <=20 cap in both Task and GO')
    require(descriptor['max_additional_updates_upper_bound'] == 20, 'Review descriptor upper bound')
    require(task['num_envs'] == go['num_envs'] == 20000, 'Whole original saved20k only')
    require(task['seed'] == go['seed'] == 20260928 and task['steps_per_env'] == go['steps_per_env'] == 24,
            'Original successful full20k constructor seed/rollout length explicitly bound')
    for key in ('source_SHA', 'source_bytes', 'source_iteration', 'source_Adam_step', 'source_LR', 'model_path'):
        require(task[key] == cfg[key], 'Selected source field ' + key)
    require(go['original_owner_pid'] == os.getppid(), 'GO must belong to actual direct original owner')
    require(type(go['original_owner_pid']) is int and go['original_owner_pid'] > 0, 'Actual original owner PID')
    require(now < go['save_deadline'] < go['nominal_end_epoch'], 'Original unexpired finite GO')
    require(task['exit_headroom_seconds'] >= 300, 'Original finite exit headroom')
    require(task['num_envs'] == descriptor['num_envs'] and descriptor['H1_training_enabled'] is False,
            'No N80 projection or H1 branch')


def validate_actual_parent_metadata(role, task, go, job, args):
    """Read only job-local parent ACTUAL receipts; never the canonical file."""
    cfg = EXPERTS[role]
    require(args.mode == 'train' and args.num_envs == 20000, 'Original whole20k train only')
    require(task['run_id'] == go['run_id'] == args.run_id and task['role_key'] == go['role_key'], 'Actual owner/run/role join')
    require(go['one_original_writer'] is True and go['source_model_SHA'] == cfg['source_SHA'], 'Original sole-writer source GO')
    require(go['source_iteration'] == cfg['source_iteration'] and go['input_Adam'] == cfg['source_Adam_step'], 'GO source counters')
    require(go['source_qualification_kind'] == cfg['original_kind'], 'Original source task identity')
    for key, value in dict(actor_obs=35, critic_obs=38, action_dim=6, physics_dt=.0025,
                           TGS=[32, 4], policy_hz=50, feedback_hz=100,
                           asset_USD_SHA=USD_SHA, asset_contract_SHA=CONTRACT_SHA).items():
        require(go[key] == value, 'GO plant/clock/interface: ' + key)
    for key, value in dict(asset_USD_SHA=USD_SHA, asset_contract_SHA=CONTRACT_SHA,
                           closure_episode_m=.01, mimic_rad=.01,
                           original_canonical_generation=CANONICAL_GENERATION, canonical_path=CANONICAL_PATH).items():
        require(task[key] == value, 'Task current plant/original authority metadata: ' + key)
    require(os.environ.get('CUDA_VISIBLE_DEVICES') == task['GPU_UUID'] == go['GPU_UUID'], 'Actual parent-selected UUID')
    parent, save, headroom = (task[k] for k in ('max_parent_seconds', 'save_after_seconds', 'exit_headroom_seconds'))
    require(all(type(x) in (int, float) and math.isfinite(x) and x > 0 for x in (parent, save, headroom)), 'Finite owner window')
    require(parent == save + headroom and parent <= 3900 and headroom >= 300, 'Original finite3900 maximum including >=300 exit')
    require(go['max_parent_seconds'] == parent and go['save_deadline'] == go['learning_started_epoch'] + save
            and go['nominal_end_epoch'] == go['learning_started_epoch'] + parent, 'Original owner absolute deadlines')
    admission_path = inside(job, job / task['root_admission_file'])
    require(admission_path.name == 'ROOT_ADMISSION_ACTUAL.json', 'Parent actual admission, no child source Ready')
    require(nonmodel_hash(admission_path) == task['root_admission_SHA'] == go['root_admission_SHA'], 'Actual root admission SHA join')
    admission = read_json(admission_path)
    require(admission['kind'] == ADMISSION_KIND, 'Explicit new EIGHT original-owner actual admission')
    for key in ('run_id', 'role_key', 'GPU_UUID', 'source_SHA', 'asset_USD_SHA', 'asset_contract_SHA'):
        require(admission[key] == task[key], 'Admission identity: ' + key)
    for key in ('actual_private_GPU_EX_held_by_original_parent', 'actual_original_shared_finite_env_SH_held',
                'actual_fresh_GPU_and_host_resources_admitted',
                'actual_current_canonical_owner_and_budget_admission_passed',
                'new_asset_native0PT_passed', 'actual_target_source_and_SDK_admitted'):
        require(admission[key] is True, 'Only original owner may assert actual admission: ' + key)
    binding = admission['canonical_binding']
    require(binding['path'] == CANONICAL_PATH and binding['generation'] == CANONICAL_GENERATION,
            'One existing authority, no new ledger')
    require(binding['owner_run_id'] == task['run_id'] and binding['owner_parent_pid'] == go['original_owner_pid'] == os.getppid()
            and binding['one_original_writer'] is True, 'Actual sole canonical parent identity metadata')
    for key in ('actual_canonical_read_receipt_SHA', 'actual_lock_and_resource_receipt_SHA',
                'new_asset_native0PT_receipt_SHA', 'target_source_SDK_receipt_SHA'):
        digest = admission[key]
        require(isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest),
                'Actual original-owner evidence digest: ' + key)
    manifest_path = inside(job, job / task['manifest_file'])
    require(nonmodel_hash(manifest_path) == go['manifest_SHA'], 'Actual parent-installed source manifest join')
    manifest = read_json(manifest_path)
    require(manifest['source_model_metadata']['SHA'] == cfg['source_SHA'], 'Installed selected-source metadata')
    require(manifest['asset_USD_SHA'] == USD_SHA and manifest['asset_contract_SHA'] == CONTRACT_SHA, 'Installed asset identity')
    for row in manifest['files']:
        relative = Path(row['relative'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'Owned installed source path')
        path = inside(job, job / relative)
        require(path.suffix.lower() not in ('.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.partial', '.pyc'), 'No model in source manifest')
        require(not path.name.upper().startswith('TRAINING_BUDGET'), 'No canonical copy as installed source')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['SHA'], 'Actual installed nonmodel bytes: ' + str(relative))
    # Reuse proof REFERENCES to prior whole20k SDK validation, but require the new
    # live restore + newly saved complete state below before any PPO/update claim.
    require(admission['prior_full20k_restore_proof_reused_as_history_only'] is True, 'Historical proof is not this new live restore')
    return admission


def original_receipts(role, log_dir, sha):
    names = list(COMMON_RECEIPTS)
    if role == 'E2':
        names.append('E2_COMMAND_RESUME_STARTUP_VERIFIED.json')
    if role == 'E3':
        names.append('E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json')
    rows = {}
    for name in names:
        p = Path(log_dir) / name
        row = read_json(p)
        require(row.get('source_sha256', row.get('source_SHA')) == sha, 'Live original helper source join: ' + name)
        rows[name] = dict(path=str(p), SHA=nonmodel_hash(p))
    if role == 'E2':
        require(read_json(Path(log_dir) / names[-1])['source_has_E2_command_state'], 'E2 original command state absent')
    if role == 'E3':
        require(read_json(Path(log_dir) / names[-1])['source_had_E3'], 'E3 original phase state absent')
    return rows


def assert_live_saved(torch, exact, value, runner, env, role, cfg, completed):
    required = set(LIVE_KEYS)
    if role == 'E2':
        required.add('E2_moving4_command_state')
    if role == 'E3':
        required.update(('E3_public_recovery_state', 'E3_reset_contract'))
    require(required.issubset(value), 'Original live save contract omitted roots: ' + str(sorted(required - set(value))))
    for key, obj in (('actor_state_dict', runner.alg.actor), ('critic_state_dict', runner.alg.critic),
                     ('optimizer_state_dict', runner.alg.optimizer)):
        require(exact(value[key], obj.state_dict()), 'Saved live core differs: ' + key)
    optimizer = value['optimizer_state_dict']
    require(len(optimizer['state']) == 17, 'Original 17 Adam states')
    require({int(v['step']) for v in optimizer['state'].values()} == {cfg['source_Adam_step'] + 20 * completed},
            'Saved Adam progress must equal actual completed original PPO updates')
    require(value['iter'] == cfg['source_iteration'] + completed, 'Saved completed-iteration label')
    require(all(g['lr'] == runner.alg.learning_rate for g in optimizer['param_groups']), 'Live adaptive/fixed original LR join')
    require(math.isfinite(float(runner.alg.learning_rate)) and runner.alg.learning_rate > 0, 'Finite actual original LR')
    from feedback_delay_runtime import delay_state
    from chassis_pd_checkpoint import current_state
    live = dict(sensor_DR_state=env._sensor_mild.state_dict(), feedback_delay_state=delay_state(env).state_dict(),
                physical_action_delay_state=env._physics_action_delay.state_dict(),
                spring_pressure_state=env._spring_pressure.state_dict(), gas_damping_state=env._gas_damping.state_dict(),
                chassis_PD_state=current_state(env))
    for key, state in live.items():
        require(exact(value[key], state), 'Saved current complete history/RNG/queue differs: ' + key)
    for key, obj in (('sensor_command_DR_rng_state', env.command_manager.get_term('twist')),
                     ('sensor_physical_DR_rng_state', env._mild_dr)):
        for name, saved in value[key].items():
            require(torch.equal(saved.cpu(), getattr(obj, name).get_state().cpu()), 'Saved private RNG: ' + key + '/' + name)
    require(torch.equal(value['sensor_global_rng_state']['cpu'].cpu(), torch.random.get_rng_state().cpu()), 'Live CPU RNG save')
    require(exact(value['sensor_global_rng_state']['cuda'], torch.cuda.get_rng_state_all()), 'Live global CUDA RNG save')
    if role == 'E2':
        from e2_command_checkpoint_v1 import current
        require(exact(value['E2_moving4_command_state'], current(env.command_manager.get_term('twist'))), 'E2 live nine fields and mode RNG')
    if role == 'E3':
        from e3_fullstate_checkpoint_v1 import state
        require(exact(value['E3_public_recovery_state'], state(env)), 'E3 live seven phase fields and command RNG')
        require(exact(value['E3_reset_contract'], env.e3_reset_receipt), 'E3 declared fixed13 reset provenance')


def prepare_original_environment(role, job, production, cfg, go):
    original = read_json(job / 'original_run_manifest.json')
    require(nonmodel_hash(job / 'original_run_manifest.json') == cfg['original_manifest_SHA'], 'Frozen original environment manifest')
    require(original['terrain'] == 'flat' and original['skill_tasks'] == 'all', 'Original expert task scope')
    for key in list(os.environ):
        if key.startswith(('RM_', 'MOD4V1_', 'MOD4_RESUME_')) or key in (
                'OWN_E2_H1_KIND', 'RANK', 'WORLD_SIZE', 'LOCAL_RANK', 'MASTER_ADDR', 'MASTER_PORT'):
            del os.environ[key]
    env = {k: str(v) for k, v in original['env'].items() if k not in ('RM_RESCUE_DEADLINE', 'RM_RESCUE_STOP_FILE')}
    require(env['RM_KEEP_STD'] == '1' and env['RM_PHYSICS_DT_S'] == '0.0025'
            and env['RM_SOLVER_POS'] == '32' and env['RM_SOLVER_VEL'] == '4', 'Original STD/clock/TGS')
    env.update(RM_MOD4_USD=str(job / 'runtime/assets/robot.usd'),
               RM_RESCUE_DEADLINE=str(go['save_deadline']), RM_RESCUE_STOP_FILE=str(production / 'STOP_AFTER_SAVE.json'))
    # Exact original full20k/E2/E3 successful worker overrides, not new rewards.
    if role in ('E2', 'E3'):
        env.update(RM_SPAWN_GRACE_STEPS='5', OWN_E2_H1_KIND=cfg['command_kind'], RM_JUMP_SCRIPT_PROB='0',
                   RM_MOD4_MAP='', RM_MOD4_TERRAIN='flat')
    require(env['RM_JUMP_SCRIPT_PROB'] == '0' and env['RM_MOD4_TERRAIN'] == 'flat', 'No H1/jump task substitution')
    os.environ.update(env)
    os.environ['MOD4_RESUME_QUEUE_CONTROL_US'] = '20000'
    prefix = 'MOD4V1_' + role + '_'
    os.environ[prefix + 'ASSET_DIR'] = str(job / 'runtime/assets')
    os.environ[prefix + 'JOB_ROOT'] = str(job)
    storage = job / 'kit_isolation'
    storage.mkdir(exist_ok=False)
    (storage / 'data').mkdir()
    (storage / 'DerivedDataCache').mkdir()
    (storage / 'data/user.config.json').write_text('{}', encoding='utf-8')
    os.environ[prefix + 'KIT_STORAGE_ROOT'] = str(storage)
    put(production / 'ORIGINAL_ENV_AND_ALLOWED_OVERRIDES.json', dict(expert=role, actual_env=env,
        original_manifest_SHA=cfg['original_manifest_SHA'], reward_task_command_STD_LR_retained=True,
        kit_storage_root=str(storage), N80_smallGPU_capacity_override=False))


def run_original_window(role, runner, n, log_dir, cache, job, production, cfg, task, go, original_bounded_learn):
    """Called by unchanged original trainer AFTER live whole20k resume + save install."""
    import torch
    from spring_pressure_checkpoint import exact
    from feedback_delay_runtime import delay_state
    source = cache.state
    # PinnedSource208.load already deep-copies the complete selected truth for
    # runner.load AND for every DR helper. An independent whole-root RAM snapshot
    # additionally detects a future Adam CPU-step storage alias or any unknown
    # cache mutation during REAL training, without re-opening/decoding the PT.
    truth_snapshot = copy.deepcopy(source)
    env, vec = runner.env.unwrapped, runner.env
    limit = task['max_additional_updates']
    require(n == limit, 'Original trainer resolved the exact additional iteration cap')
    runner.logger.writer = None  # original finite-worker convention; original logger.log stays active
    for key, obj in (('actor_state_dict', runner.alg.actor), ('critic_state_dict', runner.alg.critic),
                     ('optimizer_state_dict', runner.alg.optimizer)):
        require(exact(obj.state_dict(), source[key]), 'Fresh live whole-source core restore: ' + key)
    require(runner.current_learning_iteration == cfg['source_iteration'], 'Live restored source iteration')
    require(len(runner.alg.actor.state_dict()) == 9 and len(runner.alg.critic.state_dict()) == 8, 'Original A0 actor9/critic8')
    std_keys = [k for k in runner.alg.actor.state_dict() if k.endswith('std_param') and not k.endswith('log_std_param')]
    require(len(std_keys) == 1 and tuple(runner.alg.actor.state_dict()[std_keys[0]].shape) == (6,), 'Original scalar-STD6 parameterization')
    require({int(v['step']) for v in runner.alg.optimizer.state_dict()['state'].values()} == {cfg['source_Adam_step']}
            and len(runner.alg.optimizer.state_dict()['state']) == 17, 'Fresh live 17 Adam exact source step')
    require(all(g['lr'] == cfg['source_LR'] for g in runner.alg.optimizer.param_groups)
            and runner.alg.learning_rate == cfg['source_LR'], 'Exact restored source LR, no reset')
    require(env.num_envs == 20000 and env.physics_dt == .0025 and env.step_dt == .02
            and env.cfg.decimation == 8 and env._sim_step_counter == 0, 'Original whole20k clock before PPO')
    require(env.cfg.terminations.closure.params['threshold'] == .01 and env.cfg.terminations.mimic.params['threshold'] == .01,
            'Current approved closure/mimic gates')
    require(env._physics_action_delay.queue.control_us == 20000, 'Original physical action queue timing')
    require(tuple(delay_state(env).delay.shape) == (20000,), 'Original FeedbackDelay.delay API, not lag_steps')
    require(env.spring_pressure_recipe()['nominal_stiffness_N_m'] == 2000, 'Original k2000 gas contract')
    guard = getattr(env, '_mod4v1_' + role.lower() + '_nominal_guard')
    require(guard.restore_completed and guard.reset_calls == 1, 'ONE original startup env.reset, not a fresh D0 replacement')
    guard.assert_new_nominals_unchanged()
    obs = vec.get_observations()
    guard.check_observations(obs)
    receipts = original_receipts(role, log_dir, cfg['source_SHA'])
    bank = getattr(env, '_mod4v1_' + role.lower() + '_bank_compatibility')
    require(bank['new_contract_SHA'] == CONTRACT_SHA and bank['pose_ranges']['original_height_filter_selected_poses'] == 74,
            'Original geometric flat133/filtered74 bank under new nominal')
    if role == 'E2':
        require(type(env.command_manager.get_term('twist')).__module__ == 'e2_directional_spin_runtime_v1', 'Original E2 command implementation')
    if role == 'E3':
        require(type(env).__module__ == 'e3_recovery_runtime_v1' and env.e3_reset_enabled and not bool(env.recovery.age.any()),
                'Original E3 recovery reset path')
        require(env._e3_fixed_reset_cache.pick == 34 and env._e3_fixed_reset_cache.source_sha ==
                '78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83', 'Original fixed13 recovery bank')
    window = FiniteWindow(limit, go['save_deadline'], lambda: (production / 'STOP_AFTER_SAVE.json').exists()
                          or (Path(log_dir) / 'STOP_AFTER_SAVE').exists())
    initial_tick, initial_fb = int(env._integrated_contact.tick), int(env._feedback_100hz_tick)
    original_save = runner.save  # ALL original save contracts already installed by trainer.main()
    original_update, original_opt_step = runner.alg.update, runner.alg.optimizer.step
    original_log, original_vec_step = runner.logger.log, vec.step
    original_reward = env.reward_manager.compute
    reward_dt_calls = 0
    latest = None

    def full_save(path, *args, **kwargs):
        nonlocal latest
        require(exact(cache.state, truth_snapshot), 'Selected full-root immutable cache truth changed during original PPO')
        target = inside(production, path)
        require((target.suffix == '.pt' or target.name.endswith('.pt.partial'))
                and target != Path(cfg['model_path']).resolve(), 'Derived complete checkpoint/original rescue staging only')
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.fullstate.partial')
        require(not temporary.exists(), 'New atomic derived-save temporary only')
        previous_label = runner.current_learning_iteration
        # Original runner's observed live label is serialized as-is. No saved
        # Adam/LR/iter tensor or dictionary field is filled by arithmetic.
        original_save(str(temporary), *args, **kwargs)
        live = torch.load(temporary, map_location='cpu', weights_only=False)
        assert_live_saved(torch, exact, live, runner, env, role, cfg, window.completed)
        preserved = merge_preserving_omitted(source, live)
        retained = list(omitted_paths(source, live))
        require(all(exact(get_path(preserved, p), v) for p, v in retained), 'All omitted unknown fields retained')
        require('posttrain_finite20_v1' not in preserved, 'This exact branch source must be the selected immutable mother')
        preserved['posttrain_finite20_v1'] = dict(kind=POSTTRAIN_KIND, expert=role, source=dict(cfg),
            run_id=task['run_id'], source_read_purpose_label=task['source_read_purpose_label'],
            root_admission_SHA=task['root_admission_SHA'], **window.receipt(),
            actor35_critic38_actions6=True, policy_hz=50, feedback_hz=100, physics_dt=.0025, TGS=[32, 4],
            asset_USD_SHA=USD_SHA, asset_contract_SHA=CONTRACT_SHA,
            source_root_keys=list(source), source_omitted_dictionary_paths_retained=[list(p) for p, _ in retained],
            unknown_fields_preserved_not_claimed_newly_trained=True, one_original_startup_reset=1,
            original_reward_command_task_and_PPO=True, source_STD_not_manually_changed=True,
            current_complete_queue_history_RNG_saved=True, not_PhysX_exactresume=True,
            expert_skill_graduated=False, D6_scope='original gas damping, not all joint friction')
        torch.save(preserved, temporary)
        roundtrip = torch.load(temporary, map_location='cpu', weights_only=False)
        require(exact(roundtrip, preserved), 'Own newly derived complete checkpoint roundtrip')
        assert_live_saved(torch, exact, roundtrip, runner, env, role, cfg, window.completed)
        require(exact(cache.state, truth_snapshot), 'Own save mutated selected full-root immutable cache truth')
        temporary.replace(target)
        # ONLY this worker's NEW derived artifact is opened here, never the mother.
        with target.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        latest = dict(epoch=time.time(), path=str(target), SHA=digest, bytes=target.stat().st_size,
            original_rescue_atomic_rename_pending=target.name.endswith('.pt.partial'),
            source_SHA=cfg['source_SHA'], saved_iteration=roundtrip['iter'],
            source_Adam_step=cfg['source_Adam_step'],
            saved_17Adam=sorted({int(v['step']) for v in roundtrip['optimizer_state_dict']['state'].values()}),
            actual_saved_LR=float(runner.alg.learning_rate), raw_runner_iteration_before_save=previous_label,
            **window.receipt(), full_live_core_STD_optimizer_DR_history_RNG_queue_verified=True,
            all_source_root_fields_retained=True, expert_skill_graduated=False)
        put(production / 'latest_complete.json', latest)
        return latest

    def saved(name):
        return full_save(production / name)

    def observed_opt_step(*args, **kwargs):
        result = original_opt_step(*args, **kwargs)
        window.optimizer_step_returned()
        return result

    def observed_update(*args, **kwargs):
        window.before_update()
        result = original_update(*args, **kwargs)
        window.update_returned()
        return result

    def observed_reward(*args, **kwargs):
        nonlocal reward_dt_calls
        dt = kwargs.get('dt', args[0] if args else None)
        require(dt == .02, 'Original RewardManager dt once at 50Hz')
        reward_dt_calls += 1
        return original_reward(*args, **kwargs)

    def observed_vec_step(action):
        require(window.completed < limit and window.controls < 24 * limit, 'No rollout beyond finite original PPO cap')
        # Keep the original rescue finish-update/save-boundary stop policy.
        before, fb = int(env._integrated_contact.tick), int(env._feedback_100hz_tick)
        result = original_vec_step(action)
        window.controls += 1
        require(int(env._integrated_contact.tick) - before == 8 and int(env._feedback_100hz_tick) - fb == 2,
                'Actual 50Hz policy/100Hz feedback/400Hz physics changed')
        observations, reward = result[0], result[1]
        guard.check_observations(observations)
        require(tuple(action.shape) == (20000, 6) and all(bool(torch.isfinite(v).all())
                for v in (action, observations['policy'], observations['critic'], reward)), 'Nonfinite original PPO stream')
        return result

    def observed_log(*args, **kwargs):
        result = original_log(*args, **kwargs)
        require(window.completed == window.logged + 1, 'Original logger boundary must follow one completed update')
        window.logged = window.completed
        saved('model_update' + str(window.completed) + '_complete.pt')
        reason = window.reason()
        if reason:
            raise FiniteStop(reason)
        return result

    startup = saved('own_startup0_complete.pt')
    put(production / 'LIVE_WHOLE20K_FULLRESTORE_BEFORE_PPO.json', dict(expert=role, source_SHA=cfg['source_SHA'],
        current_live_actor_critic_STD_17Adam_LR_exact=True, source_iteration=cfg['source_iteration'],
        original_helper_receipts=receipts, original_nominal_guard=guard.receipt(), own_startup_complete=startup,
        no_source_history_slice_or_repeat=True, no_N80_live_restore_claim=True, no_pretraining_native24_replay=True,
        new_learning_not_yet_started=True, skill_graduation=False))
    # Read-only instrumentation delegates EVERY operation to the original methods.
    runner.save = full_save
    runner.alg.update, runner.alg.optimizer.step = observed_update, observed_opt_step
    runner.logger.log, vec.step, env.reward_manager.compute = observed_log, observed_vec_step, observed_reward
    stop_reason = 'ORIGINAL_FINITE_RUN_RETURNED'
    error = None
    try:
        reason = window.reason()
        if reason:
            raise FiniteStop(reason)
        # Same next-new-update convention used by the successful original finite
        # workers. Unlike the old 100000 argument, n is hard-bounded to <=20.
        runner.current_learning_iteration += 1
        # Original rescue_training.learn invokes install() ONCE and uses the
        # original runner.learn(..., init_at_random_ep_len=True). No PPO loop,
        # rollout storage, normalization, reward, action or LR replacement.
        original_bounded_learn(runner, limit, log_dir)
        stop_reason = window.reason() or stop_reason
    except FiniteStop as stop:
        stop_reason = str(stop)
    except BaseException:
        error = traceback.format_exc()
        put(production / 'ORIGINAL_PPO_ERROR_BEFORE_FINAL_SAVE.json', dict(error=error, **window.receipt()))
        raise
    finally:
        # If an original update fails half-way, its changed optimizer must NOT be
        # certified as a complete update. Preserve previous complete artifact and
        # original error instead; no retry/rollback/extra PPO is performed.
        runner.alg.update, runner.alg.optimizer.step = original_update, original_opt_step
        runner.logger.log, vec.step, env.reward_manager.compute = original_log, original_vec_step, original_reward
        if not window.update_in_progress:
            saved('model_final_complete.pt')
        runner.save = original_save
    require(error is None and not window.update_in_progress, 'Original update did not complete cleanly')
    require(reward_dt_calls == window.controls and int(env._integrated_contact.tick) - initial_tick == 8 * window.controls
            and int(env._feedback_100hz_tick) - initial_fb == 2 * window.controls, 'Actual training clock counters')
    guard.assert_new_nominals_unchanged()
    require(window.controls <= 24 * limit and window.completed <= limit, 'Finite rollout/update upper bounds')
    counts = cache.receipt()
    require(counts['source_physical_byte_opens'] == counts['source_decodes'] == 1, 'One original source read/decode per new purpose')
    put(production / 'FINAL.json', dict(epoch=time.time(), passed=window.completed > 0, passed_execution=True,
        status='FINITE_ORIGINAL_PPO_COMPLETE_SAVED' if window.completed else 'ZERO_UPDATES_FINITE_STOP_SAVED',
        expert=role, stop_reason=stop_reason, **window.receipt(), final=latest,
        actual_physics_callbacks=8 * window.controls, actual_feedback_samples=2 * window.controls,
        actual_reward_dt_s=.02, actual_reward_compute_calls=reward_dt_calls,
        actual_source_read_counts=counts, one_original_startup_reset=1,
        selected_source_cache_truth_all_roots_unchanged=exact(cache.state, truth_snapshot),
        no_extra_source_open_for_truth_audit=True,
        original_reward_command_and_task_retained=True, new_PPO_completed=window.completed > 0,
        no_automatic_tail=True, skill_qualification=False, parent_close_wait_accounting_still_required=True))


def main(forced_role=None):
    p = argparse.ArgumentParser(description='Parent-admitted finite original PPO whole20k worker; no launcher/owner')
    p.add_argument('--expert', choices=tuple(EXPERTS), default=forced_role, required=forced_role is None)
    p.add_argument('--mode', choices=('train',), required=True)
    p.add_argument('--num-envs', dest='num_envs', type=int, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    role = args.expert
    require(forced_role is None or role == forced_role, 'Role-specific entry point')
    cfg = EXPERTS[role]
    job = args.out.resolve().parent
    require(args.out.resolve() == job / 'production', 'Only new own production output')
    task, go = read_json(job / 'TASK.json'), read_json(job / 'GO_PRODUCTION.json')
    descriptor_path = inside(job, job / task['posttrain_descriptor_file'])
    descriptor = read_json(descriptor_path)
    require(nonmodel_hash(descriptor_path) == task['posttrain_descriptor_SHA'] == go['posttrain_descriptor_SHA'], 'Reviewed source descriptor join')
    validate_parent_join(role, task, go, descriptor, time.time())
    mod = job / 'runtime/isaac/mod4'
    sys.path[:0] = [str(mod), str(job / 'runtime'), str(job / 'lib')]
    validate_actual_parent_metadata(role, task, go, job, args)
    require(nonmodel_hash(job / task['posttrain_worker_file']) == task['worker_SHA'], 'Reviewed role entry SHA')
    require(nonmodel_hash(Path(__file__)) == task['posttrain_common_SHA'], 'Reviewed complete worker SHA')
    require(task['asset_dir'] == str(job / 'runtime/assets'), 'Own original new asset directory')
    diff = read_json(job / 'MOD4V1_ASSET_DIFF.json')  # must be at JOB OWNER ROOT
    require(diff['new_USD_SHA'] == USD_SHA and diff['new_contract_SHA'] == CONTRACT_SHA
            and set(diff['changed_body_names']) == {'chassis', 'left_shin', 'right_shin'}
            and diff['contract_geometry_unchanged'], 'Required owner-root immutable asset DIFF')
    production = job / 'production'
    production.mkdir(exist_ok=False)
    prepare_original_environment(role, job, production, cfg, go)
    entry = mod / ('train_mod4v1_' + role.lower() + '.py')
    # NO torch/SDK/model call occurs before all actual parent joins above.
    import torch
    from source_cache208_v3 import PinnedSource208, selected_source
    cache = None
    ns = None
    holder = {}
    try:
        cache = PinnedSource208(torch, cfg['model_path'], cfg['source_SHA'], cfg['source_bytes'])
        require(cache.state['iter'] == cfg['source_iteration'], 'Exact pinned whole-source iteration')
        sys.argv = [str(entry), '--headless', '--device', 'cuda:0', '--num_envs', str(task['num_envs']), '--seed', str(task['seed']),
                    '--steps_per_env', str(task['steps_per_env']), '--learning_rate', repr(cfg['source_LR']), '--save_interval', '25',
                    '--init_checkpoint', cfg['model_path'], '--log_root', str(production / 'logs'),
                    '--run_name', role + '_MOD4V1_ORIGINAL_PPO_FINITE20',
                    '--additional_iterations', str(task['max_additional_updates'])]
        ns = runpy.run_path(str(entry), run_name='owned_' + role + '_finite20_source_config')
        import rescue_training
        glob = ns['main'].__globals__
        original_build = glob['build_env']
        def witnessed_build():
            env = original_build()
            holder['env'] = env
            close = env.close
            def witnessed_close(*aa, **kk):
                result = close(*aa, **kk)
                holder['env_closed'] = True
                put(production / 'ENV_CLOSE_RETURNED.json', dict(epoch=time.time(), closed=True))
                return result
            env.close = witnessed_close
            return env
        glob['build_env'] = witnessed_build
        old_learn = rescue_training.learn
        def work(runner, n, log_dir):
            return run_original_window(role, runner, n, log_dir, cache, job, production, cfg, task, go, old_learn)
        rescue_training.learn = work
        try:
            with selected_source(cache):
                ns['main']()
        finally:
            rescue_training.learn = old_learn
    except BaseException:
        put(production / 'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json', dict(epoch=time.time(),
            error=traceback.format_exc(), no_automatic_retry=True, no_extra_window=True))
        raise
    finally:
        if cache is not None:
            put(production / 'SOURCE_FINAL_READ_COUNTS.json', cache.receipt())
        try:
            if 'env' in holder and not holder.get('env_closed'):
                holder['env'].close()
        finally:
            if ns is not None:
                put(production / 'APP_CLOSING.json', dict(epoch=time.time(), calling_original_App_close=True))
                ns['app'].close()
                put(production / 'APP_CLOSED.json', dict(epoch=time.time(), original_App_close_returned=True))


if __name__ == '__main__':
    main()
