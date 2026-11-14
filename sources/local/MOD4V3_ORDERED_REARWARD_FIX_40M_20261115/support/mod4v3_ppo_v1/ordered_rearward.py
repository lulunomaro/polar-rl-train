"""Contact -> rearward -> load transfer -> retract/lift; original plant and actor35 unchanged."""
from pathlib import Path
import json,types
import torch
from isaaclab.utils.math import quat_apply,quat_from_euler_xyz,quat_mul
from .scut_flat_env import tensor
from .rearward_support import RearwardSupport
from .ordered_credit import ordered_credit,world_tread_clearance

class OrderedRearward(RearwardSupport):
 def __init__(self,env):
  super().__init__(env)
  n=env.num_envs;dev=env.device
  self.phase=torch.zeros(n,dtype=torch.long,device=dev)
  self.support_dwell=torch.zeros_like(self.phase)
  self.phase_events=torch.zeros(4,dtype=torch.long,device=dev)
  self.reference_length=torch.zeros(n,2,device=dev);self.lift_origin=self.reference_length.clone()
  self.best=torch.zeros(n,3,device=dev)
  bounds=json.loads((Path(__file__).parent/'ordered_collision_bounds.json').read_text())['bounding_radius_m']
  self.leg_ids=[i for i,name in enumerate(self.names) if name in bounds and 'guide' not in name and 'wheel' not in name and i!=self.base]
  self.support_ids=self.leg_ids+self.guide+[self.base]
  self.leg_count=len(self.leg_ids)
  self.bounding=torch.tensor([bounds.get(self.names[i],.025) for i in self.support_ids],device=dev)
  self.weight=tensor(env.robot.root_physx_view.get_masses()).to(dev).sum(-1)*9.81
  bank=json.loads((Path(__file__).parent/'ordered_blocked_reset_bank.json').read_text());self.blocked=bank['poses']
  self.blocked_q=torch.tensor([[row['joint_positions'].get(name,0.) for name in env.robot.joint_names] for row in self.blocked],device=dev)
  self.upper_leg_force=torch.zeros(n,device=dev);self.contact_now=torch.zeros(n,dtype=torch.bool,device=dev)
  original_post=env.reward._postprocess_reward_terms
  def post(reward,terms):
   values=original_post(terms)
   moving=(self.phase==1)|(self.phase==2)
   for name in values:
    if name=='pen_theta_no0' or 'wheel_heading_x_centering' in name:
     values[name]=torch.where(moving,torch.zeros_like(values[name]),values[name])
   return values
  env.reward._postprocess_reward_terms=types.MethodType(post,env.reward)

 def reset(self,picked):
  e=self.env
  for v in [self.assisted,self.mounted,self.armed,self.support_paid,self.contact_now]:v[picked]=False
  self.phase[picked]=0;self.support_dwell[picked]=0;self.previous_stage[picked]=-9
  self.best[picked]=0.;self.reference[picked]=0.;self.reference_length[picked]=0.;self.allowed[picked]=False
  up=picked[e.stair_up[picked]]
  if not len(up):return
  gen=e.reset_generator;e.stair_speed[up]=torch.empty(len(up),device=e.device).uniform_(.35,.75,generator=gen)
  assist=up[torch.rand(len(up),device=e.device,generator=gen)<.30]
  if not len(assist):return
  row=torch.randint(len(self.blocked),(len(assist),),device=e.device,generator=gen)
  stage=e.stair_stage[assist];side=e.stair_side[assist];center=e._center()[assist]
  edge=torch.where(stage==0,2.9,1.4)
  inward=torch.tensor([x['root_inward_of_edge_m'] for x in self.blocked],device=e.device)[row]
  y=torch.tensor([x['root_y_m'] for x in self.blocked],device=e.device)[row]
  z=torch.tensor([x['root_above_lower_m'] for x in self.blocked],device=e.device)[row]
  qroot=torch.tensor([x['root_quat_xyzw'] for x in self.blocked],device=e.device)[row]
  yaw=torch.where(side<0,0.,torch.pi);zero=torch.zeros_like(yaw)
  turn=quat_from_euler_xyz(zero,zero,yaw)
  root=tensor(e.robot.data.default_root_state)[assist].clone()
  root[:,:3]=center;root[:,0]+=side*(edge-inward);root[:,1]+=-side*y;root[:,2]=stage*.2+z
  root[:,3:7]=quat_mul(turn,qroot);root[:,7:]=0.
  q=self.blocked_q[row]
  e.robot.write_root_state_to_sim(root,env_ids=assist);e.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=assist)
  self.assisted[assist]=True;e.stair_initial_stage[assist]=-1;e.stair_mid[assist]=True
  e.stair_approach_yaw[assist]=0.;e.stair_approach_group[assist]=0;e.stair_start[assist]=edge-inward
  e.episode_length_buf[assist]=150;e.height[assist]=.42
  e.reward.ground_z_est[assist]=stage*.2;e.reward._invalidate_step_caches();self.stats[0]+=len(assist)

 def endpoint(self):
  e=self.env;root=e.view.data.root_pos_w;body=e.view.data.body_pos_w;center=e._center();stage=e.stair_stage.clamp_max(1)
  changed=self.previous_stage!=stage
  self.phase[changed]=0;self.support_dwell[changed]=0;self.best[changed]=0.;self.armed[changed]=False
  self.mounted[changed]=False;self.support_paid[changed]=False;self.previous_stage.copy_(stage)
  forces=tensor(e.scene['contacts'].data.net_forces_w)[:,self.sensor_ids]
  ids=self.support_ids;pos=body[:,ids].clone();pos[:,-1,2]-=.17;force=forces[:,ids]
  x=(pos[:,:,0]-center[:,None,0])*e.stair_side[:,None];y=(pos[:,:,1]-center[:,None,1]).abs();z=pos[:,:,2]
  edge=torch.where(stage==0,2.9,1.4);upper=(stage+1)*.2;lower=stage*.2
  upaxis=torch.zeros(e.num_envs,3,device=e.device);upaxis[:,2]=1.
  upright=quat_apply(e.view.data.root_quat_w[:,[1,2,3,0]],upaxis)[:,2]>.8
  selected=e.continuous_stair_mask&e.stair_up&upright&(e.stair_stage<2)
  width=torch.where(stage==0,2.9,1.4)
  inside=(x<edge[:,None]+.12)&(x>torch.where(stage==0,1.39,-1.42)[:,None])&(y<width[:,None])
  close_z=(z-upper[:,None]).abs()<.065
  leg_close=(z-upper[:,None]).abs()<(self.bounding[None,:]+.04)
  no_lower=(z-self.bounding[None,:])>(lower[:,None]+.01)
  geom=close_z.clone();geom[:,:self.leg_count]=leg_close[:,:self.leg_count]&no_lower[:,:self.leg_count]
  valid=inside&geom&(force[:,:,2]>5.)&selected[:,None]
  wall=((x-edge[:,None]).abs()<self.bounding[None,:]+.06)&(y<width[:,None])&(z>lower[:,None]+.02)&(z<upper[:,None]+.22)&(force[:,:,0]*e.stair_side[:,None]>3.)&selected[:,None]
  self.allowed.zero_();self.allowed[:,ids]=valid|wall
  self.support_force=(force[:,:,2].clamp_min(0)*valid).sum(1)
  self.upper_leg_force=(force[:,:self.leg_count,2].clamp_min(0)*valid[:,:self.leg_count]).sum(1)
  wheels=body[:,e.stair_wheel_idx]
  axis=torch.zeros(e.num_envs,3,device=e.device);axis[:,0]=1.
  forward=quat_apply(e.view.data.root_quat_w[:,[1,2,3,0]],axis)
  longitudinal=((wheels-root[:,None,:])*forward[:,None,:]).sum(-1)
  wheel_x=(wheels[:,:,0]-center[:,None,0])*e.stair_side[:,None]
  wheel_wall=((wheel_x-edge[:,None]).abs()<.14)&(forces[:,e.stair_wheel_idx,0]*e.stair_side[:,None]>5.)
  self.contact_now=selected&((wall|valid).any(1)|wheel_wall.any(1))&(e.episode_length_buf*e.step_dt>=3.)
  new_touch=(self.phase==0)&self.contact_now
  self.phase[new_touch]=1;self.armed[new_touch]=True;self.reference[new_touch]=longitudinal[new_touch]
  self.reference_length[new_touch]=e.reward.length[new_touch];self.phase_events[0]+=new_touch.sum();self.stats[1]+=new_touch.sum()
  self.longitudinal=longitudinal;self.rear_delta=self.reference-longitudinal
  self.clearance=world_tread_clearance(wheels[:,:,2],stage)
  rear_ready=(self.rear_delta.amin(1)>=.025)
  loaded=self.support_force>=.20*self.weight
  ready=selected&(self.phase==1)&rear_ready&loaded
  self.support_dwell=torch.where(ready,self.support_dwell+1,torch.zeros_like(self.support_dwell))
  new_retract=(self.phase==1)&(self.support_dwell>=3)
  self.phase[new_retract]=2;self.reference_length[new_retract]=e.reward.length[new_retract];self.lift_origin[new_retract]=self.clearance[new_retract]
  self.phase_events[1]+=new_retract.sum();self.stats[3]+=new_retract.sum()
  self.mounted=(self.phase==2)&selected&(self.support_force>5.)
  top=(wheel_x<edge[:,None]-.02)&(self.clearance.abs()<.05)&(forces[:,e.stair_wheel_idx,2]>5.)
  landed=top.all(1)&selected&((self.phase==1)|(self.phase==2))
  self.phase_events[2]+=landed.sum();self.phase[landed]=3;self.mounted[landed]=False
  # The pose reached before touch is the baseline, not newly earned movement.
  self.best[new_touch,0]=(self.support_force[new_touch]/(.20*self.weight[new_touch])).clamp(0,1)

 def gain(self,active):
  e=self.env;contacted=active&((self.phase==1)|(self.phase==2))
  ready=active&(self.phase==2)&self.mounted
  support=(self.support_force/(.20*self.weight)).clamp(0,1)
  rear=(self.rear_delta/.10).clamp(0,1).mean(1)
  lift=((self.clearance-self.lift_origin)/.20).clamp(0,1).mean(1)
  retract=((self.reference_length-e.reward.length)/.08).clamp(0,1).mean(1)
  current=torch.stack((support,rear,.75*lift+.25*retract),dim=1)
  gain,self.best=ordered_credit(current,self.best,contacted,ready)
  early=(self.phase==1)*((self.reference_length-e.reward.length-.02)/.08).clamp(0,1).mean(1)
  self.stats[4]+=(gain[:,1]>0).sum();self.stats[5]+=(gain[:,2]>0).sum()
  return .2*gain[:,0]+.4*gain[:,1]+.4*gain[:,2]-.10*e.step_dt*early

 def summary(self):
  result=super().summary()
  result.update(rearward_target_absolute_body_x_m=None,reward='ordered finite support/rearward gain, then gated lift/retract; relative rearward target0.10m',world_tread_heights_m=[.2,.4],terrain_origin_z_used=False,strategy='high stance -> real riser contact -> rearward before retract -> upper support -> lift/land/stand',phase_counts=torch.bincount(self.phase,minlength=4).tolist(),phase_events=self.phase_events.tolist(),phase_labels=['approach','rearward','supported_retract','landed'],support_force_all_selected_N_mean=float(self.support_force.mean()),support_force_legs_N_max=float(self.upper_leg_force.max()),support_weight_fraction_max=float((self.support_force/self.weight).max()),rearward_before_retract_m=.025,required_upper_support_weight_fraction=.20,required_support_endpoints=3,auxiliary_pose_count=17,auxiliary_pose_projection_only=True,old_reference_loss_enabled=False,phase_in_actor_observation=False)
  return result
