"""OFFLINE candidate components. Import only on parent's existing CPU Torch.

No SDK, simulator, checkpoint I/O, dependency install, device selection or training
entrypoint. The native bridge/worker/learner are never monkeypatched here.
"""
from dataclasses import dataclass
from typing import Callable, Optional
import torch
from torch import nn


class UnknownCommandEvolution(RuntimeError):
    pass


def _body(rotation, value):
    return (rotation.transpose(-1, -2) @ value.unsqueeze(-1)).squeeze(-1)


def sampled_state_sensor_inputs(state, leg_ids, wheel_ids, default_q, default_qd):
    """SAMPLE-time clean channels; caller retains original noise+100Hz queue.

    state=(position,R_world_from_body,velocity_world,omega_world,q,qd). Current
    state1 is not necessarily a delayed sample. Motor indices/defaults are required.
    Backend angular point/frame and sample stamps must have separate receipts.
    """
    if len(leg_ids) != 4 or len(wheel_ids) != 2:
        raise ValueError('actual four leg and two wheel indices required')
    _, rotation, _, omega_w, q, qd = state
    return {'base_ang_vel': _body(rotation, omega_w),
            'projected_gravity': -rotation[..., 2, :],
            'leg_pos': q[..., list(leg_ids)] - default_q[..., list(leg_ids)],
            'leg_vel': qd[..., list(leg_ids)] - default_qd[..., list(leg_ids)],
            'wheel_vel': qd[..., list(wheel_ids)] - default_qd[..., list(wheel_ids)]}


def compose_raw35(command, height_metres, sensor_values_after_noise_and_delay,
                  last_action, mode):
    """Identical assembly for real cached values and imagined SAMPLE-time values.

    BODY sensor components retain their original sample frame. No arbitrary
    clean-current-state replacement, actor truth feature, new noise or new scale.
    """
    x = sensor_values_after_noise_and_delay
    if command.shape[-1] != 3 or last_action.shape[-1] != 6 or mode.shape[-1] != 7:
        raise ValueError('original command/action/mode dimensions required')
    height = height_metres.unsqueeze(-1) if height_metres.ndim == command.ndim - 1 else height_metres
    out = torch.cat((command, 5. * height, .5 * x['base_ang_vel'],
                     x['projected_gravity'], x['leg_pos'],
                     command.new_zeros((*command.shape[:-1], 2)),
                     .1 * x['leg_vel'], .1 * x['wheel_vel'], last_action, mode), -1)
    if out.shape[-1] != 35:
        raise ValueError('raw35 assembly mismatch')
    return out


def e2_command(command_t, heading_at_next_command_write, *, world_direction,
               signed_yaw, moving, transition, standing, next_write_elapsed,
               progress_goal, body_limit):
    """Differentiable 2V*cos-vy0; metadata model-side only. NO timer/resample here."""
    vx = (2. * progress_goal * torch.cos(heading_at_next_command_write - world_direction)).clamp(-body_limit, body_limit)
    candidate = torch.stack((vx, torch.zeros_like(vx), signed_yaw), -1)
    c = torch.where(moving.unsqueeze(-1), candidate, command_t)
    e = next_write_elapsed
    scale = torch.where(e < 1., e,
            torch.where(e < 4., torch.ones_like(e),
            torch.where(e < 5., 5. - e,
            torch.where(e < 6., torch.zeros_like(e),
            torch.where(e < 7., -(e - 6.),
            torch.where(e < 10., -torch.ones_like(e),
            torch.where(e < 11., e - 11., torch.zeros_like(e))))))))
    yaw = torch.where(transition, signed_yaw * scale, c[..., 2])
    c = torch.cat((c[..., :2], yaw.unsqueeze(-1)), -1)
    return torch.where(standing.unsqueeze(-1), torch.zeros_like(c), c)


def w35_all_rough_command(command_t, standing):
    """Actual source: all-rough eligibility false; no retained flat moving mode."""
    c = torch.cat((command_t[..., :1], torch.zeros_like(command_t[..., 1:])), -1)
    return torch.where(standing.unsqueeze(-1), torch.zeros_like(c), c)


