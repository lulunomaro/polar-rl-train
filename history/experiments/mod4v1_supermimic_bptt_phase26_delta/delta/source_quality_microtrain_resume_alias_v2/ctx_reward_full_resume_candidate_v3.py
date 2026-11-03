"""SOURCE_ONLY: task-reward/context SuperMimic extension; never launches an env.

Runtime dependency: the reviewed supermimic_vendor_v2 and PyTorch, supplied by
parent. No Isaac/SDK import, checkpoint open, hardware query or training occurs
at module import. Run the stdlib validator separately; it does not import torch.

MDP required additions to the vendor contract:
  goal_with_context(f, K, xi) -> [..., K * goal_frame_dim]
  valid_imagination_start_with_context(f, H, xi) -> bool [...]
Optional, differentiable:
  project_predicted_context(xi1_hat, state1, action, f1) -> xi1
  imagination_timeout(f1, xi1) -> bool/probability [...]
Bridge transition additions: xi1 is the actual nonterminal next context;
xi1_valid is bool [N]. If terminal actorobs is unavailable, set done xi1=0 and
xi1_valid=False, never reset-observation targets. Only (~done & xi1_valid) trains
context delta. State s1 and original r/done still use the physical transition.
xi[..., :35] is parent-owned original, un-renormalized teacher observation.
"""
from __future__ import annotations

import copy
import importlib
import json
import math
import random
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.nn import functional as F

from supermimic_vendor_v2.contract import SUPERMIMIC_TRANSITION_KEY
from supermimic_vendor_v2.geometry import invariant_features, unflatten_state
from supermimic_vendor_v2.learner import SuperMimicLearner
from supermimic_vendor_v2.networks import RunningNorm, mlp, run_mlp
from supermimic_vendor_v2.replay import ReplayBuffer


@dataclass
class UpdateCounts:
    policy_attempts: int = 0
    pi_optimizer_steps: int = 0
    pi_bptt_optimizer_steps: int = 0
    pi_unverified_steps: int = 0
    pi_skipped_nonfinite: int = 0
    pi_skipped_zero: int = 0
    wm_optimizer_steps: int = 0
    aux_optimizer_steps: int = 0
    critic_optimizer_steps: int = 0


class ContextReplayBuffer(ReplayBuffer):
    """Same ring layout; context/reward labels stay attached to real transitions."""

    def __init__(self, T, N, device, num_joints, context_dim, action_dim):
        super().__init__(T, N, device, num_joints, context_dim, action_dim)
        extras = {
            'xi1': (context_dim, torch.float32),
            'xi1_valid': ((), torch.bool),
            'term': ((), torch.bool),
            'trunc': ((), torch.bool),
            'split_known': ((), torch.bool),
            'stream_cut': ((), torch.bool),
        }
        self.fields.update(extras)
        for name, (shape, dtype) in extras.items():
            dims = (T, N) + ((shape,) if isinstance(shape, int) else shape)
            self.data[name] = torch.zeros(dims, device=self.device, dtype=dtype)

    def add(self, transition):
        if 'xi1' not in transition:
            raise KeyError('xi1 needs real nonterminal next context, plus xi1_valid')
        item = dict(transition)
        known = 'term' in item and 'trunc' in item
        zero = torch.zeros_like(item['done'], dtype=torch.bool)
        item['xi1_valid'] = item.get('xi1_valid', ~item['done'].bool()).bool() & ~item['done'].bool()
        if known and not torch.equal(item['done'].bool(), item['term'].bool() | item['trunc'].bool()):
            raise ValueError('done must equal original term | trunc')
        item.setdefault('term', zero)
        item.setdefault('trunc', zero)
        item['split_known'] = torch.full_like(zero, known)
        item['stream_cut'] = zero
        super().add(item)

    def sample_transitions(self, B):
        if self.size < 1:
            raise ValueError('real replay must be populated before auxiliary fitting')
        age = torch.randint(self.size, (B,), device=self.device)
        env = torch.randint(self.N, (B,), device=self.device)
        row = self._row(age)
        return {name: tensor[row, env] for name, tensor in self.data.items()}

    def sample_windows(self, B, k):
        # Include the terminal transition; exclude subsequent reset/stream rows.
        if not 1 <= k <= self.size:
            raise ValueError('invalid world-model window length')
        age = torch.randint(self.size - k + 1, (B,), device=self.device)
        env = torch.randint(self.N, (B,), device=self.device)
        rows = self._row(age[:, None] + torch.arange(k, device=self.device))
        envs = env[:, None].expand_as(rows)
        out = {key: self.data[key][rows, envs] for key in ('s', 's1', 'a', 'xi', 'done')}
        cut = out['done'] | self.data['stream_cut'][rows, envs]
        out['mask'] = torch.cumprod(torch.cat((torch.ones(B, 1, device=self.device),
                                               1 - cut[:, :-1].float()), -1), -1)
        return out

    def seal_stream_boundary(self):
        # A declared reset-resume is a data discontinuity, NOT an original done label.
        if self.size:
            self.data['stream_cut'][(self.ptr - 1) % self.T].fill_(True)

    def export_state(self):
        return {'T': self.T, 'N': self.N, 'ptr': self.ptr, 'size': self.size,
                'data': {key: value.detach().cpu().clone() for key, value in self.data.items()}}

    def import_state(self, payload):
        if (payload['T'], payload['N']) != (self.T, self.N):
            raise ValueError('exact replay resume requires identical capacity and num_envs')
        if set(payload['data']) != set(self.data):
            raise ValueError('replay schema mismatch')
        if not 0 <= payload['ptr'] < self.T or not 0 <= payload['size'] <= self.T:
            raise ValueError('invalid replay pointer/size')
        for key, target in self.data.items():
            source = payload['data'][key]
            if source.shape != target.shape or source.dtype != target.dtype:
                raise ValueError('replay tensor schema mismatch: ' + key)
            target.copy_(source.to(self.device))
        self.ptr, self.size = int(payload['ptr']), int(payload['size'])


