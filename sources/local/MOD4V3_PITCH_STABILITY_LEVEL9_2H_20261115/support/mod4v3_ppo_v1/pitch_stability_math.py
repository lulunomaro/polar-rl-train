"""Body attitude and actual hard start/stop schedule, independent of leg theta."""
import math
import torch

def body_pitch(gravity_b):
    return torch.atan2(gravity_b[:,0],torch.linalg.vector_norm(gravity_b[:,1:],dim=-1))

def transition_command(age,speed):
    moving_time=(age-2.).clamp_min(0.)
    leg=torch.floor(moving_time/3.).long()
    phase=torch.remainder(moving_time,3.)
    moving=(age>=2.)&(phase<1.)
    sign=torch.where(leg%2==0,1.,-1.)
    return torch.where(moving,speed*sign,torch.zeros_like(speed)),moving,phase

def stability_cost(pitch,pitch_rate,active,dt=.02):
    excess=(pitch.abs()-math.radians(5.)).clamp_min(0.)
    return -dt*(10.*excess.square()+.35*pitch_rate.square())*active
