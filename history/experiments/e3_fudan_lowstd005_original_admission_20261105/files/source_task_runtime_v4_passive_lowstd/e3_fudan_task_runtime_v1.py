"""New legal low-rise curriculum, not a replacement for the frozen 74-case E3 grader.
Install only after the entry has started SimulationApp, and before build_env.
Recipes 0..11 retain original falls, 12 retains normal, 13..25 request low-rise.
No joint envelope, actuator, physics, DR, noisy observation or action modification.
Positive tracking rewards retain V2 behavior, with no low-rise root-height gate.
Passive height and criterion evidence reuse the existing phase update before any reset.
"""
from pathlib import Path
from math import ceil
import json
import torch
_INSTALLED=False
_POSES=None
_LOWRISE_TIMEOUT_S=8.0
_LOWRISE_TIMEOUT_TERM='e3_fudan_lowrise_timeout8'
_TRACKING_REWARD_TERMS=('track_lin_vel','track_lin_vel_tight','track_ang_vel')
_LOWRISE_STATE_VERSION='fudan_legal_lowrise_passive_lowstd_v4'
_LOW_HEIGHT_SUMMARY_FIELDS=('samples','sumheight','ge023_samples','endedLowEpisodes','endedLowPeakGe023','endedLowPeakHeightSum')
_LOW_CRITERION_SUMMARY_FIELDS=('height_ok','upright_ok','speed_ok','angular_ok','wheels_ok','chassis_ok','joint_good')


def lowrise_timeout8(env):
 """Independent timeout: the framework increments episode_length_buf before compute.

 The episode counter resets to zero. At step_dt=.02, ceil(8/.02)=400,
 so the 400th completed policy step truncates, without using recovery.age/request.
 """
 p=getattr(env,'recovery',None)
 if p is None:return torch.zeros_like(env.episode_length_buf,dtype=torch.bool)
 policy_steps=ceil(_LOWRISE_TIMEOUT_S/float(env.step_dt))
 return(p.recipe>=13)&(env.episode_length_buf>=policy_steps)


