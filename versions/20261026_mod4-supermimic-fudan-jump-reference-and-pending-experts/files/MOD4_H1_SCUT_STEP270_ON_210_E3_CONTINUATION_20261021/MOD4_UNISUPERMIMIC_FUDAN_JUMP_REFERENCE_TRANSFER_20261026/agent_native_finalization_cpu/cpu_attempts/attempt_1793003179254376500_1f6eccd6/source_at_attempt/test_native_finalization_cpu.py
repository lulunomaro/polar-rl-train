"""CPU lifecycle fixtures only: no real checkpoint, environment, forward, or step."""
from pathlib import Path
import ast
import contextlib
import copy
import hashlib
import io
import json
import os
import sys
import time
import traceback
import types
import uuid

import torch
import native_finalization_v1 as candidate

HERE = Path(__file__).resolve().parent
SNAPSHOTS = HERE / 'source_snapshots'
ATTEMPT = HERE / 'cpu_attempts' / ('attempt_' + str(time.time_ns()) + '_' + uuid.uuid4().hex[:8])
ATTEMPT.mkdir(parents=True)
RESULTS = []


def extracted(source, cls, fn):
    tree = ast.parse(source.read_text('utf8'))
    body = tree.body if cls is None else next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    return copy.deepcopy(next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == fn))


def execute_function(node, scope, filename):
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(module, str(filename), 'exec'), scope)
    return scope[node.name]


RSL_SAVE = execute_function(extracted(SNAPSHOTS / 'captured_RSL_on_policy_runner.py', 'OnPolicyRunner', 'save'),
                            dict(torch=torch), 'captured_actual_RSL_save')
LOGGER_SAVE = execute_function(extracted(SNAPSHOTS / 'captured_RSL_logger.py', 'Logger', 'save_model'),
                               {}, 'captured_actual_RSL_logger_save_model')
RESCUE_CLASS = execute_function if False else None
rescue_tree = ast.parse((SNAPSHOTS / 'rescue_training.py').read_text('utf8'))
rescue_class_node = next(n for n in rescue_tree.body if isinstance(n, ast.ClassDef) and n.name == 'SavedStop')
rescue_class_scope = {}
exec(compile(ast.Module(body=[rescue_class_node], type_ignores=[]), 'captured_actual_SavedStop', 'exec'), rescue_class_scope)
SavedStop = rescue_class_scope['SavedStop']


class OwnStop(Exception):
    pass


def case_folder(name):
    path = ATTEMPT / name
    path.mkdir()
    return path


def expected_error(call, kind, same=None):
    try:
        call()
    except kind as error:
        if same is not None:
            assert error is same, 'Primary exception object was replaced'
        return error
    raise AssertionError('Expected ' + kind.__name__)


def native_value(iteration=7):
    # Only static CPU tensors/dictionaries. No model or optimizer is constructed.
    return dict(
        wm={'fixture': torch.arange(3.)}, pi={'fixture': torch.ones(2)},
        critic={'fixture': torch.zeros(1)},
        opt_wm={'state': {0: {'step': torch.tensor(3.), 'exp_avg': torch.ones(1)}}},
        opt_pi={'state': {0: {'step': torch.tensor(2.), 'exp_avg': torch.zeros(1)}}},
        opt_v={'state': {0: {'step': torch.tensor(2.), 'exp_avg': torch.ones(1)}}},
        iteration=iteration, wall_time=1.25, sim_steps=24, args={'fixture': True},
        saved_at='synthetic_fixture_only',
    )


