"""Record actual generated families and sample old commands on clear plane supports."""
import hashlib,json,math
from pathlib import Path
import numpy as np
import torch
from isaaclab.terrains.terrain_generator import TerrainGenerator
from e1_chunked_terrain import ChunkedTerrainImporter
from e1_terrain_runtime import RoughStraightCommand
from e1_full_pose_reset import query
from retained_flat_command_math import sample_commands,update_world_projection
from retention_command_state import PROFILE,FIELDS,validate
FAMILIES=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')
_LAST=None
def tensor(v):return v.torch if hasattr(v,'torch') else v

class RecordedTerrainGenerator(TerrainGenerator):
 def __init__(self,*a,**k):
  self.retention_assignment=[];super().__init__(*a,**k)
  assert len(self.retention_assignment)==self.cfg.num_rows*self.cfg.num_cols
  global _LAST;_LAST=self
 def _add_sub_terrain(self,mesh,origin,row,col,sub_terrain_cfg):
  names=[n for n,c in self.cfg.sub_terrains.items() if c is sub_terrain_cfg];assert len(names)==1
  super()._add_sub_terrain(mesh,origin,row,col,sub_terrain_cfg)
  bounds=mesh.bounds.copy();offset=np.array([-self.cfg.size[0]*self.cfg.num_rows*.5,-self.cfg.size[1]*self.cfg.num_cols*.5,0.]);bounds+=offset
  # A plane cell must be a real constant-height upward mesh, not merely a name.
  flat=bool(np.ptp(mesh.vertices[:,2])<=1e-6 and np.all(mesh.face_normals[:,2]>1.-1e-6))
  self.retention_assignment.append(dict(row=int(row),column=int(col),family=names[0],bounds=bounds.tolist(),actual_mesh_flat=flat,triangles=len(mesh.faces)))

