"""Native-capable ZERO_UPDATE tanh actor; capability is NOT actual admission or execution.

The full original A1 cache is passed in fresh. Only its ONE actor build is claimed.
Inherited mean.act keeps the exact raw35/history/command/real-boundary behavior.
This effective actor is explicitly NOT the old unbounded A1 mean, or training.
"""
from __future__ import annotations
import hashlib
import inspect
import math
from pathlib import Path
import re
import frozen_a1_raw35_v1 as h

VARIANT = 'A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'
PURPOSE = 'FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1'
KIND = 'FROZEN_ZERO_UPDATE_BOUND_ONLY_NATIVE_MEAN_RECEIPT_V1'
NATIVE_ENABLED = True  # Selected-route CAPABILITY; actual external admission/execution is never inferred.
BASE_PIN = (19226, '1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21')
BOUNDARY_PIN = (37927, '7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')
APPROVED_RSL = dict(module='rsl_rl.models.mlp_model', qualname='MLPModel', bytes=10334,
    SHA256='6219ebb3ed4df036dae7ff1c30d0fbb169eaaa659e44a659dd757a292124476b')
QUALIFIED_CONTAINERS = {
    'E3': 'a4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127',
    'W35': 'b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff',
}


def _source_binding():
    path = Path(__file__).resolve(); raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest(),
                module=__name__, purpose=PURPOSE, native_enabled=NATIVE_ENABLED)


def _verify_original_helper():
    path = Path(h.__file__).resolve(); raw = path.read_bytes()
    h.need((len(raw), hashlib.sha256(raw).hexdigest()) == BASE_PIN, 'original full A1 cache source pin differs')
    return dict(path=str(path), bytes=len(raw), SHA256=BASE_PIN[1])


class ReadOnlyActionStatistics:
    """Optional scalar reductions ONLY on this same already-computed forward.

    Host scalar reads may synchronize a GPU and affect walltime. No tensor/RNG/
    sensor/history/physics writes. No timing is labelled simulated time.
    """
    MAX_KEYS = ('raw_delta_abs_max', 'legacy_preclip_residual_abs_max', 'bound_preclip_residual_abs_max',
                'probe_vs_clipped_teacher_abs_max', 'probe_vs_legacy_action_abs_max')
    def __init__(self, enabled):
        h.need(type(enabled) is bool, 'diagnostic flag must be an actual bool')
        self.enabled = enabled; self.calls = 0; self.components = 0
        self.maximum = {k: None for k in self.MAX_KEYS}; self.nonfinite_keys = set()
        self.legacy_clip_hits = self.probe_clip_hits = 0
        self.action_abs_difference_sum = 0.
    def _scalar(self, value, name):
        number = float(value.item())
        if not math.isfinite(number): self.nonfinite_keys.add(name); return None
        return number
    def record(self, base, delta, bounded_delta, probe_preclip, action, scale):
        self.calls += 1
        if not self.enabled: return
        legacy_preclip = base + scale * delta
        legacy_action = legacy_preclip.clamp(-6., 6.)
        diff = (action - legacy_action).abs()
        values = dict(raw_delta_abs_max=delta.abs().max(),
            legacy_preclip_residual_abs_max=(scale * delta).abs().max(),
            bound_preclip_residual_abs_max=(scale * bounded_delta).abs().max(),
            probe_vs_clipped_teacher_abs_max=(action - base.clamp(-6., 6.)).abs().max(),
            probe_vs_legacy_action_abs_max=diff.max())
        for key, value in values.items():
            number = self._scalar(value, key)
            if number is not None:
                self.maximum[key] = number if self.maximum[key] is None else max(self.maximum[key], number)
        self.components += action.numel()
        self.legacy_clip_hits += int((legacy_preclip.abs() > 6.).sum().item())
        self.probe_clip_hits += int((probe_preclip.abs() > 6.).sum().item())
        number = self._scalar(diff.sum(), 'probe_vs_legacy_action_abs_difference_sum')
        if number is not None: self.action_abs_difference_sum += number
    def receipt(self):
        maxima = {k: (None if k in self.nonfinite_keys else self.maximum[k]) for k in self.MAX_KEYS}
        measured = self.enabled and self.calls > 0
        return dict(enabled=self.enabled, forward_calls=self.calls,
            action_components=self.components if measured else None, maxima=maxima,
            legacy_total_clip_hits=self.legacy_clip_hits if measured else None,
            probe_total_clip_hits=self.probe_clip_hits if measured else None,
            total_clip_hit_definition='abs(already_computed_preclip_action)>6',
            probe_vs_legacy_action_abs_difference_sum=(self.action_abs_difference_sum
                if measured and 'probe_vs_legacy_action_abs_difference_sum' not in self.nonfinite_keys else None),
            nonfinite_diagnostic_keys=sorted(self.nonfinite_keys),
            extra_teacher_or_residual_forwards=0, extra_observations_RNG_or_physics=0,
            host_scalar_synchronization_possible=self.enabled,
            walltime_is_not_simulation_time=True, native_skill_or_causal_effect=None)


