"""UNINSTALLED native85M2 -> new-episode continuation candidate.

No checkpoint path is opened here. The caller must supply the actual, closed,
CPU-reviewed checkpoint and metadata. Legacy85 replay does not exist on disk;
old observation/episode histories are retained as provenance, never spliced
into a newly reset physical episode. No environment reset/forward/step occurs.
"""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path, PurePosixPath

import torch

BOOTSTRAP_SHA = '8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6'
REFERENCE_SHA = '0b9d642f3530ad55bd353c19918a0778378746ecc250e1f22c10c58b8c095c94'
OBJECTIVE_SCHEMA = 'mod4.supermimic.partial_reference_objective_contract.v2'
SOURCE_GROUP = 'UniSuperMimic_H1_test'
EXTENSION_GROUP = 'UniSuperMimic_continuation_state_v1'
MODULES = ('wm', 'pi', 'critic')
OPTIMIZERS = ('opt_wm', 'opt_pi', 'opt_v')
PRODUCER_KEYS = ('bridge_source_SHA', 'finalization_source_SHA',
                 'bootstrap_task_source_SHA', 'reference_artifact_SHA',
                 'adapter_CPU_report_SHA', 'objective_contract_SHA',
                 'runtime_objective_contract_SHA')


class ContinuationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ContinuationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False)


def read_pinned_metadata_bundle(binding_path):
    """Read only explicitly pinned JSON metadata, contained in the new payload.

    The future source guard must pin the binding itself. Missing actual closure
    evidence is fatal, never converted from a placeholder to admitted metadata.
    """
    path = Path(binding_path)
    binding = json.loads(path.read_bytes())
    require(binding.get('status') == 'ACTUAL_CLOSED_CPU_QUALIFIED', 'Native closure still pending')
    payload = path.parent.resolve()
    outputs = {}
    for key, pin_key in (('final', 'FINAL_metadata_SHA'), ('full_cpu', 'full_CPU_report_SHA'),
                         ('collector', 'collector_report_SHA'), ('runtime_order', 'runtime_order_metadata_SHA')):
        relative = PurePosixPath(binding['metadata'][key]['relative'])
        require(not relative.is_absolute() and '..' not in relative.parts and relative.suffix == '.json', 'Metadata path not contained JSON')
        target = (payload / str(relative)).resolve()
        require(target.is_relative_to(payload), 'Metadata escaped payload')
        raw = target.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == binding[pin_key], 'Metadata pin differs: ' + key)
        outputs[key] = json.loads(raw)
    return binding, outputs


def exact(a, b):
    if torch.is_tensor(a):
        return (torch.is_tensor(b) and a.shape == b.shape and a.dtype == b.dtype
                and torch.equal(a.detach().cpu(), b.detach().cpu()))
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return type(a) is type(b) and len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


def finite(value):
    if torch.is_tensor(value):
        require(bool(torch.isfinite(value).all()), 'Nonfinite saved native state')
    elif isinstance(value, dict):
        for child in value.values():
            finite(child)
    elif isinstance(value, (tuple, list)):
        for child in value:
            finite(child)
    elif isinstance(value, float):
        require(math.isfinite(value), 'Nonfinite saved scalar')