class RecordedTerrainImporter(ChunkedTerrainImporter):
 def __init__(self,*a,**k):
  super().__init__(*a,**k);g=_LAST;assert g is not None and g.cfg.num_rows==g.cfg.num_cols==40
  self.retention_assignment=list(g.retention_assignment)
  self.retention_assignment_sha=hashlib.sha256(json.dumps(self.retention_assignment,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  self.retention_family=torch.full((40,40),-1,device=self.device,dtype=torch.long)
  self.retention_bounds=torch.zeros((40,40,2,3),device=self.device)
  self.retention_flat=torch.zeros((40,40),device=self.device,dtype=torch.bool)
  for x in self.retention_assignment:
   r,c=x['row'],x['column'];self.retention_family[r,c]=FAMILIES.index(x['family']);self.retention_bounds[r,c]=torch.tensor(x['bounds'],device=self.device);self.retention_flat[r,c]=x['actual_mesh_flat']
  assert torch.equal((self.retention_family==0).sum(1),torch.full((40,),12,device=self.device))
  self.retention_size=tuple(g.cfg.size);self.retention_radius=None

def eligibility(env,ids):
 terrain=env.scene.terrain;root=tensor(env.scene['robot'].data.root_pos_w)[ids];robot=env.scene['robot']
 xy=root[:,:2];size=torch.tensor(terrain.retention_size,device=env.device)
 rc=torch.floor(xy/size+20).long();inside=((rc>=0)&(rc<40)).all(1);safe=rc.clamp(0,39)
 family=terrain.retention_family[safe[:,0],safe[:,1]];family=torch.where(inside,family,-1)
 b=terrain.retention_bounds[safe[:,0],safe[:,1]]
 if terrain.retention_radius is None:
  bank=np.load(Path(__file__).with_name('MOD4_RESET_COLLISION_BANK.npz'))
  radius=float(np.linalg.norm(bank['points_root'][...,:2],axis=-1).max())
  terrain.retention_radius=max(1.,radius+.1)
 clearance=((xy-b[:,0,:2])>terrain.retention_radius).all(1)&((b[:,1,:2]-xy)>terrain.retention_radius).all(1)
 eligible=inside&(family==0)&terrain.retention_flat[safe[:,0],safe[:,1]]&clearance
 if eligible.any():
  candidates=ids[eligible];bodies=robot.find_bodies(['left_wheel','right_wheel'],preserve_order=True)[0]
  pts=torch.cat((tensor(robot.data.root_pos_w)[candidates,None],tensor(robot.data.body_link_pos_w)[candidates][:,bodies]),1).clone();pts[:,:,2]+=1.
  out=query(env).cast(pts.contiguous(),4.)
  expected=b[eligible,0,2,None]
  physical=out['hit'].all(1)&((out['height']-expected).abs()<=1e-6).all(1)&(out['normal'][...,2]>1.-1e-6).all(1)
  # Current body-link extent also has to fit the explicitly conservative sweep.
  distance=(tensor(robot.data.body_link_pos_w)[candidates,:,:2]-tensor(robot.data.root_pos_w)[candidates,None,:2]).norm(dim=-1).amax(1)
  physical&=(distance+.1<terrain.retention_radius)
  eligible[eligible.clone()]=physical
 return eligible,family

class RetainedFlatCommand(RoughStraightCommand):
 def __init__(self,cfg,env):
  self._retention_resampling=True
  super().__init__(cfg,env);self.progress_goal=.5
  self._retention_rng=torch.Generator(device=self.device);self._retention_rng.manual_seed(int(env.cfg.seed)+32452843)
  self.eligible_flat=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool);self.linear=torch.zeros_like(self.eligible_flat);self.moving=torch.zeros_like(self.eligible_flat)
  self.direction=torch.zeros(self.num_envs,device=self.device);self.linear_vx=torch.zeros_like(self.direction);self.family=torch.full((self.num_envs,),-1,device=self.device,dtype=torch.long)
  self.sample_histogram=torch.zeros((6,7),device=self.device,dtype=torch.long);self.control_histogram=torch.zeros_like(self.sample_histogram)
  self._retention_resampling=False;self._command_heading=torch.zeros_like(self.direction)
 def _count(self,ids,hist):
  stand=self.is_standing_env[ids];linear=self.linear[ids];moving=self.moving[ids]
  mode=torch.zeros(len(ids),device=self.device,dtype=torch.long);mode[stand]=1
  mode[linear&(self.linear_vx[ids]<0)]=2;mode[linear&(self.linear_vx[ids]>0)]=3
  mode[moving&(self.signed_yaw[ids]<0)]=4;mode[moving&(self.signed_yaw[ids]>0)]=5
  mode[self.eligible_flat[ids]&~stand&~linear&~moving]=6
  index=(self.family[ids]+1)*7+mode;hist.add_(torch.bincount(index,minlength=42).reshape(6,7))
 def _resample_command(self,env_ids):
  ids=torch.as_tensor(env_ids,device=self.device,dtype=torch.long)
  self._retention_resampling=True
  try:super()._resample_command(env_ids)
  finally:self._retention_resampling=False
  if self.manual_evaluation_mode:return
  eligible,family=eligibility(self._env,ids);heading=tensor(self.robot.data.heading_w)[ids]
  row=sample_commands(self._retention_rng,eligible,self.is_standing_env[ids],heading)
  # The non-eligible commands and old RNG consumption remain the old adapter's.
  selected=eligible&~self.is_standing_env[ids];self.vel_command_b[ids[selected]]=row['command'][selected]
  self.eligible_flat[ids]=eligible;self.family[ids]=family;self.linear[ids]=row['linear'];self.moving[ids]=row['moving'];self.direction[ids]=row['world_direction'];self.linear_vx[ids]=self.vel_command_b[ids,0]
  self.world_direction[ids]=self.direction[ids];self.signed_yaw[ids]=row['signed_yaw'];self.is_moving_spin[ids]=row['moving'];self.is_pure_spin[ids]=False;self.is_transition_spin[ids]=False
  self._write_dynamic(ids);self._count(ids,self.sample_histogram)
 def _write_dynamic(self,ids):
  if self._retention_resampling or not hasattr(self,'eligible_flat') or self.manual_evaluation_mode:return
  current,family=eligibility(self._env,ids);lost=(self.linear[ids]|self.moving[ids])&~current
  bad=ids[lost];self.linear[bad]=False;self.moving[bad]=False;self.is_moving_spin[bad]=False;self.signed_yaw[bad]=0.;self.vel_command_b[bad]=0.
  # A lost-support command becomes a stand until its next ordinary resampling.
  self.eligible_flat[ids]=current;self.family[ids]=family
  self.vel_command_b[ids[self.linear[ids]],0]=self.linear_vx[ids[self.linear[ids]]]
  moving=ids[self.moving[ids]];heading=tensor(self.robot.data.heading_w)
  self._command_heading[ids]=heading[ids]
  update_world_projection(self.vel_command_b,self.moving,heading,self.direction,self.signed_yaw)
  self.vel_command_b[self.is_standing_env]=0.
 def _update_command(self):
  super()._update_command()
  if not self.manual_evaluation_mode:self._count(torch.arange(self.num_envs,device=self.device),self.control_histogram)
 def state_dict_retention(self):
  s=dict(version=1,profile=PROFILE,num_envs=self.num_envs,rng_device_type=torch.device(self.device).type,rng=self._retention_rng.get_state().clone(),assignment_sha256=self._env.scene.terrain.retention_assignment_sha,no_position_correction=True,no_mask_actor_or_gate_input=True)
  s.update({k:getattr(self,k).clone() for k in FIELDS});s['BODY_command']=self.vel_command_b.clone();validate(s,self.num_envs);return s
 def load_state_retention(self,s):
  validate(s,self.num_envs);assert s['assignment_sha256']==self._env.scene.terrain.retention_assignment_sha and s['rng_device_type']==torch.device(self.device).type
  for k in FIELDS:getattr(self,k).copy_(s[k].to(self.device))
  self._retention_rng.set_state(s['rng'].cpu());self.world_direction.copy_(self.direction);self.is_moving_spin.copy_(self.moving);self.vel_command_b.copy_(s['BODY_command'].to(self.device))
 def audit_retention(self):
  c=self.command;active=self.linear|self.moving
  assert not self.is_pure_spin.any() and not self.is_transition_spin.any() and not (active&~self.eligible_flat).any() and not (active&self.is_standing_env).any()
  assert (c[:,1].abs()<=1e-6).all() and (c[~self.eligible_flat,2].abs()<=1e-6).all() and (c[:,2].abs()<=2.000001).all()
  err=0.
  if self.moving.any():err=float((c[self.moving,0]-torch.cos(self._command_heading[self.moving]-self.direction[self.moving])).abs().max())
  assert err<=1e-6
  return dict(profile=PROFILE,assignment_sha256=self._env.scene.terrain.retention_assignment_sha,actual_family_counts=torch.bincount(self.family+1,minlength=6).cpu().tolist(),eligible=int(self.eligible_flat.sum()),linear=int(self.linear.sum()),moving=int(self.moving.sum()),standing=int(self.is_standing_env.sum()),sample_histogram=self.sample_histogram.cpu().tolist(),control_histogram=self.control_histogram.cpu().tolist(),histogram_columns=['gentle','standing','negative_straight','positive_straight','negative_world_yaw','positive_world_yaw','eligible_without_retained_mode'],histogram_rows=['outside']+list(FAMILIES),projection_error=err,rotation_support_radius_m=self._env.scene.terrain.retention_radius,pure_high_spin=False,position_correction=False,ground_support_is_authored_mesh_query_not_contact_force_certification=True)

def inactive_retention_rolling(env,**kwargs):
 term=env.command_manager.get_term('twist');term.audit_retention()
 # The same original zero contribution: this proxy belongs only to pure yaw,
 # which is absent. World translation receives the unchanged task rewards.
 return torch.zeros(env.num_envs,device=env.device)

def configure_retention(cfg):
 from g3_cad_wave_geometry import configure_g3
 r=configure_g3(cfg);cfg.scene.terrain.terrain_generator.class_type=RecordedTerrainGenerator;cfg.scene.terrain.class_type=RecordedTerrainImporter
 cfg.commands.twist.class_type=RetainedFlatCommand;cfg.rewards.spin_contact_consistency.func=inactive_retention_rolling
 r['retained_command_scope']=dict(profile=PROFILE,actual_plane_assignment_only=True,standing_fraction=.2,noneligible_gentle_vx=[-.3,.3],conditional_nonstanding_plane_signed_straight_fraction=.5,conditional_nonstanding_plane_world_fraction=.5,straight_abs_vx=[1.,1.5],world_V=.5,yaw_abs=[1.,2.],high_pure_spin=False,other_terrain_recipes_proportions_unchanged=True,reward_zero_proxy_numerically_unchanged=True,legacy_terrain_command_range_metadata_describes_noneligible_gentle_only=True)
 return r
