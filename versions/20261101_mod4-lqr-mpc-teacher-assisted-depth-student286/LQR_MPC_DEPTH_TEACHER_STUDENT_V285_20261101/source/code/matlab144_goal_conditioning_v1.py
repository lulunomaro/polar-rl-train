"""Shared Pi/Critic fixed-unit conditioning for NEW144 root/leg goal slots.

No nn.Module/buffer/norm tensor is added or reset. ROOT configures the exact
named order once after readback and wires this SAME function to Pi/Critic.
"""
import torch

LEG_ORDER=('left_crank','left_hip','right_crank','right_hip')
ENCODING='mod4.matlab144.mask_aware_fixed_SI_root_and_own_leg_units.v1'
_SPEC=None


def configure_leg_goal_conditioning(joint_names,midpoint30,half_range30):
    global _SPEC
    names=tuple(joint_names)
    if len(names)!=30 or len(set(names))!=30 or len(midpoint30)!=30 or len(half_range30)!=30:
        raise ValueError('Exact named physical30 and source scale30 required')
    ids=tuple(names.index(n) for n in LEG_ORDER)
    spec=(tuple(13+i for i in ids),tuple(float(midpoint30[i]) for i in ids),tuple(float(half_range30[i]) for i in ids))
    if any(x<=0 for x in spec[2]):raise ValueError('Positive authored half ranges required')
    if _SPEC is not None and _SPEC!=spec:raise ValueError('Do not change Pi/Critic binding silently in one process')
    _SPEC=spec
    return dict(encoding=ENCODING,goal_slots4=spec[0],midpoint4=spec[1],half_range4=spec[2],
        root_goal_units='SI m/unitwxyz/mpersecond/radpersecond, not inheritedeps amplification',norm_tensor_changes=False)


def condition_with_spec(normalized,raw_goal,slots4,midpoint4,half_range4):
    if normalized.shape!=raw_goal.shape or raw_goal.shape[-1]!=1460:
        raise ValueError('Original10x146 goal required')
    raw=raw_goal.reshape(*raw_goal.shape[:-1],10,146)
    norm=normalized.reshape_as(raw)
    mask=raw[...,73:]
    values=norm[...,:73]*mask
    # Existing six PROCESS channels are dimensionless, not physical dq.
    values=values.clone()
    # Root velocity/orientation were constant in old134 goals despite mask1.
    # Use explicit SI/unit-quaternion values for this NEW full-motion task;
    # do not divide newlyvarying signals by inherited nearzero variance.
    values[...,:13]=raw[...,:13]*mask[...,:13]
    values[...,43:49]=(raw[...,43:49]/.01)*mask[...,43:49]
    ids=list(slots4)
    mid=raw.new_tensor(midpoint4);scale=raw.new_tensor(half_range4)
    values[...,ids]=((raw[...,ids]-mid)/scale)*mask[...,ids]
    return torch.cat((values,mask),-1).reshape_as(raw_goal)


def masked_goal_conditioning(normalized,raw_goal):
    if _SPEC is None:raise ValueError('ROOT must configure exact named leg goal conditioning before144 native use')
    return condition_with_spec(normalized,raw_goal,*_SPEC)


def validate_goal_source(raw_goal):
    if _SPEC is None:raise ValueError('Missing144 leg conditioning binding')
    raw=raw_goal.reshape(*raw_goal.shape[:-1],10,146)
    mask=raw[...,73:]
    if not torch.isfinite(raw_goal).all() or not ((mask==0)|(mask==1)).all():raise ValueError('Finite typed value/mask goal required')
    ids,mid,scale=_SPEC
    fixed=(raw[...,list(ids)]-raw.new_tensor(mid))/raw.new_tensor(scale)
    if not ((fixed.abs()<=1.00001)|(mask[...,list(ids)]==0)).all():raise ValueError('Active reference leg goal outside authored fixed units')
    return True
