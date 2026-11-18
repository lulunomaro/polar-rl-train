"""Anti-cheat measured top support & v=0 top parking; zero reward for hanging or reverse slide."""
import math
import torch


def dense_top_support(
    upper,
    active,
    pitch,
    roll,
    pitch_peak,
    invalid_contact,
    speed,
    speed_limit,
    hold_seconds,
    dt,
    stop_latched=None,
    vx=None,
    episode_speed_max=None,
):
    count = upper.long().sum(1)
    peak_cap = math.radians(25) if stop_latched is None else math.radians(38)
    pose_ok = (pitch.abs() < math.radians(25)) & (roll.abs() < math.radians(25)) & (pitch_peak <= peak_cap)
    base_ok = active & pose_ok & (~invalid_contact)

    if stop_latched is None:
        eligible = base_ok & (speed <= speed_limit)
        fraction = (hold_seconds / 0.4).clamp(0, 1)
        per_policy_step = torch.where(
            count == 2,
            0.4 + 0.4 * fraction,
            torch.where(count == 1, 0.10, torch.zeros_like(speed)),
        )
        reward = per_policy_step * eligible.to(speed.dtype) * (dt / 0.02)
        return reward, dict(
            top_support_count=count,
            top_pose_ok=pose_ok,
            top_reward_eligible=eligible,
            top_hold_fraction=fraction,
        )

    # Anti-cheat: require non-negative forward motion during un-latched climb; zero single-wheel reward unless actively advancing!
    no_reverse = torch.ones_like(active) if vx is None else (vx >= -0.02)
    advancing = torch.ones_like(active) if vx is None else (vx >= 0.05)
    move_eligible = base_ok & (~stop_latched) & (speed <= speed_limit) & no_reverse
    park_eligible = base_ok & stop_latched & (count == 2) & (speed <= 0.25) & (torch.ones_like(active) if vx is None else (vx >= -0.04))
    eligible = move_eligible | park_eligible

    fraction = (hold_seconds / 0.4).clamp(0, 1)
    single_step_rew = torch.where(advancing, torch.full_like(speed, 0.04), torch.zeros_like(speed))
    move_step = torch.where(
        count == 2,
        0.45 + 0.45 * fraction,
        torch.where(count == 1, single_step_rew, torch.zeros_like(speed)),
    )
    stillness = 1.0 - (speed / 0.25).clamp(0, 1)
    park_step = 0.65 + 0.45 * stillness
    per_policy_step = torch.where(stop_latched, park_step, move_step)

    if episode_speed_max is not None:
        quality = torch.where(episode_speed_max <= 0.60, 1.30, 0.70)
        per_policy_step = per_policy_step * quality

    reward = per_policy_step * eligible.to(speed.dtype) * (dt / 0.02)
    return reward, dict(
        top_support_count=count,
        top_pose_ok=pose_ok,
        top_reward_eligible=eligible,
        top_hold_fraction=fraction,
    )
