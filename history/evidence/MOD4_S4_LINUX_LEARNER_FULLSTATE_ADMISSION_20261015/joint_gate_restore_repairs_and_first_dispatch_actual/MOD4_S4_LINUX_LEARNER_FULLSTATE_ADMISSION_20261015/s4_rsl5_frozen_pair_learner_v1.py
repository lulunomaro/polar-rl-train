"""Native RSL5 joint categorical/conditional-Gaussian actor for the first S4 pair.

Only the declared gate and new E0-initialized critic are parameters. Recorded z
is storage metadata, never a deployed observation. The framework's original
PPO update, GAE, clipping, timeout and adaptive-KL code are inherited unchanged.
This module alone does not admit a training environment or start learning.
"""
from __future__ import annotations
import copy
import hashlib
import math
from pathlib import Path
import torch
from torch import nn
from rsl_rl.algorithms import PPO
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35, Gate35CPU
from s4_shared_feedback_hardtop1_v1 import Critic38

CHOICE = 's4_recorded_choice'
SOURCE_SHA = (
    'b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',
    'b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd',
)


def source_files(refs):
    assert len(refs) == 2 and [r['expert'] for r in refs] == ['E0', 'E1_WAVE35']
    result = []
    for r, digest in zip(refs, SOURCE_SHA):
        assert r['sha256'] == digest
        assert hashlib.sha256(Path(r['local_path']).read_bytes()).hexdigest() == digest
        ck = torch.load(r['local_path'], map_location='cpu', weights_only=False)
        assert ck.get('history_architecture', {}).get('variant', 'A0') == 'A0'
        result.append(ck)
    return result


def view35(obs):
    x = obs['policy']
    assert x.ndim == 2 and x.shape[1] == 35 and x.dtype == torch.float32 and torch.isfinite(x).all()
    normal = torch.zeros_like(x[:, 28:35]); normal[:, 0] = 1
    assert torch.equal(x[:, 28:35], normal), 'No task/terrain oracle in the first deployed pair'
    return x


class S4FrozenPairActor(nn.Module):
    is_recurrent = False

    def __init__(self, obs, obs_groups, obs_set, output_dim, *, expert_refs,
                 routing_seed, hidden_dims=(64, 32), activation='elu',
                 obs_normalization=False, distribution_cfg=None):
        super().__init__()
        assert obs_set == 'actor' and obs_groups['actor'] == ['policy'] and output_dim == 6
        assert tuple(hidden_dims) == (64, 32) and activation == 'elu' and not obs_normalization
        assert distribution_cfg is None, 'The frozen pair owns its conditional distributions'
        assert isinstance(routing_seed, int) and 0 <= routing_seed < 2**63
        view35(obs)
        src = source_files(expert_refs)
        self.expert_refs = copy.deepcopy(expert_refs)
        self.experts = nn.ModuleList([FrozenMean35(s['actor_state_dict']) for s in src])
        self.register_buffer('frozen_std', torch.stack([s['actor_state_dict']['distribution.std_param'] for s in src]).clone())
        assert self.frozen_std.shape == (2, 6) and (self.frozen_std > 0).all()
        self.gate = Gate35CPU()
        self.routing_seed = routing_seed
        self.routing_generator = None
        self.rollout_samples = 0
        self.historical_forwards = 0

    def generator(self):
        if self.routing_generator is None:
            self.routing_generator = torch.Generator(device=self.frozen_std.device)
            self.routing_generator.manual_seed(self.routing_seed)
        assert torch.device(self.routing_generator.device) == self.frozen_std.device
        return self.routing_generator

    def forward(self, obs, masks=None, hidden_state=None, stochastic_output=False):
        assert masks is None and hidden_state is None, 'First S4 pair is feedforward'
        x = view35(obs)
        self.means = torch.stack([e(x) for e in self.experts], dim=1)
        self.logits = self.gate(x)
        assert torch.isfinite(self.means).all() and torch.isfinite(self.logits).all()
        if stochastic_output and CHOICE in obs.keys():
            # Historical samples choose their recorded expert. Never redraw z/a
            # during a minibatch probability evaluation.
            z = obs[CHOICE]
            assert z.shape == (len(x), 1) and torch.isfinite(z).all()
            assert ((z == 0) | (z == 1)).all(), 'Missing/invalid historical expert choice'
            self.z = z[:, 0].long()
            self.historical_forwards += 1
        elif stochastic_output:
            self.z = torch.multinomial(self.logits.softmax(-1), 1, generator=self.generator())[:, 0]
            self.rollout_samples += len(x)
        else:
            self.z = self.logits.argmax(-1)
        self.selected_mean = self.means[torch.arange(len(x), device=x.device), self.z]
        self.selected_std = self.frozen_std[self.z]
        if stochastic_output and CHOICE not in obs.keys():
            noise = torch.randn(self.selected_mean.shape, device=x.device, generator=self.generator())
            return self.selected_mean + self.selected_std * noise
        return self.selected_mean

    @property
    def output_distribution_params(self):
        # Both conditional densities are frozen and see the same historical x.
        # Exact latent-joint KL is therefore just KL(old gate || new gate).
        return (self.logits,)

    @property
    def output_mean(self): return self.selected_mean

    @property
    def output_std(self): return self.selected_std

    @property
    def output_entropy(self):
        logp = self.logits.log_softmax(-1); p = logp.exp()
        h = (self.frozen_std.log() + .5 * math.log(2 * math.pi * math.e)).sum(-1)
        return -(p * logp).sum(-1) + (p * h).sum(-1)

    def get_output_log_prob(self, outputs):
        assert outputs.shape == self.selected_mean.shape and torch.isfinite(outputs).all()
        normal = (-.5 * ((outputs - self.selected_mean) / self.selected_std).square()
                  - self.selected_std.log() - .5 * math.log(2 * math.pi)).sum(-1)
        categorical = self.logits.log_softmax(-1).gather(-1, self.z[:, None])[:, 0]
        return categorical + normal

    def get_kl_divergence(self, old_params, new_params):
        assert len(old_params) == len(new_params) == 1
        a, b = old_params[0], new_params[0]
        assert a.shape == b.shape and a.shape[-1] == 2 and torch.isfinite(a).all() and torch.isfinite(b).all()
        old, new = a.log_softmax(-1), b.log_softmax(-1)
        return (old.exp() * (old - new)).sum(-1)

    def get_hidden_state(self): return None
    def reset(self, dones=None, hidden_state=None): pass
    def detach_hidden_state(self, dones=None): pass
    def update_normalization(self, obs): pass

    def owned_state(self):
        return dict(version=1, sources=list(SOURCE_SHA), routing_seed=self.routing_seed,
                    routing_device=str(self.frozen_std.device), private_routing_rng=self.generator().get_state().clone(),
                    rollout_samples=self.rollout_samples, historical_forwards=self.historical_forwards)

    def restore_owned(self, s):
        assert s['version'] == 1 and tuple(s['sources']) == SOURCE_SHA and s['routing_seed'] == self.routing_seed
        assert s['routing_device'] == str(self.frozen_std.device), 'No implicit CPU/CUDA RNG migration'
        assert all(isinstance(s[k], int) and s[k] >= 0 for k in ('rollout_samples', 'historical_forwards'))
        self.generator().set_state(s['private_routing_rng'].cpu())
        self.rollout_samples = s['rollout_samples']; self.historical_forwards = s['historical_forwards']

    def verify_frozen(self):
        for e, ck in zip(self.experts, source_files(self.expert_refs)):
            assert all(torch.equal(v.cpu(), ck['actor_state_dict'][k]) for k, v in e.snapshot().items())
        assert all(not p.requires_grad for e in self.experts for p in e.parameters())
        expected = torch.stack([e.snapshot()['distribution.std_param'] for e in self.experts])
        assert torch.equal(expected, self.frozen_std)
        return True


