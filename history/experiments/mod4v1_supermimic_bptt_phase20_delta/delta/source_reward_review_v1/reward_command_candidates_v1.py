"""Pure-stdlib SOURCE-ONLY formula candidates; no simulator, optimizer or file IO.

These functions are test fixtures, NOT an installed reward/command replacement.
They do not alter any original acceptance threshold, speed, DR or physics.
A passing numerical test is not evidence of a skill/pass-rate improvement.
"""
from __future__ import annotations
import math


def exp_denominator(error: float, denominator: float) -> float:
    """SCUT convention: the legacy argument named std is already the denominator."""
    if denominator <= 0:
        raise ValueError("positive exponential denominator required")
    return math.exp(-(error * error) / denominator)


def exp_error_slope(error: float, denominator: float) -> float:
    return -2.0 * error / denominator * exp_denominator(error, denominator)


def scut_forward_error(command_vx: float, body_vx: float, gravity_x: float) -> float:
    return command_vx - body_vx * math.sqrt(max(0.0, 1.0 - gravity_x * gravity_x))


def linear_band_gate(height_error: float, full: float, zero: float) -> float:
    error = abs(height_error)
    if zero <= full:
        return float(error <= full)
    return min(1.0, max(0.0, (zero - error) / (zero - full)))


def world_to_body_xy(world_vx: float, world_vy: float, yaw: float) -> tuple[float, float]:
    """Yaw-only semantic fixture; real getter/frame must be physically validated first."""
    c, s = math.cos(yaw), math.sin(yaw)
    return c * world_vx + s * world_vy, -s * world_vx + c * world_vy


def body_to_world_xy(body_vx: float, body_vy: float, yaw: float) -> tuple[float, float]:
    c, s = math.cos(yaw), math.sin(yaw)
    return c * body_vx - s * body_vy, s * body_vx + c * body_vy


def signed_body_axis(command_heading: float, body_vx: float) -> float:
    """Original W35 natural interval axis includes pi for a negative BODY command."""
    return command_heading + (math.pi if body_vx < 0 else 0.0)


def project_xy(dx: float, dy: float, axis: float, seconds: float) -> tuple[float, float]:
    if seconds <= 0:
        raise ValueError("positive same-episode duration required")
    c, s = math.cos(axis), math.sin(axis)
    return (dx * c + dy * s) / seconds, (-dx * s + dy * c) / seconds


def original_nonholonomic_body_vx(progress_speed: float, heading: float,
                                   world_direction: float, limit: float = 1.5) -> float:
    """Frozen spin_translation_math formula, NOT constant world velocity per instant."""
    value = 2.0 * progress_speed * math.cos(heading - world_direction)
    return max(-limit, min(limit, value))


def scut_linear_rate(error: float) -> float:
    """Common audited role values; this is a scalar counterexample, not a rollout."""
    return (exp_denominator(error, 0.25) + 0.2 * exp_denominator(error, 0.01)
            - float(error * error > 0.5) - (0.25 * error) ** 2)


def scut_yaw_rate(error: float) -> float:
    return 0.5 * exp_denominator(error, 0.25) - (0.25 * error) ** 2


def scut_height_rate(error: float, both_history_norm_over_1N: bool = True) -> float:
    """Height square weight is zero in all eight joined metadata envs."""
    return (0.7 * exp_denominator(error, 0.01)
            + 0.3 * exp_denominator(error, 0.001)
            + 0.3 * exp_denominator(error, 0.1) * both_history_norm_over_1N)


def scut_orientation_cost(gravity_x: float, gravity_y: float, command_vx: float) -> float:
    gain = 2.0 * math.exp(-command_vx ** 2) + 2.0
    return ((2.0 * gravity_x) ** 2 + (gain * gravity_x) ** 2
            + (gain * gravity_y) ** 2)


def rolling_scalar_cost(point_speed: float, force_z_mean: float,
                        speed_scale: float = 0.15) -> float:
    """Symmetric two-wheel fixture of original load/saturation, not material slip."""
    load = max(0.0, min(1.0, force_z_mean / 10.0))
    rolling = min(4.0, (point_speed / speed_scale) ** 2) * 2 * load / max(1.0, 2 * load)
    return rolling + 0.25 * (1.0 - load)


def bounded_tracking(error: float, scale: float) -> float:
    """Candidate rational reward; bounded [0,1], not acceptance and not invariant shaping."""
    if scale <= 0:
        raise ValueError("positive tracking scale required")
    q = error / scale
    return 1.0 / (1.0 + q * q)


def bounded_tracking_slope(error: float, scale: float) -> float:
    q = error / scale
    return -2.0 * q / scale / ((1.0 + q * q) ** 2)


def huber_tracking_cost(error: float, scale: float, delta: float = 1.0) -> float:
    """Candidate nonnegative normalized Huber cost: quadratic center, linear tails.

    It is unbounded. Clipping this cost introduces an exact zero-slope tail;
    use a finite envelope/reviewed weight rather than assuming clipping is free.
    """
    if scale <= 0 or delta <= 0:
        raise ValueError("positive Huber scale and delta required")
    q = abs(error / scale)
    return 0.5 * q * q if q <= delta else delta * (q - 0.5 * delta)


