"""Declared mean-domain auxiliary loss using only already-published policy modes."""
import math
import torch

COEFFICIENT = .001
ACTION_BOUND = 6.

def public4_mean_overflow_loss(mean, policy, coefficient=COEFFICIENT, bound=ACTION_BOUND):
    if not (torch.is_tensor(mean) and torch.is_tensor(policy)):
        raise ValueError('Tensor inputs required')
    if mean.ndim != 2 or mean.shape[1] != 6 or mean.shape[0] == 0 or policy.shape != (mean.shape[0], 35):
        raise ValueError('Exact original six actions and normal35 policy rows required')
    if not mean.is_floating_point() or policy.dtype != mean.dtype or policy.device != mean.device:
        raise ValueError('Matching floating dtype and device required')
    if not (math.isfinite(coefficient) and 0 <= coefficient <= .001 and bound == 6.):
        raise ValueError('Declared coefficient and original action bound required')
    if not torch.isfinite(mean).all() or not torch.isfinite(policy).all():
        raise ValueError('Nonfinite input')
    modes = policy[:, 28:35]
    if not (((modes == 0) | (modes == 1)).all() and (modes.sum(-1) == 1).all() and ((modes[:, 0] == 1) | (modes[:, 4] == 1)).all()):
        raise ValueError('Actual published normal0/public4 onehot required')
    request = modes[:, 4].bool()
    if not request.any() or coefficient == 0:
        return mean.sum() * 0.
    loss = coefficient * torch.relu(mean[request].abs() - bound).square().mean()
    if not torch.isfinite(loss):
        raise ValueError('Nonfinite auxiliary loss')
    return loss
