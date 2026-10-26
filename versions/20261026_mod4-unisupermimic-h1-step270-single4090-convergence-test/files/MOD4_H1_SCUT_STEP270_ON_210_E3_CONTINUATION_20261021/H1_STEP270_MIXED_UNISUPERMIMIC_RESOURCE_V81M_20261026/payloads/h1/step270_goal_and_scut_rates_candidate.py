"""CPU-reviewable H1 successor task. NOT installed, SDK-qualified, or trained.

SCUT reference: b8ff79f3df855faf9dc92f4a282bd80c42649466,
state_machines/jump_takeoff.py (takeoff_vel_z, release_vel_z_shortfall),
and airborne.py (air_wheel_zero_torque_exp, wheel_height_below_base_exp).
Copyright (c) 2026 SCUTRobotLab, MIT, for referenced reward formulae.

The .270m platform goal and heading/stop terms are explicit MOD4 adaptations.
This module accepts measured inputs only. It never selects actions, resets a
simulator, adds forces, touches a checkpoint, or constructs an optimizer.
A future SDK adapter must prove actual platform collider identity and contact.
"""
from dataclasses import dataclass
import torch

@dataclass(frozen=True)
class Contract:
    platform_top_m: float = .270
    physics_dt_s: float = .0025
    ready_callbacks: int = 80
    air_callbacks: int = 16
    landing_callbacks: int = 12
    stable_callbacks: int = 200
    support_N: float = 1.
    geometry_skin_m: float = .001
    stable_speed_m_s: float = .03
    stable_tilt_rad: float = .17453292519943295
    stable_yaw_rad: float = .2

def scut_phase_rates(*,push,airborne,landed,vz,release_reference_vz,
                     wheel_torque,wheel_bottom_relative_base,heading_error,
                     planar_speed):
    """Unweighted rates. No inherited foreign robot torque/length caps.

    push_vz and release_shortfall are the SCUT positive-vz / reference-shortfall
    formulas; their phase masks come from actual task truth. The reference
    velocity must come from an explicitly qualified trajectory planner, not
    sqrt(2*g*.27) misrepresented as guaranteed wheel clearance.
    """
    values=(vz,release_reference_vz,wheel_torque,wheel_bottom_relative_base,
            heading_error,planar_speed)
    if not all(torch.isfinite(v).all() for v in values):raise ValueError('nonfinite measured reward input')
    if not (release_reference_vz>=0).all():raise ValueError('negative release target')
    yaw=torch.atan2(torch.sin(heading_error),torch.cos(heading_error))
    return dict(
        push_vz=push.float()*vz.clamp_min(0),
        release_shortfall=push.float()*(release_reference_vz-vz).clamp_min(0),
        air_wheel_zero_torque=airborne.float()*torch.exp(-torch.square(wheel_torque.abs().amax(-1)/1.5)),
        # .22 and .01 are the explicitly traced existing MOD4/SCUT baseline,
        # not a .270m wheel-clearance target or a new leg hardware limit.
        wheel_below_base=airborne.float()*torch.exp(-torch.square(wheel_bottom_relative_base+.22)/.01).mean(-1),
        landing_heading_error=landed.float()*yaw.square(),
        landing_planar_speed=landed.float()*planar_speed.square())

class Step270Events:
    """Fresh ground-only episodes; success requires an actual top-surface hit.

    Runtime adapter admission is intentionally absent. Callers must provide
    proven authored collider footprint/edge crossings and platform contact IDs.
    Test fixtures are not simulation results and cannot admit a GPU launch.
    """
    def __init__(self,n,device='cpu',contract=Contract()):
        self.c=contract
        if contract.platform_top_m<.270:raise ValueError('Human minimum is 270mm')
        if contract.physics_dt_s!=.0025:raise ValueError('Unqualified physical clock')
        self.ready_ticks=torch.zeros(n,dtype=torch.long,device=device)
        self.air_ticks=self.ready_ticks.clone();self.land_ticks=self.ready_ticks.clone();self.stable_ticks=self.ready_ticks.clone()
        self.attempt=torch.zeros(n,dtype=torch.bool,device=device)
        self.launched=self.attempt.clone();self.edge=self.attempt.clone();self.landed=self.attempt.clone();self.success=self.attempt.clone()
        self.positive_vz=self.attempt.clone();self.progress=torch.zeros(n,device=device)

    def physical(self,*,request,ground_ready,nonwheel_clean,known_integrity,
                 wheel_N,wheel_bottom_world_z,wheel_contact_platform,
                 wheel_footprints_inside_top,both_wheel_edge_crossed,
                 root_vz,planar_speed,roll,pitch,heading_error):
        c=self.c
        if not known_integrity.all():raise ValueError('unknown/integrity rejection')
        for v in (wheel_N,wheel_bottom_world_z,root_vz,planar_speed,roll,pitch,heading_error):
            if not torch.isfinite(v).all():raise ValueError('nonfinite task witness')
        self.ready_ticks=torch.where(ground_ready&~request,self.ready_ticks+1,0)
        ready=self.ready_ticks>=c.ready_callbacks
        # Preserve previously obtained readiness at request edge, no air reset.
        if not hasattr(self,'was_ready'):self.was_ready=ready.clone()
        self.attempt|=request&self.was_ready
        self.was_ready=torch.where(request,self.was_ready,ready)
        self.positive_vz|=self.attempt&(root_vz>.05)
        air=self.attempt&self.positive_vz&(wheel_N<=c.support_N).all(-1)&nonwheel_clean
        self.air_ticks=torch.where(air,self.air_ticks+1,0)
        takeoff=(self.air_ticks>=c.air_callbacks)&~self.launched;self.launched|=takeoff
        actual_clear=(wheel_bottom_world_z>=c.platform_top_m).all(-1)
        self.edge|=self.launched&air&both_wheel_edge_crossed&actual_clear
        eligible=self.launched&air&nonwheel_clean
        peak=(wheel_bottom_world_z.amin(-1)/c.platform_top_m).clamp(0,1)
        next_progress=torch.maximum(self.progress,torch.where(eligible,peak,0))
        progress_delta=next_progress-self.progress;self.progress=next_progress
        on_top=(wheel_N>c.support_N).all(-1)&wheel_contact_platform.all(-1)&wheel_footprints_inside_top.all(-1)&(wheel_bottom_world_z>=c.platform_top_m-c.geometry_skin_m).all(-1)&nonwheel_clean
        self.land_ticks=torch.where(self.edge&on_top,self.land_ticks+1,0)
        landing=(self.land_ticks>=c.landing_callbacks)&~self.landed;self.landed|=landing
        yaw=torch.atan2(torch.sin(heading_error),torch.cos(heading_error))
        stable=self.landed&on_top&(root_vz.abs()<=c.stable_speed_m_s)&(planar_speed<=c.stable_speed_m_s)&(roll.abs()<c.stable_tilt_rad)&(pitch.abs()<c.stable_tilt_rad)&(yaw.abs()<c.stable_yaw_rad)
        self.stable_ticks=torch.where(stable,self.stable_ticks+1,0)
        recovered=(self.stable_ticks>=c.stable_callbacks)&~self.success;self.success|=recovered
        return dict(takeoff=takeoff,edge_cleared=self.edge.clone(),landing=landing,recovery=recovered,success=self.success.clone(),wheel_clearance_progress_delta=progress_delta)
