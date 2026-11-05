"""Stage one original E3 N80/160 group only after a positively learned N20000 closure.
No dispatch, SDK, learner construction, selected-model stat/read/hash, or runtime pruning.
"""
from pathlib import Path, PurePosixPath
import argparse
import ast
import copy
import hashlib
import json
import shlex
import sys
import time

KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
BRANCH = "FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005_LRSCALE001"
EVAL_KIND = "E3_FDN_FROZEN_LOW80_CONFIRM_V1"
BASE = dict(updates=0, policy_optimizer_steps=0, encoder_optimizer_steps=0, transitions_seen=0)
COUNTERS = tuple(BASE)
MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"
SOURCE_4K_SHA = "47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d"
LEARNER_SHA = "8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78"
SOURCE_KIND = "fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005_lrscale001"
OVERLAY_SHA = "a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9"
TASKS = "/home/lc01/Zonglin Li/zonglin2/tasks"
NO = {".pt", ".pth", ".ckpt", ".safetensors", ".onnx", ".pyc", ".pt2", ".pkl", ".pickle"}
EXCLUDED_SOURCE_PATHS = ('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt', '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W3_MAPPING_ADMISSION_20261104_185407_1793789647408789000/roles/E3/production/fudan_seq_full_u000064_c00003110_s0003.pt', '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W5_ADMISSION2_20261104_204218_1793796138143516800/roles/E3/production/fudan_seq20k_full_u000133_wu000069_c00003360_s0003.pt', '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_CONTINUE133_W6_20261104_231058_1793805058620541900/roles/E3/production/fudan_seq20k_full_u000205_wu000072_c00003504_s0003.pt', '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W8_ADMISSION2_20261105_013118_1793813478778262400/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt', '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_HEIGHTGATE_W9_20261105_024613_1793817973423106300/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt', '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LOWSTD005_W11_ADMISSION2_20261105_045304_1793825584020001500/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt')
EXCLUDED_SOURCE_SHAS = ('1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8', '47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d', '8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78', '3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e', '246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2', 'bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2', 'cc41bd5b8787a00be9a5d42fb7c52f8959344c9b58cedf9c24229211b4e55244')
PREFIX = "FDNLOW80_CONFIRM_ADMISSION2_"


def need(condition, message):
    if not condition:
        raise ValueError(message)


