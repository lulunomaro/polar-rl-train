"""Ordered finite reward: retraction credit is unavailable before support transfer."""
import torch

def ordered_credit(current,best,contacted,retract_ready):
    enabled=torch.stack((contacted,contacted,retract_ready),dim=1)
    gain=(current-best).clamp_min(0)*enabled
    return gain,torch.where(enabled,torch.maximum(current,best),best)

def world_tread_clearance(wheel_z,stage):
    return wheel_z-.0625-(stage[:,None]+1)*.2
