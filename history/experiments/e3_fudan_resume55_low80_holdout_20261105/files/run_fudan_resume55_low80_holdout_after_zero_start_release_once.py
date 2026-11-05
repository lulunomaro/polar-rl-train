"""Wait for the sole first collector, then bounded summary-only release observation.
No first-purpose replay or additional first-purpose remote collector.  A release
snapshot is not a lease: the unchanged Admission2 parent checks fresh resources.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import time

PREFIX = 'FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_'
INPUT_CLI_PINS = {'stage_fudan_resume55_low80_holdout_once.py': {'bytes': 24731, 'sha256': '363a5a001a1e36157dc0692e8ca052ea1bea55444fa67e09616e381e51da2567'}, 'dispatch_fudan_resume55_low80_holdout_once.py': {'bytes': 8904, 'sha256': '1354cfb96ced9903387a283a31be3f493dcc8163c3c81f30474f8975658dcaa6'}, 'collect_fudan_resume55_low80_holdout_once.py': {'bytes': 9520, 'sha256': '116907012e813ad2b30392c6f9a46306d477da8e29ca578413c50123e04ab4f0'}}
DERIVED_CLI_PINS = {'stage_fudan_resume55_low80_holdout_admission2_once.py': {'bytes': 36017, 'sha256': 'db16ab306eed1eabff16d3b9bcc536ebf40eeb3fb4b058c3a26691920fd41e92'}, 'dispatch_fudan_resume55_low80_holdout_admission2_once.py': {'bytes': 8992, 'sha256': 'a376bbdba6961a00e081f4e1d63b73a93e0d688ac37b39eea7ab4228235f9dfb'}, 'collect_fudan_resume55_low80_holdout_admission2_once.py': {'bytes': 9571, 'sha256': 'f60c598c8ff9efc850a846047c36097a079633ea0a7ac4a8a9d307600c03db78'}}
RESOURCE_QUERY = "from pathlib import Path\nimport json,time,math\nP=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')\ndef need(ok):\n if not ok:raise ValueError('summary schema gap')\ndef number(v):return type(v)in(int,float)and math.isfinite(v)\ntry:\n c=json.loads(P.read_bytes());need(type(c)is dict)\n generation=c['authority_generation'];remaining=c['remaining_training_seconds'];floor=c['finite_minimum_remaining_seconds'];active=c['active_segment']\n need(type(generation)is str and number(remaining)and number(floor)and remaining>=0 and floor>=0)\n owner=None\n if active is not None:\n  need(type(active)is dict)\n  run=active['owner_run_id'];pid=active['pid'];parent=active['owner_parent_pid'];started=active['started_epoch']\n  need(type(run)is str and bool(run)and type(pid)is int and pid>0 and type(parent)is int and parent>0 and number(started)and started>0)\n  owner=dict(owner_run_id=run,pid=pid,owner_parent_pid=parent,started_epoch=started)\n summary=dict(authority_generation=generation,remaining_training_seconds=remaining,finite_minimum_remaining_seconds=floor,active_owner=owner)\n print(json.dumps(dict(epoch=time.time(),canonical_summary=summary,schema_gap=None,read_only_summary=True),allow_nan=False))\nexcept Exception as e:\n print(json.dumps(dict(epoch=time.time(),canonical_summary=None,schema_gap=type(e).__name__,read_only_summary=True)))"

# BEGIN_ADMISSION2_EXACT_FIRST_ZERO_START_GUARD
_A2_FIRST_PREFIX = 'FDNRESUME55_LOW80_HOLDOUT_'
_A2_FIRST_ROOT = '/home/lc01/Zonglin Li/zonglin2/tasks/FDNRESUME55_LOW80_HOLDOUT_THREE_SEED_N80_20261105_105212_1793847132730709700'
_A2_LOCAL_DIR = 'F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104'
_A2_W12_CLOSED = 'F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W14_RESUME55_ADMISSION2_20261105_101210/CLOSED_RESULT.json'
_A2_W12_CLOSED_SHA = '663bb6c0b8f0e52d97f169db0240de03a2b8507b9d246d9c31cecc0e0b3cfe27'
_A2_PARENT = dict(pid=1650042, linux_start_ticks=158855248)
_A2_CONTROLLER = dict(pid=1650035, linux_start_ticks=158855229)
_A2_PARENT_SOURCE_SHA = '5f3e6d621f28ca9de7b95dbcf2ef0fafddc5287537680631a1e63fdd682e963c'
_A2_CONTROLLER_SOURCE_SHA = '2544ae2552e3a88d118005794ea81035b9a99a737f7d74e8f4fe2c8067c89a40'
_A2_TIMEOUT = 'Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions'
_A2_MEMBERS = ('E3_LOW80_20261002', 'E3_LOW80_20261003', 'E3_LOW80_20261004')
_A2_SOURCE = dict(
    path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_FULLRESUME55_CONTINUE25_W14_ADMISSION2_20261105_094946_1793843386314498300/roles/E3/production/fudan_seq20k_full_u000050_wu000025_c00001200_s0002.pt',
    bytes=146251569,
    sha256='8e27c2f35d5e1ed5ad2f71324e729bdbda9a10e1486b151ca1dd9384d3ecfe32',
    run='MOD4V1_E3_FUDAN_N20000_FULLRESUME55_CONTINUE25_W14_ADMISSION2_20261105_094946_1793843386314498300',
)
_A2_ROOT_NAMES = (
    'PARENT_STARTED.json', 'ACTUAL_GROUP_ADMISSION.json', 'GROUP_EVAL_START.json',
    'GROUP_BARRIER_STATUS.json', 'BOUNDED_ORIGINAL_RESOURCE_WAIT.json',
    'GROUP_ABORT.json', 'PARENT_ORIGINAL_ERROR.json', 'TERMINAL_ROWS.json',
    'FINAL.json', 'PARENT_EXIT_SCOPE.json',
    'FDNRESUME55_LOW80_HOLDOUT_OUTER_DISPATCH.json', 'FDNRESUME55_LOW80_HOLDOUT_PARENT_WAITED_ACTUAL.json',
)
_A2_CASE_NAMES = (
    'task.json', 'WORKER_SCENE_READY.json', 'WORKER_EVAL_STARTED.json',
    'FRESH80_FULLDR_BEFORE_CONTROL.json', 'FINAL.json', 'PRE_CLOSE.json',
    'FDN_N80_APP_CLOSE_INTENT.json', 'WORKER_ERROR.json', 'ENV_CLOSE_ERROR.json',
    'APP_CLOSE_BINDING_ERROR.json', 'CLOSE_EVIDENCE_ERROR.json', 'APP_CLOSE_ERROR.json',
)


def _a2_need(condition, message):
    if not condition:
        raise ValueError('Admission2 first-purpose guard: ' + message)


def _a2_number(value):
    import math
    return type(value) in (int, float) and math.isfinite(value)


def _a2_json(path):
    blob = path.read_bytes()
    value = json.loads(blob)
    _a2_need(type(value) is dict, 'object metadata required: ' + path.name)
    return blob, value


def _a2_zero_start_guard(D, original_w12_closed):
    _a2_need(D.resolve() == Path(_A2_LOCAL_DIR).resolve(), 'fixed local source directory')
    _a2_need(Path(original_w12_closed).resolve() == Path(_A2_W12_CLOSED).resolve(),
             'the original W12 CLOSED path must not be renamed or replaced')
    closed_blob, closed = _a2_json(D / (_A2_FIRST_PREFIX + 'CLOSED_RESULT.json'))
    scope_blob, scope = _a2_json(D / (_A2_FIRST_PREFIX + 'SCOPE_RESULT.json'))
    _, dispatch = _a2_json(D / (_A2_FIRST_PREFIX + 'DISPATCH_RESULT.json'))
    _, stage_mark = _a2_json(D / (_A2_FIRST_PREFIX + 'STAGE_ONCE.json'))
    _a2_need(closed['closed'] is True and closed['root'] == scope['root'] ==
             dispatch['root'] == stage_mark['root'] == _A2_FIRST_ROOT, 'exact first root and CLOSED')
    _a2_need(stage_mark['source'] == dispatch['source'] == scope['source'] == _A2_SOURCE,
             'retained first-purpose candidate source receipt')
    _a2_need(Path(stage_mark['closed_path']).resolve() == Path(_A2_W12_CLOSED).resolve() and
             stage_mark['closed_metadata_sha256'] == _A2_W12_CLOSED_SHA,
             'unchanged W12 closure provenance')
    _a2_need(type(dispatch['returncode']) is int and dispatch['returncode'] == 0 and
             dispatch['stderr'] == '' and dispatch['controller_SHA256'] == _A2_CONTROLLER_SOURCE_SHA,
             'the actual first outer dispatch source and RC0')
    metadata, cases = closed['metadata'], closed['cases']
    _a2_need(type(metadata) is dict and set(metadata) == set(_A2_ROOT_NAMES),
             'complete, exact first collector root metadata schema')
    _a2_need(type(cases) is dict and set(cases) == set(_A2_MEMBERS), 'all three first cases')
    for member in _A2_MEMBERS:
        row = cases[member]
        _a2_need(type(row) is dict and set(row) == set(_A2_CASE_NAMES) and
                 all(value is None for value in row.values()),
                 'all first-case task/SDK/cache/close/error/final metadata must be null: ' + member)
    for name in ('ACTUAL_GROUP_ADMISSION.json', 'GROUP_EVAL_START.json',
                 'GROUP_BARRIER_STATUS.json', 'TERMINAL_ROWS.json', 'FINAL.json'):
        _a2_need(metadata[name] is None, 'first purpose must have zero actual start: ' + name)
    started = metadata['PARENT_STARTED.json']
    _a2_need(type(started) is dict and type(started['pid']) is int and
             started['pid'] == _A2_PARENT['pid'] and _a2_number(started['creation']) and
             _a2_number(started['epoch']) and started['creation'] > 0 and
             started['kind'] == 'ONEGPU_E3_LOW80_THREE_SEED_HOLDOUT_RESUME55_NO_LEARNING',
             'actual first PARENT_STARTED pid1650042')
    first_outer = metadata[_A2_FIRST_PREFIX + 'OUTER_DISPATCH.json']
    waited = metadata[_A2_FIRST_PREFIX + 'PARENT_WAITED_ACTUAL.json']
    _a2_need(first_outer == dispatch['dispatch'] and first_outer['root'] == _A2_FIRST_ROOT and
             first_outer['controller'] == _A2_CONTROLLER and first_outer['parent'] == _A2_PARENT and
             first_outer['original_parent_SHA256'] == _A2_PARENT_SOURCE_SHA and
             first_outer['original_parent_Popen_calls'] == 1 and
             first_outer['roles'] == list(_A2_MEMBERS), 'actual first controller/parent identity and source')
    _a2_need(waited['root'] == _A2_FIRST_ROOT and waited['controller'] == _A2_CONTROLLER and
             waited['parent'] == _A2_PARENT and waited['roles'] == list(_A2_MEMBERS) and
             waited['actual_parent_p_wait_returned'] is True and waited['original_parent_reaped'] is True and
             type(waited['returncode']) is int and waited['returncode'] == 0 and
             waited['errors'] == [] and waited['original_parent_Popen_calls'] == 1 and
             waited['controller_Cwrites_model_or_lock_operations'] == 0,
             'actual first outer wait/reaped/RC0/errors[]')
    parent_error = metadata['PARENT_ORIGINAL_ERROR.json']
    errors = parent_error['errors']
    _a2_need(parent_error['no_samepurpose_automatic_retry'] is True and
             type(errors) is list and len(errors) == 1 and type(errors[0]) is str and
             _A2_TIMEOUT in errors[0] and errors[0].rstrip().endswith('TimeoutError: ' + _A2_TIMEOUT),
             'only the original1800 zero-start timeout, not an actual execution error')
    abort = metadata['GROUP_ABORT.json']
    _a2_need(abort['errors'] == errors and abort['ownscope_only'] is True, 'preserved original timeout abort')
    exit_scope = metadata['PARENT_EXIT_SCOPE.json']
    _a2_need(exit_scope['all_own_children_waited'] is True and exit_scope['child_waits'] == [] and
             exit_scope['original_single_GPU_private_EX_released'] is True and
             exit_scope['original_global_finite_EX_released'] is True and exit_scope['errors'] == errors and
             exit_scope['no_foreign_scope_touched'] is True and exit_scope['canonical_writes'] == 0 and
             exit_scope['SDK_PT_opens_by_parent'] == 0 and _a2_number(exit_scope['wall_seconds']) and
             exit_scope['wall_seconds'] >= 1800, 'actual empty child waits and both original EX releases')
    wait_rows = metadata['BOUNDED_ORIGINAL_RESOURCE_WAIT.json']
    _a2_need(type(wait_rows) is list and len(wait_rows) > 0, 'actual bounded resource wait rows')
    for row in wait_rows:
        _a2_need(type(row) is dict and row['locks_held'] == 0 and
                 row['SDK_or_selected_model_opened'] is False and row['canonical_writes'] == 0 and
                 type(row['reason']) is str and _a2_number(row['remaining_wait_seconds']) and
                 row['remaining_wait_seconds'] >= 0, 'zero-start resource-only wait evidence')
    _a2_need(scope['execution_qualified'] is False and scope['kind'] ==
             'E3_FROZEN_CANDIDATE_LOW80_THREE_INDEPENDENT_SEED_CONFIRMATION',
             'explicit unqualified old scope')
    for key in ('aggregate_denominator', 'first_episode_stable_credits',
                'credited_and_stable_at_end', 'source_IO_group_actual', 'paired_native_difference'):
        _a2_need(scope[key] is None, 'no denominator/credits/source cache or paired result: ' + key)
    _a2_need(scope['independent_case_seeds'] == [20261002, 20261003, 20261004] and
             scope['num_envs_per_case'] == 80 and scope['controls_per_case'] == 400 and
             scope['source_IO_per_case'] == 1 and scope['source_IO_group_expected'] == 3 and
             scope['reference_native_cohorts_executed'] is False and
             scope['original_E3_74_score_recomputed'] is False and
             scope['no_cross_scope_score_combination'] is True and scope['goal_complete'] is False,
             'unchanged first candidate-only scope and honest I/O')
    old_rows = scope['cases']
    _a2_need(type(old_rows) is list and len(old_rows) == 3 and
             [row['case'] for row in old_rows] == list(_A2_MEMBERS), 'exact scope case rows')
    for row in old_rows:
        _a2_need(row['execution_qualified'] is False and
                 row['seed'] == int(row['case'].rsplit('_', 1)[1]), 'unqualified original case')
        for key in ('actual_parent_wait_qualification', 'source_cache', 'skill',
                    'failed_worker_metadata', 'D0_D7_fresh_audit_before', 'D0_D7_fresh_audit_after'):
            _a2_need(row[key] is None, 'no SDK/cache/result/error evidence in old scope: ' + key)
    expected_checks = dict(actual_external_parent_wait=True, all_own_children_waited=True,
        original_private_and_finite_released=True, parent_error_absent=False,
        actual_all_cases_terminal=False, original_parent_final_all_complete=False,
        actual_common_barrier=False)
    expected_checks.update({'case_' + member: False for member in _A2_MEMBERS})
    checks = scope['execution_checks']
    _a2_need(type(checks) is dict and set(checks) == set(expected_checks) and
             all(checks[key] is expected for key, expected in expected_checks.items()),
             'exact timeout-only first collector execution checks')
    return dict(first_root=_A2_FIRST_ROOT, first_parent=_A2_PARENT,
        first_controller=_A2_CONTROLLER, first_closed_sha256=hashlib.sha256(closed_blob).hexdigest(),
        first_scope_sha256=hashlib.sha256(scope_blob).hexdigest(),
        first_timeout=_A2_TIMEOUT, first_execution_qualified=False,
        first_aggregate_denominator=None, first_credits=None,
        all_first_case_metadata_null=True, both_first_original_EX_released=True,
        samepurpose_retry=False, new_admission2_purpose_only=True)
# END_ADMISSION2_EXACT_FIRST_ZERO_START_GUARD


def _optional_json(path):
    if not path.exists():
        return None
    value = json.loads(path.read_bytes())
    _a2_need(type(value) is dict, 'local collector metadata must be an object')
    return value


def _first_activity(closed, scope):
    if closed is not None:
        _a2_need(closed.get('root') == _A2_FIRST_ROOT, 'local first CLOSED root')
        meta, cases = closed.get('metadata'), closed.get('cases')
        _a2_need(type(meta) is dict and type(cases) is dict, 'local CLOSED schemas')
        for name in ('ACTUAL_GROUP_ADMISSION.json', 'GROUP_EVAL_START.json',
                     'GROUP_BARRIER_STATUS.json', 'TERMINAL_ROWS.json', 'FINAL.json'):
            _a2_need(name in meta, 'missing first root metadata: ' + name)
            if meta[name] is not None:
                return 'FIRST_PURPOSE_ADMITTED_OR_STARTED'
        for row in cases.values():
            _a2_need(type(row) is dict, 'case metadata schema')
            if any(value is not None for value in row.values()):
                return 'FIRST_CASE_HAS_TASK_SDK_CACHE_RESULT_OR_ERROR'
    if scope is not None:
        _a2_need(scope.get('root') == _A2_FIRST_ROOT, 'local first SCOPE root')
        if scope.get('execution_qualified') is True:
            return 'FIRST_PURPOSE_EXECUTION_QUALIFIED'
        for key in ('aggregate_denominator', 'first_episode_stable_credits',
                    'credited_and_stable_at_end', 'source_IO_group_actual'):
            _a2_need(key in scope, 'missing scope evidence field: ' + key)
            if scope[key] is not None:
                return 'FIRST_PURPOSE_HAS_NATIVE_OR_SOURCE_EVIDENCE'
        rows = scope.get('cases')
        _a2_need(type(rows) is list, 'scope case list')
        for row in rows:
            _a2_need(type(row) is dict, 'scope case object')
            for key in ('actual_parent_wait_qualification', 'source_cache', 'skill',
                        'failed_worker_metadata', 'D0_D7_fresh_audit_before', 'D0_D7_fresh_audit_after'):
                _a2_need(key in row, 'scope case evidence field: ' + key)
                if row[key] is not None:
                    return 'FIRST_CASE_HAS_NATIVE_OR_SOURCE_EVIDENCE'
    return None


def _validate_summary(value):
    _a2_need(type(value) is dict and set(value) ==
             {'epoch', 'canonical_summary', 'schema_gap', 'read_only_summary'}, 'release envelope schema')
    _a2_need(value['read_only_summary'] is True and _a2_number(value['epoch']), 'actual summary read')
    if value['schema_gap'] is not None:
        _a2_need(type(value['schema_gap']) is str and value['canonical_summary'] is None,
                 'schema gap summary envelope')
        return None
    summary = value['canonical_summary']
    _a2_need(type(summary) is dict and set(summary) == {'authority_generation',
        'remaining_training_seconds', 'finite_minimum_remaining_seconds', 'active_owner'},
        'canonical whitelist only')
    _a2_need(type(summary['authority_generation']) is str and
        _a2_number(summary['remaining_training_seconds']) and summary['remaining_training_seconds'] >= 0 and
        _a2_number(summary['finite_minimum_remaining_seconds']) and summary['finite_minimum_remaining_seconds'] >= 0,
        'finite original remaining/reserve fields')
    owner = summary['active_owner']
    if owner is not None:
        _a2_need(type(owner) is dict and set(owner) ==
            {'owner_run_id', 'pid', 'owner_parent_pid', 'started_epoch'} and
            type(owner['owner_run_id']) is str and bool(owner['owner_run_id']) and
            type(owner['pid']) is int and owner['pid'] > 0 and
            type(owner['owner_parent_pid']) is int and owner['owner_parent_pid'] > 0 and
            _a2_number(owner['started_epoch']) and owner['started_epoch'] > 0, 'active owner whitelist')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--closed', default=_A2_W12_CLOSED,
        help='Unchanged original W12 CLOSED_RESULT.json, not the first LOW80 closure')
    args = parser.parse_args()
    D = Path(__file__).resolve().parent
    _a2_need(D.resolve() == Path(_A2_LOCAL_DIR).resolve() and
        Path(args.closed).resolve() == Path(_A2_W12_CLOSED).resolve(), 'fixed local directory/W12 closure')
    mark = D / (PREFIX + 'CONTROLLED_RELEASE_ONCE.json')
    result_path = D / (PREFIX + 'CONTROLLED_RELEASE_RESULT.json')
    current_path = D / (PREFIX + 'RELEASE_WATCH_CURRENT.json')
    _a2_need(not any(path.exists() for path in (mark, result_path, current_path)),
        'unused controlled-release namespace; never replay this purpose')
    for name, pin in DERIVED_CLI_PINS.items():
        blob = (D / name).read_bytes()
        _a2_need(len(blob) == pin['bytes'] and hashlib.sha256(blob).hexdigest() == pin['sha256'],
            'generated CLI source pin changed: ' + name)
    for suffix in ('STAGE_ONCE.json', 'STAGE_RESULT.json', 'GROUP_PLAN_SOURCE.json',
                   'DISPATCH_STARTED_ONCE.json', 'DISPATCH_RESULT.json', 'COLLECTOR_ONCE.json',
                   'CLOSED_RESULT.json', 'SCOPE_RESULT.json', 'QUALITY_RESULTS_V1.md'):
        _a2_need(not (D / (PREFIX + suffix)).exists(), 'Admission2 already touched: ' + suffix)
    start = time.time()
    events, steps = [], []
    with mark.open('x', encoding='utf8') as stream:
        json.dump(dict(epoch=start, first_root=_A2_FIRST_ROOT, first_parent=_A2_PARENT,
            first_controller=_A2_CONTROLLER, input_cli_pins=INPUT_CLI_PINS,
            derived_cli_pins=DERIVED_CLI_PINS, local_wait_cap_seconds=2100,
            local_wait_interval_seconds=15, release_watch_cap_seconds=1800,
            release_watch_interval_seconds=30, first_remote_collector_repeated=False,
            first_parent_extended=False, no_samepurpose_retry=True), stream, indent=2, allow_nan=False)

    def save_current(value):
        temporary = current_path.with_suffix(current_path.suffix + '.partial')
        with temporary.open('w', encoding='utf8') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
        temporary.replace(current_path)

    def finish(status, **extra):
        result = dict(kind='LOW80_ADMISSION2_CONTROLLED_RELEASE_NOT_A_RESOURCE_LEASE',
            epoch=time.time(), wall_seconds=time.time()-start, status=status,
            first_root=_A2_FIRST_ROOT, first_parent=_A2_PARENT, first_controller=_A2_CONTROLLER,
            first_purpose_replayed=False, samepurpose_retries=0, first_parent_extended=False,
            first_remote_collectors_started=0, resource_watch_lock_GPU_model_raw_signal_operations=0,
            canonical_writes=0, canonical_bytes_copied=False, events=events, subprocess_steps=steps)
        result.update(extra)
        with result_path.open('x', encoding='utf8') as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
        print('LOW80_ADMISSION2_RELEASE_RESULT ' + json.dumps(result, allow_nan=False), flush=True)
        return 0

    try:
        deadline = time.monotonic() + 2100
        while True:
            closed = _optional_json(D / (_A2_FIRST_PREFIX + 'CLOSED_RESULT.json'))
            scope = _optional_json(D / (_A2_FIRST_PREFIX + 'SCOPE_RESULT.json'))
            activity = _first_activity(closed, scope)
            if activity is not None:
                return finish('STOP_NO_SECOND_PURPOSE_' + activity, new_tasks_started=False)
            if closed is not None and scope is not None and closed.get('closed') is True:
                first_guard = _a2_zero_start_guard(D, args.closed)
                break
            if time.monotonic() >= deadline:
                return finish('STOP_FIRST_COLLECTOR_NOT_NATURALLY_CLOSED_WITHIN2100',
                    closed_file_present=closed is not None, scope_file_present=scope is not None,
                    new_tasks_started=False)
            time.sleep(min(15, max(0, deadline-time.monotonic())))
    except Exception as exc:
        return finish('STOP_FIRST_ZERO_START_OR_METADATA_GUARD', error_type=type(exc).__name__,
            error=str(exc), new_tasks_started=False)

    events.append(dict(epoch=time.time(), event='EXACT_FIRST_ZERO_START_CLOSED_VALIDATED', **first_guard))
    T = D.parent / 'mod4v1_experts_fulldr_rm70_20261101'
    sys.path.insert(0, str(T))
    connection = None
    release = None
    watch_start = time.time()
    watch_deadline = time.monotonic() + 1800
    gaps = 0
    try:
        from project_connector import connect72
        connection = connect72()
        while time.monotonic() < watch_deadline:
            envelope = summary = None
            gap_type = None
            try:
                timeout = max(0.1, min(30, watch_deadline-time.monotonic()))
                stdin, stdout, stderr = connection.exec_command(
                    shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh') +
                    ' -B -c ' + shlex.quote(RESOURCE_QUERY), timeout=timeout)
                stdin.close()
                text = stdout.read().decode('utf8')
                discarded_stderr = stderr.read()
                rc = stdout.channel.recv_exit_status()
                _a2_need(rc == 0 and not discarded_stderr, 'summary query returned error')
                envelope = json.loads(text)
                summary = _validate_summary(envelope)
                if summary is None:
                    gap_type = envelope['schema_gap']
            except Exception as exc:
                gap_type = type(exc).__name__
            if summary is None:
                gaps += 1
                event = dict(epoch=time.time(), event='RESOURCE_SUMMARY_SCHEMA_GAP',
                    schema_gap_number=gaps, schema_gap_type=gap_type)
            else:
                event = dict(epoch=envelope['epoch'], event='READ_ONLY_CANONICAL_WHITELIST_SUMMARY',
                    canonical_summary=summary, snapshot_not_lease=True)
            events.append(event)
            save_current(event)
            print('LOW80_ADMISSION2_RELEASE_SUMMARY ' + json.dumps(event, allow_nan=False), flush=True)
            if gaps >= 3:
                return finish('STOP_THREE_RESOURCE_READ_SCHEMA_GAPS', new_tasks_started=False,
                    first_zero_start=first_guard)
            if time.monotonic() >= watch_deadline:
                break
            if summary is not None:
                if summary['authority_generation'] != 'MOD4_SINGLE_WRITER72_20261026':
                    return finish('STOP_AUTHORITY_GENERATION_CHANGED', new_tasks_started=False,
                        first_zero_start=first_guard)
                reserve_ok = summary['remaining_training_seconds'] > summary['finite_minimum_remaining_seconds']
                if not reserve_ok:
                    return finish('STOP_ORIGINAL_FINITE_RESERVE_NOT_PASSED', new_tasks_started=False,
                        first_zero_start=first_guard)
                if summary['active_owner'] is None and reserve_ok:
                    release = dict(epoch=envelope['epoch'], observed_at=time.time(),
                        canonical_summary=summary, actual_read_only_release_observed=True,
                        snapshot_not_lease=True, watch_wall_seconds=time.time()-watch_start)
                    events.append(dict(event='ACTUAL_READ_ONLY_RELEASE_OBSERVED', **release))
                    save_current(events[-1])
                    break
            time.sleep(min(30, max(0, watch_deadline-time.monotonic())))
    except Exception as exc:
        return finish('STOP_RESOURCE_OBSERVER_ERROR', error_type=type(exc).__name__,
            new_tasks_started=False, first_zero_start=first_guard)
    finally:
        if connection is not None:
            connection.close()
    if release is None:
        return finish('STOP_READ_ONLY_RELEASE_WATCH_EXPIRED1800', new_tasks_started=False,
            first_zero_start=first_guard, observer_does_not_extend_first_parent=True)

    try:
        repeated_guard = _a2_zero_start_guard(D, args.closed)
        _a2_need(repeated_guard == first_guard, 'first closure changed during release observation')
        commands = (
            ('stage', 'stage_fudan_resume55_low80_holdout_admission2_once.py', ('--closed', args.closed)),
            ('dispatch', 'dispatch_fudan_resume55_low80_holdout_admission2_once.py', ()),
            ('collector', 'collect_fudan_resume55_low80_holdout_admission2_once.py', ()),
        )
        for label, filename, extra in commands:
            completed = subprocess.run([sys.executable, '-B', str(D / filename), *extra],
                cwd=str(D), check=False)
            steps.append(dict(entry=label, filename=filename, returncode=completed.returncode,
                stdio='inherit', actual_wait_returned=True, automatic_retries=0))
            if completed.returncode != 0:
                return finish('STOP_ADMISSION2_' + label.upper() + '_NONZERO_NO_RETRY',
                    new_tasks_started=any(row['entry'] == 'dispatch' for row in steps),
                    first_zero_start=first_guard, read_only_release=release)
    except Exception as exc:
        return finish('STOP_ADMISSION2_SEQUENCE_ERROR_NO_RETRY', error_type=type(exc).__name__,
            new_tasks_started=any(row['entry'] == 'dispatch' for row in steps),
            first_zero_start=first_guard, read_only_release=release)
    return finish('ADMISSION2_ENTRY_SEQUENCE_WAITED', new_tasks_started=True,
        first_zero_start=first_guard, read_only_release=release,
        scope_result_path=str(D / (PREFIX + 'SCOPE_RESULT.json')),
        execution_qualification_deferred_to_original_parent_and_collector=True)


if __name__ == '__main__':
    raise SystemExit(main())
