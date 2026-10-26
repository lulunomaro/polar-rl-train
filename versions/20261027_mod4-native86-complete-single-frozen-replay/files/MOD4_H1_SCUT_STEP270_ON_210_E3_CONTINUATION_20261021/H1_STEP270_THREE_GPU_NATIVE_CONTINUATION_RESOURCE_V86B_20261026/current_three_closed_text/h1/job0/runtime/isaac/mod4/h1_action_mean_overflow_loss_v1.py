"""Owned H1 optimization repair candidate; never changes actions, STD or reward."""
import math
import torch
COEFFICIENT=0.001
ACTION_BOUND=6.0

def mean_overflow_loss(mean,coefficient=COEFFICIENT,bound=ACTION_BOUND):
 if not isinstance(mean,torch.Tensor) or mean.ndim!=2 or mean.shape[1]!=6 or mean.shape[0]==0:raise ValueError('Expected nonempty six-action mean batch')
 if not mean.is_floating_point() or not bool(torch.isfinite(mean).all()):raise ValueError('Expected finite floating actor means')
 if not math.isfinite(coefficient) or not 0<=coefficient<=COEFFICIENT:raise ValueError('Unreviewed loss coefficient')
 if bound!=ACTION_BOUND:raise ValueError('Original action clip6 bound required')
 excess=(mean.abs()-bound).clamp_min(0)
 return coefficient*excess.square().mean()
