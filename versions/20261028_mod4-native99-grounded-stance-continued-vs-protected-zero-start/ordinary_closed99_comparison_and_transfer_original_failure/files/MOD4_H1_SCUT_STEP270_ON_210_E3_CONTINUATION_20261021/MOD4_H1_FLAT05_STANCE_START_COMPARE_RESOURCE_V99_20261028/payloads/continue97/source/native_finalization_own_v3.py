"""UNINSTALLED candidate: complete native save publication and error-preserving exit.

No environment, actor forward, optimizer step, or production-source admission occurs
here. An exception from an inner save chain is never assumed to mean a complete
checkpoint. In particular, SavedStop is not bypassed or swallowed in that chain.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import time
import traceback
import uuid

import torch


REQUIRED_ORIGINAL_GROUPS = (
    'actor_state_dict', 'critic_state_dict', 'optimizer_state_dict',
    'sensor_DR_state', 'sensor_command_DR_rng_state',
    'sensor_physical_DR_rng_state', 'sensor_global_rng_state',
    'feedback_delay_state', 'physical_action_delay_state',
    'spring_pressure_state', 'gas_damping_state', 'chassis_PD_state',
    'H1_step270_task_state', 'H1_step270_runtime_contract',
)
REQUIRED_NATIVE_GROUPS = (
    'wm', 'pi', 'critic', 'opt_wm', 'opt_pi', 'opt_v',
    'iteration', 'wall_time', 'sim_steps', 'args', 'saved_at',
)
NATIVE_CONTRACT = dict(
    state_joints=30, actions=6, obs_dim=86, goal_dim=146,
    packed_state_dim=127, dynamic_aux_dim=54, static_context_dim=31,
    fresh4096_policy_only_bootstrap=True,
    original_physics_and_success_unchanged=True,
    original_RSL_core_frozen_bootstrap_only=True,
    not_production_expert_source=True,
    replay_not_saved_matching_upstream_resume_not_exact_PhysX_replay=True,
)


class PublicationError(RuntimeError):
    pass


def source_sha():
    """Hash this source file, never an old model or an existing pilot artifact."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path, value):
    """Fresh, single-writer output directory required; refuse stale manifests."""
    path = Path(path)
    if path.exists():
        raise FileExistsError('Refusing to replace an existing receipt: ' + str(path))
    temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.partial')
    with temporary.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    if path.exists():
        raise FileExistsError('Receipt appeared during publication: ' + str(path))
    os.replace(temporary, path)


def error_record(phase, error):
    return dict(
        epoch=time.time(), phase=phase,
        exception_type=type(error).__module__ + '.' + type(error).__qualname__,
        error=str(error),
        traceback=''.join(traceback.format_exception(type(error), error, error.__traceback__)),
    )


def emit_error(out, name, value):
    """Preserve receipt-write errors too; stderr is last resort if storage fails."""
    path = Path(out) / name
    if path.exists():
        path = path.with_name(path.stem + '_' + uuid.uuid4().hex + path.suffix)
    try:
        atomic_json(path, value)
        return dict(path=str(path), durable=True, write_errors=[])
    except BaseException as error:
        fallback = dict(value, receipt_write_errors=[error_record('error_receipt_write', error)])
        fallback_path = Path(out) / ('NATIVE_RECEIPT_FALLBACK_' + uuid.uuid4().hex + '.json')
        try:
            atomic_json(fallback_path, fallback)
            return dict(path=str(fallback_path), durable=True, write_errors=fallback['receipt_write_errors'])
        except BaseException as secondary:
            fallback['receipt_write_errors'].append(error_record('fallback_receipt_write', secondary))
            # The caller keeps the original exception even if diagnostic storage is lost.
            try:
                print('NATIVE_LIFECYCLE_UNPERSISTED_ERROR ' + json.dumps(fallback, allow_nan=False),
                      file=sys.stderr, flush=True)
            except BaseException:
                pass
            return dict(path=None, durable=False, write_errors=fallback['receipt_write_errors'])


def assert_finite(value, key='checkpoint'):
    if torch.is_tensor(value):
        if not bool(torch.isfinite(value).all()):
            raise PublicationError('Nonfinite tensor in ' + key)
    elif isinstance(value, dict):
        for name, child in value.items():
            assert_finite(child, key + '.' + str(name))
    elif isinstance(value, (tuple, list)):
        for index, child in enumerate(value):
            assert_finite(child, key + '[' + str(index) + ']')
    elif isinstance(value, float) and not math.isfinite(value):
        raise PublicationError('Nonfinite scalar in ' + key)


