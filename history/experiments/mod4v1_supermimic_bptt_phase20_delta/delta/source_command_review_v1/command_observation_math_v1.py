"""Isolated MOD4v1 formula candidate. stdlib only; no SDK/training side effects.

Real actor inputs remain the original noisy/delayed 35-D manager observation.
Clean state projection is only a sample-time building block: it is NOT a
replacement for the actor's current sensor feedback. Command metadata is for
world-model/critic bookkeeping only, never an extra actor feature.
"""
from dataclasses import dataclass
import math
from typing import Mapping, Optional, Sequence, Tuple

CHANNEL_WIDTHS = {'base_ang_vel': 3, 'projected_gravity': 3,
                  'leg_pos': 4, 'leg_vel': 4, 'wheel_vel': 2}
CHANNEL_SCALES = {'base_ang_vel': .5, 'projected_gravity': 1.,
                  'leg_pos': 1., 'leg_vel': .1, 'wheel_vel': .1}
RAW35_SLICES = {'command': (0, 3), 'height': (3, 4),
                'base_ang_vel': (4, 7), 'projected_gravity': (7, 10),
                'leg_pos': (10, 14), 'wheel_position_zero': (14, 16),
                'leg_vel': (16, 20), 'wheel_vel': (20, 22),
                'last_action': (22, 28), 'mode': (28, 35)}


def vector(value: Sequence[float], width: int) -> Tuple[float, ...]:
    out = tuple(float(x) for x in value)
    if len(out) != width or not all(math.isfinite(x) for x in out):
        raise ValueError('wrong width or nonfinite value')
    return out


def clip(x: float, low: float, high: float) -> float:
    return min(high, max(low, x))


def transpose_rotate(rotation, value):
    r = tuple(vector(row, 3) for row in rotation)
    if len(r) != 3:
        raise ValueError('rotation must be 3x3')
    v = vector(value, 3)
    return tuple(sum(r[i][j] * v[i] for i in range(3)) for j in range(3))


def clean_sensor_inputs(rotation_w_from_b, omega_w, q, qd,
                        leg_ids, wheel_ids, default_q, default_qd):
    """Unscaled, uncorrupted values at the SENSOR SAMPLE state, not apply state.

    Joint order/defaults must come from the actual resolved SceneEntityCfg and
    robot defaults. No assumption that the first six of the 30 joints are motors.
    The angular-velocity point/frame must be verified separately on the backend.
    """
    if len(leg_ids) != 4 or len(wheel_ids) != 2:
        raise ValueError('actual four leg / two wheel indices required')
    if not (len(q) == len(qd) == len(default_q) == len(default_qd)):
        raise ValueError('joint arrays/defaults must agree')
    ids = tuple(leg_ids) + tuple(wheel_ids)
    if len(set(ids)) != 6 or any(i < 0 or i >= len(q) for i in ids):
        raise ValueError('resolved motor indices must be distinct and in range')
    return {'base_ang_vel': transpose_rotate(rotation_w_from_b, omega_w),
            'projected_gravity': tuple(-float(x) for x in rotation_w_from_b[2]),
            'leg_pos': tuple(q[i] - default_q[i] for i in leg_ids),
            'leg_vel': tuple(qd[i] - default_qd[i] for i in leg_ids),
            'wheel_vel': tuple(qd[i] - default_qd[i] for i in wheel_ids)}


@dataclass(frozen=True)
class SensorSample:
    """Values AFTER original corruption and delay, BEFORE manager scaling."""
    values: Mapping[str, Sequence[float]]
    sample_ticks: Mapping[str, int]
    apply_tick: int
    episode: int

    def validate(self):
        if set(self.values) != set(CHANNEL_WIDTHS) or set(self.sample_ticks) != set(CHANNEL_WIDTHS):
            raise ValueError('all original feedback channels required')
        if self.apply_tick < 0 or self.episode < 0:
            raise ValueError('invalid sensor clock/episode')
        for key, width in CHANNEL_WIDTHS.items():
            vector(self.values[key], width)
            if self.apply_tick - self.sample_ticks[key] not in (0, 1):
                raise ValueError('feedback sample age must be 0 or 10ms')
        return self


