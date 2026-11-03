"""Explicit embedded-teacher mean REFERENCE; stdlib-only at import.

Consumes an ALREADY strict-loaded FrozenA1MeanPolicy. No checkpoint reader,
model constructor, optimizer, SDK, RNG restoration or candidate fallback exists.
The original full mean/cache guards remain live even though residual is unused.
"""
from __future__ import annotations
import hashlib
import inspect
import json
from pathlib import Path

POLICY_VARIANT = 'ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1'
PURPOSE = 'FROZEN_ORIGINAL_EMBEDDED_TEACHER_REFERENCE_N80_V1'
RECEIPT_KIND = 'FROZEN_EMBEDDED_TEACHER_REFERENCE_RECEIPT_V1'
APPROVED_RSL = dict(module='rsl_rl.models.mlp_model', qualname='MLPModel', bytes=10334,
    SHA256='6219ebb3ed4df036dae7ff1c30d0fbb169eaaa659e44a659dd757a292124476b')
RSL_BINDING_KEY = 'rsl_rl.models.MLPModel'
FREEZE_EVIDENCE_KIND = 'PARENT_VERIFIED_ACTUAL_PRODUCER_TEACHER_STATE_GUARD_V1'


def need(value, message):
    if not value:
        raise ValueError(message)


def _sha(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _copy(value):
    return json.loads(json.dumps(value, allow_nan=False))


def _actual_model_source(teacher):
    """Small actual class-source read, NOT a checkpoint/data read."""
    cls = type(teacher)
    path = Path(inspect.getfile(cls)).resolve()
    need(path.suffix == '.py', 'actual RSL Python model source required')
    raw = path.read_bytes()
    return dict(module=cls.__module__, qualname=cls.__qualname__, path=str(path),
                bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def _teacher_identity(value):
    need(type(value) is dict and value.get('teacher_frozen') is True, 'original frozen teacher identity required')
    need(type(value.get('source_path')) is str and value['source_path'] and _sha(value.get('source_SHA'))
         and type(value.get('source_bytes')) is int and value['source_bytes'] > 0, 'original teacher byte provenance differs')
    return {k: value[k] for k in ('source_path', 'source_SHA', 'source_bytes', 'teacher_frozen')}


def _freeze_evidence(value, final, source_sha):
    # The parent supplies verified actual staged-producer/source provenance.
    # Static knowledge of the historical V4 source alone is deliberately NOT it.
    if value is None:
        return None
    need(type(value) is dict and value.get('kind') == FREEZE_EVIDENCE_KIND, 'explicit producer state-guard evidence required')
    for key in ('role', 'role_key', 'run_id'):
        need(value.get(key) == final[key], 'producer state-guard identity differs: ' + key)
    need(value.get('source_A1_SHA') == source_sha, 'producer state-guard checkpoint differs')
    worker = value.get('actual_staged_worker_source')
    need(type(worker) is dict and type(worker.get('path')) is str and worker['path']
         and type(worker.get('bytes')) is int and worker['bytes'] > 0 and _sha(worker.get('SHA256')),
         'actual staged producer worker pin required')
    for key in ('parent_verified_actual_staged_source', 'state_dict_snapshot_all_parameters_and_buffers',
                'torch_equal_before_each_complete_save', 'torch_equal_before_success_FINAL',
                'producer_success_FINAL_and_checkpoint_teacher_unchanged'):
        need(value.get(key) is True, 'producer state-guard evidence incomplete: ' + key)
    return _copy(value)


class EmbeddedTeacherMeanReference:
    """Direct public mean.pi.teacher, never mean.act / residual / teacher PT.

    tensor_dict_cls is the original worker's TensorDict class (not a new input
    projection). producer_final is the original runtime's already byte-attested
    A1 FINAL. Missing actual producer-guard evidence leaves qualification null.
    """
    def __init__(self, mean, *, tensor_dict_cls, producer_final,
                 expected_rsl_source=None, producer_freeze_evidence=None):
        self.mean, self.cache = mean, mean.cache
        self.t, self.device, self.num_envs = mean.t, mean.device, mean.num_envs
        self.TD = tensor_dict_cls
        need(callable(self.TD) and type(self.num_envs) is int and self.num_envs == 80, 'original TensorDict/fresh N80 required')
        need(mean.calls == 0 and mean._history is None and mean._failed is False, 'reference needs its own fresh unconsumed mean/cache')
        mean.assert_frozen()
        self.pi = self.teacher = mean.pi.teacher
        self.calls = 0; self._failed = False
        approved = APPROVED_RSL if expected_rsl_source is None else expected_rsl_source
        need(type(approved) is dict and all(type(approved.get(k)) is type(v) and approved[k] == v for k, v in APPROVED_RSL.items()),
             'explicit reviewed RSL source selection differs')
        declared = mean.source_bindings[RSL_BINDING_KEY]
        actual = _actual_model_source(self.teacher)
        for key, expected in APPROVED_RSL.items():
            need(type(declared.get(key)) is type(expected) and declared[key] == expected
                 and type(actual.get(key)) is type(expected) and actual[key] == expected,
                 'actual embedded-teacher RSL class/source differs: ' + key)
        self.actual_RSL_source = _copy(actual)
        final = producer_final
        need(type(final) is dict and final.get('kind') == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
             and final.get('passed_execution') is True and final.get('teacher_unchanged') is True, 'successful actual A1 producer FINAL required')
        for key in ('role', 'role_key', 'run_id'):
            need(final.get(key) == self.cache.expected[key] == self.cache.root[key], 'cache/producer identity differs: ' + key)
        cp = final.get('checkpoint')
        need(type(cp) is dict and cp.get('SHA') == self.cache.SHA and cp.get('bytes') == len(self.cache.raw)
             and cp.get('teacher_unchanged') is True, 'same full A1 checkpoint/teacher receipt required')
        self.bootstrap_teacher = _teacher_identity(self.cache.root['bootstrap_teacher'])
        need(self.bootstrap_teacher == _teacher_identity(final['teacher']) == _teacher_identity(cp['teacher_source']),
             'bootstrap teacher provenance differs')
        self.producer_identity = {k: final[k] for k in ('role', 'role_key', 'run_id')}
        self.producer_guard = _freeze_evidence(producer_freeze_evidence, final, self.cache.SHA)
        self.teacher_state_manifest = self._compare_full_teacher_state()
        self.assert_frozen()

    def _compare_full_teacher_state(self):
        saved = {k[len('teacher.'):]: v for k, v in self.cache.root['pi'].items() if k.startswith('teacher.')}
        current = self.teacher.state_dict()
        need(saved and set(current) == set(saved), 'full embedded teacher state keys differ (including norm/std/buffers)')
        parameters = dict(self.teacher.named_parameters())
        buffers = dict(self.teacher.named_buffers())
        need(set(parameters).isdisjoint(buffers) and set(current) <= set(parameters) | set(buffers), 'unreviewed teacher state extras or aliases')
        manifest = []
        for key, value in current.items():
            source = saved[key]
            need(tuple(value.shape) == tuple(source.shape) and value.dtype == source.dtype,
                 'full embedded teacher shape/dtype differs: ' + key)
            need(bool(self.t.isfinite(value).all()) and bool(self.t.isfinite(source).all()), 'nonfinite embedded teacher state: ' + key)
            need(bool(self.t.equal(value.detach().to('cpu'), source)), 'full embedded teacher value differs: ' + key)
            manifest.append(dict(name=key, shape=list(value.shape), dtype=str(value.dtype),
                                 kind='parameter' if key in parameters else 'buffer'))
        return manifest

    def assert_frozen(self):
        self.mean.assert_frozen()  # Whole pi params+buffers AND whole original CPU root.
        need(self.mean.pi.teacher is self.teacher and self.pi is self.teacher, 'public embedded teacher object rebound')
        need(self.mean.calls == 0 and self.mean._history is None and self.mean._failed is False,
             'reference scope executed candidate inference or consumed candidate history')
        return True

    def act(self, raw35, *, episode_start):
        need(not self._failed, 'reference inference sequence previously failed; end own eval scope')
        try:
            self.assert_frozen(); t = self.t
            need(t.is_tensor(raw35) and tuple(raw35.shape) == (80, 35) and raw35.device == self.device
                 and raw35.dtype == t.float32 and bool(t.isfinite(raw35).all()), 'original finite noisy/delayed float32 policy35 required')
            need(t.is_tensor(episode_start) and tuple(episode_start.shape) == (80,)
                 and episode_start.device == self.device and episode_start.dtype == t.bool,
                 'first/previous true term|trunc bool N80 required')
            if self.calls == 0:
                need(bool(episode_start.all()), 'first reference action requires all fresh episodes')
            with t.inference_mode():
                action = self.teacher(self.TD(dict(policy=raw35), batch_size=[80]), stochastic_output=False).clamp(-6., 6.)
                need(tuple(action.shape) == (80, 6) and action.dtype == t.float32 and action.device == self.device
                     and bool(t.isfinite(action).all()), 'nonfinite or wrong original teacher mean action')
            self.calls += 1
            self.assert_frozen()
            return action
        except BaseException:
            self._failed = True
            raise

    def receipt(self):
        self.assert_frozen()
        # Final/full receipt rechecks actual full values, not merely the source
        # declaration. No second model/root or normalization copy is constructed.
        need(self._compare_full_teacher_state() == self.teacher_state_manifest, 'teacher state manifest changed')
        cache = self.cache.receipt()
        need(cache['physical_byte_opens'] == cache['CPU_decodes'] == cache['SHA_calculations'] == 1
             and cache['mother_checkpoint_opens'] == 0, 'same single-read whole A1 cache required')
        return dict(kind=RECEIPT_KIND, policy_variant=POLICY_VARIANT, purpose=PURPOSE,
            **self.producer_identity, source_A1_SHA=cache['source_SHA'], source_A1_bytes=cache['source_bytes'],
            source_cache=cache, original_bootstrap_teacher=dict(self.bootstrap_teacher),
            actual_eval_RSL_source_binding=dict(self.actual_RSL_source),
            producer_teacher_state_guard=self.producer_guard,
            producer_teacher_weights_buffers_guard_verified=True if self.producer_guard is not None else None,
            full_teacher_state_keys_shapes_dtypes_values_equal_cached_pi=True,
            full_teacher_state_manifest=_copy(self.teacher_state_manifest),
            actor_calls=self.calls, actor_frozen=True, inference_failed=self._failed,
            effective_actor='public_FrozenA1MeanPolicy.pi.teacher', actor_input='original_noisy_delayed_policy35',
            candidate_mean_calls=self.mean.calls, residual_forward_calls=0,
            reference_history=None, reference_history_required=False, candidate_history_restored_or_used=False,
            boundary_mask='first_OR_previous_true_terminated_OR_true_truncated',
            action_clip=6., action_noise=0., normalization_updates=0, optimizer_updates=0,
            new_model_constructions=0, RNG_draws_or_restoration_by_adapter=0,
            independent_original_mother_PT_equivalence=None, actual_parent_wait_close_admission_proof=None,
            actual_paired_protocol_UID_match=None, relative_improvement=None, skill_pass_rate=None)


class EmbeddedTeacherReferenceCaller:
    """Use the already reviewed OriginalEpisodeBoundary, unchanged."""
    def __init__(self, reference, *, boundary):
        need(boundary.t is reference.t and boundary.device == reference.device and boundary.n == 80
             and boundary.actions == boundary.transitions == 0 and boundary.pending_step is False,
             'fresh original episode boundary with same Torch/device/N80 required')
        self.mean, self.boundary = reference, boundary

    def __call__(self, observation, stochastic_output=False):
        need(stochastic_output is False, 'explicit original deterministic teacher mean only')
        return self.mean.act(observation['policy'], episode_start=self.boundary.for_action())

    def observe_transition(self, terminated, truncated):
        self.boundary.after_original_step(terminated, truncated)

    def assert_frozen(self):
        return self.mean.assert_frozen()

    def receipt(self):
        return dict(self.mean.receipt(), original_episode_boundary=self.boundary.receipt())


def validate_reference_semantics(receipt, *, expected_role, expected_source_sha,
                                 expected_bootstrap_teacher_sha, expected_actor_calls):
    """Policy component gate only; original actual wait/close/locks still required."""
    need(type(receipt) is dict and receipt.get('kind') == RECEIPT_KIND
         and receipt.get('policy_variant') == POLICY_VARIANT and receipt.get('purpose') == PURPOSE,
         'explicit teacher-reference kind/variant/purpose required; never a candidate fallback')
    need(receipt.get('role') == expected_role and _sha(expected_source_sha) and receipt.get('source_A1_SHA') == expected_source_sha,
         'teacher-reference role/A1 checkpoint differs')
    need(_sha(expected_bootstrap_teacher_sha) and receipt.get('original_bootstrap_teacher', {}).get('source_SHA') == expected_bootstrap_teacher_sha,
         'teacher-reference bootstrap teacher source differs')
    need(type(expected_actor_calls) is int and expected_actor_calls > 0 and type(receipt.get('actor_calls')) is int
         and receipt['actor_calls'] == expected_actor_calls, 'actual original reference control count differs')
    for key in ('actor_frozen', 'full_teacher_state_keys_shapes_dtypes_values_equal_cached_pi',
                'producer_teacher_weights_buffers_guard_verified'):
        need(receipt.get(key) is True, 'reference policy evidence missing: ' + key)
    need(receipt.get('inference_failed') is False and receipt.get('effective_actor') == 'public_FrozenA1MeanPolicy.pi.teacher'
         and receipt.get('actor_input') == 'original_noisy_delayed_policy35' and receipt.get('action_clip') == 6., 'reference actor/input/clip differs')
    for key in ('candidate_mean_calls', 'residual_forward_calls', 'action_noise', 'normalization_updates', 'optimizer_updates',
                'new_model_constructions', 'RNG_draws_or_restoration_by_adapter'):
        need(type(receipt.get(key)) in (int, float) and type(receipt.get(key)) is not bool and receipt[key] == 0,
             'reference must not execute/update candidate or draw RNG: ' + key)
    source = receipt.get('source_cache', {})
    need(source.get('source_SHA') == expected_source_sha and source.get('whole_root_CPU_unchanged') is True
         and all(type(source.get(k)) is int and source[k] == 1 for k in ('physical_byte_opens', 'CPU_decodes', 'SHA_calculations'))
         and type(source.get('mother_checkpoint_opens')) is int and source['mother_checkpoint_opens'] == 0, 'reference single-read cache integrity differs')
    actual_rsl = receipt.get('actual_eval_RSL_source_binding', {})
    need(all(type(actual_rsl.get(k)) is type(v) and actual_rsl[k] == v for k, v in APPROVED_RSL.items()),
         'reference terminal actual RSL source differs')
    _freeze_evidence(receipt.get('producer_teacher_state_guard'), receipt, expected_source_sha)
    need(receipt.get('producer_teacher_state_guard') is not None, 'reference terminal producer state-guard evidence missing')
    boundary = receipt.get('original_episode_boundary', {})
    need(all(type(boundary.get(k)) is int and boundary[k] == expected_actor_calls for k in ('actions', 'original_step_transitions'))
         and boundary.get('pending_original_step') is False and boundary.get('synthetic_episode_mask') is False,
         'original reference action/transition boundary differs')
    return dict(passed_reference_policy_semantics=True, qualified_reference_execution=None,
                actual_wait_close_admission_must_be_checked_by_original_owner=True,
                actual_paired_protocol_UID_match=None, relative_improvement=None)
