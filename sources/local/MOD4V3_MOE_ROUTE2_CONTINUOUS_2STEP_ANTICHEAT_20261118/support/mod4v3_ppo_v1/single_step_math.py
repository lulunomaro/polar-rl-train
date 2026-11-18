"""Shared 1-step (20cm) and continuous 2-step (20cm+20cm=40cm) geometry & support qualification."""
from dataclasses import dataclass
import torch


@dataclass(frozen=True)
class CourseSpec:
    heights: tuple = (0.20, 0.40)
    edge: float = 1.5
    edge_2step_s1: float = 2.6
    edge_2step_s2: float = 1.1
    half_width: float = 1.5
    half_width_2step_s1: float = 2.6
    half_width_2step_s2: float = 1.1
    radius: float = 0.0625
    wheel_margin: float = 0.025
    body_margin: float = 0.12
    support_force: float = 5.0
    maximum_speed: float = 0.6
    minimum_entry_speed: float = 0.1
    hold_seconds: float = 0.4
    maximum_angle: float = 25.0 * 3.141592653589793 / 180.0
    maximum_rate: float = 1.5
    settle_seconds: float = 1.0
    review_fraction: float = 0.25
    failures_to_demote: int = 3


SPEC = CourseSpec()
COURSE = 'route2_continuous_2step_anticheat_v1'


def advance(mastered, episode_level, success_streak, success, attempted):
    streak = torch.where(attempted, torch.where(success, success_streak + 1, torch.zeros_like(success_streak)), success_streak)
    promoted = (streak >= 2) & (mastered < len(SPEC.heights) - 1) & (episode_level == mastered)
    new = mastered + promoted.long()
    streak = torch.where(promoted, torch.zeros_like(streak), streak.clamp_max(2))
    return new, streak, promoted, torch.zeros_like(promoted)


def supported_step_band(wheel_x, wheel_y, wheel_z, force_z, x_max, x_min, half_y, step_z):
    tol = 0.024
    return (
        (wheel_x < x_max - SPEC.wheel_margin)
        & (wheel_x > x_min)
        & (wheel_y.abs() < half_y - 0.10)
        & ((wheel_z - (step_z + SPEC.radius)).abs() < tol)
        & (force_z > SPEC.support_force)
    )


def supported_upper(wheel_x, wheel_y, wheel_z, force_z, height):
    is_two = height > 0.30
    x_max = torch.where(is_two, wheel_x.new_full(height.shape, SPEC.edge_2step_s2), wheel_x.new_full(height.shape, SPEC.edge))
    x_min = -x_max + 0.10
    half_y = torch.where(is_two, wheel_x.new_full(height.shape, SPEC.half_width_2step_s2), wheel_x.new_full(height.shape, SPEC.half_width))
    return (
        (wheel_x < (x_max - SPEC.wheel_margin)[:, None])
        & (wheel_x > x_min[:, None])
        & (wheel_y.abs() < (half_y - 0.10)[:, None])
        & ((wheel_z - (height[:, None] + SPEC.radius)).abs() < 0.024)
        & (force_z > SPEC.support_force)
    )


def stable_completion(upper, body_x, pitch, roll, rate, vertical_speed, entry_speed, maximum_speed, entry_seen, failed, active, maximum_allowed=None, final_edge=None):
    limit = SPEC.maximum_speed if maximum_allowed is None else maximum_allowed
    edge = body_x.new_full(body_x.shape, SPEC.edge) if final_edge is None else final_edge
    return (
        upper.all(1)
        & (body_x < edge - SPEC.body_margin)
        & (body_x > -edge + 0.20)
        & (pitch.abs() < SPEC.maximum_angle)
        & (roll.abs() < SPEC.maximum_angle)
        & (rate < SPEC.maximum_rate)
        & (vertical_speed.abs() < 0.25)
        & entry_seen
        & (entry_speed >= SPEC.minimum_entry_speed)
        & (entry_speed <= limit)
        & (maximum_speed <= limit)
        & (~failed)
        & active
    )


def first_landings(already, upper, active):
    gained = upper & (~already) & active[:, None]
    return gained, already | gained