def project_observation(command, height_command, sensors: SensorSample,
                        last_action, mode):
    """The shared state/command observation assembly, retaining sampled BODY frame.

    Height is in physical metres here. No sample-to-apply BODY rotation is added.
    SensorSample can be read from the real feedback cache or built from an
    imagined SAMPLE state + the unchanged exogenous noise/bias/delay process.
    """
    sensors.validate()
    obs = list(vector(command, 3)) + [5. * float(height_command)]
    for key in ('base_ang_vel', 'projected_gravity', 'leg_pos'):
        obs.extend(CHANNEL_SCALES[key] * x for x in sensors.values[key])
    obs.extend((0., 0.))
    for key in ('leg_vel', 'wheel_vel'):
        obs.extend(CHANNEL_SCALES[key] * x for x in sensors.values[key])
    obs.extend(vector(last_action, 6))
    obs.extend(vector(mode, 7))
    return vector(obs, 35)


def retain_original_actor_observation(raw35):
    """Real-path identity. Do not denoise, rotate, append truth or inspect UID."""
    return vector(raw35, 35)


class FeedbackQueue100Hz:
    """Scalar-environment reference of existing 0/10ms queue; explicit noise tape.

    Tick advances every .01s, TWO ticks per .02s action. A caller that only has
    50Hz endpoint states must report the missing intermediate sample rather than
    silently replaying a 50Hz queue. No RNG or episode distribution is changed.
    """
    def __init__(self, delay_ticks: int, episode: int = 0):
        self.reset(delay_ticks, episode)

    def reset(self, delay_ticks: int, episode: int):
        if delay_ticks not in (0, 1):
            raise ValueError('original delay distribution is 0/1 feedback ticks')
        self.delay = delay_ticks
        self.episode = episode
        self.cache = {}

    def apply(self, key, noisy_before_scale, tick):
        x = vector(noisy_before_scale, CHANNEL_WIDTHS[key])
        old = self.cache.get(key)
        if old is not None and old['last'] == tick:
            return old['out'], old['sample_tick']
        if old is not None and old['last'] != tick - 1:
            raise ValueError('Skipped/reversed feedback sample clock')
        delayed = old is not None and self.delay == 1
        out = old['cur'] if delayed else x
        sample_tick = old['last'] if delayed else tick
        self.cache[key] = dict(last=tick, cur=x, out=out, sample_tick=sample_tick)
        return out, sample_tick


def corrupt_sensor_inputs(clean, noise, episode_leg_bias):
    """Original additive noise/bias order; draws are supplied, not generated here."""
    bounds = {'base_ang_vel': .125, 'projected_gravity': .025,
              'leg_pos': .005, 'leg_vel': .25, 'wheel_vel': .5}
    bias = vector(episode_leg_bias, 4)
    if max(abs(x) for x in bias) > .0075 + 1e-12:
        raise ValueError('episode encoder bias outside original recipe')
    out = {}
    for key, width in CHANNEL_WIDTHS.items():
        base, eps = vector(clean[key], width), vector(noise[key], width)
        if max(abs(x) for x in eps) > bounds[key] + 1e-12:
            raise ValueError('noise outside original pre-scale recipe')
        out[key] = tuple(base[i] + eps[i] + (bias[i] if key == 'leg_pos' else 0.)
                         for i in range(width))
    return out


def e2_body_command(progress_goal, world_direction, heading, body_limit):
    """Exact source expression, NOT general 2D world-to-body vector rotation."""
    if progress_goal <= 0 or body_limit <= 0:
        raise ValueError('positive source configuration required')
    return (clip(2. * progress_goal * math.cos(heading - world_direction),
                 -body_limit, body_limit), 0.)


