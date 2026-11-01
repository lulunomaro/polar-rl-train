"""Isolated ideal kinematics; not a controller or a physics acceptance result.

For a planar nonholonomic two-wheel chassis, vy_body = 0. When yaw sweeps
uniformly through complete turns, vx_body = 2*V*cos(yaw-direction) has mean
world velocity V along direction, with a twice-yaw lateral ripple. A speed
clip changes that mean, so desired net progress and instantaneous speed must
be reported separately. This does not assume the learned robot can follow it.
"""
import torch


def body_command(speed, direction, heading, body_speed_limit=1.5):
    """Return feasible planar body vx/vy references for a world progress goal.

    Inputs broadcast normally. The unconstrained instantaneous peak is 2*speed.
    No lateral body velocity is requested. Callers must independently evaluate
    actual displacement, lateral error, yaw tracking and hardware constraints.
    """
    if body_speed_limit <= 0:
        raise ValueError('body_speed_limit must be positive')
    vx = 2 * speed * torch.cos(heading - direction)
    vx = vx.clamp(-body_speed_limit, body_speed_limit)
    return vx, torch.zeros_like(vx)


def project_velocity(velocity_xy_w, direction):
    """Signed along-goal and cross-goal velocity, not speed magnitude."""
    cosine = torch.cos(direction)
    sine = torch.sin(direction)
    along = velocity_xy_w[..., 0] * cosine + velocity_xy_w[..., 1] * sine
    cross = -velocity_xy_w[..., 0] * sine + velocity_xy_w[..., 1] * cosine
    return along, cross
