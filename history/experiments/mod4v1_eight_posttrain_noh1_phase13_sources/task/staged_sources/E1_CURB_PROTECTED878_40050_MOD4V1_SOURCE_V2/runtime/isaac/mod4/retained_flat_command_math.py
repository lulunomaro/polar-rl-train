"""Undeployed command-only repair candidate. No SDK, actor, plant or gate imports.

Eligibility must be provided by actual plane_for_rm assignment plus verified
physical support/clearance, never a label supplied to actor observations.
Standing20%, terrain proportions and all non-eligible low-speed commands stay
unchanged. Within eligible non-standing plane, half signed straight, half old
world-progress projection; this is a command conditional, not terrain quotas.
No pure high-rate spin, teacher, old off-policy replay, S7 or S8 expansion.
"""
import math
import torch

def sample_commands(generator, eligible_flat, standing, heading):
    assert eligible_flat.dtype==standing.dtype==torch.bool
    assert eligible_flat.shape==standing.shape==heading.shape
    u=torch.rand((len(heading),5),generator=generator,device=heading.device)
    available=eligible_flat & ~standing
    linear=available & (u[:,0]<.5)
    moving=available & ~linear
    signed=torch.where(u[:,1]<.5,-1.,1.)
    direction=(2*u[:,3]-1)*math.pi
    yaw=signed*(1+u[:,2])
    command=torch.zeros((len(heading),3),device=heading.device,dtype=heading.dtype)
    command[:,0]=.6*u[:,4]-.3
    command[linear,0]=signed[linear]*(1.+.5*u[linear,4])
    command[moving,0]=torch.cos(heading[moving]-direction[moving])
    command[moving,2]=yaw[moving]
    command[standing]=0.
    return dict(command=command,linear=linear,moving=moving,
                world_direction=direction,signed_yaw=torch.where(moving,yaw,0.))

def update_world_projection(command, moving, heading, world_direction, signed_yaw):
    """V=.5: BODY vx=2Vcos(theta-alpha),vy0; no position correction."""
    command[moving,0]=torch.cos(heading[moving]-world_direction[moving])
    command[moving,1]=0.
    command[moving,2]=signed_yaw[moving]
    return command
