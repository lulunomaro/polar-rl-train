"""UNEXECUTED review candidate: one fresh single-env native-policy attempt.

Root must supply a fresh, admitted original SDK env via build_env, the exact
native H1 current-state reader and PartialFudan MDP. This is not a standalone
admitted launcher. No checkpoint is opened by this module. Never call training
main/learn/collect or the training control-prefix trace to use it.
"""
from pathlib import Path
from copy import deepcopy
import json,math,time,traceback


def make_frozen_native_policy(checkpoint,policy_class,device):
 """Root supplies the qualified formal native checkpoint object exactly once."""
 import torch
 native=checkpoint['UniSuperMimic_H1_test'];contract=checkpoint['UniSuperMimic_test_contract'];cfg=native['args']
 assert contract['state_joints']==30 and contract['actions']==6 and contract['obs_dim']==128 and contract['goal_dim']==73
 assert cfg['hist']==10 and cfg['goal_frames']==1 and cfg['test_hidden_dims'] is None and cfg['amp']=='none'
 # Construct on CPU under a private scope, then strict-load the saved native Pi
 # and its RunningNorm buffers. No PPO actor is a policy source here.
 with torch.random.fork_rng(devices=[]):
  pi=policy_class(128,73,hist=10,z_dim=cfg['z_dim'],num_joints=6,hidden=cfg['policy_hidden'])
 pi.load_state_dict(native['pi'],strict=True);pi.to(device);pi.eval()
 for parameter in pi.parameters():parameter.requires_grad_(False)
 return pi


