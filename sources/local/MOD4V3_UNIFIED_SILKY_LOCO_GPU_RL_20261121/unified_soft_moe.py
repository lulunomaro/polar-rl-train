"""The actor shared by Isaac PPO, the MuJoCo judge and the WASD player."""
import torch
from torch import nn
from torch.nn import functional as F

EXPERTS = ('Cruise / Spin', 'Rough / Curb', 'Stair / Rim', 'Crest / Transition')
TEMPERATURE = 1.


class HistoryEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.temporal = nn.Sequential(nn.Conv1d(35, 64, 3, padding=1), nn.ELU(),
                                      nn.Conv1d(64, 64, 3, stride=2, padding=1), nn.ELU())
        self.project = nn.Sequential(nn.Linear(6*64+35, 128), nn.LayerNorm(128), nn.ELU())

    def forward(self, observation, history):
        batch = history.reshape(-1, 12, 35).transpose(1, 2)
        features = self.temporal(batch).flatten(1).reshape(*observation.shape[:-1], 6*64)
        return self.project(torch.cat((observation, features), -1))


class Expert(nn.Module):
    def __init__(self):
        super().__init__()
        self.obs = nn.Linear(35, 256)
        self.context = nn.Linear(128, 256, bias=False)
        self.head = nn.Sequential(nn.ELU(), nn.Linear(256, 128), nn.ELU(),
                                  nn.Linear(128, 64), nn.ELU(), nn.Linear(64, 6))

    def forward(self, observation, encoded):
        return self.head(self.obs(observation) + self.context(encoded))

    @torch.no_grad()
    def warm_start(self, e0):
        for dest, index in ((self.obs, 0), (self.head[1], 2), (self.head[3], 4), (self.head[5], 6)):
            dest.weight.copy_(e0[f'mlp.{index}.weight'])
            dest.bias.copy_(e0[f'mlp.{index}.bias'])
        self.context.weight.zero_()


class UnifiedSoftMoEActor(nn.Module):
    """All heads contribute to one action and backpropagate through the PPO mean."""
    def __init__(self):
        super().__init__()
        self.history_encoder = HistoryEncoder()
        self.router = nn.Sequential(nn.Linear(35 + 128, 96), nn.ELU(), nn.Linear(96, len(EXPERTS)))
        self.experts = nn.ModuleList(Expert() for _ in EXPERTS)
        self.last_weights = None

    @torch.no_grad()
    def warm_start(self, state):
        for k, expert in enumerate(self.experts):
            expert.warm_start(state)
            if k:
                nn.init.normal_(expert.context.weight, std=.002)
                expert.head[-1].weight.add_(torch.randn_like(expert.head[-1].weight)*.002)
        nn.init.normal_(self.router[-1].weight, std=.01)
        self.router[-1].bias.zero_()

    def components(self, policy):
        observation, history = policy[..., :35], policy[..., 35:]
        encoded = self.history_encoder(observation, history)
        logits = self.router(torch.cat((observation, encoded), -1))/TEMPERATURE
        actions = torch.stack([head(observation, encoded) for head in self.experts], dim=-2)
        return logits, actions

    def forward(self, policy):
        logits, actions = self.components(policy)
        self.last_weights = logits.softmax(-1)
        return (self.last_weights.unsqueeze(-1) * actions).sum(-2)

    def load_balance_loss(self, sample_mask):
        count = sample_mask.sum()
        terrain_weights = self.last_weights[:, 1:]
        mean = (terrain_weights * sample_mask[:, None]).sum(0) / count.clamp_min(1)
        return (mean - 1./terrain_weights.shape[1]).square().sum() * (count > 0)

    def entropy(self):
        weights = self.last_weights.clamp_min(1e-8)
        return -(weights*weights.log()).sum(-1).mean()


def distill_experts(actor, source, examples, steps, seed):
    """Fit the unified policy once using fixed offline examples before native rollouts."""
    device = next(actor.parameters()).device
    with torch.no_grad():
        for i, source_head in ((2, 'head'), (3, 'top_head')):
            expert = actor.experts[i]
            extra = source[f'mlp.e1.{source_head}.0.weight']
            fitted = {f'mlp.{k}.{attr}': source[f'mlp.e1.{source_head}.{k}.{attr}']
                      for k in (0, 2, 4, 6) for attr in ('weight', 'bias')}
            fitted['mlp.0.weight'] = extra[:, :35]
            expert.warm_start(fitted)
            expert.obs.bias.add_(extra[:, 29] - extra[:, 28] + extra[:, 33])
            expert.context.weight[:, :16].copy_(extra[:, 35:])

    policy = torch.as_tensor(examples['inputs'], device=device)
    action = torch.as_tensor(examples['actions'], device=device, dtype=policy.dtype)
    label = torch.as_tensor(examples['expert'], device=device, dtype=torch.long)
    if policy.shape != (len(label), 455) or action.shape != (len(label), 6):
        raise ValueError('Unexpected warm-start observation or action order')
    if not torch.isfinite(policy).all() or not torch.isfinite(action).all() or action.abs().max() > 6.:
        raise ValueError('Invalid warm-start values')
    buckets = [torch.where(label == k)[0] for k in range(len(EXPERTS))]
    if not all(map(len, buckets)):
        raise ValueError('Warm-start data does not cover all four experts')
    # Preserve the exact E0 head through distillation.
    params = [p for module in (actor.history_encoder, actor.router, *actor.experts[1:])
              for p in module.parameters()]
    optimizer = torch.optim.Adam(params, lr=.001, fused=device.type == 'cuda')
    rng = torch.Generator(device=device).manual_seed(seed)
    before = fit_summary(actor, policy, action, label, buckets)
    actor.experts[0].requires_grad_(False)
    for _ in range(steps):
        rows = torch.cat([ids[torch.randint(len(ids), (96,), device=device, generator=rng)] for ids in buckets])
        x, y, k = policy[rows], action[rows], label[rows]
        # Include the recorded low speed and the neighboring training speeds.
        frames = x.reshape(-1, 13, 35)
        speed = frames[:, :, 0]
        increment = torch.rand(len(rows), 1, device=device, generator=rng)*.16
        slow_demonstration = (speed >= .44) & (speed <= .48)
        speed.add_(increment * slow_demonstration)
        logits, actions = actor.components(x)
        chosen = actions[torch.arange(len(rows), device=device), k]
        mixed = (logits.softmax(-1)[..., None]*actions).sum(-2)
        loss = (F.smooth_l1_loss(chosen, y) + 2.*F.smooth_l1_loss(mixed, y)
                + .06*F.cross_entropy(logits, k, label_smoothing=.08))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    actor.experts[0].requires_grad_(True)
    actor.zero_grad(set_to_none=True)
    return dict(optimizer_steps=steps, examples=[len(ids) for ids in buckets], before=before,
                after=fit_summary(actor, policy, action, label, buckets))


@torch.no_grad()
def fit_summary(actor, x, y, labels, buckets):
    logits, action = actor.components(x)
    weights = logits.softmax(-1)
    mean = (weights[..., None]*action).sum(-2)
    return dict(mixed_mae=[float((mean[ids]-y[ids]).abs().mean()) for ids in buckets],
                expert_mae=[float((action[ids, k]-y[ids]).abs().mean()) for k, ids in enumerate(buckets)],
                labeled_gate_mean=[float(weights[ids, k].mean()) for k, ids in enumerate(buckets)],
                route_accuracy=float((weights.argmax(-1) == labels).float().mean()))
