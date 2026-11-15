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

def stability_components(pitch,pitch_rate,active,dt=.02,transition_window=None):
    """The added lookahead is a training cost, not a dynamics or command filter."""
    excess=(pitch.abs()-math.radians(5.)).clamp_min(0.)
    predicted=pitch+.2*pitch_rate
    future_excess=(predicted.abs()-math.radians(5.)).clamp_min(0.)
    window=torch.ones_like(active) if transition_window is None else transition_window
    return torch.stack((-dt*30.*excess.square()*active,
                        -dt*3.5*pitch_rate.square()*active,
                        -dt*60.*future_excess.square()*active*window),dim=-1)

def stability_cost(pitch,pitch_rate,active,dt=.02,transition_window=None):
    return stability_components(pitch,pitch_rate,active,dt,transition_window).sum(-1)


def stability_active_mask(target, contact, support_seen, terminated, age):
    """Ground-start specialist remains charged during an unintended unload."""
    support_seen = support_seen | (target & contact)
    active = target & support_seen & (~terminated) & (age >= 1.)
    return support_seen, active
