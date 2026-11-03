"""Selected SCUT 1m central-platform spawn relation, specialized to one 270mm step.

The published inverted-stair generator has several steps and terrain branches.
This course selects its 1m centre and original root reset range, not the entire
rough curriculum. Four raised sides keep every sampled heading meaningful.
"""
import math
import torch
from .acceptance import Strict270, wheel_bounds
from .math_ops import euler_xyz_from_quat

HALF_CENTRE = .5
OUTER = 3.5
HEIGHT = .27
SPAWN_HEIGHT = .38
POSE_RANGE = dict(roll=(-.15,.15), pitch=(-.15,.15), yaw=(-3.14,3.14))
BOXES = ((.5,3.5,-3.5,3.5), (-3.5,-.5,-3.5,3.5),
         (-.5,.5,.5,3.5), (-.5,.5,-3.5,-.5))


def metadata():
    return dict(source_branch='inv_stair_slope_for_rm_mid platform_width=1m',
        centre_width_m=1., nearest_edge_from_centre_m=.5,
        root_position_m=[0.,0.,SPAWN_HEIGHT], pose_range=POSE_RANGE,
        root_velocity_zero=True, step_height_m=HEIGHT, raised_boxes_xy=BOXES,
        explicit_specialization='One270mm step, four sides; no rough terrain curriculum',
        original_model_joint_pose_not_copied=True)


def top_mask(points):
    xy = points[..., :2].abs()
    return ((points[...,2]-HEIGHT).abs() < .001) & (xy.amax(-1) <= OUTER+.001) & (xy.amax(-1) >= HALF_CENTRE-.001)


class FourSideStrict270:
    """Unchanged strict thresholds applied separately to each real platform edge."""
    def __init__(self, n, device):
        self.n, self.device = n, device
        self.meters = [Strict270(n,device,half_width=OUTER) for _ in range(4)]
        self.initial_yaw = torch.full((n,),torch.nan,device=device)

    def __getattr__(self, name):
        values = [getattr(m,name) for m in self.meters]
        stacked = torch.stack(values)
        return stacked.any(0) if stacked.dtype == torch.bool else stacked.amax(0)

    def reset(self, ids):
        self.initial_yaw[ids] = torch.nan
        for meter in self.meters:
            meter.reset(ids)

    def set_spawn_orientation(self, ids, quaternion):
        """Yaw acceptance is relative to the reset pose, before physics moves it."""
        self.initial_yaw[ids] = euler_xyz_from_quat(quaternion)[2]

    def update_world(self, positions, quaternions, contract, origins, top_force,
                     ground_force, wheel_net, nonwheel_force, velocity, root_quat, active):
        low,high = wheel_bounds(positions,quaternions,contract)
        low = low-origins[:,None]
        high = high-origins[:,None]
        yaw = euler_xyz_from_quat(root_quat)[2]
        self.initial_yaw = torch.where(torch.isnan(self.initial_yaw),yaw,self.initial_yaw)
        for side,meter in enumerate(self.meters):
            # Cardinal axes preserve exact finite-cylinder AABBs, including width.
            c,s = ((1.,0.),(0.,1.),(-1.,0.),(0.,-1.))[side]
            a = low.clone(); b = high.clone()
            a[...,0] = torch.minimum(c*low[...,0],c*high[...,0])+torch.minimum(s*low[...,1],s*high[...,1])-.5
            b[...,0] = torch.maximum(c*low[...,0],c*high[...,0])+torch.maximum(s*low[...,1],s*high[...,1])-.5
            a[...,1] = torch.minimum(-s*low[...,0],-s*high[...,0])+torch.minimum(c*low[...,1],c*high[...,1])
            b[...,1] = torch.maximum(-s*low[...,0],-s*high[...,0])+torch.maximum(c*low[...,1],c*high[...,1])
            v = velocity.clone()
            v[:,0],v[:,1] = c*velocity[:,0]+s*velocity[:,1],-s*velocity[:,0]+c*velocity[:,1]
            # qz(-angle) * q, all SCUT-facing quaternions are wxyz.
            cw,sz = torch.cos(-self.initial_yaw/2),torch.sin(-self.initial_yaw/2)
            w,x,y,z = root_quat.unbind(-1)
            q = torch.stack((cw*w-sz*z,cw*x-sz*y,cw*y+sz*x,cw*z+sz*w),-1)
            meter.update(a,b,top_force,ground_force,wheel_net,nonwheel_force,v,q,active)
