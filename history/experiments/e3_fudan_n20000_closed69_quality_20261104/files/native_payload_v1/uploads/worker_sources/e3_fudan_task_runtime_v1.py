"""New legal low-rise curriculum, not a replacement for the frozen 74-case E3 grader.
Install only after the entry has started SimulationApp, and before build_env.
Recipes 0..11 retain original falls, 12 retains normal, 13..25 request low-rise.
No joint envelope, actuator, physics, DR, noisy observation or action modification.
"""
from pathlib import Path
import json
import torch
_INSTALLED=False
_POSES=None

def install_before_build():
 global _INSTALLED
 assert not _INSTALLED,'one install in a new own process';_INSTALLED=True
 import e3_recovery_runtime_v1 as old
 from h1_fullstate_environment_v1 import tensor
 BasePhase=old.RecoveryPhase;old_place=old.RecoveryEnv.place_declared_fall;old_publish=old.RecoveryEnv.publish;old_configure=old.configure
 class FudanLowRisePhase(BasePhase):
  def __init__(self,n,device):
   super().__init__(n,device);self.recipe=torch.arange(n,device=device,dtype=torch.long)%26;self.env=None;self.needs_initial=torch.ones(n,device=device,dtype=torch.bool);self.totals=torch.zeros(4,device=device,dtype=torch.long)
  def active(self):return(self.recipe!=12)&(self.age<torch.where(self.recipe>=13,800,300))
  def mode(self):return torch.where(self.active(),3,0).long()
  def begin(self):self.request.copy_(self.active());self.delta.zero_()
  def update(self,gravity_z,root_speed,angular_speed):
   upright=((1-gravity_z)/2).clamp(0,1);low=self.recipe>=13;env=self.env;assert env is not None
   root=tensor(env.scene['robot'].data.root_state_w);height=root[:,2]-env.scene.env_origins[:,2];rise=((height-.1781)/(.25-.1781)).clamp(0,1);potential=torch.where(low,.5*upright+.5*upright*rise,upright);self.peak.copy_(torch.where(low&self.needs_initial,potential,self.peak));self.needs_initial.zero_();now=torch.where(self.request,torch.maximum(self.peak,potential),self.peak);self.delta.copy_(now-self.peak);self.peak.copy_(now)
   good=(gravity_z<-.984807753)&(root_speed<.03)&(angular_speed<.2)&self.request
   if bool(low.any()):
    force=tensor(env.scene.sensors['full_robot_contact'].contact_view.get_net_contact_forces(dt=float(env.physics_dt))).reshape(self.n,31,3).norm(dim=-1);wheel=force[:,env.e3_wheels];base=force[:,env.e3_contact_names.index('chassis')];good&=~low|((height>=.23)&(wheel>1.).all(-1)&(base<1.))
   self.stable.copy_(torch.where(good,self.stable+2,0));event=(self.stable>=50)&~self.credited;self.delta.add_(event.float());self.credited|=event;self.age+=2
  def reset(self,ids,initial_upright=None):
   low=self.recipe[ids]>=13;ended=self.age[ids]>0;credit=self.credited[ids];self.totals+=torch.stack(((low&ended).sum(),(low&ended&credit).sum(),(~low&ended).sum(),(~low&ended&credit).sum()));super().reset(ids,initial_upright);self.needs_initial[ids]=True
  def state_dict(self):return dict(version='fudan_legal_lowrise_v1',tensors={k:getattr(self,k).clone()for k in('age','recipe','peak','delta','stable','credited','request','needs_initial','totals')},scene_resume='explicit fresh environment; not bitwise PhysX continuation')
  def load_state_dict(self,s):
   assert s['version']=='fudan_legal_lowrise_v1'
   for k,v in s['tensors'].items():
    a=getattr(self,k);assert a.shape==v.shape and a.dtype==v.dtype;assert not v.is_floating_point()or torch.isfinite(v).all();a.copy_(v.to(a.device))
 def place(self,ids):
  regular=ids[self.recovery.recipe[ids]<13]
  if len(regular):old_place(self,regular)
  ids=ids[self.recovery.recipe[ids]>=13]
  if not len(ids):return
  assert _POSES is not None,'bind_after_build must precede the sole explicit reset';r=self.scene['robot'];q=torch.zeros((len(ids),len(r.joint_names)),device=self.device);root=tensor(r.data.root_state_w)[ids].clone();root[:,:2]=self.scene.env_origins[ids,:2];root[:,2]=self.scene.env_origins[ids,2]+.1781;root[:,3:7]=torch.tensor([0.,0.,0.,1.],device=self.device);root[:,7:]=0
  # Native Isaac convention is xyzw (the original fall cache uses the same convention).
  for k,p in enumerate(_POSES):
   rows=((self.recovery.recipe[ids]-13)%len(_POSES))==k
   for side,jv in p['joint_values'].items():
    for name,value in jv.items():q[rows,r.joint_names.index(side+'_'+name)]=float(value)
  r.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids);r.write_root_state_to_sim(root,env_ids=ids);self.recovery.reset(ids,torch.ones(len(ids),device=self.device));self.publish();self.e3_fudan_low_reset_receipt=dict(root_height_m=.1781,source_31body_contract_joint_bounds_unchanged=True,body_and_both_wheels_ground_supported_kinematic_initial_state=True,whole_leg_same_end_video_pose=False,zero_initial_velocities=True,no_pose_animation_or_external_lift=True)
 def publish(self):
  old_publish(self)
  if self.recovery is not None:
   import mod4_task
   mod4_task.height_cmd(self)[self.recovery.recipe>=13,0]=.25
 def masked_termination(env,original_func,original_params,name):
  v=original_func(env,**original_params);p=getattr(env,'recovery',None)
  if p is None:return v
  env.recovery_original_soft[name]=v.clone();return v&~p.active()
 def masked_reward(env,original_func,original_params,reward_name=None):
  value=original_func(env,**original_params);p=getattr(env,'recovery',None)
  if p is None:return value
  # Keep original fallen masking. Low-rise must actually be paid for raising its body,
  # while vertical-velocity penalty stays masked during its requested lift.
  mask=p.request&((p.recipe<13)|(reward_name=='lin_vel_z'));return torch.where(mask,torch.zeros_like(value),value)
 def configure(cfg):
  cfg=old_configure(cfg)
  for name in old.MASKED_REWARDS:
   t=getattr(cfg.rewards,name,None)
   if t is not None:t.func=masked_reward;t.params['reward_name']=name
  return cfg
 old.RecoveryPhase=FudanLowRisePhase;old.RecoveryEnv.place_declared_fall=place;old.RecoveryEnv.publish=publish;old.masked_termination=masked_termination;old.masked_reward=masked_reward;old.configure=configure