class TaskAuxiliaryModel(nn.Module):
    """Learn original r, reset probability, and pre-reset delta-xi, NOT a new reward."""

    def __init__(self, num_joints, action_dim, context_dim, hidden, policy_dt_s):
        super().__init__()
        self.context_dim = context_dim
        self.policy_dt_s = float(policy_dt_s)
        feature_dim = 2 * (13 + 2 * num_joints) + 2 * action_dim + context_dim + 1
        self.in_norm = RunningNorm(feature_dim)
        self.reward_norm = RunningNorm(1, eps=1e-4)
        self.context_norm = RunningNorm(context_dim, eps=1e-4)
        self.net = mlp(feature_dim, hidden, context_dim + 2, act=nn.SiLU)
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)
        with torch.no_grad():
            self.net[-1].bias[-1] = math.log(0.01 / 0.99)

    def features(self, state, state1, action, previous_action, normalized_context, frames):
        seconds = frames.float().unsqueeze(-1) * self.policy_dt_s
        return torch.cat((invariant_features(state), invariant_features(state1),
                          action, previous_action, normalized_context, seconds), -1)

    def forward(self, features):
        prediction = run_mlp(self.net, self.in_norm(features))
        reward = prediction[..., :1] * self.reward_norm.std() + self.reward_norm.mean
        delta = prediction[..., 1:-1] * self.context_norm.std() + self.context_norm.mean
        return reward.squeeze(-1), delta, prediction[..., -1]

    def supervised_loss(self, features, reward, delta_context, done, xi1_valid):
        self.in_norm.update(features)
        self.reward_norm.update(reward.unsqueeze(-1))
        valid = (~done.bool()) & xi1_valid.bool()
        if bool(valid.any()):
            self.context_norm.update(delta_context[valid])
        prediction = run_mlp(self.net, self.in_norm(features))
        reward_loss = F.mse_loss(prediction[..., 0], self.reward_norm(reward.unsqueeze(-1)).squeeze(-1))
        context_error = (prediction[..., 1:-1] - self.context_norm(delta_context)).square().mean(-1)
        context_loss = (context_error * valid.float()).sum() / valid.sum().clamp(min=1)
        # Natural, unweighted BCE; class reweighting would alter probability calibration.
        done_loss = F.binary_cross_entropy_with_logits(prediction[..., -1], done.float())
        return reward_loss + context_loss + done_loss, (reward_loss, context_loss, done_loss)