def transition_yaw(elapsed, target):
    if elapsed < 0:
        raise ValueError('elapsed must be nonnegative')
    scale = (elapsed if elapsed < 1. else 1. if elapsed < 4.
             else 5. - elapsed if elapsed < 5. else 0. if elapsed < 6.
             else -(elapsed - 6.) if elapsed < 7. else -1. if elapsed < 10.
             else elapsed - 11. if elapsed < 11. else 0.)
    return float(target) * scale


@dataclass(frozen=True)
class CommandSnapshot:
    """Model-side metadata only; none of these fields are added to actor input.

    time_left is the actual unscaled manager timer at the current observation.
    next_write_elapsed is phase_elapsed AFTER the most recent E2 write (+dt).
    clock_verified means decrement -> resample -> update order was established
    from exact source/runtime receipts, not assumed from comments.
    """
    role: str
    body_command: Tuple[float, float, float]
    standing: Optional[bool]
    time_left: Optional[float]
    clock_verified: bool = False
    dt: float = .02
    moving: Optional[bool] = None
    pure: Optional[bool] = None
    transition: Optional[bool] = None
    world_direction: Optional[float] = None
    signed_yaw: Optional[float] = None
    progress_goal: Optional[float] = None
    body_limit: Optional[float] = None
    next_write_elapsed: Optional[float] = None
    manual_evaluation_mode: bool = False
    heading_correction_disabled: bool = False
    w35_all_rough: bool = False


@dataclass(frozen=True)
class CommandTrace:
    commands: Tuple[Tuple[float, float, float], ...]
    unknown_from: Optional[int]
    reason: str


def short_command_trace(snapshot: CommandSnapshot, predicted_headings):
    """Known next-observation commands up to (not across) a stochastic resample.

    No window/role is silently discarded. Unknown suffix is returned explicitly;
    resample RNG/terminal/reset/external controller futures need separate evidence.
    """
    s = snapshot
    vector(s.body_command, 3)
    if s.dt <= 0 or s.role not in ('E2', 'W35'):
        raise ValueError('expected E2/W35 and positive control dt')
    if not s.clock_verified:
        return CommandTrace((), 0, 'command manager clock order not verified')
    if s.standing is None or s.time_left is None:
        return CommandTrace((), 0, 'actual standing Boolean / timer missing')
    if s.manual_evaluation_mode:
        return CommandTrace((), 0, 'external/manual future command tape required')
    if not s.heading_correction_disabled:
        return CommandTrace((), 0, 'heading-correction future not modelled')
    if s.role == 'W35' and not s.w35_all_rough:
        return CommandTrace((), 0, 'retained support transitions require actual support logic')
    if s.role == 'E2':
        if None in (s.moving, s.pure, s.transition):
            return CommandTrace((), 0, 'actual E2 mode Booleans missing')
        if s.moving and None in (s.world_direction, s.signed_yaw, s.progress_goal, s.body_limit):
            return CommandTrace((), 0, 'fixed world axis / signed rate / source config missing')
        if s.transition and None in (s.next_write_elapsed, s.signed_yaw):
            return CommandTrace((), 0, 'transition next-write phase/rate missing')
    commands = []
    for i, heading in enumerate(predicted_headings):
        # Original CommandTerm decrements time_left before resample/update.
        if s.time_left - (i + 1) * s.dt <= 1e-12:
            return CommandTrace(tuple(commands), i, 'natural stochastic resampling boundary')
        if s.standing:
            c = (0., 0., 0.)
        elif s.role == 'W35':
            c = (float(s.body_command[0]), 0., 0.)
        else:
            c = s.body_command
            if s.moving:
                vx, vy = e2_body_command(s.progress_goal, s.world_direction,
                                         float(heading), s.body_limit)
                c = (vx, vy, float(s.signed_yaw))
            if s.transition:
                c = (c[0], c[1], transition_yaw(s.next_write_elapsed + i * s.dt, s.signed_yaw))
        commands.append(vector(c, 3))
    return CommandTrace(tuple(commands), None, 'known conditional on no terminal/reset')