# BEGIN_ADMISSION2_EXACT_FIRST_ZERO_START_GUARD
_A2_FIRST_PREFIX = 'FDNLOW80_CONFIRM_'
_A2_FIRST_ROOT = '/home/lc01/Zonglin Li/zonglin2/tasks/FDNLOW80_CONFIRM_THREE_SEED_N80_20261105_074818_1793836098533851800'
_A2_LOCAL_DIR = 'F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104'
_A2_W12_CLOSED = 'F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W12_LRSCHEDULE001_20261105_065807/CLOSED_RESULT.json'
_A2_W12_CLOSED_SHA = '6a2b446951dffc7aad45f7b42d2ef7d98ada33b82a822aaee82019ff79631662'
_A2_PARENT = dict(pid=1641988, linux_start_ticks=157753080)
_A2_CONTROLLER = dict(pid=1641981, linux_start_ticks=157753059)
_A2_PARENT_SOURCE_SHA = 'c9cc481aa7d06d9d8d01db0b51ffb6386c8b6142ee18d50bf4a21bcb3668c9e1'
_A2_CONTROLLER_SOURCE_SHA = 'b9e47b31f6684f1485bbce83f268c08b70f3d798d171c809dd744d5ae74a17d4'
_A2_TIMEOUT = 'Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions'
_A2_MEMBERS = ('E3_LOW80_20260929', 'E3_LOW80_20260930', 'E3_LOW80_20261001')
_A2_SOURCE = dict(
    path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LRSCHEDULE001_W12_20261105_065201_1793832721176405000/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt',
    bytes=146247985,
    sha256='55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7',
    run='MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LRSCHEDULE001_W12_20261105_065201_1793832721176405000',
)
_A2_ROOT_NAMES = (
    'PARENT_STARTED.json', 'ACTUAL_GROUP_ADMISSION.json', 'GROUP_EVAL_START.json',
    'GROUP_BARRIER_STATUS.json', 'BOUNDED_ORIGINAL_RESOURCE_WAIT.json',
    'GROUP_ABORT.json', 'PARENT_ORIGINAL_ERROR.json', 'TERMINAL_ROWS.json',
    'FINAL.json', 'PARENT_EXIT_SCOPE.json',
    'FDNLOW80_CONFIRM_OUTER_DISPATCH.json', 'FDNLOW80_CONFIRM_PARENT_WAITED_ACTUAL.json',
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
             started['kind'] == 'ONEGPU_E3_LOW80_THREE_SEED_CONFIRM_NO_LEARNING',
             'actual first PARENT_STARTED pid1641988')
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
    _a2_need(scope['independent_case_seeds'] == [20260929, 20260930, 20261001] and
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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closed", required=True, help="Actual own CLOSED_RESULT.json after N20000 closure")
    args = parser.parse_args()
    D = Path(__file__).resolve().parent
    _a2_zero_start_guard(D, args.closed)
    closed_path = Path(args.closed)
    need(closed_path.name == "CLOSED_RESULT.json" and closed_path.suffix.lower() == ".json",
         "--closed must name CLOSED_RESULT.json, not a model or raw artifact")
    closed_raw = closed_path.read_bytes()
    closed = json.loads(closed_raw)
    need(closed["closed"] is True, "Actual closed observer evidence required")
    m = closed["metadata"]
    owner = m["OWNER_EXIT_ACTUAL.json"]
    outer = m["OUTER_OWNER_WAIT_ACTUAL.json"]
    need(owner["errors"] == [] and owner["all_own_children_waited"] is True and
         owner["original_cost_settled"] is True and owner["original_leases_released"] is True,
         "Error-free original inner wait, cost settlement and lease release required")
    need(outer["original_owner_reaped"] is True and type(outer["actual_wait_returncode"]) is int and
         outer["actual_wait_returncode"] == 0, "Actual outer RC0/reaped required")
    need(m.get("OWNER_ORIGINAL_ERROR.json") is None, "Original owner error evidence present")
    qualification = m["FDN_PARENT_WAIT_QUALIFICATION.json"]
    need(qualification["qualified"] is True and qualification["error"] is None and
         qualification["actual_child_wait_returncode"] == 0 and qualification["checks"] and
         all(value is True for value in qualification["checks"].values()),
         "Actual positive FDN parent-wait qualification required")
    f = m["FDN_FINAL.json"]
    latest = m["FDN_LATEST_COMPLETE_SAVE.json"]
    intent = m["FDN_APP_FAST_CLOSE_INTENT.json"]
    need(f["kind"] == KIND and f["version"] == 7 and f["branch_kind"] == BRANCH and
         f["role"] == "E3" and f["final"] is True and f["complete_save"] is True and
         f["error"] is None and f["close_errors"] == [], "Qualified version7 LR001 E3 full save required")
    run = f["run"]
    train_root = PurePosixPath(closed["root"])
    need(train_root.is_absolute() and ".." not in train_root.parts and
         train_root.parent == PurePosixPath(TASKS) and train_root.name == run and
         owner["run_id"] == run, "Closed original run/root binding differs")
    need(type(f["parent_pid"]) is int and type(f["worker_pid"]) is int and
         f["parent_pid"] > 0 and f["worker_pid"] > 0 and
         outer["original_owner_pid"] == m["OWNER_PARENT_IDENTITY.json"]["pid"] ==
         qualification["original_owner_pid"] == f["parent_pid"], "Actual original owner PID binding differs")
    cohort = m["COHORT_FINAL.json"]
    need(cohort["run_id"] == run and cohort["errors"] == [] and
         cohort["all_own_children_waited"] is True and cohort["original_cost_settled"] is True,
         "Actual cohort settlement required")
    rows = list(cohort["rows"].values())
    need(len(rows) == 1 and rows[0]["role"] == "E3" and rows[0]["phase"] == "terminal" and
         rows[0]["terminal_all_own_children_waited"] is True and rows[0]["returncode"] == 0 and
         rows[0]["original_error"] is False and rows[0]["final"] == f, "Actual E3 child wait/FINAL differs")
    need(latest == f["latest_complete_save"] == intent["latest_complete_save"] and
         intent["kind"] == KIND and intent["version"] == 7 and intent["branch_kind"] == BRANCH and
         intent["worker_pid"] == f["worker_pid"] and
         f["resource_binding"]["actual_parent_pid"] == f["parent_pid"] and intent["env_close_returned"] is True and
         intent["worker_final_qualified"] is True and intent["error_before_close"] is None and
         intent["close_errors"] == [], "Producer FINAL/latest/close receipt differs")
    for name in ("FDN_NATIVE_ERROR.json", "FDN_SAVE_ERROR.json", "FDN_FINAL_METADATA_ERROR.json", "FDN_APP_CLOSE_ERROR.json"):
        need(m.get(name) is None, "Preserved producer error: " + name)
    need(latest["kind"] == KIND and latest["version"] == 7 and latest["branch_kind"] == BRANCH and
         all(latest[key] is True for key in ("fullstate_required_components_complete", "both_Adam_states_present",
             "model_and_all_required_RNG_present", "new_asset_and_fresh_D0_D7_state_present")) and
         latest["own_new_save_hash_opens"] == 1, "Producer's complete new-save receipt required")
    base, window, counters = f["base_counters"], f["window_counters"], f["counters"]
    need(base == BASE and window == counters and set(counters) == set(BASE) and
         all(type(counters[k]) is int and counters[k] >= 0 for k in COUNTERS),
         "Fresh zero-base, window-only counters required")
    wu = counters["updates"]
    need(0 < wu <= 25 and counters["policy_optimizer_steps"] == counters["encoder_optimizer_steps"] == 20 * wu and
         counters["transitions_seen"] == 48 * 20000 * wu, "Positive actual finite25 N20000 learning required")
    source_receipt = f["source_checkpoint"]
    need(source_receipt == latest["source_checkpoint"] == intent["source_checkpoint"] and
         source_receipt["source_sha256"] == MOTHER_SHA and source_receipt["source_bytes"] == 14715029 and
         source_receipt["source_iter"] == 43090 and source_receipt["physical_byte_opens"] ==
         source_receipt["SHA_calculations"] == source_receipt["CPU_decodes"] == latest["original_mother_reads"] == 1 and
         all(source_receipt[k] is True for k in ("whole_source_root_and_bytes_retained", "source_tensor_versions_unchanged",
             "actor_critic_MLP_only", "source_optimizer_and_DR_state_not_restored", "old_iteration_not_inherited")),
         "Actual single1cd MLP-only warm receipt and retained source required")
    init, update = m["FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json"], m["FDN_NATIVE_UPDATE.json"]
    need(init["version"] == 7 and init["fresh_envs"] == 20000 and init["initial_counters"] == BASE and
         init["source_checkpoint"] == source_receipt and init["history_initialized_from_new_returned_raw35_repeated_five"] is True and
         init["source_global_RNG_environment_DR_history_queues_or_pending_applied"] is False and
         update["rollout_N"] == 20000 and update["rollout_T"] == 48 and update["actual_native_training_update"] is True and
         update["base_counters"] == BASE and update["window_counters"] == update["counters"] == counters,
         "Actual fresh initialized/trained N20000 and T48 required")
    native = f["native_counters"]
    c = native["actual_native_policy_steps"]
    need(type(c) is int and c > 0 and f["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
         native["actual_native_transitions"] == 20000 * c and native["physical_callbacks"] == 8 * c and
         native["feedback_callbacks"] == 2 * c and native["termination_computations"] == c and
         0 <= c - 48 * wu <= 48, "Current N20000 native clocks/unoptimized partial differ")
    for item in (f, latest, intent):
        need(item["source_kind"] == SOURCE_KIND and item["base_counters"] == BASE and item["window_counters"] == counters and
             item["num_envs"] == 20000 and item["inherited_old_iterations"] == 0 and item["full_learner_resume"] is False and
             item["bad_candidate_reads"] == 0 and item["task_runtime_overlay"] == f["task_runtime_overlay"],
             "All fresh producer/save/intent provenance must match")
    need(latest["counters"] == counters and latest["native_counters"] == native and
         latest["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
         f["task_runtime_overlay"]["bytes"] == 12745 and f["task_runtime_overlay"]["sha256"] == OVERLAY_SHA,
         "Latest full state/current native/unchanged fixed timeout8 metadata required")
    for key, expected in dict(initial_std=.05, learning_rate=1e-5, min_learning_rate=1e-7,
                              max_learning_rate=1e-4, encoder_learning_rate=.001).items():
        need(init["learner_config"].get(key) == expected, "Actual fresh LR001 learner initialization differs: " + key)
    summary=f["task_summary"];tracking=summary["tracking_reward_config"];passive=summary["low_rollout_summary"];criteria=summary["low_criterion_summary"]
    need(tracking["height_gate_enabled"] is False and
         set(tracking["terms"]) == {"track_lin_vel","track_lin_vel_tight","track_ang_vel"} and
         all(t["height_gate_installed"] is False for t in tracking["terms"].values()),
         "Actual original positive tracking functions without heightgate required")
    samples=summary["low_envs"]*native["actual_native_policy_steps"]
    need(passive["dtype"] == "float64" and passive["descriptive_only_not_acceptance"] is True and
         passive["samples"] == criteria["samples"] == samples and samples>0 and
         0<=passive["ge023_samples"]<=samples, "Actual pre-reset passive sample clock required")
    criterion_names={"height_ok","upright_ok","speed_ok","angular_ok","wheels_ok","chassis_ok","joint_good"}
    need(criteria["descriptive_only_not_acceptance"] is True and set(criteria["counts"])==criterion_names and
         set(criteria["fractions"])==criterion_names and all(0<=v<=samples for v in criteria["counts"].values()) and
         all(criteria["counts"]["joint_good"]<=v for v in criteria["counts"].values()),
         "Actual seven passive criteria bounded; not acceptance or a new grader")
    selected = dict(path=latest["path"], bytes=latest["bytes"], sha256=latest["sha256"], run=run)
    selected_path = PurePosixPath(selected["path"])
    need(selected_path.parent == train_root / "roles/E3/production" and selected_path.suffix == ".pt" and
         type(selected["bytes"]) is int and selected["bytes"] > 0 and
         isinstance(selected["sha256"], str) and len(selected["sha256"]) == 64 and
         all(ch in "0123456789abcdef" for ch in selected["sha256"]) and
         selected["sha256"] not in EXCLUDED_SOURCE_SHAS and
          str(selected_path) not in EXCLUDED_SOURCE_PATHS and
         selected["path"] != source_receipt["source_path"], "Actual own NEW save path/bytes/SHA required")
    # All closure validation above precedes every mkdir, connector import and upload.
    T = D.parent / "mod4v1_experts_fulldr_rm70_20261101"
    A = D.parent / "mod4v1_current_nine_assessment_20261104"
    marker = D / (PREFIX + "STAGE_ONCE.json")
    plan_path = D / (PREFIX + "GROUP_PLAN_SOURCE.json")
    result_path = D / (PREFIX + "STAGE_RESULT.json")
    need(not any(path.exists() for path in (marker, plan_path, result_path)), "Unused staging namespace required")
    old = json.loads((A / "GROUP_PLAN_SOURCE.json").read_bytes())
    gid = PREFIX + "THREE_SEED_N80_" + time.strftime("%Y%m%d_%H%M%S") + "_" + str(time.time_ns())
    root = TASKS + "/" + gid
    oldroot = TASKS + "/" + old["group_id"]
    need(root not in (str(train_root), oldroot), "A new group root is mandatory")
    plan=copy.deepcopy(old);template=copy.deepcopy(next(r for r in old["roles"]if r["role"]=="E3"));roles=[]
    for seed in (20260929,20260930,20261001):
        role=copy.deepcopy(template);member="E3_LOW80_"+str(seed)
        for key in ("source_iteration","source_Adam17","source_LR"):role.pop(key,None)
        role.update(role=member,expert_role="E3",seed=seed,controls=400,num_envs=80,physics_callbacks=3200,feedback_samples=800,
            worker="worker_sources/parent/worker_fudan_original_n80.py",runtime_origin=template["runtime_root"],
            runtime_root=root+"/runtimes/"+member,asset_dir=root+"/runtimes/"+member+"/runtime/assets",
            source_path=selected["path"],source_bytes=selected["bytes"],source_SHA=selected["sha256"],source_run=run,
            source_training_execution_qualified=True,expected_learner_counters=dict(counters),expected_native_counters=copy.deepcopy(native),
            kind=EVAL_KIND,purpose=EVAL_KIND,policy_input_interface="fudan_sequence_raw35_history5_latent3_clipped_mean_v1",
            evaluation_scope="LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM")
        roles.append(role)
    need(selected["sha256"]=="55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7"and selected["bytes"]==146247985,"Actual retained candidate55afa required")
    pose_raw=(D/"CONTRACT_PARITY_AND_POSE_V2.json").read_bytes();pose=json.loads(pose_raw)
    need(pose["body_count"]==31 and pose["coordinates"]==30 and len(pose["best_candidates"])==5 and pose["same_end_poses"]==0,"Original legal five poses only")
    plan.update(kind="SINGLE_GPU_THREE_INDEPENDENT_LOW80_FROZEN_CONFIRM_PLAN",group_id=gid,roles=roles,
        original_74_score_recomputed=False,reference_native_cohort_executed=False,source_reads_per_independent_case=1,group_source_reads_planned=3,
        low80_pose_spec=dict(bytes=len(pose_raw),sha256=hashlib.sha256(pose_raw).hexdigest()))
    workers = D / "source_fudan_frozen_low80_confirm_v1"
    parents = D / "source_fudan_frozen_low80_parent_v1"
    source_override = {"single_gpu_group_supervisor.py": parents / "single_gpu_group_supervisor.py"}
    for name in ("fudan_task_contract_v2.py", "fudan_eval_parent_wait_contract_v1.py"):
        source_override["worker_sources/parent/" + name] = parents / name
    for name in ("worker_fudan_original_n80.py", "frozen_sequence_mean.py", "fudan_frozen_eval_safe.py",
                 "n80_gpu_capacity.py", "launch_storage_contract.py", "app_close_semantics_v6.py", "resume_runtime_contracts_v3.py", "e3_fudan_task_runtime_v1.py", "pose_cache_runtime_adapter_v4.py", "low80_confirmation_phase_v1.py"):
        source_override["worker_sources/parent/" + name] = workers / name
    need(len(source_override) == 13, "Frozen low80 worker/phase and original parent closure sources required")
    blobs, uploaded = {}, {}
    seen = set()
    for row in plan["worker_files"]:
        need(row["relative"] not in seen, "Duplicate original worker manifest path")
        seen.add(row["relative"])
    for relative, local in source_override.items():
        need(local.suffix.lower() == ".py" and PurePosixPath(relative).suffix == ".py", "Python overlay only")
        raw = local.read_bytes()
        blobs[relative] = raw
        uploaded[relative] = "FDNLOW80_CONFIRM_ADMISSION2_SOURCE_OVERRIDES/" + relative
        rows = [row for row in plan["worker_files"] if row["relative"] == relative]
        need(len(rows) <= 1, "Duplicate override destination")
        row = rows[0] if rows else dict(relative=relative)
        row.update(bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())
        if not rows:
            plan["worker_files"].append(row)
    need(any(row["relative"] == "worker_sources/parent/task_contract.py" for row in plan["worker_files"]),
         "Original task_contract.py dependency must remain in full archive materialization")
    # Literal extraction only: do not import/execute either original stager or prune its runtime closure.
    tree = ast.parse((T / "stage_current_nine_assessment_20261104_once.py").read_bytes())
    node = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign) and
                any(isinstance(target, ast.Name) and target.id == "code" for target in node.targets))
    need(isinstance(node.value, ast.Call) and isinstance(node.value.func.value, ast.Constant),
         "Original materializer literal shape changed")
    materializer = node.value.func.value.value
    anchor = "with zipfile.ZipFile(B/'NONPT_GROUP_SOURCE.zip')as z:"
    need(materializer.count(anchor) == 1, "Original full materializer archive anchor changed")
    additions = "source_override=json.loads((B/'FDNLOW80_CONFIRM_ADMISSION2_SOURCE_OVERRIDE.json').read_bytes())\n"
    additions += "assert set(source_override)==set(" + repr(sorted(source_override)) + ")\n"
    additions += "assert all(v=='FDNLOW80_CONFIRM_ADMISSION2_SOURCE_OVERRIDES/'+k and Path(v).suffix=='.py' and not Path(v).is_absolute() and '..'not in Path(v).parts for k,v in source_override.items())\n"
    materializer = materializer.replace(anchor, additions + anchor, 1)
    needle = "raw=z.read(r['relative']);assert"
    need(materializer.count(needle) == 1, "Original materializer worker read changed")
    materializer = materializer.replace(needle,
        "raw=(B/source_override[r['relative']]).read_bytes() if r['relative'] in source_override else z.read(r['relative']);assert", 1)
    needle = "  if p.is_file():out=asset/"
    need(materializer.count(needle) == 1, "Original pinned-assets materializer anchor changed")
    materializer = materializer.replace(needle, "  if p.suffix.lower()not in NO and p.is_file():out=asset/", 1)
    need(materializer.count("ROOT") == 1, "Original materializer ROOT substitution changed")
    materializer = materializer.replace("ROOT", repr(root))
    materializer += "\nfrom pathlib import Path\nimport hashlib,json\ngroup=Path("+repr(root)+")\npose=(group/'LOW80_POSE_SPEC.json').read_bytes()\nplan=json.loads((group/'GROUP_PLAN.json').read_bytes())\nassert len(pose)==plan['low80_pose_spec']['bytes']and hashlib.sha256(pose).hexdigest()==plan['low80_pose_spec']['sha256']\nfor r in plan['roles']:\n p=Path(r['runtime_root'])/'fudan_task_pose.json';assert not p.exists();p.write_bytes(pose)\n"
    ast.parse(materializer)
    # Non-PT runtime/lib/assets/static-NPZ loops and all original archive rows stay complete.
    with marker.open("x", encoding="utf8") as stream:
        json.dump(dict(epoch=time.time(), root=root, closed_path=str(closed_path),
            closed_metadata_sha256=hashlib.sha256(closed_raw).hexdigest(), source=selected,
            source_saved_cumulative_counters=counters, source_positive_window_counters=window,
            new_evaluation_policy_updates=0, selected_model_stat_read_hash_operations=0), stream, indent=2, allow_nan=False)
    with plan_path.open("x", encoding="utf8") as stream:
        json.dump(plan, stream, indent=2, allow_nan=False)
    sys.path.insert(0, str(T))
    from project_connector import connect72
    result = dict(root=root, GPU_UUID=plan["GPU_UUID"], source=selected, roles=[r["role"]for r in roles], num_envs=80,
                  controls=400, seeds=[20260929,20260930,20261001], source_training_num_envs=20000,
                  new_evaluation_policy_updates=0, selected_model_stat_read_hash_operations=0,
                  runtime_dependency_pruning=False, assessment_dispatched=False)
    c = s = None
    try:
        c = connect72()
        s = c.open_sftp()
        try:
            s.lstat(root)
            raise RuntimeError("Unused remote group root required")
        except FileNotFoundError:
            pass
        s.mkdir(root)
        for relative in ("FDNLOW80_CONFIRM_ADMISSION2_SOURCE_OVERRIDES", "FDNLOW80_CONFIRM_ADMISSION2_SOURCE_OVERRIDES/worker_sources",
                         "FDNLOW80_CONFIRM_ADMISSION2_SOURCE_OVERRIDES/worker_sources/parent"):
            s.mkdir(root + "/" + relative)
        for name, raw in (("GROUP_PLAN.json", json.dumps(plan, indent=2, allow_nan=False).encode()),
                           ("LOW80_POSE_SPEC.json",pose_raw),
                          ("FDNLOW80_CONFIRM_ADMISSION2_SOURCE_OVERRIDE.json", json.dumps(uploaded, indent=2).encode())):
            with s.open(root + "/" + name, "wx") as stream:
                stream.write(raw)
        for relative, raw in blobs.items():
            with s.open(root + "/" + uploaded[relative], "wx") as stream:
                stream.write(raw)
        preamble = "from pathlib import Path;import shutil;shutil.copy2(Path(" + repr(oldroot) + ")/'NONPT_GROUP_SOURCE.zip',Path(" + repr(root) + ")/'NONPT_GROUP_SOURCE.zip')\n"
        i, o, e = c.exec_command(shlex.quote("/home/lc01/Zonglin Li/zonglin2/run-python.sh") +
            " -B -c " + shlex.quote(preamble + materializer), timeout=300)
        i.close()
        stdout, stderr = o.read().decode(), e.read().decode()
        rc = o.channel.recv_exit_status()
        result.update(returncode=rc, stdout=stdout, stderr=stderr)
        need(rc == 0, stderr)
    finally:
        if s is not None:
            s.close()
        if c is not None:
            c.close()
        with result_path.open("x", encoding="utf8") as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
        print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
