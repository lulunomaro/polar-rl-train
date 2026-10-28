"""Bounded mixture of actual replay starts; source candidate, not installed.

Half the requested batch targets the 200ms before takeoff through the requested
flight. The remainder is the original unconditional valid-start distribution.
If the replay lacks enough focused starts, original valid starts fill the batch.
No states, histories, actions, physical resets, rewards or terminals are edited.
Extra original sampler calls consume its RNG; RNG equivalence is not claimed.
"""
import math
import torch
from private_phase_frame_v1 import decode

CONTRACT = dict(schema='mod4.flat95.real_replay_task_focus.v1',
                numerator=1, denominator=2, maximum_original_sampler_calls=8,
                preparation_ticks=20, height_m=.05, policy_hz=100,
                unchanged_physical_timeout_ticks=500,
                insufficient_focus='fill_with_original_valid_starts',
                generated_or_modified_transitions=False,
                original_sampler_RNG_draw_count_unchanged=False)


def focused_mask(frames):
    info = decode(frames)
    age, delay = info['public_age'], info['delay_ticks']
    flight_ticks = 2 * math.sqrt(2 * 9.81 * .05) / 9.81 / .01
    valid = info['valid_actual'] & (age < 500)
    relative = age - 200 - delay
    # The second request occurs 250 controls after the first. Neither request
    # may invent an age beyond the original five-second episode.
    selected = ((relative >= -20) & (relative <= flight_ticks))
    selected |= ((relative >= 230) & (relative <= 250 + flight_ticks))
    return valid & selected


def attach_task_focused_starts(learner, *, diagnostic=None):
    assert not hasattr(learner, '_flat95_task_focused_starts')
    original = learner._sample_valid_starts
    totals = dict(calls=0, original_sampler_calls=0, requested_focus=0,
                  selected_focus=0, fallback_uniform=0, returned_starts=0)

    def sample(batch_size):
        assert type(batch_size) is int and batch_size > 0
        uniform = original(batch_size)
        requested = batch_size // 2
        starts, histories, count, draws = [], [], 0, 1
        candidate = uniform
        while True:
            start, history = candidate
            indices = focused_mask(start['f']).nonzero(as_tuple=False).squeeze(-1)
            indices = indices[:requested-count]
            if len(indices):
                starts.append({k: v[indices] for k, v in start.items()})
                histories.append({k: v[indices] for k, v in history.items()})
                count += len(indices)
            if count == requested or draws == 8:
                break
            candidate = original(batch_size)
            draws += 1
        # Whole rows and their matching histories stay paired. The original
        # uniform sample also supplies a truthful fallback when focus is absent.
        remaining = batch_size-count
        def combine(parts, base):
            return {k: torch.cat([*(p[k] for p in parts), v[:remaining]], dim=0)
                    for k, v in base.items()}
        result = (combine(starts, uniform[0]), combine(histories, uniform[1]))
        totals['calls'] += 1
        totals['original_sampler_calls'] += draws
        totals['requested_focus'] += requested
        totals['selected_focus'] += count
        totals['fallback_uniform'] += requested-count
        totals['returned_starts'] += batch_size
        if diagnostic is not None:
            diagnostic(dict(totals, last=dict(batch_size=batch_size,
                       requested_focus=requested, selected_focus=count,
                       fallback_uniform=requested-count, original_calls=draws)))
        return result

    learner._sample_valid_starts = sample
    learner._flat95_task_focused_starts = totals
    return totals
