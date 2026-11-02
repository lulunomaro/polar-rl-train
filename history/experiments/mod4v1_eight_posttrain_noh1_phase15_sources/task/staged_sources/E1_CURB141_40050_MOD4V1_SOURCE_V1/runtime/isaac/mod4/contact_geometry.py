"""Input-hull support and lowest-vertex slip approximation, control-rate only."""
import torch
from isaaclab.utils.math import quat_apply

class ControlGeometry:
    def __init__(self, env, usd_path):
        from pxr import Usd,UsdGeom
        self.env=env;self.robot=env.scene['robot']
        self.reference_version="wheel_link_support_velocity_v2"
        self.ids,_=self.robot.find_bodies(['left_wheel','right_wheel'],preserve_order=True)
        stage=Usd.Stage.Open(usd_path);points=[]
        for name in ['left_wheel','right_wheel']:
            body=stage.GetPrimAtPath('/Robot/links/'+name)
            c=[p for p in Usd.PrimRange(body) if p.GetAttribute('physics:collisionEnabled').Get()]
            if len(c)!=1 or c[0].GetTypeName()!='Mesh':raise RuntimeError('Expected one wheel mesh')
            cache=UsdGeom.XformCache();tf=cache.GetLocalToWorldTransform(c[0])*cache.GetLocalToWorldTransform(body).GetInverse()
            points.append(torch.tensor([list(tf.Transform(v)) for v in UsdGeom.Mesh(c[0]).GetPointsAttr().Get()],device=env.device))
        self.vertices=torch.stack(points)[None].expand(env.num_envs,-1,-1,-1)

    def read(self):
        r=self.robot;n=self.env.num_envs;m=self.vertices.shape[2]
        q=r.data.body_quat_w[:,self.ids]
        rotated=quat_apply(q[:,:,None,:].expand(-1,-1,m,-1).reshape(-1,4),self.vertices.reshape(-1,3)).reshape(n,2,m,3)
        low=rotated[:,:,:,2].argmin(2)
        support=rotated.gather(2,low[:,:,None,None].expand(-1,-1,1,3)).squeeze(2)
        ground=getattr(self.env,'_mod4_ground_z',torch.zeros(n,device=self.env.device))
        gap=r.data.body_pos_w[:,self.ids,2]+support[:,:,2]-ground[:,None]
        vel=r.data.body_link_lin_vel_w[:,self.ids]+torch.cross(r.data.body_ang_vel_w[:,self.ids],support,dim=-1)
        legacy=r.data.body_lin_vel_w[:,self.ids]+torch.cross(r.data.body_ang_vel_w[:,self.ids],support,dim=-1)
        self.legacy_reference_slip=legacy[:,:,:2].norm(dim=-1)
        return gap,vel[:,:,:2].norm(dim=-1)