def fixture(folder, *, rescue_stop=False, missing_writer=False, pi=2, native=None, augmentation_error=None):
    calls = []
    core = dict(actor_state_dict={'fixture': torch.arange(4.)},
                critic_state_dict={'fixture': torch.ones(3)},
                optimizer_state_dict={'state': {0: {'step': torch.tensor(1.), 'exp_avg': torch.zeros(4)}}})
    logger = types.SimpleNamespace(log=lambda *a, **kw: None)
    logger.save_model = types.MethodType(LOGGER_SAVE, logger)
    if not missing_writer:
        logger.writer = None
    runner = types.SimpleNamespace(alg=types.SimpleNamespace(save=lambda: copy.deepcopy(core)),
                                   current_learning_iteration=829700, logger=logger)
    runner.save = types.MethodType(RSL_SAVE, runner)
    if rescue_stop:
        log = folder / 'synthetic_rescue_log'
        log.mkdir()
        # Actual rescue source, isolated fake os.environ. Host budgets/env are untouched.
        fake_os = types.SimpleNamespace(replace=os.replace, getpid=os.getpid,
                                        environ={'RM_RESCUE_DEADLINE': '-1'})
        rescue_scope = dict(Path=Path, os=fake_os, json=json, time=time, SavedStop=SavedStop)
        install = execute_function(extracted(SNAPSHOTS / 'rescue_training.py', None, 'install'),
                                   rescue_scope, 'captured_actual_rescue_install')
        install(runner, log)
    lower = runner.save
    physical = {key: {'fixture': torch.tensor([index], dtype=torch.int64)}
                for index, key in enumerate(candidate.REQUIRED_ORIGINAL_GROUPS)
                if key not in core}

    def full_original(path, *args, **kwargs):
        calls.append(('original_chain_begin', str(path)))
        lower(path, *args, **kwargs)
        if augmentation_error is not None:
            raise augmentation_error
        state = torch.load(path, map_location='cpu', weights_only=False)
        state.update(copy.deepcopy(physical))
        torch.save(state, path)
        calls.append(('all_original_groups_appended', str(path)))

    learner = types.SimpleNamespace(iteration=7, obs_hist=torch.zeros(2, 10, 128),
                                    _checkpoint=lambda include: copy.deepcopy(native_value() if native is None else native))
    bridge = types.SimpleNamespace(ep_step=torch.tensor([3, 4], dtype=torch.int32), wm_updates=3, pi_updates=pi)
    producer = dict(bridge_source_SHA='fixture_bridge_source', finalization_source_SHA='fixture_module_source',
                    bootstrap_task_source_SHA='fixture_bootstrap_not_a_real_model')
    publisher = candidate.NativeCheckpointPublisher(full_original, learner, bridge, folder, producer)
    return types.SimpleNamespace(publisher=publisher, learner=learner, bridge=bridge,
                                 core=core, physical=physical, calls=calls)


def lifecycle(folder, f, **overrides):
    params = dict(train=lambda: None, stop_types=(OwnStop,), persist_trace=lambda: None,
                  save=f.publisher, out=folder, iteration=lambda: f.learner.iteration,
                  world_updates=lambda: f.bridge.wm_updates, policy_updates=lambda: f.bridge.pi_updates,
                  events=lambda: {'fixture_actual_success': 0})
    params.update(overrides)
    return candidate.run_native_lifecycle(**params)


def boom(error):
    def fail(*args, **kwargs):
        raise error
    return fail


def load_json(path):
    return json.loads(path.read_text('utf8'))


def assert_no_final(folder):
    assert not (folder / 'FINAL.json').exists()


def check_source_ast():
    old = ast.parse((SNAPSHOTS / 'bridge_v5_h1_supermimic_bridge_v1.py').read_text('utf8'))
    new = ast.parse((HERE / 'h1_supermimic_bridge_v1.py').read_text('utf8'))
    oldrun = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    newrun = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    old_prefix = oldrun.body[:next(i for i, n in enumerate(oldrun.body) if ast.unparse(n) == 'failed = False')]
    assert isinstance(newrun.body[-1], ast.Return)
    new_prefix = newrun.body[:-1]
    publisher_assignments = [n for n in new_prefix if isinstance(n, ast.Assign) and
                             any(isinstance(t, ast.Name) and t.id == 'publisher' for t in n.targets)]
    assert len(publisher_assignments) == 1
    new_prefix = [n for n in new_prefix if n is not publisher_assignments[0]]
    old_save = next(n for n in old_prefix if isinstance(n, ast.FunctionDef) and n.name == 'save')
    new_save = next(n for n in new_prefix if isinstance(n, ast.FunctionDef) and n.name == 'save')
    assert ast.unparse(new_save) == 'def save(path, *args, **kwargs):\n    return publisher(path, *args, **kwargs)'
    new_prefix[new_prefix.index(new_save)] = old_save
    assert ast.dump(ast.Module(body=old_prefix, type_ignores=[])) == ast.dump(ast.Module(body=new_prefix, type_ignores=[]))
    added = [n for n in new.body if isinstance(n, ast.ImportFrom) and n.module == 'native_finalization_v1']
    assert len(added) == 1
    old_other = [n for n in old.body if n is not oldrun]
    new_other = [n for n in new.body if n is not newrun and n is not added[0]]
    assert ast.dump(ast.Module(body=old_other, type_ignores=[])) == ast.dump(ast.Module(body=new_other, type_ignores=[]))
    assert [ast.unparse(d) for d in next(n for n in old.body if isinstance(n, ast.ClassDef) and n.name == 'H1Bridge').body
            if isinstance(d, ast.FunctionDef)] == [ast.unparse(d) for d in next(n for n in new.body if isinstance(n, ast.ClassDef) and n.name == 'H1Bridge').body
                                                if isinstance(d, ast.FunctionDef)]
    protected = ('H1GoalMdp all methods', 'H1Bridge all methods and inference_mode decorators',
                 'SuperMimicConfig exact values', 'WM/Pi wrappers and finite checks/counters',
                 'physical source restoration and SDK probe', 'trace construction/install',
                 'startup contract', 'runner.alg.act stub', 'runner.logger.writer None')
    return dict(exact_AST_restriction_passed=True, protected=list(protected),
                allowed_changes=['one lifecycle import', 'publisher construction', 'nested save delegation',
                                 'replace old failed/try/finally terminal block with lifecycle call'])


