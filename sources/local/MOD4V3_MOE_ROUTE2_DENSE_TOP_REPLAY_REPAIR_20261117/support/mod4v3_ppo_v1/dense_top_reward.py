"""Dense measured top support; never award floor contact or an overturned pose."""
import math
import torch

def dense_top_support(upper, active, pitch, roll, pitch_peak, invalid_contact, speed, speed_limit, hold_seconds, dt):
    count=upper.long().sum(1)
    pose_ok=(pitch.abs()<math.radians(25))&(roll.abs()<math.radians(25))&(pitch_peak<=math.radians(25))
    eligible=active&pose_ok&(~invalid_contact)&(speed<=speed_limit)
    fraction=(hold_seconds/.4).clamp(0,1)
    per_policy_step=torch.where(count==2,.4+.4*fraction,torch.where(count==1,.10,torch.zeros_like(speed)))
    reward=per_policy_step*eligible.to(speed.dtype)*(dt/.02)
    return reward,dict(top_support_count=count,top_pose_ok=pose_ok,top_reward_eligible=eligible,top_hold_fraction=fraction)