@contextmanager
def frozen_parameters(*modules):
    """Freeze weights, not autograd through state/action/context inputs."""
    saved = [(parameter, parameter.requires_grad)
             for module in modules for parameter in module.parameters()]
    try:
        for parameter, _ in saved:
            parameter.requires_grad_(False)
        yield
    finally:
        for parameter, enabled in saved:
            parameter.requires_grad_(enabled)


def capture_rng():
    result = {'python': random.getstate(), 'torch_cpu': torch.get_rng_state(),
              'torch_cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_initialized() else []}
    np = sys.modules.get('numpy')
    if np is not None:
        name, values, pos, gauss, cached = np.random.get_state()
        result['numpy'] = (name, values.tolist(), int(pos), int(gauss), float(cached))
    return result


def restore_rng(state):
    random.setstate(state['python'])
    torch.set_rng_state(state['torch_cpu'].cpu())
    if state['torch_cuda']:
        torch.cuda.set_rng_state_all([item.cpu() for item in state['torch_cuda']])
    if 'numpy' in state:
        np = importlib.import_module('numpy')
        name, values, pos, gauss, cached = state['numpy']
        np.random.set_state((name, np.asarray(values, dtype='uint32'), pos, gauss, cached))


class ContextRewardLearner(SuperMimicLearner):
    """Original state WM + learned task heads + truly unrolled policy optimization.

    Parent may subclass _make_policy() to install a frozen teacher35 + residual.
    cfg.compile=False until this extension has its own runtime compilation tests.
    Exact resume requires parent bridge export/import_supermimic_resume methods.
    """

    def __init__(self, env, cfg, log_dir, device=None, backend='', *,
                 aux_hidden=(256, 256), aux_batch=None, policy_dt_s=0.02,
                 predict_context_mask=None, require_exact_env_resume=False):
        if cfg.compile:
            raise ValueError('source extension requires compile=False')
        if cfg.horizon < 2:
            raise ValueError('true multi-step policy BPTT requires horizon >= 2')
        if not math.isclose(policy_dt_s, 0.02, rel_tol=0, abs_tol=1e-12):
            raise ValueError('this MOD4v1 integration is explicitly 50 Hz')
        for name in ('goal_with_context', 'valid_imagination_start_with_context'):
            if not callable(getattr(env.supermimic_mdp, name, None)):
                raise TypeError('parent task MDP must implement ' + name)
        super().__init__(env, cfg, log_dir, device, backend)
        A = getattr(self.mdp, 'action_dim', self.mdp.num_joints)
        self.buffer = ContextReplayBuffer(cfg.buffer_steps, env.num_envs, self.device,
                                          self.mdp.num_joints, self.mdp.context_dim, A)
        self.aux = TaskAuxiliaryModel(self.mdp.num_joints, A, self.mdp.context_dim,
                                     tuple(aux_hidden), policy_dt_s).to(self.device)
        # _make_policy has already installed the parent's frozen-teacher wrapper.
        # Construct/filter BEFORE installing post-step hooks; do not replace later.
        trainable_pi = [p for p in self.pi.parameters() if p.requires_grad]
        if not trainable_pi:
            raise ValueError('policy needs trainable student parameters')
        self.opt_pi = torch.optim.Adam(trainable_pi, lr=cfg.lr, betas=(0.9, 0.95))
        self.opt_aux = torch.optim.Adam(self.aux.parameters(), lr=cfg.lr)
        self.aux_batch = cfg.wm_batch if aux_batch is None else int(aux_batch)
        self.require_exact_env_resume = bool(require_exact_env_resume)
        self.counts = UpdateCounts()
        self.last_aux = {}
        self.last_bptt_receipt = {}
        self.collect_fraction = 0.0
        self.pending_iteration = None
        self._pending_bptt = None
        self.audit_path = self.log_dir / 'policy_optimizer_receipts.jsonl'
        mask = torch.ones(self.mdp.context_dim) if predict_context_mask is None else torch.as_tensor(predict_context_mask)
        if mask.shape != (self.mdp.context_dim,) or not torch.isfinite(mask).all() or not ((mask == 0) | (mask == 1)).all():
            raise ValueError('predict_context_mask must have context_dim binary entries')
        self.context_predict_mask = mask.to(self.device, dtype=torch.float32)
        self.extension_contract = {'schema': 'mod4v1.ctx_task_reward.v1',
            'num_joints': self.mdp.num_joints, 'action_dim': A,
            'context_dim': self.mdp.context_dim, 'obs_dim': self.mdp.obs_dim,
            'goal_frame_dim': self.mdp.goal_frame_dim, 'policy_dt_s': float(policy_dt_s),
            'aux_hidden': list(aux_hidden), 'aux_batch': self.aux_batch,
            'num_envs': env.num_envs, 'reward_source': 'original_real_transition_r',
            'termination_label': 'original_done_term_OR_trunc',
            'predict_context_mask': self.context_predict_mask.detach().cpu().tolist()}
        if not hasattr(self.opt_pi, 'register_step_post_hook'):
            raise RuntimeError('PyTorch optimizer step-post-hook support is required')
        self._hooks = [self.opt_pi.register_step_post_hook(self._on_pi_step)]
        for optimizer, name in ((self.opt_wm, 'wm_optimizer_steps'),
                                (self.opt_v, 'critic_optimizer_steps'),
                                (self.opt_aux, 'aux_optimizer_steps')):
            self._hooks.append(optimizer.register_step_post_hook(
                lambda opt, args, kwargs, field=name: setattr(self.counts, field, getattr(self.counts, field) + 1)))

    def _on_pi_step(self, optimizer, args, kwargs):
        self.counts.pi_optimizer_steps += 1
        pending = self._pending_bptt
        eligible = False
        receipt = {'iteration': self.iteration, 'pi_optimizer_steps': self.counts.pi_optimizer_steps,
                   'horizon': self.cfg.horizon, 'policy_dt_s': self.extension_contract['policy_dt_s']}
        if pending is not None:
            delta = float((pending['probe'].detach() - pending['before']).norm())
            eligible = (pending['cross_time_finite'] and pending['cross_time_grad_norm'] > 0
                        and pending['wm_path_finite'] and pending['wm_path_grad_norm'] > 0
                        and pending['parameter_grad_norm'] > 0 and math.isfinite(delta) and delta > 0
                        and any(group['lr'] > 0 for group in optimizer.param_groups))
            receipt.update({key: value for key, value in pending.items() if key not in ('probe', 'before')})
            receipt['probe_parameter_delta_l2'] = delta
        if eligible:
            self.counts.pi_bptt_optimizer_steps += 1
        else:
            self.counts.pi_unverified_steps += 1
        receipt.update(verified_bptt_optimizer_step=bool(eligible),
                       pi_bptt_optimizer_steps=self.counts.pi_bptt_optimizer_steps,
                       policy_attempts=self.counts.policy_attempts)
        self.last_bptt_receipt = receipt
        with self.audit_path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt, allow_nan=False) + '\n')

    def _goal(self, frames, context):
        return self.mdp.goal_with_context(frames, self.cfg.goal_frames, context)

    @torch.no_grad()
    def collect(self, n_steps):
        for _ in range(n_steps):
            info = self._state_info()
            state = unflatten_state(info['s'])
            obs = self.mdp.add_noise(self.mdp.obs(state, info['a_prev'], info['xi'], info['f']))
            fresh = info['ep_step'] == 0
            shifted = torch.cat((self.obs_hist[:, 1:], obs.unsqueeze(1)), 1)
            self.obs_hist = torch.where(fresh[:, None, None], obs.unsqueeze(1).expand_as(self.obs_hist), shifted)
            goal = self._goal(info['f'], info['xi'])
            self.pi.obs_norm.update(obs)
            self.pi.goal_norm.update(goal)
            if hasattr(self.env, 'before_action'):
                self.env.before_action()
            action = self.pi(self.obs_hist, goal)
            action = torch.clamp(action + self.cfg.action_noise * torch.randn_like(action), -20, 20)
            step_state = self.env.step(action.to(self.env_device))
            transition = step_state.info[SUPERMIMIC_TRANSITION_KEY]
            if self._bridged:
                transition = {key: value.to(self.device) for key, value in transition.items()}
            self.buffer.add(transition)
            initial, next_state = unflatten_state(transition['s']), unflatten_state(transition['s1'])
            self.wm.in_norm.update(self.wm.inputs(initial, transition['a'], self.mdp.normalize_context(transition['xi'])))
            self.wm.out_norm.update(self.wm.targets(initial, next_state))
            self.sim_steps += self.env.num_envs
            self.stats['r'].append(transition['r'].mean() / self.mdp.max_step_reward)
            if 'ep_len' in transition:
                self.stats['ep_len'].append(transition['ep_len'].mean())
                self.stats['ep_ret'].append(transition['ep_ret_norm'].mean())
                if 'term' in transition:
                    self.stats['term'].append(transition['term'].float().sum())
                self.stats['done'].append(transition['done'].float().sum())

    def aux_update(self):
        sample = self.buffer.sample_transitions(self.aux_batch)
        state, state1 = unflatten_state(sample['s']), unflatten_state(sample['s1'])
        features = self.aux.features(state, state1, sample['a'], sample['a_prev'],
                                     self.mdp.normalize_context(sample['xi']), sample['f'])
        loss, parts = self.aux.supervised_loss(features, sample['r'], sample['xi1'] - sample['xi'],
                                                sample['done'], sample['xi1_valid'])
        self.opt_aux.zero_grad(set_to_none=True)
        loss.backward()
        grad = nn.utils.clip_grad_norm_(self.aux.parameters(), 1.0)
        if not bool(torch.isfinite(loss) & torch.isfinite(grad)):
            raise FloatingPointError('non-finite auxiliary reward/context/terminal gradient')
        self.opt_aux.step()
        self.last_aux = dict(loss=float(loss.detach()), reward_z_mse=float(parts[0].detach()),
                             context_z_mse=float(parts[1].detach()), done_bce=float(parts[2].detach()),
                             original_done_fraction=float(sample['done'].float().mean()),
                             valid_next_context_fraction=float((~sample['done'] & sample['xi1_valid']).float().mean()))
        return loss.detach()

    def wm_update(self):
        result = super().wm_update()  # original real-state multi-step WM loss
        self.aux_update()             # separate supervised optimizer; never a policy step
        return result

    def _sample_valid_starts(self, batch_size):
        starts, histories, count = [], [], 0
        for _ in range(64):
            start, history = self.buffer.sample_starts(2 * batch_size, self.cfg.hist)
            valid = self.mdp.valid_imagination_start_with_context(start['f'], self.cfg.horizon, start['xi'])
            indices = valid.bool().nonzero(as_tuple=False).squeeze(-1)[:batch_size - count]
            if indices.numel():
                starts.append({key: value[indices] for key, value in start.items()})
                histories.append({key: value[indices] for key, value in history.items()})
                count += int(indices.numel())
            if count == batch_size:
                join = lambda parts: {key: torch.cat([part[key] for part in parts]) for key in parts[0]}
                return join(starts), join(histories)
        raise RuntimeError('insufficient valid imagination starts after 64 draws; inspect task/context/time bounds')

    def policy_update(self):
        self.counts.policy_attempts += 1
        start, history = self._sample_valid_starts(self.cfg.pi_batch)
        state = unflatten_state(start['s'])
        context, frames, previous_action = start['xi'], start['f'], start['a_prev']
        with torch.no_grad():
            obs_hist = self.mdp.obs(unflatten_state(history['s']), history['a_prev'], history['xi'], history['f'])
        obs_hist = self.mdp.add_noise(obs_hist)
        goal = self._goal(frames, context)
        states, contexts, all_frames, goals = [state], [context], [frames], [goal]
        actions, rewards, dones = [], [], []
        with frozen_parameters(self.wm, self.critic, self.aux):
            for _ in range(self.cfg.horizon):
                normalized = self.mdp.normalize_context(context)
                action = self.pi(obs_hist, goal).clamp(-6, 6)
                state1 = self.wm.step(state, action, normalized)
                next_frames = frames + 1
                features = self.aux.features(state, state1, action, previous_action, normalized, frames)
                reward, delta_context, done_logit = self.aux(features)
                next_context = context + self.context_predict_mask * delta_context
                project = getattr(self.mdp, 'project_predicted_context', None)
                if callable(project):
                    next_context = project(next_context, state1, action, next_frames)
                done = torch.sigmoid(done_logit)
                timeout = getattr(self.mdp, 'imagination_timeout', None)
                if callable(timeout):
                    timeout_probability = timeout(next_frames, next_context).float().clamp(0, 1)
                    done = 1 - (1 - done) * (1 - timeout_probability)
                next_obs = self.mdp.add_noise(self.mdp.obs(state1, action, next_context, next_frames))
                obs_hist = torch.cat((obs_hist[:, 1:], next_obs.unsqueeze(1)), 1)
                goal = self._goal(next_frames, next_context)
                state, context, frames, previous_action = state1, next_context, next_frames, action
                states.append(state); contexts.append(context); all_frames.append(frames); goals.append(goal)
                actions.append(action); rewards.append(reward); dones.append(done)
            rewards, dones = torch.stack(rewards), torch.stack(dones)
            alive = torch.cumprod(1 - dones, 0)
            continuation = torch.cat((torch.ones_like(alive[:1]), alive[:-1]), 0)
            discount = self.cfg.gamma ** torch.arange(self.cfg.horizon, device=self.device, dtype=torch.float32)[:, None]
            contributions = discount * continuation * rewards
            objective = contributions.sum(0)
            bootstrap = torch.zeros_like(objective)
            if not self.cfg.no_critic:
                bootstrap = self.cfg.gamma ** self.cfg.horizon * alive[-1] * self.critic(
                    self._critic_input(state, frames, self.mdp.normalize_context(context), goal))
                objective = objective + bootstrap
            loss = -objective.mean()
            # This tests FUTURE reward/bootstrap -> FIRST action, not merely a direct action-rate gradient.
            delayed = contributions[1:].sum(0) + bootstrap
            delayed_grad = torch.autograd.grad(delayed.mean(), actions[0], retain_graph=True, allow_unused=True)[0]
            cross_finite = delayed_grad is not None and bool(torch.isfinite(delayed_grad).all())
            cross_norm = float(delayed_grad.norm()) if cross_finite else 0.0
            # Exclude the a_prev shortcut: also measure future objective -> s1 -> a0.
            # This VJP explicitly traverses the frozen learned STATE transition.
            state_cotangents = torch.autograd.grad(delayed.mean(), states[1], retain_graph=True, allow_unused=True)
            state_cotangents = tuple(torch.zeros_like(value) if cotangent is None else cotangent.detach()
                                     for value, cotangent in zip(states[1], state_cotangents))
            wm_vjp = torch.autograd.grad(states[1], actions[0], grad_outputs=state_cotangents,
                                         retain_graph=True, allow_unused=True)[0]
            wm_finite = wm_vjp is not None and bool(torch.isfinite(wm_vjp).all())
            wm_norm = float(wm_vjp.norm()) if wm_finite else 0.0
            self.opt_pi.zero_grad(set_to_none=True)
            loss.backward()
            trainable = [p for group in self.opt_pi.param_groups for p in group['params'] if p.requires_grad]
            grad_norm = nn.utils.clip_grad_norm_(trainable, 1.0)
            nn.utils.clip_grad_value_(trainable, 0.1)
            finite = bool(torch.isfinite(loss) & torch.isfinite(grad_norm))
            probe = next((p for p in trainable if p.grad is not None and bool(p.grad.detach().abs().max() > 0)), None)
            if finite and float(grad_norm) > 0 and probe is not None:
                self._pending_bptt = dict(probe=probe, before=probe.detach().clone(),
                    cross_time_finite=bool(cross_finite), cross_time_grad_norm=cross_norm,
                    wm_path_finite=bool(wm_finite), wm_path_grad_norm=wm_norm,
                    parameter_grad_norm=float(grad_norm), loss=float(loss.detach()),
                    wm_weights_frozen=True, auxiliary_weights_frozen=True,
                    imagined_reward_source='original_real_reward_supervised_head')
                try:
                    self.opt_pi.step()  # only this successful post-hook may increment BPTT steps
                finally:
                    self._pending_bptt = None
            elif finite:
                self.counts.pi_skipped_zero += 1
            else:
                self.counts.pi_skipped_nonfinite += 1
        value_loss = torch.zeros((), device=self.device)
        if not self.cfg.no_critic:
            with torch.no_grad():
                critic_input = torch.stack([self._critic_input(
                    tuple(item.detach() for item in st), fr,
                    self.mdp.normalize_context(xi.detach()), go.detach())
                    for st, fr, xi, go in zip(states, all_frames, contexts, goals)])
                self.critic.norm.update(critic_input)
                values = self.critic(critic_input)
                target = values[-1]
                targets = []
                for index in range(self.cfg.horizon - 1, -1, -1):
                    target = rewards[index].detach() + self.cfg.gamma * (1 - dones[index].detach()) * (
                        (1 - self.cfg.lam) * values[index + 1] + self.cfg.lam * target)
                    targets.append(target)
                flat_targets = torch.stack(targets[::-1]).flatten()
            flat_input = critic_input[:-1].flatten(0, 1)
            n = flat_input.shape[0]
            m = n // self.cfg.critic_minibatches
            if m < 1:
                raise ValueError('critic minibatches exceed imagined transitions')
            for _ in range(self.cfg.critic_epochs):
                permutation = torch.randperm(n, device=self.device)
                for index in range(self.cfg.critic_minibatches):
                    ids = permutation[index * m:(index + 1) * m]
                    value_loss = (self.critic(flat_input[ids]) - flat_targets[ids]).square().mean()
                    self.opt_v.zero_grad(set_to_none=True)
                    value_loss.backward()
                    v_grad = nn.utils.clip_grad_norm_(self.critic.parameters(), 1.0)
                    if not bool(torch.isfinite(value_loss) & torch.isfinite(v_grad)):
                        raise FloatingPointError('non-finite critic gradient')
                    self.opt_v.step()
        imagined_reward = ((continuation * rewards).detach().sum(0) / self.cfg.horizon / self.mdp.max_step_reward).mean()
        return loss.detach(), value_loss.detach(), imagined_reward, grad_norm.detach(), alive[-1].mean().detach()

    def _checkpoint(self, include_optimizers):
        payload = super()._checkpoint(include_optimizers)
        extension = {'contract': self.extension_contract, 'aux': self.aux.state_dict(),
                     'counts': asdict(self.counts), 'last_bptt_receipt': self.last_bptt_receipt,
                     'context_predict_mask': self.context_predict_mask.detach().cpu(),
                     'full_resume': bool(include_optimizers)}
        if include_optimizers:
            exporter = getattr(self.env, 'export_supermimic_resume', None)
            env_resume = exporter() if callable(exporter) else None
            boundary_safe = self.pending_iteration is None or self.pending_iteration.get('phase') == 'collect'
            exact = isinstance(env_resume, dict) and env_resume.get('exact') is True
            if self.require_exact_env_resume and (not exact or not boundary_safe):
                raise ValueError('parent bridge exact physical/queue/RNG resume payload is required')
            extension.update(opt_aux=self.opt_aux.state_dict(), replay=self.buffer.export_state(),
                obs_hist=self.obs_hist.detach().cpu().clone(), rng=capture_rng(),
                collect_fraction=self.collect_fraction, pending_iteration=self.pending_iteration, environment=env_resume,
                update_boundary_safe=boundary_safe,
                resume_scope='exact_environment_and_learner' if exact else 'learner_full_environment_reset_required')
        payload['context_reward_extension'] = extension
        return payload

    def load(self, path, *, allow_environment_reset=False, allow_partial_update=False):
        # Own newly produced checkpoint only; this method is never called by source review.
        payload = torch.load(path, map_location='cpu', weights_only=True)
        return self.load_full_checkpoint(payload, allow_environment_reset=allow_environment_reset,
                                         allow_partial_update=allow_partial_update)

    def load_full_checkpoint(self, payload, *, allow_environment_reset=False, allow_partial_update=False):
        # Already byte-pinned/decoded exactly once by the admitted future worker.
        # Original full restore body below: all models/optimizers/replay/RNG/counts.
        payload = copy.deepcopy(payload)
        ext = payload.get('context_reward_extension', {})
        required = {'critic', 'opt_wm', 'opt_pi', 'opt_v'}
        if not required.issubset(payload) or not ext.get('full_resume'):
            raise ValueError('full context/reward/optimizer/replay checkpoint is required')
        if ext['contract'] != self.extension_contract:
            raise ValueError('task dimensions, auxiliary architecture, clock or context mask changed')
        if not ext.get('update_boundary_safe', False) and not allow_partial_update:
            raise ValueError('checkpoint interrupts optimizer transaction; explicit allow_partial_update=True required')
        saved_cfg = payload['args']
        current_cfg = asdict(self.cfg)
        # Iteration cap, save/log cadence are owner controls; algorithmic values must match.
        mutable = {'iterations', 'ckpt_every', 'log_every', 'log_backend'}
        if any(saved_cfg[key] != value for key, value in current_cfg.items() if key not in mutable):
            raise ValueError('algorithmic config differs from full checkpoint')
        exact = ext['resume_scope'] == 'exact_environment_and_learner'
        importer = getattr(self.env, 'import_supermimic_resume', None)
        if exact and not callable(importer):
            raise ValueError('exact parent bridge importer is missing')
        if not exact and not allow_environment_reset:
            raise ValueError('explicit allow_environment_reset=True required for reset-resume')
        self.wm.load_state_dict(payload['wm']); self.pi.load_state_dict(payload['pi'])
        self.critic.load_state_dict(payload['critic']); self.aux.load_state_dict(ext['aux'])
        for name in ('wm', 'pi', 'v', 'aux'):
            getattr(self, 'opt_' + name).load_state_dict(payload.get('opt_' + name, ext.get('opt_' + name)))
        self.buffer.import_state(ext['replay'])
        self.counts = UpdateCounts(**ext['counts'])
        self.last_bptt_receipt = ext['last_bptt_receipt']
        self.collect_fraction = float(ext['collect_fraction'])
        self.pending_iteration = ext.get('pending_iteration')
        self.iteration, self.wall_time, self.sim_steps = payload['iteration'], payload['wall_time'], payload['sim_steps']
        if exact:
            importer(ext['environment'])
            self.obs_hist.copy_(ext['obs_hist'].to(self.device))
        else:
            # Parent must already have constructed/reset its new original-task bridge.
            self.buffer.seal_stream_boundary()
            self.obs_hist.zero_()
        # Last: restore global RNG after model/optimizer/environment operations.
        restore_rng(ext['rng'])

    def train(self, resume=None, *, target_bptt_steps=None):
        if resume is not None:
            self.load(resume)
        if target_bptt_steps is not None and target_bptt_steps < 1:
            raise ValueError('positive cumulative BPTT step target required')
        required = max(self.cfg.hist, self.cfg.wm_window, self.cfg.warmup_steps)
        if self.buffer.size < required:
            self.collect(required - self.buffer.size)
        started = time.monotonic()
        previous_wall = self.wall_time
        try:
            while self.iteration < self.cfg.iterations:
                if target_bptt_steps is not None and self.counts.pi_bptt_optimizer_steps >= target_bptt_steps:
                    break
                for optimizer in (self.opt_wm, self.opt_pi, self.opt_v, self.opt_aux):
                    for group in optimizer.param_groups:
                        group['lr'] = self.lr_at(self.iteration)
                if self.pending_iteration is None:
                    self.collect_fraction += 1.0 / self.cfg.utd
                    steps = int(self.collect_fraction)
                    self.collect_fraction -= steps
                    self.pending_iteration = {'phase': 'collect', 'collect_left': steps,
                                              'wm_left': self.cfg.wm_batches}
                pending = self.pending_iteration
                # Original owner stop-before-action can interrupt here; the exact
                # number of not-yet-collected controls is persisted with the ring.
                while pending['collect_left']:
                    self.collect(1)
                    pending['collect_left'] -= 1
                pending['phase'] = 'wm'
                wm_result = None
                while pending['wm_left']:
                    wm_result = self.wm_update()
                    pending['wm_left'] -= 1
                pending['phase'] = 'policy'
                if self.iteration >= self.cfg.wm_only_iters:
                    self.policy_update()
                self.iteration += 1
                self.pending_iteration = None
                self.wall_time = previous_wall + time.monotonic() - started
                if self.iteration % self.cfg.log_every == 0:
                    row = dict(iteration=self.iteration, sim_steps=self.sim_steps, wall_time=self.wall_time,
                               counts=asdict(self.counts), auxiliary=self.last_aux,
                               bptt_receipt=self.last_bptt_receipt,
                               wm_loss=None if wm_result is None else float(wm_result[0]))
                    with (self.log_dir / 'context_reward_train.jsonl').open('a', encoding='utf-8') as stream:
                        stream.write(json.dumps(row, allow_nan=False) + '\n')
                    self.stats = {key: [] for key in self.stats}
                if self.iteration % self.cfg.ckpt_every == 0:
                    self.save()
        finally:
            self.wall_time = previous_wall + time.monotonic() - started
        return dict(iteration=self.iteration, sim_steps=self.sim_steps, counts=asdict(self.counts),
                    target_bptt_reached=target_bptt_steps is not None and self.counts.pi_bptt_optimizer_steps >= target_bptt_steps)