def admit_closed_source(binding, final, full_cpu, collector, runtime_order,
                        current_runtime_order, current_runtime_objective):
    """Validate existing85M2 receipt schemas; no rc0-only or prefix admission.

    Root must pin raw metadata bytes separately before decoding these objects.
    binding is a new, explicit native continuation source record, not TASK/GO.
    """
    require(binding.get('schema') == 'mod4.native.continuation_source_binding.v1', 'Binding schema')
    require(binding.get('status') == 'ACTUAL_CLOSED_CPU_QUALIFIED', 'Source still pending')
    require(binding.get('source_namespace') == 'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026', 'Wrong native generation')
    for key in ('checkpoint_SHA', 'FINAL_metadata_SHA', 'full_CPU_report_SHA', 'collector_report_SHA'):
        value = binding.get(key)
        require(isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'Unpinned ' + key)
    require(final.get('passed') is True and final.get('trace_persisted') is True, 'No successful formal FINAL')
    require(final.get('primary_error') is None and not final.get('secondary_errors'), 'Original/secondary error')
    publication = final['final']
    require(publication.get('verified_new_publication') is True and publication.get('original_full_save_chain_returned') is True, 'Unverified publication')
    require(publication['SHA'] == binding['checkpoint_SHA'], 'Wrong checkpoint producer SHA')
    require(publication['updates'] > 0 and publication['world_updates'] > 0 and publication['policy_updates'] > 0, 'No positive native learning')
    producer = publication['producer']
    require(all(producer[k] == binding['producer'][k] for k in PRODUCER_KEYS), 'Producer pins differ')
    require(producer['bootstrap_task_source_SHA'] == BOOTSTRAP_SHA and producer['reference_artifact_SHA'] == REFERENCE_SHA, 'Wrong bootstrap/reference')
    require(full_cpu.get('passed') is True and full_cpu.get('all_owner_nodes_children_actual_out') is True, 'No complete closed CPU review')
    reviewed = full_cpu['native_method']
    require(reviewed.get('present') is True and reviewed.get('native_fullstate_CPU_verified') is True and reviewed.get('bootstrap_frozen_Adam829700') is True, 'Native fullstate not qualified')
    require(reviewed['final']['SHA'] == publication['SHA'] and reviewed['producer'] == producer, 'CPU review source differs')
    require(collector.get('actual_finite_transport_returned') is True and collector.get('original_canonical_cost_settled') is True, 'Unsettled original cost')
    authority = collector['authority72']
    require(authority.get('all_authority72_owner_children_actual_out') is True, 'Owner/children not out')
    require(authority['cohort'].get('original_cost_settled') is True and authority['owner_exit'].get('original_cost_settled') is True, 'Owner settlement incomplete')
    require(all(row.get('actual_fcntl_free') is True for row in authority['original_locks']) and len(authority['original_locks']) == 2, 'Original two locks not free at collection')
    terminal = authority['cohort']['rows']['e2']
    require(terminal.get('returncode') == 0 and not terminal.get('original_error') and not terminal.get('errors') and terminal.get('final') == final, 'Native original terminal differs')
    cost = authority['original_segment']['experts']['e2']
    require(cost.get('duration_bound_passed') is True and 0 < cost['charged_seconds'] <= 3900, 'Native original actual cost/bound failed')
    for order in (runtime_order, current_runtime_order):
        require(order.get('actual_runtime_order_readback') is True and order.get('complete_named_permutation') is True and order.get('before_first_physical_step_and_Pi') is True, 'Missing actual runtime named-order guard')
        require(order['reference_artifact_SHA'] == REFERENCE_SHA, 'Runtime reference differs')
    require(runtime_order['original_run_id'] == binding['source_run_id'], 'Source run identity differs')
    require(runtime_order['actual_robot_joint_names'] == current_runtime_order['actual_robot_joint_names'], 'Learned state joint order changed; no network reorder admitted')
    require(len(set(runtime_order['actual_robot_joint_names'])) == 30, 'Joint schema')
    require(runtime_order['runtime_objective_contract_SHA'] == current_runtime_order['runtime_objective_contract_SHA'] == producer['runtime_objective_contract_SHA'], 'Runtime objective changed')
    require(current_runtime_objective.get('schema') == OBJECTIVE_SCHEMA and current_runtime_objective.get('provider_execution_scope') == 'runtime_actual_SDK_named_mapping_required' and current_runtime_objective['reference_metadata'].get('sdk_joint_order_verified') is True, 'Objective runtime scope')
    digest = hashlib.sha256((canonical(current_runtime_objective) + '\n').encode('utf8')).hexdigest()
    require(digest == producer['runtime_objective_contract_SHA'], 'Runtime objective bytes/digest differ')
    return dict(admitted=True, checkpoint_SHA=publication['SHA'], source_run_id=binding['source_run_id'],
                publication=deepcopy(publication), producer=deepcopy(producer),
                mode='native_parameters_optimizers_counters_new_physical_episode',
                legacy_replay_available=False, not_PhysX_exact_resume=True)


