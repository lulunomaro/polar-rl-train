"""NEW passive-interface contract. No old quality/producer gate is relaxed."""
from pathlib import PurePosixPath
import hashlib
import json

PURPOSE = 'NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_TASK_V1'
PLAN_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_ONLY_PLAN_V1'
FINAL_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_E3_N80_FINAL_V1'
INTEGRATION = 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1'
POLICY_VARIANT = 'EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY'
PRODUCER_ABI = 'PHASE1_TYPED_NATIVE_PRODUCER_ABI_V1'
COMMON_START_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_COMMON_START_V1'
GROUP_FINAL_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_GROUP_FINAL_V1'
INCOMPLETE_KIND = 'PHASE1_TYPED_NATIVE_CAPTURE_INCOMPLETE_V1'
ROLES = ('E3', 'W35', 'CURB_INDEPENDENT113', 'CURB_PROTECTED878', 'SLOPE135', 'SLOPE_INDEPENDENT50', 'E0', 'E2')
REQUESTED = ('E3',)
USD = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
PHYSICS = dict(physics_dt=.0025, control_dt=.02, decimation=8, feedback_hz=100, TGS=[32, 4], closure=.01, mimic=.01)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def relative(value):
    need(type(value) is str and value and ':' not in value and '\\' not in value, 'relative POSIX source alias required')
    need(not value.startswith('/') and all(x not in ('', '.', '..') for x in value.split('/')), 'alias escapes group')
    return value


