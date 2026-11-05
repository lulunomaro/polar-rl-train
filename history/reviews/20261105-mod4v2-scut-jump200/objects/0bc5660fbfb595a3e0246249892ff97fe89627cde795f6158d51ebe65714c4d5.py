"""Single 200mm vertical step and actual jump/landing observations.

This is an explicit task adaptation of SCUT's high-step and ballistic takeoff
helpers. It is separate from the saved25-40mm rough-stair locomotion recipe.
"""
import torch

from .acceptance import wheel_bounds
from .math_ops import euler_xyz_from_quat, wrap_to_pi

HEIGHT = .2
EDGE = .8
OUTER = 3.5
HALF_WIDTH = 3.5
SPAWN_HEIGHT = .38
BOXES = ((EDGE, OUTER, -HALF_WIDTH, HALF_WIDTH),)
POSE_RANGE = dict(roll=(-.05, .05), pitch=(-.05, .05), yaw=(-.05, .05))


def metadata():
    return dict(kind='MOD4_SINGLE_STEP_JUMP200', step_height_m=HEIGHT,
        near_edge_m=EDGE, top_end_m=OUTER, half_width_m=HALF_WIDTH,
        raised_boxes_xy=BOXES, root_position_m=[0., 0., SPAWN_HEIGHT],
        pose_range=POSE_RANGE, root_velocity_zero=True, requires_airborne=True,
        first_flight_only=False, requires_270mm=False,
        task_adaptation='Single200mm vertical face and horizontal top; not small-stair locomotion',
        source='SCUT high-step dimensions and optional ballistic takeoff helper',
        physical_assist=False)


def top_mask(points):
    return (((points[..., 2]-HEIGHT).abs() < .001)
            & (points[..., 0] >= EDGE-.001) & (points[..., 0] <= OUTER+.001)
            & (points[..., 1].abs() <= HALF_WIDTH+.001))


class Jump200Acceptance:
    """Require ground support, upward flight, airborne clearance, then landing.

    Failed early attempts may be retried. A spawn drop, wheel-on-wall climb or
    elevated body alone never qualifies. All inputs are measured400Hz endpoints.
    """
    def __init__(self, n, device):
        self.n, self.device = n, device
        self.success = torch.zeros(n, dtype=torch.bool, device=device)
        for key in ('wholeclear', 'leading', 'ground_seen', 'previous_air',
                    'up', 'current_clear', 'failed_return', 'landed_top'):
            setattr(self, key, self.success.clone())
        self.flight_id = torch.zeros(n, dtype=torch.long, device=device)
        for key in ('stable_ticks', 'stable_peak', 'support_ticks', 'support_peak'):
            setattr(self, key, self.flight_id.clone())
        self.initial_yaw = torch.full((n,), torch.nan, device=device)

    def reset(self, ids):
        for key, value in vars(self).items():
            if torch.is_tensor(value):
                value[ids] = torch.nan if key == 'initial_yaw' else 0

    def set_spawn_orientation(self, ids, quaternion):
        self.initial_yaw[ids] = euler_xyz_from_quat(quaternion)[2]

    def update_world(self, positions, quaternions, contract, origins, top_force,
                     ground_force, wheel_net, nonwheel_force, velocity, root_quat, active):
        low, high = wheel_bounds(positions, quaternions, contract)
        low, high = low-origins[:, None], high-origins[:, None]
        self.ground_seen |= (ground_force > 1).all(-1) & active
        airborne = ((wheel_net.norm(dim=-1) <= 1).all(-1)
                    & (low[..., 2] > .005).all(-1) & (nonwheel_force <= 1) & active)
        launch = airborne & ~self.previous_air & self.ground_seen
        self.flight_id += launch.long()
        for key in ('up', 'current_clear', 'failed_return', 'landed_top'):
            getattr(self, key)[launch] = False
        self.ground_seen[launch] = False
        self.up |= airborne & (self.flight_id > 0) & (velocity[:, 2] > .05)
        high_enough = (low[..., 2] >= HEIGHT).all(-1)
        front_crossed = (high[..., 0] >= EDGE).all(-1)
        rear_crossed = (low[..., 0] >= EDGE).all(-1)
        self.leading |= airborne & self.up & high_enough & front_crossed
        self.current_clear |= airborne & self.up & high_enough & rear_crossed
        self.wholeclear |= self.current_clear
        self.failed_return |= self.current_clear & active & (
            (ground_force > 1).any(-1) | (low[..., 0] < EDGE-.02).any(-1))
        inside = ((low[..., 0] >= EDGE) & (high[..., 0] <= OUTER)
                  & (low[..., 1] >= -HALF_WIDTH) & (high[..., 1] <= HALF_WIDTH)).all(-1)
        supported = (self.current_clear & ~self.failed_return & inside
                     & (top_force > 1).all(-1) & (nonwheel_force <= 1) & active)
        self.landed_top |= supported
        self.support_ticks = torch.where(supported, self.support_ticks+1, 0)
        self.support_peak = torch.maximum(self.support_peak, self.support_ticks)
        roll, pitch, yaw = euler_xyz_from_quat(root_quat)
        self.initial_yaw = torch.where(torch.isnan(self.initial_yaw), yaw, self.initial_yaw)
        steady = (supported & (velocity[:, :2].norm(dim=-1) <= .03)
                  & (velocity[:, 2].abs() <= .03) & (roll.abs() <= torch.pi/18)
                  & (pitch.abs() <= torch.pi/18)
                  & (wrap_to_pi(yaw-self.initial_yaw).abs() <= .2))
        self.stable_ticks = torch.where(steady, self.stable_ticks+1, 0)
        self.stable_peak = torch.maximum(self.stable_peak, self.stable_ticks)
        self.success |= (self.stable_ticks >= 200) & active
        self.previous_air.copy_(airborne)
        return steady
