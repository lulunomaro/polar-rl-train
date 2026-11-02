"""Candidate-only E3/W35 subset schema and barrier; original A1 mechanisms reused.

Import reads one pinned small Python source, never a checkpoint/SDK/resource.
No reference evaluator, training, ledger, lock acquisition, or model decoder here.
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
BATCH_PURPOSE = 'A1_FROZEN_CANDIDATE_ONLY_E3_W35_MICROBATCH_V1'
PLAN_KIND = 'A1_FROZEN_EVAL_MICROBATCH_GROUP_PLAN_V1'
REQUESTED_ROLES = ('E3', 'W35')
STAGE_REQUIRED_ALIASES = (
    'single_gpu_e3_w35_a1_frozen_parent_v1.py', 'frozen_eval_microbatch_runtime_v1.py',
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
KIND, INTEGRATION = _base.KIND, _base.INTEGRATION
USD, CONTRACT = _base.USD, _base.CONTRACT
need = _base.need
_validate_approved_reference = _base._validate_approved_reference
_producer_descriptor = _base._producer_descriptor
validate_paired_protocol = _base.validate_paired_protocol
# These are the identical reviewed component objects, not reimplementations.
A1CheckpointAdapter = _base.A1CheckpointAdapter
install_paired_pose_before_original_reset = _base.install_paired_pose_before_original_reset
record_primary_error = _base.record_primary_error
close_original_eval_resources = _base.close_original_eval_resources
paired_protocol_receipt = _base.paired_protocol_receipt
unresolved_evidence = _base.unresolved_evidence
evaluate_waited_eval_case = _base.evaluate_waited_eval_case
OriginalA1NoResetDecisionVec = _base.OriginalA1NoResetDecisionVec
build_a1_original_vec = _base.build_a1_original_vec
DEFERRED_ROLES = tuple(role for role in ROLES if role not in REQUESTED_ROLES)
ORIGINAL_SCOPES = {role: dict(num_envs=80, seed=20260928, controls=CONTROLS[role],
    policy_hz=50, feedback_hz=100, physics_dt=.0025, TGS=[32, 4],
    physics_callbacks=CONTROLS[role] * 8, feedback_samples=CONTROLS[role] * 2)
    for role in ROLES}


def _batch_fields(value):
    need(type(value) is dict and value.get('batch_purpose') == BATCH_PURPOSE,
         'explicit independent candidate-only microbatch purpose required')
    need(value.get('requested_roles') == list(REQUESTED_ROLES)
         and type(value.get('requested_roles')) is list, 'this version requests E3 then W35 only')
    need(value.get('deferred_roles') == list(DEFERRED_ROLES)
         and type(value.get('deferred_roles')) is list, 'all six unrequested roles must be explicit deferred')
    need('overall_eight_pass_rate' in value and value['overall_eight_pass_rate'] is None,
         'subset cannot assert an eight-role pass rate')
    need(value.get('comparison') is None, 'candidate-only schema has no paired improvement')


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
         and set(STAGE_REQUIRED_ALIASES) <= set(relatives), 'all thirteen reviewed/current mappings must be present once')


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
         'this candidate-only version does not verify or execute a mother reference')
    selected = [by_role[role] for role in REQUESTED_ROLES]
    for row in selected:
        need(row.get('worker') == 'worker_sources/parent/worker_five_original_n80.py',
             'requested formal worker must retain its original installed alias')
        _producer_descriptor(row.get('a1_producer'), row['role'])
    return selected


def _validate_batch_members(task, role):
    _batch_fields(task)
    need(role in REQUESTED_ROLES and task.get('eval_members') == list(REQUESTED_ROLES)
         and type(task.get('eval_members')) is list, 'only the requested two are admitted worker members')
    need(task.get('role_catalog') == list(ROLES), 'task must retain the complete original role catalog')
    need(task['paired_reset_protocol'].get('reference_actual_receipt') is None,
         'actual reference is unimplemented in this candidate-only batch')


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
    _validate_batch_members(result, role['role'])
    return result


def task_args():
    parser = argparse.ArgumentParser(); parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--group-root', type=Path, required=True); args = parser.parse_args()
    task, _ = _base._metadata(args.task)
    validate_group_task(task, task.get('role'), args.group_root, args.task.parent)
    _base.configure_candidate_runtime(task, args.task.parent)
    return task, args.task.parent, args.group_root


def batch_start(plan, ready, epoch):
    select_requested_roles(plan)
    need(type(ready) is list and len(ready) == 2 and set(ready) == set(REQUESTED_ROLES),
         'both and only requested scenes must be ready before the common start')
    return dict(group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], members=list(ready),
                all_members_ready=True, epoch=epoch, batch_purpose=BATCH_PURPOSE,
                requested_roles=list(REQUESTED_ROLES), deferred_roles=list(DEFERRED_ROLES),
                overall_eight_pass_rate=None, comparison=None,
                source='BothRequestedOriginalScenes_FrozenA1_N80FullDR_BeforeAnyControlledStep')


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
    return dict(kind='ACTUAL_REQUESTED_E3_W35_A1_FROZEN80_MICROBATCH_V1', batch_purpose=BATCH_PURPOSE,
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
        old20k_fullrestore_proof_preserved_separately=True, new_PPO_BPTT_GO=0, canonical_writes=0,
        training_counts_are_not_skill_success=True, epoch=epoch)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Source metadata validation only; no admission or dispatch.')
    parser.add_argument('--validate-plan', required=True, type=Path)
    args = parser.parse_args()
    plan, _ = _base._metadata(args.validate_plan)
    rows = select_requested_roles(plan)
    print(json.dumps(dict(kind='SOURCE_MICROBATCH_PLAN_VALIDATION_NOT_NATIVE',
        requested_roles=[row['role'] for row in rows], deferred_roles=list(DEFERRED_ROLES),
        overall_eight_pass_rate=None, comparison=None, resources_acquired=0, model_opens=0), sort_keys=True))