def canonical_digest(rows):
    return sha(json.dumps(rows, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def validate_task(task):
    need(type(task) is dict, 'task mapping required')
    for key, expected in dict(kind=KIND, purpose=PURPOSE, batch_purpose=PURPOSE, integration=INTEGRATION,
                              policy_variant=POLICY_VARIANT, typed_producer_schema=PRODUCER_ABI, role='E3', requested_roles=['E3'],
                              role_catalog=list(ROLES), num_envs=80, seed=20260928, model_PT_reads=0,
                              synthetic_action=[0., 0., 0., 0., 0., 0.], train=False,
                              quality_evaluation=False, full_clean35='UNKNOWN').items():
        need(type(task.get(key)) is type(expected) and task[key] == expected, 'NEW task field differs: ' + key)
    need(type(task.get('controls')) is int and task['controls'] in (64, 128), 'bounded interface64/128, not160/1600 quality')
    need(task.get('physics') == PHYSICS, 'original physics/DR thresholds remain unchanged')
    need(task.get('asset_SHA') == USD and task.get('contract_SHA') == CONTRACT, 'original plant identity required')
    need(task.get('overall_eight_pass_rate') is None and task.get('comparison') is None, 'no skill/comparison rate')
    need(not any(k in task for k in ('teacher_path', 'source_path', 'checkpoint', 'a1_producer')), 'synthetic path carries no model/producer fallback')
    need(type(task.get('group_id')) is str and task['group_id'] and type(task.get('GPU_UUID')) is str,
         'explicit new group/GPU identity required')
    need(type(task.get('absolute_worker_deadline_epoch')) in (int, float), 'original finite deadline required')
    return task


def validate_plan(plan, source_index):
    need(plan.get('kind') == PLAN_KIND and plan.get('batch_purpose') == PURPOSE
         and plan.get('typed_producer_schema') == PRODUCER_ABI, 'NEW typed plan, not old capture or quality kind')
    need(plan.get('requested_roles') == ['E3'] and plan.get('deferred_roles') == list(ROLES[1:]), 'explicit E3-only membership')
    rows = plan.get('roles')
    need(type(rows) is list and len(rows) == 8 and {x.get('role') for x in rows} == set(ROLES), 'retain complete original eight-role catalog')
    selected = [x for x in rows if x['role'] == 'E3']
    need(selected[0].get('worker') == 'worker_passive_interface_v1.py', 'only NEW capture worker may dispatch')
    files = plan.get('worker_files')
    need(type(files) is list and files, 'complete original worker-file verification inventory required')
    observed = {relative(x['relative']): (x['bytes'], x['SHA']) for x in files}
    need(len(observed) == len(files), 'unique full source aliases required')
    for row in source_index['original17'] + source_index['new_sources'] + source_index['dependency_sources']:
        alias = row['install_relative']
        need(observed.get(alias) == (row['bytes'], row['SHA256']), 'required full SOURCE mapping differs: ' + alias)
    inventory = plan.get('retained_static_inventory')
    need(type(inventory) is dict and inventory.get('kind') == 'COMPLETE_ORIGINAL_STATIC_TREE_REFERENCE_V1',
         'future materializer must retain full original static-tree reference, not an AST subset')
    baseline, installed = inventory.get('baseline'), inventory.get('installed')
    need(type(baseline) is list and baseline and baseline == installed, 'all original runtime/bank/static relative identities must be retained')
    need(inventory.get('SHA256') == canonical_digest(baseline), 'whole static inventory digest differs')
    aliases = [relative(x['relative']) for x in baseline]
    need(len(aliases) == len(set(aliases)), 'static inventory duplicates')
    need(all(any(x.startswith('runtimes/' + r + '/') for x in aliases) for r in ROLES), 'all eight complete runtimes retained')
    need(any(x.startswith('pinned_assets/') for x in aliases) and any(x.startswith('worker_sources/') for x in aliases), 'original assets/workers retained')
    vendor = [x for x in baseline if x['relative'].startswith('supermimic_vendor_v2/')]
    need(len(vendor) == 7 and inventory.get('vendor7_SHA256') == 'ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0',
         'complete original vendor7 inventory required')
    # Equality proves preservation against the supplied baseline, not its provenance.
    # Future root review/materializer must pin that complete baseline independently.
    return selected


def candidate_final(task, *, completed, physics, feedback, delay_calls, boundary, sensor, actuation,
                    coverage, rng_counts, trace, restore, setup, primary_error=False):
    validate_task(task)
    execution = (not primary_error and completed == task['controls'] and physics == completed * 8
                 and feedback == completed * 2 and delay_calls == dict(legs=completed*8, wheels=completed*8)
                 and boundary.get('actions') == completed and boundary.get('original_step_transitions') == completed
                 and boundary.get('pending_original_step') is False and restore.get('ok') is True)
    deficits = list(coverage.get('deficits', []))
    if not coverage.get('natural_terminal_env_events', 0): deficits.append('NO_NATURAL_TERMINAL_ENV_EVENT')
    if not coverage.get('natural_partial_reset_candidate_controls', 0): deficits.append('NO_NATURAL_PARTIAL_RESET_CANDIDATE')
    deficits.extend(['UNTAPPED_ACTOR35_BITWISE_LIVE_VERIFIER_PENDING', 'PER_ROW_EPISODE_PAIR_LIVE_VERIFIER_PENDING',
                     'SDK_PHYSICAL_PARAMETER_READBACK_UNKNOWN', 'PARENT_ACTUAL_WAIT_AND_EX_RELEASE_PENDING'])
    return dict(kind=FINAL_KIND, purpose=PURPOSE, integration=INTEGRATION, role='E3', group_id=task['group_id'],
                 typed_producer_schema=PRODUCER_ABI, typed_pending_control=sensor.get('incomplete_current_control'),
                 science_consistency_status='UNKNOWN_PENDING_TYPED_CONSUMER',
                 metadata_retention_complete=sensor.get('metadata_retention_complete') is True,
                GPU_UUID=task['GPU_UUID'], num_envs=80, controls=completed, requested_controls=task['controls'],
                physics_callbacks=physics, feedback_samples=feedback, delay_calls=delay_calls,
                passed_execution=execution, execution_scope='BOUNDED_SYNTHETIC_INTERFACE_NOT_SKILL',
                policy_variant=POLICY_VARIANT, model_PT_reads=0, training_updates=0, optimizer_updates=0,
                learner_created=False, replay_created=False, teacher_created=False,
                actor35_source='ORIGINAL_RETURNED_POLICY_BUFFER', clean16_only=True, full_clean35='UNKNOWN',
                sensor=sensor, actuation=actuation, boundary=boundary, coverage=coverage,
                rng_counts=rng_counts, bounded_trace=trace, restore=restore, original_setup=setup,
                interface_coverage_status='INCONCLUSIVE_PENDING_LIVE_VERIFIER', inconclusive_reasons=sorted(set(deficits)),
                gate1='UNKNOWN', exact=False, capture_interface_passed=False, paper_ready=False, stage2_GO=False,
                skill_success_rate=None, overall_eight_pass_rate=None, reference_comparison=None)


def validate_preclose(final, task):
    validate_task(task)
    need(final.get('kind') == FINAL_KIND and final.get('purpose') == PURPOSE and final.get('integration') == INTEGRATION,
         'NEW capture FINAL required, not old quality/training FINAL')
    need(final.get('group_id') == task['group_id'] and final.get('role') == task['role'], 'capture FINAL identity differs')
    need(final.get('typed_producer_schema') == PRODUCER_ABI, 'explicit typed producer ABI required')
    sensor = final.get('sensor', {}); ledger = sensor.get('control_ledger', {})
    need(sensor.get('kind') == 'PASSIVE_SENSOR_CAPTURE_V3' and type(ledger) is dict
         and ledger.get('kind') == 'BOUNDED_TYPED_CONTROL_LEDGER_V1'
         and ledger.get('requested_controls') == ledger.get('recorded_controls') == task['controls']
         and ledger.get('run_id') == task['group_id'] + ':E3', 'original complete bounded ledger identity required')
    need(final.get('actuation', {}).get('capture_schema') == 'PHASE1_TYPED_C2_EVENT_WINDOWS_V1',
         'typed C2 event container required; C1 is not this schema')
    need(final.get('passed_execution') is True and type(final.get('controls')) is int and final['controls'] == task['controls'],
         'complete bounded execution required for capture fast-close intent')
    need(final.get('physics_callbacks') == task['controls']*8 and final.get('feedback_samples') == task['controls']*2,
         'actual original callback counts required')
    need(final.get('delay_calls') == dict(legs=task['controls']*8, wheels=task['controls']*8), 'actual original delay callbacks required')
    need(final.get('restore', {}).get('ok') is True and final['restore'].get('order') == ['actuation', 'sensor', 'bridge'],
         'reverse tap restore then original bridge required before env/App close')
    need(all(final.get(k) is False for k in ('capture_interface_passed', 'exact', 'stage2_GO')) and final.get('gate1') == 'UNKNOWN',
         'execution is not Gate1 or exact or training admission')
    need(final.get('model_PT_reads') == 0 and final.get('training_updates') == 0 and final.get('optimizer_updates') == 0,
         'synthetic probe does no model/training work')
    return True
