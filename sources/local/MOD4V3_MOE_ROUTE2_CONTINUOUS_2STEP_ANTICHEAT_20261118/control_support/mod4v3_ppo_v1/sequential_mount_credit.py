"""Finite sequential credit: rear preparation, real mount, then wheel lift/place."""
import torch


def transfer_scores(longitudinal, reference, wheel_z, stage, inward, cleared):
    lower = stage[:, None] * .2
    rear = ((reference - longitudinal) / .08).clamp(0., 1.)
    lift = ((wheel_z - .0625 - lower - .005) / .210).clamp(0., 1.)
    clearance = wheel_z - .0625 - (lower + .2)
    placement = ((inward - .02) / .15).clamp(0., 1.)
    placement = placement * cleared * (clearance >= -.01)
    return torch.stack((rear, lift, placement), dim=-1), lift


def transfer_credit(current, best, enabled):
    gain = (current - best).clamp_min(0.) * enabled
    updated = torch.where(enabled, torch.maximum(best, current), best)
    weights = current.new_tensor([.2, .5, .1])
    weighted = (gain * weights).sum(-1).mean(1)
    return weighted, updated, gain


def load_credit(current, best, enabled):
    gain = (current - best).clamp_min(0.) * enabled
    updated = torch.where(enabled, torch.maximum(best, current), best)
    return gain, updated


def lift_regression(lift, best_lift, enabled):
    return ((best_lift - lift - .05).clamp(0., 1.)).mean(1) * enabled
