"""Training-only reward accounting; idle pre-wall behaviour cannot farm net survival reward."""
import torch,math

def fixed200_reward(base,event,stair,command,vx,speed,pitch,yaw,height_error,wheel_lifting,landed,landing_seen,no_progress_seconds,wheel_actions,speed_limit,dt,height_aux_active):
    moving=command>.1
    pre=stair & moving & (~landed)
    stalled=pre & ((vx<command*.35)|(yaw.abs()>math.radians(15))|(no_progress_seconds>.4))
    removed=torch.where(stalled,base.clamp_min(0),torch.zeros_like(base))
    stand=8.*speed.square()*(command.abs()<.05)
    tilt=2.*((pitch.abs()-math.radians(15)).clamp_min(0)/math.radians(20)).square()
    rollback=6.*(-vx).clamp_min(0).square()*landing_seen
    reverse=.1*(-wheel_actions).clamp_min(0).square().sum(-1)*landing_seen*moving
    overspeed=4.*(speed-speed_limit).clamp_min(0).square()
    height=.25*(height_error/.10).square().clamp_max(1.)*(~wheel_lifting)*height_aux_active
    heading=1.5*(yaw.sin()/math.sin(math.radians(10))).square()*moving
    slow=2.*(command-vx).clamp_min(0).square()*pre
    idle=.5*stalled
    penalties=torch.stack((stand,tilt,rollback,reverse,overspeed,height,heading,slow,idle),1)*stair[:,None]*dt
    result=base-removed+event-penalties.sum(1)
    # Outside E1, preserve the exact original scalar reward.
    result=torch.where(stair,result,base)
    return result,dict(base=base,positive_base_removed=removed,event=event,penalties=penalties,total=result,stalled=stalled,pure_stall=stalled&(event<=1e-9))
