"""NEW source-only N80 A1 integration. No SDK/Torch/model/resource opens on import.

Future admission is owned by the original finite/private-EX parent. This module
never acquires locks, edits a budget, starts a process, restores an environment,
or executes a training/model-migration fallback. Source tests use only fixtures.
"""
from pathlib import Path
import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import sys
import time
import traceback

KIND = 'N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'
INTEGRATION = 'A1_FROZEN_RAW35_N80_INTEGRATION_SOURCE_V2'
ROLES = ('E3', 'W35', 'CURB_INDEPENDENT113', 'CURB_PROTECTED878',
         'SLOPE135', 'SLOPE_INDEPENDENT50', 'E0', 'E2')
CONTROLS = dict(E0=1000, E2=1200, E3=160, W35=1600, CURB_PROTECTED878=750,
                CURB_INDEPENDENT113=750, SLOPE135=750, SLOPE_INDEPENDENT50=1000)
COUNT_FIELDS = ('policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps',
                'pi_unverified_steps', 'pi_skipped_nonfinite', 'pi_skipped_zero',
                'wm_optimizer_steps', 'aux_optimizer_steps', 'critic_optimizer_steps')
USD = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
HELPER_PIN = (19226, '1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21')
POSE_PIN = (18161, '7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f')
APP_PIN = (27769, '3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39')
POSE_VERSION = 'POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1'
POSE_TIMING = 'after_env_construction_before_original_single_explicit_reset'
APPROVED_RSL_MODEL_SOURCE = dict(SHA256='6219ebb3ed4df036dae7ff1c30d0fbb169eaaa659e44a659dd757a292124476b',
                                 bytes=10334, module='rsl_rl.models.mlp_model', qualname='MLPModel')
APPROVED_REFERENCE_PROVENANCE = dict(
    kind='PARENT_APPROVED_ACTUAL_CPU_REFERENCE_SOURCE_NOT_NATIVE_EVAL_OBSERVATION_V2',
    parent_agent_selection_message='m01585',
    selected_by='executing_parent_agent_not_a_new_human_approval_or_runtime_claim',
    source_selection_report='mod4v1_supermimic_bptt_20261102/reports/EVAL_RSL_REFERENCE_SOURCE_SELECTION_V1.json',
    source_report='mod4v1_supermimic_bptt_20261102/reports/A1_FROZEN_MEAN_POLICY_CPU_V1.json',
    report_bytes=8696, report_SHA256='0329771e37873d17bf3f806b9caa27b0ef669fec3fbf3e334ff28924094925f0',
    evidence_route="receipt.source_bindings['rsl_rl.models.MLPModel']",
    observed_CPU_source_path='/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib/python3.12/site-packages/rsl_rl/models/mlp_model.py',
    source_kind='OWN_SYNTHETIC_CPU_TORCH_NOT_ORIGINAL_CHECKPOINT_OR_NATIVE_EVAL',
    actual_CPU_mean_controls=4, actual_CPU_num_envs=80, max_reference_error=0.0,
    original_native_GPU_source_binding_observed=None, actual_frozen_evaluation=None,
    requires_actual_eval_class_and_bytes_SHA_match_before_first_action=True)
CONTEXT = {}


class IntegrationError(ValueError):
    pass


def need(value, message):
    if not value:
        raise IntegrationError(message)