def make_bound_only_wrapper(original_wrapper, tensor_dict_cls, tensor_module, statistics):
    """The original ctor is INHERITED, hence still runs BEFORE strict load.

    No parameters/buffers/submodules are added, no existing actor is reconstructed,
    no hooks or global/private-runtime monkeypatches are installed.
    """
    class BoundTeacherResidualPolicy(original_wrapper):
        def forward(self, history, goal):
            obs = history[..., -1, self.offset:self.offset + 35]
            td = tensor_dict_cls(dict(policy=obs), batch_size=list(obs.shape[:-1]))
            base = self.teacher(td, stochastic_output=False)
            delta = self.residual(history, goal)
            bounded_delta = tensor_module.tanh(delta)
            preclip = base + self.scale * bounded_delta
            action = preclip.clamp(-6., 6.)
            statistics.record(base, delta, bounded_delta, preclip, action, self.scale)
            return action
    return BoundTeacherResidualPolicy


class BoundOnlyFrozenMean(h.FrozenA1MeanPolicy):
    def __init__(self, cache, pi, modules, device, num_envs, *, statistics, binding, original_wrapper, synthetic_only):
        self._probe_statistics = statistics
        self._probe_forward = type(pi).forward
        self._probe_class = type(pi)
        self._probe_original_constructor = original_wrapper.__init__
        self._probe_binding = binding
        self._probe_synthetic = synthetic_only
        # Original complete parameter/buffer/cache snapshot and initialization.
        super().__init__(cache, pi, modules, device, num_envs)
    def assert_frozen(self):
        h.need(type(self.pi) is self._probe_class and type(self.pi).forward is self._probe_forward,
               'bound-only effective forward/class changed')
        h.need(type(self.pi).__init__ is self._probe_original_constructor,
               'original pre-strict-load wrapper constructor changed')
        h.need('forward' not in self.pi.__dict__, 'instance forward override is not the reviewed bound probe')
        h.need(self._probe_statistics.calls == self.calls, 'one same-forward statistics event per action required')
        return super().assert_frozen()
    # act is deliberately NOT overridden: exact original raw35/history/noise/goal.
    def receipt(self):
        value = super().receipt()
        value.update(kind=KIND, purpose=PURPOSE, policy_variant=VARIANT,
            algorithm_family='zero_update_postprocess_bound_probe_not_training',
            container_algorithm_family=self.cache.root['algorithm_family'],
            container_algorithm_variant=self.cache.root['algorithm_variant'],
            container_algorithm_actor_view=self.cache.root['actor_view'],
            container_checkpoint_SHA=self.cache.SHA,
            container_role=self.cache.expected['role'],
            original_bootstrap_teacher=dict(self.cache.root['bootstrap_teacher']),
            source_container_is_unmodified_original_A1=True,
            effective_forward='clip(teacher(raw35,mean)+0.05*tanh(residual(history10,knowncmd3)),-6,6)',
            inherited_original_mean_act=True, inherited_original_constructor_before_strict_load=True,
            state_dict_keys_shapes_values_norms_and_teacher_loaded_strictly=True,
            effective_wrapper=dict(module=type(self.pi).__module__, qualname=type(self.pi).__qualname__,
                                   source=dict(self._probe_binding)),
            bound_probe_action_statistics=self._probe_statistics.receipt(),
            probe_optimizer_updates=dict(pi=0, wm=0, aux=0, critic=0),
            probe_BPTT_policy_steps=0, probe_training_updates=0,
            source_producer_counts_are_historical_not_probe_updates=True,
            preclip_residual_component_bound_real_arithmetic=.05,
            postclip_vs_clipped_teacher_component_bound_real_arithmetic=.05,
            NOT_a_point05_bound_vs_old_unbounded_candidate=True,
            synthetic_only=self._probe_synthetic, native_enabled=NATIVE_ENABLED,
            qualified_native_execution=None, relative_or_causal_skill_effect=None,
            measured_skill_pass_rate=None, eligible_for_promotion=False)
        return value


