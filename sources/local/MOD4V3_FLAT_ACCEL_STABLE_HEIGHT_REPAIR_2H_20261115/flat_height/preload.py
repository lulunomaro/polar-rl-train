"""Measure stroke and stored energy relative to the physical extended stop."""
import torch

PRELOAD_STROKE_M = .030
LOW_CHASSIS_M = .275
MAX_PREPARATION_S = .32


def spring_state(position, lower, upper, reference, stiffness):
    q = torch.maximum(lower, torch.minimum(position, upper))
    compression = upper - q
    energy = .5 * stiffness * ((reference - q).square() - (reference - upper).square())
    return compression, energy.clamp_min(0.).sum(-1)


def ready_to_push(compression, chassis_height):
    return (compression.amin(-1) >= PRELOAD_STROKE_M) | (chassis_height <= LOW_CHASSIS_M)


def release_fraction(start_energy, released_energy):
    return (released_energy / start_energy.clamp_min(1.)).clamp(0., 1.)
