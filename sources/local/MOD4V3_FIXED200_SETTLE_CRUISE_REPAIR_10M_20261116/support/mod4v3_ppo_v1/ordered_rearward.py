"""Contact -> rearward -> load transfer -> retract/lift; original plant and actor35 unchanged."""
from pathlib import Path
import json,types
import torch
from isaaclab.utils.math import quat_apply,quat_from_euler_xyz,quat_mul
from .scut_flat_env import tensor
from .rearward_support import RearwardSupport
from .ordered_credit import world_tread_clearance
from .sequential_mount_credit import transfer_scores,transfer_credit,load_credit,lift_regression

class OrderedRearward(RearwardSupport):
 def __init__(self,env):
  super().__init__(env)
  n=env.num_envs;dev=env.device
  self.phase=torch.zeros(n,dtype=torch.long,device=dev)
  self.support_dwell=torch.zeros_like(self.phase)
  self.phase_events=torch.zeros(5,dtype=torch.long,device=dev)
  self.reference_length=torch.zeros(n,2,device=dev);self.lift_origin=self.reference_length.clone()
  self.best=torch.zeros(n,2,3,device=dev)
  self.best_lift=torch.zeros(n,2,device=dev);self.wheel_cleared=torch.zeros(n,2,device=dev,dtype=torch.bool)
  self.support_seen=torch.zeros(n,device=dev,dtype=torch.bool);self.maneuver=self.support_seen.clone()
  self.transfer_scores=torch.zeros(n,2,3,device=dev);self.lift_progress=torch.zeros(n,2,device=dev)
  self.last_transfer_gain=torch.zeros(n,device=dev);self.last_regression=torch.zeros(n,device=dev)
  self.loaded_once=torch.zeros(n,device=dev,dtype=torch.bool)
  self.load_score=torch.zeros(n,device=dev);self.best_load=torch.zeros(n,device=dev)
  self.last_components=torch.zeros(n,4,device=dev);self.component_totals=torch.zeros(4,device=dev)
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
   moving=self.maneuver
   for name in values:
    if name=='pen_theta_no0' or 'wheel_heading_x_centering' in name:
     values[name]=torch.where(moving,torch.zeros_like(values[name]),values[name])
   for name in list(values):
    if name.startswith('track_height_'):values[name]=torch.where(self.maneuver,torch.zeros_like(values[name]),values[name])
   return values
  env.reward._postprocess_reward_terms=types.MethodType(post,env.reward)

 def reset(self,picked):
  e=self.env
  for v in [self.assisted,self.mounted,self.armed,self.support_paid,self.contact_now]:v[picked]=False
  self.phase[picked]=0;self.support_dwell[picked]=0;self.previous_stage[picked]=-9
  self.loaded_once[picked]=False;self.best_load[picked]=0.;self.load_score[picked]=0.;self.last_components[picked]=0.
  self.best[picked]=0.;self.best_lift[picked]=0.;self.wheel_cleared[picked]=False;self.support_seen[picked]=False;self.maneuver[picked]=False;self.reference[picked]=0.;self.reference_length[picked]=0.;self.allowed[picked]=False
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
  self.loaded_once[changed]=False;self.best_load[changed]=0.;self.load_score[changed]=0.
  self.mounted[changed]=False;self.support_paid[changed]=False;self.best_lift[changed]=0.;self.wheel_cleared[changed]=False;self.support_seen[changed]=False;self.maneuver[changed]=False;self.previous_stage.copy_(stage)
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
  # Preparation is rewarded before mount; actual upper support releases lift credit.
  loaded=self.support_force>=.20*self.weight
  ready=selected&self.armed&loaded
  self.support_dwell=torch.where(ready,self.support_dwell+1,torch.zeros_like(self.support_dwell))
  new_retract=(self.phase==1)&(self.support_dwell>=3)
  self.loaded_once|=new_retract
  self.load_score=(self.support_force/(.20*self.weight).clamp_min(1.)).clamp(0.,1.)
  self.phase[new_retract]=2;self.reference_length[new_retract]=e.reward.length[new_retract]
  self.phase_events[1]+=new_retract.sum();self.stats[3]+=new_retract.sum()
  self.support_seen|=selected&self.armed&(self.support_force>5.)
  now_clear=self.clearance>=.015
  just_clear=(~self.wheel_cleared)&now_clear&self.loaded_once[:,None]&selected[:,None]
  self.wheel_cleared|=just_clear
  self.phase_events[2]+=just_clear.any(1).sum();self.stats[2]+=just_clear.sum()
  self.phase=torch.where(just_clear.any(1)&(self.phase<3),torch.full_like(self.phase,3),self.phase)
  top=(wheel_x<edge[:,None]-.02)&(self.clearance.abs()<.05)&(forces[:,e.stair_wheel_idx,2]>5.)
  landed=top.all(1)&selected&self.armed&(self.phase<4)
  self.phase_events[3]+=landed.sum();self.phase[landed]=4
  near=(wheel_x-edge[:,None]).abs().amin(1)<.55
  self.maneuver=selected&self.armed&(self.phase<4)&near
  # Actual upper contact selects supported-airborne reward treatment. Height freedom
  # starts at real near-edge contact and ends on bilateral landing.
  self.mounted=self.maneuver&(self.support_force>5.)
  inward=edge[:,None]-wheel_x
  self.transfer_scores,self.lift_progress=transfer_scores(longitudinal,self.reference,wheels[:,:,2],stage,inward,self.wheel_cleared)
  # Existing motion at reset/touch is the baseline, never newly earned credit.
  self.best[new_touch]=self.transfer_scores[new_touch]
  self.best_lift[new_touch]=self.lift_progress[new_touch]
  self.best_load[new_touch]=self.load_score[new_touch]
  # Existing lift at mount is not newly earned; reward subsequent retraction.
  self.best[new_retract,:,1]=self.lift_progress[new_retract]
  self.best_lift[new_retract]=self.lift_progress[new_retract]

 def gain(self,active):
  contact=active&self.maneuver&(self.env.stair_stage<2)
  lift_on=contact&self.loaded_once
  enabled=torch.stack((contact,lift_on,lift_on),dim=-1)[:,None,:]
  motion,self.best,parts=transfer_credit(self.transfer_scores,self.best,enabled)
  mounting,self.best_load=load_credit(self.load_score,self.best_load,contact)
  regression=lift_regression(self.lift_progress,self.best_lift,lift_on)
  self.best_lift=torch.where(lift_on[:,None],torch.maximum(self.best_lift,self.lift_progress),self.best_lift)
  self.last_components=torch.stack((.2*parts[:,:,0].mean(1),.2*mounting,.5*parts[:,:,1].mean(1),.1*parts[:,:,2].mean(1)),dim=-1)
  self.component_totals+=self.last_components.sum(0)
  gain=motion+.2*mounting
  self.stats[4]+=(gain>0).sum();self.stats[5]+=(regression>0).sum()
  self.last_transfer_gain=gain;self.last_regression=regression
  return gain-.5*self.env.step_dt*regression

 def summary(self):
  result=super().summary()
  result.update(columns=['assisted_resets','real_contact_events','wheel_clear_events','loaded_phase_events','sequential_gain_endpoints','lift_regression_endpoints','late_assisted_resets_legacy'],strategy='real contact -> rearward preparation on lower floor -> actual upper load transfer -> independent wheel lift -> clear/place -> land/stand',reward='0.6*(0.2 finite rear preparation+0.2 finite real load transfer+0.5 independent post-mount lift+0.1 post-clear placement) minus original local lift regression',phase_counts=torch.bincount(self.phase,minlength=5).tolist(),phase_events=self.phase_events.tolist(),phase_labels=['approach','contact_rearward_preparation','loaded_retract_lift','clear_and_place','landed'],phase_event_labels=['contact','loaded_transfer','wheel_clear','bilateral_landing','reserved'],world_tread_heights_m=[.2,.4],terrain_origin_z_used=False,height_exempt_maneuver_count=int(self.maneuver.sum()),support_seen_count=int(self.support_seen.sum()),loaded_once_count=int(self.loaded_once.sum()),wheel_clear_count=int(self.wheel_cleared.sum()),support_force_all_selected_N_mean=float(self.support_force.mean()),support_force_legs_N_max=float(self.upper_leg_force.max()),support_weight_fraction_max=float((self.support_force/self.weight).max()),rearward_progress_scale_m=.08,load_weight_fraction=.20,load_dwell_endpoints=3,per_wheel_transfer=True,rear_lift_product=False,rearward_target_absolute_body_x_m=None,last_sequential_gain_mean=float(self.last_transfer_gain.mean()),last_lift_regression_mean=float(self.last_regression.mean()),component_labels=['rearward_preparation','actual_load_transfer','post_mount_lift','post_clear_placement'],component_totals_before_outer06=self.component_totals.tolist(),last_component_mean_before_outer06=self.last_components.mean(0).tolist(),auxiliary_pose_count=17,old_reference_loss_enabled=False,phase_in_actor_observation=False)
  return result
