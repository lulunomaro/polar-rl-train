"""Typed native continuation admission. Importing this module does no I/O.

Actual checkpoint reads belong to the installed CPU entry point only. This
guard never interprets the frozen PPO bootstrap as the learned native source.
"""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json

KIND = 'UNISUPERMIMIC_FUDAN_NATIVE85_CONTINUATION_SOURCE_SDK_CPU_V86'
NATIVE_SHA = '94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af'
BOOTSTRAP_SHA = '8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6'
BOOTSTRAP_ADAM = 829700
GPU = 'GPU-16828f91-2b45-b646-8dc0-9481138e2842'
BACKEND = 'target72'
CONTROL_PATHS = frozenset(('three_slot_common_v1.py', 'three_real_gpu_resource_v1.py',
    'forwarded_original_owner_control_v1.py', 'closed_production_continuation_CPU_v2.py'))
NATIVE_REPLACEMENTS = frozenset(('source/h1_supermimic_bridge_v1.py',
    'h1_unisupermimic_step270_worker_v1.py'))
METADATA_REPLACEMENTS = frozenset(('job0/TASK.json',))
CONTROL_ADDITIONS = frozenset(('mixed86_protocol_v1.py',))
EXACT_NATIVE_OVERLAY_PATHS = frozenset((
    'native86_source_guard_v1.py', 'target_native86_source_sdk_cpu_review_v1.py',
    'native86_closed_source_CPU_v1.py', 'h1_unisupermimic_step270_worker_v1.py',
    'closed_production_continuation_CPU_v2.py',
    'test_native_h1_fudan_reference_CPU_v86.py', 'native_continuation_v1.py',
    'source/h1_supermimic_bridge_v1.py', 'source/native_continuation_v1.py',
    'source/native_policy_phase_coverage_v1.py', 'NATIVE_CONTINUATION_BINDING_ACTUAL.json',
    'NATIVE85_ORIGINAL_COMPLETE_MANIFEST.json',
    'native_source_metadata/NATIVE85M2_FINAL_ACTUAL.json',
    'native_source_metadata/NATIVE85M2_COMPLETE_CPU_REVIEW_ACTUAL.json',
    'native_source_metadata/NATIVE85M2_ORIGINAL_COST_ALLOUT_COLLECTOR_ACTUAL.json',
    'native_source_metadata/NATIVE85M2_RUNTIME_ORDER_ACTUAL.json',
    'native_source_metadata/NATIVE85M2_RUNTIME_OBJECTIVE_CONTRACT_ACTUAL.json'))


class AdmissionError(RuntimeError):
    pass


def require(value, message):
    if not value:
        raise AdmissionError(message)


def H(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def contained(base, relative):
    require(isinstance(relative, str) and relative, 'Empty relative path')
    p = PurePosixPath(relative)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in relative
            and ':' not in relative and p.as_posix() == relative, 'Uncontained relative path')
    base = Path(base).resolve()
    target = base.joinpath(*p.parts)
    require(target.resolve().is_relative_to(base), 'Resolved path escaped payload')
    cursor = target
    while cursor != base:
        require(not cursor.is_symlink(), 'Symlink in payload path')
        cursor = cursor.parent
    return target


def rows_by_path(rows):
    require(isinstance(rows, list), 'File rows absent')
    indexed = {}
    for row in rows:
        relative = row['relative']
        require(relative not in indexed, 'Duplicate file pin: ' + relative)
        require(type(row['bytes']) is int and row['bytes'] >= 0, 'Invalid byte count')
        require(isinstance(row['SHA'], str) and len(row['SHA']) == 64
                and all(c in '0123456789abcdef' for c in row['SHA']), 'Invalid SHA')
        indexed[relative] = row
    return indexed


def validate_identity(spec):
    require(spec.get('native_continuation') is True and spec['key'] == 'e2', 'Typed native role absent')
    require(spec['source_SHA'] == NATIVE_SHA, 'Native source SHA differs')
    require(spec['source_Adamstep'] == BOOTSTRAP_ADAM, 'Bootstrap Adam differs')
    require(spec['bootstrap_source_SHA'] == BOOTSTRAP_SHA,
            'Explicit frozen bootstrap identity absent')
    require(spec['GPU_UUID'] == GPU and spec['execution_backend'] == BACKEND, 'Native backend/GPU differs')
    require(spec.get('native_continuation_restore_required') is True, 'Native restore not required')
    return True


