"""Only WAVE50 command direction changes; immutable entry/plant/reward/DR reused."""
import torch
from retention_flat_runtime_named_owned import RetainedFlatNamedOwnedCommand
from wave50_entry_runtime_v2 import configure_retention as old_configure,reset_entry_xy
from wave50_direction_state import PROFILE,FIELDS,validate

class WaveEntryDirectionCommand(RetainedFlatNamedOwnedCommand):
 def __init__(self,cfg,env):
  super().__init__(cfg,env)
  self.wave_mask=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
  self.entry_sign=torch.zeros(self.num_envs,device=self.device)
  self.bound_episode=torch.full((self.num_envs,),-1,device=self.device,dtype=torch.long)
  self.reset_xy=torch.zeros((self.num_envs,2),device=self.device)
  self.direction_control_histogram=torch.zeros((2,3),device=self.device,dtype=torch.long)

 def _bind_episode(self,ids):
  if not hasattr(self._env,'_e1_episode'):return
  changed=ids[self.bound_episode[ids]!=self._env._e1_episode[ids]]
  if not len(changed):return
  xy=reset_entry_xy(self._env,changed);t=self._env.scene.terrain
  size=torch.tensor(t.retention_size,device=self.device)
  rc=torch.floor(xy/size+20).long();assert ((rc>=0)&(rc<40)).all()
  b=t.retention_bounds[rc[:,0],rc[:,1]];mask=t.retention_family[rc[:,0],rc[:,1]]==4
  d=xy[:,0]-(b[:,0,0]+b[:,1,0])*.5
  receipt=self._env._wave50_entry_map_receipt
  ex=torch.tensor(receipt['collision_sample_extent_xy'],device=self.device)
  assert (d[mask].abs()-ex[0]-receipt['ten_wave_span_m']*.5>=.4-1e-6).all()
  assert ((xy[mask]-ex>=b[mask,0,:2]+.004-1e-6)&(xy[mask]+ex<=b[mask,1,:2]-.004+1e-6)).all()
  self.wave_mask[changed]=mask;self.entry_sign[changed]=torch.where(mask,-torch.sign(d),0.)
  self.reset_xy[changed]=xy;self.bound_episode[changed]=self._env._e1_episode[changed]

 def _write_dynamic(self,ids):
  super()._write_dynamic(ids)
  if not hasattr(self,'wave_mask') or self._retention_resampling or self.manual_evaluation_mode:return
  ids=torch.as_tensor(ids,device=self.device,dtype=torch.long);self._bind_episode(ids)
  selected=ids[self.wave_mask[ids]&(self.family[ids]==4)&~self.is_standing_env[ids]]
  self.vel_command_b[selected,0]=self.vel_command_b[selected,0].abs()*self.entry_sign[selected]
  assert (self.vel_command_b[selected,1:].abs()<=1e-6).all()
  self.vel_command_b[self.is_standing_env]=0.

 def _update_command(self):
  super()._update_command()
  if self.manual_evaluation_mode:return
  self._write_dynamic(torch.arange(self.num_envs,device=self.device))
  ids=torch.nonzero(self.wave_mask&(self.family==4)).flatten();c=self.vel_command_b[ids,0]
  mode=torch.where(self.is_standing_env[ids],2,torch.where(c<0,0,1))
  side=(self.entry_sign[ids]<0).long()
  self.direction_control_histogram.add_(torch.bincount(side*3+mode,minlength=6).reshape(2,3))

 def state_dict_direction(self):
  s=dict(version=1,profile=PROFILE,num_envs=self.num_envs,assignment_sha256=self._env.scene.terrain.retention_assignment_sha,
   entry_map_sha256=self._env._wave50_entry_map_receipt['map_sha256'],entry_origin_sha256=self._env._wave50_entry_map_receipt['actual_origin_sha256'],no_new_rng=True,no_live_position_or_heading_correction=True)
  for k in FIELDS:s[k]=(self.direction_control_histogram if k=='control_histogram' else getattr(self,k)).clone()
  validate(s,self.num_envs);return s

 def load_state_direction(self,s):
  validate(s,self.num_envs)
  assert s['assignment_sha256']==self._env.scene.terrain.retention_assignment_sha
  reset_entry_xy(self._env,torch.arange(self.num_envs,device=self.device))
  assert s['entry_map_sha256']==self._env._wave50_entry_map_receipt['map_sha256']
  assert s['entry_origin_sha256']==self._env._wave50_entry_map_receipt['actual_origin_sha256']
  for k in FIELDS:(self.direction_control_histogram if k=='control_histogram' else getattr(self,k)).copy_(s[k].to(self.device))

 def audit_direction(self):
  s=self.state_dict_direction();c=self.vel_command_b;ids=self.wave_mask&(self.family==4)&~self.is_standing_env
  assert (self.bound_episode==self._env._e1_episode).all()
  assert (c[ids,0]*self.entry_sign[ids]>=0).all() and (c[ids,0].abs()<=.300001).all()
  assert (c[self.wave_mask&(self.family==4),1:].abs()<=1e-6).all() and (c[self.is_standing_env].abs()<=1e-6).all()
  return dict(profile=PROFILE,assignment_sha256=s['assignment_sha256'],entry_map_sha256=s['entry_map_sha256'],
   actual_WAVE50_environments=int(self.wave_mask.sum()),positive_entry_direction=int((self.entry_sign>0).sum()),
   negative_entry_direction=int((self.entry_sign<0).sum()),control_histogram=self.direction_control_histogram.cpu().tolist(),
   histogram_rows=['left_entry_positive_direction','right_entry_negative_direction'],histogram_columns=['negative','positive','standing'],
   only_episode_reset_binding=True,no_live_position_or_heading_correction=True,no_new_rng=True,non_WAVE50_commands_unchanged=True,
   no_assignment_actor_or_gate_input=True,all_episode_identity_exact=True)

def configure_retention(cfg):
 r=old_configure(cfg);cfg.commands.twist.class_type=WaveEntryDirectionCommand
 r['WAVE50_command_direction_scope']=dict(profile=PROFILE,only_direction_axis=True,old_random_draws_and_absolute_speed_unchanged=True,
  standing_fraction=.2,non_WAVE50_commands_unchanged=True,no_new_rng=True,no_live_position_or_heading_correction=True)
 return r
