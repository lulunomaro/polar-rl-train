"""Measured task outcomes, shared by simulation and acceptance tests."""
import torch

SCHEMA = 'MOD4V3_AUTONOMOUS_STAIR_OBS_V1'
SLOTS = ['base_mode', 'jump_request', 'measured_air', 'signed_edge_distance_m',
         'step_height_m', 'tread_depth_m', 'vertical_velocity_m_s']


def task_slots(request, air, distance, height, tread, vz):
    return torch.stack((torch.ones_like(distance), request.float(), air.float(),
                        distance.clamp(-2.4, 2.4), height.clamp(0., .5),
                        tread.clamp(0., 2.4), vz.clamp(-4., 4.) * .25), -1)


def scan_target(hits, root, yaw):
    direction = torch.stack((yaw.cos(), yaw.sin()), -1)
    along = ((hits[:, :, :2] - root[:, None, :2]) * direction[:, None]).sum(-1)
    order = along.argsort(-1)
    x = along.gather(1, order)
    z = hits[:, :, 2].gather(1, order)
    valid = torch.isfinite(z)
    rises = (z[:, 1:] - z[:, :-1] > .02) & valid[:, 1:] & valid[:, :-1]
    rises &= x[:, 1:] > .025
    index = rises.float().argmax(-1)
    has_edge = rises.any(-1)
    first = .5 * (x.gather(1, index[:, None]) + x.gather(1, index[:, None] + 1)).squeeze(1)
    bottom = z.gather(1, index[:, None]).squeeze(1)
    top = z.gather(1, index[:, None] + 1).squeeze(1)
    later = rises & (torch.arange(rises.shape[1], device=hits.device)[None] > index[:, None])
    next_index = later.float().argmax(-1)
    next_x = .5 * (x.gather(1, next_index[:, None]) + x.gather(1, next_index[:, None] + 1)).squeeze(1)
    distance = torch.where(has_edge, first, torch.full_like(first, 2.4))
    height = torch.where(has_edge, top - bottom, torch.zeros_like(top))
    tread = torch.where(has_edge & later.any(-1), next_x - first, torch.full_like(first, 1.5))
    return distance, height, tread


class Outcome:
    def __init__(self, n, device, dt=.02):
        self.dt = dt
        self.air = torch.zeros(n, device=device)
        self.max_air = self.air.clone()
        self.rim_peak = self.air.clone()
        self.stable = self.air.clone()
        self.max_stable = self.air.clone()
        self.air_pitch = self.air.clone()
        self.air_roll = self.air.clone()
        self.took_off = self.air.bool()
        self.qualified = self.took_off.clone()
        self.crossed = self.took_off.clone()
        self.landed = self.took_off.clone()
        self.success = self.took_off.clone()
        self.support = torch.zeros(25, n, 2, device=device)
        self.slot = 0

    def reset(self, ids):
        for key, value in vars(self).items():
            if torch.is_tensor(value):
                if key == 'support':
                    value[:, ids] = 0
                else:
                    value[ids] = 0

    def update(self, *, requested, wheel, forces, all_force, edge, next_edge,
               ground, height, vz, vx, command_vx, roll, pitch, angular, terminated):
        radius = .0625
        rim = wheel[:, :, 2].amin(-1) - radius - ground
        no_contact = torch.linalg.vector_norm(all_force, dim=-1).sum(-1) < 1.
        self.air = torch.where(no_contact & requested, self.air + self.dt, torch.zeros_like(self.air))
        self.max_air = torch.maximum(self.max_air, self.air)
        start = requested & ~self.qualified & (self.air >= .06 - 1e-6)
        start &= (vz > .1) & (rim > .005) & (wheel[:, :, 0].amax(-1) + radius < edge + .02)
        self.took_off |= start
        self.qualified = no_contact & (self.qualified | start)
        flying = requested & self.qualified & no_contact
        previous_peak = self.rim_peak.clone()
        self.rim_peak = torch.where(flying, torch.maximum(self.rim_peak, rim), self.rim_peak)
        self.air_pitch = torch.where(flying, torch.maximum(self.air_pitch, pitch.abs()), self.air_pitch)
        self.air_roll = torch.where(flying, torch.maximum(self.air_roll, roll.abs()), self.air_roll)
        crossing = flying & ~self.crossed & (wheel[:, :, 0].amin(-1) > edge + radius)
        crossing &= (rim >= height - .01) & (self.max_air >= .08 - 1e-6)
        self.crossed |= crossing
        footprint = (wheel[:, :, 0] > edge[:, None] + radius) & (wheel[:, :, 0] < next_edge[:, None] - radius)
        footprint &= wheel[:, :, 1].abs() < 4.25
        on_top = footprint & ((wheel[:, :, 2] - radius - ground[:, None] - height[:, None]).abs() < .025)
        on_top &= forces[:, :, 2] > 5.
        first_land = self.crossed & ~self.landed & on_top.all(-1)
        self.landed |= first_land
        self.support[self.slot] = on_top.float()
        self.slot = (self.slot + 1) % 25
        stable = self.landed & self.crossed & on_top.all(-1)
        stable &= (roll.abs() < .2617994) & (pitch.abs() < .2617994) & (angular.norm(dim=-1) < 2.)
        stable &= (vx > .1) & (vx < command_vx + .5) & ~terminated
        self.stable = torch.where(stable, self.stable + self.dt, torch.zeros_like(self.stable))
        self.max_stable = torch.maximum(self.max_stable, self.stable)
        accepted = stable & ~self.success & (self.stable >= .5 - 1e-6)
        accepted &= (self.support.mean(0) >= .8).all(-1)
        self.success |= accepted
        gain = (self.rim_peak.minimum(height + .05) - previous_peak.minimum(height + .05)).clamp_min(0.)
        return dict(takeoff=start, crossing=crossing, landing=first_land, success=accepted,
                    clearance_gain=gain, air=no_contact, rim=rim, top=on_top)
