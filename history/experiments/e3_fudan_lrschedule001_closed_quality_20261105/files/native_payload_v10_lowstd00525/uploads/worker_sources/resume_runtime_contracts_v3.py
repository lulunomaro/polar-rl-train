"""SOURCE CANDIDATE ONLY: semantic completion, owned full resume and close receipts.

Stdlib at import. No SDK/Torch import, checkpoint read, hardware query, lock,
accounting or process launch occurs here. Future workers explicitly supply the
Torch decoder AFTER their original admission. Current tests use fake byte readers.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import math
import os
import re
import sys
import time
import traceback
from collections.abc import Mapping
from pathlib import Path

FINAL_KIND = 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
LIFECYCLE_KIND = 'MOD4V1_SUPERMIMIC_ORIGINAL_CLOSE_COMPLETE_V3'
BASELINE_ACTOR_VIEW = 'baseline_fullctx_v1'
RAW35_ACTOR_VIEW = 'raw35_legacy_held_aux_v1'
BASELINE_EXTENSION_SCHEMA = 'mod4v1.ctx_task_reward.v1'
COUNT_FIELDS = (
    'policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps',
    'pi_unverified_steps', 'pi_skipped_nonfinite', 'pi_skipped_zero',
    'wm_optimizer_steps', 'aux_optimizer_steps', 'critic_optimizer_steps',
)
WORKER_ERROR_NAMES = ('WORKER_ERROR.json', 'WORKER_ERROR_FALLBACK_V2.json',
                      'WORKER_PRESTART_ERROR_V2.json')


def validate_worker_variant(task):
    resume = task.get('resume_bptt') is not None
    view = task.get('actor_view', BASELINE_ACTOR_VIEW)
    default = ('A1_RAW35_RESUME' if resume else 'A1_RAW35_FRESH') if view == RAW35_ACTOR_VIEW else ('A0_FULLCTX_RESUME' if resume else 'A0_FULLCTX_FRESH')
    variant = task.get('algorithm_variant', default)
    choices = {
        'A0_FULLCTX_FRESH': (BASELINE_ACTOR_VIEW, 'a0_fullctx_legacy_v1', False),
        'A0_FULLCTX_RESUME': (BASELINE_ACTOR_VIEW, 'a0_fullctx_legacy_v1', True),
        'A1_RAW35_FRESH': (RAW35_ACTOR_VIEW, 'a1_raw35_legacy_v1', False),
        'A1_RAW35_RESUME': (RAW35_ACTOR_VIEW, 'a1_raw35_legacy_v1', True),
    }
    require(variant in choices, 'explicit A0/A1 algorithm variant differs')
    expected_view, family, expected_resume = choices[variant]
    require(view == expected_view and resume == expected_resume, 'actor view/resume descriptor does not match selected variant')
    if resume:
        require(task['resume_bptt'].get('actor_view') == view, 'cross-view weights/Adam/history/counter migration is not admitted')
    return dict(algorithm_variant=variant, actor_view=view, algorithm_family=family,
                actor_observation_dim=35 if view == RAW35_ACTOR_VIEW else None,
                command_tracking_fixed=False, sensor_projection_exact=False,
                bound_anchor_reward_changes=0)


def require(value, message):
    if not value:
        raise ValueError(message)


def _nonnegative_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def validate_count_snapshot(counts):
    require(isinstance(counts, Mapping), 'producer counters are missing')
    require(all(k in counts and _nonnegative_integer(counts[k]) for k in COUNT_FIELDS),
            'all nine original producer counters must be nonnegative integers')
    require(counts['pi_bptt_optimizer_steps'] <= counts['pi_optimizer_steps'] <= counts['policy_attempts'],
            'producer BPTT/optimizer/attempt counter ordering differs')
    return dict(counts)


def _read_json(path):
    """Read only terminal evidence; error presence is checked separately."""
    try:
        raw = Path(path).read_bytes()
    except FileNotFoundError:
        return None, 'missing'
    except BaseException as exc:
        return None, 'read_error:' + type(exc).__name__
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError):
        return None, 'malformed_json'
    return value, None if isinstance(value, dict) else 'not_object'


def evaluate_waited_worker(job_root, returncode, entry, run_id):
    """Only call AFTER actual p.wait(). RC0 by itself is never semantic success.

    No checkpoint is opened. A finite, fully saved execution may pass this gate
    with target_reached=False; no skill/90-percent interpretation is made.
    """
    job = Path(job_root)
    output = job / 'production'
    reasons = []
    if type(returncode) is not int or returncode != 0:
        reasons.append('nonzero_process_returncode')
    error_paths = [output / name for name in WORKER_ERROR_NAMES]
    error_paths += [job / 'WORKER_ERROR_FALLBACK_V2.json', job / 'WORKER_PRESTART_ERROR_V2.json']
    present_errors = []
    for path in error_paths:
        try:
            if path.exists():
                present_errors.append(str(path))
        except BaseException:
            present_errors.append(str(path) + ':presence_unknown')
    if present_errors:
        reasons.append('worker_error_sidefile_present_or_unknown')
    final, read_error = _read_json(output / 'FINAL.json')
    if read_error:
        reasons.append('success_FINAL_' + read_error)
    else:
        try:
            require(final.get('kind') == FINAL_KIND, 'new FINAL schema differs')
            require(final.get('passed_execution') is True, 'execution not explicitly successful')
            require(final.get('role') == entry['role'] and final.get('role_key') == entry['role_key'], 'role identity differs')
            require(final.get('run_id') == run_id, 'FINAL run identity differs')
            selected = validate_worker_variant(entry)
            require(final.get('actor_view') == selected['actor_view'] and final.get('algorithm_family') == selected['algorithm_family'], 'FINAL A0/A1 actor family differs')
            counts = validate_count_snapshot(final.get('counts'))
            require(final.get('actual_BPTT_policy_steps') == counts['pi_bptt_optimizer_steps'], 'FINAL count differs')
            checkpoint = final.get('checkpoint')
            require(isinstance(checkpoint, dict) and _sha(checkpoint.get('SHA')), 'complete checkpoint receipt is missing')
            require(_nonnegative_integer(checkpoint.get('bytes')) and checkpoint['bytes'] > 0, 'checkpoint byte size differs')
            require(checkpoint.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved') is True, 'full checkpoint declaration is missing')
            require(checkpoint.get('counts') == counts and final.get('teacher_unchanged') is True, 'checkpoint counters/teacher declaration differ')
            expected = output / 'checkpoints'
            require(Path(checkpoint['path']).resolve().is_relative_to(expected.resolve()), 'checkpoint is not an own new production checkpoint')
        except (ValueError, KeyError, TypeError) as exc:
            reasons.append('bad_success_FINAL:' + str(exc))
    lifecycle, life_error = _read_json(output / 'WORKER_LIFECYCLE_COMPLETE_V3.json')
    if life_error:
        reasons.append('original_close_completion_' + life_error)
    elif not (lifecycle.get('kind') == LIFECYCLE_KIND and lifecycle.get('passed_execution') is True
              and lifecycle.get('role') == entry['role'] and lifecycle.get('run_id') == run_id
              and lifecycle.get('all_original_close_calls_returned') is True):
        reasons.append('bad_original_close_completion')
    return dict(kind='ACTUAL_WAIT_SEMANTIC_RESULT_V2', original_error=bool(reasons),
                passed_execution=not reasons, returncode=returncode, reasons=reasons,
                error_sidefiles=present_errors, final=final,
                finite_saved_is_not_skill_pass=True, checkpoint_bytes_opened=0)


def validate_resume_descriptor(value):
    require(isinstance(value, dict), 'explicit own full-resume descriptor required')
    require(value.get('kind') == 'OWN_NEW_BPTT_FULL_CHECKPOINT_V2', 'old PPO/actor-only resume is not this contract')
    require(isinstance(value.get('path'), str) and value['path'], 'full checkpoint source path required')
    require(_sha(value.get('SHA')) and _nonnegative_integer(value.get('bytes')) and value['bytes'] > 0, 'pinned full checkpoint byte identity required')
    require(value.get('actor_view') in (BASELINE_ACTOR_VIEW, RAW35_ACTOR_VIEW), 'known actor view is required')
    if value['actor_view'] == RAW35_ACTOR_VIEW:
        require(value.get('algorithm_family') == 'a1_raw35_legacy_v1', 'A1 resumes require an own same-variant full checkpoint')
    require(value.get('allow_environment_reset') is True, 'one explicit fresh environment reset must be declared')
    require(value.get('allow_partial_update') is False, 'partial optimizer transaction resume is not admitted')
    require(isinstance(value.get('producer_run_id'), str) and value['producer_run_id'], 'producer run provenance required')
    return dict(value)


def validate_bridge_adapter_descriptor(value):
    require(isinstance(value, dict), 'bridge adapter descriptor must be explicit')
    module = value.get('module')
    require(isinstance(module, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', module), 'adapter module must be a single owned module name')
    require(value.get('source_relative') == 'worker_sources/' + module + '.py', 'adapter must be a manifest-pinned owned worker source')
    require(value.get('interface') == 'NativeTaskBridge.v1' and value.get('symbol') == 'NativeTaskBridge', 'adapter interface differs')
    require(_sha(value.get('SHA')) and _nonnegative_integer(value.get('bytes')) and value['bytes'] > 0, 'adapter source identity required')
    return dict(value)


def bind_future_task_extensions(task, entry):
    """Pure future metadata; all original owner admission/accounting stays outside."""
    output = dict(task)
    output['actor_view'] = entry.get('actor_view', BASELINE_ACTOR_VIEW)
    if entry.get('algorithm_variant') is not None:
        output['algorithm_variant'] = entry['algorithm_variant']
    if entry.get('resume_bptt') is not None:
        output['resume_bptt'] = validate_resume_descriptor(entry['resume_bptt'])
    else:
        output.pop('resume_bptt', None)
    output.update(validate_worker_variant(output))
    if entry.get('bridge_adapter') is not None:
        output['bridge_adapter'] = validate_bridge_adapter_descriptor(entry['bridge_adapter'])
    return output


class PinnedOwnFullCheckpoint:
    """Future-only one physical byte open, one SHA, one decode, retained payload.

    `decoder` receives a BytesIO (worker supplies torch.load(weights_only=True)).
    A custom reader exists solely for stdlib synthetic contract tests.
    """
    def __init__(self, descriptor, decoder, *, read_bytes=None):
        self.descriptor = validate_resume_descriptor(descriptor)
        read = (lambda path: Path(path).read_bytes()) if read_bytes is None else read_bytes
        raw = read(self.descriptor['path'])
        require(isinstance(raw, bytes), 'owned checkpoint reader must return bytes')
        require(len(raw) == self.descriptor['bytes'], 'owned full checkpoint byte size differs')
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == self.descriptor['SHA'], 'owned full checkpoint SHA differs')
        self.raw = raw
        self.payload = decoder(io.BytesIO(raw))
        require(isinstance(self.payload, dict), 'owned full checkpoint decoder returned a non-object')

    def receipt(self):
        return dict(source_path=self.descriptor['path'], source_SHA=self.descriptor['SHA'],
                    source_bytes=len(self.raw), physical_byte_opens=1, SHA_calculations=1,
                    decodes=1, whole_full_checkpoint_retained=True,
                    producer_run_id=self.descriptor['producer_run_id'],
                    source_kind='OWN_NEW_BPTT_FULL_CHECKPOINT_V2')


def validate_full_resume_payload(payload, task, current_contract, context_layout):
    """Metadata/schema gate before any load_state_dict mutation; tensor/opt shapes
    are additionally checked by original strict loaders. No actor-only fallback.
    """
    descriptor = validate_resume_descriptor(task.get('resume_bptt'))
    variant = validate_worker_variant(task)
    view = variant['actor_view']
    require(descriptor['actor_view'] == view, 'descriptor/worker actor view differs')
    required_top = {'args', 'wm', 'pi', 'critic', 'opt_wm', 'opt_pi', 'opt_v',
                    'iteration', 'sim_steps', 'wall_time', 'bootstrap_teacher',
                    'role', 'original_task_protocol', 'asset_SHA', 'contract_SHA',
                    'new_algorithm_not_PPO_resume', 'context_reward_extension'}
    require(isinstance(payload, dict) and required_top <= payload.keys(), 'four-model/four-optimizer/full producer checkpoint required')
    extension = payload['context_reward_extension']
    required_extension = {'contract', 'aux', 'opt_aux', 'counts', 'last_bptt_receipt',
                          'context_predict_mask', 'full_resume', 'replay', 'obs_hist',
                          'rng', 'collect_fraction', 'pending_iteration', 'environment',
                          'update_boundary_safe', 'resume_scope'}
    require(isinstance(extension, dict) and required_extension <= extension.keys(), 'complete replay/RNG/history/update transaction extension required')
    require(extension['full_resume'] is True and extension['update_boundary_safe'] is True, 'complete safe-boundary full checkpoint required')
    require(extension['resume_scope'] == 'learner_full_environment_reset_required', 'this worker uses one explicit fresh environment, not exact PhysX warmstart')
    contract = extension['contract']
    require(contract == current_contract and contract.get('schema') == BASELINE_EXTENSION_SCHEMA, 'baseline full-context schema/algorithm/clock/mask differs')
    expected_obs = 35 if view == RAW35_ACTOR_VIEW else 79 + contract.get('context_dim', -1000)
    require(contract.get('obs_dim') == expected_obs, 'same-view full observation/norm/optimizer dimensions required')
    if view == RAW35_ACTOR_VIEW:
        require(payload.get('actor_view') == view and payload.get('algorithm_family') == variant['algorithm_family'], 'A1 requires embedded same-view/family full-checkpoint provenance')
    else:
        require(payload.get('actor_view', view) == view and payload.get('algorithm_family', variant['algorithm_family']) == variant['algorithm_family'], 'A0 checkpoint actor family differs')
    require(contract.get('num_joints') == 30 and contract.get('action_dim') == 6
            and contract.get('num_envs') == task['num_envs'], 'baseline plant/action/batch dimensions differ')
    require(payload['role'] == task['role'] and payload['asset_SHA'] == task['asset_SHA']
            and payload['contract_SHA'] == task['contract_SHA'], 'owned role/asset identity differs')
    require(payload['original_task_protocol'] == task['original_protocol']
            and payload['new_algorithm_not_PPO_resume'] is True, 'original task protocol differs')
    teacher = payload['bootstrap_teacher']
    require(isinstance(teacher, dict) and teacher.get('source_SHA') == task['teacher_SHA']
            and teacher.get('source_bytes') == task['teacher_bytes']
            and teacher.get('source_path') == task['teacher_path'], 'original frozen teacher identity differs')
    require(Path(descriptor['path']).resolve() != Path(task['teacher_path']).resolve(), 'new BPTT source and old teacher PT must be distinct')
    environment = extension['environment']
    require(isinstance(environment, dict) and environment.get('exact') is False, 'reset-resume environment receipt required')
    saved_layout = [list(item) for item in environment.get('context_layout', [])]
    require(saved_layout == [list(item) for item in context_layout], 'named context order/width identity differs')
    counts = validate_count_snapshot(extension['counts'])
    require(_nonnegative_integer(payload['iteration']) and _nonnegative_integer(payload['sim_steps']), 'saved iteration/control counters differ')
    require(isinstance(payload['wall_time'], (int, float)) and math.isfinite(payload['wall_time']) and payload['wall_time'] >= 0, 'saved wall time differs')
    require(isinstance(extension['rng'], dict) and {'python', 'torch_cpu', 'torch_cuda'} <= extension['rng'].keys(), 'complete learner global RNG required')
    return dict(restored_counts=counts, restored_iteration=payload['iteration'],
                restored_sim_steps=payload['sim_steps'], saved_history_retained_in_source=True,
                live_history_after_reset='zeros_then_original_fresh_episode_padding',
                reset_resume_stream_cut_required=True, producer_run_id_embedded_in_checkpoint=payload.get('run_id'),
                declared_source_run_id=descriptor['producer_run_id'],
                no_actor_only_fallback=True, no_counter_offset_or_fresh_count_splicing=True)


def load_decoded_full_checkpoint_once(learner, pinned, task, context_layout):
    receipt = validate_full_resume_payload(pinned.payload, task, learner.extension_contract, context_layout)
    require(callable(getattr(learner, 'load_full_checkpoint', None)), 'decoded full checkpoint API missing')
    learner.load_full_checkpoint(pinned.payload, allow_environment_reset=True, allow_partial_update=False)
    require(vars(learner.counts) == receipt['restored_counts'], 'loader did not restore exact producer counters')
    require(learner.iteration == receipt['restored_iteration'] and learner.sim_steps == receipt['restored_sim_steps'], 'loader did not restore exact iteration/sim counters')
    return dict(receipt, byte_cache=pinned.receipt(), loader='load_full_checkpoint(decoded_payload)',
                explicit_allow_environment_reset=True, explicit_allow_partial_update=False)


def resolve_future_bridge_adapter(default_class, task, job_root):
    value = task.get('bridge_adapter')
    if value is None:
        return default_class, dict(adapter_requested=False, default_bridge_source_unchanged=True,
                                   quaternion_and_guard_changes_in_this_candidate=0)
    descriptor = validate_bridge_adapter_descriptor(value)
    path = (Path(job_root) / descriptor['source_relative']).resolve()
    root = (Path(job_root) / 'worker_sources').resolve()
    require(path.is_relative_to(root), 'adapter source escaped owned worker_sources')
    raw = path.read_bytes()
    require(len(raw) == descriptor['bytes'] and hashlib.sha256(raw).hexdigest() == descriptor['SHA'], 'adapter source differs from explicit task identity')
    spec = importlib.util.spec_from_file_location(descriptor['module'], path)
    require(spec is not None and spec.loader is not None, 'adapter import specification missing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cls = getattr(module, descriptor['symbol'])
    require(isinstance(cls, type) and all(callable(getattr(cls, name, None)) for name in
            ('init_state', 'step', 'export_supermimic_resume', 'close')), 'adapter bridge protocol differs')
    return cls, dict(adapter_requested=True, source_relative=descriptor['source_relative'],
                     source_SHA=descriptor['SHA'], source_bytes=len(raw),
                     runtime_binding='EXPLICIT_FUTURE_MERGE_PENDING_NATIVE_VALIDATION')


def preserve_worker_error(output, *, role, error, phase, counts=None, source_cache=None):
    """Durable first error; later errors get separate files, never erase primary.
    Does not change locks, accounting, windows or signals. Parent also checks a
    missing/bad FINAL, so write failure never turns RC0 into success.
    """
    output = Path(output)
    value = dict(epoch=time.time(), role=role, phase=phase, error=error,
                 counts=counts, source_cache=source_cache, no_unchanged_automatic_retry=True)
    text = json.dumps(value, indent=2, allow_nan=False)
    candidates = [output / 'WORKER_ERROR.json', output.parent / 'WORKER_ERROR_FALLBACK_V2.json']
    failures = []
    for path in candidates:
        try:
            try:
                stream = path.open('x', encoding='utf-8')
            except FileExistsError:
                path = path.with_name(path.stem + '_SECONDARY_' + str(time.time_ns()) + path.suffix)
                stream = path.open('x', encoding='utf-8')
            with stream:
                stream.write(text + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            return dict(path=str(path), persisted=True, earlier_write_errors=failures)
        except BaseException as exc:
            failures.append(type(exc).__name__ + ':' + str(exc))
    sys.stderr.write('WORKER_ERROR_PERSISTENCE_FAILURE_V2 ' + text + '\n' + repr(failures) + '\n')
    sys.stderr.flush()
    return dict(persisted=False, write_errors=failures)


def close_original_resources(bridge, env, namespace, emit):
    """Attempt original bridge/env/App close once each, preserving BaseException.

    A SystemExit(0) from close is a close error, not successful execution. Hard
    process exit has no post-close receipt and is blocked by the future owner.
    """
    records = []
    failures = []

    def call(name, obj, before_name, after_name):
        if obj is None:
            return
        if before_name:
            try:
                emit(before_name, dict(epoch=time.time(), calling_original_close=True))
            except BaseException:
                failures.append(dict(phase=before_name + '_sidefile', error=traceback.format_exc()))
        try:
            obj.close()
        except BaseException:
            failures.append(dict(phase=name, error=traceback.format_exc()))
            records.append(dict(resource=name, returned=False))
        else:
            records.append(dict(resource=name, returned=True))
            if after_name:
                try:
                    emit(after_name, dict(epoch=time.time(), closed=True))
                except BaseException:
                    failures.append(dict(phase=after_name + '_sidefile', error=traceback.format_exc()))

    call('bridge', bridge, None, None)
    call('env', env, 'APP_CLOSING.json', 'ENV_CLOSED.json')
    application = None if namespace is None else namespace.get('app')
    if namespace is not None and application is None:
        failures.append(dict(phase='app_handle', error='constructed namespace has no original app handle'))
    call('app', application, None, 'APP_CLOSED.json')
    return dict(records=records, errors=failures, all_original_close_calls_returned=not failures)