def construct_preserving_post_reset_global_rng(factory, capture, restore):
    """D0-D7 owns global streams. Do not let learner.manual_seed rewind them.

    Runtime callbacks must cover CPU + all CUDA global states. Private component
    streams are never touched. This restores *post-new-episode* state, not saved
    pre-reset state. Native stochastic bitwise continuation is not claimed.
    """
    state = capture()
    try:
        return factory()
    finally:
        restore(state)


def _compatible_state(target, source, path):
    require(isinstance(target, dict) and isinstance(source, dict) and set(target) == set(source), 'State keys differ: ' + path)
    for key, value in target.items():
        saved = source[key]
        if torch.is_tensor(value):
            require(torch.is_tensor(saved) and value.shape == saved.shape and value.dtype == saved.dtype, 'Tensor schema differs: ' + path + '.' + key)
        elif isinstance(value, dict):
            _compatible_state(value, saved, path + '.' + key)


def restore_legacy85_new_episode(checkpoint, learner, bridge, admission,
                                 new_episode_proof, verify_original_publication):
    """Call after original complete D0-D7 restore/reset + learner construction.

    verify_original_publication is frozen native_finalization.verify_native.
    Unexpected loader errors are fatal; caller must abort before first control.
    """
    require(admission.get('admitted') is True, 'Native source not admitted')
    require(new_episode_proof.get('source_SHA') == admission['checkpoint_SHA'] and new_episode_proof.get('new_physical_episode_zeroes_goal_credit') is True and new_episode_proof.get('not_PhysX_exact_resume') is True and new_episode_proof['complete_D0_D7_original_proof'].get('new_physical_episode') is True, 'Original D0-D7 new-episode receipt absent')
    verify_original_publication(checkpoint, checkpoint['UniSuperMimic_publication'])
    pub = checkpoint['UniSuperMimic_publication']
    final = admission['publication']
    require(pub['producer'] == admission['producer'] and all(pub[key] == final[key] for key in ('run_token', 'save_token', 'world_updates', 'policy_updates')), 'Checkpoint/FINAL binding differs')
    native = checkpoint[SOURCE_GROUP]
    require(native['iteration'] == pub['native_iteration'] == final['updates'] > 0, 'Iteration differs')
    require(canonical(native['args']) == canonical(asdict(learner.cfg)), 'Learner configuration changed')
    require(checkpoint['UniSuperMimic_test_contract']['replay_not_saved_matching_upstream_resume_not_exact_PhysX_replay'] is True and EXTENSION_GROUP not in checkpoint, 'Not legacy85 replay contract')
    require(learner.iteration == 0 and learner.buffer.size == 0 and learner.buffer.ptr == 0 and bridge.wm_updates == bridge.pi_updates == 0, 'Restore into a used learner forbidden')
    require(not bool(bridge.ep_step.any()), 'New bridge episode not zero')
    for name in MODULES:
        _compatible_state(getattr(learner, name).state_dict(), native[name], name)
    for name in OPTIMIZERS:
        require(set(native[name]) == {'state', 'param_groups'} and native[name]['param_groups'] and native[name]['state'], 'Optimizer state missing: ' + name)
        live = getattr(learner, name).state_dict()['param_groups']
        require(len(live) == len(native[name]['param_groups']) and all(len(a['params']) == len(b['params']) for a, b in zip(live, native[name]['param_groups'])), 'Optimizer parameter group mismatch')
    finite(native)
    # Validate all schemas before the first mutation. Any loader exception below
    # is terminal; no fresh-weight fallback or partial-restore training is valid.
    for name in MODULES:
        getattr(learner, name).load_state_dict(native[name], strict=True)
    for name in OPTIMIZERS:
        getattr(learner, name).load_state_dict(native[name])
    for name in ('iteration', 'wall_time', 'sim_steps'):
        setattr(learner, name, native[name])
    bridge.wm_updates = int(pub['world_updates'])
    bridge.pi_updates = int(pub['policy_updates'])
    bridge.window_start_wm_updates = bridge.wm_updates
    bridge.window_start_pi_updates = bridge.pi_updates
    learner.obs_hist.zero_()
    bridge.ep_step.zero_()
    bridge.state = None  # current freshly reset plant is sampled lazily again
    for name in MODULES + OPTIMIZERS:
        require(exact(getattr(learner, name).state_dict(), native[name]), 'Post-load roundtrip differs: ' + name)
    return dict(schema='mod4.native.restore_new_episode_receipt.v1', passed=True,
                source_checkpoint_SHA=admission['checkpoint_SHA'], source_run_id=admission['source_run_id'],
                restored_iteration=learner.iteration, restored_world_updates=bridge.wm_updates,
                restored_policy_updates=bridge.pi_updates, restored_wall_time=learner.wall_time,
                restored_sim_steps=learner.sim_steps, all_three_native_optimizers_restored=True,
                old_saved_history_retained_as_source_provenance_not_injected=True,
                new_physical_episode=True, replay_restored=False, replay_missing_in_legacy85=True,
                fresh_replay_refill_steps=max(learner.cfg.hist, learner.cfg.wm_window, learner.cfg.warmup_steps),
                wm_only_phase_uses_cumulative_iteration=True, not_PhysX_exact_resume=True)


