"""Original Fudan stairs geometry; explicit warm-data placement, not original curriculum.

No reward implementation is installed here. Low-base/reset height uses the
original height query on the actual terrain. Eight flat-mode IDs use its flat
border; jump IDs use original level0..5 origins. Levels stay fixed for warm data.
"""
from types import SimpleNamespace
import hashlib,numpy as np,torch
from literal_stairs3_original_config import OriginalStairs3Cfg,class_to_dict
from literal_stairs3_original_terrain import Terrain
from original_height_query272 import OriginalHeightQuery272
from spring_nominal_sdk_readback import tensor
import mixed240_sdk as jump
import mod4_task as task
DATA={}
def yaw_apply(q,v):
 shape=v.shape;q=q.reshape(-1,4);v=v.reshape(-1,3);x,y,z,w=q.unbind(-1);a=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z));c,s=a.cos(),a.sin();x,y,z=v.unbind(-1)
 return torch.stack((c*x-s*y,s*x+c*y,z),-1).reshape(shape)
def spawn_original(prim_path,cfg,translation=None,orientation=None,**kwargs):
 from pxr import UsdGeom,UsdPhysics
 from isaaclab.sim import get_current_stage,define_collision_properties,bind_physics_material
 c=SimpleNamespace(**class_to_dict(OriginalStairs3Cfg.terrain));assert c.mesh_type=='trimesh'and c.terrain_proportions==[0.,0.,0.,.5,.5,0.]
 terrain=Terrain(c,DATA['num_envs']);vertices=np.asarray(terrain.vertices,dtype=np.float32).copy();faces=np.asarray(terrain.triangles,dtype=np.int32);vertices[:,:2]-=c.border_size
 stage=get_current_stage();root=UsdGeom.Xform.Define(stage,prim_path).GetPrim();path=prim_path+'/original_Fudan_STAIRS3';mesh=UsdGeom.Mesh.Define(stage,path)
 mesh.CreatePointsAttr().Set(vertices.tolist());mesh.CreateFaceVertexCountsAttr().Set([3]*len(faces));mesh.CreateFaceVertexIndicesAttr().Set(faces.reshape(-1).tolist());mesh.CreateSubdivisionSchemeAttr().Set('none')
 UsdPhysics.CollisionAPI.Apply(mesh.GetPrim());UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr().Set('none')
 if cfg.collision_props is not None:define_collision_properties(path,cfg.collision_props,stage=stage)
 if cfg.physics_material is not None:
  material=prim_path+'/physicsMaterial';cfg.physics_material.func(material,cfg.physics_material);bind_physics_material(path,material,stage=stage)
 DATA.update(terrain=terrain,metadata=dict(source_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',snapshot='plane/logs/wheel_legged/上台阶3',original_Terrain_and_height_query_unchanged=True,heightfield_shape=list(terrain.height_field_raw.shape),heightfield_SHA=hashlib.sha256(terrain.height_field_raw.tobytes()).hexdigest(),vertices=len(vertices),triangles=len(faces),step_width_m=.7,step_formula='.05+.18*difficulty',original_max_quantized_step_m=.21,terrain_geometry_original=True,warm_placement_new=True,original_dynamic_curriculum_not_claimed=True,no_270mm_extension=True,static_friction=.5,dynamic_friction=.5,restitution=.5))
 return root
def configure(cfg):
 jump.configure(cfg);DATA['num_envs']=cfg.scene.num_envs;cfg.scene.ground.spawn.func=spawn_original;cfg.scene.ground.init_state.pos=(0.,0.,0.)
 task.ground_height=lambda e:e.current_original_heights272().mean(-1)
 return cfg
class TerrainMixed272Env(jump.Mixed209Env):
 def __init__(self,*a,**kw):
  self._terrain272_ready=False;super().__init__(*a,**kw)
  import original_height_query272 as query
  query.quat_apply_yaw=yaw_apply
  terrain=DATA['terrain'];n=self.num_envs;d=self.device;k=self.terrain272=OriginalHeightQuery272();k.cfg=OriginalStairs3Cfg();k.num_envs=n;k.device=d;k.terrain=terrain;k.height_samples=torch.tensor(terrain.height_field_raw.astype(np.int32),device=d)
  k.terrain_origins=torch.tensor(terrain.env_origins,device=d,dtype=torch.float32);k.terrain_levels=torch.randint(0,6,(n,),device=d);k.terrain_types=torch.div(torch.arange(n,device=d),n/20,rounding_mode='floor').long().clamp_max(19);k.env_origins=self.scene.env_origins
  k.env_origins.copy_(k.terrain_origins[k.terrain_levels,k.terrain_types]);flat=torch.where(self._mixed209_flat)[0]
  # The actual original heightfield includes this25m flat border. No new plane
  # is substituted and no root/velocity setter is applied mid-episode.
  k.env_origins[flat,0]=-12.;k.env_origins[flat,1]=torch.arange(len(flat),device=d,dtype=torch.float32)*3.+4.;k.env_origins[flat,2]=0.
  x=torch.tensor(k.cfg.terrain.measured_points_x,device=d);y=torch.tensor(k.cfg.terrain.measured_points_y,device=d);x,y=torch.meshgrid(x,y,indexing='ij');p=torch.stack((x.flatten(),y.flatten(),torch.zeros(x.numel(),device=d)),-1);k.height_points=p[None].expand(n,-1,-1).clone();k.num_height_points=p.shape[0]
  self._terrain272_ready=True
 def current_original_heights272(self):
  if not self._terrain272_ready:raise RuntimeError('Original terrain binding requested before initialization')
  r=self.scene['robot'];self.terrain272.root_states=tensor(r.data.root_state_w);self.terrain272.base_quat=tensor(r.data.root_quat_w)
  return self.terrain272._get_heights()
