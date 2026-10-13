"""One-factor frozen diagnostic action wrapper, never installed in production.

The original mechanical target guard still executes downstream. This function
changes only the left crank request to match the other leg's guarded motor-input
difference; it does not change the hip, wheel, command, plant, reward, or teacher.
Root must approve and lease a single GPU process before applying this candidate.
"""
import torch

FACTOR_ID='left_crank_requested_difference_match_right_v1'

def apply_factor(action, *, diff_min, diff_max, leg_scale=.5, offsets=None):
    assert action.ndim==2 and action.shape[1]==6 and torch.isfinite(action).all()
    assert leg_scale>0 and diff_min<diff_max
    clipped=action.clamp(-6.,6.)
    off=clipped.new_zeros((action.shape[0],4)) if offsets is None else offsets
    assert off.shape==(action.shape[0],4) and torch.isfinite(off).all()
    target=clipped[:,:4]*leg_scale+off
    right_difference=(target[:,2]-target[:,3]).clamp(diff_min,diff_max)
    replacement=(target[:,1]+right_difference-off[:,0])/leg_scale
    out=clipped.clone();out[:,0]=replacement.clamp(-6.,6.)
    assert torch.equal(out[:,1:],clipped[:,1:]), 'Exactly one requested action column changes'
    return out