def check_normal():
    folder = case_folder('normal_completion')
    f = fixture(folder)
    result = lifecycle(folder, f)
    assert result['passed'] is True
    saved = torch.load(folder / 'native_supermimic_H1_final.pt', map_location='cpu', weights_only=False)
    for key in f.core:
        assert key in saved
    assert torch.equal(saved['actor_state_dict']['fixture'], f.core['actor_state_dict']['fixture'])
    assert torch.equal(saved['critic_state_dict']['fixture'], f.core['critic_state_dict']['fixture'])
    assert set(candidate.REQUIRED_NATIVE_GROUPS) <= saved['UniSuperMimic_H1_test'].keys()
    final = load_json(folder / 'FINAL.json')
    assert final['final']['save_token'] == saved['UniSuperMimic_publication']['save_token']
    assert final['final']['SHA'] == candidate.file_sha(folder / 'native_supermimic_H1_final.pt')
    assert final['not_production_H1_or_E2_source'] and final['not_frozen_skill_graduation']
    return dict(passed=True, final_checkpoint_and_manifest_same_new_token=True)


def check_ownstop():
    folder = case_folder('own_stop')
    f = fixture(folder)
    result = lifecycle(folder, f, train=boom(OwnStop('own deadline scenario')))
    assert result['passed'] and result['completion_kind'] == 'own_complete_saved_stop_requested'
    return dict(own_stop_produces_verified_new_final=True)


def check_actual_preupdate_path():
    folder = case_folder('actual_trace_preupdate_path')
    f = fixture(folder)
    trace_tree = ast.parse((SNAPSHOTS / 'h1_production_control_prefix_trace_v1.py').read_text('utf8'))
    cls = next(n for n in trace_tree.body if isinstance(n, ast.ClassDef) and n.name == 'H1ControlPrefixTrace')
    install = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'install')
    act = copy.deepcopy(next(n for n in install.body if isinstance(n, ast.FunctionDef) and n.name == 'act'))
    # Only the actual act wrapper is executed; old_act is a plain callback stub.
    holder = types.SimpleNamespace(folder=folder, rows=[], source_models=[], observed=None, total=0,
                                   runner=types.SimpleNamespace(save=f.publisher))
    scope = dict(self=holder, torch=torch, H=candidate.file_sha, old_act=lambda *a, **kw: None)
    fn = execute_function(act, scope, 'captured_actual_trace_act')
    assert fn({'policy': torch.zeros(2, 35), 'critic': torch.zeros(2, 38)}) is None
    expected = folder / 'preupdate_fullsource_0.pt'
    assert expected.exists() and not (folder / 'preupdate_fullsource_0.pt.partial').exists()
    assert holder.source_models[0]['path'] == str(expected)
    assert holder.source_models[0]['before_control'] == 0 and holder.source_models[0]['no_optimizer_call']
    value = torch.load(expected, map_location='cpu', weights_only=False)
    assert value['UniSuperMimic_publication']['native_iteration'] == 7
    return dict(actual_trace_wrapper_success_paths_unchanged=True, no_model_forward_or_optimizer_call=True)