def build_bound_only_mean_policy(cache, device, num_envs=80, *, expected_container_sha=None,
                                 collect_action_statistics=False, synthetic_only=False):
    """Consume ONE fresh original cache, not an already-built mean; no rearming.

    Production source binds the TWO actual qualified A1 containers. Synthetic-only
    CPU fixtures must pass their own explicit new SHA and remain non-native.
    Failure after claiming the build consumes the cache too: never fall back.
    """
    _verify_original_helper()
    h.need(isinstance(cache, h.FrozenA1CheckpointCache), 'fresh original whole A1 cache required')
    h.need(type(synthetic_only) is bool and type(collect_action_statistics) is bool, 'actual bool probe flags required')
    role = cache.expected['role']; h.need(role in QUALIFIED_CONTAINERS, 'bound-only source scope is E3/W35')
    if synthetic_only:
        h.need(type(expected_container_sha) is str and re.fullmatch('[0-9a-f]{64}', expected_container_sha),
               'own new synthetic container SHA required')
    else:
        h.need(expected_container_sha in (None, QUALIFIED_CONTAINERS[role]), 'probe must use the actual qualified original A1 container')
        expected_container_sha = QUALIFIED_CONTAINERS[role]
    h.need(cache.SHA == expected_container_sha, 'bound probe source container SHA differs')
    h.need(not cache._built and type(num_envs) is int and num_envs == 80, 'one fresh N80 inference policy per cache')
    # This claim is NEVER cleared, including on an error. No cache rearm/fallback.
    cache._built = True
    modules = h._runtime_modules(); t = modules.t
    h.need(t is cache.t, 'decode/build Torch binding differs')
    actual_rsl = modules.source_bindings['rsl_rl.models.MLPModel']
    h.need(all(actual_rsl.get(k) == v for k, v in APPROVED_RSL.items()), 'bound probe requires original approved RSL6219 source')
    statistics = ReadOnlyActionStatistics(collect_action_statistics)
    original_wrapper = modules.Wrapper
    wrapper = make_bound_only_wrapper(original_wrapper, modules.TD, t, statistics)
    binding = _source_binding()
    cache.assert_unchanged()
    # Original build algorithm copied locally, with ONLY the effective wrapper and
    # mean receipt class changed. Constructor zeroing precedes the full strict load.
    with t.inference_mode(False), t.no_grad(), t.random.fork_rng(devices=[]):
        obs = modules.TD(dict(policy=t.zeros(2, 35), critic=t.zeros(2, 38)), batch_size=[2])
        distribution = dict(class_name='rsl_rl.modules.distribution:GaussianDistribution', init_std=1., std_type='scalar')
        teacher = modules.MLP(obs, dict(actor=['policy'], critic=['critic']), 'actor', 6, [256, 128, 64], 'elu', distribution_cfg=distribution)
        residual = modules.Policy(35, 3, hist=cache.cfg['hist'], z_dim=cache.cfg['z_dim'], num_joints=6, hidden=cache.cfg['policy_hidden'])
        pi = wrapper(residual, teacher, 0, scale=.05)
        current, saved = pi.state_dict(), cache.root['pi']
        h.need(set(current) == set(saved), 'strict A1 pi state keys differ')
        for key, value in current.items():
            h.need(tuple(value.shape) == tuple(saved[key].shape) and value.dtype == saved[key].dtype, 'pi shape/dtype differs: ' + key)
            h.need(bool(t.isfinite(saved[key]).all()), 'nonfinite saved pi: ' + key)
        for prefix in ('residual.obs_norm.', 'residual.goal_norm.'):
            h.need(bool((saved[prefix + 'var'] >= 0).all()) and bool((saved[prefix + 'count'] >= 0).all()), 'normalization variance/count must be nonnegative')
        pi.load_state_dict(saved, strict=True, assign=False)
        for key, value in pi.state_dict().items():
            h.need(t.equal(value, saved[key]), 'strict-loaded pi value differs: ' + key)
        pi.eval().requires_grad_(False)
        pi.to(device)
    return BoundOnlyFrozenMean(cache, pi, modules, device, num_envs, statistics=statistics,
        binding=binding, original_wrapper=original_wrapper, synthetic_only=synthetic_only)


class BoundOnlyPolicyCaller:
    """Reuse an ORIGINAL OriginalEpisodeBoundary instance supplied by the route."""
    def __init__(self, mean, *, boundary):
        h.need(isinstance(mean, BoundOnlyFrozenMean), 'only explicit bound-probe mean accepted')
        boundary_class = type(boundary); path = Path(inspect.getfile(boundary_class)).resolve(); raw = path.read_bytes()
        h.need(boundary_class.__qualname__ == 'OriginalEpisodeBoundary'
               and (len(raw), hashlib.sha256(raw).hexdigest()) == BOUNDARY_PIN,
               'original unchanged episode-boundary class/source required')
        self.boundary_source = dict(path=str(path), bytes=len(raw), SHA256=BOUNDARY_PIN[1])
        h.need(boundary.t is mean.t and boundary.device == mean.device and boundary.n == 80,
               'original N80 boundary/device binding differs')
        h.need(boundary.actions == boundary.transitions == 0 and boundary.pending_step is False,
               'fresh original boundary required')
        self.mean, self.boundary = mean, boundary
    def __call__(self, observation, stochastic_output=False):
        h.need(stochastic_output is False, 'bound probe is deterministic mean only')
        return self.mean.act(observation['policy'], episode_start=self.boundary.for_action())
    def observe_transition(self, terminated, truncated):
        self.boundary.after_original_step(terminated, truncated)
    def assert_frozen(self): return self.mean.assert_frozen()
    def receipt(self):
        return dict(self.mean.receipt(), original_episode_boundary=self.boundary.receipt(),
                    original_episode_boundary_source=dict(self.boundary_source))


