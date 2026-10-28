"""Frozen native127/obs86/future10 driver. No checkpoint I/O or learning here."""
from pathlib import Path
import ast,hashlib,json,time,traceback
from flat98_eval_contract_v1 import SEEDS,require

def literal(a,b):
 import torch
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(literal(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a) is type(b) and len(a)==len(b) and all(literal(x,y) for x,y in zip(a,b))
 return type(a) is type(b) and a==b
def make_frozen_policy(checkpoint,policy_class,device,*,expected_native_contract):
 import torch
 require(expected_native_contract['changed_plant700_to_nominal400'] is True and expected_native_contract['native_objective_changed'] is True and expected_native_contract['nominal_gas_stiffness_N_m']==2000.,'native88C/400N output recipe required')
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
    self.count+=1;require(self.count<=2000,'fixed original5s/2000 callback cap exceeded')
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

def run_single_case(vec,bridge,pi,unflatten_state,tensor,out,*,seed,source_identity,term_contract,authority_check,wm,flat_counter):
 import torch
 require(seed in SEEDS,'only fixed single seed20260928')
 e=vec.unwrapped;out=Path(out);require(not out.exists(),'consumed episode namespace cannot retry');out.mkdir()
 require(e.num_envs==1 and e.physics_dt==.0025 and e.step_dt==.01 and e.cfg.decimation==4 and e.cfg.episode_length_s==5.,'actual fresh N1 original clock/5s required')
 require(not e.h1_capture and not bool(e.h1_phase.age_control.any()) and not bool(e.h1_phase.goal.success.any()),'fresh original episode/no credit required')
 before={k:v.detach().cpu().clone() for k,v in pi.state_dict().items()}
 wm_before={k:v.detach().cpu().clone() for k,v in wm.state_dict().items()};paired=[]
 history=torch.zeros(1,10,86,device=e.device);previous=torch.zeros(1,6,device=e.device);ep_step=torch.zeros(1,dtype=torch.int32,device=e.device)
 status=dict(seed=seed,source_identity=source_identity,action_mode='deterministic_native_mean_no_collection_noise',native127_obs86_goal146x10=True,
  controls=0,physics_callbacks=0,termination=None,no_learning_no_learner_no_optimizer=True,frozen_WM_prediction_diagnostic=True,
  exact_training_trajectory_replay=False,no_retry_or_seed_selection=True,body_names=list(e.scene['robot'].body_names))
 with (out/'ACTUAL_400HZ_31BODY_FRAMES.jsonl').open('x',encoding='utf8') as fs,(out/'ACTUAL_100HZ_CONTROLS.jsonl').open('x',encoding='utf8') as cs:
  capture=ActualFrames(e,fs,tensor,term_contract);capture.install()
  try:
   with torch.inference_mode():
    initial=capture.state();fs.write(json.dumps(json_value(dict(kind='initial_fresh_episode',physics_callback=0,state=initial)),allow_nan=False)+'\n')
    for control in range(500):
     authority_check();s,xi=bridge.current();age=e.h1_phase.age_control.clone()
     from native_flat_jump_adapter_v1 import encode_frame
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
     require(all(torch.isfinite(v).all() for v in objective.values()),'finite existing own-flat objective required')
     predicted=wm.step(unflatten_state(s),last['executed6'][None],bridge.mdp.normalize_context(xi))
     predicted_geometry=bridge.mdp.wheel_geometry(predicted);actual_geometry=bridge.mdp.wheel_geometry(unflatten_state(s1))
     wm_error=dict(predicted_root_z=predicted[0][0,2],actual_root_z=s1[0,2],predicted_wheel_bottom=predicted_geometry['low'][0,:,2],actual_wheel_bottom=actual_geometry['low'][0,:,2],predicted_Rzz=predicted[1][0,2,2],actual_Rzz=unflatten_state(s1)[1][0,2,2])
     paired.append((s.clone(),xi.clone(),last['executed6'][None].clone(),s1.clone(),frames.clone()))
     cs.write(json.dumps(json_value(dict(control=control+1,age_for_action=age,packed127_for_action=s[0],xi31_for_action=xi[0],mean6=mean[0],raw_native_clamp20_6=raw[0],
      terminal_pre_reset=terminal,terminal_packed127_same_point=s1[0],actual_ownwheel_V2_objective=objective,frozen_WM_one_step=wm_error,actual_original_done=bool(done[0]),physical_V8_reward=reward[0])),allow_nan=False)+'\n')
     previous=last['executed6'][None].clone();ep_step+=1
     status.update(controls=control+1,physics_callbacks=capture.count,last_original_state=json_value(last),last_termination_terms=terminal['termination_terms'])
     if bool(done[0]):status['termination']='actual_original_done';break
    else:status['termination']='fixed5s_cap_censored_if_original_done_absent'
  except BaseException:
   status.update(termination='original_error_partial_single_attempt',original_error=traceback.format_exc());raise
  finally:
   capture.restore();fs.flush();cs.flush()
   status['policy_parameters_and_saved_normalizers_literal_unchanged']=literal(pi.state_dict(),before)
   status['WM_parameters_and_saved_normalizers_literal_unchanged']=literal(wm.state_dict(),wm_before)
   status['flat_real_physics_events']=flat_counter.snapshot()
   status['not_retarget_animation_or_frozen_skill_graduation']=True
   with (out/'FROZEN_SINGLE_CASE_STATUS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(status,f,indent=2,allow_nan=False)
   require(status['policy_parameters_and_saved_normalizers_literal_unchanged'],'frozen policy/normalizers changed')
 from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack
 rollouts=[]
 with torch.inference_mode():
  for start in (0,32,64,96,128,160,192,200,208,216,224,240,256,288,320,400):
   if start+8>len(paired):continue
   predicted=unpack(paired[start][0])
   for offset in range(8):
    row=paired[start+offset];predicted=wm.step(predicted,row[2],bridge.mdp.normalize_context(row[1]))
   target=unpack(paired[start+7][3]);pg=bridge.mdp.wheel_geometry(predicted);tg=bridge.mdp.wheel_geometry(target)
   rollouts.append(json_value(dict(start_control=start+1,horizon=8,original_frame=paired[start][4],predicted_root_z=predicted[0][0,2],actual_root_z=target[0][0,2],predicted_wheel_bottom=pg['low'][0,:,2],actual_wheel_bottom=tg['low'][0,:,2],predicted_Rzz=predicted[1][0,2,2],actual_Rzz=target[1][0,2,2])))
 with (out/'FROZEN_WM_EIGHT_STEP_PAIRED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(rows=rollouts,actual_executed_actions=True,no_actor_or_optimizer_in_rollout=True,not_full_population_or_gradient_accuracy_proof=True),f,indent=2,allow_nan=False)
 require(literal(pi.state_dict(),before) and literal(wm.state_dict(),wm_before),'frozen model or normalizers changed')
 return status