class S4NewSourceCritic(nn.Module):
    is_recurrent = False
    def __init__(self, obs, obs_groups, obs_set, output_dim, *, expert_refs,
                 hidden_dims=(256, 128, 64), activation='elu', obs_normalization=False):
        super().__init__()
        assert obs_set == 'critic' and obs_groups['critic'] == ['critic'] and output_dim == 1
        assert tuple(hidden_dims) == (256, 128, 64) and activation == 'elu' and not obs_normalization
        assert obs['critic'].shape[-1] == 38
        self.body = Critic38(source_files(expert_refs)[0]['critic_state_dict'])

    def forward(self, obs, masks=None, hidden_state=None, stochastic_output=False):
        assert masks is None and hidden_state is None and not stochastic_output
        return self.body(obs['critic'])
    def get_hidden_state(self): return None
    def reset(self, dones=None, hidden_state=None): pass
    def detach_hidden_state(self, dones=None): pass
    def update_normalization(self, obs): pass


class S4RecordedChoicePPO(PPO):
    """Minimal act/storage and owned-state extensions; no override of update/GAE."""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        assert isinstance(self.actor, S4FrozenPairActor) and isinstance(self.critic, S4NewSourceCritic)
        assert not self.is_multi_gpu and self.rnd is None and self.symmetry is None
        assert CHOICE in self.storage.observations.keys()
        assert self.storage.observations[CHOICE].shape[-1] == 1
        self.actor.verify_frozen()

    def act(self, obs):
        assert CHICE_ABSENT(obs), 'Live feedback must not contain a historical choice'
        action = super().act(obs)
        # RSL's storage allocates observation buffers as float32. Exact 0/1
        # values explicitly validated above preserve z without a dtype claim.
        saved = obs.clone()
        saved[CHOICE] = self.actor.z[:, None].to(dtype=torch.float32)
        self.transition.observations = saved
        return action

    def save(self):
        assert self.storage.step == 0, 'Only an update boundary can save an empty rollout'
        self.actor.verify_frozen()
        ck = super().save()
        ck['S4_owned_learning'] = dict(schema=1, explicitly_new_gate_critic_optimizer=True,
            expert_optimizer_resumed=False, expert_sha=list(SOURCE_SHA),
            adaptive_learning_rate=float(self.learning_rate), actor_owned=self.actor.owned_state(),
            environment_fullstate_is_separate_required_contract=True)
        return ck

    def load(self, ck, load_cfg=None, strict=True):
        assert strict and load_cfg is None and self.storage.step == 0
        s = ck['S4_owned_learning']
        assert s['schema'] == 1 and tuple(s['expert_sha']) == SOURCE_SHA
        assert s['explicitly_new_gate_critic_optimizer'] is True and s['expert_optimizer_resumed'] is False
        result = super().load(ck, None, True)
        self.learning_rate = float(s['adaptive_learning_rate'])
        assert math.isfinite(self.learning_rate) and self.learning_rate > 0
        assert all(g['lr'] == self.learning_rate for g in self.optimizer.param_groups)
        self.actor.restore_owned(s['actor_owned']); self.actor.verify_frozen()
        return result

    @staticmethod
    def construct_algorithm(obs, env, cfg, device):
        assert CHICE_ABSENT(obs)
        extended = obs.clone()
        extended[CHOICE] = torch.full((env.num_envs, 1), -1., device=device)
        return PPO.construct_algorithm(extended, env, cfg, device)


def CHICE_ABSENT(obs):
    return CHOICE not in obs.keys()
