"""Causal cycle cross-drift estimator. No simulator or policy dependency.

Subtract the ideal periodic cross displacement -V cos(2 phi)/(2 omega)
inside the current yaw cycle. A completed actual 2pi cycle contributes its
measured cross displacement. Normal periodic swing is not a drift penalty.
The partial-cycle correction assumes the requested constant signed yaw; it
is an engineering reward estimator, not a material-contact measurement.
"""
import math
import torch

VERSION = 'phase_compensated_cycle_cross_v1'


class CycleCrossDrift:
    def __init__(self, count, device='cpu', dtype=torch.float32):
        self.valid = torch.zeros(count, device=device, dtype=torch.bool)
        self.xy = torch.zeros((count, 2), device=device, dtype=dtype)
        self.anchor = self.xy.clone()
        self.heading = torch.zeros(count, device=device, dtype=dtype)
        self.angle = self.heading.clone()
        self.anchor_angle = self.heading.clone()
        self.elapsed = self.heading.clone()
        self.last_cross = self.heading.clone()
        self.last_duration = self.heading.clone()
        self.direction = self.heading.clone()
        self.yaw = self.heading.clone()
        self.goal = self.heading.clone()
        self.clock = self.heading.clone()
        self.net_cross = self.heading.clone()
        self.cycles = torch.zeros(count, device=device, dtype=torch.long)

    def reset(self, ids=None):
        ids = slice(None) if ids is None else ids
        self.valid[ids] = False
        self.net_cross[ids] = 0
        self.cycles[ids] = 0

    def update(self, xy, heading, direction, yaw, goal, active, clock, dt):
        changed = ((clock < self.clock - 1e-6)
                   | ((direction-self.direction).abs() > 1e-6)
                   | ((yaw-self.yaw).abs() > 1e-6)
                   | ((goal-self.goal).abs() > 1e-6))
        begin = active & (~self.valid | changed)
        work = active & self.valid & ~changed
        self.anchor[begin] = xy[begin]
        self.anchor_angle[begin] = heading[begin]
        self.angle[begin] = heading[begin]
        self.elapsed[begin] = 0
        self.last_cross[begin] = 0
        self.last_duration[begin] = 0
        self.cycles[begin] = 0
        delta = torch.atan2(torch.sin(heading-self.heading), torch.cos(heading-self.heading))
        next_angle = self.angle + torch.where(work, delta, 0)
        next_elapsed = self.elapsed + torch.where(work, dt, 0)
        safe_yaw = torch.where(yaw.abs() >= .5, yaw, torch.ones_like(yaw))
        sign = safe_yaw.sign()
        progress = sign * (next_angle-self.anchor_angle)
        crossed = work & (progress >= 2*math.pi)
        # At most one crossing per 10ms step in the 1--2 rad/s lesson.
        boundary_angle = self.anchor_angle + sign*2*math.pi
        fraction = ((boundary_angle-self.angle) / torch.where(delta.abs() > 1e-9, delta, torch.ones_like(delta))).clamp(0, 1)
        boundary_xy = self.xy + fraction[:, None]*(xy-self.xy)
        normal = torch.stack((-torch.sin(direction), torch.cos(direction)), dim=1)
        cycle_cross = ((boundary_xy-self.anchor)*normal).sum(dim=1)
        cycle_duration = self.elapsed + fraction*dt
        self.last_cross[crossed] = cycle_cross[crossed]
        self.last_duration[crossed] = cycle_duration[crossed]
        self.anchor[crossed] = boundary_xy[crossed]
        self.anchor_angle[crossed] = boundary_angle[crossed]
        next_elapsed[crossed] = (1-fraction[crossed])*dt
        self.cycles[crossed] += 1
        phi = next_angle-direction
        phi0 = self.anchor_angle-direction
        ideal_cross = -goal/(2*safe_yaw)*(torch.cos(2*phi)-torch.cos(2*phi0))
        partial_cross = ((xy-self.anchor)*normal).sum(dim=1)-ideal_cross
        denominator = (self.last_duration+next_elapsed).clamp_min(0)
        floor = (2*math.pi/safe_yaw.abs())/4
        estimate = (self.last_cross+partial_cross)/torch.maximum(denominator, floor)
        self.net_cross = torch.where(work, estimate, torch.zeros_like(estimate))
        self.xy.copy_(xy)
        self.heading.copy_(heading)
        self.angle.copy_(next_angle)
        self.elapsed.copy_(next_elapsed)
        self.direction.copy_(direction)
        self.yaw.copy_(yaw)
        self.goal.copy_(goal)
        self.clock.copy_(clock)
        self.valid.copy_(active)
        return self.net_cross.clone()

    def cost(self, scale=.10, max_cost=4.):
        return ((self.net_cross/scale)**2).clamp(max=max_cost)
