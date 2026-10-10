"""Undeployed CPU-only candidate: fill the missing OLD flat pure-yaw command mode.

No SDK, actor, reward, plant, terrain geometry or gate imports. Actual verified
plane support/clearance is an external admission requirement. Standing stays
unchanged. World sampling remains the identical half of eligible non-standing
plane draws; half of the old straight half becomes old signed pure-yaw practice.
Other terrain remains gentle yaw0. This does not authorize rough spin or S7/S8.
"""
import math
import torch
PROFILE='E1_G3_verified_plane_straight_world_and_old_pure_v2_CPU_ONLY'
OLD_FLAT_PURE_ABS_RATES=(1.,2.,4.,6.,8.,10.,4.*math.pi)

def sample_commands(generator,eligible_flat,standing,heading):
 assert eligible_flat.dtype==standing.dtype==torch.bool
 assert eligible_flat.shape==standing.shape==heading.shape
 u=torch.rand((len(heading),5),generator=generator,device=heading.device)
 available=eligible_flat & ~standing
 linear=available & (u[:,0]<.25)
 pure=available & (u[:,0]>=.25) & (u[:,0]<.5)
 moving=available & (u[:,0]>=.5)
 sign=torch.where(u[:,1]<.5,-1.,1.)
 direction=(2*u[:,3]-1)*math.pi
 yaw=sign*(1.+u[:,2])
 rates=torch.tensor(OLD_FLAT_PURE_ABS_RATES,device=heading.device,dtype=heading.dtype)
 pure_yaw=sign*rates[torch.floor(u[:,2]*len(rates)).long().clamp_max(len(rates)-1)]
 command=torch.zeros((len(heading),3),device=heading.device,dtype=heading.dtype)
 command[:,0]=.6*u[:,4]-.3
 command[linear,0]=sign[linear]*(1.+.5*u[linear,4])
 command[moving,0]=torch.cos(heading[moving]-direction[moving])
 command[moving,2]=yaw[moving]
 command[pure,0]=0.
 command[pure,2]=pure_yaw[pure]
 command[standing]=0.
 return dict(command=command,linear=linear,pure=pure,moving=moving,
             world_direction=direction,signed_yaw=torch.where(moving,yaw,0.),
             pure_signed_yaw=torch.where(pure,pure_yaw,0.))

def update_world_projection(command,moving,heading,world_direction,signed_yaw):
 command[moving,0]=torch.cos(heading[moving]-world_direction[moving])
 command[moving,1]=0.
 command[moving,2]=signed_yaw[moving]
 return command