def validate_bound_probe_receipt(value, *, expected_role, expected_source_sha, expected_actor_calls):
    """Policy-component gate only; NEVER an admission/wait/close/skill gate."""
    h.need(type(value) is dict and value.get('kind') == KIND and value.get('purpose') == PURPOSE
           and value.get('policy_variant') == VARIANT, 'explicit ZERO_UPDATE bound-probe semantics required')
    h.need(value.get('container_role') == expected_role and expected_role in QUALIFIED_CONTAINERS,
           'bound probe role differs')
    h.need(value.get('source_SHA') == value.get('container_checkpoint_SHA') == expected_source_sha,
           'actual A1 container provenance differs')
    h.need(type(expected_actor_calls) is int and expected_actor_calls >= 0
           and type(value.get('actor_calls')) is int and value['actor_calls'] == expected_actor_calls,
           'bound probe action count differs')
    updates = value.get('probe_optimizer_updates')
    h.need(all(type(value.get(k)) is int and value[k] == 0 for k in ('probe_training_updates', 'probe_BPTT_policy_steps'))
           and type(updates) is dict and set(updates) == {'pi', 'wm', 'aux', 'critic'}
           and all(type(v) is int and v == 0 for v in updates.values()), 'ZERO_UPDATE counters differ')
    binding = value.get('effective_wrapper', {}).get('source', {}); actual_helper = _source_binding()
    h.need(all(binding.get(k) == actual_helper[k] for k in ('bytes', 'SHA256'))
           and value.get('effective_wrapper', {}).get('qualname') == 'make_bound_only_wrapper.<locals>.BoundTeacherResidualPolicy',
           'effective bound-probe helper source/forward identity differs')
    h.need(value.get('container_algorithm_family') == h.FAMILY and value.get('container_algorithm_variant') in h.VARIANTS
           and value.get('container_algorithm_actor_view') == h.VIEW and value.get('residual_scale') == .05
           and value.get('action_clip') == 6. and value.get('native_enabled') is True
           and value.get('qualified_native_execution') is None and value.get('eligible_for_promotion') is False,
           'native-capable probe/container semantics differ')
    h.need(value.get('actor_frozen') is True and value.get('whole_root_CPU_unchanged') is True
           and value.get('inference_failed') is False, 'bound probe frozen state failed')
    h.need(all(type(value.get(k)) is int and value[k] == 1 for k in ('physical_byte_opens', 'SHA_calculations', 'CPU_decodes'))
           and type(value.get('mother_checkpoint_opens')) is int and value['mother_checkpoint_opens'] == 0,
           'whole own cache one-open/hash/decode and no mother reopen required')
    actual_rsl = value.get('actor_source_bindings', {}).get('rsl_rl.models.MLPModel', {})
    h.need(all(actual_rsl.get(k) == v for k, v in APPROVED_RSL.items()), 'effective actor RSL source differs')
    h.need(type(value.get('synthetic_only')) is bool, 'synthetic/native scope distinction required')
    if not value['synthetic_only']:
        h.need(expected_source_sha == QUALIFIED_CONTAINERS[expected_role], 'not the actual original qualified A1 container')
    boundary_binding = value.get('original_episode_boundary_source', {})
    h.need((boundary_binding.get('bytes'), boundary_binding.get('SHA256')) == BOUNDARY_PIN,
           'original episode-boundary source pin differs')
    boundary = value.get('original_episode_boundary', {})
    h.need(all(type(boundary.get(k)) is int and boundary[k] == expected_actor_calls
               for k in ('actions', 'original_step_transitions')) and boundary.get('pending_original_step') is False
           and boundary.get('synthetic_episode_mask') is False, 'original actual T/Tr transition accounting incomplete')
    forward_calls = value.get('bound_probe_action_statistics', {}).get('forward_calls')
    h.need(type(forward_calls) is int and forward_calls == expected_actor_calls,
           'one teacher/residual same-forward pair per original action required')
    return dict(passed_policy_component=True, policy_variant=VARIANT, purpose=PURPOSE,
                native_enabled=True, actual_admission_wait_close_or_skill=None,
                ZERO_UPDATE=True, relative_or_training_effect=None)