@dataclass
class ProjectedTransition:
    command: torch.Tensor
    sensor_values: Optional[dict] = None
    # Both clocks and both 100Hz samples/control must be explicitly accounted for.
    command_clock_verified: bool = False
    no_resample_or_reset: bool = False
    feedback_100hz_sample_clock_verified: bool = False
    status: str = 'unverified'


@dataclass
class SourceCommandSnapshot:
    """Fresh MODEL-SIDE snapshot; never appended to actor raw35/goal/history.

    time_left_seconds is decoded from native seconds (bridge's .01 scale undone).
    next_write_elapsed is post-observation E2 phase_elapsed: next write's phase.
    No acceptance UID, chosen terrain family or physical DR truth is required.
    """
    role: str
    start_frames: torch.Tensor
    time_left_seconds: torch.Tensor
    standing: torch.Tensor
    command_clock_verified: bool = False
    manual_evaluation_mode: bool = False
    moving: Optional[torch.Tensor] = None
    transition: Optional[torch.Tensor] = None
    world_direction: Optional[torch.Tensor] = None
    signed_yaw: Optional[torch.Tensor] = None
    next_write_elapsed: Optional[torch.Tensor] = None
    progress_goal: float = .5
    body_limit: float = 1.5


class FrozenSourceCommandProjection:
    """Concrete conditional short-H E2/W35 provider, with explicit unknown edges.

    At natural resampling, reset, external manual-reference mutation or absent
    heading/sample receipts, report unknown rather than redraw future commands or
    silently exclude hard windows. This is not yet a production collection bridge.
    """
    def __init__(self, snapshot, *, heading_from_state=None,
                 sampled_sensor_provider=None, sampled_sensor_clock_verified=False,
                 dt=.02):
        self.snapshot = snapshot
        self.heading_from_state = heading_from_state
        self.sampled_sensor_provider = sampled_sensor_provider
        self.sampled_sensor_clock_verified = bool(sampled_sensor_clock_verified)
        self.dt = float(dt)

    def __call__(self, context, state, state1, action, frames, next_frames):
        s = self.snapshot
        if s.manual_evaluation_mode:
            raise UnknownCommandEvolution('external frozen/manual command future requires its own tape')
        elapsed_writes = frames - s.start_frames
        next_writes = next_frames - s.start_frames
        known = (next_writes >= 1) & (s.time_left_seconds - next_writes * self.dt > 1e-12)
        if not bool(known.all()):
            return ProjectedTransition(context[..., :3], command_clock_verified=s.command_clock_verified,
                                       no_resample_or_reset=False, status='unknown_resample_or_reset')
        if s.role == 'E2':
            fields = (s.moving, s.transition, s.world_direction, s.signed_yaw, s.next_write_elapsed)
            if self.heading_from_state is None or any(v is None for v in fields):
                raise UnknownCommandEvolution('E2 immutable mode/axis/phase and heading-frame receipt required')
            command = e2_command(context[..., :3], self.heading_from_state(state1),
                         world_direction=s.world_direction, signed_yaw=s.signed_yaw,
                         moving=s.moving, transition=s.transition, standing=s.standing,
                         next_write_elapsed=s.next_write_elapsed + elapsed_writes * self.dt,
                         progress_goal=s.progress_goal, body_limit=s.body_limit)
        elif s.role == 'W35':
            command = w35_all_rough_command(context[..., :3], s.standing)
        else:
            raise UnknownCommandEvolution('source-specific command evolution not audited for role ' + s.role)
        sensors = None
        if self.sampled_sensor_provider is not None:
            sensors = self.sampled_sensor_provider(context, state, state1, action, frames, next_frames)
        return ProjectedTransition(command, sensors, s.command_clock_verified, True,
                                   sensors is not None and self.sampled_sensor_clock_verified,
                                   'conditional_command_and_sampled_sensor_projection')


