"""Body attitude and actual hard start/stop schedule, independent of leg theta."""
import math
import torch

def body_pitch(gravity_b):
    return torch.atan2(gravity_b[:,0],torch.linalg.vector_norm(gravity_b[:,1:],dim=-1))

def _transition_ticks(age):
    # The policy contract is50Hz. Integer ticks avoid float32 boundary drift.
    tick=torch.round(age/.02).long()
    elapsed=(tick-100).clamp_min(0)
    return tick,elapsed,torch.remainder(elapsed,150)

def transition_command(age,speed):
    tick,elapsed,phase_tick=_transition_ticks(age)
    moving=(tick>=100)&(phase_tick<50)
    sign=torch.where(torch.div(elapsed,150,rounding_mode='floor')%2==0,1.,-1.)
    return torch.where(moving,speed*sign,torch.zeros_like(speed)),moving,phase_tick.to(age.dtype)*.02

def transition_window(age,speed):
    tick,_,phase_tick=_transition_ticks(age)
    return (tick>=100)&((phase_tick<20)|((phase_tick>=50)&(phase_tick<70)))

def stability_components(pitch,pitch_rate,active,dt=.02,transition_window=None,command_vx=None):
    """SCUT gravity-pitch shaping, with no deadband or uncalibrated lookahead."""
    command_vx=torch.zeros_like(pitch)if command_vx is None else command_vx
    gx=torch.sin(pitch)
    gain=.25*(2.*torch.exp(-command_vx.square()/3.)+2.).square()
    return torch.stack((-dt*gain*gx.square()*active,
                        -dt*.05*pitch_rate.square()*active,
                        -dt*2.*(1.-torch.exp(-gx.square()/.02))*active),dim=-1)

def stability_cost(pitch,pitch_rate,active,dt=.02,transition_window=None):
    return stability_components(pitch,pitch_rate,active,dt,transition_window).sum(-1)


def stability_active_mask(target, contact, support_seen, terminated, age):
    """Ground-start specialist remains charged during an unintended unload."""
    support_seen = support_seen | (target & contact)
    active = target & support_seen & (~terminated) & (age >= 1.)
    return support_seen, active
