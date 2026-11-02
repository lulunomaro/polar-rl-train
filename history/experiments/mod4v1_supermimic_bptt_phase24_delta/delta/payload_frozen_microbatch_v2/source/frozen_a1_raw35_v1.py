"""A1-only frozen inference SOURCE helper; stdlib-only at import.

Future admitted CPU/Torch entrypoints below read ONE own full A1 checkpoint.
They never construct a learner/SDK/optimizer, restore replay/RNG, or open a mother
checkpoint. The original N80 eval/resource/acceptance harness stays authoritative.
"""
from __future__ import annotations
import hashlib
import importlib
import inspect
import io
import math
from pathlib import Path
import re
from types import SimpleNamespace

VIEW = 'raw35_legacy_held_aux_v1'
FAMILY = 'a1_raw35_legacy_v1'
VARIANTS = ('A1_RAW35_FRESH', 'A1_RAW35_RESUME')
ROLES = ('E0', 'E2', 'E3', 'W35', 'CURB_PROTECTED878', 'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50')
COUNT_FIELDS = ('policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps',
                'pi_unverified_steps', 'pi_skipped_nonfinite', 'pi_skipped_zero',
                'wm_optimizer_steps', 'aux_optimizer_steps', 'critic_optimizer_steps')
_SOURCE_PINS = {
    'supermimic_vendor_v2.networks': (8609, 'c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706'),
    'native_supermimic_bridge': (13125, '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'),
}


def need(value, message):
    if not value:
        raise ValueError(message)


def counts(value):
    need(type(value) is dict and set(COUNT_FIELDS) <= set(value), 'nine producer counts required')
    need(all(type(value[k]) is int and value[k] >= 0 for k in COUNT_FIELDS), 'producer count type/value differs')
    need(value['pi_bptt_optimizer_steps'] <= value['pi_optimizer_steps'] <= value['policy_attempts'], 'producer count ordering differs')
    return {k: value[k] for k in COUNT_FIELDS}


