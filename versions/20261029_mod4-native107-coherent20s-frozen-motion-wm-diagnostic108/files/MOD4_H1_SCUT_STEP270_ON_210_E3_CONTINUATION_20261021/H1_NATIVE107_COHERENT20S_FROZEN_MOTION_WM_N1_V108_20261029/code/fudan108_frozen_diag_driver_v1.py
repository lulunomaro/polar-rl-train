"""Frozen native127/obs86/future10 driver. No checkpoint I/O or learning here."""
from pathlib import Path
import ast,hashlib,json,time,traceback
from fudan108_eval_contract_v1 import SEEDS,require

def literal(a,b):
 import torch
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(literal(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a) is type(b) and len(a)==len(b) and all(literal(x,y) for x,y in zip(a,b))
 return type(a) is type(b) and a==b
def make_frozen_policy(checkpoint,policy_class,device,*,expected_native_contract):
 import torch
 require(expected_native_contract['changed_plant700_to_nominal400'] is False and expected_native_contract['native_objective_changed'] is True and expected_native_contract['nominal_gas_stiffness_N_m']==2000.,'native88C/400N output recipe required')
 native=checkpoint['UniSuperMimic_H1_test'];cfg=native['args']
 require(literal(checkpoint['UniSuperMimic_test_contract'],expected_native_contract),'exact new native127 contract required; legacy native86 forbidden')
 require(cfg['hist']==10 and cfg['goal_frames']==10 and cfg['z_dim']==32 and cfg['amp']=='none' and cfg['test_hidden_dims'] is None,'saved policy architecture differs')
 require(tuple(cfg['policy_hidden'])==(2048,1024,512,256),'saved native policy hidden layout differs')
 require(checkpoint['UniSuperMimic_publication']['policy_updates']>0,'formal trained native Pi required')
 saved=native['pi']
 for k,v in saved.items():require(torch.is_tensor(v) and bool(torch.isfinite(v).all()),'nonfinite/missing saved Pi tensor '+k)
 for prefix,dim in [('obs_norm',86),('goal_norm',1460)]:
  require(saved[prefix+'.mean'].shape==saved[prefix+'.var'].shape==(dim,) and saved[prefix+'.count'].numel()==1,'saved normalizer layout differs')
 with torch.random.fork_rng(devices=[]):pi=policy_class(86,1460,hist=10,z_dim=32,num_joints=6,hidden=cfg['policy_hidden'])
 pi.load_state_dict(saved,strict=True)
 require(literal(pi.state_dict(),saved),'policy load cast or altered saved tensor/normalizer')
 pi.to(device);pi.eval()
 for parameter in pi.parameters():parameter.requires_grad_(False)
 return pi
def fresh_history(history,obs,episode_steps):
 import torch
 require(history.shape==(1,10,86) and obs.shape==(1,86),'fresh native observation history layout')
 shifted=torch.cat((history[:,1:],obs.unsqueeze(1)),1)
 return torch.where((episode_steps==0)[:,None,None],obs[:,None].expand_as(history),shifted)
def json_value(x):
 import torch
 if torch.is_tensor(x):return x.detach().cpu().tolist()
 if isinstance(x,dict):return {k:json_value(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [json_value(v) for v in x]
 return x

def termination_cache_contract(source_path):
 """Exact API obtained for this new N1 purpose; never call compute again."""
 raw=Path(source_path).read_bytes();t=ast.parse(raw);result=dict(source_path=str(source_path),source_SHA=hashlib.sha256(raw).hexdigest(),available=False)
 require(result['source_SHA']=='cb6333f11fa6472f7d8034bae9835714e83ae3edde97894b767f1351a7eea99d','actual SDK TerminationManager source differs')
 classes=[n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='TerminationManager']
 require(len(classes)==1,'actual TerminationManager class unavailable')
 def returns(name):
  f=next(x for x in classes[0].body if isinstance(x,ast.FunctionDef) and x.name==name)
  return [x.value for x in f.body if isinstance(x,ast.Return)]
 require([ast.dump(x) for x in returns('active_terms')]==[ast.dump(ast.parse('self._term_names',mode='eval').body)],'actual active_terms API changed')
 require([ast.dump(x) for x in returns('get_term')]==[ast.dump(ast.parse('self._term_dones[:, self._term_name_to_term_idx[name]]',mode='eval').body)],'actual cached get_term API changed')
 return dict(result,available=True,names_attribute='_term_names',values_attribute='_term_dones',actual_get_term_cached_no_recompute=True)

class ActualFrames:
 def __init__(self,env,stream,tensor,term_contract):
  self.env=env;self.stream=stream;self.tensor=tensor;self.term_contract=term_contract
  self.recording=False;self.count=0;self.control=0;self.last=None
 def terms(self):
  c=self.term_contract
  if not c['available']:return dict(exact_terms_available=False,source_contract=c)
  manager=self.env.termination_manager;names=getattr(manager,c['names_attribute']);values=self.tensor(getattr(manager,c['values_attribute']))
  import torch
  require(isinstance(names,list) and values.shape==(1,len(names)) and values.dtype==torch.bool,'actual cached termination shape/dtype differs')
  return dict(exact_terms_available=True,values={name:bool(values[0,i]) for i,name in enumerate(names)},source_contract=c)
 def state(self):
  e=self.env;r=e.scene['robot'];p=e.h1_phase;t=self.tensor
  forces=__import__('h1_fullstate_environment_v1').tensor(e.h1_sensor.contact_view.get_net_contact_forces(dt=float(e.physics_dt))).reshape(1,31,3)
  force_order=[e.h1_contact_names.index(name) for name in r.body_names]
  caches={k:v[0].clone() for k,v in p.last_measured.items() if k in ('step_wheel_min','step_wheel_max','step_query_height','step_query_face','step_platform_contact','step_footprint_inside','step_first_cross_clear','step_stable_ticks','step_goal_success')}
  root=t(r.data.root_state_w)[0];gravity=t(r.data.projected_gravity_b)[0].clone();metrics=dict(root_vx_world=root[7].clone(),tilt_rad=__import__('torch').acos((-gravity[2]).clamp(-1,1)),wheel_cache_available='step_wheel_min' in caches)
  if 'step_wheel_min' in caches:
   lo,hi=caches['step_wheel_min'],caches['step_wheel_max'];origin=e.scene.env_origins[0];edge=origin[0]+.35
   metrics.update(wheel_bottom_above_floor_m=lo[:,2]-origin[2],wheel_front_edge_gap_m=edge-hi[:,0],wheel_rear_edge_gap_m=edge-lo[:,0],wheel_bottom_minus_platform_m=lo[:,2]-(origin[2]+.27))
  return dict(metrics=metrics,projected_gravity_b=gravity,root13_sdk_xyzw=t(r.data.root_state_w)[0].clone(),q30=t(r.data.joint_pos)[0].clone(),qd30=t(r.data.joint_vel)[0].clone(),
   applied_torque30=t(r.data.applied_torque)[0].clone(),body_position31_world=t(r.data.body_pos_w)[0].clone(),body_quaternion31_sdk_xyzw=t(r.data.body_quat_w)[0].clone(),
   body_contact_force31=forces[0,force_order].clone(),contact_history18=e._integrated_contact.history[0].clone(),
   executed6=e.action_manager.action[0].clone(),physical_applied_processed6=__import__('torch').cat([t(e._physics_action_delay.queue.groups[k]['applied']) for k in ('legs','wheels')],-1)[0].clone(),
   public_age=int(p.age_control[0]),public_request=bool(p.request_for_action[0]),
   takeoff_count=int(p.takeoff_count[0]),landing_count=int(p.landing_count[0]),recovery_count=int(p.recovery_count[0]),
   crossed2=p.crossed[0].clone(),success=bool(p.goal.success[0]),stable_callback_ticks=int(p.goal.stable_ticks[0]),episode=int(e._sensor_mild.episode[0]),
   actual_original_success_caches=caches)
 def install(self):
  e=self.env;self.old_update=e.scene.update;self.old_term=e.termination_manager.compute
  def update(dt):
   result=self.old_update(dt)
   if self.recording:
    self.count+=1;require(self.count<=8000,'fixed coherent20s/8000 callback cap exceeded')
    self.stream.write(json.dumps(json_value(dict(kind='actual_physics_frame',physics_callback=self.count,control=self.control,sim_time_s=self.count*.0025,state=self.state())),allow_nan=False)+'\n')
   return result
  def term(*a,**kw):
   try:
    result=self.old_term(*a,**kw)
    self.last=dict(state=self.state(),original_aggregate_done=self.tensor(result).clone(),termination_terms=self.terms())
    return result
   finally:self.recording=False
  e.scene.update=update;e.termination_manager.compute=term
 def restore(self):
  self.recording=False;self.env.scene.update=self.old_update;self.env.termination_manager.compute=self.old_term

def run_single_case(vec,bridge,pi,unflatten_state,tensor,out,*,seed,source_identity,term_contract,authority_check,wm,critic,model_args,original_counter):
 import torch
 require(seed in SEEDS,'only fixed single seed20260928')
 e=vec.unwrapped;out=Path(out);require(not out.exists(),'consumed episode namespace cannot retry');out.mkdir()
 require(e.num_envs==1 and e.physics_dt==.0025 and e.step_dt==.01 and e.cfg.decimation==4 and e.cfg.episode_length_s==20.,'actual fresh N1 original clock/20s required')
 require(not e.h1_capture and not bool(e.h1_phase.age_control.any()) and not bool(e.h1_phase.goal.success.any()),'fresh original episode/no credit required')
 before={k:v.detach().cpu().clone() for k,v in pi.state_dict().items()}
 critic_before={k:v.detach().cpu().clone() for k,v in critic.state_dict().items()}
 wm_before={k:v.detach().cpu().clone() for k,v in wm.state_dict().items()};paired=[];phase_records=[]
 history=torch.zeros(1,10,86,device=e.device);previous=torch.zeros(1,6,device=e.device);ep_step=torch.zeros(1,dtype=torch.int32,device=e.device)
 status=dict(seed=seed,source_identity=source_identity,action_mode='deterministic_native_mean_no_collection_noise',native127_obs86_goal146x10=True,
  controls=0,physics_callbacks=0,termination=None,no_learning_no_learner_no_optimizer=True,frozen_WM_prediction_diagnostic=True,actual_Fudan270_target=True,
  exact_training_trajectory_replay=False,no_retry_or_seed_selection=True,body_names=list(e.scene['robot'].body_names))
 with (out/'ACTUAL_400HZ_31BODY_FRAMES.jsonl').open('x',encoding='utf8') as fs,(out/'ACTUAL_100HZ_CONTROLS.jsonl').open('x',encoding='utf8') as cs:
  capture=ActualFrames(e,fs,tensor,term_contract);capture.install()
  try:
   with torch.inference_mode():
    initial=capture.state();fs.write(json.dumps(json_value(dict(kind='initial_fresh_episode',physics_callback=0,state=initial)),allow_nan=False)+'\n')
    for control in range(2000):
     authority_check();s,xi=bridge.current();age=e.h1_phase.age_control.clone()
     from private_phase_frame_v1 import encode as encode_frame
     frames=encode_frame(age,torch.zeros_like(age))
     require(s.shape==(1,127) and xi.shape==(1,31),'actual native state/static dimensions')
     obs=bridge.mdp.add_noise(bridge.mdp.obs(unflatten_state(s),previous,xi,frames));history=fresh_history(history,obs,ep_step)
     goal=bridge.mdp.goal(frames,10);require(goal.shape==(1,1460),'actual native future10 goal dimension')
     mean=pi(history,goal);require(mean.shape==(1,6) and bool(torch.isfinite(mean).all()),'finite native mean action6 required')
     raw=mean.clamp(-20,20);capture.control=control+1;capture.last=None;capture.recording=True;last_count=capture.count
     observations,reward,done,extras=vec.step(raw);capture.recording=False
     require(capture.last is not None and capture.count-last_count==4,'original4 callback complete control required')
     terminal=capture.last;last=terminal['state']
     from static_dynamic_delay_contract_v1 import pack_dynamic_aux
     aux=pack_dynamic_aux(last['contact_history18'][None],last['applied_torque30'][None],last['physical_applied_processed6'][None])
     s1=bridge.pack(last['root13_sdk_xyzw'][None],last['q30'][None],last['qd30'][None],aux)
     objective=bridge.mdp.objective_terms(unflatten_state(s1),frames+1,last['executed6'][None],previous)
     require(nested_finite(objective),'finite nested Fudan reward and metadata required')
     predicted=wm.step(unflatten_state(s),last['executed6'][None],bridge.mdp.normalize_context(xi))
     predicted_geometry=bridge.mdp.wheel_geometry(predicted);actual_geometry=bridge.mdp.wheel_geometry(unflatten_state(s1))
     wm_error=dict(predicted_root_z=predicted[0][0,2],actual_root_z=s1[0,2],predicted_wheel_bottom=predicted_geometry['low'][0,:,2],actual_wheel_bottom=actual_geometry['low'][0,:,2],predicted_Rzz=predicted[1][0,2,2],actual_Rzz=unflatten_state(s1)[1][0,2,2])
     paired.append((s.clone(),xi.clone(),last['executed6'][None].clone(),s1.clone(),frames.clone(),history.clone(),previous.clone()))
     phase_records.append(actual_phase_record(last,actual_geometry,age,control+1,list(e.scene['robot'].body_names)))
     original_counter.record(last)
     value,known=bridge.mdp.provider.query(frames)
     from flat91_mask_aware_goal_conditioning_v1 import masked_goal_conditioning
     conditioned=masked_goal_conditioning(pi.goal_norm(goal),goal)
     p0,R0,_,_,_,_,aux0=unflatten_state(s1)
     sagittal=(R0.transpose(-1,-2).unsqueeze(-3)@(actual_geometry['centre']-p0.unsqueeze(-2)).unsqueeze(-1)).squeeze(-1)-bridge.mdp.hip_anchors
     diagnostics=dict(goal_value73=value[0],goal_mask73=known[0],actor_conditioned1460=conditioned[0],virtual_leg_length2=sagittal[...,[0,2]].norm(dim=-1)[0],virtual_leg_angle2=torch.atan2(sagittal[...,0],-sagittal[...,2])[0],actual_contact_force_z2=torch.maximum(aux0[...,:18].reshape(1,3,2,3)[:,0,:,2],aux0[...,:18].reshape(1,3,2,3)[:,1,:,2])[0],fudan_contact_step_modes=objective['contact_step_modes'],raw_original_command3=e.command_manager.get_term('twist').command[0].clone())
     cs.write(json.dumps(json_value(dict(control=control+1,age_for_action=age,packed127_for_action=s[0],xi31_for_action=xi[0],mean6=mean[0],raw_native_clamp20_6=raw[0],
      task_relative_features7_for_action=bridge.mdp.relative_features(unflatten_state(s),frames)[0],actor_obs86_for_action=obs[0],packed_frame_for_action=frames[0],env_origin3_world=e.scene.env_origins[0].clone(),physics_dt_s=.0025,control_dt_s=.01,actual_phase_record=phase_records[-1],terminal_pre_reset=terminal,terminal_packed127_same_point=s1[0],actual_Fudan270_objective=objective,own_actual_goal_contact_geometry=diagnostics,frozen_WM_one_step=wm_error,actual_original_done=bool(done[0]),physical_V8_reward=reward[0])),allow_nan=False)+'\n')
     previous=last['executed6'][None].clone();ep_step+=1
     status.update(controls=control+1,physics_callbacks=capture.count,last_original_state=json_value(last),last_termination_terms=terminal['termination_terms'])
     if bool(done[0]):status['termination']='actual_original_done';break
    else:status['termination']='fixed20s_cap_censored_if_original_done_absent'
  except BaseException:
   status.update(termination='original_error_partial_single_attempt',original_error=traceback.format_exc());raise
  finally:
   capture.restore();fs.flush();cs.flush()
   status['policy_parameters_and_saved_normalizers_literal_unchanged']=literal(pi.state_dict(),before)
   status['WM_parameters_and_saved_normalizers_literal_unchanged']=literal(wm.state_dict(),wm_before)
   status['original270_terminal_physics_events']=original_counter.snapshot()
   status['not_retarget_animation_or_frozen_skill_graduation']=True
   with (out/'FROZEN_SINGLE_CASE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(status,f,indent=2,allow_nan=False)
   require(status['policy_parameters_and_saved_normalizers_literal_unchanged'],'frozen policy/normalizers changed')
 from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack
 validate_actual_action_windows(paired,phase_records,bridge,wm,out)
 sensitivity=frozen_first_action_sensitivity(paired,bridge,pi,wm,critic,model_args)
 with (out/'FROZEN_FUDAN270_32STEP_FIRST_ACTION_SENSITIVITY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(rows=sensitivity,only_frozen_first_action_derivative=True,all_physical_controls_finished_before_imagination=True,no_policy_or_optimizer_step=True,noise_draws_in_imagination_not_same_training_RNG_replay=True,not_causal_or_mechanical_proof=True),f,indent=2,allow_nan=False)
 require(literal(pi.state_dict(),before) and literal(wm.state_dict(),wm_before) and literal(critic.state_dict(),critic_before),'frozen model or normalizers changed')
 return status

def nested_finite(value):
 import torch,math
 if torch.is_tensor(value):return bool(torch.isfinite(value).all())
 if isinstance(value,dict):return all(nested_finite(x) for x in value.values())
 if isinstance(value,(tuple,list)):return all(nested_finite(x) for x in value)
 if isinstance(value,float):return math.isfinite(value)
 return value is None or isinstance(value,(str,int,bool))

def frozen_first_action_sensitivity(paired,bridge,pi,wm,critic,model_args):
 """Frozen original32-step equations; derivative wrt first imagined action only.

 No policy-parameter gradient, optimizer, physical counterfactual or skill claim.
 """
 import torch
 from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack
 sensitivity=[]
 for start in (0,160,192,200,240,512,1000,1280,1600,1900):
  if start>=len(paired):continue
  row=paired[start]
  with torch.inference_mode(False),torch.enable_grad():
   state=unpack(row[0].detach().clone());context=row[1].detach().clone();frames=row[4].detach().clone();hist=row[5].detach().clone();previous=row[6].detach().clone();normal=bridge.mdp.normalize_context(context)
   action0=pi(hist,bridge.mdp.goal(frames,10)).clamp(-6,6).detach().requires_grad_(True)
   reward_objective=action0.sum()*0;survival=action0.new_ones((1,));gamma=float(model_args['gamma']);rows=[]
   for h in range(32):
    action=action0 if h==0 else pi(hist,bridge.mdp.goal(frames,10)).clamp(-6,6)
    state=wm.step(state,action,normal);frames=frames+1
    terms=bridge.mdp.objective_terms(state,frames,action,previous);reward=terms['total'];done=bridge.mdp.soft_termination(state,frames)
    reward_objective=reward_objective+(gamma**h)*survival*reward;survival=survival*(1-done)
    geometry=bridge.mdp.wheel_geometry(state)
    rows.append(dict(offset=h+1,frame=json_value(frames),root_xyz=json_value(state[0]),wheel_bottom2=json_value(geometry['low'][...,2]),reward=json_value(reward),soft_done=json_value(done),contact_step_modes=json_value(terms['contact_step_modes'])))
    obs=bridge.mdp.add_noise(bridge.mdp.obs(state,action,context,frames));hist=torch.cat((hist[:,1:],obs.unsqueeze(1)),1);previous=action
   tail=action0.sum()*0
   if not model_args['no_critic']:
    goal=bridge.mdp.goal(frames,10);features=bridge.mdp.critic_features(state,frames,normal);tail=(gamma**32)*survival*critic(torch.cat((features,goal),-1))
   gr=torch.autograd.grad(reward_objective.sum(),action0,retain_graph=True)[0]
   gt=torch.autograd.grad(tail.sum(),action0)[0]
   sensitivity.append(dict(start_control=start+1,initial_frame=json_value(row[4]),reward_objective=json_value(reward_objective),critic_tail=json_value(tail),first_action_reward_gradient6=json_value(gr),first_action_critic_tail_gradient6=json_value(gt),all_values_finite=bool(torch.isfinite(gr).all() and torch.isfinite(gt).all()),predicted32=rows))
 return sensitivity

def actual_phase_record(last,geometry,age,control,names):
 import torch
 forces=last['body_contact_force31'].norm(dim=-1);ids=[names.index(x) for x in ('left_wheel','right_wheel')];non=[i for i in range(len(names)) if i not in ids]
 bottoms=geometry['low'][0,:,2];loads=forces[ids];nonmax=forces[non].amax()
 air=bool((bottoms>.005).all() and (loads<=1).all() and nonmax<=1)
 return dict(control=control,age_for_action=int(age[0]),public_request_for_action=bool((age[0]>=200)&(age[0]<2000)),airborne_both_above5mm_and_unloaded=air,both_supported=bool((loads>1).all()),wheel_bottom2=json_value(bottoms),wheel_load_norm2=json_value(loads),nonwheel_max_load_N=float(nonmax),root_vz=float(last['root13_sdk_xyzw'][9]),original_counter=last['takeoff_count'],done_boundary_observed_separately=True)

def validate_actual_action_windows(paired,phases,bridge,wm,out):
 import torch
 from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack
 count=len(paired);transitions=[i for i in range(1,count) if phases[i]['airborne_both_above5mm_and_unloaded']!=phases[i-1]['airborne_both_above5mm_and_unloaded']]
 selected=[]
 # Deterministic bounded phase-transition starts first, then uniform temporal
 # coverage. Missing airborne transitions stay explicitly missing.
 for i in transitions[:16]:
  for shift in (31,16,7,4,0):
   j=max(0,i-shift)
   if j not in selected:selected.append(j)
 for i in [0,160,192,200,240,512,1000,1280,1600,1900,*range(0,count,128)]:
  if i<count and i not in selected:selected.append(i)
 selected=selected[:80];rows=[]
 with torch.inference_mode():
  for horizon in (8,32):
   for start in selected:
    if start+horizon>count:continue
    window=paired[start:start+horizon];base=window[0][4]
    if not all(torch.equal(x[4],base+k) for k,x in enumerate(window)):continue
    predicted=unpack(window[0][0]);steps=[]
    for offset,row in enumerate(window,1):
     predicted=wm.step(predicted,row[2],bridge.mdp.normalize_context(row[1]));actual=unpack(row[3]);pg=bridge.mdp.wheel_geometry(predicted);ag=bridge.mdp.wheel_geometry(actual)
     error=(pg['low'][0,:,2]-ag['low'][0,:,2]).abs()
     steps.append(json_value(dict(offset=offset,predicted_root_z=predicted[0][0,2],actual_root_z=actual[0][0,2],predicted_wheel_bottom2=pg['low'][0,:,2],actual_wheel_bottom2=ag['low'][0,:,2],wheel_bottom_abs_error2=error,actual_phase=phases[start+offset-1])))
    labels=phases[start:start+horizon];air=[x['airborne_both_above5mm_and_unloaded'] for x in labels]
    rows.append(dict(start_control=start+1,horizon=horizon,start_age=phases[start]['age_for_action'],starts_grounded_not_air=not air[0],contains_actual_airborne=any(air),grounded_start_then_air=not air[0] and any(air[1:]),contains_air_to_supported=any(air[j-1] and labels[j]['both_supported'] for j in range(1,horizon)),actual_executed_actions_only=True,no_actor_resampling_or_observation_noise_in_validation=True,steps=steps))
 with (out/'NEW108_ACTUAL_ACTION_CONTIGUOUS_8_32_WM_WINDOWS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(rows=rows,actual_controls=count,max_selected_starts=80,phase_transition_count=len(transitions),phase_records=phases,scope='one NEW frozen case, no update; not population heldout accuracy',missing_airborne_windows_not_synthesized=True,no_reset_crossing_imaginary_data=True),f,indent=2,allow_nan=False)