def validate_inventory(manifest, original, contract):
    """Only exact reviewed per-file deltas; no protected-directory exception."""
    current = rows_by_path(manifest['files'])
    baseline = rows_by_path(original['files'])
    overlay = rows_by_path(contract['overlay_files'])
    require(set(overlay) == EXACT_NATIVE_OVERLAY_PATHS, 'Native overlay exact path set differs')
    replacements = {r['relative']: r for r in contract.get('controller_replacements', [])}
    require(len(replacements) == len(contract.get('controller_replacements', [])), 'Duplicate controller replacement')
    require(set(replacements) <= CONTROL_PATHS, 'Unapproved controller replacement path')
    metadata_replacements = {r['relative']: r for r in contract.get('metadata_replacements', [])}
    require(len(metadata_replacements) == len(contract.get('metadata_replacements', [])), 'Duplicate metadata replacement')
    require(set(metadata_replacements) <= METADATA_REPLACEMENTS, 'Unapproved metadata replacement path')
    additions = rows_by_path(contract.get('controller_additions', []))
    require(set(additions) <= CONTROL_ADDITIONS, 'Unapproved added controller path')
    require(set(contract.get('removed_files', [])) == set(), 'Protected original removal forbidden')
    for relative, previous in baseline.items():
        require(relative in current, 'Original file omitted: ' + relative)
        actual = current[relative]
        if relative in NATIVE_REPLACEMENTS:
            require(relative in overlay and actual == overlay[relative], 'Native replacement differs')
        elif relative in replacements or relative in metadata_replacements:
            review = (replacements if relative in replacements else metadata_replacements)[relative]
            require(review['original_SHA'] == previous['SHA'], 'Wrong controller original SHA')
            require(actual['SHA'] == review['SHA'] and actual['bytes'] == review['bytes'], 'Controller bytes differ')
        else:
            require(actual == previous, 'Protected original file changed: ' + relative)
    for relative, row in overlay.items():
        require(current.get(relative) == row, 'Required exact overlay pin absent: ' + relative)
    for relative, row in additions.items():
        require(relative not in baseline and current.get(relative) == row, 'Added exact controller pin absent')
    extra = set(current) - set(baseline) - set(overlay) - set(additions)
    # Exactly one new native checkpoint path; the old bootstrap row stays frozen.
    source_relative = 'job0/source/' + manifest['source_filename']
    require(extra == {source_relative, 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'},
            'Unapproved added inventory: ' + repr(sorted(extra)))
    require(current[source_relative]['SHA'] == NATIVE_SHA and current[source_relative]['bytes'] == 140492265,
            'Native checkpoint pin differs')
    require(manifest['bootstrap_filename'] == original['source_filename'], 'Bootstrap source renamed')
    require(current['job0/source/' + manifest['bootstrap_filename']]['SHA'] == BOOTSTRAP_SHA,
            'Frozen bootstrap pin absent')
    require(manifest['source_SHA'] == NATIVE_SHA and manifest['source_Adamstep'] == BOOTSTRAP_ADAM,
            'Manifest typed source differs')
    require(manifest['bootstrap_SHA'] == BOOTSTRAP_SHA and manifest['bootstrap_Adam'] == BOOTSTRAP_ADAM,
            'Manifest bootstrap identity differs')
    return current


def check_payload(B, spec=None, verify_model_bytes=True):
    B = Path(B).resolve()
    manifest_path = B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json'
    manifest = read(manifest_path)
    contract = read(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json')
    require(H(B / 'NATIVE85_ORIGINAL_COMPLETE_MANIFEST.json') == contract['original_manifest_SHA'],
            'Original baseline manifest pin differs')
    original = read(B / 'NATIVE85_ORIGINAL_COMPLETE_MANIFEST.json')
    rows = validate_inventory(manifest, original, contract)
    for relative, row in rows.items():
        path = contained(B, relative)
        require(path.is_file() and path.stat().st_size == row['bytes'], 'Missing/size changed: ' + relative)
        if verify_model_bytes or path.suffix not in ('.pt', '.npz', '.usd', '.zip'):
            require(H(path) == row['SHA'], 'File SHA differs: ' + relative)
        if path.suffix == '.py':
            ast.parse(path.read_text('utf8'), filename=relative)
    actual_python = {p.relative_to(B).as_posix() for p in B.rglob('*.py')}
    require(actual_python == {p for p in rows if p.endswith('.py')}, 'Unapproved Python file present')
    require(H(B / 'native_continuation_v1.py') == H(B / 'source/native_continuation_v1.py'),
            'Producer/import continuation copies differ')
    require(H(B / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json') == contract['binding_SHA'], 'Binding differs')
    if spec is not None:
        validate_identity(spec)
        require(spec['manifest_SHA'] == H(manifest_path), 'Spec manifest differs')
        require(spec['candidate_pins'] == contract['candidate_pins'], 'Spec candidate pins differ')
        require(spec['native_source_contract_SHA'] == H(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'),
                'Spec contract differs')
    return dict(passed=True, manifest_SHA=H(manifest_path), candidate_pins=contract['candidate_pins'],
                exact_all_original_inventory_retained=True, unapproved_python_rejected=True,
                duplicate_continuation_byte_exact=True)


def validate_whole_native(checkpoint, bootstrap, binding, final, validate_new_phase, verify_native):
    """CPU objects supplied by caller. No file read, inference, reset or optimizer step."""
    import torch
    from native_continuation_v1 import exact, finite
    from native_finalization_v1 import REQUIRED_ORIGINAL_GROUPS, NATIVE_CONTRACT
    require(all(k in checkpoint for k in REQUIRED_ORIGINAL_GROUPS), 'Original D0-D7/save group missing')
    require(checkpoint['UniSuperMimic_test_contract'] == NATIVE_CONTRACT, 'Native contract differs')
    publication = checkpoint['UniSuperMimic_publication']
    verify_native(checkpoint, publication)
    native = checkpoint['UniSuperMimic_H1_test']
    require(native['iteration'] == publication['native_iteration'] == final['final']['updates'] == 68, 'Native iteration differs')
    require(publication['world_updates'] == 680 and publication['policy_updates'] == 58, 'Native baseline counters differ')
    require(publication['producer'] == binding['producer'], 'Native producer differs')
    require(all(publication[k] == final['final'][k] for k in ('run_token', 'save_token', 'world_updates', 'policy_updates')),
            'Native publication/FINAL differs')
    for k in ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict'):
        require(exact(checkpoint[k], bootstrap[k]), 'Frozen bootstrap core differs: ' + k)
    require(len(checkpoint['actor_state_dict']) == 9 and len(checkpoint['critic_state_dict']) == 8, 'PPO bootstrap layout')
    require(tuple(checkpoint['actor_state_dict']['distribution.std_param'].shape) == (6,), 'Frozen six STD layout')
    adam = checkpoint['optimizer_state_dict']
    require(len(adam['state']) == 17 and {int(v['step']) for v in adam['state'].values()} == {BOOTSTRAP_ADAM},
            'Frozen bootstrap 17 Adam differs')
    for name in ('sensor_DR_state', 'feedback_delay_state', 'physical_action_delay_state', 'spring_pressure_state', 'gas_damping_state'):
        require(checkpoint[name]['n'] == 20000, 'D0-D7 env count differs: ' + name)
    for name in ('COM', 'PD'):
        require(checkpoint['chassis_PD_state'][name]['num_envs'] == 20000, 'Chassis env count differs')
    task = checkpoint['H1_step270_task_state']
    require(task['version'] == 270, 'Step270 state version differs')
    validate_new_phase(task['phase'], 20000)
    require(checkpoint['H1_step270_runtime_contract']['original_D0_D7_STD_optimizer_save_chain_retained'] is True,
            'Original save contract absent')
    for name in ('wm', 'pi', 'critic'):
        require(isinstance(native[name], dict) and native[name], 'Missing native module: ' + name)
        require(all(torch.is_tensor(v) for v in native[name].values()), 'Native module nontensor state')
    for name in ('opt_wm', 'opt_pi', 'opt_v'):
        value = native[name]
        require(set(value) == {'state', 'param_groups'} and value['state'] and value['param_groups'], 'Missing native optimizer')
        listed = [p for group in value['param_groups'] for p in group['params']]
        # Adam may legitimately omit parameters that never received a gradient.
        # Preserve upstream load semantics; never invent a PPO update formula.
        require(len(listed) == len(set(listed)) and set(value['state']) <= set(listed), 'Native optimizer state/param binding')
        for state in value['state'].values():
            require({'step', 'exp_avg', 'exp_avg_sq'} <= set(state), 'Native Adam tensor missing')
            require(int(state['step']) > 0 and state['exp_avg'].shape == state['exp_avg_sq'].shape, 'Native Adam schema')
    require('UniSuperMimic_continuation_state_v1' not in checkpoint, 'Unexpected legacy replay extension')
    finite(checkpoint)
    return dict(passed=True, native_fullstate_CPU_verified=True, bootstrap_core_literal_exact=True,
                bootstrap_frozen_Adam829700=True, native_iteration=68, world_updates=680, policy_updates=58,
                native_three_optimizers=True, native_PPO20Adam_rule_applied=False,
                original_D0_D7_and_step270_phase_validated=True)


def validate_task_go(task, go, manifest_sha):
    validate_identity(task)
    # TASK is itself pinned inside the manifest. Its SHA cannot contain the
    # manifest SHA; the signed controller GO binds that outer object instead.
    require(go['manifest_SHA'] == manifest_sha, 'Signed GO manifest differs')
    require(go['source_qualification_kind'] == KIND and go['source_SHA'] == task['source_SHA'], 'GO native role differs')
    require(go['bootstrap_SHA'] == task['bootstrap_source_SHA'] and go['bootstrap_Adam'] == BOOTSTRAP_ADAM,
            'GO bootstrap differs')
    require(go['native_continuation_restore_required'] is True, 'GO native restore absent')
    require(go['source_native_iteration'] == 68 and go['window_start_world_updates'] == 680
            and go['window_start_policy_updates'] == 58, 'GO cumulative native baseline differs')
    require(go['max_parent_seconds'] == 3900 and go['exit_headroom_seconds'] == 300
            and go['save_deadline'] < go['nominal_end_epoch'], 'Original bounded grant differs')
    return True


def ready_value(spec, sdk, unit, contract):
    from mixed84_protocol_v1 import validate_objective_contract
    validate_identity(spec)
    require(sdk['passed_CPU_only'] and sdk['actual_H1_source_SDK_CPU_passed'], 'Fresh SDK CPU absent')
    require(sdk['source_SHA'] == NATIVE_SHA and sdk['bootstrap_SHA'] == BOOTSTRAP_SHA, 'SDK typed source differs')
    require(sdk['bootstrap_Adam'] == BOOTSTRAP_ADAM and sdk['native85_fullstate_source_CPU_passed'], 'Whole native CPU absent')
    require(sdk['source_original85_cost_allout_passed'] is True and sdk['native_continuation_restore_required'] is True,
            'Native85 original settlement/restore requirement absent')
    require(len(sdk['actual_RSL_sources']) == 2 and sdk['sampling_acceleration_CPU']['passed'], 'Original RSL/sampling CPU absent')
    require(sdk['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested'], 'Original installed V8 reward CPU absent')
    require(sdk['boundary_repair_integration_CPU']['passed'], 'Original boundary CPU absent')
    require(sdk['manifest_SHA'] == unit['manifest_SHA'] == spec['manifest_SHA'], 'Ready manifest differs')
    require(unit['passed'] and unit['actual_installed_CPU_passed'] and not unit['CUDA_initialized'], 'Fresh native reference CPU absent')
    require(unit['source_SHA'] == NATIVE_SHA, 'Reference CPU typed source differs')
    for name in ('reference_artifact_SHA', 'adapter_CPU_report_SHA', 'objective_contract_SHA'):
        require(unit[name] == spec[name], 'Reference/objective CPU pin differs: ' + name)
    require(unit['candidate_pins'] == contract['candidate_pins'] == spec['candidate_pins'], 'Ready candidate pins differ')
    require(unit['offline_named_mapping_verified'] and unit['actual_runtime_order_readback'] is False, 'Offline/current order scope differs')
    validate_objective_contract(unit['offline_objective_contract'])
    require(unit['offline_objective_contract']['reference_metadata']['sdk_joint_order_verified'] is False
            and unit['offline_objective_contract']['provider_execution_scope'] == 'offline_CPU_named_mapping_SDK_readback_false',
            'Offline objective scope differs')
    require(unit['original_physics_and_success_unchanged'] and unit['finalization_lifecycle_CPU_passed']
            and unit['partial_mask_objective_actual_CPU_admitted']
            and unit['ascent_phase_mask_and_own_step_support_loss_CPU_passed'], 'Original reference lifecycle/phase guards absent')
    require(sdk['rsl_load_roundtrip_CPU'] and sdk['whole_native']['passed'], 'Actual RSL/full native checks absent')
    return dict(kind=KIND, passed=True, source_SHA=NATIVE_SHA, bootstrap_SHA=BOOTSTRAP_SHA,
        bootstrap_Adam=BOOTSTRAP_ADAM, source_Adam=BOOTSTRAP_ADAM,
        GPU_UUID=spec['GPU_UUID'], execution_backend=spec['execution_backend'],
        actual_installed_CPU_passed=True, actual_H1_source_SDK_CPU_passed=True,
        native85_fullstate_source_CPU_passed=True, source_original85_cost_allout_passed=True,
        native_continuation_restore_required=True, native_joint_states=30, actions=6,
        source_native_iteration=68, window_start_WM=680, window_start_Pi=58,
        source_world_updates=680, source_policy_updates=58,
        reference_artifact_SHA=spec['reference_artifact_SHA'], adapter_CPU_report_SHA=spec['adapter_CPU_report_SHA'],
        objective_contract_SHA=spec['objective_contract_SHA'], candidate_pins=contract['candidate_pins'],
        native_source_contract_SHA=spec['native_source_contract_SHA'],
        metadata_helper_byteexact=True, original_H1_270_physics_source_exact=True,
        metadata_helper_bytes=2536, metadata_helper_SHA='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e',
        reference_and_adapter_actual_CPU_validated=True, offline_named_mapping_verified=True,
        actual_runtime_order_readback=False, actual_fresh30_joint_order_required_before_control=True,
        not_production_E2_source_or_skill_qualification=True)
