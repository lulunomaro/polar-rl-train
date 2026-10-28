"""Typed flat91 goal encoding, source only until fresh installed admission.

The 1460-vector is ten [value73, known-mask73] frames. Unknown values
must remain absent after normalization; a binary mask is a condition,
not a continuous feature to standardize with an older task's variance.
No module, parameter, buffer, RNG call, action or physical state is added.
"""
import torch

ENCODING = 'mod4.flat91.mask_aware_after_normalization.v1'


def masked_goal_conditioning(normalized, raw_goal):
    if normalized.shape != raw_goal.shape or raw_goal.shape[-1] != 1460:
        raise ValueError('exact ten [value73, binary known-mask73] goals required')
    shape = raw_goal.shape
    raw = raw_goal.reshape(*shape[:-1], 10, 146)
    norm = normalized.reshape(*shape[:-1], 10, 146)
    mask = raw[..., 73:]
    return torch.cat((norm[..., :73] * mask, mask), -1).reshape(shape)


def validate_goal_source(raw_goal):
    """Admission-only check; never installed as a physical-step GPU query."""
    if raw_goal.shape[-1] != 1460 or not torch.isfinite(raw_goal).all():
        raise ValueError('finite typed goal required')
    mask = raw_goal.reshape(*raw_goal.shape[:-1], 10, 146)[..., 73:]
    if not ((mask == 0) | (mask == 1)).all():
        raise ValueError('literal known/unknown mask required')
    return True