def bind_after_build(env,jobroot):
 global _POSES
 p=Path(jobroot)/'fudan_task_pose.json';v=json.loads(p.read_bytes());assert v['kind']=='NOMINAL_CONTRACT_PARITY_PLUS_KINEMATIC_POSE_SEARCH_NOT_SKILL'and v['body_count']==31 and v['coordinates']==30 and v['same_end_poses']==0;_POSES=v['best_candidates'];assert _POSES and all(x['original_ranges_preserved']and not x['same_end_knee_and_wheel']for x in _POSES);env.recovery.env=env;env.e3_reset_enabled=True

def state_summary(env):
 from h1_fullstate_environment_v1 import tensor
 p=env.recovery;low=p.recipe>=13;z=tensor(env.scene['robot'].data.root_state_w)[:,2]-env.scene.env_origins[:,2]
 return dict(kind='TRAINING_CURRICULUM_DESCRIPTION_NOT_INDEPENDENT_SKILL_PASS_RATE',recipes=26,original_falls_0_11_retained=True,normal_12_retained=True,lowrise_13_25=True,low_envs=int(low.sum()),low_current_credited=int((low&p.credited).sum()),low_height_mean=float(z[low].mean()),low_height_ge_023=int((low&(z>=.23)).sum()),completed_training_low_episodes=int(p.totals[0]),credited_training_low_episodes=int(p.totals[1]),completed_training_other_episodes=int(p.totals[2]),credited_training_other_episodes=int(p.totals[3]),new_local_lowrise_predicate=dict(height_min_m=.23,gravity_z_max=-.984807753,root_speed_max_m_s=.03,angular_speed_max_rad_s=.2,two_wheel_last_substep_force_min_N=1.,chassis_force_max_N=1.,continuous_s=.5,request_window_s=8.),original_74_grader_unchanged=True,exact_video_whole_leg_same_end_covered=False)