def w35_sampled_axis(sampled_heading, sampled_body_vx, sampled_standing):
    """Measurement helper only; sampled axis is immutable for this command UID.

    This is not RM70Command208._command_heading, which is rewritten each update.
    UID itself remains outside both actor and this math helper.
    """
    if type(sampled_standing) is not bool:
        raise ValueError('original sampled standing Boolean required')
    axis = sampled_heading + (math.pi if sampled_body_vx < 0 else 0.)
    return dict(axis=axis, nominal_speed=abs(sampled_body_vx), standing=sampled_standing,
                speed_tolerance=max(.03, .1 * abs(sampled_body_vx)))


def bounded_teacher_action(teacher, residual_logits, radius=.05, action_bound=6.):
    if radius <= 0 or action_bound <= 0:
        raise ValueError('positive candidate trust radius and original action bound required')
    base = tuple(clip(x, -action_bound, action_bound) for x in vector(teacher, 6))
    logits = vector(residual_logits, 6)
    action = tuple(clip(b + radius * math.tanh(d), -action_bound, action_bound)
                   for b, d in zip(base, logits))
    return action, base


def teacher_anchor(action, teacher_baseline, radius=.05):
    """Dimensionless candidate penalty; lambda/coverage must be separate ablation."""
    if radius <= 0:
        raise ValueError('positive trust radius required')
    return sum(((a - b) / radius) ** 2
               for a, b in zip(vector(action, 6), vector(teacher_baseline, 6))) / 6.


def original_tracking_components(command_t, root_lin_vel_b_at_reward,
                                 root_ang_vel_b_at_reward, gravity_b_at_reward,
                                 lin_sigma=.25, tight_sigma=.01,
                                 gap=.5, square_sigma=.25, yaw_sigma=.25,
                                 yaw_square_sigma=.25, height_gate=1.):
    """Unweighted source terms, NOT a replacement for full original task reward.

    SCUT linear exp/gap/square use pitch-compensated BODY vx, yaw square does not.
    'sigma' is denominator (not std squared). Weight*dt aggregation is caller-owned
    until exact active RewardManager/config is verified. Native reward stays intact.
    """
    cmd = vector(command_t, 3)
    v = vector(root_lin_vel_b_at_reward, 3)
    w = vector(root_ang_vel_b_at_reward, 3)
    g = vector(gravity_b_at_reward, 3)
    if min(lin_sigma, tight_sigma, yaw_sigma) <= 0 or not 0 <= height_gate <= 1:
        raise ValueError('positive source denominators / original gate required')
    forward = cmd[0] - v[0] * math.sqrt(max(0., 1. - g[0] ** 2))
    yaw = cmd[2] - w[2]
    return {'track_lin_vel': math.exp(-forward ** 2 / lin_sigma),
            'track_lin_vel_tight': math.exp(-forward ** 2 / tight_sigma),
            'track_lin_vel_huge_gap': float(forward ** 2 > gap),
            'track_lin_vel_square': (square_sigma * forward) ** 2,
            'track_ang_vel': math.exp(-yaw ** 2 / yaw_sigma),
            'track_ang_vel_square': (yaw_square_sigma * yaw) ** 2 * height_gate}


def split_original_reward(native_reward, exact_component_sum):
    return float(native_reward) - float(exact_component_sum)


def reward_lower_confidence(head_predictions, beta):
    if len(head_predictions) < 2 or beta < 0:
        raise ValueError('ensemble >=2 and beta>=0 required')
    p = vector(head_predictions, len(head_predictions))
    mean = sum(p) / len(p)
    variance = sum((x - mean) ** 2 for x in p) / len(p)
    return mean - beta * math.sqrt(variance)
