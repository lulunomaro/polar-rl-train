"""Strict data boundary for future native50Hz teacher pairs, no missing zeros.

This validates supplied natural buffers. No SDK packing implementation or
learned WM/Pi/Critic is implied by accepting a fixture.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class MeasuredClock208:
    control_uid: int
    physics_begin_tick: int
    physics_end_tick: int
    feedback_timestamps_us: tuple[int, int]
    action_callback_ticks: tuple[int, ...]
    physics_us: int = 2500
    control_us: int = 20000

    def validate(self):
        if self.physics_us != 2500 or self.control_us != 20000:
            raise ValueError('Wrong original physical clock')
        if self.physics_end_tick - self.physics_begin_tick != 8:
            raise ValueError('Missing original eight applied substeps')
        if self.action_callback_ticks != tuple(range(self.physics_begin_tick + 1, self.physics_end_tick + 1)):
            raise ValueError('Duplicate/skipped applied action callback')
        begin = self.physics_begin_tick * 2500
        if self.feedback_timestamps_us != (begin + 10000, begin + 20000):
            raise ValueError('Need both original feedback100Hz timestamps')


def validate_natural_pair(t, values, clock, selected_envs):
    clock.validate()
    dimensions = dict(s=127, s1=127, a=6, xi=31,
        original_policy35=35, original_teacher_raw6=6,
        original_critic38=38, auxiliary_before54=54, auxiliary_terminal54=54,
        episode_uid=(), command_uid=(), terminated_before_reset=(), timeout_before_reset=())
    if set(values) != set(dimensions) | {'eight_processed_targets6', 'all_original_reason_masks'}:
        raise ValueError('Incomplete or undeclared native pair; absent fields cannot be filled with zeros')
    for key, dimension in dimensions.items():
        value = values[key]
        expected = (selected_envs,) if dimension == () else (selected_envs, dimension)
        if not t.is_tensor(value) or tuple(value.shape) != expected:
            raise ValueError('Wrong native pair shape: ' + key)
        if value.is_floating_point() and (value.dtype != t.float32 or not bool(t.isfinite(value).all())):
            raise ValueError('Nonfinite/non-F32 natural state: ' + key)
    for key in ('episode_uid', 'command_uid'):
        if values[key].dtype != t.long or bool((values[key] < 0).any()):
            raise ValueError('Invalid natural UID: ' + key)
    for key in ('terminated_before_reset', 'timeout_before_reset'):
        if values[key].dtype != t.bool:
            raise ValueError('Pre-reset mask must have original bool dtype')
    targets = values['eight_processed_targets6']
    if targets.shape != (selected_envs, 8, 6) or targets.dtype != t.float32 or not bool(t.isfinite(targets).all()):
        raise ValueError('Need all eight real processed leg/wheel target vectors')
    if not isinstance(values['all_original_reason_masks'], dict) or not values['all_original_reason_masks']:
        raise ValueError('Original termination reasons missing')
    if any(v.shape != (selected_envs,) or v.dtype != t.bool for v in values['all_original_reason_masks'].values()):
        raise ValueError('Wrong original reason mask schema')
    return True
