"""ZERO_UPDATE tanh-bound-only E3/W35 schema; original plant/barrier/close retained.

Import reads one pinned small Python source, never a checkpoint/SDK/resource.
Import executes no training, ledger, lock acquisition, model decoder, SDK, or actor.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import os
import time

CORE_PIN = (37927, '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')
BATCH_PURPOSE = 'FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1'
PLAN_KIND = 'FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_PLAN_V1'
REQUESTED_ROLES = ('E3', 'W35')
STAGE_REQUIRED_ALIASES = (
    'single_gpu_e3_w35_bound_only_parent_v1.py', 'bound_only_native_runtime_v1.py',
    'bound_only_native_helper_v1.py', 'bound_only_native_route_v1.py', 'producer_bound_probe_guard_v1.py', 'resume_runtime_contracts_v3.py',
    'worker_sources/parent/worker_five_original_n80.py',
    'worker_sources/e1/e1_parallel_worker_safe.py', 'worker_sources/e1/e1_fresh_runtime_bridge.py',
    'a1_frozen_eval_runtime_v2.py', 'frozen_a1_raw35_v1.py', 'pose_cache_runtime_adapter_v3.py',
    'app_close_semantics_v5.py', 'native_supermimic_bridge.py',
    'supermimic_vendor_v2/networks.py', 'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py')


def _load_core():
    name = 'a1_frozen_eval_runtime_v2'
    spec = importlib.util.find_spec(name)
    if spec is None or not isinstance(spec.origin, str):
        raise ValueError('sealed A1 core source is required')
    path = Path(spec.origin).resolve()
    if path.suffix != '.py':
        raise ValueError('plain pinned A1 Python source is required')
    raw = path.read_bytes()
    if (len(raw), hashlib.sha256(raw).hexdigest()) != CORE_PIN:
        raise ValueError('sealed A1 integration core source pin differs')
    core = importlib.import_module(name)
    if Path(core.__file__).resolve() != path:
        raise ValueError('actual A1 core module source differs')
    return core


_base = _load_core()
ROLES = _base.ROLES
CONTROLS = _base.CONTROLS
KIND = 'FROZEN_ZERO_UPDATE_BOUND_ONLY_N80_TASK_V1'
INTEGRATION = 'FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_INTEGRATION_V1'
POLICY_VARIANT = 'A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'
_guard = _base._pinned_module('producer_bound_probe_guard_v1', (9754, 'a840746e22eab3a55781069521b77ba92f67427baae1001b117d732453c76f1e'))
validate_bound_probe_row = _guard.validate_bound_probe_row
_probe = _base._pinned_module('bound_only_native_helper_v1', (19233, '3375168c0d11fe349c8428cb81bb343a90d1520feb90c1e034f829f98ef4a0c9'))
_route = _base._pinned_module('bound_only_native_route_v1', (3378, '0f241475909a7c84e325416f2f6530f7ad912526ff41d7779f5ac0bcb2c87458'))
USD, CONTRACT = _base.USD, _base.CONTRACT
need = _base.need
_validate_approved_reference = _base._validate_approved_reference
# Metadata-only wrapper below avoids pre-admission checkpoint lstat; original schema remains unchanged.
validate_paired_protocol = _base.validate_paired_protocol
# These are the identical reviewed component objects, not reimplementations.
# Reference adapter is defined below; original cache implementation remains unchanged.
install_paired_pose_before_original_reset = _base.install_paired_pose_before_original_reset
# Original error/close bodies are copied below with this explicit reference integration label.
# close_original_eval_resources: original reviewed body, defined below.
paired_protocol_receipt = _base.paired_protocol_receipt
unresolved_evidence = _base.unresolved_evidence
# Reference policy component gate plus unchanged common cache/close semantic body, below.
OriginalA1NoResetDecisionVec = _base.OriginalA1NoResetDecisionVec
build_a1_original_vec = _base.build_a1_original_vec
DEFERRED_ROLES = tuple(role for role in ROLES if role not in REQUESTED_ROLES)
ORIGINAL_SCOPES = {role: dict(num_envs=80, seed=20260928, controls=CONTROLS[role],
    policy_hz=50, feedback_hz=100, physics_dt=.0025, TGS=[32, 4],
    physics_callbacks=CONTROLS[role] * 8, feedback_samples=CONTROLS[role] * 2)
    for role in ROLES}


def _batch_fields(value):
    need(value.get('policy_variant') == POLICY_VARIANT, 'explicit ZERO_UPDATE bounded effective policy required')
    need(type(value) is dict and value.get('batch_purpose') == BATCH_PURPOSE,
         'explicit independent ZERO_UPDATE bound-only purpose required')
    need(value.get('requested_roles') == list(REQUESTED_ROLES)
         and type(value.get('requested_roles')) is list, 'this version requests E3 then W35 only')
    need(value.get('deferred_roles') == list(DEFERRED_ROLES)
         and type(value.get('deferred_roles')) is list, 'all six unrequested roles must be explicit deferred')
    need('overall_eight_pass_rate' in value and value['overall_eight_pass_rate'] is None,
         'subset cannot assert an eight-role pass rate')
    need(value.get('comparison') is None, 'reference-only execution has no paired improvement')


def _stage_file_metadata(plan):
    files = plan.get('worker_files')
    need(type(files) is list and files and all(type(item) is dict for item in files),
         'original parent source-file verification list is required')
    relatives = []
    for item in files:
        relative = item.get('relative')
        need(type(relative) is str and relative and not relative.startswith('/')
             and '\\' not in relative and ':' not in relative
             and all(part not in ('', '.', '..') for part in relative.split('/')),
             'source-file aliases must stay relative to the new group')
        need(type(item.get('bytes')) is int and item['bytes'] > 0 and _base._sha(item.get('SHA')),
             'source file bytes/SHA metadata required before original byte verification')
        relatives.append(relative)
    need(len(set(relatives)) == len(relatives)
         and set(STAGE_REQUIRED_ALIASES) <= set(relatives), 'all seventeen complete bound-only mappings must be present once')


def select_requested_roles(plan):
    """Validate a full eight-role catalog but return only the two requested rows."""
    _batch_fields(plan)
    _stage_file_metadata(plan)
    need(plan.get('kind') == PLAN_KIND, 'new independent microbatch plan schema required')
    rows = plan.get('roles')
    need(type(rows) is list and len(rows) == 8 and all(type(row) is dict for row in rows),
         'retain the complete original eight-role dictionary')
    names = [row.get('role') for row in rows]
    need(len(set(names)) == 8 and set(names) == set(ROLES), 'full original non-H1 role catalog required')
    by_role = {row['role']: row for row in rows}
    for role in ROLES:
        row = by_role[role]
        need(type(row.get('controls')) is int and row['controls'] == CONTROLS[role],
             'original role control count differs: ' + role)
        for key, expected in ORIGINAL_SCOPES[role].items():
            if key in row:
                need(type(row[key]) is type(expected) and row[key] == expected,
                     'original role scope differs: ' + role + ':' + key)
    need(plan.get('asset_SHA') == USD and plan.get('contract_SHA') == CONTRACT,
         'original asset/contract plan identity differs')
    need(type(plan.get('group_id')) is str and plan['group_id']
         and type(plan.get('GPU_UUID')) is str and plan['GPU_UUID'], 'own group/GPU identity required')
    validate_paired_protocol(plan.get('paired_reset_protocol'))
    need(plan['paired_reset_protocol'].get('reference_actual_receipt') is None,
         'same-seed configuration does not establish matched reference/candidate UID or pose')
    selected = [by_role[role] for role in REQUESTED_ROLES]
    for row in selected:
        need(row.get('worker') == 'worker_sources/parent/worker_five_original_n80.py',
             'requested formal worker must retain its original installed alias')
        _producer_descriptor(row.get('a1_producer'), row['role'])
        validate_bound_probe_row(row)
    return selected


def _validate_batch_members(task, role):
    _batch_fields(task)
    need(role in REQUESTED_ROLES and task.get('eval_members') == list(REQUESTED_ROLES)
         and type(task.get('eval_members')) is list, 'only the requested two are admitted worker members')
    need(task.get('role_catalog') == list(ROLES), 'task must retain the complete original role catalog')
    need(task['paired_reset_protocol'].get('reference_actual_receipt') is None,
         'actual paired reference/candidate equivalence remains unverified')


# Exact reviewed core validator body except its single all-eight membership test.
# All resource descriptors, scope/DR/physics, producer, and reference-source checks remain.
def validate_group_task(task, role, group_root, case, contracts=None, *, environment=None, fd_check=None, now=None):
    environment = os.environ if environment is None else environment
    now = time.time if now is None else now
    need(role in ROLES and task.get('role') == role and task.get('kind') == task.get('purpose') == KIND, 'eight original roles excluding H1')
    need(task.get('integration') == INTEGRATION, 'explicit new integration purpose required')
    for key, value in dict(num_envs=80, seed=20260928, optimizer_updates=0, fresh_fullDR_cohort=True,
                           saved20k_DR_physically_applied=False, state_projection_or_slicing=False,
                           whole20k_savedrestore_claim=False, policy_hz=50, feedback_hz=100,
                           physics_dt=.0025, TGS=[32, 4], closure_m=.01, mimic_rad=.01,
                           gas_N=400, stiffness_N_m=2000, damping_Ns_m=3.).items():
        need(task.get(key) == value and type(task.get(key)) is type(value), 'original evaluation scope differs: ' + key)
    need(task.get('controls') == CONTROLS[role] and task.get('physics_callbacks') == CONTROLS[role] * 8
         and task.get('feedback_samples') == CONTROLS[role] * 2, 'original finite evaluation controls differ')
    need(task.get('asset_SHA') == USD and task.get('contract_SHA') == CONTRACT, 'original pinned asset/contract differs')
    admission = task.get('actual_group_admission')
    need(type(admission) is dict and task.get('group_id') == admission.get('group_id')
         and task.get('GPU_UUID') == admission.get('GPU_UUID') == environment.get('CUDA_VISIBLE_DEVICES'), 'original group/GPU admission differs')
    need(all(admission.get(k) is True for k in ('source_SDK_admitted', 'private_GPU_EX_held', 'global_finite_EX_held')),
         'original parent must hold private/finite EX before SDK/model access')
    fds = admission.get('inherited_lock_fds')
    need(type(fds) is list and len(fds) == len(set(fds)) == 2 and all(type(fd) is int and fd >= 0 for fd in fds), 'two original inherited resource descriptors required')
    for fd in fds:
        (fd_check or os.fstat)(fd)
    need(Path(case).resolve().is_relative_to(Path(group_root).resolve()), 'own original eval group scope required')
    need(type(task.get('absolute_worker_deadline_epoch')) in (float, int) and task['absolute_worker_deadline_epoch'] > now(), 'original finite worker deadline elapsed')
    _validate_batch_members(task, role)
    validate_bound_probe_row(task)
    _validate_approved_reference(task)
    producer = _producer_descriptor(task.get('a1_producer'), role)
    checkpoint = producer['FINAL']['checkpoint']
    need(all(task.get(task_key) == checkpoint[checkpoint_key] for task_key, checkpoint_key in
             (('source_path', 'path'), ('source_SHA', 'SHA'), ('source_bytes', 'bytes'))),
         'observer source identity must be the same admitted own A1 checkpoint')
    validate_paired_protocol(task.get('paired_reset_protocol'))
    return True


def make_task(role, plan, deadline, fds):
    selected = select_requested_roles(plan)
    need(role in selected and role.get('role') in REQUESTED_ROLES, 'only an exact selected catalog row may dispatch')
    result = _base.make_task(role, plan, deadline, fds)
    result.update(batch_purpose=BATCH_PURPOSE, requested_roles=list(REQUESTED_ROLES),
                  deferred_roles=list(DEFERRED_ROLES), role_catalog=list(ROLES),
                  eval_members=list(REQUESTED_ROLES), overall_eight_pass_rate=None, comparison=None)
    result.update(kind=KIND, purpose=KIND, integration=INTEGRATION, policy_variant=POLICY_VARIANT)
    validate_bound_probe_row(result)
    _validate_batch_members(result, role['role'])
    return result


def task_args():
    parser = argparse.ArgumentParser(); parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--group-root', type=Path, required=True); args = parser.parse_args()
    task, _ = _base._metadata(args.task)
    validate_group_task(task, task.get('role'), args.group_root, args.task.parent)
    _base.configure_candidate_runtime(task, args.task.parent)
    _base.put_json(args.task.parent / 'BOUND_PROBE_POLICY_IDENTITY_V1.json', dict(policy_variant=POLICY_VARIANT,
        batch_purpose=BATCH_PURPOSE, actor_semantics=task['actor_semantics'], actor_container_identity=task['actor_container_identity'],
        source_path=task['source_path'], source_SHA=task['source_SHA'], source_bytes=task['source_bytes'],
        original_bootstrap_teacher=task['original_bootstrap_teacher'], actual_paired_protocol_UID_match=None))
    return task, args.task.parent, args.group_root


def batch_start(plan, ready, epoch):
    select_requested_roles(plan)
    need(type(ready) is list and len(ready) == 2 and set(ready) == set(REQUESTED_ROLES),
         'both and only requested scenes must be ready before the common start')
    return dict(policy_variant=POLICY_VARIANT, group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], members=list(ready),
                all_members_ready=True, epoch=epoch, batch_purpose=BATCH_PURPOSE,
                requested_roles=list(REQUESTED_ROLES), deferred_roles=list(DEFERRED_ROLES),
                overall_eight_pass_rate=None, comparison=None,
                source='BothRequestedOriginalScenes_ZERO_UPDATE_BoundOnly_N80FullDR_BeforeAnyControlledStep')


def validate_start(task, value):
    _validate_batch_members(task, task['role'])
    _batch_fields(value)
    need(value.get('group_id') == task['group_id'] and value.get('GPU_UUID') == task['GPU_UUID']
         and value.get('all_members_ready') is True, 'own requested ready barrier differs')
    members = value.get('members')
    need(type(members) is list and len(members) == 2 and set(members) == set(REQUESTED_ROLES),
         'no eight/nine/one-member or duplicate-members ready substitution')
    return True


def wait_start(task, out, group, ready):
    """Same zero-control ready/common-start protocol, bound to this explicit subset."""
    _validate_batch_members(task, task['role'])
    _base.put_json(Path(out) / 'WORKER_SCENE_READY.json', dict(group_id=task['group_id'],
        GPU_UUID=task['GPU_UUID'], role=task['role'], pid=os.getpid(), epoch=time.time(),
        zero_controls_before_group_barrier=True, batch_purpose=BATCH_PURPOSE, **ready))
    until = min(task['absolute_worker_deadline_epoch'], time.time() + 900)
    while time.time() < until:
        if (Path(group) / 'GROUP_ABORT.json').exists():
            raise RuntimeError('own requested microbatch startup aborted')
        path = Path(group) / 'GROUP_EVAL_START.json'
        if path.exists():
            value, _ = _base._metadata(path)
            validate_start(task, value)
            _base.put_json(Path(out) / 'WORKER_EVAL_STARTED.json', dict(epoch=time.time(),
                GPU_UUID=task['GPU_UUID'], role=task['role'], group_id=task['group_id'], batch_purpose=BATCH_PURPOSE))
            return value
        time.sleep(.1)
    raise TimeoutError('requested original ready barrier 900s expired without stepping')


def _absolute_skill(role, data):
    """Only original available metadata; never parse raw rows or construct a new predicate."""
    if type(data) is not dict or type(data.get('skill')) is not dict:
        return dict(absolute_original_scope_rate=None, reason='original skill metadata unavailable')
    skill = data['skill']
    if role == 'E3':
        rows = skill.get('original_recovery_recipe_rows')
        if type(rows) is not list or len(rows) != 13 or any(type(row) is not dict for row in rows):
            return dict(absolute_original_scope_rate=None, reason='original thirteen recipe rows missing')
        by_recipe = {row.get('recipe'): row for row in rows}
        if set(by_recipe) != set(range(13)) or any(type(row.get('recipe')) is not int for row in rows):
            return dict(absolute_original_scope_rate=None, reason='original unique recipe identities missing')
        for recipe, row in by_recipe.items():
            keys = ('initial_envs', 'first_episode_original_stable_credit', 'first_episode_physical_terminated')
            if any(type(row.get(k)) is not int or row[k] < 0 for k in keys):
                return dict(absolute_original_scope_rate=None, reason='original recipe counters are not nonnegative integers')
            if (row.get('original_request') is not (recipe != 12)
                or row[keys[1]] > row[keys[0]] or row[keys[2]] > row[keys[0]]):
                return dict(absolute_original_scope_rate=None, reason='original recipe cohort/counters inconsistent')
        rescue = [by_recipe[i] for i in range(12)]
        denominator = sum(row['initial_envs'] for row in rescue)
        normal = by_recipe[12]
        if denominator != 74 or normal['initial_envs'] != 6:
            return dict(absolute_original_scope_rate=None, reason='original fixed N80 rescue74/normal6 cohort differs')
        numerator = sum(row['first_episode_original_stable_credit'] for row in rescue)
        return dict(scope='ORIGINAL_E3_FIRST_EPISODE_OWNER_CREDIT_NOT_GLOBAL_EXPERT_GRADUATION',
            passed=numerator, denominator=denominator, absolute_original_scope_rate=numerator / denominator,
            recipe_rows=copy.deepcopy(rows), normal_group=copy.deepcopy(normal), normal_scored_as_rescue=False,
            missing_or_uncredited_initial_rescue_remains_denominator=True,
            first_episode_timeout_detail=None, global_expert_graduation=None)
    facts = skill.get('original_RM70_interval_route_facts')
    return dict(scope='ORIGINAL_W35_NATURAL_BODY_INTERVALS_MOVING_AND_STANDING_SEPARATE',
        absolute_original_scope_rate=None, moving_rate=None, standing_rate=None,
        original_combined_events=copy.deepcopy(facts.get('events')) if type(facts) is dict else None,
        reason='available FINAL events pool moving+standing; original split metadata is missing',
        combined_true_over_complete_is_not_moving_rate=True, partial_attempt_ledger=None,
        original_full_expert_graduation=None)


def _terminal_success(row):
    semantic = row.get('semantic')
    return (row.get('actual_waited') is True and type(row.get('returncode')) is int
        and row['returncode'] == 0 and row.get('passed_execution') is True
        and type(semantic) is dict and semantic.get('passed_execution') is True
        and semantic.get('original_error') is False
        and type(semantic.get('actual_waited_returncode')) is int
        and semantic['actual_waited_returncode'] == 0)


def batch_result(plan, terminal, group_start, *, epoch):
    select_requested_roles(plan)
    need(type(terminal) is list and len(terminal) == 2
         and all(type(row) is dict for row in terminal)
         and {row.get('role') for row in terminal} == set(REQUESTED_ROLES), 'exact requested terminal rows required')
    complete = all(_terminal_success(row) for row in terminal)
    results = {row['role']: (_absolute_skill(row['role'], row.get('data'))
               if _terminal_success(row)
               else dict(absolute_original_scope_rate=None, reason='actual waited semantic success required'))
               for row in terminal}
    return dict(kind='ACTUAL_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_PROBE_V1', batch_purpose=BATCH_PURPOSE, policy_variant=POLICY_VARIANT,
        group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], requested_roles=list(REQUESTED_ROLES),
        deferred_roles=list(DEFERRED_ROLES), original_eight_role_catalog=copy.deepcopy(plan['roles']),
        original_scopes=copy.deepcopy(ORIGINAL_SCOPES), common_start_epoch=group_start,
        requested_ready_before_start=group_start is not None, all_requested_actual_execution_complete=complete,
        coverage={role: ('requested' if role in REQUESTED_ROLES else 'deferred') for role in ROLES},
        absolute_original_scope_results=results, rows=terminal, overall_eight_pass_rate=None,
        all_eight_actual_execution_complete=None, subset_pooled_skill_rate=None, comparison=None,
        relative_improvement=None, paired_actual_reference=None, UID_alignment=None,
        reference_cache_match=None, reward_effect_identification=None,
        E0_original_binary_predicate=None, SLOPE_INDEPENDENT50_original_binary_predicate=None,
        source20k_DR_history_sliced=False, source20k_histories_physically_applied=False,
        probe_training_updates=0, probe_BPTT_policy_steps=0, probe_optimizer_updates=dict(pi=0, wm=0, aux=0, critic=0),
        old20k_fullrestore_proof_preserved_separately=True, new_PPO_BPTT_GO=0, canonical_writes=0,
        training_counts_are_not_skill_success=True, epoch=epoch)


_metadata = _base._metadata
_pinned_module = _base._pinned_module
put_json = _base.put_json
APP_PIN = _base.APP_PIN
APPROVED_RSL_MODEL_SOURCE = _base.APPROVED_RSL_MODEL_SOURCE
_validate_returned_app_binding = _base._validate_returned_app_binding
import sys, traceback

def record_primary_error(case, *, role, phase, error, cache=None):
    case = Path(case); value = dict(kind=INTEGRATION, role=role, phase=phase, error=error,
                source_cache=None, no_samepurpose_retry=True)
    if cache is not None:
        try:
            value['source_cache'] = cache.receipt()
        except BaseException:
            value['source_cache_error'] = traceback.format_exc()
    path = case / 'WORKER_ERROR.json'
    if path.exists():
        path = case / ('WORKER_ERROR_SECONDARY_' + str(time.time_ns()) + '.json')
    try:
        with path.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, allow_nan=False); stream.flush(); os.fsync(stream.fileno())
    except BaseException:
        sys.stderr.write('A1_EVAL_PRIMARY_ERROR\n' + error + '\n' + traceback.format_exc())
        raise
    return value

def close_original_eval_resources(env, app, case, task, *, env_already_closed=False):
    """One original env close and one original App close; fast-exit intent is metadata.

    Original App may os._exit(0). A successful intent is NOT a wait receipt. The
    unchanged original parent must actually wait before evaluate_waited_eval_case.
    """
    case = Path(case); errors = []
    def remember(phase):
        error = traceback.format_exc(); errors.append(dict(phase=phase, error=error))
        try:
            record_primary_error(case, role=task['role'], phase=phase, error=error)
        except BaseException:
            errors.append(dict(phase=phase + '_error_sidefile', error=traceback.format_exc()))
    def publish(path, value):
        try:
            put_json(path, value)
            return True
        except BaseException:
            remember('close_sidefile:' + Path(path).name)
            return False
    if env is not None and not env_already_closed:
        try:
            env.close()
            publish(case / 'ENV_CLOSE_RETURNED_A1_EVAL_V2.json', dict(closed=True))
        except BaseException:
            remember('original_env_close')
    else:
        publish(case / 'ENV_CLOSE_RETURNED_A1_EVAL_V2.json', dict(closed=env_already_closed))
    publish(case / 'PRE_CLOSE.json', dict(kind=INTEGRATION, role=task['role'], group_id=task['group_id'],
             original_env_close_returned=bool((case / 'ENV_CLOSE_RETURNED_A1_EVAL_V2.json').exists() and not errors),
             App_close_will_be_called=app is not None, parent_actual_wait_required=True))
    if app is None:
        need(errors or (case / 'WORKER_ERROR.json').exists(), 'successful evaluation cannot omit original App')
        return errors
    binding = None
    try:
        helper = _pinned_module('app_close_semantics_v5', APP_PIN)
        binding = helper._pin_original_app_close(app)  # Actual reviewed source/API, no SDK getter.
        if binding['fast_shutdown']:
            helper._validate_binding_receipt(binding)
        put_json(case / 'APP_CLOSE_BINDING_A1_EVAL_V2.json', binding)
        if not errors and not (case / 'WORKER_ERROR.json').exists() and (case / 'FINAL.json').exists():
            final, raw = _metadata(case / 'FINAL.json')
            need(final.get('passed_execution') is True and final.get('integration') == INTEGRATION, 'successful A1 evaluation FINAL required')
            if binding['fast_shutdown']:
                put_json(case / 'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json', dict(kind='PINNED_A1_EVAL_FAST_CLOSE_INTENT_V2',
                         role=task['role'], group_id=task['group_id'], final_SHA=hashlib.sha256(raw).hexdigest(),
                         final_bytes=len(raw), binding=binding, original_env_close_returned=True,
                         publication='FSYNC_ATOMIC_METADATA_BEFORE_ORIGINAL_APP_CLOSE', actual_parent_wait=None))
    except BaseException:
        remember('actual_original_app_binding_or_intent')
    try:
        app.close()  # EXACT original call, no mode changes, no replacement close, once.
        put_json(case / 'APP_CLOSE_RETURNED_A1_EVAL_V2.json', dict(returned=True, binding=binding))
    except BaseException:
        remember('original_App_close_raised')
    return errors

def _producer_descriptor(value, role):
    """Original descriptor schema; metadata never resolves/stats checkpoint paths.

    Actual admitted A1CheckpointAdapter/cache physical containment and byte checks
    stay unchanged. This narrow temporary wrapper is used only for metadata.
    """
    original = Path.resolve
    def lexical_checkpoint(path, *args, **kwargs):
        if path.suffix.lower() in ('.pt', '.pth', '.ckpt', '.safetensors', '.onnx'):
            return Path(os.path.abspath(os.path.normpath(os.fspath(path))))
        return original(path, *args, **kwargs)
    try:
        Path.resolve = lexical_checkpoint
        return _base._producer_descriptor(value, role)
    finally:
        Path.resolve = original


class BoundProbeCaller(_probe.BoundOnlyPolicyCaller):
    def receipt(self):
        return dict(super().receipt(), paired_reset_protocol=paired_protocol_receipt(), unresolved_evidence=unresolved_evidence())


class A1CheckpointAdapter(_route.BoundOnlyCheckpointAdapter):
    """ONE original cache; virtual caller factory, never super().actor then rebuild."""
    caller_type = BoundProbeCaller
    def __init__(self, torch_module, task):
        validate_bound_probe_row(task)
        super().__init__(torch_module, task)
    def receipt(self):
        value = super().receipt()
        value.update(integration=INTEGRATION, batch_purpose=BATCH_PURPOSE,
            actor_semantics='OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE',
            actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
            original_bootstrap_teacher=dict(self.task['original_bootstrap_teacher']),
            producer_teacher_freeze_evidence=validate_bound_probe_row(self.task),
            old_RSL_actor_checkpoint_loader_used=False,
            approved_reference_provenance=dict(self.task['approved_reference_provenance']),
            admitted_producer_run_id=self.task['a1_producer']['run_id'],
            actual_BPTT_policy_steps=self.task['a1_producer']['FINAL']['actual_BPTT_policy_steps'],
            legacy_source_provenance_aliases_are_historical_not_probe_updates=True,
            actual_eval_RSL_source_binding=(dict(self.caller.mean.source_bindings['rsl_rl.models.MLPModel']) if self.caller is not None else None))
        if self.caller is not None:
            value['bound_only_probe'] = value.pop('frozen_mean')
        return value


def evaluate_waited_eval_case(case, returncode, role_entry, group_id):
    """Metadata-only semantic gate called strictly AFTER original p.wait()."""
    case = Path(case); role = role_entry['role']; reasons = []
    final = intent = binding = None
    if returncode != 0:
        reasons.append('actual_worker_RC_nonzero')
    if (case / 'WORKER_ERROR.json').exists() or list(case.glob('WORKER_ERROR_SECONDARY_*.json')):
        reasons.append('durable_primary_or_secondary_worker_error')
    try:
        final, raw = _metadata(case / 'FINAL.json')
        need(final.get('passed_execution') is True and final.get('integration') == INTEGRATION
             and final.get('role') == role and final.get('group_id') == group_id, 'successful own role/group FINAL required')
        need(type(final.get('num_envs')) is int and final['num_envs'] == 80 and final.get('controls') == CONTROLS[role], 'original finite N80 execution incomplete')
        producer = _producer_descriptor(role_entry.get('a1_producer'), role)
        checkpoint = producer['FINAL']['checkpoint']
        source = final['source_cache']
        _validate_approved_reference(source)
        actual_source = source.get('actual_eval_RSL_source_binding')
        need(type(actual_source) is dict and all(actual_source.get(k) == v for k, v in APPROVED_RSL_MODEL_SOURCE.items()),
             'actual evaluator RSL source identity missing or differs from selected CPU reference')
        need(all(source.get(k) == checkpoint[v] for k, v in (('source_path', 'path'), ('source_SHA', 'SHA'), ('source_bytes', 'bytes')))
             and source.get('admitted_producer_run_id') == producer['run_id']
             and source.get('actual_BPTT_policy_steps') == producer['FINAL']['actual_BPTT_policy_steps'], 'actual own A1 source identity differs')
        need(all(type(source.get(k)) is int and source[k] == 1 for k in ('physical_byte_opens', 'SHA_calculations', 'CPU_decodes')),
             'one own full checkpoint bytes/hash/decode receipt required')
        need(type(source.get('mother_checkpoint_opens')) is int and source['mother_checkpoint_opens'] == 0
             and source.get('whole_root_CPU_unchanged') is True
             and source.get('replay_or_saved_history_sliced_or_restored') is False
             and source.get('live_optimizer_WM_critic_replay_created') is False,
             'whole CPU cache/mother-zero receipt required')
        need(final.get('policy_variant') == POLICY_VARIANT and final.get('evaluation_purpose') == BATCH_PURPOSE
             and final.get('actor_semantics') == 'OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE', 
             'explicit bound-probe FINAL variant/purpose required')
        evidence = validate_bound_probe_row(role_entry)
        probe = source.get('bound_only_probe')
        _probe.validate_bound_probe_receipt(probe, expected_role=role, expected_source_sha=checkpoint['SHA'], expected_actor_calls=CONTROLS[role])
        need(probe.get('synthetic_only') is False and source.get('native_enabled') is True
             and source.get('probe_training_updates') == source.get('probe_BPTT_policy_steps') == 0
             and source.get('probe_optimizer_updates') == dict(pi=0, wm=0, aux=0, critic=0)
             and source.get('producer_teacher_freeze_evidence') == evidence and 'frozen_mean' not in source
             and 'embedded_teacher_reference' not in source and source.get('policy_variant') == POLICY_VARIANT
             and source.get('policy_family') == 'zero_update_tanh_postprocess_of_original_full_A1_not_training'
             and source.get('actor_semantics') == 'OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE'
             and source.get('original_bootstrap_teacher') == role_entry['original_bootstrap_teacher'],
             'ZERO_UPDATE effective actor/source/producer identity differs')
        paired = probe.get('paired_reset_protocol')
        need(type(paired) is dict and paired.get('candidate_pose_installed') is True
             and paired.get('protocol') == validate_paired_protocol(role_entry.get('paired_reset_protocol')),
             'shared original pose installer/protocol receipt missing; no matched UID claim')
        need((case / 'PRE_CLOSE.json').exists() and (case / 'ENV_CLOSE_RETURNED_A1_EVAL_V2.json').exists(), 'original env/preclose proof missing')
        closed, _ = _metadata(case / 'ENV_CLOSE_RETURNED_A1_EVAL_V2.json')
        need(closed.get('closed') is True, 'original env close did not return successfully')
        if (case / 'APP_CLOSE_RETURNED_A1_EVAL_V2.json').exists():
            returned, _ = _metadata(case / 'APP_CLOSE_RETURNED_A1_EVAL_V2.json')
            need(returned.get('returned') is True and type(returned.get('binding')) is dict, 'original App returned without actual binding')
            binding = returned['binding']
        else:
            intent, _ = _metadata(case / 'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json')
            need(intent.get('kind') == 'PINNED_A1_EVAL_FAST_CLOSE_INTENT_V2' and intent.get('role') == role
                 and intent.get('group_id') == group_id and intent.get('final_SHA') == hashlib.sha256(raw).hexdigest()
                 and intent.get('final_bytes') == len(raw) and intent.get('original_env_close_returned') is True
                 and intent.get('publication') == 'FSYNC_ATOMIC_METADATA_BEFORE_ORIGINAL_APP_CLOSE', 'original fast-close intent differs')
            binding = intent['binding']
        helper = _pinned_module('app_close_semantics_v5', APP_PIN)
        if binding.get('fast_shutdown') is True:
            helper._validate_binding_receipt(binding)
        else:
            # The exact original source may return when mode False. No inference
            # from a fast-close-only intent is accepted for that configuration.
            need(intent is None, 'non-fast source mode requires an actual returned App close record')
            _validate_returned_app_binding(binding, helper)
    except BaseException as exc:
        reasons.append('semantic_metadata:' + str(exc))
    return dict(kind='ACTUAL_WAITED_ZERO_UPDATE_BOUND_ONLY_N80_SEMANTIC_V1', role=role, group_id=group_id,
                actual_waited_returncode=returncode, passed_execution=not reasons, original_error=bool(reasons), reasons=reasons,
                original_fast_close_expected_nonreturn_accepted=bool(not reasons and intent is not None),
                actual_resource_admission_or_parent_wait_proof='CALLER_ORIGINAL_P_WAIT_REQUIRED_NOT_CREATED_HERE',
                UID_alignment=None, reference_cache_match=None, paired_reward_effect=None)

def grade_closed_bound_probe_group(group_root):
    """Read-only original close/exit receipts; never creates external parent-wait proof."""
    root = Path(group_root).resolve(); reasons = []; checked = []
    def read(name):
        path = root / name
        with path.open('rb') as stream:
            raw = stream.read(8 * 1024 * 1024 + 1)
        need(len(raw) <= 8 * 1024 * 1024, 'bounded group metadata required: ' + name)
        return json.loads(raw)
    try:
        for name in ('PARENT_ORIGINAL_ERROR.json', 'GROUP_ABORT.json', 'GROUP_STARTUP_ABORT.json'):
            need(not (root / name).exists(), 'original group error remains: ' + name)
        plan = read('GROUP_PLAN.json'); rows = select_requested_roles(plan)
        need(plan['group_id'] == root.name, 'own closed reference group identity differs')
        final = read('FINAL.json'); _batch_fields(final)
        need(final.get('kind') == 'ACTUAL_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_PROBE_V1'
             and final.get('group_id') == plan['group_id'] and final.get('GPU_UUID') == plan['GPU_UUID']
             and final.get('all_requested_actual_execution_complete') is True
             and final.get('requested_ready_before_start') is True
             and final.get('original_eight_role_catalog') == plan['roles'], 'original bound-probe batch FINAL incomplete or mismatched')
        admission = read('ACTUAL_GROUP_ADMISSION.json')
        need(admission.get('group_id') == plan['group_id'] and admission.get('original_private_GPU_EX_held') is True
             and admission.get('original_global_finite_EX_held') is True and admission.get('canonical_writes') == 0
             and admission.get('canonical_owner_at_read') is None, 'original group admission receipt incomplete')
        exit_receipt = read('PARENT_EXIT_SCOPE.json')
        need(all(exit_receipt.get(key) is True for key in ('all_own_children_waited',
             'original_single_GPU_private_EX_released', 'original_global_finite_EX_released'))
             and exit_receipt.get('errors') == [] and exit_receipt.get('canonical_writes') == 0,
             'original actual waits/resource release/errors do not qualify')
        waits = exit_receipt.get('child_waits'); terminal = read('TERMINAL_ROWS.json')
        need(type(waits) is list and len(waits) == 2 and type(terminal) is list and len(terminal) == 2
             and {v.get('role') for v in waits} == set(REQUESTED_ROLES)
             and {v.get('role') for v in terminal} == set(REQUESTED_ROLES)
             and final.get('rows') == terminal, 'exact original two waited child rows required')
        for entry in rows:
            role = entry['role']; waited = next(v for v in waits if v['role'] == role)
            row = next(v for v in terminal if v['role'] == role)
            need(waited.get('actual_waited') is True and type(waited.get('returncode')) is int
                 and waited['returncode'] == 0 and waited.get('pid') == row.get('pid')
                 and _terminal_success(row), 'original terminal/cleanup child wait differs: ' + role)
            case = root / 'cases' / role
            semantic = evaluate_waited_eval_case(case, row['returncode'],
                dict(entry, paired_reset_protocol=plan['paired_reset_protocol']), plan['group_id'])
            need(semantic.get('passed_execution') is True and row.get('semantic') == semantic,
                 'bound-probe original semantic gate differs after close: ' + role)
            case_final, _ = _base._metadata(case / 'FINAL.json')
            need(row.get('data') == case_final, 'original terminal/actual case FINAL differs: ' + role)
            checked.append(role)
    except Exception as error:
        reasons.append(type(error).__name__ + ':' + str(error))
    return dict(kind='CLOSED_ZERO_UPDATE_BOUND_ONLY_NATIVE_SOURCE_GRADE_V1', policy_variant=POLICY_VARIANT,
        batch_purpose=BATCH_PURPOSE, group_root=str(root), passed_closed_bound_probe_source_grade=not reasons,
        original_error=bool(reasons), reasons=reasons, checked_roles=checked,
        external_executing_parent_actual_wait_required=True, external_parent_wait_proof_created_here=False,
        qualified_bound_probe_execution=None, UID_alignment=None, reference_cache_match=None,
        relative_improvement=None, paired_reward_effect=None, overall_eight_pass_rate=None,
        C_or_lock_or_SDK_or_checkpoint_operations=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Source metadata validation only; no admission or dispatch.')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--validate-plan', type=Path)
    modes.add_argument('--grade-closed-group', type=Path)
    args = parser.parse_args()
    if args.grade_closed_group is not None:
        result = grade_closed_bound_probe_group(args.grade_closed_group)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result['passed_closed_bound_probe_source_grade'] else 1)
    plan, _ = _base._metadata(args.validate_plan)
    rows = select_requested_roles(plan)
    print(json.dumps(dict(kind='SOURCE_MICROBATCH_PLAN_VALIDATION_NOT_NATIVE',
        requested_roles=[row['role'] for row in rows], deferred_roles=list(DEFERRED_ROLES),
        policy_variant=POLICY_VARIANT, zero_update_bound_probe=True, native_capable=True, actual_native_enabled=False, actual_staged=False,
        overall_eight_pass_rate=None, comparison=None, resources_acquired=0, model_opens=0), sort_keys=True))
