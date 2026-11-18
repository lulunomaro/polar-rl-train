"""Training-only reward accounting; anti-sprint, anti-squat, and top parking alignment."""
import math
import torch


def fixed200_reward(
    base,
    event,
    stair,
    command,
    vx,
    speed,
    pitch,
    yaw,
    height_error,
    wheel_lifting,
    landed,
    landing_seen,
    no_progress_seconds,
    wheel_actions,
    speed_limit,
    dt,
    height_aux_active,
):
    moving = command > 0.1
    pre = stair & moving & (~landed)
    stalled = pre & ((vx < command * 0.35) | (yaw.abs() > math.radians(15)) | (no_progress_seconds > 0.4))
    removed = torch.where(stalled, base.clamp_min(0), torch.zeros_like(base))
    stand = 12.0 * speed.square() * (command.abs() < 0.05)
    tilt = 2.0 * ((pitch.abs() - math.radians(15)).clamp_min(0) / math.radians(20)).square()
    rollback = 12.0 * (-vx).clamp_min(0).square() * landing_seen
    reverse = 0.30 * (-wheel_actions).clamp_min(0).square().sum(-1) * landing_seen * (moving | (vx < -0.02))
    soft_speed_cap = 10.0 * (speed - 0.54).clamp_min(0).square() * moving
    overspeed = 4.0 * (speed - speed_limit).clamp_min(0).square() + soft_speed_cap
    height = 0.30 * (height_error / 0.10).square().clamp_max(2.5) * (~wheel_lifting) * height_aux_active
    wheel_sym = 0.25 * (wheel_actions[:, 0] - wheel_actions[:, 1]).square()
    heading = 1.5 * (yaw.sin() / math.sin(math.radians(10))).square() * moving + wheel_sym
    slow = 0.1 * (command - vx).clamp_min(0).square() * pre
    idle = 0.02 * stalled
    penalties = torch.stack((stand, tilt, rollback, reverse, overspeed, height, heading, slow, idle), 1) * stair[:, None] * dt
    result = base - removed + event - penalties.sum(1)
    # Outside E1, preserve the exact original scalar reward.
    result = torch.where(stair, result, base)
    return result, dict(
        base=base,
        positive_base_removed=removed,
        event=event,
        penalties=penalties,
        total=result,
        stalled=stalled,
        pure_stall=stalled & (event <= 1e-9),
    )