def check_wrapped_stop():
    folder = case_folder('actual_rescue_wrapped_save_stop')
    f = fixture(folder, rescue_stop=True)
    error = expected_error(lambda: lifecycle(folder, f), SavedStop)
    assert_no_final(folder)
    assert not (folder / 'native_supermimic_H1_final.pt').exists()
    stages = list(folder.glob('.*.native_*.partial'))
    assert len(stages) == 1
    value = torch.load(stages[0], map_location='cpu', weights_only=False)
    assert 'actor_state_dict' in value and 'H1_step270_task_state' not in value and 'UniSuperMimic_H1_test' not in value
    receipt = load_json(folder / 'NATIVE_FULLSAVE_ORIGINAL_ERROR.json')
    assert receipt['primary_error']['exception_type'].endswith('SavedStop')
    failed = load_json(folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json')
    assert failed['passed'] is False and failed['final'] is None
    return dict(actual_rescue_source_stop_reproduced_as_synthetic_scenario=True,
                incomplete_stage_retained_and_never_promoted=True, error=str(error),
                actual82Q_cause_claimed=False)


def check_trace_failure():
    folder = case_folder('trace_persistence_failure')
    f = fixture(folder)
    error = OSError('synthetic trace persistence failure')
    expected_error(lambda: lifecycle(folder, f, persist_trace=boom(error)), OSError, error)
    assert_no_final(folder)
    failed = load_json(folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json')
    assert failed['passed'] is False and failed['trace_persisted'] is False
    assert failed['final']['verified_new_publication'] and (folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE.pt').exists()
    assert any(kind == 'all_original_groups_appended' for kind, _ in f.calls)
    return dict(trace_failure_does_not_skip_new_save=True, trace_error_reraised_unchanged=True)


def check_primary_secondary():
    folder = case_folder('primary_learning_secondary_save_failure')
    secondary = OSError('synthetic original fullsave augmentation failure')
    f = fixture(folder, augmentation_error=secondary)
    primary = ValueError('synthetic original learning failure')
    expected_error(lambda: lifecycle(folder, f, train=boom(primary)), ValueError, primary)
    assert_no_final(folder)
    record = load_json(folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json')
    assert record['primary_error']['error'] == str(primary)
    assert record['secondary_errors'][0]['error'] == str(secondary)
    assert record['passed'] is False and record['final'] is None
    return dict(primary_learning_exception_identity_and_traceback_preserved=True,
                secondary_save_failure_separately_recorded=True)


def check_all_secondary_failures():
    folder = case_folder('primary_plus_trace_save_manifest_failures')
    f = fixture(folder, augmentation_error=OSError('secondary save'))
    primary = RuntimeError('primary learning')
    expected_error(lambda: lifecycle(folder, f, train=boom(primary),
                                    persist_trace=boom(OSError('secondary trace')),
                                    write_manifest=boom(OSError('secondary manifest'))), RuntimeError, primary)
    record = load_json(folder / 'NATIVE_FINALIZATION_FAILED_ACTUAL.json')
    assert record['primary_error']['error'] == 'primary learning'
    assert [r['error'] for r in record['secondary_errors']] == ['secondary trace', 'secondary save', 'secondary manifest']
    assert record['passed'] is False and not record['manifest_committed']
    assert_no_final(folder)
    return dict(all_chronological_errors_retained=True, original_exception_preserved=True)


def check_primary_with_saved_partial():
    folder = case_folder('learning_failure_successful_full_partial_save')
    f = fixture(folder)
    primary = RuntimeError('synthetic learning failure with save success')
    expected_error(lambda: lifecycle(folder, f, train=boom(primary)), RuntimeError, primary)
    value = load_json(folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json')
    assert not value['passed'] and value['final']['verified_new_publication']
    assert_no_final(folder)
    return dict(full_verified_failed_partial_retained=True, learning_failure_never_passed=True)


def check_native_missing_optimizer():
    folder = case_folder('native_missing_optimizer_rejected')
    native = native_value()
    del native['opt_v']
    f = fixture(folder, native=native)
    error = expected_error(lambda: lifecycle(folder, f), candidate.PublicationError)
    assert 'Incomplete native' in str(error)
    assert_no_final(folder)
    assert list(folder.glob('.*.native_*.partial'))
    return dict(incomplete_native_optimizer_group_rejected=True, error=str(error))


def check_original_group_missing():
    folder = case_folder('original_full_chain_missing_group_rejected')
    f = fixture(folder)
    del f.physical['chassis_PD_state']
    error = expected_error(lambda: lifecycle(folder, f), candidate.PublicationError)
    assert 'chassis_PD_state' in str(error)
    assert_no_final(folder)
    return dict(missing_physical_chain_group_rejected=True, error=str(error))


def check_nonfinite():
    folder = case_folder('nonfinite_native_rejected')
    native = native_value()
    native['pi']['fixture'][0] = float('nan')
    f = fixture(folder, native=native)
    error = expected_error(lambda: lifecycle(folder, f), candidate.PublicationError)
    assert 'Nonfinite tensor' in str(error)
    assert_no_final(folder)
    assert not (folder / 'native_supermimic_H1_final.pt').exists()
    return dict(nonfinite_integrity_guard_preserved=True, error=str(error))


def check_manifest_failure():
    folder = case_folder('manifest_failure_after_complete_checkpoint')
    f = fixture(folder)
    primary = OSError('synthetic FINAL publication failure')
    expected_error(lambda: lifecycle(folder, f, write_manifest=boom(primary)), OSError, primary)
    assert_no_final(folder)
    assert (folder / 'native_supermimic_H1_final.pt').exists()
    record = load_json(folder / 'NATIVE_FINALIZATION_FAILED_ACTUAL.json')
    assert record['final']['verified_new_publication'] and record['passed'] is False
    assert record['checkpoint_retained_but_not_promoted_without_manifest']
    return dict(complete_checkpoint_retained_but_manifest_failure_explicit=True)


def check_stale_destination():
    folder = case_folder('stale_destination_not_read_or_promoted')
    f = fixture(folder)
    stale = folder / 'native_supermimic_H1_final.pt'
    stale.write_bytes(b'NOT_A_CHECKPOINT_STALE_SYNTHETIC_FIXTURE')
    error = expected_error(lambda: lifecycle(folder, f), FileExistsError)
    assert not f.calls, 'Old save was called despite stale destination'
    assert stale.read_bytes() == b'NOT_A_CHECKPOINT_STALE_SYNTHETIC_FIXTURE'
    assert load_json(folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json')['final'] is None
    assert_no_final(folder)
    return dict(stale_destination_not_loaded_hashed_or_promoted=True, error=str(error))


def check_receiptless_save():
    folder = case_folder('receiptless_save_rejected')
    f = fixture(folder)
    error = expected_error(lambda: lifecycle(folder, f, save=lambda path: None), candidate.PublicationError)
    assert 'no verified receipt' in str(error)
    assert_no_final(folder)
    return dict(rc0_or_unverified_save_return_is_not_success=True, error=str(error))


def check_zero_policy_updates():
    folder = case_folder('zero_policy_updates_not_passed')
    f = fixture(folder, pi=0)
    result = lifecycle(folder, f)
    assert result['passed'] is False and result['final']['verified_new_publication']
    assert load_json(folder / 'FINAL.json')['passed'] is False
    return dict(normal_return_not_success_without_policy_update=True)


def check_actual_logger_missing_writer():
    folder = case_folder('actual_RSL_missing_writer_negative')
    f = fixture(folder, missing_writer=True)
    error = expected_error(lambda: lifecycle(folder, f), AttributeError)
    assert 'writer' in str(error)
    assert_no_final(folder)
    assert list(folder.glob('.*.native_*.partial'))
    return dict(actual_RSL_missing_writer_synthetic_negative_retained=True, error=str(error))


def check_event_snapshot_failure():
    folder = case_folder('lifetime_event_snapshot_failure')
    f = fixture(folder)
    primary = RuntimeError('synthetic lifetime snapshot failure')
    expected_error(lambda: lifecycle(folder, f, events=boom(primary)), RuntimeError, primary)
    assert_no_final(folder)
    value = load_json(folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json')
    assert value['passed'] is False and value['final']['verified_new_publication']
    return dict(event_snapshot_failure_cannot_hide_behind_complete_file=True)


def check_receipt_storage_failure():
    folder = case_folder('primary_preserved_when_error_receipts_cannot_write')
    f = fixture(folder, augmentation_error=OSError('secondary save'))
    primary = RuntimeError('primary learning retained through receipt failure')
    old = candidate.atomic_json
    diagnostic = io.StringIO()
    try:
        candidate.atomic_json = boom(OSError('synthetic all diagnostic storage unavailable'))
        with contextlib.redirect_stderr(diagnostic):
            expected_error(lambda: lifecycle(folder, f, train=boom(primary)), RuntimeError, primary)
    finally:
        candidate.atomic_json = old
    text = diagnostic.getvalue()
    (folder / 'stderr_fallback_captured.txt').write_text(text, 'utf8')
    assert 'NATIVE_LIFECYCLE_UNPERSISTED_ERROR' in text and 'fallback_receipt_write' in text
    value = load_json(folder / 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json')
    assert not value['passed'] and any(not r['durable'] for r in value['error_receipts'])
    return dict(original_primary_preserved_when_receipt_storage_fails=True,
                unpersisted_receipts_explicitly_identified_and_stderr_retained=True)


def check_manifest_not_overwritten():
    folder = case_folder('existing_manifest_not_overwritten')
    path = folder / 'existing_manifest.json'
    path.write_text('{"passed":false,"old":true}', 'utf8')
    old = path.read_bytes()
    expected_error(lambda: candidate.atomic_json(path, {'passed': True}), FileExistsError)
    assert path.read_bytes() == old
    return dict(old_false_report_never_overwritten=True)


def main():
    torch.set_num_threads(1)
    assert not torch.cuda.is_initialized()
    tests = [check_source_ast, check_normal, check_ownstop, check_actual_preupdate_path,
             check_wrapped_stop, check_trace_failure, check_primary_secondary,
             check_all_secondary_failures, check_primary_with_saved_partial,
             check_native_missing_optimizer, check_original_group_missing, check_nonfinite,
             check_manifest_failure, check_stale_destination, check_receiptless_save,
             check_zero_policy_updates, check_actual_logger_missing_writer,
             check_event_snapshot_failure, check_receipt_storage_failure,
             check_manifest_not_overwritten]
    with (ATTEMPT / 'cpu_stdout_stderr.txt').open('x', encoding='utf8') as log:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            for test in tests:
                start = time.time()
                try:
                    details = test()
                    RESULTS.append(dict(name=test.__name__, passed=True, details=details,
                                        elapsed_s=time.time() - start))
                except BaseException as error:
                    RESULTS.append(dict(name=test.__name__, passed=False,
                                        error=candidate.error_record('CPU_fixture_test', error),
                                        elapsed_s=time.time() - start))
    assert not torch.cuda.is_initialized()
    artifacts = [dict(path=str(p), bytes=p.stat().st_size, fixture_only=True)
                 for p in ATTEMPT.rglob('*') if p.is_file()]
    result = dict(
        attempt_id=ATTEMPT.name, epoch=time.time(), passed=all(r['passed'] for r in RESULTS),
        tests=RESULTS, count=len(RESULTS), passed_count=sum(r['passed'] for r in RESULTS),
        Python=sys.executable, torch_version=torch.__version__, CPU_only=True,
        CUDA_initialized=False, real_model_or_pilot_checkpoint_content_read=False,
        real_environment_or_actor_forward_or_optimizer_step_or_training=False,
        network_or_SSH_remote_or_budget_ledger_locks_or_Git_write=False,
        candidate_uninstalled=True, actual82Q_cause='UNPROVEN',
        scope='Only new tiny synthetic CPU tensor/bytes fixtures and captured local source extraction',
        actual_sources_executed=['captured actual RSL save', 'captured actual logger save_model',
                                 'captured actual rescue install in isolated fake os.environ scenario',
                                 'captured actual trace preupdate act with plain callback stub'],
        fixture_physical_groups='Synthetic dictionaries; original physical runtime validations not executed',
        artifacts=artifacts,
        source_SHA={name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                    for name in ('native_finalization_v1.py', 'h1_supermimic_bridge_v1.py',
                                 'test_native_finalization_cpu.py')},
        Git_status='PENDING_ROOT_PHASE_ARCHIVE_NO_AGENT_GIT_WRITE',
    )
    report = ATTEMPT / 'CPU_LIFECYCLE_TESTS_ACTUAL.json'
    with report.open('x', encoding='utf8') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(dict(passed=result['passed'], tests=result['count'], passed_count=result['passed_count'], report=str(report))))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