def install_before_build():
 global _INSTALLED
 assert not _INSTALLED,'one install in a new own process';_INSTALLED=True
 import e3_recovery_runtime_v1 as old
 from h1_fullstate_environment_v1 import tensor
 BasePhase=old.RecoveryPhase;old_place=old.RecoveryEnv.place_declared_fall;old_publish=old.RecoveryEnv.publish;old_configure=old.configure
 class FudanLowRisePhase(BasePhase):
  def __init__(self,n,device):
   super().__init__(n,device);self.recipe=torch.arange(n,device=device,dtype=torch.long)%26;self.env=None;self.needs_initial=torch.ones(n,device=device,dtype=torch.bool);self.totals=torch.zeros(4,device=device,dtype=torch.long)
   self.low_episode_peak_height=torch.full((n,),.1781,device=device,dtype=torch.float32)
   self.low_rollout_summary=torch.zeros(6,device=device,dtype=torch.float64)
   self.low_criterion_summary=torch.zeros(7,device=device,dtype=torch.float64)
  def active(self):return(self.recipe!=12)&(self.age<torch.where(self.recipe>=13,800,300))
  def mode(self):return torch.where(self.active(),3,0).long()
  def begin(self):self.request.copy_(self.active());self.delta.zero_()
  def update(self,gravity_z,root_speed,angular_speed):
   upright=((1-gravity_z)/2).clamp(0,1);low=self.recipe>=13;env=self.env;assert env is not None
   root=tensor(env.scene['robot'].data.root_state_w);height=root[:,2]-env.scene.env_origins[:,2];rise=((height-.1781)/(.25-.1781)).clamp(0,1);potential=torch.where(low,.5*upright+.5*upright*rise,upright);self.peak.copy_(torch.where(low&self.needs_initial,potential,self.peak));self.needs_initial.zero_();now=torch.where(self.request,torch.maximum(self.peak,potential),self.peak);self.delta.copy_(now-self.peak);self.peak.copy_(now)
   # Fixed-size passive evidence: reuse this update's already-read height and low mask.
   self.low_episode_peak_height.copy_(torch.where(low,torch.maximum(self.low_episode_peak_height,height),self.low_episode_peak_height))
   self.low_rollout_summary[:3].add_(torch.stack((low.sum(dtype=torch.float64),torch.where(low,height,0.).sum(dtype=torch.float64),(low&(height>=.23)).sum(dtype=torch.float64))))
   good=(gravity_z<-.984807753)&(root_speed<.03)&(angular_speed<.2)&self.request
   if bool(low.any()):
    force=tensor(env.scene.sensors['full_robot_contact'].contact_view.get_net_contact_forces(dt=float(env.physics_dt))).reshape(self.n,31,3).norm(dim=-1);wheel=force[:,env.e3_wheels];base=force[:,env.e3_contact_names.index('chassis')];good&=~low|((height>=.23)&(wheel>1.).all(-1)&(base<1.))
    self.low_criterion_summary.add_(torch.stack((
     (low&(height>=.23)).sum(dtype=torch.float64),
     (low&(gravity_z<-.984807753)).sum(dtype=torch.float64),
     (low&(root_speed<.03)).sum(dtype=torch.float64),
     (low&(angular_speed<.2)).sum(dtype=torch.float64),
     (low&(wheel>1.).all(-1)).sum(dtype=torch.float64),
     (low&(base<1.)).sum(dtype=torch.float64),
     (low&good).sum(dtype=torch.float64))))
   self.stable.copy_(torch.where(good,self.stable+2,0));event=(self.stable>=50)&~self.credited;self.delta.add_(event.float());self.credited|=event;self.age+=2
  def reset(self,ids,initial_upright=None):
   low=self.recipe[ids]>=13;ended=self.age[ids]>0;credit=self.credited[ids];self.totals+=torch.stack(((low&ended).sum(),(low&ended&credit).sum(),(~low&ended).sum(),(~low&ended&credit).sum()))
   ended_low=low&ended;episode_peak=self.low_episode_peak_height[ids]
   self.low_rollout_summary[3:].add_(torch.stack((ended_low.sum(dtype=torch.float64),(ended_low&(episode_peak>=.23)).sum(dtype=torch.float64),torch.where(ended_low,episode_peak,0.).sum(dtype=torch.float64))))
   self.low_episode_peak_height[ids]=.1781
   super().reset(ids,initial_upright);self.needs_initial[ids]=True
  def state_dict(self):
   # Preserve the base typed state and any unknown base metadata/tensor fields.
   state=super().state_dict();state['version']=_LOWRISE_STATE_VERSION
   state['tensors'].update({k:getattr(self,k).clone()for k in('needs_initial','totals','low_episode_peak_height','low_rollout_summary','low_criterion_summary')})
   state['scene_resume']='explicit fresh environment; not bitwise PhysX continuation'
   return state
  def load_state_dict(self,s):
   assert s['version']==_LOWRISE_STATE_VERSION
   assert {'low_episode_peak_height','low_rollout_summary','low_criterion_summary'}<=s['tensors'].keys()
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
  # Add after original soft-term wrapping; never route this independent term through request masking.
  from isaaclab.managers import TerminationTermCfg
  setattr(cfg.terminations,_LOWRISE_TIMEOUT_TERM,TerminationTermCfg(func=lowrise_timeout8,time_out=True))
  return cfg
 old.RecoveryPhase=FudanLowRisePhase;old.RecoveryEnv.place_declared_fall=place;old.RecoveryEnv.publish=publish;old.masked_termination=masked_termination;old.masked_reward=masked_reward;old.configure=configure


def bind_after_build(env,jobroot):
 global _POSES
 p=Path(jobroot)/'fudan_task_pose.json';v=json.loads(p.read_bytes());assert v['kind']=='NOMINAL_CONTRACT_PARITY_PLUS_KINEMATIC_POSE_SEARCH_NOT_SKILL'and v['body_count']==31 and v['coordinates']==30 and v['same_end_poses']==0;_POSES=v['best_candidates'];assert _POSES and all(x['original_ranges_preserved']and not x['same_end_knee_and_wheel']for x in _POSES);env.recovery.env=env;env.e3_reset_enabled=True


