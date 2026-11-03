"""NEW finite-validation capture glue; original owner/EX/Popen lifecycle is external.

No old newkind/sourcehardpin or quality gate is patched. Nothing executes on
import beyond stdlib definitions. SOURCE package has not admitted any native run.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
from phase1_capture_contract import *

HERE = Path(__file__).resolve().parent
APP_PIN = (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39')
CORE_PIN = (37927, '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')
_core_value = None
ORIGINAL_COST_PROTOCOL = dict(
    route='EXISTING_QUALIFIED_FINITE_ENVIRONMENT_VALIDATION_NOT_TRAINING',
    original_parent_source='source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py:21-38,63-78',
    original_gate='private_GPU_EX + finiteEX; canonical generation/remaining>finite_minimum/activeNone',
    canonical_access_by_parent='READ_ONLY', canonical_writes_by_this_parent=0,
    training_expert_seconds_writer_in_this_parent=False, SDK_real_wall_cost_is_not_zero=True,
    actual_external_settlement_receipt='UNKNOWN_SOURCE_EVIDENCE_GAP_NOT_A_NEW_APPROVAL_GATE')


def _metadata(path, maximum=64*1024*1024):
    raw = Path(path).read_bytes()
    need(len(raw) <= maximum, 'bounded capture metadata exceeded')
    return json.loads(raw), raw


def source_index():
    return _metadata(HERE/'CAPTURE_SOURCE_INDEX.json', 2*1024*1024)[0]


def load_file(name, relative_name, identity):
    path = HERE/relative(relative_name)
    raw = path.read_bytes()
    need((len(raw), sha(raw)) == tuple(identity), 'SOURCE hardpin differs: ' + relative_name)
    if name in sys.modules:
        module = sys.modules[name]
        need(Path(module.__file__).resolve() == path.resolve(), 'actual module alias/source differs: ' + name)
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def dependency(name, relative_name):
    rows = source_index()['dependency_sources']
    row = next(x for x in rows if x['install_relative'] == relative_name)
    return load_file(name, relative_name, (row['bytes'], row['SHA256']))


def core():
    global _core_value
    if _core_value is None:
        # Independent alias, exact 37927/7a092 source; no producer or cache API called.
        _core_value = load_file('_phase1_capture_pinned_a1_core', 'a1_frozen_eval_runtime_v2.py', CORE_PIN)
    return _core_value


def _pinned_module(name, pin):
    # Original AppV6 loader also verifies full Base dependency when imported.
    return core()._pinned_module(name, pin)


def put_json(path, value, *, add_capture_epoch=True):
    value = dict(value, capture_metadata_epoch=time.time()) if type(value) is dict and add_capture_epoch else value
    path = Path(path); raw = json.dumps(value, indent=2, allow_nan=False).encode()
    need(len(raw) <= 64*1024*1024, 'bounded capture JSON exceeds64MiB')
    temporary = path.with_suffix(path.suffix+'.partial')
    with temporary.open('wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def record_primary_error(case, **value):
    path = Path(case)/'WORKER_ERROR.json'
    if path.exists():
        previous, _ = _metadata(path)
        previous.setdefault('additional_errors', []).append(value)
        value = previous
    else:
        value = dict(kind='PHASE1_CAPTURE_PRIMARY_ERROR_V1', **value)
    put_json(path, value)


def select_requested_roles(plan):
    selected = validate_plan(plan, source_index())
    result = copy.deepcopy(selected)
    for row in result: row['capture_controls'] = plan.get('capture_controls', 64)
    return result


def make_task(row, plan, deadline, fds):
    validate_plan(plan, source_index())
    need(row['role'] == 'E3' and len(fds) == 2, 'one E3 member/two inherited original EX descriptors')
    task = dict(kind=KIND, purpose=PURPOSE, batch_purpose=PURPOSE, integration=INTEGRATION,
                policy_variant=POLICY_VARIANT, role='E3', requested_roles=['E3'], role_catalog=list(ROLES),
                num_envs=80, seed=20260928, controls=plan.get('capture_controls', 64), physics=dict(PHYSICS),
                model_PT_reads=0, synthetic_action=[0., 0., 0., 0., 0., 0.], train=False,
                quality_evaluation=False, full_clean35='UNKNOWN', comparison=None, overall_eight_pass_rate=None,
                asset_SHA=USD, contract_SHA=CONTRACT, group_id=plan['group_id'], GPU_UUID=plan['GPU_UUID'],
                runtime_root=row['runtime_root'], asset_dir=row['asset_dir'],
                absolute_worker_deadline_epoch=deadline, inherited_lock_fds=list(fds),
                paired_reset_protocol=copy.deepcopy(plan['paired_reset_protocol']),
                finite_validation_cost_protocol=copy.deepcopy(plan.get('finite_validation_cost_protocol', ORIGINAL_COST_PROTOCOL)),
                canonical_access_by_worker=False, new_PPO_or_BPTT=False)
    return validate_task(task)


def validate_inherited_admission(task, admission, *, environment=None, fd_check=None, now=None):
    """Original pre-SDK GPU/deadline/two-fstat semantics; no new lock inspection."""
    environment = os.environ if environment is None else environment
    now = time.time if now is None else now
    need(admission.get('group_id') == task['group_id']
         and task['GPU_UUID'] == admission.get('resource', {}).get('GPU_UUID') == environment.get('CUDA_VISIBLE_DEVICES'),
         'original group/GPU/admission/CUDA_VISIBLE_DEVICES identity differs')
    need(admission.get('original_private_GPU_EX_held') is True
         and admission.get('original_global_finite_EX_held') is True and admission.get('canonical_writes') == 0,
         'actual unchanged original parent admission receipt required')
    fds = task.get('inherited_lock_fds')
    need(type(fds) is list and len(fds) == len(set(fds)) == 2 and all(type(x) is int and x >= 0 for x in fds),
         'original two unique nonnegative inherited descriptors')
    for fd in fds: (fd_check or os.fstat)(fd)  # Existence only, exactly original; no flock/acquire/release.
    need(type(task.get('absolute_worker_deadline_epoch')) in (int, float)
         and task['absolute_worker_deadline_epoch'] > now(), 'original finite worker deadline elapsed before SDK')
    return admission


def validate_installed_root(group, installed_root):
    """The staged runtime and its group must share the same remote tasks root."""
    group = Path(group).resolve(); installed_root = Path(installed_root).resolve()
    tasks = Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve()
    need(group.is_relative_to(tasks) and group != tasks and group == installed_root,
         'own installed group/runtime root under original remote tasks required; local SOURCE is not admission')
    return group


def validate_group_task(task, plan, group):
    validate_task(task); validate_plan(plan, source_index())
    need(task['group_id'] == plan['group_id'] == group.name and task['GPU_UUID'] == plan['GPU_UUID'], 'group/GPU identity differs')
    need(task['controls'] == plan.get('capture_controls', 64), 'NEW capture bound differs')
    admission, _ = _metadata(group/'ACTUAL_GROUP_ADMISSION.json')
    validate_inherited_admission(task, admission)
    # Verify every whole-tree retained file; the independently reviewed baseline
    # must be supplied/pinned by a future materializer. This SOURCE set creates none.
    for row in plan['retained_static_inventory']['installed']:
        path = group/relative(row['relative'])
        need(not path.is_symlink(), 'static retained file is symlink')
        raw = path.read_bytes()
        need((len(raw), sha(raw)) == (row['bytes'], row['SHA256']), 'full retained static inventory differs: ' + row['relative'])
    return admission


def task_args():
    parser = argparse.ArgumentParser(); parser.add_argument('--task', required=True); parser.add_argument('--group-root', required=True)
    args = parser.parse_args(); group = Path(args.group_root).resolve(); case = Path(args.task).resolve().parent
    validate_installed_root(group, HERE)  # Correct installation has group == runtime.parent, not group != HERE.
    task, _ = _metadata(args.task); plan, _ = _metadata(group/'GROUP_PLAN.json')
    need(case == group/'cases'/'E3', 'one E3 own case')
    validate_group_task(task, plan, group)
    core().configure_candidate_runtime(task, case)
    return task, case, group


def install_paired_pose_before_original_reset(env):
    return core().install_paired_pose_before_original_reset(env)


def paired_protocol_receipt():
    return core().paired_protocol_receipt()


def wait_start(task, case, group, ready):
    validate_task(task)
    put_json(case/'WORKER_SCENE_READY.json', dict(kind=INTEGRATION, role='E3', epoch=time.time(), ready=ready))
    until = min(task['absolute_worker_deadline_epoch'], time.time()+900)
    while time.time() < until:
        need(not (group/'GROUP_ABORT.json').exists(), 'own group aborted before common GO')
        path = group/'GROUP_EVAL_START.json'
        if path.exists():
            go, _ = _metadata(path)
            need(go.get('kind') == 'PHASE1_PASSIVE_CAPTURE_COMMON_START_V1' and go.get('purpose') == PURPOSE
                 and go.get('group_id') == task['group_id'] and go.get('members') == ['E3'], 'NEW purpose common GO differs')
            put_json(case/'WORKER_EVAL_STARTED.json', dict(kind=INTEGRATION, role='E3', epoch=time.time(), GO_epoch=go['epoch'],
                     SDK_wall_cost_is_not_zero_by_PT0=True, original_cost_protocol=task['finite_validation_cost_protocol']))
            return go
        time.sleep(.25)
    raise TimeoutError('Original ready barrier900s or own finite deadline reached')


def batch_start(plan, ready, epoch):
    select_requested_roles(plan)
    need(ready == ['E3'], 'NEW explicit E3-only common start')
    return dict(kind='PHASE1_PASSIVE_CAPTURE_COMMON_START_V1', purpose=PURPOSE, group_id=plan['group_id'],
                members=['E3'], epoch=epoch, policy_variant=POLICY_VARIANT, stage2_GO=False)


def evaluate_waited_eval_case(case, rc, row, group_id):
    """Only after original p.wait. Execution closure != interface/Gate1 proof."""
    case = Path(case); errors = []; final = None
    try:
        need(type(rc) is int and rc == 0, 'actual waited returncode must be zero; RC0 alone is insufficient')
        need(not (case/'WORKER_ERROR.json').exists(), 'primary worker error remains')
        task, _ = _metadata(case/'task.json'); final, raw = _metadata(case/'FINAL.json')
        need(task['group_id'] == group_id and row['role'] == 'E3' and task['controls'] == row.get('capture_controls', 64), 'waited task identity/bound differs')
        validate_preclose(final, task)
        env, _ = _metadata(case/'ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json'); need(env.get('closed') is True, 'original env close not returned')
        binding, _ = _metadata(case/'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json')
        helper = _pinned_module('app_close_semantics_v5', APP_PIN)
        if binding.get('fast_shutdown') is True:
            helper._validate_binding_receipt(binding)
            intent, _ = _metadata(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json')
            need(intent.get('kind') == 'PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1' and intent.get('final_SHA') == sha(raw)
                 and intent.get('final_bytes') == len(raw) and intent.get('binding') == binding
                 and intent.get('original_env_close_returned') is True, 'exact capture preclose intent missing/different')
        else:
            core()._validate_returned_app_binding(binding, helper)
            returned, _ = _metadata(case/'APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json')
            need(returned.get('returned') is True and returned.get('binding') == binding, 'actual original App close returned receipt missing')
    except BaseException:
        errors.append(traceback.format_exc())
    return dict(kind='PHASE1_CAPTURE_WAITED_EXECUTION_SEMANTICS_V1', purpose=PURPOSE, passed_execution=not errors,
                errors=errors, native_interface_verified=False, interface_status='INCONCLUSIVE_PENDING_LIVE_VERIFIER',
                gate1='UNKNOWN', exact=False, capture_interface_passed=False, skill_success_rate=None,
                actual_wait_call_attested_by_caller=True, waited_return_observed_epoch=time.time(), independent_parent_wait_and_EX_release_pending=True,
                observed_final_kind=None if final is None else final.get('kind'))


def batch_result(plan, terminal, group_start, epoch):
    return dict(kind='PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1', purpose=PURPOSE, integration=INTEGRATION,
                group_id=plan['group_id'], requested_roles=['E3'], deferred_roles=list(ROLES[1:]), terminal=terminal,
                passed_execution=len(terminal)==1 and terminal[0].get('actual_waited') is True and terminal[0].get('passed_execution') is True,
                GO_epoch=group_start, terminal_epoch=epoch, GO_to_terminal_wall_seconds=None if group_start is None else epoch-group_start,
                finite_validation_cost_protocol=plan.get('finite_validation_cost_protocol'),
                cost_settlement='EXISTING_ORIGINAL_PROTOCOL_ONLY_NO_NEW_WRITER; ACTUAL_RECEIPT_PENDING_PARENT_REVIEW',
                SDK_wall_cost_is_not_zero_by_PT0=True, canonical_writes_by_new_code=0,
                interface_status='INCONCLUSIVE_PENDING_LIVE_VERIFIER', capture_interface_passed=False,
                gate1='UNKNOWN', exact=False, stage2_GO=False, overall_eight_pass_rate=None)


def grade_closed_capture_group(group):
    group = Path(group); errors = []; final = None
    try:
        need(not (group/'PARENT_ORIGINAL_ERROR.json').exists(), 'parent error exists')
        final, _ = _metadata(group/'FINAL.json'); scope, _ = _metadata(group/'PARENT_EXIT_SCOPE.json')
        need(final.get('kind') == 'PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1' and final.get('purpose') == PURPOSE
             and final.get('passed_execution') is True, 'NEW purpose group execution FINAL required')
        need(scope.get('all_own_children_waited') is True and scope.get('original_single_GPU_private_EX_released') is True
             and scope.get('original_global_finite_EX_released') is True and scope.get('canonical_writes') == 0
             and not scope.get('errors'), 'actual unchanged wait/finally full EX release receipt required')
        need(len(scope.get('child_waits', [])) == 1 and scope['child_waits'][0].get('actual_waited') is True
             and scope['child_waits'][0].get('role') == 'E3', 'one original actual child wait required')
    except BaseException: errors.append(traceback.format_exc())
    return dict(kind='PHASE1_CAPTURE_CLOSED_SOURCE_GRADE_V1', purpose=PURPOSE, passed_closed_capture_execution=not errors,
                errors=errors, capture_interface_passed=False, gate1='UNKNOWN', exact=False, stage2_GO=False,
                outer_controller_actual_parent_Popen_wait='PENDING_REQUIRED_SEPARATE_RECEIPT',
                SDK_cost_settlement_verified=False, original_finite_validation_protocol_retained=True,
                external_settlement_reference='UNKNOWN_SOURCE_EVIDENCE_GAP_NO_NEW_APPROVAL_GATE')

# close_original_eval_resources body is mechanically copied from the complete
# original evaluator with NEW capture-only predicate/labels.
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
            publish(case / 'ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json', dict(closed=True))
        except BaseException:
            remember('original_env_close')
    else:
        publish(case / 'ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json', dict(closed=env_already_closed))
    publish(case / 'PRE_CLOSE.json', dict(kind=INTEGRATION, role=task['role'], group_id=task['group_id'],
             original_env_close_returned=bool((case / 'ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json').exists() and not errors),
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
        put_json(case / 'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json', binding, add_capture_epoch=False)
        if not errors and not (case / 'WORKER_ERROR.json').exists() and (case / 'FINAL.json').exists():
            final, raw = _metadata(case / 'FINAL.json')
            validate_preclose(final, task)  # NEW capture-only predicate; no old quality/training predicate relaxed.
            if binding['fast_shutdown']:
                put_json(case / 'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json', dict(kind='PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1',
                         role=task['role'], group_id=task['group_id'], final_SHA=hashlib.sha256(raw).hexdigest(),
                         final_bytes=len(raw), binding=binding, original_env_close_returned=True,
                         publication='FSYNC_ATOMIC_METADATA_BEFORE_ORIGINAL_APP_CLOSE', actual_parent_wait=None))
    except BaseException:
        remember('actual_original_app_binding_or_intent')
    try:
        publish(case / 'APP_CLOSE_CALLED_PHASE1_CAPTURE_V1.json', dict(epoch=time.time(), original_call_about_to_execute=True))
        app.close()  # EXACT original call, no mode changes, no replacement close, once.
        put_json(case / 'APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json', dict(returned=True, binding=binding))
    except BaseException:
        remember('original_App_close_raised')
    return errors

