"""Video-matched tread support and rearward-upward wheel transfer, ascent only."""
from pathlib import Path
import json,types
import torch
from isaaclab.utils.math import quat_apply,quat_from_euler_xyz
from .scut_flat_env import tensor
from .rearward_progress import scores,credit

class RearwardSupport:
 def __init__(self,env):
  self.env=env;n=env.num_envs;dev=env.device
  self.assisted=torch.zeros(n,device=dev,dtype=torch.bool)
  self.mounted=self.assisted.clone();self.armed=self.assisted.clone();self.support_paid=self.assisted.clone()
  self.previous_stage=torch.full((n,),-9,device=dev,dtype=torch.long)
  self.reference=torch.zeros(n,2,device=dev);self.best=self.reference.clone()
  self.support_force=torch.zeros(n,device=dev);self.rear_delta=self.reference.clone();self.clearance=self.reference.clone();self.longitudinal=self.reference.clone()
  self.stats=torch.zeros(7,device=dev,dtype=torch.long);self.airborne_reward_exempt_endpoints=torch.zeros((),device=dev,dtype=torch.long)
  self.names=list(env.robot.body_names);self.guide=[i for i,x in enumerate(self.names) if 'guide' in x];self.base=int(env.full_dr.base_id)
  self.support_ids=self.guide+[self.base]
  self.sensor_ids=[env.scene['contacts'].body_names.index(x) for x in self.names]
  self.allowed=torch.zeros((n,len(self.names)),device=dev,dtype=torch.bool)
  bank=json.loads((Path(__file__).parent/'rearward_mount_bank.json').read_text());self.bank=bank['poses']
  self.bank_q=torch.tensor([[row['joint_positions'].get(name,0.) for name in env.robot.joint_names] for row in self.bank],device=dev)
  reward=env.reward;original_contact=reward._stair_contact_termination;original_post=reward._postprocess_reward_terms
  def contact(r,force):
   hit=force>1.;columns=r._reset_contact_link_idx
   allow=self.allowed[:,columns]|(r._stair_guide_columns[None,:]&r._stair_guide_allowed[:,None])
   r._stair_contact_raw=(hit&~allow).any(-1)
   r._stair_suppressed_guide_raw=(hit&allow).any(-1)
   return r._stair_contact_raw.clone()
  reward._stair_contact_termination=types.MethodType(contact,reward)
  def post(r,terms):
   supported=self.mounted&(self.support_force>5.)
   airborne=r.height_reward_airborne_state.clone()
   r.height_reward_airborne_state.copy_(airborne&~supported)
   try:values=original_post(terms)
   finally:r.height_reward_airborne_state.copy_(airborne)
   self.airborne_reward_exempt_endpoints+=(supported&airborne).sum()
   for name in list(values):
    if name.startswith('track_height_'):values[name]=torch.where(self.mounted&(self.support_force>5.),torch.zeros_like(values[name]),values[name])
   if 'undesired_contact' in values:
    forces=r.contact_sensor.data.net_forces_w;ids=[i for i in r._undesired_contact_link_idx if i not in r._reset_contact_link_idx]
    bad=(forces[:,ids].norm(dim=-1)>1.)&~self.allowed[:,ids]
    values['undesired_contact']=bad.any(-1).float()
   return values
  reward._postprocess_reward_terms=types.MethodType(post,reward)

 def reset(self,picked):
  e=self.env
  for x in [self.assisted,self.mounted,self.armed,self.support_paid]:x[picked]=False
  self.previous_stage[picked]=-9;self.best[picked]=0.;self.reference[picked]=0.;self.allowed[picked]=False
  up=picked[e.stair_up[picked]]
  if not len(up):return
  gen=e.reset_generator;e.stair_speed[up]=torch.empty(len(up),device=e.device).uniform_(.35,.75,generator=gen)
  assist=up[torch.rand(len(up),device=e.device,generator=gen)<.30]
  if not len(assist):return
  row=torch.randint(len(self.bank),(len(assist),),device=e.device,generator=gen);stage=e.stair_stage[assist];side=e.stair_side[assist];center=e._center()[assist]
  edge=torch.where(stage==0,2.9,1.4);height=(stage+1)*.2
  inward=torch.tensor([x['root_inward_of_edge_m'] for x in self.bank],device=e.device)[row]
  root=tensor(e.robot.data.default_root_state)[assist].clone();root[:,:3]=center;root[:,0]+=side*(edge-inward);root[:,2]=height+.1785
  yaw=torch.where(side<0,0.,torch.pi);root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw);root[:,7:]=0.
  q=self.bank_q[row];e.robot.write_root_state_to_sim(root,env_ids=assist);e.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=assist)
  self.stats[6]+=(row>=3).sum();self.assisted[assist]=True;e.stair_initial_stage[assist]=-1;e.stair_mid[assist]=True;e.stair_approach_yaw[assist]=0.;e.stair_approach_group[assist]=0
  e.stair_start[assist]=edge-inward;e.episode_length_buf[assist]=150;e.height[assist]=.42
  e.reward.ground_z_est[assist]=stage*.2;e.reward._invalidate_step_caches();self.stats[0]+=len(assist)

 def endpoint(self):
  e=self.env;root=e.view.data.root_pos_w;body=e.view.data.body_pos_w;center=e._center();stage=e.stair_stage.clamp_max(1)
  changed=self.previous_stage!=stage
  for x in [self.mounted,self.armed,self.support_paid]:x[changed]=False
  self.best[changed]=0.;self.previous_stage.copy_(stage)
  forces=tensor(e.scene['contacts'].data.net_forces_w)[:,self.sensor_ids];ids=self.support_ids;pos=body[:,ids].clone();pos[:,-1,2]-=.17;force=forces[:,ids]
  x=(pos[:,:,0]-center[:,None,0])*e.stair_side[:,None];y=(pos[:,:,1]-center[:,None,1]).abs()
  # Only upward-loaded body/guide contacts geometrically on either upper tread qualify.
  first=(x<2.92)&(x>1.39)&(y<2.90)&((pos[:,:,2]-(.2)).abs()<.065)
  second=(x<1.42)&(x>-1.42)&(y<1.42)&((pos[:,:,2]-(.4)).abs()<.065)
  vertical=force[:,:,2]>5.;upaxis=torch.zeros(e.num_envs,3,device=e.device);upaxis[:,2]=1.;upright=quat_apply(e.view.data.root_quat_w[:,[1,2,3,0]],upaxis)[:,2]>.8
  selected=e.continuous_stair_mask&e.stair_up&upright
  valid=(first|second)&vertical&selected[:,None];self.allowed.zero_();self.allowed[:,ids]=valid
  target=torch.where((stage==0)[:,None],first,second)&vertical&selected[:,None]
  self.support_force=(force[:,:,2].clamp_min(0)*target).sum(1)
  edge=torch.where(stage==0,2.9,1.4);rootx=(root[:,0]-center[:,0])*e.stair_side
  eligible=selected&(rootx<edge-.015)&(self.support_force>5.)&(e.stair_stage<2)
  new=eligible&~self.mounted;self.mounted|=eligible;self.stats[1]+=new.sum()
  axis=torch.zeros(e.num_envs,3,device=e.device);axis[:,0]=1.;forward=quat_apply(e.view.data.root_quat_w[:,[1,2,3,0]],axis)
  wheels=body[:,e.stair_wheel_idx];longitudinal=((wheels-root[:,None,:])*forward[:,None,:]).sum(-1)
  near=((wheels[:,:,0]-center[:,None,0])*e.stair_side[:,None]-edge[:,None]).abs().amin(1)<.45
  arm=selected&near&~self.armed;self.reference[arm]=longitudinal[arm];self.armed|=arm
  self.longitudinal=longitudinal;self.rear_delta=self.reference-longitudinal
  self.clearance=wheels[:,:,2]-.0625-((stage[:,None]+1)*.2)
  # Landing ends the temporary height exemption; ascent then recovers commanded stance.
  wheelx=(wheels[:,:,0]-center[:,None,0])*e.stair_side[:,None]
  top=(wheelx<edge[:,None]-.02)&(self.clearance.abs()<.05)&(forces[:,e.stair_wheel_idx,2]>5.)
  landed=top.all(1);self.mounted&=~landed
  self.stats[2]+=(selected&(longitudinal<-.12).all(1)&(self.clearance>.005).all(1)).sum()
  # Existing progress in a reset or first mount is the baseline, not earned movement.
  baseline=scores(self.longitudinal,self.clearance);self.best[new]=baseline[new]

 def gain(self,active):
  e=self.env
  supported=self.mounted&active&self.armed&(self.support_force>5.)
  current=scores(self.longitudinal,self.clearance)
  gain,self.best=credit(current,self.best,supported)
  first=supported&~self.support_paid;self.support_paid|=first
  self.stats[3]+=first.sum();self.stats[4]+=(gain[:,0]>0).sum();self.stats[5]+=(gain[:,1]>0).sum()
  # Original outer0.6 multiplier retained: at most0.12 support+0.24 rear+0.24 rise per stage.
  return .2*first.float()+.4*gain.sum(1)

 def summary(self):
  return dict(supported_airborne_reward_exempt_endpoints=int(self.airborne_reward_exempt_endpoints),airborne_scope='Only reward application during actual ascending tread-supported mount; state, guards,retained rough/flat/true air unchanged',strategy='tread-supported rearward-upward wheel transfer then genuine landing and re-standing',stats=self.stats.tolist(),columns=['assisted_resets','mount_events','rear_clear_endpoints','support_credits','rearward_gain_endpoints','rise_gain_endpoints','late_assisted_resets'],assisted_now=int(self.assisted.sum()),mounted_now=int(self.mounted.sum()),body_support_force_mean_N=float(self.support_force.mean()),rearward_delta_mean_m=self.rear_delta.mean(0).tolist(),wheel_clearance_mean_m=self.clearance.mean(0).tolist(),phase_observation_added=False,old_specialist_BC_enabled=False,rearward_target_absolute_body_x_m=-.24,reward='independent best-so-far rearward and upward gains; no product dead zone')
