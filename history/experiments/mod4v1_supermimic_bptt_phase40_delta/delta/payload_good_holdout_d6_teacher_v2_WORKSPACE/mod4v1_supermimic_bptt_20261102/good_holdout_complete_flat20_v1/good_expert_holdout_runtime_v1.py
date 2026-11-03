"""Good-expert ORIGINAL TEACHER holdout C878/S135 schema; original plant/barrier/close retained.

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
BATCH_FAMILY = 'GOOD_EXPERT_HOLDOUT_C878_S135_V1'
ALLOWED_SEEDS = (20260929, 20260930)
SOURCE_ENABLED = False
SOURCE_STAGED = False
PLAN_KIND = 'GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1'
REQUESTED_ROLES = ('CURB_PROTECTED878', 'SLOPE135')
STAGE_REQUIRED_ALIASES = (
    'single_gpu_good_expert_holdout_parent_v1.py', 'good_expert_holdout_runtime_v1.py',
    'embedded_teacher_reference_v1.py', 'producer_teacher_guard_v1.py', 'resume_runtime_contracts_v3.py',
    'worker_sources/e1/e1_route80_factories.py',
    'worker_sources/e1/e1_parallel_worker_safe.py', 'worker_sources/e1/e1_fresh_runtime_bridge.py',
    'a1_frozen_eval_runtime_v2.py', 'frozen_a1_raw35_v1.py', 'pose_cache_runtime_adapter_v3.py',
    'app_close_semantics_v5.py', 'native_supermimic_bridge.py',
    'supermimic_vendor_v2/networks.py', 'supermimic_vendor_v2/geometry.py', 'supermimic_vendor_v2/contract.py',
    'worker_sources/e1/worker_curb878_n80.py', 'worker_sources/e1/worker_slope135_n80.py',
    'worker_sources/e1/e1_endpoint_predicate.py', 'worker_sources/e1/ROLE_CONTRACTS.json')


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
KIND = 'GOOD_EXPERT_HOLDOUT_C878_S135_N80_TASK_V1'
INTEGRATION = 'GOOD_EXPERT_HOLDOUT_E1_EMBEDDED_TEACHER_INTEGRATION_V1'
POLICY_VARIANT = 'ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1'
_guard = _base._pinned_module('producer_teacher_guard_v1', (8902, '855e13c931eb8b8711a15b829a4ca95b10692f11b6a68df73a1dece18f98ecf0'))
validate_reference_row = _guard.validate_reference_row
_ref = _base._pinned_module('embedded_teacher_reference_v1', (16333, '400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407'))
USD, CONTRACT = _base.USD, _base.CONTRACT
need = _base.need
_validate_approved_reference = _base._validate_approved_reference
# Metadata-only wrapper below avoids pre-admission checkpoint lstat; original schema remains unchanged.
# NEW seed-bound implementation below; canonical core remains unchanged.
# These are the identical reviewed component objects, not reimplementations.
# Reference adapter is defined below; original cache implementation remains unchanged.
# NEW seed-bound implementation below; canonical core remains unchanged.
# Original error/close bodies are copied below with this explicit reference integration label.
# close_original_eval_resources: original reviewed body, defined below.
# NEW seed-bound implementation below; canonical core remains unchanged.
unresolved_evidence = _base.unresolved_evidence
# Reference policy component gate plus unchanged common cache/close semantic body, below.
OriginalA1NoResetDecisionVec = _base.OriginalA1NoResetDecisionVec
build_a1_original_vec = _base.build_a1_original_vec
DEFERRED_ROLES = tuple(role for role in ROLES if role not in REQUESTED_ROLES)
ORIGINAL_SCOPES = {role: dict(num_envs=80, seed=20260928, controls=CONTROLS[role],
    policy_hz=50, feedback_hz=100, physics_dt=.0025, TGS=[32, 4],
    physics_callbacks=CONTROLS[role] * 8, feedback_samples=CONTROLS[role] * 2)
    for role in ROLES}


POSE_PIN, POSE_VERSION, POSE_TIMING = _base.POSE_PIN, _base.POSE_VERSION, _base.POSE_TIMING
CONTEXT = {}
"""Source fragment assembled into the NEW runtime, not a native entrypoint.
All model identities below are published metadata strings; no file at those paths
is opened, resolved or statted by these functions.
"""
WORKER_ALIASES = {
    'CURB_PROTECTED878': 'worker_sources/e1/worker_curb878_n80.py',
    'SLOPE135': 'worker_sources/e1/worker_slope135_n80.py',
}
BASELINE_IDENTITIES = {
    'CURB_PROTECTED878': dict(
        source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000/roles/CURB_PROTECTED878/production/checkpoints/model_BPTT000000_I000000_S0001_complete.pt',
        source_bytes=220144758,
        source_SHA='ae4ac8d31b82c9b7488e7e40419bf2d590be6566822b78a7604e49f848e6bcfe',
        mother_source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/CURB_PROTECTED878/production/model_posttrain_final_complete_U020.pt',
        mother_source_bytes=17621306,
        mother_source_SHA='db3d5a6a2a81fb71f6f4e3ca0ee18c09785ddff80b990787960ffc3d8d376d68'),
    'SLOPE135': dict(
        source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000/roles/SLOPE135/production/checkpoints/model_BPTT000000_I000000_S0001_complete.pt',
        source_bytes=220144758,
        source_SHA='22d7ea42c208256cc5c89980472f72df71d8f279a9bc98f09c1eaa8426f2abe1',
        mother_source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR3_GENERIC_V2_20261102_131153_1793596313729480700/roles/SLOPE135/production/model_posttrain_final_complete_U020.pt',
        mother_source_bytes=17620922,
        mother_source_SHA='ec5b495691e10bf4ef6587e7fad99df02a18ff48e44f6b70d5170aaa7b641b05'),
}


def validate_seed(seed):
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'only independent holdout seed20260929 or20260930 admitted; historical20260928 is not new evidence')
    return seed


def purpose_for(seed):
    return 'GOOD_EXPERT_HOLDOUT_C878_S135_SEED' + str(validate_seed(seed)) + '_V1'


def holdout_protocol(seed):
    seed = validate_seed(seed)
    return dict(kind='INDEPENDENT_GOOD_EXPERT_HOLDOUT_SEED_PROTOCOL_V1', seed=seed,
        purpose=purpose_for(seed), published_baseline_seed=20260928,
        historical_seed_reassessment_counts_as_new_evidence=False,
        independent_group_per_seed=True, paired_effect_claim=False,
        cohort='original_env_id_mod3_ascending27_descending27_stand26',
        controls_per_role=750, num_envs=80, original_acceptance_unchanged=True)


def current_seed():
    need(CONTEXT and 'task' in CONTEXT, 'one configured holdout task is required before factory/seed use')
    return validate_seed(CONTEXT['task']['seed'])


def _validate_zero_update_baseline(row):
    role = row['role']; need(role in REQUESTED_ROLES, 'only good-expert source containers')
    producer = _producer_descriptor(row.get('a1_producer'), role)
    final = producer['FINAL']; checkpoint = final['checkpoint']; expected = BASELINE_IDENTITIES[role]
    need(final['actual_BPTT_policy_steps'] == 0 and checkpoint.get('iteration') == 0
         and all(type(value) is int and value == 0 for value in final['counts'].values()),
         'baseline is actual0 fullfreshcapture, not a trained SM candidate')
    for key, source_key in (('path', 'source_path'), ('bytes', 'source_bytes'), ('SHA', 'source_SHA')):
        need(checkpoint[key] == expected[source_key], 'published source-container identity differs: ' + key)
    teacher = final['teacher']
    for key in ('source_path', 'source_bytes', 'source_SHA'):
        need(teacher[key] == expected['mother_' + key], 'published original motherteacher identity differs: ' + key)
    need(checkpoint.get('teacher_source') == teacher and row.get('original_bootstrap_teacher') == teacher
         and teacher.get('teacher_frozen') is True, 'source-container/motherteacher identity distinction required')
    return producer


def _validate_e1_execution(final, row):
    seed = validate_seed(row.get('seed'))
    need(final.get('seed') == seed and final.get('holdout_protocol') == row.get('holdout_protocol') == holdout_protocol(seed),
         'actual E1 FINAL seed/independent purpose differs')
    need(final.get('physics') == 6000 and final.get('feedback') == 1500 and final.get('actor_calls') == 750,
         'original E1 physical/control/feedback/actor counts incomplete')
    for key in ('fresh_fullDR_before', 'fresh_fullDR_after'):
        audit = final.get(key)
        need(type(audit) is dict and audit.get('original_seed') == seed
             and audit.get('purpose') == purpose_for(seed) and audit.get('one_explicit_fresh_reset') == 1
             and audit.get('fresh_N80_D0_D7_enabled') is True
             and audit.get('saved20k_history_physically_applied') is False
             and audit.get('new_constructor_nominals_preserved') is True,
             'original fresh N80 seed/D0D7/reset receipt missing: ' + key)
    _absolute_skill(row['role'], final)
    return True


def summarize_independent_seed_results(results):
    """Metadata-only conditional counts, no new acceptance or global quality claim.

    Call only on two externally qualified, actually waited batch FINALs. This
    function creates no wait/admission/native measurement proof of its own.
    """
    import math
    need(type(results) is list and len(results) == 2 and {r.get('seed') for r in results} == set(ALLOWED_SEEDS),
         'exact independent two-seed results required; duplicate seed is not a replicate')
    need(len({r.get('group_id') for r in results}) == 2, 'each seed needs its own independent group')
    def interval(k, n):
        z = 1.959963984540054; p = k / n; a = 1 + z*z/n
        mid = (p + z*z/(2*n)) / a
        half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / a
        return dict(numerator=k, denominator=n, rate=p, wilson95=[max(0., mid-half), min(1., mid+half)])
    for result in results:
        _batch_fields(result)
        need(result.get('kind') == 'ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1'
             and result.get('all_requested_actual_execution_complete') is True
             and result.get('requested_ready_before_start') is True, 'actually qualified per-seed batch required')
        rows = result.get('rows')
        need(type(rows) is list and len(rows) == 2 and {r.get('role') for r in rows} == set(REQUESTED_ROLES)
             and all(_terminal_success(r) for r in rows), 'actual two waited semantic terminal rows required')
        for row in rows:
            source = row['data']['source_cache']; expected = BASELINE_IDENTITIES[row['role']]
            need(all(source.get(key) == expected[key] for key in ('source_path', 'source_SHA', 'source_bytes'))
                 and source.get('actual_BPTT_policy_steps') == 0
                 and source.get('original_bootstrap_teacher', {}).get('source_SHA') == expected['mother_source_SHA'],
                 'fixed original-teacher baseline identity required for conditional seed aggregation')
            _validate_e1_execution(row['data'], dict(seed=result['seed'], holdout_protocol=result['holdout_protocol'], role=row['role']))
            actual = _absolute_skill(row['role'], row['data'])
            need(actual == result['absolute_original_scope_results'][row['role']], 'per-seed counts differ from original endpoint rows')
            need(row['data']['seed'] == result['seed'] and row['data']['evaluation_purpose'] == result['batch_purpose'], 'cross-seed terminal data')
    summary = {}
    for role in REQUESTED_ROLES:
        stats = [result['absolute_original_scope_results'][role] for result in results]
        by_direction = {}
        for direction in ('ascending', 'descending'):
            denominator = sum(stat[direction]['denominator'] for stat in stats)
            by_direction[direction] = {metric: interval(sum(stat[direction][metric] for stat in stats), denominator)
                                       for metric in ('complete', 'contact_confirmed')}
        by_direction['stand'] = interval(sum(stat['stand']['no_failure'] for stat in stats),
                                         sum(stat['stand']['denominator'] for stat in stats))
        summary[role] = by_direction
    return dict(kind='CONDITIONAL_TWO_SEED_METADATA_SUMMARY_NOT_NEW_NATIVE_PROOF_V1', seeds=list(ALLOWED_SEEDS),
        role_results=summary, seedwise_results=copy.deepcopy(results), pooled_whole_skill_rate=None,
        ninety_percent_whole_skill_claim=None, relative_improvement=None, noninferiority_claim=None,
        seed_independence='protocol_independent_seed_not_IID_or_UID_equivalence_proof',
        intervals='descriptive_Wilson95_per_direction_or_standing_not_simultaneous_or_cluster_adjusted',
        original_thresholds_changed=False, admission_or_wait_proof_created_here=False)

def validate_paired_protocol(protocol):
    need(type(protocol) is dict and protocol.get('kind') == 'PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', 'paired reset protocol required')
    reference, candidate = protocol.get('reference_planned_protocol'), protocol.get('candidate_planned_protocol')
    expected = dict(pose_source_SHA=POSE_PIN[1], pose_source_bytes=POSE_PIN[0],
                    pose_source_version=POSE_VERSION, install_timing=POSE_TIMING,
                    seed=validate_seed(candidate.get('seed') if type(candidate) is dict else None), num_envs=80, explicit_original_reset_count=1,
                    physics_dt=.0025, control_dt=.02, feedback_hz=100,
                    actor_observation='original_noisy_delayed_policy35')
    need(type(reference) is dict and type(candidate) is dict and reference == candidate == expected,
         'mother/candidate planned reset/cache protocol must be identical')
    need(protocol.get('historical_bug_baseline_reused') is False, 'historical unpaired cache-bug baseline is not a paired reference')
    # Real reference receipt/UID matching is evidence, not invented from config.
    reference_actual = protocol.get('reference_actual_receipt')
    need(reference_actual is None or type(reference_actual) is dict, 'reference actual receipt is mapping or null')
    if reference_actual is not None:
        need(reference_actual.get('protocol') == expected and reference_actual.get('passed_execution') is True,
             'provided reference receipt contradicts paired protocol')
        need(type(reference_actual.get('eval_id')) is str and reference_actual['eval_id'], 'actual reference eval id required')
    return expected

def configure_candidate_runtime(task, case):
    need(not CONTEXT, 'one evaluation context, no same-purpose restart')
    CONTEXT.update(task=task, case=Path(case), pose_handle=None, pose_installed=False,
                   pose_event_counts={}, first_pose_events=[], last_pose_event=None,
                   reference_comparison=None)

def install_paired_pose_before_original_reset(env):
    need(CONTEXT and not CONTEXT['pose_installed'], 'one paired pose installer before the original explicit reset')
    task, case = CONTEXT['task'], CONTEXT['case']
    protocol = validate_paired_protocol(task['paired_reset_protocol'])
    pose = _pinned_module('pose_cache_runtime_adapter_v3', POSE_PIN)
    def record(event):
        need(type(event) is dict, 'pose event mapping required')
        # Bounded metadata only, never observe SDK fields or alter actor observations.
        name = event.get('event', 'UNKNOWN')
        counts = CONTEXT['pose_event_counts']; counts[name] = counts.get(name, 0) + 1
        if len(CONTEXT['first_pose_events']) < 3:
            CONTEXT['first_pose_events'].append(event)
        CONTEXT['last_pose_event'] = event
        put_json(case / 'PAIRED_POSE_CACHE_EVENTS_V2.json', dict(kind=INTEGRATION, protocol=protocol,
                 counters=dict(counts), first=list(CONTEXT['first_pose_events']), last=event))
    handle = pose.install_pose_cache_runtime_adapter_v3(env.scene['robot'], receipt_callback=record)
    CONTEXT.update(pose_handle=handle, pose_installed=True)
    return handle

def paired_protocol_receipt():
    if not CONTEXT:
        return None
    task = CONTEXT['task']; actual_reference = task['paired_reset_protocol'].get('reference_actual_receipt')
    return dict(protocol=validate_paired_protocol(task['paired_reset_protocol']),
                candidate_pose_installed=CONTEXT['pose_installed'], counters=dict(CONTEXT['pose_event_counts']),
                declared_reference_receipt_metadata=actual_reference,
                declared_reference_protocol_matches=(True if actual_reference is not None else None),
                reference_receipt_verification=None, actual_reference_same_protocol=None,
                historical_bug_baseline_reused=False, UID_alignment=None, raw_reference_cache_match=None,
                reward_effect_identification=None, baseline_adjusted_improvement=None)


def _batch_fields(value):
    need(value.get('policy_variant') == POLICY_VARIANT, 'explicit original teacher reference policy required')
    need(type(value) is dict and value.get('batch_purpose') == purpose_for(value.get('seed')),
         'explicit independent ORIGINAL TEACHER reference purpose required')
    need(value.get('requested_roles') == list(REQUESTED_ROLES)
         and type(value.get('requested_roles')) is list, 'this version requests C878 then S135 only')
    need(value.get('deferred_roles') == list(DEFERRED_ROLES)
         and type(value.get('deferred_roles')) is list, 'all six unrequested roles must be explicit deferred')
    need('overall_eight_pass_rate' in value and value['overall_eight_pass_rate'] is None,
         'subset cannot assert an eight-role pass rate')
    need(value.get('comparison') is None, 'reference-only execution has no paired improvement')
    need(value.get('holdout_protocol') == holdout_protocol(value['seed']), 'explicit independent seed protocol differs')


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
         and set(STAGE_REQUIRED_ALIASES) <= set(relatives), 'all twenty complete holdout overlay mappings must be present once')


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
            if key == 'seed':
                expected = plan['seed'] if role in REQUESTED_ROLES else 20260928
            if key in row:
                need(type(row[key]) is type(expected) and row[key] == expected,
                     'original role scope differs: ' + role + ':' + key)
    need(plan.get('asset_SHA') == USD and plan.get('contract_SHA') == CONTRACT,
         'original asset/contract plan identity differs')
    need(type(plan.get('group_id')) is str and plan['group_id']
         and type(plan.get('GPU_UUID')) is str and plan['GPU_UUID'], 'own group/GPU identity required')
    need(validate_paired_protocol(plan.get('paired_reset_protocol'))['seed'] == plan['seed'], 'plan/pose seed binding differs')
    need(plan['paired_reset_protocol'].get('reference_actual_receipt') is None,
         'same-seed configuration does not establish matched reference/candidate UID or pose')
    selected = [by_role[role] for role in REQUESTED_ROLES]
    for row in selected:
        need(row.get('worker') == WORKER_ALIASES[row['role']],
             'requested E1 worker must retain its original installed alias')
        _validate_zero_update_baseline(row)
        validate_reference_row(row)
    return selected


def _validate_batch_members(task, role):
    _batch_fields(task)
    need(validate_paired_protocol(task.get('paired_reset_protocol'))['seed'] == task['seed'], 'task/pose seed binding differs')
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
    for key, value in dict(num_envs=80, seed=validate_seed(task.get('seed')), optimizer_updates=0, fresh_fullDR_cohort=True,
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
    validate_reference_row(task)
    _validate_zero_update_baseline(task)
    _validate_approved_reference(task)
    producer = _producer_descriptor(task.get('a1_producer'), role)
    checkpoint = producer['FINAL']['checkpoint']
    need(all(task.get(task_key) == checkpoint[checkpoint_key] for task_key, checkpoint_key in
             (('source_path', 'path'), ('source_SHA', 'SHA'), ('source_bytes', 'bytes'))),
         'observer source identity must be the same admitted own A1 checkpoint')
    validate_paired_protocol(task.get('paired_reset_protocol'))
    return True


def make_task(role, plan, deadline, fds):
    # Same source-only task producer interface as the original parent; no C/model reads.
    result = dict(role)
    result.update(kind=KIND, purpose=KIND, integration=INTEGRATION,
                  group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], num_envs=80,
                  seed=validate_seed(plan.get('seed')), optimizer_updates=0, fresh_fullDR_cohort=True,
                  saved20k_DR_physically_applied=False, state_projection_or_slicing=False,
                  whole20k_savedrestore_claim=False, policy_hz=50, feedback_hz=100,
                  physics_dt=.0025, TGS=[32, 4], closure_m=.01, mimic_rad=.01, gas_N=400,
                  stiffness_N_m=2000, damping_Ns_m=3., physics_callbacks=role['controls'] * 8,
                  feedback_samples=role['controls'] * 2, asset_SHA=plan['asset_SHA'], contract_SHA=plan['contract_SHA'],
                  paired_reset_protocol=plan['paired_reset_protocol'],
                  approved_RSL_model_source=plan.get('approved_RSL_model_source', dict(APPROVED_RSL_MODEL_SOURCE)),
                  approved_reference_provenance=plan.get('approved_reference_provenance', dict(APPROVED_REFERENCE_PROVENANCE)),
                  absolute_worker_deadline_epoch=deadline, eval_members=list(ROLES),
                  actual_group_admission=dict(group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], source_SDK_admitted=True,
                                              private_GPU_EX_held=True, global_finite_EX_held=True, inherited_lock_fds=list(fds)))
    _validate_approved_reference(result)
    producer = _producer_descriptor(result.get('a1_producer'), result['role'])
    checkpoint = producer['FINAL']['checkpoint']
    result.update(source_path=checkpoint['path'], source_SHA=checkpoint['SHA'], source_bytes=checkpoint['bytes'],
                  source_identity='OWN_A1_FULL_NEW_CHECKPOINT_NOT_MOTHER_OR_OLD_PPO')
    validate_paired_protocol(result['paired_reset_protocol'])
    result.update(batch_purpose=purpose_for(plan['seed']), requested_roles=list(REQUESTED_ROLES),
                  deferred_roles=list(DEFERRED_ROLES), role_catalog=list(ROLES), eval_members=list(REQUESTED_ROLES),
                  overall_eight_pass_rate=None, comparison=None, policy_variant=POLICY_VARIANT,
                  holdout_protocol=holdout_protocol(plan['seed']))
    need(role in select_requested_roles(plan) and role['role'] in REQUESTED_ROLES, 'exact selected E1 row required')
    validate_reference_row(result)
    _validate_batch_members(result, role['role'])
    return result


def task_args():
    parser = argparse.ArgumentParser(); parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--group-root', type=Path, required=True); args = parser.parse_args()
    task, _ = _base._metadata(args.task)
    validate_group_task(task, task.get('role'), args.group_root, args.task.parent)
    configure_candidate_runtime(task, args.task.parent)
    _base.put_json(args.task.parent / 'REFERENCE_POLICY_IDENTITY.json', dict(policy_variant=POLICY_VARIANT,
        batch_purpose=purpose_for(task['seed']), actor_semantics=task['actor_semantics'], actor_container_identity=task['actor_container_identity'],
        source_path=task['source_path'], source_SHA=task['source_SHA'], source_bytes=task['source_bytes'],
        original_bootstrap_teacher=task['original_bootstrap_teacher'], actual_paired_protocol_UID_match=None))
    return task, args.task.parent, args.group_root


def batch_start(plan, ready, epoch):
    select_requested_roles(plan)
    need(type(ready) is list and len(ready) == 2 and set(ready) == set(REQUESTED_ROLES),
         'both and only requested scenes must be ready before the common start')
    return dict(policy_variant=POLICY_VARIANT, seed=plan['seed'], holdout_protocol=holdout_protocol(plan['seed']), group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], members=list(ready),
                all_members_ready=True, epoch=epoch, batch_purpose=purpose_for(plan['seed']),
                requested_roles=list(REQUESTED_ROLES), deferred_roles=list(DEFERRED_ROLES),
                overall_eight_pass_rate=None, comparison=None,
                source='BothRequestedOriginalScenes_EmbeddedOriginalTeacher_N80FullDR_BeforeAnyControlledStep')


def validate_start(task, value):
    _validate_batch_members(task, task['role'])
    _batch_fields(value)
    need(value.get('group_id') == task['group_id'] and value.get('GPU_UUID') == task['GPU_UUID']
         and value.get('all_members_ready') is True, 'own requested ready barrier differs')
    need(value['seed'] == task['seed'] and value['batch_purpose'] == task['batch_purpose'], 'cross-seed barrier substitution')
    members = value.get('members')
    need(type(members) is list and len(members) == 2 and set(members) == set(REQUESTED_ROLES),
         'no eight/nine/one-member or duplicate-members ready substitution')
    return True


def wait_group_start(task, group, maximum_seconds=900):
    """E1 ready was published by the unchanged original _ready; no reset/step/RNG here."""
    _validate_batch_members(task, task['role'])
    need(type(maximum_seconds) is int and maximum_seconds == 900, 'original ready wait900 required')
    until = min(task['absolute_worker_deadline_epoch'], time.time() + maximum_seconds)
    while time.time() < until:
        if (Path(group) / 'GROUP_ABORT.json').exists():
            raise RuntimeError('own requested holdout startup aborted')
        path = Path(group) / 'GROUP_EVAL_START.json'
        if path.exists():
            value, _ = _metadata(path)
            validate_start(task, value)
            put_json(Path(group) / 'cases' / task['role'] / 'WORKER_EVAL_STARTED.json',
                     dict(epoch=time.time(), GPU_UUID=task['GPU_UUID'], role=task['role'],
                          group_id=task['group_id'], seed=task['seed'], batch_purpose=task['batch_purpose']))
            return value
        time.sleep(.1)
    raise TimeoutError('requested original ready barrier 900s expired without stepping')


def _absolute_skill(role, data):
    """Extract existing EndpointPredicate + published standing assessor, not a new skill gate."""
    need(role in REQUESTED_ROLES and type(data) is dict, 'own requested E1 metadata required')
    metrics = data['metrics']; groups = metrics['groups']; rows = metrics['rows']
    need(type(rows) is list and len(rows) == 80 and {v.get('env') for v in rows} == set(range(80)), 'original unique N80 rows required')
    need(metrics.get('standing_not_required_to_cross') is True and metrics.get('all_valid_failed_incomplete_prefixes_retained') is True, 'original endpoint scope differs')
    result = {}
    for index, (group, denominator) in enumerate((('ascending', 27), ('descending', 27), ('stand', 26))):
        subset = [v for v in rows if v['group'] == group]
        need(len(subset) == denominator and all(v['env'] % 3 == index for v in subset), 'original fixed directional cohort differs')
        for v in subset:
            need(type(v.get('complete')) is bool and type(v.get('contact_confirmed')) is bool, 'original endpoint bool required')
            need(not v['contact_confirmed'] or v['complete'], 'contact endpoint must be complete')
            failure = v['first_ordinary_failure_control']
            need(failure is None or type(failure) is int and 0 <= failure < 750, 'original failure control differs')
        ncomplete = sum(v['complete'] for v in subset); ncontact = sum(v['contact_confirmed'] for v in subset)
        need(groups[group] == dict(environments=denominator, complete_envs=ncomplete, contact_confirmed_envs=ncontact), 'original group/row counts differ')
        if group == 'stand':
            # Exact existing assess_pair3_retention_closed_metadata_v1.py no_failure rule.
            no_failure = sum(v['first_ordinary_failure_control'] is None for v in subset)
            result[group] = dict(denominator=denominator, no_failure=no_failure,
                                 no_failure_rate=no_failure / denominator, crossing_required=False)
        else:
            result[group] = dict(denominator=denominator, complete=ncomplete, contact_confirmed=ncontact,
                                 complete_rate=ncomplete / denominator, contact_confirmed_rate=ncontact / denominator)
    return dict(scope='ORIGINAL_E1_CONDITIONAL_DIRECTION_AND_STANDING_ONLY', **result,
                whole_skill_rate=None, new_acceptance_predicate=None, full_expert_graduation=None)


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
    return dict(kind='ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1', batch_purpose=purpose_for(plan['seed']), policy_variant=POLICY_VARIANT,
        seed=plan['seed'], holdout_protocol=holdout_protocol(plan['seed']), group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'], requested_roles=list(REQUESTED_ROLES),
        deferred_roles=list(DEFERRED_ROLES), original_eight_role_catalog=copy.deepcopy(plan['roles']),
        original_scopes={role: dict(scope, seed=plan['seed']) if role in REQUESTED_ROLES else copy.deepcopy(scope) for role, scope in ORIGINAL_SCOPES.items()}, published_baseline_seed=20260928, common_start_epoch=group_start,
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


_metadata = _base._metadata
_pinned_module = _base._pinned_module
put_json = _base.put_json
APP_PIN = _base.APP_PIN
APPROVED_RSL_MODEL_SOURCE = _base.APPROVED_RSL_MODEL_SOURCE
APPROVED_REFERENCE_PROVENANCE = _base.APPROVED_REFERENCE_PROVENANCE
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


class ReferenceCaller(_ref.EmbeddedTeacherReferenceCaller):
    def receipt(self):
        return dict(super().receipt(), paired_reset_protocol=paired_protocol_receipt(), unresolved_evidence=unresolved_evidence())


class A1CheckpointAdapter(_base.A1CheckpointAdapter):
    """Same ONE whole A1 cache; effective actor is only the embedded original teacher."""
    def __init__(self, torch_module, task):
        validate_reference_row(task)
        super().__init__(torch_module, task)
    def actor(self, device, n=80):
        original = super().actor(device, n)
        from tensordict import TensorDict
        reference = _ref.EmbeddedTeacherMeanReference(original.mean, tensor_dict_cls=TensorDict,
            producer_final=self.task['a1_producer']['FINAL'], expected_rsl_source=self.task['approved_RSL_model_source'],
            producer_freeze_evidence=validate_reference_row(self.task))
        self.caller = ReferenceCaller(reference, boundary=original.boundary)
        return self.caller
    def receipt(self):
        result = dict(self.cache.receipt(), integration=INTEGRATION, policy_variant=POLICY_VARIANT,
            policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN', batch_purpose=purpose_for(self.task['seed']),
            actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
            original_bootstrap_teacher=dict(self.task['original_bootstrap_teacher']),
            producer_teacher_freeze_evidence=validate_reference_row(self.task),
            old_RSL_actor_checkpoint_loader_used=False,
            approved_reference_provenance=dict(self.task['approved_reference_provenance']),
            approved_RSL_model_source=dict(self.task['approved_RSL_model_source']),
            actual_eval_RSL_source_binding=(dict(self.caller.mean.actual_RSL_source) if self.caller is not None else None),
            admitted_producer_run_id=self.task['a1_producer']['run_id'],
            actual_BPTT_policy_steps=self.task['a1_producer']['FINAL']['actual_BPTT_policy_steps'])
        if self.caller is not None:
            reference = self.caller.receipt()
            result['embedded_teacher_reference'] = reference
            states = reference['full_teacher_state_manifest']
            norms = [row['name'] for row in states if 'norm' in row['name'].lower()]
            buffers = [row['name'] for row in states if row['kind'] == 'buffer']
            result['actual_teacher_state_capabilities'] = dict(normalization_state_names=norms, named_buffers=buffers,
                normalization='identity_no_persistent_teacher_norm_state_observed' if not norms else 'actual_manifest_above',
                persistent_buffer_case='not_applicable_no_buffer_in_actual_schema' if not buffers else 'all_buffers_value_checked',
                std_state_names=[row['name'] for row in states if 'std' in row['name'].lower()],
                whole_pi_residual_RMS_guard_still_active=True)
        return result


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
        producer = _validate_zero_update_baseline(role_entry)
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
        need(final.get('policy_variant') == POLICY_VARIANT and final.get('evaluation_purpose') == purpose_for(role_entry.get('seed')),
             'explicit reference FINAL variant/purpose required')
        _validate_e1_execution(final, role_entry)
        evidence = validate_reference_row(role_entry)
        reference = source.get('embedded_teacher_reference')
        _ref.validate_reference_semantics(reference, expected_role=role, expected_source_sha=checkpoint['SHA'],
            expected_bootstrap_teacher_sha=role_entry['original_bootstrap_teacher']['source_SHA'], expected_actor_calls=CONTROLS[role])
        need(reference.get('producer_teacher_state_guard') == evidence
             and source.get('producer_teacher_freeze_evidence') == evidence and 'frozen_mean' not in source
             and source.get('policy_variant') == POLICY_VARIANT
             and source.get('policy_family') == 'EMBEDDED_ORIGINAL_TEACHER_MEAN'
             and source.get('original_bootstrap_teacher') == role_entry['original_bootstrap_teacher'], 'reference source/producer/actor identity differs')
        paired = reference.get('paired_reset_protocol')
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
    return dict(kind='ACTUAL_WAITED_EMBEDDED_ORIGINAL_TEACHER_N80_REFERENCE_SEMANTIC_V1', role=role, group_id=group_id,
                actual_waited_returncode=returncode, passed_execution=not reasons, original_error=bool(reasons), reasons=reasons,
                original_fast_close_expected_nonreturn_accepted=bool(not reasons and intent is not None),
                actual_resource_admission_or_parent_wait_proof='CALLER_ORIGINAL_P_WAIT_REQUIRED_NOT_CREATED_HERE',
                UID_alignment=None, reference_cache_match=None, paired_reward_effect=None)

def grade_closed_reference_group(group_root):
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
        need(final.get('kind') == 'ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1'
             and final.get('group_id') == plan['group_id'] and final.get('GPU_UUID') == plan['GPU_UUID']
             and final.get('all_requested_actual_execution_complete') is True
             and final.get('requested_ready_before_start') is True
             and final.get('original_eight_role_catalog') == plan['roles'], 'original reference batch FINAL incomplete or mismatched')
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
                dict(entry, seed=plan['seed'], holdout_protocol=plan['holdout_protocol'], paired_reset_protocol=plan['paired_reset_protocol']), plan['group_id'])
            need(semantic.get('passed_execution') is True and row.get('semantic') == semantic,
                 'reference original semantic gate differs after close: ' + role)
            case_final, _ = _base._metadata(case / 'FINAL.json')
            need(row.get('data') == case_final, 'original terminal/actual case FINAL differs: ' + role)
            checked.append(role)
    except Exception as error:
        reasons.append(type(error).__name__ + ':' + str(error))
    return dict(kind='CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1', policy_variant=POLICY_VARIANT,
        batch_purpose=purpose_for(plan['seed']) if 'plan' in locals() else None, group_root=str(root), passed_closed_reference_source_grade=not reasons,
        original_error=bool(reasons), reasons=reasons, checked_roles=checked,
        external_executing_parent_actual_wait_required=True, external_parent_wait_proof_created_here=False,
        qualified_reference_execution=None, UID_alignment=None, reference_cache_match=None,
        relative_improvement=None, paired_reward_effect=None, overall_eight_pass_rate=None,
        C_or_lock_or_SDK_or_checkpoint_operations=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Source metadata validation only; no admission or dispatch.')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--validate-plan', type=Path)
    modes.add_argument('--grade-closed-group', type=Path)
    args = parser.parse_args()
    if args.grade_closed_group is not None:
        result = grade_closed_reference_group(args.grade_closed_group)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result['passed_closed_reference_source_grade'] else 1)
    plan, _ = _base._metadata(args.validate_plan)
    rows = select_requested_roles(plan)
    print(json.dumps(dict(kind='SOURCE_GOOD_EXPERT_HOLDOUT_PLAN_VALIDATION_NOT_NATIVE',
        requested_roles=[row['role'] for row in rows], deferred_roles=list(DEFERRED_ROLES),
        policy_variant=POLICY_VARIANT, reference_not_candidate=True,
        overall_eight_pass_rate=None, comparison=None, resources_acquired=0, model_opens=0), sort_keys=True))
