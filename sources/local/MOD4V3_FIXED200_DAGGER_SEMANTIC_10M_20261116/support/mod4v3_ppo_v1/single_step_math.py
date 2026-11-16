"""Shared course geometry, independent state transition and real support qualification."""
from dataclasses import dataclass
import torch

@dataclass(frozen=True)
class CourseSpec:
    heights: tuple = (.20,)
    edge: float = 1.5
    half_width: float = 1.5
    radius: float = .0625
    wheel_margin: float = .025
    body_margin: float = .12
    support_force: float = 5.
    maximum_speed: float = .6
    minimum_entry_speed: float = .1
    hold_seconds: float = .4
    maximum_angle: float = 25.*3.141592653589793/180.
    maximum_rate: float = 1.5
    settle_seconds: float = 1.5
    review_fraction: float = 0.
    failures_to_demote: int = 3

SPEC=CourseSpec()
COURSE='fixed_200mm_serial_teacher_v1'

def advance(mastered,episode_level,failures,success,attempted):
    zeros=torch.zeros_like(mastered)
    flags=torch.zeros_like(success,dtype=torch.bool)
    return zeros,zeros,flags,flags

def supported_upper(wheel_x,wheel_y,wheel_z,force_z,height):
    tolerance=(height*.30).clamp(.012,.025)
    return ((wheel_x<SPEC.edge-SPEC.wheel_margin)&(wheel_x>-SPEC.edge+.1)&
            (wheel_y.abs()<SPEC.half_width-.1)&
            ((wheel_z-(height[:,None]+SPEC.radius)).abs()<tolerance[:,None])&
            (force_z>SPEC.support_force))

def stable_completion(upper,body_x,pitch,roll,rate,vertical_speed,entry_speed,maximum_speed,entry_seen,failed,active):
    return (upper.all(1)&(body_x<SPEC.edge-SPEC.body_margin)&
            (body_x>-SPEC.edge+.2)&(pitch.abs()<SPEC.maximum_angle)&
            (roll.abs()<SPEC.maximum_angle)&(rate<SPEC.maximum_rate)&
            (vertical_speed.abs()<.25)&entry_seen&
            (entry_speed>=SPEC.minimum_entry_speed)&(entry_speed<=SPEC.maximum_speed)&
            (maximum_speed<=SPEC.maximum_speed)&(~failed)&active)

def first_landings(already,upper,active):
    gained=upper&(~already)&active[:,None]
    return gained,already|gained
