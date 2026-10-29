"""SOURCE CANDIDATE116: direct world command and BOTH wheel-bottom target tracking.

No positive term for force loss, generic flight, body height, tuck or extension.
No action/force/reset controller; these functions return reward scalars only.
Not admitted to any runtime or training. Parameters are engineering proposals.
"""
from dataclasses import dataclass
import torch

@dataclass(frozen=True)
class CommandReward:
    dt:float=.01
    speed:float=.5
    velocity_sigma:float=.35
    step_height:float=.27
    edge_x:float=.35
    far_x:float=1.15
    half_width:float=.6
    goal_root_x:float=.75
    final_brake_distance:float=.2
    near_start:float=.18
    near_full:float=.04
    boundary_ramp:float=.02
    height_coefficient:float=.5
    supported_landing_coefficient:float=2.
    quiet_coefficient:float=1.
    score_scale:float=4.
    quiet_speed_sigma:float=.15

def smooth01(x):
    t=x.clamp(0,1)
    return t*t*(3-2*t)

def modes(low,high,force_z,root_x,p=CommandReward()):
    """Own wheel min/max mesh supports, in meters relative to own world floor.

    Force history is only a declared landing surrogate, never airborne truth.
    Unloaded wheels cannot unlock jump rewards. Both front edges must approach.
    """
    support=force_z.clamp_min(0)/(force_z.clamp_min(0)+1.)
    front_gap=p.edge_x-high[...,0].amin(-1)
    near=smooth01((p.near_start-front_gap)/(p.near_start-p.near_full))
    rear=low[...,0].amin(-1)-p.edge_x
    far=p.far_x-high[...,0].amax(-1)
    yl=low[...,1].amin(-1)+p.half_width
    yr=p.half_width-high[...,1].amax(-1)
    footprint=smooth01(rear/p.boundary_ramp)*smooth01(far/p.boundary_ramp)*smooth01(yl/p.boundary_ramp)*smooth01(yr/p.boundary_ramp)
    top_height=torch.exp(-((low[...,2]-p.step_height)/.02).square().mean(-1))
    P=footprint*top_height*support.prod(-1)
    near=near*smooth01(far/p.boundary_ramp)*smooth01(yl/p.boundary_ramp)*smooth01(yr/p.boundary_ramp)
    base_vx=p.speed*((p.goal_root_x-root_x)/p.final_brake_distance).clamp(-1,1)
    return dict(near=near,top_support=P,footprint=footprint,front_gap_both=front_gap,base_command_vx=base_vx)

def height_score(wheel_bottom2,p=CommandReward()):
    """Target .27m for EACH own wheel bottom, never chassis/COM height.

    Score zero at ground, max ONLY at target, decreases above target.
    The lower of the two target scores prevents rewarding a one-wheel lift.
    No broad high-reward body-height plateau and no positive flight offset.
    """
    u=wheel_bottom2/p.step_height
    each=(2*u-u.square()).clamp_min(0)
    return each.amin(-1)

def evaluate(m,mode,legacy_nonrequest_recovery,effort_quality,p=CommandReward()):
    """Every selected summand is returned verbatim; total is their exact sum.

    effort_quality is a bounded [exp(-.5),1] attenuation derived from the
    retained nonpositive action/torque/limit terms, independent of mode blending.
    A runtime adapter is REQUIRED to supply actual low/high world mesh supports.
    """
    for x in (m['wheel_bottom2'],m['world_velocity3'],m['world_angular_velocity3'],m['request_active'],effort_quality):
        if not bool(torch.isfinite(x).all()):raise ValueError('nonfinite command reward input')
    P=mode['top_support'];near=mode['near'];v=m['world_velocity3']
    desired_x=mode['base_command_vx']*(1-P)
    error=(v[...,0]-desired_x).square()+v[...,1].square()
    velocity=torch.exp(-error/p.velocity_sigma**2)
    heading=(1-m['heading_cos'].clamp(-1,1)).clamp_min(0)
    alignment=torch.exp(-heading/(1-.9800665778412416)-m['root_y'].square()/.3**2)
    # A stationary hop has EXACTLY ZERO height bonus. Slow bouncing has a
    # quadratic small factor; it cannot replace tracking the +.5m/s command.
    forward_fraction=(v[...,0]/p.speed).clamp(0,1).square()
    H=height_score(m['wheel_bottom2'],p)
    quiet=torch.exp(-v[...,:2].square().sum(-1)/p.quiet_speed_sigma**2
        -v[...,2].square()/p.quiet_speed_sigma**2
        -m['world_angular_velocity3'].square().sum(-1)/.3**2
        -(1-m['upright_cos'].clamp(-1,1)).clamp_min(0)/(1-.984807753012208)
        -heading/(1-.9800665778412416))
    active=m['request_active'];k=p.score_scale*p.dt*effort_quality
    selected=dict(
        command_world_velocity=k*velocity*alignment*active,
        both_wheel_height_270_with_forward_command=k*p.height_coefficient*near*(1-P)*H*forward_fraction*alignment*active,
        supported_top_landing=k*p.supported_landing_coefficient*P*active,
        supported_top_quiet=k*p.quiet_coefficient*P*quiet*active,
        original_nonrequest_recovery=(1-active)*legacy_nonrequest_recovery)
    total=sum(selected.values())
    if not bool(torch.isfinite(total).all()):raise ValueError('nonfinite reward')
    return dict(total=total,selected_terms=selected,command_vx=desired_x,command_wheel_bottom_height=p.step_height,
        both_wheel_height_score=H,forward_command_fraction_squared=forward_fraction,
        planning_top_support=P,planning_near=near,quiet=quiet,
        no_airborne_success_inferred=True,not_runtime_admitted=True)
