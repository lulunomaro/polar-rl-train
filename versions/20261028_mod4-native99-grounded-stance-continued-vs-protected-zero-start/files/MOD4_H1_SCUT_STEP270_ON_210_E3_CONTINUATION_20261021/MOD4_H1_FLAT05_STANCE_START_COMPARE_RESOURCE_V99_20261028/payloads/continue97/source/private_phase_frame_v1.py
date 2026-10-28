"""Packed private phase lookup frame; original public age/reset/RNG unchanged.

Units:100Hz control ticks. delay=env_id%250, frame=delay*1024+public_age.
The signed phase_age=public_age-delay retains initial200tick standing semantics.
No learner/replay modification, sampling, SDK or device-to-host scalar reads.
"""
import torch
STRIDE=1024
DELAY_PERIOD_TICKS=250
PUBLIC_EPISODE_MAX_TICKS=500
LOOKAHEAD_LIMITS={'world':32,'policy':10}

def _long(x):
 assert torch.is_tensor(x) and x.dtype==torch.long,'frame/age/env IDs must be long, no float truncation'
 return x

def encode(public_age,env_ids):
 """Return long packed frame; invalid actual ages/IDs get explicit sentinel-1."""
 age,ids=torch.broadcast_tensors(_long(public_age),_long(env_ids))
 assert age.device==ids.device
 valid=(age>=0)&(age<=PUBLIC_EPISODE_MAX_TICKS)&(ids>=0)
 frame=torch.remainder(ids,DELAY_PERIOD_TICKS)*STRIDE+age
 return torch.where(valid,frame,torch.full_like(frame,-1))

def decode(frame):
 """Preserve actual public age and delayed phase age, even for future lookups.

 A predicted age501 is not silently reset to0 or relabeled as actual age<=500.
 valid_actual flags the original physical episode bounds without a GPU sync.
 """
 f=_long(frame);delay=torch.div(f,STRIDE,rounding_mode='floor');age=torch.remainder(f,STRIDE)
 valid=(f>=0)&(delay>=0)&(delay<DELAY_PERIOD_TICKS)&(age<=PUBLIC_EPISODE_MAX_TICKS)
 return dict(delay_ticks=delay,public_age=age,phase_age=age-delay,valid_actual=valid)

def horizon_checks(frame,lookahead,*,kind):
 """Per-row masks; caller retains original done/reset handling.

 within_episode means a horizon does not cross the actual5s reset boundary.
 lookup_encoding_valid also describes terminal lookups up to the admitted
32(world)/10(policy) offsets without falsely making those actual physical ages.
 """
 assert kind in LOOKAHEAD_LIMITS and type(lookahead)is int and 0<=lookahead<=LOOKAHEAD_LIMITS[kind]
 before=decode(frame);after=decode(frame+lookahead)
 same_delay=after['delay_ticks']==before['delay_ticks']
 lookup=before['valid_actual']&same_delay&(after['public_age']<=PUBLIC_EPISODE_MAX_TICKS+lookahead)
 return dict(within_episode=before['valid_actual']&after['valid_actual']&same_delay,
  lookup_encoding_valid=lookup,same_private_delay=same_delay,
  public_age=before['public_age'],phase_age=before['phase_age'],
  next_public_age=after['public_age'],next_phase_age=after['phase_age'])

def horizon_valid(frame,lookahead,*,kind):
 return horizon_checks(frame,lookahead,kind=kind)['within_episode']