def verify_native(checkpoint, expected):
    if not isinstance(checkpoint, dict):
        raise PublicationError('Checkpoint is not a dictionary')
    missing = sorted(set(REQUIRED_ORIGINAL_GROUPS) - set(checkpoint))
    if missing:
        raise PublicationError('Incomplete original save chain: ' + repr(missing))
    native = checkpoint.get('UniSuperMimic_H1_test')
    if not isinstance(native, dict) or set(REQUIRED_NATIVE_GROUPS) - set(native):
        raise PublicationError('Incomplete native world/policy/critic/optimizer state')
    if native['iteration'] != expected['native_iteration']:
        raise PublicationError('Native iteration does not match this save invocation')
    if checkpoint.get('UniSuperMimic_publication') != expected:
        raise PublicationError('Fresh producer/save token verification failed')
    if checkpoint.get('UniSuperMimic_test_contract') != NATIVE_CONTRACT:
        raise PublicationError('Native test contract mismatch')
    history = checkpoint.get('UniSuperMimic_obs_history')
    steps = checkpoint.get('UniSuperMimic_bridge_ep_step')
    if not torch.is_tensor(history) or tuple(history.shape) != tuple(expected['history_shape']):
        raise PublicationError('Native observation history shape mismatch')
    if not torch.is_tensor(steps) or tuple(steps.shape) != tuple(expected['episode_step_shape']):
        raise PublicationError('Native episode steps shape mismatch')
    assert_finite(checkpoint)


class NativeCheckpointPublisher:
    """Invoke the entire old chain, augment a fresh stage, verify, then publish.

    The incoming destination remains identical for successful preupdate saves.
    If oldsave raises (including SavedStop), its stage is retained untrusted and
    no upper-layer state is fabricated. No pre-existing destination is read.
    """
    def __init__(self, oldsave, learner, bridge, out, producer):
        self.oldsave = oldsave
        self.learner = learner
        self.bridge = bridge
        self.out = Path(out)
        self.producer = dict(producer)
        self.run_token = uuid.uuid4().hex
        self.last_publication = None

    def __call__(self, path, *args, **kwargs):
        destination = Path(path)
        token = uuid.uuid4().hex
        stage = destination.with_name('.' + destination.name + '.native_' + token + '.partial')
        phase = 'reject_existing_destination'
        published = False

        def event(next_phase):
            nonlocal phase
            phase = next_phase
            try:
                print('NATIVE_SAVE_PHASE ' + json.dumps(dict(
                    epoch=time.time(), phase=phase, destination=str(destination),
                    stage=str(stage), run_token=self.run_token, save_token=token)),
                    file=sys.stderr, flush=True)
            except BaseException:
                pass

        try:
            if destination.exists():
                raise FileExistsError('Refusing stale/overwrite destination: ' + str(destination))
            if stage.exists():
                raise FileExistsError('Refusing existing save stage: ' + str(stage))
            event('original_full_save_chain')
            self.oldsave(str(stage), *args, **kwargs)
            # No catch-and-continue for stop exceptions: upper old wrappers may
            # not yet have appended physical/task state when such a stop fires.
            event('original_full_save_chain_returned_native_augmentation')
            state = torch.load(stage, map_location='cpu', weights_only=False)
            expected = dict(
                version=1, run_token=self.run_token, save_token=token,
                producer=self.producer,
                native_iteration=int(self.learner.iteration),
                history_shape=list(self.learner.obs_hist.shape),
                episode_step_shape=list(self.bridge.ep_step.shape),
                world_updates=int(self.bridge.wm_updates),
                policy_updates=int(self.bridge.pi_updates),
            )
            state['UniSuperMimic_H1_test'] = self.learner._checkpoint(True)
            state['UniSuperMimic_obs_history'] = self.learner.obs_hist.detach().cpu()
            state['UniSuperMimic_bridge_ep_step'] = self.bridge.ep_step.detach().cpu()
            state['UniSuperMimic_test_contract'] = dict(NATIVE_CONTRACT)
            state['UniSuperMimic_publication'] = expected
            with stage.open('wb') as stream:
                torch.save(state, stream)
                stream.flush()
                os.fsync(stream.fileno())
            del state
            event('verify_new_complete_native_stage')
            checked = torch.load(stage, map_location='cpu', weights_only=False)
            verify_native(checked, expected)
            del checked
            size = stage.stat().st_size
            digest = file_sha(stage)
            if destination.exists():
                raise FileExistsError('Destination appeared before publication: ' + str(destination))
            event('atomic_checkpoint_publication')
            os.replace(stage, destination)
            published = True
            receipt = dict(
                path=str(destination), bytes=size, SHA=digest,
                verified_new_publication=True,
                original_full_save_chain_returned=True,
                producer=self.producer, run_token=self.run_token, save_token=token,
                updates=expected['native_iteration'],
                world_updates=expected['world_updates'], policy_updates=expected['policy_updates'],
                not_production_H1_or_E2_source=True,
                not_PhysX_exact_resume=True,
            )
            self.last_publication = receipt
            event('new_checkpoint_publication_complete')
            return receipt
        except BaseException as error:
            record = dict(
                epoch=time.time(), passed=False, destination=str(destination),
                stage=str(stage), stage_retained_if_present=True,
                checkpoint_published=published, verified_complete=False,
                failure=error_record(phase, error),
                no_existing_file_promoted_to_complete=True,
                wrapped_stop_is_a_scenario_not_actual82Q_cause=True,
            )
            emit_error(self.out, 'NATIVE_SAVE_PUBLICATION_ORIGINAL_ERROR_' + token + '.json', record)
            raise