def _sha(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def _teacher_identity(value):
    need(type(value) is dict and value.get('teacher_frozen') is True, 'frozen embedded teacher receipt required')
    path, sha, size = (value.get(k) for k in ('source_path', 'source_SHA', 'source_bytes'))
    need(type(path) is str and path and _sha(sha) and type(size) is int and size > 0, 'teacher metadata malformed')
    return path, sha, size


def _decode_cpu(stream):
    # Deliberately lazy: local source tests replace this PRIVATE decoder with their
    # own JSON fixture, never import Torch and never touch a production checkpoint.
    torch = importlib.import_module('torch')
    with torch.inference_mode(False):
        root = torch.load(stream, map_location='cpu', weights_only=True)
    return torch, root


def _runtime_modules():
    torch = importlib.import_module('torch')
    td = importlib.import_module('tensordict').TensorDict
    model = importlib.import_module('rsl_rl.models').MLPModel
    modules, bindings = {}, {}
    for name, expected in _SOURCE_PINS.items():
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        raw = path.read_bytes()
        need((len(raw), hashlib.sha256(raw).hexdigest()) == expected, 'reviewed actor source pin differs: ' + name)
        modules[name] = module
        bindings[name] = dict(path=str(path), bytes=len(raw), SHA256=expected[1])
    model_path = Path(inspect.getfile(model)).resolve()
    model_raw = model_path.read_bytes()
    bindings['rsl_rl.models.MLPModel'] = dict(module=model.__module__, qualname=model.__qualname__, path=str(model_path),
        bytes=len(model_raw), SHA256=hashlib.sha256(model_raw).hexdigest(), hardcoded_source_pin=False)
    policy = modules['supermimic_vendor_v2.networks'].Policy
    wrapper = modules['native_supermimic_bridge'].TeacherResidualPolicy
    for cls, module_name in ((policy, 'supermimic_vendor_v2.networks'), (wrapper, 'native_supermimic_bridge')):
        need(cls.__module__ == module_name and Path(inspect.getfile(cls)).resolve() == Path(modules[module_name].__file__).resolve(), 'actual actor class/source binding differs')
    return SimpleNamespace(t=torch, TD=td, MLP=model, Policy=policy, Wrapper=wrapper, source_bindings=bindings)


def _snapshot(value, t, *, require_cpu):
    """Identity/version guard, NOT a second full tensor copy or byte decode."""
    if t.is_tensor(value):
        if require_cpu:
            need(value.device.type == 'cpu', 'whole cached root must remain CPU')
        return ('tensor', value, value._version, tuple(value.shape), value.dtype, str(value.device))
    if isinstance(value, dict):
        return ('dict', value, [(k, _snapshot(v, t, require_cpu=require_cpu)) for k, v in value.items()])
    if type(value) in (tuple, list):
        return (type(value).__name__, value, [_snapshot(v, t, require_cpu=require_cpu) for v in value])
    need(type(value) in (type(None), bool, int, float, str, bytes), 'unreviewed full-root leaf type: ' + type(value).__name__)
    return ('scalar', type(value), value)


def _same(value, guard, t, *, require_cpu):
    kind = guard[0]
    if kind == 'tensor':
        need(t.is_tensor(value) and value is guard[1] and value._version == guard[2] and tuple(value.shape) == guard[3]
             and value.dtype == guard[4] and str(value.device) == guard[5], 'cached/live actor tensor identity/version changed')
        if require_cpu:
            need(value.device.type == 'cpu', 'whole cached root moved from CPU')
    elif kind == 'dict':
        need(value is guard[1] and list(value) == [k for k, _ in guard[2]], 'cached dictionary identity/schema changed')
        for k, child in guard[2]:
            _same(value[k], child, t, require_cpu=require_cpu)
    elif kind in ('list', 'tuple'):
        need(value is guard[1] and type(value).__name__ == kind and len(value) == len(guard[2]), 'cached sequence changed')
        for child, saved in zip(value, guard[2]):
            _same(child, saved, t, require_cpu=require_cpu)
    else:
        equal = value == guard[2] or (type(value) is float and guard[1] is float and math.isnan(value) and math.isnan(guard[2]))
        need(type(value) is guard[1] and equal, 'cached metadata changed')


def _validate_payload(root, final, expected, t):
    need(type(root) is dict, 'full A1 root must be a mapping')
    need({'wm', 'pi', 'critic', 'opt_wm', 'opt_pi', 'opt_v', 'args', 'context_reward_extension'} <= set(root), 'full own A1 checkpoint fields missing')
    for k in ('role', 'role_key', 'run_id', 'actor_view', 'algorithm_family', 'algorithm_variant'):
        need(root.get(k) == final.get(k), 'payload/FINAL provenance differs: ' + k)
    need(root.get('new_algorithm_not_PPO_resume') is True, 'own SuperMimic checkpoint required')
    need(root.get('asset_SHA') == expected['asset_SHA'] and root.get('contract_SHA') == expected['contract_SHA'], 'source asset/contract differs')
    cfg = root['args']
    need(type(cfg) is dict and all(type(cfg.get(k)) is int and cfg[k] == v for k, v in (('hist', 10), ('z_dim', 32), ('goal_frames', 1))), 'A1 policy history/goal/latent config differs')
    need(type(cfg.get('policy_hidden')) in (tuple, list) and all(type(v) is int for v in cfg['policy_hidden']) and tuple(cfg['policy_hidden']) == (512, 256, 128), 'reviewed policy hidden config differs')
    need(cfg.get('test_hidden_dims') is None and cfg.get('amp') == 'none', 'test/AMP policy branch not reviewed')
    ext = root['context_reward_extension']
    need(type(ext) is dict and ext.get('full_resume') is True and {'aux', 'opt_aux', 'replay', 'obs_hist', 'rng', 'environment'} <= set(ext), 'full root extension required without restoring it')
    need(counts(ext['counts']) == counts(final['counts']), 'saved/FINAL producer counts differ')
    need(type(root.get('iteration')) is int and root['iteration'] == final['checkpoint']['iteration'], 'saved/FINAL iteration differs')
    contract = ext['contract']
    need(type(contract) is dict, 'original A1 extension contract required')
    for k, value in dict(schema='mod4v1.ctx_task_reward.v1', obs_dim=35, action_dim=6, num_joints=30,
                         goal_frame_dim=3, policy_dt_s=.02, num_envs=1024).items():
        need(contract.get(k) == value and type(contract.get(k)) is type(value), 'reviewed A1 contract differs: ' + k)
    need(type(contract.get('context_dim')) is int and contract['context_dim'] >= 35, 'original full context dimension missing')
    replay = ext['replay']
    need(type(replay) is dict and replay.get('N') == 1024 and replay.get('T') == cfg.get('buffer_steps') == 128, 'source N1024 replay capacity differs')
    need(t.is_tensor(ext['obs_hist']) and tuple(ext['obs_hist'].shape) == (1024, 10, 35), 'whole source history shape differs; never slice to N80')
    teacher = _teacher_identity(root['bootstrap_teacher'])
    need(teacher == _teacher_identity(final['teacher']) == _teacher_identity(final['checkpoint']['teacher_source']), 'producer teacher metadata differs')
    pi = root['pi']
    need(isinstance(pi, dict) and pi and all(type(k) is str and t.is_tensor(v) for k, v in pi.items()), 'pi must be an exact tensor state mapping')
    need(any(k.startswith('teacher.') for k in pi) and any(k.startswith('residual.enc.') for k in pi)
         and any(k.startswith('residual.dec.') for k in pi), 'embedded teacher/residual missing; no mother reopen fallback')
    for prefix, width in (('residual.obs_norm.', 35), ('residual.goal_norm.', 3)):
        for k in ('mean', 'var', 'count'):
            need(prefix + k in pi, 'strict normalization buffer missing: ' + prefix + k)
        need(tuple(pi[prefix + 'mean'].shape) == tuple(pi[prefix + 'var'].shape) == (width,), 'normalization dimension differs')
        need(tuple(pi[prefix + 'count'].shape) == (), 'normalization count shape differs')
    return cfg


class FrozenA1CheckpointCache:
    def __init__(self, final, *, own_job_root, role, role_key, run_id, asset_SHA, contract_SHA):
        need(role in ROLES and type(role_key) is str and role_key and type(run_id) is str and run_id, 'explicit own role/key/run required')
        need(_sha(asset_SHA) and _sha(contract_SHA), 'asset/contract SHA required')
        need(type(final) is dict and final.get('kind') == 'MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3'
             and final.get('passed_execution') is True and final.get('teacher_unchanged') is True, 'actual successful producer FINAL required')
        need(final.get('role') == role and final.get('role_key') == role_key and final.get('run_id') == run_id, 'producer FINAL role/key/run differs')
        need(final.get('actor_view') == VIEW and final.get('algorithm_family') == FAMILY and final.get('algorithm_variant') in VARIANTS, 'A1 raw35 only; not A0 or strict/bounded B')
        c = counts(final['counts']); checkpoint = final['checkpoint']
        need(type(checkpoint) is dict and checkpoint.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved') is True
             and checkpoint.get('teacher_unchanged') is True and counts(checkpoint['counts']) == c, 'complete producer checkpoint receipt required')
        need(type(final.get('actual_BPTT_policy_steps')) is int and final['actual_BPTT_policy_steps'] == c['pi_bptt_optimizer_steps'], 'FINAL verified-BPTT counter differs')
        self.job = Path(own_job_root).resolve(); self.path = Path(checkpoint['path']).resolve()
        need(self.path.is_relative_to(self.job / 'production' / 'checkpoints') and self.path.name.endswith('_complete.pt'), 'checkpoint must be the own producer full-save path')
        need(type(checkpoint.get('bytes')) is int and checkpoint['bytes'] > 0 and _sha(checkpoint.get('SHA'))
             and type(checkpoint.get('iteration')) is int and checkpoint['iteration'] >= 0, 'producer checkpoint bytes/SHA/iteration malformed')
        self.io_counts = dict(physical_byte_opens=0, SHA_calculations=0, CPU_decodes=0)
        self.raw = self.path.read_bytes(); self.io_counts['physical_byte_opens'] += 1
        need(len(self.raw) == checkpoint['bytes'], 'own checkpoint bytes differ')
        self.SHA = hashlib.sha256(self.raw).hexdigest(); self.io_counts['SHA_calculations'] += 1
        need(self.SHA == checkpoint['SHA'], 'own checkpoint SHA differs')
        self.t, self.root = _decode_cpu(io.BytesIO(self.raw)); self.io_counts['CPU_decodes'] += 1
        self._guard = _snapshot(self.root, self.t, require_cpu=True)
        self.expected = dict(role=role, role_key=role_key, run_id=run_id, asset_SHA=asset_SHA, contract_SHA=contract_SHA)
        self.cfg = _validate_payload(self.root, final, self.expected, self.t)
        self._built = False

    def assert_unchanged(self):
        _same(self.root, self._guard, self.t, require_cpu=True)
        return True

    def receipt(self):
        return dict(kind='OWN_FULL_A1_CPU_CACHE_FOR_FROZEN_N80_NOT_RESUME_V1', source_path=str(self.path),
                    source_SHA=self.SHA, source_bytes=len(self.raw), **self.io_counts,
                    whole_root_CPU_unchanged=self.assert_unchanged(), source_num_envs=1024, eval_num_envs=80,
                    replay_or_saved_history_sliced_or_restored=False, live_optimizer_WM_critic_replay_created=False,
                    mother_checkpoint_opens=0, actual_resource_admission_or_parent_wait_proof=None)

    def build_mean_policy(self, device, num_envs=80):
        need(not self._built and type(num_envs) is int and num_envs == 80, 'one fresh N80 inference policy per cache')
        modules = _runtime_modules(); t = modules.t
        need(t is self.t, 'decode/build Torch binding differs')
        self.assert_unchanged()
        with t.inference_mode(False), t.no_grad(), t.random.fork_rng(devices=[]):
            obs = modules.TD(dict(policy=t.zeros(2, 35), critic=t.zeros(2, 38)), batch_size=[2])
            distribution = dict(class_name='rsl_rl.modules.distribution:GaussianDistribution', init_std=1., std_type='scalar')
            teacher = modules.MLP(obs, dict(actor=['policy'], critic=['critic']), 'actor', 6, [256, 128, 64], 'elu', distribution_cfg=distribution)
            residual = modules.Policy(35, 3, hist=self.cfg['hist'], z_dim=self.cfg['z_dim'], num_joints=6, hidden=self.cfg['policy_hidden'])
            # Original wrapper zeroes residual final layer in __init__. Strict load
            # MUST follow it, so trained residual weights are never zeroed later.
            pi = modules.Wrapper(residual, teacher, 0, scale=.05)
            current, saved = pi.state_dict(), self.root['pi']
            need(set(current) == set(saved), 'strict A1 pi state keys differ')
            for key, value in current.items():
                need(tuple(value.shape) == tuple(saved[key].shape) and value.dtype == saved[key].dtype, 'pi shape/dtype differs: ' + key)
                need(bool(t.isfinite(saved[key]).all()), 'nonfinite saved pi: ' + key)
            for prefix in ('residual.obs_norm.', 'residual.goal_norm.'):
                need(bool((saved[prefix + 'var'] >= 0).all()) and bool((saved[prefix + 'count'] >= 0).all()), 'normalization variance/count must be nonnegative')
            pi.load_state_dict(saved, strict=True, assign=False)
            for key, value in pi.state_dict().items():
                need(t.equal(value, saved[key]), 'strict-loaded pi value differs: ' + key)
            pi.eval().requires_grad_(False)
            pi.to(device)
        self._built = True
        return FrozenA1MeanPolicy(self, pi, modules, device, num_envs)


class FrozenA1MeanPolicy:
    def __init__(self, cache, pi, modules, device, num_envs):
        self.cache, self.pi, self.t, self.num_envs = cache, pi, modules.t, num_envs
        self.device = next(pi.parameters()).device  # Resolve e.g. 'cuda' to actual cuda:0.
        self.source_bindings = modules.source_bindings
        self._weights = [(name, value, _snapshot(value, self.t, require_cpu=False)) for name, value in list(pi.named_parameters()) + list(pi.named_buffers())]
        self._history = None; self.calls = 0; self._failed = False
        self.assert_frozen()

    def assert_frozen(self):
        self.cache.assert_unchanged()
        need(type(self.pi.offset) is int and self.pi.offset == 0 and type(self.pi.scale) is float and self.pi.scale == .05
             and type(self.pi.residual.hist) is int and self.pi.residual.hist == 10, 'fixed raw35 wrapper/history semantics changed')
        for norm in (self.pi.obs_norm, self.pi.goal_norm):
            need(norm.eps == .01 and norm.max_count == 2e8, 'normalization hyperparameters changed')
        need(not any(module.training for module in self.pi.modules()), 'eval modules changed to training')
        need(not any(p.requires_grad for p in self.pi.parameters()), 'inference parameters became trainable')
        current = dict(list(self.pi.named_parameters()) + list(self.pi.named_buffers()))
        need(set(current) == {name for name, _, _ in self._weights}, 'live actor tensor schema changed')
        for name, value, saved in self._weights:
            need(current[name] is value, 'live actor tensor rebound: ' + name)
            _same(value, saved, self.t, require_cpu=False)
        return True

    def act(self, raw35, *, episode_start):
        need(not self._failed, 'inference sequence previously failed; abort own eval scope')
        try:
            self.assert_frozen(); t = self.t
            need(t.is_tensor(raw35) and tuple(raw35.shape) == (self.num_envs, 35) and raw35.device == self.device
                 and raw35.dtype == t.float32 and bool(t.isfinite(raw35).all()), 'original finite float32 noisy/delayed policy35 required')
            need(t.is_tensor(episode_start) and tuple(episode_start.shape) == (self.num_envs,)
                 and episode_start.device == self.device and episode_start.dtype == t.bool, 'original first/term|trunc bool mask required')
            if self._history is None:
                need(bool(episode_start.all()), 'first action requires all original fresh episodes')
                self._history = t.zeros(self.num_envs, 10, 35, device=self.device)
            with t.inference_mode():
                shifted = t.cat((self._history[:, 1:], raw35.unsqueeze(1)), 1)
                self._history = t.where(episode_start[:, None, None], raw35.unsqueeze(1).expand_as(self._history), shifted)
                goal = raw35[:, :3]  # SAME known-command prefix, not fresh sensor/DR/UID input.
                action = self.pi(self._history, goal).clamp(-6., 6.)
                need(tuple(action.shape) == (self.num_envs, 6) and bool(t.isfinite(action).all()), 'nonfinite or wrong mean action')
            self.calls += 1; self.assert_frozen()
            return action
        except BaseException:
            self._failed = True
            raise

    def receipt(self):
        return dict(self.cache.receipt(), kind='FROZEN_A1_RAW35_MEAN_N80_V1', actor_view=VIEW,
                    algorithm_family=FAMILY, actor_calls=self.calls, history=10, first_reset_padding='repeat_current_observation',
                    goal='same_raw35_prefix_3', residual_scale=.05, teacher_offset=0, action_clip=6.,
                    action_noise=0., normalization_updates=0, optimizer_updates=0, inference_failed=self._failed,
                    actor_frozen=self.assert_frozen(), actor_source_bindings=self.source_bindings,
                    saved_environment_RNG_history_or_replay_restored=False, skill_pass_rate=None)
