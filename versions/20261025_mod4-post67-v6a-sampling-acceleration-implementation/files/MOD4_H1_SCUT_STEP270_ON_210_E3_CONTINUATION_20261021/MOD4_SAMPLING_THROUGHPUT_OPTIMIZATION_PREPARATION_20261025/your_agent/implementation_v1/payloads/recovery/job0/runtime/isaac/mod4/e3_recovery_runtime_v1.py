"""Isolated recovery task. Original hardware, DR and physical step retained."""
import torch,numpy as np
from pathlib import Path
from chassis_pd_training_env import ChassisPDMod4Env
from e3_public_recovery_phase_v1 import RecoveryPhase
from h1_authored_full_collider_plane_reference_v1 import extract,evaluate
from h1_fullstate_environment_v1 import tensor
from e3_reset_bank_cache_v1 import E3ResetBankCache
MASKED_REWARDS=('height','height_tight','height_both_wheels','height_square','height_deficit','height_error_l1','lin_vel_z')
def masked_termination(env,original_func,original_params,name):
 value=original_func(env,**original_params);phase=getattr(env,'recovery',None)
 if phase is None:return value
 active=(phase.recipe!=12)&(phase.age<300);env.recovery_original_soft[name]=value.clone();return value&~active
def masked_reward(env,original_func,original_params):
 value=original_func(env,**original_params);p=getattr(env,'recovery',None);return value if p is None else torch.where(p.request,torch.zeros_like(value),value)
def recovery_event_rate(env):
 p=getattr(env,'recovery',None);return torch.zeros(env.num_envs,device=env.device) if p is None else p.delta/float(env.step_dt)
def configure(cfg):
 from isaaclab.managers import RewardTermCfg
 for name in ('bad_orientation','base_contact'):
  t=getattr(cfg.terminations,name);assert not t.time_out;t.func,t.params=masked_termination,dict(original_func=t.func,original_params=dict(t.params),name=name)
 for name in MASKED_REWARDS:
  t=getattr(cfg.rewards,name,None)
  if t is not None:t.func,t.params=masked_reward,dict(original_func=t.func,original_params=dict(t.params))
 cfg.rewards.e3_upright_peak_and_recovery=RewardTermCfg(func=recovery_event_rate,weight=1.)
 return cfg
class RecoveryEnv(ChassisPDMod4Env):
 def __init__(self,*a,**kw):
  self.e3_reset_enabled=False;self.recovery=None;self.recovery_original_soft={};self.e3_capture=False;self.e3_physical=[];self.e3_frame=None;self.e3_stepping=False
  super().__init__(*a,**kw);self.recovery=RecoveryPhase(self.num_envs,self.device);r=self.scene['robot'];self.e3_body_names=list(r.body_names);self.e3_contact_names=list(self.scene.sensors['full_robot_contact'].body_names);assert set(self.e3_body_names)==set(self.e3_contact_names) and len(self.e3_body_names)==31;self.e3_shapes=extract(self.sim.stage,'/World/envs/env_0/Robot',self.e3_body_names);assert len(self.e3_shapes)==34;self.e3_wheels=[self.e3_contact_names.index(n) for n in ('left_wheel','right_wheel')];self.e3_witness=torch.tensor([0,1,2,3,self.num_envs//4,self.num_envs//2,3*self.num_envs//4,self.num_envs-1],device=self.device)
  self._e3_fixed_reset_cache=E3ResetBankCache(Path(__file__).resolve().parent/'MOD4_RESET_COLLISION_BANK.npz',r.joint_names,self.device)
  original_update=self.scene.update
  def update(dt):
   original_update(dt)
   if self.e3_capture and self.e3_stepping:
    r=self.scene['robot'];pos=tensor(r.data.body_pos_w);quat=tensor(r.data.body_quat_w);force=tensor(self.scene.sensors['full_robot_contact'].contact_view.get_net_contact_forces(dt=float(dt))).reshape(self.num_envs,31,3);wheel=tensor(self._integrated_contact.sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(self.num_envs,2,3);ids=self.e3_witness
    self.e3_physical.append(dict(root13=tensor(r.data.root_state_w).clone(),q30=tensor(r.data.joint_pos).clone(),all31_force=force.clone(),wheel_raw=wheel.clone(),witness_body_pos=pos[ids].clone(),witness_body_quat_xyzw=quat[ids].clone(),witness_clear34=evaluate(pos[ids],quat[ids],self.e3_shapes),episode=self._sensor_mild.episode.clone()))
  self.scene.update=update;original_term=self.termination_manager.compute
  def termination(*aa,**kk):
   out=original_term(*aa,**kk)
   if self.e3_stepping:
    r=self.scene['robot'];g=tensor(r.data.projected_gravity_b)[:,2];root=tensor(r.data.root_state_w);self.recovery.update(g,root[:,7:10].norm(dim=-1),root[:,10:13].norm(dim=-1))
    if self.e3_capture:
     import mod4_task as task
     self.e3_frame=dict(root13=root.clone(),q30=tensor(r.data.joint_pos).clone(),executed6=self.action_manager.action.clone(),impulse=self._integrated_contact.impulse.clone(),history=self._integrated_contact.history.clone(),closure=torch.stack(list(task.closure_errors(self).values())).amax(0),mimic=torch.stack(list(task.mimic_errors(self).values())).amax(0),gravity_z=g.clone(),event_delta=self.recovery.delta.clone(),request=self.recovery.request.clone(),age_after=self.recovery.age.clone(),peak=self.recovery.peak.clone(),soft_orientation=self.recovery_original_soft['bad_orientation'].clone(),soft_contact=self.recovery_original_soft['base_contact'].clone())
   return out
  self.termination_manager.compute=termination;original_obs=self.observation_manager.compute
  def observation(*aa,**kk):self.publish();return original_obs(*aa,**kk)
  self.observation_manager.compute=observation;self.publish()
 def publish(self):
  if self.recovery is not None:
   self._mod4_mode_bit=self.recovery.mode();t=self.command_manager.get_term('twist');t.set_manual_evaluation_mode();t.vel_command_b.zero_()
 def _reset_idx(self,ids):
  out=super()._reset_idx(ids)
  if self.recovery is not None and self.e3_reset_enabled and len(ids):self.place_declared_fall(ids)
  return out
 def place_declared_fall(self,ids):
  if self.recovery is not None and len(ids):
   r=self.scene['robot'];cache=self._e3_fixed_reset_cache
   q,quat,minimum,initial=cache.selected_geometry(self.recovery.recipe[ids],r.joint_names)
   pick=cache.pick
   root=tensor(r.data.root_state_w)[ids].clone();root[:,:2]=self.scene.env_origins[ids,:2];root[:,2]=.0001-minimum;root[:,3:7]=quat;root[:,7:]=0;r.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids);r.write_root_state_to_sim(root,env_ids=ids);self.recovery.reset(ids,initial);self.publish();self.e3_reset_receipt=dict(legal_original_q30_bank_pose=pick,public_request_normal_oneof13_and_twelve_fixed_fall_recipes=True,all_authored_sample_points_margin_m=.0001,zero_root_and_joint_velocity=True,geometry_bank_source_sha=cache.source_sha,not_cookedShapeLocal_or_manifold_nonpenetration=True)
 def step(self,action):
  self.recovery.begin();self.e3_stepping=True
  try:return super().step(action)
  finally:self.e3_stepping=False