def run_native_lifecycle(*, train, stop_types, persist_trace, save, out,
                         iteration, world_updates, policy_updates, events,
                         write_manifest=atomic_json):
    """Always attempt trace persistence and a new save; preserve first error.

    Primary learning/collection error is re-raised with its original traceback
    after all secondary finalization errors are recorded. FINAL is the last
    commit marker and is never inferred from process rc or an existing file.
    """
    out = Path(out)
    errors = []
    receipts = []
    timeline = []
    stop_kind = 'normal_completion'
    publication = None
    trace_persisted = False

    def event(phase):
        row = dict(epoch=time.time(), phase=phase)
        timeline.append(row)
        try:
            print('NATIVE_LIFECYCLE ' + json.dumps(row), file=sys.stderr, flush=True)
        except BaseException:
            pass

    def capture(phase, error, name):
        record = error_record(phase, error)
        errors.append((error, error.__traceback__, record))
        receipt = emit_error(out, name, dict(
            epoch=time.time(), passed=False,
            primary_error=errors[0][2], secondary_errors=[entry[2] for entry in errors[1:]],
            current_error=record, phases=timeline,
            partial_files_retained=True, not_production_H1_or_E2_source=True,
        ))
        receipts.append(receipt)

    event('learning_or_collection_begin')
    try:
        train()
    except stop_types:
        stop_kind = 'own_complete_saved_stop_requested'
        event('own_stop_caught_no_complete_file_assumed')
    except BaseException as error:
        stop_kind = 'original_learning_or_collection_error'
        capture('learning_or_collection', error, 'NATIVE_SUPERMIMIC_LEARN_ORIGINAL_ERROR.json')
    event('trace_persist_begin')
    try:
        persist_trace()
        trace_persisted = True
        event('trace_persist_complete')
    except BaseException as error:
        capture('trace_persist', error, 'NATIVE_TRACE_PERSIST_ORIGINAL_ERROR.json')
    path = out / ('FAILED_PARTIAL_NATIVE_FULLSTATE.pt' if errors else 'native_supermimic_H1_final.pt')
    event('new_full_native_save_begin')
    try:
        publication = save(str(path))
        if (not isinstance(publication, dict)
                or publication.get('verified_new_publication') is not True
                or publication.get('path') != str(path)):
            raise PublicationError('Save returned no verified receipt for this destination')
        event('new_full_native_save_verified_and_published')
    except BaseException as error:
        publication = None
        capture('final_native_save', error, 'NATIVE_FULLSAVE_ORIGINAL_ERROR.json')
    actual_events = None
    try:
        actual_events = events()
    except BaseException as error:
        capture('lifetime_event_snapshot', error, 'NATIVE_EVENT_SNAPSHOT_ORIGINAL_ERROR.json')
    try:
        counters = dict(updates=int(iteration()), world_updates=int(world_updates()),
                        policy_updates=int(policy_updates()))
        if publication is not None:
            if any(publication[key] != value for key, value in counters.items()):
                raise PublicationError('Post-save native counters changed before manifest')
    except BaseException as error:
        counters = None
        capture('native_counter_snapshot', error, 'NATIVE_COUNTER_SNAPSHOT_ORIGINAL_ERROR.json')
    passed = (not errors and publication is not None and trace_persisted
              and counters is not None and counters['policy_updates'] > 0)
    final = None if publication is None else dict(publication, original_H1_events=actual_events)
    event('terminal_manifest_commit_begin')
    manifest = dict(
        epoch=time.time(), passed=passed, final=final,
        completion_kind=stop_kind, trace_persisted=trace_persisted,
        counters=counters,
        primary_error=errors[0][2] if errors else None,
        secondary_errors=[entry[2] for entry in errors[1:]],
        error_receipts=receipts, phases=timeline,
        not_frozen_skill_graduation=True,
        not_production_H1_or_E2_source=True,
        rc0_is_not_success_evidence=True,
        actual82Q_manifest_gap_cause='UNPROVEN',
    )
    name = 'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json' if errors else 'FINAL.json'
    try:
        write_manifest(out / name, manifest)
    except BaseException as error:
        capture('terminal_manifest_commit', error, 'NATIVE_MANIFEST_ORIGINAL_ERROR.json')
        emit_error(out, 'NATIVE_FINALIZATION_FAILED_ACTUAL.json', dict(
            epoch=time.time(), passed=False, final=final,
            manifest_committed=False, intended_manifest=name,
            primary_error=errors[0][2], secondary_errors=[entry[2] for entry in errors[1:]],
            error_receipts=receipts, phases=timeline,
            checkpoint_retained_but_not_promoted_without_manifest=True,
            not_production_H1_or_E2_source=True,
        ))
    if errors:
        primary, original_traceback, _ = errors[0]
        raise primary.with_traceback(original_traceback)
    return manifest