def _function_name(func):
 return getattr(func,'__module__',type(func).__module__)+'.'+getattr(func,'__qualname__',type(func).__qualname__)


def _constructed_tracking_summary(env):
 terms={}
 for name in _TRACKING_REWARD_TERMS:
  term=getattr(env.cfg.rewards,name);func=term.func
  terms[name]=dict(weight=float(term.weight),func=_function_name(func),original_func=_function_name(getattr(func,'__wrapped__',func)),params=dict(term.params),height_gate_installed=getattr(func,'_e3_fudan_lowheightgate',False) is True)
 return dict(source='constructed env.cfg.rewards; not module defaults',height_gate_enabled=False,terms=terms)


def state_summary(env):
 from h1_fullstate_environment_v1 import tensor
 p=env.recovery;low=p.recipe>=13;z=tensor(env.scene['robot'].data.root_state_w)[:,2]-env.scene.env_origins[:,2]
 summary=dict(kind='TRAINING_CURRICULUM_DESCRIPTION_NOT_INDEPENDENT_SKILL_PASS_RATE',recipes=26,original_falls_0_11_retained=True,normal_12_retained=True,lowrise_13_25=True,low_envs=int(low.sum()),low_current_credited=int((low&p.credited).sum()),low_height_mean=float(z[low].mean()),low_height_ge_023=int((low&(z>=.23)).sum()),completed_training_low_episodes=int(p.totals[0]),credited_training_low_episodes=int(p.totals[1]),completed_training_other_episodes=int(p.totals[2]),credited_training_other_episodes=int(p.totals[3]),new_local_lowrise_predicate=dict(height_min_m=.23,gravity_z_max=-.984807753,root_speed_max_m_s=.03,angular_speed_max_rad_s=.2,two_wheel_last_substep_force_min_N=1.,chassis_force_max_N=1.,continuous_s=.5,request_window_s=8.),original_74_grader_unchanged=True,exact_video_whole_leg_same_end_covered=False,lowrise_timeout8=dict(term_name=_LOWRISE_TIMEOUT_TERM,time_out=bool(getattr(env.cfg.terminations,_LOWRISE_TIMEOUT_TERM).time_out),duration_s=_LOWRISE_TIMEOUT_S,policy_steps=ceil(_LOWRISE_TIMEOUT_S/float(env.step_dt)),step_dt_s=float(env.step_dt),counter='env.episode_length_buf',recipe_mask='recipe>=13',request_mask_applied=False,phase_age_used=False),actual_env_cfg_episode_length_s=float(env.cfg.episode_length_s))
 values=p.low_rollout_summary.detach().cpu().tolist();evidence=dict(zip(_LOW_HEIGHT_SUMMARY_FIELDS,values));samples=values[0];ended=values[3]
 evidence.update(source='existing phase.update height before reset: root_z minus env_origin_z',scope='cumulative phase state, not a single PPO rollout',dtype='float64',descriptive_only_not_acceptance=True,sample_height_mean_m=values[1]/samples if samples else None,sample_ge023_fraction=values[2]/samples if samples else None,ended_low_peak_height_mean_m=values[5]/ended if ended else None,ended_low_peak_ge023_fraction=values[4]/ended if ended else None)
 summary['low_rollout_summary']=evidence;summary['tracking_reward_config']=_constructed_tracking_summary(env)
 criterion_values=p.low_criterion_summary.detach().cpu().tolist();criterion_counts=dict(zip(_LOW_CRITERION_SUMMARY_FIELDS,criterion_values));criterion_fractions={k:v/samples if samples else None for k,v in criterion_counts.items()}
 summary['low_criterion_summary']=dict(names=_LOW_CRITERION_SUMMARY_FIELDS,counts=criterion_counts,fractions=criterion_fractions,samples=samples,source='existing phase.update criterion tensors before reset',scope='cumulative phase state, not a single PPO rollout',dtype='float64',cumulative=True,descriptive_only_not_acceptance=True,descriptive_not_acceptance=True)
 return summary
