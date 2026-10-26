"""Read-only pre-reset capture, inherited flat robot/physics; H1 external request only."""
import os,torch
from chassis_pd_training_env import ChassisPDMod4Env
class E2H1FlatEnv(ChassisPDMod4Env):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self._own_flat_frame=None;self._own_raw_physical=[];self._own_native_capture=False
  original=self.termination_manager.compute
  def compute(*aa,**kk):
   out=original(*aa,**kk)
   if self._own_native_capture:
    import mod4_task as task
    r=self.scene['robot'];ground=task.ground_height(self)
    self._own_flat_frame=dict(root13=r.data.root_state_w.clone(),q30=r.data.joint_pos.clone(),joint_vel=r.data.joint_vel.clone(),applied_torque=r.data.applied_torque.clone(),ground=ground.clone(),closure=torch.stack(list(task.closure_errors(self).values())).amax(0),mimic=torch.stack(list(task.mimic_errors(self).values())).amax(0),executed6=self.action_manager.action.clone(),impulse=self._integrated_contact.impulse.clone(),history=self._integrated_contact.history.clone(),command=self.command_manager.get_term('twist').command.clone())
   return out
  self.termination_manager.compute=compute
  oldupdate=self.scene.update
  def update(dt):
   oldupdate(dt)
   if self._own_native_capture:
    raw=self._integrated_contact.sensor.contact_view.get_net_contact_forces(dt=float(self.physics_dt))
    if hasattr(raw,'torch'):raw=raw.torch
    elif not torch.is_tensor(raw):
     import warp as wp
     raw=wp.to_torch(raw)
    self._own_raw_physical.append(raw.reshape(self.num_envs,2,3).clone())
  self.scene.update=update
 def step(self,action):
  if os.environ['OWN_E2_H1_KIND']=='E5_H1_OPERATOR_JUMP_NATIVE_ADMISSION':
   term=self.command_manager.get_term('twist');term.set_manual_evaluation_mode();term.vel_command_b.zero_();self._mod4_mode_bit=torch.full((self.num_envs,),4,device=self.device,dtype=torch.long)
  return super().step(action)