def _json_value(value):
 import torch
 if torch.is_tensor(value):return value.detach().cpu().tolist()
 if isinstance(value,dict):return {k:_json_value(v) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [_json_value(v) for v in value]
 return value


class SelectedActualFrames:
 """Read-only hooks, no preupdate save, retention or training reward flag."""
 def __init__(self,env,stream,tensor_reader):
  self.env=env;self.stream=stream;self.tensor=tensor_reader;self.physics_rows=0;self.control=0
  self.recording=False;self.last=None;self.before_update=None;self.before_term=None
 def _state(self):
  e=self.env;r=e.scene['robot'];p=e.h1_phase;t=self.tensor
  assert len(r.body_names)==31
  forces=t(e.h1_sensor.contact_view.get_net_contact_forces(dt=float(e.physics_dt))).reshape(1,31,3)
  return dict(root13_sdk_xyzw=t(r.data.root_state_w)[0].clone(),q30=t(r.data.joint_pos)[0].clone(),
   joint_velocity30=t(r.data.joint_vel)[0].clone(),body_position31_world=t(r.data.body_pos_w)[0].clone(),
   body_quaternion31_sdk_xyzw=t(r.data.body_quat_w)[0].clone(),body_contact_force31=forces[0].clone(),
   executed6=e.action_manager.action[0].clone(),public_age=int(p.age_control[0]),
   public_request=bool(p.request_for_action[0]),takeoff_count=int(p.takeoff_count[0]),
   landing_count=int(p.landing_count[0]),recovery_count=int(p.recovery_count[0]),
   crossed2=p.crossed[0].clone(),success=bool(p.goal.success[0]),
   stable_callback_ticks=int(p.goal.stable_ticks[0]),episode=int(e._sensor_mild.episode[0]))
 def install(self):
  e=self.env;self.before_update=e.scene.update;self.before_term=e.termination_manager.compute
  def update(dt):
   result=self.before_update(dt)
   if self.recording:
    self.physics_rows+=1;row=self._state()
    self.stream.write(json.dumps(_json_value(dict(kind='actual_physics_frame',physics_row=self.physics_rows,
     control=self.control,sim_time_s=self.physics_rows*float(e.physics_dt),state=row)),allow_nan=False)+'\n')
   return result
  def term(*args,**kwargs):
   try:
    result=self.before_term(*args,**kwargs)
    # Original term includes end-of-control age advance. Capture before SDK
    # selected reset; stop callback capture before any reset readback/update.
    self.last=self._state();return result
   finally:self.recording=False
  e.scene.update=update;e.termination_manager.compute=term
 def restore(self):
  self.recording=False
  self.env.scene.update=self.before_update;self.env.termination_manager.compute=self.before_term


def run_frozen_single_attempt(vec,mdp,pi,current_state,unflatten_state,tensor_reader,output_dir,*,
 source_identity,actual_joint_order,learned_joint_order,runtime_objective_SHA,expected_runtime_objective_SHA,
 action_mode,seed=20261026,max_seconds=10.0):
 """Fresh N1 SDK only. current_state reuses original H1Bridge.current/pack.

Stops at the first actual done, original success, or10-second cap. A cap is
labelled censored, never called complete success. There is no retry/selection.
"""
 import torch
 e=vec.unwrapped;out=Path(output_dir);assert not out.exists();out.mkdir(parents=True)
 assert e.num_envs==1,'Small-N SDK/config/reset must be explicitly admitted; do not reshape20k DR state'
 assert float(e.physics_dt)==.0025 and float(e.step_dt)==.01 and e.cfg.decimation==4
 assert e.h1_phase.state_dict()['geometry']==dict(height=.270,edge_x=.35,depth=.8,width=1.2)
 assert actual_joint_order==learned_joint_order and len(set(actual_joint_order))==30
 assert runtime_objective_SHA==expected_runtime_objective_SHA,'Native PartialFudan wrapper/config differs'
 assert action_mode in ('deterministic_native_mean','fixed_seed_original_collection_noise')
 assert 0<max_seconds<=10.0 and not e.h1_capture
 assert not e.h1_phase.age_control.any() and not e.h1_phase.goal.success.any(),'Start one original fresh episode; no manual age reset'
 device=e.device;N=1;steps=math.ceil(max_seconds/float(e.step_dt));previous=torch.zeros((N,6),device=device)
 episode_steps=torch.zeros(N,device=device,dtype=torch.int32);history=torch.zeros((N,10,128),device=device)
 before={k:v.detach().cpu().clone() for k,v in pi.state_dict().items()}
 pi.eval();noise=torch.Generator(device=device);noise.manual_seed(seed)
 status=dict(source_identity=source_identity,action_mode=action_mode,seed=seed,
  fresh_episode=True,source20k_physical_state_not_reshaped_or_restored=True,
  saved_native_normalizers_frozen=True,no_training_or_WM=True,exact_training_trajectory_replay=False,
  native_obs128_history10_goal73_actions6=True,physics_dt=.0025,control_dt=.01,
  actual_joint_order=actual_joint_order,body_names=list(e.scene['robot'].body_names),
  environment_origin_m=e.scene.env_origins[0].detach().cpu().tolist(),
  max_seconds=max_seconds,termination=None,controls=0,physics_frames=0)
 frames=out/'ACTUAL_SINGLE_ATTEMPT_FRAMES.jsonl';controls=out/'ACTUAL_SINGLE_ATTEMPT_CONTROLS.jsonl'
 with frames.open('x',encoding='utf8') as frame_stream,controls.open('x',encoding='utf8') as control_stream:
  capture=SelectedActualFrames(e,frame_stream,tensor_reader);capture.install()
  try:
   with torch.inference_mode():
    for control in range(steps):
     state,context=current_state();age=e.h1_phase.age_control.clone()
     obs=mdp.add_noise(mdp.obs(unflatten_state(state),previous,context,age))
     assert obs.shape==(1,128) and context.shape==(1,49)
     shifted=torch.cat((history[:,1:],obs.unsqueeze(1)),1)
     history=torch.where((episode_steps==0)[:,None,None],obs[:,None].expand_as(history),shifted)
     goal=mdp.goal(age,1);assert goal.shape==(1,73)
     policy_output=pi(history,goal);assert policy_output.shape==(1,6) and torch.isfinite(policy_output).all()
     raw=policy_output
     if action_mode=='fixed_seed_original_collection_noise':raw=raw+.1*torch.randn(raw.shape,generator=noise,device=device,dtype=raw.dtype)
     raw=raw.clamp(-20,20) # Original native collect bound; SDK clip6 stays in vec.
     capture.control=control+1;capture.last=None;capture.recording=True;before_tick=capture.physics_rows
     result=vec.step(raw);capture.recording=False
     observations,reward,done,extras=result
     assert capture.last is not None and capture.physics_rows-before_tick==4,'Actual original4-callback control required'
     last=capture.last
     control_stream.write(json.dumps(_json_value(dict(control=control+1,sim_time_s=(control+1)*.01,
      policy_output6=policy_output[0],raw_native_command6=raw[0],actual_pre_reset=last,
      done=bool(done[0]),physical_reward=reward[0])),allow_nan=False)+'\n')
     previous=last['executed6'][None].clone();episode_steps+=1
     status['controls']=control+1;status['physics_frames']=capture.physics_rows
     status['original_success']=last['success'];status['final_original_stable_callback_ticks']=last['stable_callback_ticks']
     status['final_original_event_counts']={k:last[k] for k in ('takeoff_count','landing_count','recovery_count')}
     if bool(done[0]):status['termination']='actual_original_done';break
     if last['success']:status['termination']='original_success_with_callback_ticks';break
    else:status['termination']='ten_second_cap_censored_not_complete_success'
  except BaseException:
   status['termination']='original_error_partial_attempt';status['original_error']=traceback.format_exc();raise
  finally:
   capture.restore();frame_stream.flush();control_stream.flush()
   status['Pi_parameters_and_normalizers_literal_unchanged']=all(torch.equal(v.detach().cpu(),before[k]) for k,v in pi.state_dict().items())
   status['recorded_at_epoch']=time.time()
   with (out/'FROZEN_SINGLE_ATTEMPT_STATUS.json').open('x',encoding='utf8') as stream:json.dump(status,stream,indent=2,allow_nan=False)
   assert status['Pi_parameters_and_normalizers_literal_unchanged'],'Frozen policy state mutated'
 return status
