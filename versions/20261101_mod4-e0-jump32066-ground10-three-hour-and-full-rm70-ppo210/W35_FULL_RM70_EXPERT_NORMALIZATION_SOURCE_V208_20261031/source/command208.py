"""Original W35 rough sampler/retained RNG, explicit new all-rough arena."""
import torch
from course_math208 import COURSE_PROFILE as PROFILE, COLLISION_USDC_SHA
from terrain208 import RoughStraightCommand
from retained_flat_command_math import sample_commands, update_world_projection
from retention_command_state import FIELDS, validate as legacy_validate, PROFILE as LEGACY_PROFILE
FAMILIES=('plane_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','random_uniform_for_rm')

def tensor(v):
 return v.torch if hasattr(v,'torch') else v

def validate(s,n):
 assert s['profile']==PROFILE
 return legacy_validate(dict(s,profile=LEGACY_PROFILE),n)

def rm70_eligibility(env,ids):
 # All routes are this new original-CAD rough lesson. No certification of an
 # old plane cell, no actor terrain mask, and no forced yaw/velocity correction.
 return (torch.zeros(len(ids),device=env.device,dtype=torch.bool),
         torch.full((len(ids),),4,device=env.device,dtype=torch.long))

class RM70Command208(RoughStraightCommand):
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
  eligible,family=rm70_eligibility(self._env,ids);heading=tensor(self.robot.data.heading_w)[ids]
  row=sample_commands(self._retention_rng,eligible,self.is_standing_env[ids],heading)
  # The non-eligible commands and old RNG consumption remain the old adapter's.
  selected=eligible&~self.is_standing_env[ids];self.vel_command_b[ids[selected]]=row['command'][selected]
  self.eligible_flat[ids]=eligible;self.family[ids]=family;self.linear[ids]=row['linear'];self.moving[ids]=row['moving'];self.direction[ids]=row['world_direction'];self.linear_vx[ids]=self.vel_command_b[ids,0]
  self.world_direction[ids]=self.direction[ids];self.signed_yaw[ids]=row['signed_yaw'];self.is_moving_spin[ids]=row['moving'];self.is_pure_spin[ids]=False;self.is_transition_spin[ids]=False
  self._write_dynamic(ids);self._count(ids,self.sample_histogram)
 def _write_dynamic(self,ids):
  if self._retention_resampling or not hasattr(self,'eligible_flat') or self.manual_evaluation_mode:return
  current,family=rm70_eligibility(self._env,ids);lost=(self.linear[ids]|self.moving[ids])&~current
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
 @property
 def _retention_rng(self):
  return self._retention_rng_owner['generator']
 @_retention_rng.setter
 def _retention_rng(self,value):
  self._retention_rng_owner={'generator':value}
