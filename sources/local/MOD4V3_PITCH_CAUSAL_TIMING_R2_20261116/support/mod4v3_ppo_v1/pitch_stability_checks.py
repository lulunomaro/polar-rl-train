"""Actual 2048-env full-DR endpoint/contact/substep audit, no optimizer."""
import time, types, torch
from tensordict import TensorDict
from .scut_flat_env import tensor
from .pitch_stability_math import body_pitch,transition_command

def run_probe(env,algorithm):
 env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy();start=time.time()
 pre=env._pre_physics_step;apply=env._apply_action;rewards=env._get_rewards
 state={'rates':[],'contact_seen':torch.zeros(env.num_envs,dtype=torch.bool,device=env.device),'sum':torch.zeros(15,device=env.device),'peak':torch.zeros(4,device=env.device),'commands_max_error':0.,'step_counts':set()}
 def contact():return (tensor(env.scene['contacts'].data.net_forces_w)[:,env.wheel_sensor_ids,2]>5.).any(1)
 def audited_pre(self,actions):
  state['rates']=[];state['contact_seen'][self.episode_length_buf==0]=False
  result=pre(actions);state['pre_command']=self.command[:,0].clone();return result
 def audited_apply(self):
  state['rates'].append(self.view.data.root_ang_vel_b[:,1].clone());return apply()
 def audited_rewards(self):
  out=rewards();rate=self.view.data.root_ang_vel_b[:,1];angles=body_pitch(self.view.data.projected_gravity_b);incontact=contact();state['contact_seen']|=incontact
  valid=self.pitch_target_mask&(~self.reset_terminated)&(self.episode_length_buf*self.step_dt>=1.)
  missing=valid&state['contact_seen']&(~incontact);ground=valid&incontact
  rates=torch.stack(state['rates']+[rate]);state['step_counts'].add(len(state['rates']));integral=(.5*rates[0].square()+rates[1:-1].square().sum(0)+.5*rates[-1].square())*self.physics_dt
  endpoint=rate.square()*self.step_dt;peak=rates.abs().amax(0);v=state['sum']
  v+=torch.stack((valid.sum(),ground.sum(),missing.sum(),endpoint[valid].sum(),endpoint[ground].sum(),endpoint[missing].sum(),integral[valid].sum(),peak[valid].square().sum()*self.step_dt,((peak>rate.abs()*1.25)&valid&(peak>1.)).sum(),self.last_pitch_reward[valid].sum(),out[valid].sum(),((rate.abs()>2.)&ground).sum(),((rate.abs()>2.)&missing).sum(),((rate.abs()>2.)&ground&(angles.abs()<torch.pi/36)).sum(),(endpoint[ground]*.35).sum()))
  for j,x in enumerate([rate.abs()[valid],peak[valid],angles.abs()[valid],(self.command[:,0]-state['pre_command']).abs()[valid]]):
   if x.numel():state['peak'][j]=torch.maximum(state['peak'][j],x.max())
  return out
 env._pre_physics_step=types.MethodType(audited_pre,env);env._apply_action=types.MethodType(audited_apply,env);env._get_rewards=types.MethodType(audited_rewards,env)
 for k in range(250):
  with torch.inference_mode():action=policy(obs,stochastic_output=False);raw,reward,term,timeout,_=env.step(action)
  if not bool(torch.isfinite(reward).all()):raise RuntimeError('Nonfinite probe reward')
  obs=TensorDict(raw,batch_size=[env.num_envs])
 labels=['target_samples','endpoint_grounded_samples','unloaded_after_contact_samples','endpoint_rate2_dt_all','endpoint_rate2_dt_grounded','endpoint_rate2_dt_missed_unloaded','substep_trapezoid_rate2_dt_all','substep_peak_rate2_dt_all','steps_substep_peak_over125pct_endpoint_and1rad_s','old_extra_reward_sum','total_reward_sum','grounded_fast_rate_samples_above2rad_s','unloaded_fast_rate_samples_above2rad_s','grounded_fast_rate_within5deg','old_rate_cost_sum']
 result=dict(no_optimizer_updates=True,steps=250,num_envs=env.num_envs,wall_seconds=time.time()-start,measurements=dict(zip(labels,state['sum'].tolist())),peaks=dict(zip(['endpoint_rad_s','substep_rad_s','pitch_rad','command_overwrite_m_s'],state['peak'].tolist())),actual_substeps_per_policy_step=sorted(state['step_counts']),done_totals=dict(env.done_totals),pitch=env.pitch_summary(),physics_dt_s=env.physics_dt,policy_dt_s=env.step_dt)
 assert env.enforce_closure_reset and env.cfg.decimation==8
 return result
