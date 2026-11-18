"""Two independent experts: frozen c874 E0 and kinematic-standup + contact-gated StairExpert E1."""
import torch
from torch import nn

H = 12
OBS = 35
LATENT = 16


class HistoryQueue:
    def __init__(self):
        self.buffer = None

    def reset(self, obs):
        self.buffer = obs.unsqueeze(-2).repeat(*([1] * (obs.ndim - 1)), H, 1).clone()
        return self.buffer.flatten(-2)

    def append(self, obs, done=None):
        if self.buffer is None:
            return self.reset(obs)
        self.buffer = torch.cat((self.buffer[..., 1:, :], obs.unsqueeze(-2)), -2)
        if done is not None and bool(done.any()):
            self.buffer[done] = obs[done, None, :].expand(-1, H, -1)
        return self.buffer.flatten(-2)


def action_mlp(n):
    return nn.Sequential(
        nn.Linear(n, 256),
        nn.ELU(),
        nn.Linear(256, 128),
        nn.ELU(),
        nn.Linear(128, 64),
        nn.ELU(),
        nn.Linear(64, 6),
    )


class HistoryFeatures(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer('mean', torch.zeros(OBS))
        self.register_buffer('scale', torch.ones(OBS))
        self.net = nn.Sequential(
            nn.Linear(420, 128),
            nn.ELU(),
            nn.Linear(128, 64),
            nn.ELU(),
            nn.Linear(64, LATENT),
        )

    def forward(self, h):
        h = ((h.reshape(*h.shape[:-1], H, OBS) - self.mean) / self.scale).clamp(-10, 10).flatten(-2)
        z = self.net(h)
        return torch.cat((z[..., :3], z[..., 3:5].sigmoid(), z[..., 5:]), -1)


class StairExpert(nn.Module):
    """Pure obs(35)+history(420)->action(6) continuous multi-step stair expert:
    - approach_base (frozen): tall, straight, twitch-free approach on ground & stair treads
    - gate (frozen): history-only step-contact climb detector
    - head (trainable): step climb head (retract & pull wheels onto step)
    - standup_head (trainable): smooth tread stand-up recovery head (active via kinematic joint extension
      obs[10:14] when crouched on Step 1 under tall command obs[3]>1.7 after wall climb ends)
    - top_head (trainable): final platform low-stance stabilization & v=0 parking head (obs[3]<1.5)
    """

    def __init__(self):
        super().__init__()
        self.approach_base = action_mlp(OBS)
        self.approach_base.requires_grad_(False)
        self.gate = nn.Sequential(
            nn.Linear(420, 128),
            nn.ELU(),
            nn.Linear(128, 32),
            nn.ELU(),
            nn.Linear(32, 1),
        )
        self.gate.requires_grad_(False)
        self.register_buffer('gate_mean', torch.zeros(OBS))
        self.register_buffer('gate_scale', torch.ones(OBS))
        self.encoder = HistoryFeatures()
        self.head = action_mlp(OBS + LATENT)
        self.standup_head = action_mlp(OBS + LATENT)
        self.top_head = action_mlp(OBS + LATENT)

    def gate_prob(self, h):
        hn = ((h.reshape(*h.shape[:-1], H, OBS) - self.gate_mean) / self.gate_scale).clamp(-10, 10).flatten(-2)
        return torch.sigmoid(self.gate(hn))

    def forward(self, x, h):
        normal_x = x.clone()
        normal_x[..., 28:35] = normal_x.new_tensor([1., 0., 0., 0., 0., 0., 0.])
        a_base = self.approach_base(normal_x)
        z = self.encoder(h)
        xz = torch.cat((x, z), -1)
        a_climb = self.head(xz)
        a_standup = self.standup_head(xz)
        a_top = self.top_head(xz)
        g_climb = self.gate_prob(h)

        # Disjoint phase-portrait gate in (obs[3], ext, d_ext) space:
        # 1) Riser climb (ext > -0.34 or d_ext < 0 before 5 crouched frames): g_su == 0 -> pure g_climb * a_climb!
        # 2) Post-crest crouched pull (past 5 frames all ext < -0.34): crouched_settled -> 1 -> standup_head!
        # 3) Smooth tread stand-up (d_ext = ext - ext_h[0] > +0.025 while ext < 0.19): rising_tread -> 1 -> standup_head!
        h_seq = h.reshape(*h.shape[:-1], H, OBS)
        ext = 0.25 * (x[..., 10:11] - x[..., 11:12] + x[..., 12:13] - x[..., 13:14])
        ext_h = 0.25 * (h_seq[..., 10] - h_seq[..., 11] + h_seq[..., 12] - h_seq[..., 13])
        max_recent5 = ext_h[..., -5:].amax(-1, keepdim=True)
        crouched_settled = ((-0.33 - max_recent5) / 0.05).clamp(0.0, 1.0)
        d_ext = ext - ext_h[..., 0:1]
        rising_tread = ((d_ext - 0.020) / 0.035).clamp(0.0, 1.0) * ((0.195 - ext) / 0.045).clamp(0.0, 1.0)
        g_su = torch.maximum(crouched_settled, rising_tread) * (x[..., 3:4] > 1.7).to(x.dtype)

        a_climb_or_walk = a_base + g_climb * (a_climb - a_base)
        a_pre = a_climb_or_walk + g_su * (a_standup - a_climb_or_walk)
        is_top = x[..., 3:4] < 1.5
        return torch.where(is_top, a_top, a_pre)


class Route2Body(nn.Module):
    def __init__(self):
        super().__init__()
        self.e0 = action_mlp(OBS)
        self.e0.requires_grad_(False)
        self.e1 = StairExpert()

    def forward(self, inputs):
        x = inputs[..., :OBS]
        h = inputs[..., OBS:]
        route = x[..., 29:30] > .5
        normal_x = x.clone()
        normal_x[..., 28:35] = normal_x.new_tensor([1., 0., 0., 0., 0., 0., 0.])
        a0 = self.e0(normal_x)
        a1 = self.e1(x, h)
        return torch.where(route, a1, a0)


class LocalStd(nn.Module):
    def __init__(self):
        super().__init__()
        self.e0_std = nn.Parameter(torch.ones(6), requires_grad=False)
        self.e1_log_std = nn.Parameter(torch.tensor([.010, .010, .010, .010, .020, .020]).log())

    def std(self, obs):
        return torch.where(
            obs[..., 29:30] > .5,
            self.e1_log_std.exp().expand(*obs.shape[:-1], 6),
            self.e0_std.expand(*obs.shape[:-1], 6),
        )


class LocalRoute2Actor(nn.Module):
    def __init__(self):
        super().__init__()
        self.mlp = Route2Body()
        self.distribution = LocalStd()

    def forward(self, obs, history):
        return self.mlp(torch.cat((obs, history), -1))

    def load_checkpoint(self, ck):
        self.load_state_dict(ck['actor_state_dict'], strict=True)
        return self


class StatefulRoute2Actor(LocalRoute2Actor):
    def __init__(self):
        super().__init__()
        self.queue = HistoryQueue()

    def reset_history(self):
        self.queue = HistoryQueue()

    def forward(self, obs):
        return super().forward(obs, self.queue.append(obs))