class Raw35ActorMDP:
    """New explicit MDP wrapper: actor raw35 only, privileged WM/critic unchanged.

    Transition projector is pure and receives current/next state and original
    context. Metadata/UID/DR never enter obs or goal. Real obs is an IDENTITY slice,
    preserving noise/bias/delay. Sensor-model-only mode is labelled approximate;
    strict mode (default) demands actual/sample-time sensor values and receipts.
    """
    obs_dim = 35
    actor_context_offset = 0

    def __init__(self, base_mdp, transition_projector=None, *,
                 require_sampled_sensor_projection=True, tracking_component=None):
        self.base_mdp = base_mdp
        self.transition_projector = transition_projector
        self.require_sampled_sensor_projection = require_sampled_sensor_projection
        self.tracking_component = tracking_component
        self.last_projection_status = 'not_used'

    def __getattr__(self, name):
        return getattr(self.base_mdp, name)

    def to(self, device):
        self.base_mdp.to(device)
        return self

    def obs(self, state, previous_action, context, frames):
        if context.shape[-1] < 35:
            raise ValueError('original noisy raw35 context prefix required')
        return context[..., :35]

    def goal_with_context(self, frames, num_frames, context):
        return context[..., :3].repeat(*([1] * (context.ndim - 1)), num_frames)

    def add_noise(self, obs):
        # Original raw35 is already corrupted. Never double draw sensor noise.
        return obs

    def project_transition_context(self, context, state, state1, action, frames,
                                   next_frames, delta_context, predict_mask):
        predicted = context + predict_mask * delta_context
        if self.transition_projector is None:
            raise UnknownCommandEvolution('explicit command/sensor transition provider required')
        p = self.transition_projector(context, state, state1, action, frames, next_frames)
        if not p.command_clock_verified or not p.no_resample_or_reset:
            raise UnknownCommandEvolution('unknown command boundary: report coverage; do not shrink domain')
        if p.sensor_values is None:
            if self.require_sampled_sensor_projection:
                raise UnknownCommandEvolution('100Hz SAMPLE-time noisy/delayed sensor projection missing')
            # Explicit diagnostic approximation only: original aux sensor dynamics.
            raw = torch.cat((p.command, predicted[..., 3:14],
                             predicted.new_zeros((*predicted.shape[:-1], 2)),
                             predicted[..., 16:22], action, predicted[..., 28:35]), -1)
            self.last_projection_status = 'command_exact_sensor_aux_approximation'
        else:
            if not p.feedback_100hz_sample_clock_verified:
                raise UnknownCommandEvolution('sampled sensor clock/delay receipt required')
            raw = compose_raw35(p.command, context[..., 3:4] / 5., p.sensor_values,
                                action, context[..., 28:35])
            self.last_projection_status = p.status
        # Other context predictions remain available ONLY to WM/critic/aux.
        return torch.cat((raw, predicted[..., 35:]), -1)

    def aux_reward_target(self, sample, state, state1):
        if self.tracking_component is None:
            return sample['r']
        # Reward clock is transition pre-control f, command xi_t, physical s1.
        exact = self.tracking_component(state1, sample['xi'], sample['f'])
        return sample['r'] - exact

    def project_imagined_reward(self, learned_reward, state, state1, action,
                               previous_action, context, frames):
        if self.tracking_component is None:
            return learned_reward
        return learned_reward + self.tracking_component(state1, context, frames)