def continuation_manifest_writer(original_writer, bridge, restore_receipt):
    """Keep cumulative counters; require a genuinely new Pi for passed FINAL."""
    def write(path, manifest):
        progress = dict(world_updates=bridge.wm_updates - bridge.window_start_wm_updates,
                        policy_updates=bridge.pi_updates - bridge.window_start_pi_updates)
        require(min(progress.values()) >= 0, 'Cumulative counters regressed')
        manifest['native_continuation'] = dict(restore=restore_receipt, window_progress=progress,
                                               no_fresh_weight_restart=True)
        manifest['passed'] = bool(manifest['passed'] and progress['policy_updates'] > 0)
        return original_writer(path, manifest)
    return write


def snapshot_replay_extension_candidate(learner, bridge, global_rng_snapshot):
    """Future publisher hook ONLY: not wired into installed85 or candidate86.

    Requires a new publisher contract/verification and save-budget admission.
    Preserve ring storage exactly; before resuming into a new physical episode,
    WM windows need the episode-restart mask below. Never inject old obs history
    or rewind the shared RNG after D0-D7 has reset a new episode.
    """
    buffer = learner.buffer
    return dict(schema='mod4.supermimic.continuation_state.v1',
                replay=dict(T=buffer.T, N=buffer.N, ptr=buffer.ptr, size=buffer.size,
                            data={k: v.detach().cpu().clone() for k, v in buffer.data.items()}),
                obs_history=learner.obs_hist.detach().cpu().clone(),
                bridge_ep_step=bridge.ep_step.detach().cpu().clone(),
                native_counters=dict(iteration=learner.iteration, world_updates=bridge.wm_updates,
                                     policy_updates=bridge.pi_updates, sim_steps=learner.sim_steps,
                                     wall_time=learner.wall_time),
                rng_snapshot=deepcopy(global_rng_snapshot),
                rng_ownership='D0_D7_global_and_private_streams_restore_then_one_new_episode',
                old_episode_history_injection_forbidden=True,
                exact_physics_or_native_stochastic_replay_claimed=False,
                integration_status='UNWIRED_SOURCE_CANDIDATE_REQUIRES_NEW_PUBLICATION_CONTRACT')


def mask_episode_restart_windows(original_mask, ep_steps):
    """Future replay mask hook; no extra sampling/RNG, preserve real done flags."""
    require(original_mask.shape == ep_steps.shape, 'Replay mask/ep-step shape')
    continuation = ep_steps[:, 1:] == ep_steps[:, :-1] + 1
    first = torch.ones((ep_steps.shape[0], 1), dtype=original_mask.dtype, device=original_mask.device)
    seam_mask = torch.cumprod(torch.cat((first, continuation.to(original_mask.dtype)), -1), -1)
    return original_mask * seam_mask
