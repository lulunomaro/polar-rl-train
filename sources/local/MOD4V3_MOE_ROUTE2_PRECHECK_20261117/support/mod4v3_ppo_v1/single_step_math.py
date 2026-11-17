"""Shared course geometry, independent state transition and real support qualification."""
from dataclasses import dataclass
import torch

@dataclass(frozen=True)
class CourseSpec:
    heights: tuple = (.10,.14,.17,.20)
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
COURSE='moe_route2_per_env_height_v1'

def advance(mastered,episode_level,success_streak,success,attempted):
    streak=torch.where(attempted,torch.where(success,success_streak+1,torch.zeros_like(success_streak)),success_streak)
    promoted=(streak>=3)&(mastered<len(SPEC.heights)-1)&(episode_level==mastered)
    new=mastered+promoted.long();streak=torch.where(promoted,torch.zeros_like(streak),streak.clamp_max(3))
    return new,streak,promoted,torch.zeros_like(promoted)

def supported_upper(wheel_x,wheel_y,wheel_z,force_z,height):
    tolerance=(height*.30).clamp(.012,.025)
    return ((wheel_x<SPEC.edge-SPEC.wheel_margin)&(wheel_x>-SPEC.edge+.1)&
            (wheel_y.abs()<SPEC.half_width-.1)&
            ((wheel_z-(height[:,None]+SPEC.radius)).abs()<tolerance[:,None])&
            (force_z>SPEC.support_force))

def stable_completion(upper,body_x,pitch,roll,rate,vertical_speed,entry_speed,maximum_speed,entry_seen,failed,active,maximum_allowed=None):
    limit=SPEC.maximum_speed if maximum_allowed is None else maximum_allowed
    return (upper.all(1)&(body_x<SPEC.edge-SPEC.body_margin)&
            (body_x>-SPEC.edge+.2)&(pitch.abs()<SPEC.maximum_angle)&
            (roll.abs()<SPEC.maximum_angle)&(rate<SPEC.maximum_rate)&
            (vertical_speed.abs()<.25)&entry_seen&
            (entry_speed>=SPEC.minimum_entry_speed)&(entry_speed<=limit)&
            (maximum_speed<=limit)&(~failed)&active)

def first_landings(already,upper,active):
    gained=upper&(~already)&active[:,None]
    return gained,already|gained
