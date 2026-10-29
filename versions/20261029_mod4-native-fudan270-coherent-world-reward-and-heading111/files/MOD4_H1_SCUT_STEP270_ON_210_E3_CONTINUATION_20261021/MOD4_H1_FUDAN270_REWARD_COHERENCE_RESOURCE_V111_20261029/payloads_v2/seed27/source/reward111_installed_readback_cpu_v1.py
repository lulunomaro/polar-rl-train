"""Actual installed own FK/reward/input-normalizer readback for a NEW admission."""
import math,torch
from converted_MOD4_jump_mdp_v4 import ConvertedMOD4JumpMdp
from private_phase_frame_v1 import encode
from supermimic_wheel_leg_v3.geometry import axis_angle_to_mat
def check(mdp,pi,critic,bank_state):
 n=len(bank_state[0]);frame=encode(torch.full((n,),300,dtype=torch.long),torch.zeros(n,dtype=torch.long));zero=torch.zeros(n,6);xi=torch.zeros(n,31)
 states=[];rewards=[]
 for x in (.056,.20):
  root=bank_state[0].clone();root[:,0]=x;root[:,1]=0
  aux=bank_state[6].clone();aux[...,:18].reshape(n,3,2,3)[:,:,:,2]=100.
  s=(root,*bank_state[1:6],aux);out=mdp.objective_terms(s,frame,zero,zero)
  assert torch.isfinite(out['total']).all() and torch.all(out['contact_step_modes']['top_support']==0)
  states.append(s);rewards.append(out['total'])
 assert torch.all(rewards[1]>=rewards[0]-2e-7),'actual installed source own-bank floor approach adverse reward'
 s=states[0];R=axis_angle_to_mat(torch.tensor([[0.,0.,1.]]).expand(n,-1),torch.full((n,),math.pi))
 turned=(s[0],R,*s[2:]);obs=mdp.obs(s,zero,xi,frame);back=mdp.obs(turned,zero,xi,frame)
 old=ConvertedMOD4JumpMdp.obs(mdp,s,zero,xi,frame)
 assert torch.equal(obs[...,:3],old[...,:3]) and torch.equal(obs[...,4:],old[...,4:])
 norm=torch.cat((pi.obs_norm(obs),pi.obs_norm(back)),0)
 assert torch.isfinite(norm).all() and norm[:,3].abs().max()<=1.1,'inherited old zero-slot norm does not admit bounded heading signal'
 assert (obs[:,3]-back[:,3]).abs().min()>.009
 assert mdp.max_step_reward==.16
 return dict(passed=True,source_own_bank_poses=n,minimum_approach_reward_delta=float((rewards[1]-rewards[0]).min()),
  counterexample_scope='same recorded own FK bank pose and synthetic100N force history translated along supported floor; not a physics rollout',
  actual_inherited_heading_normalizer_mean=float(pi.obs_norm.mean[3]),actual_inherited_heading_normalizer_std=float(pi.obs_norm.std()[3]),
  actual_inherited_heading_normalizer_count=float(pi.obs_norm.count),maximum_heading_normalized_input=float(norm[:,3].abs().max()),
  fullgoal_and_other_obs_features_unchanged=True,strict_weights_norms_opts_already_restored=True,
  no_actor_WM_forward_or_norm_update=True,no_actual_GPU_or_skill_proof=True,
  actual_precontrol_term_cfg_tilt075_lowbase_minus1_readback_still_required=True)
