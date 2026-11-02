"""NEW SOURCE ONLY: pinned fast-App-close intent, never a new shutdown policy.

Stdlib only.  No automatic installation, SDK import, checkpoint byte read,
subprocess, accounting, lock, clock-limit or physics operation occurs at import.
The original close is still invoked with zero arguments and the original mode.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback
import types

import resume_runtime_contracts_v3 as _base

INTENT_NAME = 'APP_FAST_CLOSE_INTENT_V5.json'
INTENT_KIND = 'PINNED_ORIGINAL_APP_FAST_CLOSE_INTENT_V5'
BOUNDED_EVENTS_KIND = 'POSE_CACHE_RUNTIME_ADAPTER_BOUNDED_EVENTS_V5'
_APP_CLOSED = 'APP_CLOSED.json'
_LIFECYCLE = 'WORKER_LIFECYCLE_COMPLETE_V3.json'


class AppCloseEvidenceError(ValueError):
    """A witness is absent, unknown or inconsistent; no success substitution."""


@dataclass(frozen=True)
class _AppPin:
    module: str
    class_name: str
    source_bytes: int
    source_SHA256: str
    close_firstlineno: int


# Not a public override. Tests patch this PRIVATE policy to their OWN fake file;
# such a receipt is explicitly not a native SimulationApp binding receipt.
_APP_PIN = _AppPin(
    'isaacsim.simulation_app.simulation_app', 'SimulationApp', 48933,
    '6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903', 848,
)


def _need(value, message):
    if not value:
        raise AppCloseEvidenceError(message)


def _class_id(cls):
    return cls.__module__ + '.' + cls.__qualname__


def _plain_field(obj, name):
    """Only plain instance fields; do not evaluate any application descriptor."""
    try:
        namespace = object.__getattribute__(obj, '__dict__')
    except (AttributeError, TypeError) as exc:
        raise AppCloseEvidenceError('plain application instance fields missing') from exc
    _need(type(namespace) is dict and name in namespace, 'plain field missing: ' + name)
    value = namespace[name]
    _need(inspect.getattr_static(obj, name) is value, 'field shadowed by descriptor: ' + name)
    return value


def _pin_original_app_close(application):
    """Inspect only Python identity/config/source; never query the running SDK."""
    pin = _APP_PIN
    cls = type(application)
    _need(cls.__module__ == pin.module and cls.__qualname__ == pin.class_name,
          'actual application exact class differs')
    mro = cls.__mro__
    _need(mro == (cls, object), 'actual application MRO differs')
    definition = cls.__dict__.get('close')
    _need(isinstance(definition, types.FunctionType), 'original close is not a class Python function')
    bound = getattr(application, 'close')
    _need(isinstance(bound, types.MethodType) and bound.__self__ is application
          and bound.__func__ is definition, 'actual bound close self/function differs')
    _need(definition.__module__ == pin.module
          and definition.__qualname__ == pin.class_name + '.close', 'close owner/qualname differs')
    module = sys.modules.get(pin.module)
    _need(module is not None and getattr(module, pin.class_name, None) is cls,
          'actual module/class identity differs')
    module_file = vars(module).get('__file__')
    _need(type(module_file) is str and bool(module_file), 'actual close module file missing')
    source = Path(module_file).resolve(strict=True)
    _need(source.suffix == '.py', 'actual close is not a Python source file')
    try:
        class_file = Path(inspect.getsourcefile(cls)).resolve(strict=True)
    except (OSError, TypeError) as exc:
        raise AppCloseEvidenceError('actual application class source missing') from exc
    _need(class_file == source and Path(definition.__code__.co_filename).resolve(strict=True) == source,
          'class/module/code source paths differ')
    raw = source.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    _need(len(raw) == pin.source_bytes and actual_sha == pin.source_SHA256,
          'actual original application source bytes/SHA differ')
    tree = ast.parse(raw, filename=str(source))
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == pin.class_name]
    _need(len(classes) == 1, 'original application class AST differs')
    methods = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name == 'close']
    _need(len(methods) == 1 and not methods[0].decorator_list
          and methods[0].lineno == definition.__code__.co_firstlineno == pin.close_firstlineno,
          'actual original close AST/code line differs')
    config = _plain_field(application, 'config')
    _need(type(config) is dict, 'application config is not an exact plain dict')
    mode = config.get('fast_shutdown')
    _need(type(mode) is bool, 'actual plain fast_shutdown mode is unknown')
    receipt = dict(
        kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5', actual_class=_class_id(cls),
        actual_MRO=[_class_id(c) for c in mro], close_owner=_class_id(cls),
        close_module=pin.module, close_qualname=definition.__qualname__,
        source_file=str(source), module_file=str(source), code_filename=str(source),
        source_bytes=len(raw), source_SHA256=actual_sha, close_firstlineno=pin.close_firstlineno,
        exact_class_verified=True, method_self_is_application=True,
        method_function_is_MRO_definition=True, fast_shutdown=mode,
        no_extra_SDK_getters=True,
    )
    return receipt


def _validate_binding_receipt(value):
    pin = _APP_PIN
    _need(type(value) is dict, 'pinned close binding receipt missing')
    class_id = pin.module + '.' + pin.class_name
    expected = dict(
        kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5', actual_class=class_id,
        actual_MRO=[class_id, 'builtins.object'], close_owner=class_id,
        close_module=pin.module, close_qualname=pin.class_name + '.close',
        source_bytes=pin.source_bytes, source_SHA256=pin.source_SHA256,
        close_firstlineno=pin.close_firstlineno, exact_class_verified=True,
        method_self_is_application=True, method_function_is_MRO_definition=True,
        fast_shutdown=True, no_extra_SDK_getters=True,
    )
    for key, item in expected.items():
        _need(type(value.get(key)) is type(item) and value.get(key) == item,
              'pinned fast close receipt differs: ' + key)
    paths = [value.get(k) for k in ('source_file', 'module_file', 'code_filename')]
    _need(all(type(p) is str and p for p in paths) and paths[0] == paths[1] == paths[2],
          'pinned close receipt source paths differ')
    _need(Path(paths[0]).is_absolute() and Path(paths[0]).suffix == '.py',
          'pinned close receipt source path is not absolute Python source')


def _read_object(path):
    raw = Path(path).read_bytes()
    value = json.loads(raw)
    _need(type(value) is dict, 'receipt is not a JSON object: ' + Path(path).name)
    return value, raw


def _error_evidence(job):
    """Own small terminal sidefiles only; include new/secondary errors, no raw logs."""
    job = Path(job)
    errors = set()
    try:
        for directory in (job, job / 'production'):
            for pattern in ('WORKER_ERROR*.json', 'WORKER_PRESTART_ERROR*.json',
                            'APP_CLOSE_*ERROR*V5.json'):
                for path in directory.glob(pattern):
                    errors.add(str(path))
    except BaseException as exc:
        errors.add('error_sidefile_presence_unknown:' + type(exc).__name__)
    return sorted(errors)


def _checkpoint_identity(final):
    checkpoint = final.get('checkpoint')
    _need(type(checkpoint) is dict, 'complete checkpoint receipt missing')
    return {key: checkpoint.get(key) for key in (
        'path', 'bytes', 'SHA', 'counts', 'full_new_model_critic_aux_optimizers_replay_RNG_hist_saved')}


def _validate_final_for_intent(final, task, job):
    """A pre-close witness check, NOT an actual-wait gate or checkpoint decode.

    The owner subsequently executes ALL original V4 FINAL/error/full-save checks.
    This duplicated precondition never replaces or filters those owner checks.
    """
    _need(final.get('kind') == _base.FINAL_KIND and final.get('passed_execution') is True,
          'successful original-schema FINAL missing before app close')
    for key in ('role', 'role_key', 'run_id'):
        _need(type(task.get(key)) is str and bool(task[key]) and final.get(key) == task[key],
              'FINAL/task identity differs: ' + key)
    variant = _base.validate_worker_variant(task)
    _need(final.get('actor_view') == variant['actor_view']
          and final.get('algorithm_family') == variant['algorithm_family'], 'FINAL actor family differs')
    counts = _base.validate_count_snapshot(final.get('counts'))
    _need(final.get('actual_BPTT_policy_steps') == counts['pi_bptt_optimizer_steps'], 'FINAL BPTT count differs')
    checkpoint = _checkpoint_identity(final)
    _need(_base._sha(checkpoint['SHA']) and type(checkpoint['bytes']) is int and checkpoint['bytes'] > 0,
          'checkpoint byte/SHA receipt differs')
    _need(checkpoint['counts'] == counts
          and checkpoint['full_new_model_critic_aux_optimizers_replay_RNG_hist_saved'] is True
          and final.get('teacher_unchanged') is True, 'full checkpoint/counters/teacher receipt differs')
    _need(type(checkpoint['path']) is str and Path(checkpoint['path']).resolve().is_relative_to(
        (Path(job) / 'production' / 'checkpoints').resolve()), 'checkpoint is not own new production output')
    return counts, checkpoint


def _publish_fsynced_intent(job, value):
    """Publish complete JSON only AFTER its temp-file flush+fsync succeeds.

    There is one worker/writer per new job. Existing intent is a fail-closed
    collision, never an overwritten earlier witness. No checkpoint is opened.
    """
    output = Path(job).resolve(strict=True) / 'production'
    _need(output.is_dir(), 'own production output missing')
    target = output / INTENT_NAME
    temporary = output / (INTENT_NAME + '.unpublished')
    _need(target.resolve().parent == temporary.resolve().parent == output.resolve(), 'intent path escaped own output')
    _need(not target.exists() and not temporary.exists(), 'intent output already exists')
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')
    with temporary.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    # Resolved source/target are verified above, and this is only own new metadata.
    os.replace(temporary, target)


def _durable_close_error(job, task, phase, error):
    try:
        return _base.preserve_worker_error(Path(job) / 'production', role=task.get('role', 'UNKNOWN'),
                                           error=error, phase=phase)
    except BaseException as exc:
        # The missing witness/FINAL or new error sidefile still blocks the owner.
        return dict(persisted=False, persistence_error=type(exc).__name__)


def close_original_resources(bridge, env, namespace, emit, *, job_root, task, primary_error=None):
    """Same original close calls/order; narrow fast-close intent before App.close.

    A true process exit never returns here. A Python SystemExit, including code
    zero, IS caught/preserved as an error and is NOT fast-nonreturn evidence.
    No flag, exit_code argument, config entry, _exiting field or SDK state is set.
    """
    job = Path(job_root).resolve(strict=True)
    records, failures = [], []

    def remember(phase, error):
        failures.append(dict(phase=phase, error=error))
        _durable_close_error(job, task, phase, error)

    def close_before_app(name, obj, before=None, after=None):
        if obj is None:
            return
        if before:
            try:
                emit(before, dict(epoch=time.time(), calling_original_close=True))
            except BaseException:
                remember(before + '_sidefile', traceback.format_exc())
        try:
            obj.close()
        except BaseException:
            records.append(dict(resource=name, returned=False))
            remember(name, traceback.format_exc())
        else:
            records.append(dict(resource=name, returned=True))
            if after:
                try:
                    emit(after, dict(epoch=time.time(), closed=True))
                except BaseException:
                    remember(after + '_sidefile', traceback.format_exc())

    close_before_app('bridge', bridge)
    close_before_app('env', env, 'APP_CLOSING.json', 'ENV_CLOSED.json')
    application = None if namespace is None else namespace.get('app')
    if namespace is not None and application is None:
        remember('app_handle', 'constructed namespace has no original app handle')
    binding = None
    if application is not None:
        try:
            binding = _pin_original_app_close(application)
        except BaseException:
            remember('app_close_binding_preflight_v5', traceback.format_exc())
        if primary_error is not None:
            _durable_close_error(job, task, 'primary_error_before_app_close_v5', str(primary_error))
        # False is a known non-fast mode: preserve the original normal-return
        # route, with NO intent. Unknown mode/source already recorded an error.
        eligible = (binding is not None and binding['fast_shutdown'] is True
                    and primary_error is None and not failures
                    and records == [dict(resource='bridge', returned=True), dict(resource='env', returned=True)]
                    and not _error_evidence(job))
        if eligible:
            try:
                final, final_raw = _read_object(job / 'production' / 'FINAL.json')
                counts, checkpoint = _validate_final_for_intent(final, task, job)
                intent = dict(
                    kind=INTENT_KIND, role=task['role'], role_key=task['role_key'], run_id=task['run_id'],
                    job_root=str(job), original_app_close_arguments=[], original_fast_shutdown_unchanged=True,
                    expected_process_nonreturn=True, app_close_returned=None,
                    binding=binding, prior_original_closes=list(records),
                    primary_error_absent=True, error_sidefiles_absent=True, prior_close_errors_absent=True,
                    final_bytes=len(final_raw), final_SHA256=hashlib.sha256(final_raw).hexdigest(),
                    counts=counts, checkpoint=checkpoint, checkpoint_bytes_opened=0,
                    publication='TEMP_FLUSH_FSYNC_THEN_ATOMIC_RENAME_BEFORE_ORIGINAL_APP_CLOSE',
                )
                _publish_fsynced_intent(job, intent)
            except BaseException:
                remember('app_close_intent_preflight_or_persistence_v5', traceback.format_exc())
        # The original zero-argument call is immediately after intent publishing;
        # no SDK query, callback, observation, reset, step or mode change intervenes.
        try:
            application.close()
        except BaseException:
            records.append(dict(resource='app', returned=False))
            remember('app', traceback.format_exc())
        else:
            records.append(dict(resource='app', returned=True))
            try:
                emit(_APP_CLOSED, dict(epoch=time.time(), closed=True))
            except BaseException:
                remember(_APP_CLOSED + '_sidefile', traceback.format_exc())
    return dict(records=records, errors=failures,
                all_original_close_calls_returned=not failures,
                app_close_binding=binding, original_fast_shutdown_setting_changed=False)


def _validate_intent(intent, final, final_raw, job, entry, run_id):
    _need(type(intent) is dict and intent.get('kind') == INTENT_KIND, 'fast close intent kind differs')
    for key, value in (('role', entry['role']), ('role_key', entry['role_key']), ('run_id', run_id),
                       ('job_root', str(Path(job).resolve()))):
        _need(type(intent.get(key)) is str and intent[key] == value, 'fast close intent identity differs: ' + key)
    _validate_binding_receipt(intent.get('binding'))
    for key in ('original_fast_shutdown_unchanged', 'expected_process_nonreturn', 'primary_error_absent',
                'error_sidefiles_absent', 'prior_close_errors_absent'):
        _need(intent.get(key) is True, 'fast close intent declaration missing: ' + key)
    _need(intent.get('original_app_close_arguments') == [] and intent.get('app_close_returned') is None,
          'fast close intent changed original call or invented a return')
    prior = intent.get('prior_original_closes')
    _need(type(prior) is list and len(prior) == 2
          and all(type(row) is dict and set(row) == {'resource', 'returned'}
                  and type(row['resource']) is str and row['resource'] == name and row['returned'] is True
                  for row, name in zip(prior, ('bridge', 'env'))),
          'prior original bridge/env closes did not both explicitly return')
    _need(type(intent.get('final_bytes')) is int and intent['final_bytes'] == len(final_raw)
          and intent.get('final_SHA256') == hashlib.sha256(final_raw).hexdigest(),
          'FINAL bytes/SHA changed after close intent')
    counts = _base.validate_count_snapshot(intent.get('counts'))
    checkpoint = intent.get('checkpoint')
    _need(type(checkpoint) is dict and type(checkpoint.get('bytes')) is int
          and checkpoint['bytes'] > 0 and type(checkpoint.get('path')) is str
          and _base._sha(checkpoint.get('SHA'))
          and checkpoint.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved') is True,
          'fast close intent checkpoint metadata types/full-save flag differ')
    checkpoint_counts = _base.validate_count_snapshot(checkpoint.get('counts'))
    _need(counts == final.get('counts') and checkpoint_counts == counts
          and checkpoint == _checkpoint_identity(final),
          'fast close intent counters/checkpoint identity differ')
    _need(type(intent.get('checkpoint_bytes_opened')) is int and intent['checkpoint_bytes_opened'] == 0,
          'close intent unexpectedly opened checkpoint bytes')
    _need(intent.get('publication') == 'TEMP_FLUSH_FSYNC_THEN_ATOMIC_RENAME_BEFORE_ORIGINAL_APP_CLOSE',
          'fast close intent publication protocol differs')


def evaluate_waited_worker(job_root, returncode, entry, run_id):
    """Call ONLY after the owner's original actual p.wait(), never a poll/intent.

    Keep every original FINAL/error/full-save failure. Only the single exact
    missing-close-lifecycle reason can be replaced by a strict pinned intent.
    """
    original = _base.evaluate_waited_worker(job_root, returncode, entry, run_id)
    reasons = list(original['reasons'])
    job = Path(job_root).resolve()
    output = job / 'production'
    new_errors = _error_evidence(job)
    if new_errors:
        reasons.append('V5_any_new_or_secondary_error_sidefile_present_or_unknown')
    valid_intent = False
    intent = None
    try:
        present = (output / INTENT_NAME).exists()
    except BaseException:
        present = False
        reasons.append('V5_fast_close_intent_presence_unknown')
    if present:
        try:
            intent, _ = _read_object(output / INTENT_NAME)
            final, final_raw = _read_object(output / 'FINAL.json')
            _validate_intent(intent, final, final_raw, job, entry, run_id)
            valid_intent = True
        except BaseException as exc:
            reasons.append('V5_bad_fast_close_intent:' + type(exc).__name__ + ':' + str(exc))
    accepted_expected_nonreturn = False
    if original['reasons'] == ['original_close_completion_missing']:
        if not present:
            reasons.append('V5_fast_close_intent_missing')
        if valid_intent and not new_errors and type(returncode) is int and returncode == 0:
            try:
                _need(not (output / _APP_CLOSED).exists(), 'post-App marker exists but original lifecycle is missing')
                _need(not (output / _LIFECYCLE).exists(), 'original lifecycle is not actually absent')
                _need(reasons == ['original_close_completion_missing'], 'other original/V5 failures remain')
            except BaseException as exc:
                reasons.append('V5_missing_marker_substitution_blocked:' + str(exc))
            else:
                reasons = []  # This is the ONLY replaced original reason.
                accepted_expected_nonreturn = True
    return dict(
        kind='ACTUAL_WAIT_APP_CLOSE_SEMANTIC_RESULT_V5', original_error=bool(reasons),
        passed_execution=not reasons, returncode=returncode, reasons=reasons,
        original_V4_reasons=list(original['reasons']), original_V4_result=original,
        error_sidefiles=sorted(set(original.get('error_sidefiles', []) + new_errors)),
        final=original.get('final'), checkpoint_bytes_opened=0, finite_saved_is_not_skill_pass=True,
        actual_wait_returned=True, app_close_expected_nonreturn=accepted_expected_nonreturn,
        app_close_returned=None if accepted_expected_nonreturn else (True if not reasons else None),
        accepted_missing_post_app_marker=accepted_expected_nonreturn,
        close_outcome=('PINNED_FAST_CLOSE_EXPECTED_PROCESS_NONRETURN_PLUS_ACTUAL_WAIT'
                       if accepted_expected_nonreturn else 'ORIGINAL_POST_RETURN_GATE' if not reasons else 'FAIL_CLOSED'),
        historical_app_mode_or_exit_cause_inferred=False,
    )


class BoundedPoseCacheEventsV5:
    """O(1)-size first-three/last/counters; publish every 20s OR 128 events.

    The first three and any adapter-error event publish immediately. Nothing
    calls an SDK getter, observation, reset or RNG. No unbounded event history.
    """
    _EVENTS = ('installed', 'write_returned_and_invalidated', 'original_writer_raised',
               'adapter_rejected_before_write', 'adapter_rejected_after_write',
               'install_rejected', 'uninstalled')

    def __init__(self, emit, *, clock=time.monotonic):
        _need(callable(emit) and callable(clock), 'bounded recorder requires Python emit/clock callbacks')
        self._emit, self._clock = emit, clock
        self._first, self._last = [], None
        self._counts = {key: 0 for key in self._EVENTS}
        self._total = self._published_at_count = self._publications = 0
        self._last_published_time = None

    def __call__(self, event):
        _need(type(event) is dict and event.get('event') in self._counts, 'unknown adapter event schema')
        raw = json.dumps(event, sort_keys=True, allow_nan=False).encode('utf-8')
        _need(len(raw) <= 131072, 'one adapter event exceeds bounded metadata limit')
        value = json.loads(raw)
        self._total += 1
        self._counts[value['event']] += 1
        if len(self._first) < 3:
            self._first.append(value)
        self._last = value
        force = self._total <= 3 or 'rejected' in value['event'] or value['event'].endswith('_raised')
        self.flush(force=force)

    def snapshot(self):
        value = dict(kind=BOUNDED_EVENTS_KIND, first_three=list(self._first), last=self._last,
                     event_counts=dict(self._counts), events_seen=self._total,
                     retained_event_records=len(self._first) + (self._last is not None),
                     publications=self._publications, publication_interval_s=20.0,
                     publication_event_stride=128, no_extra_observation_getters=True,
                     no_extra_reset_step_or_RNG=True)
        return json.loads(json.dumps(value, allow_nan=False))

    def flush(self, *, force=False):
        now = self._clock()
        _need(type(now) in (int, float) and math.isfinite(now), 'bounded recorder clock is not finite Python scalar')
        due = (force or self._last_published_time is None
               or self._total - self._published_at_count >= 128
               or now - self._last_published_time >= 20.0)
        if not due:
            return False
        value = self.snapshot()
        value['publications'] = self._publications + 1
        self._emit(value)
        self._publications += 1
        self._published_at_count = self._total
        self._last_published_time = now
        return True


def force_pose_cache_event_receipt_v5(events, output, *, role):
    """Final/error flush without masking the already preserved primary error."""
    try:
        events.flush(force=True)
    except BaseException:
        error = traceback.format_exc()
        try:
            _base.preserve_worker_error(output, role=role, error=error, phase='pose_cache_receipt_flush_v5')
        except BaseException:
            pass
        return error
    return None
