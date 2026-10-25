"""Own H1 public-request observer and reward environment; inherited physical loop unchanged."""
import torch
from chassis_pd_training_env import ChassisPDMod4Env
from h1_public_request_phase_v1 import H1PublicRequestPhase
from h1_authored_full_collider_plane_reference_v1 import extract,evaluate
def tensor(v):
 if hasattr(v,'torch'):return v.torch
 if torch.is_tensor(v):return v
 import warp as wp
 return wp.to_torch(v)
class H1FullstateEnv(ChassisPDMod4Env):
 def __init__(self,*a,**kw):
  self.h1_phase=None;self.h1_capture=False;self.h1_physical_rows=[];self.h1_control_frame=None;self.h1_stepping=False
  super().__init__(*a,**kw);self.h1_phase=H1PublicRequestPhase(self.num_envs,self.device);robot=self.scene['robot'];self.h1_body_names=list(robot.body_names);self.h1_sensor=self.scene.sensors['full_robot_contact'];self.h1_contact_names=list(self.h1_sensor.body_names);assert len(self.h1_contact_names)==31 and set(self.h1_body_names)==set(self.h1_contact_names);self.h1_shapes=extract(self.sim.stage,'/World/envs/env_0/Robot',self.h1_body_names);assert len(self.h1_shapes)==34
  self.h1_wheel_shapes=[[i for i,s in enumerate(self.h1_shapes) if s['body']==name] for name in ('left_wheel','right_wheel')];self.h1_contact_wheels=[self.h1_contact_names.index(x) for x in ('left_wheel','right_wheel')];self.h1_nonwheel=[i for i,x in enumerate(self.h1_contact_names) if x not in ('left_wheel','right_wheel')];self.h1_witness_ids=torch.tensor([0,1,2,3,self.num_envs//4,self.num_envs//2,3*self.num_envs//4,self.num_envs-1],device=self.device,dtype=torch.long)
  self.h1_force_error=0.;self.h1_callback_count=0;original_update=self.scene.update
  def update(dt):
   original_update(dt)
   if not self.h1_stepping:return
   r=self.scene['robot'];pos=tensor(r.data.body_pos_w);qbody=tensor(r.data.body_quat_w);root=tensor(r.data.root_state_w);clear=evaluate(pos,qbody,self.h1_shapes);forces=tensor(self.h1_sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(self.num_envs,31,3);wheelraw=tensor(self._integrated_contact.sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(self.num_envs,2,3);wheelmean=self._integrated_contact.history[:,0];wc=torch.stack([clear[:,ids].amin(-1) for ids in self.h1_wheel_shapes],-1);non=forces[:,self.h1_nonwheel].norm(dim=-1).amax(-1);wheel_norm=wheelmean.norm(dim=-1);planar_speed=root[:,7:9].norm(dim=-1);x,y,z,w=root[:,3:7].unbind(-1);roll=torch.atan2(2*(w*x+y*z),1-2*(x*x+y*y));pitch=torch.asin((2*(w*y-z*x)).clamp(-1,1));yaw=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z));event=self.h1_phase.physical(wheel_N=wheel_norm,wheel_clear_m=wc,all_min_clear_m=clear.amin(-1),nonwheel_max_N=non,root_vz=root[:,9],root_planar_speed=planar_speed,roll=roll,pitch=pitch,yaw=yaw);self.h1_callback_count+=1
   if self.h1_capture:
    err=float((forces[:,self.h1_contact_wheels]-wheelraw).abs().amax());self.h1_force_error=max(self.h1_force_error,err);assert self.h1_force_error<=.1
    ids=self.h1_witness_ids;row=dict(root13=root.clone(),q30=tensor(r.data.joint_pos).clone(),all34_clearance=clear.clone(),all31_contact_force=forces.clone(),wheel_raw=wheelraw.clone(),wheel_5ms_mean=wheelmean.clone(),wheel_norm_N=wheel_norm.clone(),root_planar_speed=planar_speed.clone(),wheel_clearance=wc.clone(),nonwheel_max=non.clone(),roll=roll.clone(),pitch=pitch.clone(),yaw=yaw.clone(),event_delta=event['event_delta'].clone(),takeoff=event['takeoff'].clone(),landing=event['landing'].clone(),recovery=event['recovery'].clone(),prepared=event['prepared'].clone(),episode=self._sensor_mild.episode.clone(),witness_body_pos=pos[ids].clone(),witness_body_quat_xyzw=qbody[ids].clone());self.h1_physical_rows.append(row)
  self.scene.update=update
  original_term=self.termination_manager.compute
  def termination(*aa,**kk):
   out=original_term(*aa,**kk)
   if self.h1_stepping:
    if self.h1_capture:
     import mod4_task as task
     r=self.scene['robot'];self.h1_control_frame=dict(root13=tensor(r.data.root_state_w).clone(),q30=tensor(r.data.joint_pos).clone(),executed6=self.action_manager.action.clone(),impulse=self._integrated_contact.impulse.clone(),history=self._integrated_contact.history.clone(),closure=torch.stack(list(task.closure_errors(self).values())).amax(0),mimic=torch.stack(list(task.mimic_errors(self).values())).amax(0),ground=task.ground_height(self).clone(),public_request=self.h1_phase.request_for_action.clone(),event_expected=self.h1_phase.event_control.clone())
    self.h1_phase.finish_control_before_selected_reset()
   return out
  self.termination_manager.compute=termination;original_observation=self.observation_manager.compute
  def observation(*aa,**kk):
   self._h1_publish_external_request();return original_observation(*aa,**kk)
  self.observation_manager.compute=observation;self._h1_publish_external_request();original_reward=self.reward_manager.compute
  def reward(dt,*aa,**kk):
   out=original_reward(dt,*aa,**kk)
   if self.h1_capture and self.h1_stepping:
    idx=self.reward_manager._term_names.index('h1_control_events');self.h1_control_frame['event_applied']=tensor(self.reward_manager._step_reward)[:,idx].clone()*self.h1_reward_readout_scale
   return out
  self.reward_manager.compute=reward
 def _h1_publish_external_request(self):
  if self.h1_phase is not None:
   self._mod4_mode_bit=self.h1_phase.public_mode();term=self.command_manager.get_term('twist');term.set_manual_evaluation_mode();term.vel_command_b.zero_()
 def _reset_idx(self,env_ids):
  result=super()._reset_idx(env_ids)
  if self.h1_phase is not None:self.h1_phase.reset(env_ids);self._h1_publish_external_request()
  return result
 def step(self,action):
  self.h1_phase.begin_control();self.h1_stepping=True
  try:return super().step(action)
  finally:self.h1_stepping=False
