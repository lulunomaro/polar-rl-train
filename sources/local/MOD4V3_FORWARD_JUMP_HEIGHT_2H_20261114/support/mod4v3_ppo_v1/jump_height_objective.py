"""Height objectives use measured body motion and the unmodified gravity."""
import torch


def required_upward_speed(body_z, target_z):
    return torch.sqrt(2. * 9.81 * (target_z - body_z).clamp_min(0.))


def push_height_reward(body_z, velocity_z, reference_z, target_rise):
    upward = velocity_z.clamp_min(0.)
    predicted_rise = (body_z - reference_z + upward.square() / (2. * 9.81)).clamp_min(0.)
    speed_target = required_upward_speed(body_z, reference_z + target_rise)
    energy_progress = (predicted_rise / target_rise.clamp_min(.05)).clamp_max(1.5)
    speed_tracking = torch.exp(-((velocity_z - speed_target) / .65).square())
    return 3. * energy_progress + 2. * speed_tracking


def measured_height_bonus(body_increment, rim_increment, target_rise, target_clearance, orientation):
    return orientation * (45. * body_increment / target_rise.clamp_min(.05)
                          + 20. * rim_increment / target_clearance.clamp_min(.05))
