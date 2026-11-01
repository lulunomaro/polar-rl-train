"""New 270mm teacher-student course; original reward and physical plant retained."""
import numpy as np
import torch
from spring_nominal_sdk_readback import tensor
import mixed240_sdk as mixed
import mod4_task as task

DATA={}

def layout():
    rng=np.random.default_rng(286)
    origins=[];targets=[]
    for i in range(80):
        origins.append([(i//10)*10.,(i%10)*10.,0.])
        targets.append([float(rng.uniform(.65,1.35)),float(rng.uniform(-.12,.12)),.27,float(rng.uniform(-.12,.12))])
    return np.array(origins,np.float32),np.array(targets,np.float32)

def spawn(prim_path,cfg,**kwargs):
    from pxr import UsdGeom,UsdPhysics
    from isaaclab.sim import get_current_stage,define_collision_properties,bind_physics_material
    origins,targets=layout();points=[];faces=[]
    for i,(origin,t) in enumerate(zip(origins,targets)):
        start=len(points);ox,oy,_=origin
        points.extend([(ox+x,oy+y,0.) for x,y in ((-4.,-4.),(6.,-4.),(6.,5.),(-4.,5.))])
        faces.extend([(start,start+1,start+2),(start,start+2,start+3)])
        if i%10==0:continue
        start=len(points);edge,lat,height,yaw=t;c,s=np.cos(yaw),np.sin(yaw)
        corners=[(x,y,z)for z in (0.,height) for x,y in ((0.,-1.),(3.,-1.),(3.,1.),(0.,1.))]
        points.extend([(ox+edge+c*x-s*y,oy+lat+s*x+c*y,z) for x,y,z in corners])
        cube=[(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),
            (1,2,6),(1,6,5),(0,1,5),(0,5,4),(3,7,6),(3,6,2)]
        faces.extend([tuple(start+x for x in f)for f in cube])
    stage=get_current_stage();root=UsdGeom.Xform.Define(stage,prim_path).GetPrim()
    path=prim_path+'/teacher_step270';mesh=UsdGeom.Mesh.Define(stage,path)
    mesh.CreatePointsAttr().Set(np.asarray(points,dtype=np.float32).tolist());mesh.CreateFaceVertexCountsAttr().Set([3]*len(faces))
    mesh.CreateFaceVertexIndicesAttr().Set([i for f in faces for i in f]);mesh.CreateSubdivisionSchemeAttr().Set('none')
    UsdPhysics.CollisionAPI.Apply(mesh.GetPrim());UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr().Set('none')
    if cfg.collision_props is not None:define_collision_properties(path,cfg.collision_props,stage=stage)
    if cfg.physics_material is not None:
        material=prim_path+'/physicsMaterial';cfg.physics_material.func(material,cfg.physics_material);bind_physics_material(path,material,stage=stage)
    DATA.update(metadata=dict(new_teacher_course=True,original_Fudan_terrain=False,height_m=.27,
        tile_spacing_m=10.,edge_distance_range=[.65,1.35],lateral_range=[-.12,.12],edge_yaw_range=[-.12,.12],
        platform_size_m=[3.,2.,.27],physical_and_depth_mesh_same=True,GT_target_only_labels_and_height_guard=True))
    return root

def ground_height(env):
    if not getattr(env,'ready286',False):return torch.zeros(env.num_envs,device=env.device)
    pos=tensor(env.scene['robot'].data.root_pos_w)-env.scene.env_origins
    t=env.target286;c,s=t[:,3].cos(),t[:,3].sin();delta=pos[:,:2]-t[:,:2]
    x=c*delta[:,0]+s*delta[:,1];y=-s*delta[:,0]+c*delta[:,1]
    on=(x>=0)&(x<=3)&(y.abs()<=1)&(~env._mixed209_flat)
    return torch.where(on,t[:,2],torch.zeros_like(t[:,2]))

class Teacher286Command(mixed.Mixed209Command):
    def _resample_command(self, env_ids):
        super()._resample_command(env_ids)
        ids=torch.as_tensor(env_ids,device=self.device,dtype=torch.long)
        jump=ids[~self._env._mixed209_flat[ids]]
        self.vel_command_b[jump]=torch.tensor([1.4,0.,0.],device=self.device)
        task.height_cmd(self._env)[jump,0]=.135

def configure(cfg):
    mixed.configure(cfg);cfg.commands.twist.class_type=Teacher286Command;cfg.scene.ground.spawn.func=spawn;cfg.scene.ground.init_state.pos=(0.,0.,0.)
    cfg.scene.env_spacing=10.;task.ground_height=ground_height
    return cfg

class Teacher286Env(mixed.Mixed209Env):
    def __init__(self,*args,**kwargs):
        self.ready286=False;super().__init__(*args,**kwargs)
        origins,targets=layout();self.scene.env_origins.copy_(torch.tensor(origins,device=self.device))
        self.target286=torch.tensor(targets,device=self.device);self.ready286=True

    def _reset_idx(self,ids):
        out=super()._reset_idx(ids)
        # A declared new command scope replaces random blind jump commands;
        # original reward methods/weights still consume their usual command ABI.
        if getattr(self,'ready286',False):
            cmd=self.command_manager.get_term('twist');ids=torch.as_tensor(ids,device=self.device,dtype=torch.long)
            jump=ids[~self._mixed209_flat[ids]]
            cmd.vel_command_b[jump]=torch.tensor([1.4,0.,0.],device=self.device)
            task.height_cmd(self)[jump,0]=.135
        return out