def _sha(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _metadata(path, maximum=262144):
    # Metadata only. Never used for any checkpoint/raw/NPZ/budget file.
    path = Path(path)
    need(path.suffix.lower() == '.json' and 'budget' not in path.name.lower(), 'bounded JSON metadata only')
    with path.open('rb') as stream:
        raw = stream.read(maximum + 1)
    need(len(raw) <= maximum, 'JSON metadata exceeds bounded source contract')
    value = json.loads(raw)
    need(type(value) is dict, 'metadata mapping required')
    return value, raw


def put_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.partial')
    with temporary.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _pinned_module(name, pin):
    need(type(name) is str and '.' not in name, 'reviewed flat worker source name required')
    spec = importlib.util.find_spec(name)
    need(spec is not None and type(spec.origin) is str, 'reviewed source module is missing: ' + name)
    source = Path(spec.origin).resolve()
    need(source.suffix == '.py', 'reviewed source module required: ' + name)
    raw = source.read_bytes()  # Small Python source, never checkpoint bytes.
    need((len(raw), hashlib.sha256(raw).hexdigest()) == pin, 'integration source pin differs: ' + name)
    module = importlib.import_module(name)
    need(Path(module.__file__).resolve() == source, 'actual integration module origin differs: ' + name)
    return module


def validate_paired_protocol(protocol):
    need(type(protocol) is dict and protocol.get('kind') == 'PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', 'paired reset protocol required')
    reference, candidate = protocol.get('reference_planned_protocol'), protocol.get('candidate_planned_protocol')
    expected = dict(pose_source_SHA=POSE_PIN[1], pose_source_bytes=POSE_PIN[0],
                    pose_source_version=POSE_VERSION, install_timing=POSE_TIMING,
                    seed=20260928, num_envs=80, explicit_original_reset_count=1,
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


def _producer_descriptor(value, role):
    need(type(value) is dict, 'explicit successful A1 producer metadata required')
    job = Path(value.get('own_job_root', '')).resolve()
    final_path = Path(value.get('FINAL_path', '')).resolve()
    need(final_path == job / 'production' / 'FINAL.json', 'producer FINAL must be its own production metadata')
    need(type(value.get('run_id')) is str and value['run_id'] and type(value.get('role_key')) is str and value['role_key'],
         'producer role key/run id required')
    final = value.get('FINAL')
    need(type(final) is dict and final.get('kind') == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
         and final.get('passed_execution') is True and final.get('teacher_unchanged') is True,
         'actual successful A1 FINAL required; startup/count inference is not a producer FINAL')
    need(final.get('role') == role and final.get('role_key') == value['role_key'] and final.get('run_id') == value['run_id'],
         'producer identity mismatch')
    need(final.get('actor_view') == 'raw35_legacy_held_aux_v1' and final.get('algorithm_family') == 'a1_raw35_legacy_v1'
         and final.get('algorithm_variant') in ('A1_RAW35_FRESH', 'A1_RAW35_RESUME'), 'only admitted A1 legacy raw35 producer')
    need(_sha(value.get('FINAL_SHA')) and type(value.get('FINAL_bytes')) is int and value['FINAL_bytes'] > 0,
         'actual bounded FINAL bytes/SHA required')
    checkpoint = final.get('checkpoint')
    need(type(checkpoint) is dict and checkpoint.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved') is True,
         'whole own full checkpoint receipt required, not actor-only')
    need(_sha(checkpoint.get('SHA')) and type(checkpoint.get('bytes')) is int and checkpoint['bytes'] > 0,
         'producer checkpoint byte identity missing')
    path = Path(checkpoint.get('path', '')).resolve()
    need(path.is_relative_to(job / 'production' / 'checkpoints') and path.name.endswith('_complete.pt'), 'own A1 full-save path only')
    need(final.get('counts') == checkpoint.get('counts'), 'FINAL/checkpoint counters differ')
    need(type(final.get('counts')) is dict and set(final['counts']) == set(COUNT_FIELDS), 'all nine named producer counters required')
    need(all(type(v) is int and v >= 0 for v in final['counts'].values()), 'producer counters must be actual nonnegative integers')
    need(final['counts']['pi_bptt_optimizer_steps'] <= final['counts']['pi_optimizer_steps'] <= final['counts']['policy_attempts'], 'producer count ordering differs')
    need(type(final.get('actual_BPTT_policy_steps')) is int and final['actual_BPTT_policy_steps'] == final['counts']['pi_bptt_optimizer_steps'], 'actual BPTT receipt differs')
    need(checkpoint.get('teacher_unchanged') is True, 'actual saved teacher integrity receipt required')
    return value


def _validate_approved_reference(task):
    selected = task.get('approved_RSL_model_source')
    need(type(selected) is dict and selected.get('SHA256') == APPROVED_RSL_MODEL_SOURCE['SHA256']
         and type(selected.get('bytes')) is int and selected['bytes'] == APPROVED_RSL_MODEL_SOURCE['bytes'],
         'parent-selected actual CPU reference source bytes/SHA required; no source fallback')
    for key in ('module', 'qualname'):
        need(selected.get(key, APPROVED_RSL_MODEL_SOURCE[key]) == APPROVED_RSL_MODEL_SOURCE[key], 'selected reference exact class differs')
    need(task.get('approved_reference_provenance') == APPROVED_REFERENCE_PROVENANCE,
         'CPU/reference selection provenance must not become a human approval or native-GPU observation claim')
    return selected


def validate_group_task(task, role, group_root, case, contracts=None, *, environment=None, fd_check=None, now=None):
    environment = os.environ if environment is None else environment
    now = time.time if now is None else now
    need(role in ROLES and task.get('role') == role and task.get('kind') == task.get('purpose') == KIND, 'eight original roles excluding H1')
    need(task.get('integration') == INTEGRATION, 'explicit new integration purpose required')
    for key, value in dict(num_envs=80, seed=20260928, optimizer_updates=0, fresh_fullDR_cohort=True,
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
        (fd_check or os.fstat)(fd)  # Existence only: no worker flock, acquire, or release.
    need(Path(case).resolve().is_relative_to(Path(group_root).resolve()), 'own original eval group scope required')
    need(type(task.get('absolute_worker_deadline_epoch')) in (float, int) and task['absolute_worker_deadline_epoch'] > now(), 'original finite worker deadline elapsed')
    need(type(task.get('eval_members')) is list and len(task['eval_members']) == 8 and set(task['eval_members']) == set(ROLES), 'one original parent must own all eight members')
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
                  seed=20260928, optimizer_updates=0, fresh_fullDR_cohort=True,
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
    return result


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


def unresolved_evidence():
    return dict(UID_identity_alignment=None, root_getter_backend_point_clock_binding=None,
                original_reference_cache_available=None, E0_original_binary_predicate=None,
                SLOPE_INDEPENDENT50_original_binary_predicate=None, paired_reference_effect=None,
                reward_effect_identification=None, skill_pass_rate=None,
                actual_parent_cost_close_receipt=None, original_accepted_UID_reference_snapshot=None)


def _read_actual_final(task):
    descriptor = _producer_descriptor(task['a1_producer'], task['role'])
    actual, raw = _metadata(descriptor['FINAL_path'])
    need(len(raw) == descriptor['FINAL_bytes'] and hashlib.sha256(raw).hexdigest() == descriptor['FINAL_SHA'], 'actual producer FINAL metadata bytes differ')
    need(actual == descriptor['FINAL'], 'actual producer FINAL differs from admitted plan')
    return actual


class OriginalEpisodeBoundary:
    """One action -> one original env.step -> next first|previous(term|trunc)."""
    def __init__(self, torch_module, device, n=80):
        need(type(n) is int and n == 80, 'fresh independent N80 only')
        self.t, self.device, self.n = torch_module, device, n
        self.next_start = self.t.ones(n, dtype=self.t.bool, device=device)
        self.pending_step = False; self.actions = 0; self.transitions = 0
    def for_action(self):
        need(not self.pending_step, 'original step/true term+trunc flags missing before next action')
        self.pending_step = True; self.actions += 1
        return self.next_start
    def after_original_step(self, terminated, truncated):
        need(self.pending_step, 'original termination supplied without a corresponding action')
        for value in (terminated, truncated):
            need(self.t.is_tensor(value) and tuple(value.shape) == (self.n,) and value.dtype == self.t.bool
                 and value.device == self.device, 'separate original bool term/trunc N80 required')
        self.next_start = (terminated | truncated).clone()
        self.pending_step = False; self.transitions += 1
    def receipt(self):
        return dict(actions=self.actions, original_step_transitions=self.transitions,
                    first_action_all_fresh=True, mask='first_OR_previous_true_terminated_OR_true_truncated',
                    pending_original_step=self.pending_step, synthetic_episode_mask=False)


class A1PolicyCaller:
    def __init__(self, mean):
        self.mean = mean
        self.boundary = OriginalEpisodeBoundary(mean.t, mean.device)
    def __call__(self, observation, stochastic_output=False):
        need(stochastic_output is False, 'original deterministic mean only')
        return self.mean.act(observation['policy'], episode_start=self.boundary.for_action())
    def observe_transition(self, terminated, truncated):
        self.boundary.after_original_step(terminated, truncated)
    def assert_frozen(self):
        return self.mean.assert_frozen()
    def receipt(self):
        return dict(self.mean.receipt(), original_episode_boundary=self.boundary.receipt(),
                    paired_reset_protocol=paired_protocol_receipt(), unresolved_evidence=unresolved_evidence())


class A1CheckpointAdapter:
    def __init__(self, torch_module, task):
        final = _read_actual_final(task)
        helper = _pinned_module('frozen_a1_raw35_v1', HELPER_PIN)
        producer = task['a1_producer']
        self.cache = helper.FrozenA1CheckpointCache(final, own_job_root=producer['own_job_root'],
                     role=task['role'], role_key=producer['role_key'], run_id=producer['run_id'],
                     asset_SHA=task['asset_SHA'], contract_SHA=task['contract_SHA'])
        need(self.cache.t is torch_module, 'actual cache/worker Torch binding differs')
        self.t = torch_module; self.SHA = self.source_SHA = self.cache.SHA
        self.task = task; self.caller = None
    def actor(self, device, n=80):
        need(self.caller is None and n == 80, 'one frozen N80 pi per whole CPU cache')
        approved = _validate_approved_reference(self.task)
        mean = self.cache.build_mean_policy(device, num_envs=80)
        actual = mean.source_bindings['rsl_rl.models.MLPModel']
        need(actual.get('SHA256') == approved['SHA256'] and actual.get('bytes') == approved['bytes']
             and actual.get('module') == APPROVED_RSL_MODEL_SOURCE['module']
             and actual.get('qualname') == APPROVED_RSL_MODEL_SOURCE['qualname'],
             'actual evaluator RSL class/source differs from parent-selected CPU reference; no fallback')
        self.caller = A1PolicyCaller(mean)
        return self.caller
    def check(self):
        self.cache.assert_unchanged()
        if self.caller is not None:
            self.caller.assert_frozen()
        return True
    def assert_entire_root_unchanged(self):
        return self.check()
    def check_actor(self, actor):
        need(self.caller is not None and (actor is self.caller or actor is self.caller.mean.pi), 'only the whole own A1 pi is live')
        return self.check()
    def receipt(self):
        result = dict(self.cache.receipt(), integration=INTEGRATION,
                      policy_family='own_A1_teacher_plus_trained_residual', old_RSL_actor_checkpoint_loader_used=False,
                      approved_reference_provenance=dict(self.task['approved_reference_provenance']),
                      approved_RSL_model_source=dict(self.task['approved_RSL_model_source']),
                      actual_eval_RSL_source_binding=(dict(self.caller.mean.source_bindings['rsl_rl.models.MLPModel']) if self.caller is not None else None),
                      admitted_producer_run_id=self.task['a1_producer']['run_id'],
                      actual_BPTT_policy_steps=self.task['a1_producer']['FINAL']['actual_BPTT_policy_steps'])
        if self.caller is not None:
            result['frozen_mean'] = self.caller.receipt()
        return result


class OriginalA1NoResetDecisionVec:
    def __init__(self, env, cache, torch_module, TensorDict, tensor):
        self.env = self.unwrapped = env; self.cache = cache
        self.t, self.TD, self.tensor = torch_module, TensorDict, tensor
        self.num_envs, self.device = env.num_envs, env.device
        need(self.num_envs == 80, 'independent N80 environment required')
        self.caller = cache.actor(self.device)
        self.actor_calls = 0; self.command_error = 0.; self.env_reset_calls = 0
    def get_observations(self):
        original = self.env.observation_manager.compute()  # EXACT original once/control call.
        need(tuple(original['policy'].shape) == (80, 35) and tuple(original['critic'].shape) == (80, 38), 'original N80 observation layout differs')
        self.command_error = max(self.command_error, float((original['policy'][:, :3] - self.env.command_manager.get_term('twist').command).abs().max()))
        need(self.command_error <= 1e-6, 'original known-command prefix differs')
        return self.TD(dict(policy=original['policy']), batch_size=[80])
    def policy(self, observation):
        self.actor_calls += 1
        return self.caller(observation, stochastic_output=False)
    def step(self, action):
        observation, reward, terminated, truncated, extra = self.env.step(self.t.clamp(action, -6., 6.))
        self.caller.observe_transition(terminated, truncated)
        return observation, reward, terminated | truncated, extra
    def audit(self):
        return dict(integration=INTEGRATION, actor_calls=self.actor_calls, actual_command_error=self.command_error,
                    extra_explicit_env_resets=0, actor_receives='original_noisy_delayed_policy35_only',
                    critic_DR_UID_actor_input=False, original_episode_boundary=self.caller.boundary.receipt())


def build_a1_original_vec(env, cache, torch_module, tensor, holder):
    from tensordict import TensorDict
    vec = OriginalA1NoResetDecisionVec(env, cache, torch_module, TensorDict, tensor)
    holder.update(actor=cache.caller.mean.pi, vec=vec, cache=cache)
    return vec, vec.policy, vec


def task_args():
    parser = argparse.ArgumentParser(); parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--group-root', type=Path, required=True); args = parser.parse_args()
    task, _ = _metadata(args.task)
    validate_group_task(task, task.get('role'), args.group_root, args.task.parent)
    configure_candidate_runtime(task, args.task.parent)
    return task, args.task.parent, args.group_root


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


def _validate_returned_app_binding(binding, helper):
    """Same exact source/class evidence for the reviewed non-fast returned path."""
    need(type(binding) is dict and binding.get('fast_shutdown') is False, 'exact returned non-fast binding required')
    module = binding.get('actual_module')
    need(module in ('isaacsim.simulation_app.simulation_app', 'simulation_app.simulation_app'), 'published original App export required')
    name = module + '.SimulationApp'
    expected = dict(kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5', actual_class=name,
                    actual_MRO=[name, 'builtins.object'], close_owner=name, actual_module=module,
                    actual_type_name='SimulationApp', close_module=module, close_qualname='SimulationApp.close',
                    source_SHA256='6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903',
                    source_bytes=48933, close_firstlineno=848, exact_class_verified=True,
                    method_self_is_application=True, method_function_is_MRO_definition=True,
                    fast_shutdown=False, no_extra_SDK_getters=True,
                    source_code_version='V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES',
                    helper_source_bytes=APP_PIN[0], helper_source_SHA256=APP_PIN[1])
    for key, value in expected.items():
        need(type(binding.get(key)) is type(value) and binding[key] == value, 'returned original App binding differs: ' + key)
    paths = [binding.get(k) for k in ('source_file', 'module_file', 'code_filename')]
    need(all(type(p) is str and Path(p).is_absolute() and Path(p).suffix == '.py' for p in paths)
         and paths[0] == paths[1] == paths[2], 'returned original App source paths differ')
    need(type(binding.get('helper_source_file')) is str
         and Path(binding['helper_source_file']).resolve() == Path(helper.__file__).resolve(), 'actual returned helper source path differs')
    return True


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
        producer = _producer_descriptor(role_entry.get('a1_producer'), role)
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
        mean = source.get('frozen_mean')
        need(type(mean) is dict and mean.get('actor_frozen') is True and mean.get('actor_calls') == CONTROLS[role]
             and mean.get('normalization_updates') == mean.get('optimizer_updates') == 0,
             'frozen own pi/exact control inference receipt required')
        paired = mean.get('paired_reset_protocol')
        need(type(paired) is dict and paired.get('candidate_pose_installed') is True
             and paired.get('protocol') == validate_paired_protocol(role_entry.get('paired_reset_protocol')),
             'candidate and planned reference must retain the same reviewed reset/cache protocol')
        boundary = mean['original_episode_boundary']
        need(boundary.get('actions') == boundary.get('original_step_transitions') == CONTROLS[role]
             and boundary.get('pending_original_step') is False, 'original first/true term/trunc sequence incomplete')
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
    return dict(kind='ACTUAL_WAITED_A1_N80_EVAL_SEMANTIC_V2', role=role, group_id=group_id,
                actual_waited_returncode=returncode, passed_execution=not reasons, original_error=bool(reasons), reasons=reasons,
                original_fast_close_expected_nonreturn_accepted=bool(not reasons and intent is not None),
                actual_resource_admission_or_parent_wait_proof='CALLER_ORIGINAL_P_WAIT_REQUIRED_NOT_CREATED_HERE',
                UID_alignment=None, reference_cache_match=None, paired_reward_effect=None)