class BoundedTeacherResidualPolicy(nn.Module):
    """raw35-only residual + frozen teacher; no extra truth/acceptance metadata.

    Instantiate residual with obs_dim=35, hist=original hist, goal_dim=3. The
    teacher_forward adapter accepts ONLY (teacher, newest_raw35). No no_grad()
    around teacher forward: frozen weights still permit input derivatives.
    radius is an experimental action-unit trust budget, not a proven skill bound.
    Anchor default 0 keeps B/D-anchor distinct. Stage D uses explicit positive
    coefficient with a replay retention panel, never acceptance UID features.
    """
    def __init__(self, residual, teacher, teacher_forward: Callable, radius=.05,
                 anchor_coefficient=0., zero_output_init=True):
        super().__init__()
        if radius <= 0 or anchor_coefficient < 0:
            raise ValueError('positive radius / nonnegative anchor required')
        self.residual = residual
        self.teacher = teacher.eval().requires_grad_(False)
        self.teacher_forward = teacher_forward
        self.radius = float(radius)
        self.anchor_coefficient = float(anchor_coefficient)
        if zero_output_init:
            if not isinstance(residual.dec[-1], nn.Linear):
                raise ValueError('explicit zero output layer required')
            with torch.no_grad():
                residual.dec[-1].weight.zero_()
                residual.dec[-1].bias.zero_()

    @property
    def obs_norm(self):
        return self.residual.obs_norm

    @property
    def goal_norm(self):
        return self.residual.goal_norm

    def train(self, mode=True):
        super().train(mode)
        self.teacher.eval()
        return self

    def teacher_baseline(self, history):
        if history.shape[-1] != 35:
            raise ValueError('deployable policy accepts raw35 history only')
        return self.teacher_forward(self.teacher, history[..., -1, :]).clamp(-6., 6.)

    def forward(self, history, goal):
        base = self.teacher_baseline(history)
        delta = self.radius * torch.tanh(self.residual(history, goal))
        return (base + delta).clamp(-6., 6.)

    def policy_regularizer(self, history, goal, action):
        if self.anchor_coefficient == 0:
            return action.sum(-1) * 0.
        base = self.teacher_baseline(history)
        # Neither action nor sample-state input is detached. For nonsaturated
        # actions teacher derivatives cancel, leaving a true residual penalty.
        return self.anchor_coefficient * ((action - base) / self.radius).square().mean(-1)


class ScaledTeacherResidualPolicy35(BoundedTeacherResidualPolicy):
    """A1/B/C actor-view control: original .05*logits scaling, NOT a hard bound.

    Use this matched policy in tracking/reward-only contrasts. The bounded policy
    above is a separate D-bound intervention; positive anchor is another contrast.
    """
    def forward(self, history, goal):
        if history.shape[-1] != 35:
            raise ValueError('deployable policy accepts raw35 history only')
        base = self.teacher_forward(self.teacher, history[..., -1, :])
        return (base + self.radius * self.residual(history, goal)).clamp(-6., 6.)


def original_tracking_terms(command_t, velocity_b_at_reward, omega_b_at_reward,
                            gravity_b_at_reward, *, lin_sigma=.25, tight_sigma=.01,
                            gap=.5, square_sigma=.25, yaw_sigma=.25,
                            yaw_square_sigma=.25, height_gate=1.):
    """Unweighted original source components; native full reward is never replaced."""
    forward = command_t[..., 0] - velocity_b_at_reward[..., 0] * (1. - gravity_b_at_reward[..., 0].square()).clamp_min(0).sqrt()
    yaw = command_t[..., 2] - omega_b_at_reward[..., 2]
    return {'track_lin_vel': torch.exp(-forward.square() / lin_sigma),
            'track_lin_vel_tight': torch.exp(-forward.square() / tight_sigma),
            'track_lin_vel_huge_gap': (forward.square() > gap).to(forward.dtype),
            'track_lin_vel_square': (square_sigma * forward).square(),
            'track_ang_vel': torch.exp(-yaw.square() / yaw_sigma),
            'track_ang_vel_square': (yaw_square_sigma * yaw).square() * height_gate}


def lower_confidence_reward(predictions, beta):
    if predictions.shape[0] < 2 or beta < 0:
        raise ValueError('ensemble dimension >=2 and beta>=0 required')
    # Population variance; no clipping/threshold rewrite of original native reward.
    return predictions.mean(0) - beta * predictions.var(0, unbiased=False).clamp_min(1e-12).sqrt()
