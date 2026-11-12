"""Independent 270mm first-flight/actual-support acceptance at 400Hz.

Training state-machine success flags never enter this meter. Wheel bounds are
the authored finite cylinders, including width and current body orientation.
"""
import torch
from .math_ops import quat_apply, euler_xyz_from_quat, wrap_to_pi


def wheel_bounds(position, quaternion, contract):
    """Exact world AABB of each tire cylinder from the enhanced USD contract."""
    lows, highs = [], []
    for i, side in enumerate(('left', 'right')):
        geom = contract['geometry'][side+'_tire']
        if geom['type'] != 5 or geom['body'] != side+'_wheel':
            raise ValueError('Expected the authored tire cylinder')
        radius, half_width = geom['size'][:2]
        local_q = quaternion.new_tensor(geom['quat_wxyz'])
        cylinder_axis = quat_apply(local_q, quaternion.new_tensor([0., 0., 1.]))
        world_axis = quat_apply(quaternion[:, i], cylinder_axis[None].expand(len(position), -1))
        world_axis = world_axis/world_axis.norm(dim=-1, keepdim=True)
        # Sum the two perpendicular components, avoiding cancellation in
        # sqrt(1-axis**2) when a float32 axis is almost exactly horizontal.
        radial = torch.stack([world_axis[:, [j for j in range(3) if j != k]].norm(dim=-1)
                              for k in range(3)], -1)
        half_extent = radius*radial+half_width*world_axis.abs()
        offset = quaternion.new_tensor(geom['position_m'])[None].expand(len(position), -1)
        center = position[:, i]+quat_apply(quaternion[:, i], offset)
        lows.append(center-half_extent)
        highs.append(center+half_extent)
    return torch.stack(lows, 1), torch.stack(highs, 1)


class Strict270:
    def __init__(self, n, device, half_width=1.):
        self.n, self.device = n, device
        self.half_width = half_width
        self.support_seen = torch.zeros(n, dtype=torch.bool, device=device)
        self.previous_air = self.support_seen.clone()
        self.up = self.support_seen.clone()
        self.wholeclear = self.support_seen.clone()
        self.leading = self.support_seen.clone()
        self.ground_return = self.support_seen.clone()
        self.edge_return = self.support_seen.clone()
        self.success = self.support_seen.clone()
        self.flight_id = torch.zeros(n, dtype=torch.long, device=device)
        self.stable_ticks = torch.zeros_like(self.flight_id)
        self.stable_peak = self.stable_ticks.clone()
        self.support_ticks = self.stable_ticks.clone()
        self.support_peak = self.stable_ticks.clone()
        self.previous_rear = torch.full((n, 2), -torch.inf, device=device)
        self.previous_front = self.previous_rear.clone()
        self.rear_cross = torch.zeros(n, 2, dtype=torch.bool, device=device)
        self.front_cross = self.rear_cross.clone()

    def update(self, low, high, top_force, ground_force, wheel_net, nonwheel_force,
               root_velocity_w, root_quaternion, active):
        # xy bounds relative to the near platform edge x=.8, y=0.
        wheel_load = wheel_net.norm(dim=-1)
        airborne = ((wheel_load <= 1).all(-1) & (low[..., 2] > .005).all(-1)
                    & (nonwheel_force <= 1) & active)
        self.support_seen |= (wheel_load > 1).all(-1) & active
        self.flight_id += (airborne & ~self.previous_air & self.support_seen & active).long()
        first = (self.flight_id == 1) & self.support_seen
        self.up |= airborne & first & (root_velocity_w[:, 2] > .05)
        self.front_cross |= ((self.previous_front < 0) & (high[..., 0] >= 0)
                             & (low[..., 2] >= .27) & airborne[:, None] & first[:, None])
        self.rear_cross |= ((self.previous_rear < 0) & (low[..., 0] >= 0)
                            & (low[..., 2] >= .27) & airborne[:, None] & first[:, None])
        self.wholeclear |= self.rear_cross.all(-1) & self.up & first
        self.leading |= self.front_cross.all(-1) & self.up & first
        self.ground_return |= self.wholeclear & (ground_force > 1).any(-1) & active
        self.edge_return |= self.wholeclear & (low[..., 0] < -.02).any(-1) & active
        inside = ((low[..., 0] >= 0) & (high[..., 0] <= 3)
                  & (low[..., 1] >= -self.half_width) & (high[..., 1] <= self.half_width)).all(-1)
        roll, pitch, yaw = euler_xyz_from_quat(root_quaternion)
        supported = (inside & (top_force > 1).all(-1) & (nonwheel_force <= 1)
                     & self.wholeclear & ~self.ground_return & ~self.edge_return & active)
        self.support_ticks = torch.where(supported, self.support_ticks+1, 0)
        self.support_peak = torch.maximum(self.support_peak, self.support_ticks)
        steady = (supported & (self.support_ticks >= 12)
                  & (root_velocity_w[:, :2].norm(dim=-1) <= .03)
                  & (root_velocity_w[:, 2].abs() <= .03)
                  & (roll.abs() <= torch.pi/18) & (pitch.abs() <= torch.pi/18)
                  & (wrap_to_pi(yaw).abs() <= .2))
        self.stable_ticks = torch.where(steady, self.stable_ticks+1, 0)
        self.stable_peak = torch.maximum(self.stable_peak, self.stable_ticks)
        self.success |= (self.stable_ticks >= 200) & active
        self.previous_air.copy_(airborne)
        self.previous_rear.copy_(low[..., 0])
        self.previous_front.copy_(high[..., 0])
        return steady

    def reset(self, ids):
        for key, value in vars(self).items():
            if not torch.is_tensor(value):
                continue
            value[ids] = -torch.inf if key in ('previous_rear', 'previous_front') else 0