def huber_cost_slope(error: float, scale: float, delta: float = 1.0) -> float:
    q = error / scale
    return max(-delta, min(delta, q)) / scale


def bounded_directional_potential(progress: float, length: float) -> float:
    """Candidate only: direction/route/phase reference must be part of the Markov state."""
    if length <= 0:
        raise ValueError("positive progress length required")
    return math.tanh(progress / length)


def potential_transition(phi0: float, phi1: float, gamma: float,
                         continuation: float = 1.0) -> float:
    """F = gamma * c * Phi(s1) - Phi(s), including the terminal transition.

    Algebraic telescoping requires the SAME gamma and continuation as the return,
    the same augmented state/reference, no reset joins, and V'=V-Phi at bootstrap.
    A learned reward/WM/soft-done fit does not establish these conditions physically.
    """
    if not 0 <= gamma <= 1 or not 0 <= continuation <= 1:
        raise ValueError("gamma and continuation must be in [0,1]")
    return gamma * continuation * phi1 - phi0


def potential_manager_rate(phi0: float, phi1: float, gamma: float,
                           continuation: float, step_dt: float) -> float:
    """Only for a manager that later multiplies term weight by dt; not bridge r."""
    if step_dt <= 0:
        raise ValueError("positive control dt required")
    return potential_transition(phi0, phi1, gamma, continuation) / step_dt


def discounted_return(rewards: list[float], continuation: list[float], gamma: float,
                      bootstrap: float = 0.0) -> float:
    if len(rewards) != len(continuation):
        raise ValueError("transition lengths must agree")
    result, discount = 0.0, 1.0
    for reward, c in zip(rewards, continuation):
        result += discount * reward
        discount *= gamma * c
    return result + discount * bootstrap


def potential_augmented_return(rewards: list[float], continuation: list[float],
                               phis: list[float], gamma: float,
                               bootstrap: float = 0.0) -> float:
    if len(phis) != len(rewards) + 1:
        raise ValueError("each pre/post transition needs one potential")
    shaped = [r + potential_transition(phis[i], phis[i + 1], gamma, c)
              for i, (r, c) in enumerate(zip(rewards, continuation))]
    return discounted_return(shaped, continuation, gamma, bootstrap - phis[-1])


def phase_gate(original_gate: float, externally_declared_active: bool,
               floor: float = 0.25) -> float:
    """Candidate soft floor for a declared task phase, not an oracle or termination change."""
    if not 0 <= floor <= 1:
        raise ValueError("gate floor must be in [0,1]")
    return max(original_gate, floor) if externally_declared_active else original_gate


def declared_phase_cost_multiplier(externally_declared_active: bool,
                                   active_multiplier: float = 0.5) -> float:
    """New candidate finite cost reduction; normal phase exactly unchanged."""
    if not 0 <= active_multiplier <= 1:
        raise ValueError("phase cost multiplier must be in [0,1]")
    return active_multiplier if externally_declared_active else 1.0


def e2_cycle_accept(along: float, cross: float, yaw_error: float, seconds: float,
                    complete: bool, terminated: bool, truncated: bool) -> bool:
    """Pure formula fixture of known E2 predicate, not a new evaluator/cohort."""
    return (complete and seconds > 0 and not terminated and not truncated
            and abs(along - 0.5) <= 0.05 and abs(cross) <= 0.05
            and abs(yaw_error) <= 0.2)


def endpoint_ordered(before_index: int | None, after_index: int | None,
                     first_ordinary_failure: int | None) -> bool:
    """Ordering fixture only; real E1 wheel/body/link/Fz predicates stay authoritative."""
    return (before_index is not None and after_index is not None
            and before_index < after_index
            and (first_ordinary_failure is None or after_index < first_ordinary_failure))


class RecoveryPhaseFixture:
    """Scalar replica of source E3 phase, not a simulator or a replacement acceptance."""
    def __init__(self, recipe: int, initial_upright: float = 0.0):
        self.recipe, self.peak = recipe, initial_upright
        self.age = self.stable = 0
        self.credited = self.request = False
        self.delta = 0.0

    def step(self, gravity_z: float, root_speed: float, angular_speed: float) -> float:
        self.request = self.recipe != 12 and self.age < 300
        upright = min(1.0, max(0.0, (1.0 - gravity_z) / 2.0))
        now = max(self.peak, upright) if self.request else self.peak
        self.delta, self.peak = now - self.peak, now
        good = (gravity_z < -0.984807753 and root_speed < 0.03
                and angular_speed < 0.2 and self.request)
        self.stable = self.stable + 2 if good else 0
        event = self.stable >= 50 and not self.credited
        self.delta += float(event)
        self.credited = self.credited or event
        self.age += 2
        return self.delta
