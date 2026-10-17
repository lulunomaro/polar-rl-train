"""Read-only native3060 witnesses added around original three skill loops.

No policy feedback is recomputed by observers. The old probes' numeric gates,
commands, reset, DR and rewards are kept in the generated main functions.
"""
from pathlib import Path
import hashlib,json,time,math,numpy as np,torch,warp as wp
from factor_runtime_3060_reference17b_v1 import tensor,cpu,js,params,actual_substep_hardware_and_COM
SMALL_EVAL_CAPACITY=dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20)
CONTEXT={}
from e2_frozen_prefix_guard_v4 import check_physics,check_control,check_reasons,declared_config

def plane_query_actual(e,phase):
 from h1_plane_reference80_v1 import plane_query_actual as new_reference
 return new_reference(e,phase,CONTEXT)



def scalar_or_tensor_json(value):
 """Keep exact native scalars; all tensor/ProxyArray reads use original js."""
 import numbers
 if isinstance(value,np.generic):value=value.item()
 if isinstance(value,bool):return value
 if isinstance(value,numbers.Integral):return int(value)
 if isinstance(value,numbers.Real):
  result=float(value);assert math.isfinite(result),'Nonfinite actual hardware constant';return result
 return js(value)

class Witness:
 def __init__(self,e,args):
  self.e=e;self.args=args;self.O=Path(args.output).parent;self.rows=[];self.sub=[];self.episode=np.zeros(e.num_envs,dtype=np.int64);self.active=False;self.phase=None;self.obs=None;self.raw_action=None;self.initial=None;self.calls0=None;self.cap=e._integrated_contact
  self.names=tuple(e.termination_manager.active_terms);check_reasons(self.names)
  self.reason_time_out={n:bool(e.termination_manager.get_term_cfg(n).time_out) for n in self.names}
  original_compute=e.termination_manager.compute
  def compute(*a,**k):
   result=original_compute(*a,**k)
   if self.active:
    r=e.scene['robot'];tm=e.termination_manager
    from mod4_task import closure_errors,mimic_errors
    self.phase=dict(root=cpu(r.data.root_state_w),q=cpu(r.data.joint_pos),heading=cpu(r.data.heading_w),terminated=cpu(tm.terminated),truncated=cpu(tm.time_outs),reasons=np.stack([cpu(tm.get_term(n)) for n in self.names],-1),impulse=cpu(self.cap.impulse),contact_history=cpu(self.cap.history),wheel_force=cpu(e.scene.sensors['wheel_contact'].data.net_forces_w),joint_vel=cpu(r.data.joint_vel),applied_torque=cpu(r.data.applied_torque),closure=cpu(torch.stack(list(closure_errors(e).values())).max(0).values),mimic=cpu(torch.stack(list(mimic_errors(e).values())).max(0).values),processed_action=cpu(e.action_manager.action),guarded_leg_targets=cpu(e.action_manager.get_term('legs').processed_actions))
   return result
  e.termination_manager.compute=compute
  capture=self.cap.capture
  def measured(dt):
   capture(dt)
   if not self.active:return
   assert float(dt)==.0025
   raw=self.cap.sensor.contact_view.get_net_contact_forces(dt=self.cap.dt).view(wp.vec3)
   h=actual_substep_hardware_and_COM(e);r=e.scene['robot']
   ids,_=r.find_bodies(['left_wheel','right_wheel'],preserve_order=True)
   self.sub.append(dict(force=cpu(wp.to_torch(raw).reshape(e.num_envs,2,3)),**h['arrays'],COM_frame_error_m=np.asarray(h['COM_frame_error_m']),mass_weighted_COM_world=h['mass_weighted_COM_world'],wheel_link_pose=cpu(tensor(r.data.body_link_pose_w)[:,ids]),wheel_COM_pose=cpu(tensor(r.data.body_com_pose_b)[:,ids]),wheel_COM_vel=cpu(tensor(r.data.body_com_vel_w)[:,ids]),wheel_link_vel=cpu(tensor(r.data.body_link_vel_w)[:,ids])))
   check_physics(h)
  self.cap.capture=measured
  step=e.step
  def measured_step(action):
   assert self.obs is not None and self.raw_action is not None,'Actual decision feedback and raw policy output must be captured before action'
   r=e.scene['robot'];cmd=e.command_manager.get_term('twist')
   if self.initial is None:
    self.initial=dict(root=js(r.data.root_state_w),q30=js(r.data.joint_pos),physical_parameters=params(e),phase='after all original resets and policy construction, before first physical step',plane_query=plane_query_actual(e,'first_physics'))
    self.calls0=dict(e._physics_action_delay.calls)
    self.hardware_constants={name:{key:scalar_or_tensor_json(getattr(r.actuators[name],key)) for key in ('_vel_at_effort_lim','_saturation_effort','velocity_limit','effort_limit')} for name in ('legs','wheels')}
   before=cpu(r.data.root_state_w);before_q=cpu(r.data.joint_pos);command=cpu(cmd.command);obs=self.obs.copy();act=cpu(action);count=len(self.sub);self.active=True
   result=step(action);self.active=False
   assert self.phase is not None and len(self.sub)-count==4
   row=dict(before_root=before,before_q=before_q,command=command,policy_obs=obs,raw_actor_action=self.raw_action.copy(),vec_clipped_action=act,episode=self.episode.copy(),after_reset_root=cpu(r.data.root_state_w),**self.phase)
   force=np.stack([x['force'] for x in self.sub[count:]])
   row['independent_control_mean_load_error_N']=np.asarray(np.max(abs(np.maximum(force[...,2].astype(np.float64),0.).sum(0)*.0025-row['impulse']))/.01)
   assert float(row['independent_control_mean_load_error_N'])<=.1
   from mod4_task import closure_errors,mimic_errors
   row['post_reset_closure']=cpu(torch.stack(list(closure_errors(e).values())).max(0).values)
   row['post_reset_mimic']=cpu(torch.stack(list(mimic_errors(e).values())).max(0).values)
   self.rows.append(row);check_control(row);self.episode+=(row['terminated']|row['truncated']).astype(np.int64);self.phase=None;self.obs=None;self.raw_action=None
   return result
  e.step=measured_step

 def finish(self,result):
  assert len(self.rows)==self.args.steps and len(self.sub)==4*self.args.steps
  e=self.e;r=e.scene['robot'];source=torch.load(self.args.checkpoint,map_location='cpu',weights_only=False)
  from h1_mean_repair_first_source_guard_v1 import validate_H1_source
  validate_H1_source(source)
  arrays={k:np.stack([x[k] for x in self.rows]) for k in self.rows[0]}
  arrays.update({'substep_'+k:np.stack([x[k] for x in self.sub]) for k in self.sub[0]})
  for k,x in arrays.items():
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  assert arrays['q'].shape==(self.args.steps,e.num_envs,30)
  assert arrays['policy_obs'].shape==(self.args.steps,e.num_envs,35)
  assert np.array_equal(arrays['before_root'][0],np.asarray(self.initial['root'],dtype=np.float32))
  for i in range(1,self.args.steps):
   assert np.array_equal(arrays['before_root'][i],arrays['after_reset_root'][i-1])
  path=self.O/'retention_full_control_substep_actual.npz';assert not path.exists();np.savez_compressed(path,**arrays)
  query=self.O/'retention_plane_query_actual.json';assert not query.exists();query.write_text(json.dumps(dict(initial=self.initial['plane_query'],final=plane_query_actual(e,'final')),indent=2),encoding='utf8')
  callbacks={k:v-self.calls0[k] for k,v in e._physics_action_delay.calls.items()};assert callbacks==dict(legs=self.args.steps*4,wheels=self.args.steps*4)
  report=dict(actual_eval_integrity_guard=CONTEXT['actual_eval_integrity_guard'],declared_eval_integrity_guard=CONTEXT['declared_eval_integrity_guard'],case_id=self.args.case_id,kind=self.args.kind,checkpoint_sha256=self.args.checkpoint_sha,source_saved_envs=20000,fixture_envs=e.num_envs,steps=self.args.steps,callbacks=self.args.steps*4,seed=self.args.seed,DR_profile=self.args.dr_profile,first_physics_initial=self.initial,final_physical_parameters=params(e),raw=dict(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),shapes={k:list(x.shape) for k,x in arrays.items()}),actual_plane_query=dict(path=str(query),sha256=hashlib.sha256(query.read_bytes()).hexdigest()),reason_names=self.names,reason_time_out=self.reason_time_out,hardware_model_constants=self.hardware_constants,action_callback_delta=callbacks,ordinary_actual=int(arrays['terminated'].sum()),truncation_actual=int(arrays['truncated'].sum()),independent_mean_load_error_N=float(arrays['independent_control_mean_load_error_N'].max()),COM_frame_error_m=float(arrays['substep_COM_frame_error_m'].max()),only_actor_loaded=CONTEXT['router_mode']=='single_eval',only_frozen_policy_outputs_executed=True,loaded_control_mode=CONTEXT['router_mode'],trained_gate_loaded_only_for_pair=CONTEXT['router_mode']!='single_eval',no_PPO=True,initial_source_DR_not_restored=True,original_numeric_gates_retained=True,old_original_flags={k:result[k] for k in ('strict_pass','spin_skill_pass','spin_skill_pass_legacy_reference','physical_smoke_pass','strict_pass_window','physics_pass') if k in result},pending_qualification=True)
  result['native_readonly_witness']=report
  Path(self.args.output).write_text(json.dumps(result,indent=2),encoding='utf8')
  CONTEXT['save']('COMPLETE_ACTUAL.json',dict(passed_data_contract=True,case_id=self.args.case_id,kind=self.args.kind,checkpoint_sha256=self.args.checkpoint_sha,steps=self.args.steps,num_envs=e.num_envs,callbacks=self.args.steps*4,raw=report['raw'],probe=dict(path=self.args.output,sha256=hashlib.sha256(Path(self.args.output).read_bytes()).hexdigest()),ordinary=report['ordinary_actual'],no_PPO=True,qualification_claimed=False,new_scope_native120_only=self.args.steps==120))
  e.close()

def create_observed_env(args,cfg):
 from h1_takeoff_progress_environment_v2 import H1FullstateEnv
 from h1_takeoff_progress_reward_v2 import configure,isolated_actual_SDK_dt_probe
 from isaaclab.sensors import ContactSensorCfg
 assert cfg.sim.dt==.0025 and cfg.decimation==4 and cfg.scene.num_envs==80
 configure(cfg);cfg.scene.full_robot_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/.*',update_period=0.0,history_length=1,track_air_time=False)
 CONTEXT['declared_eval_integrity_guard']=declared_config(cfg)
 e=H1FullstateEnv(cfg=cfg);CONTEXT['env']=e
 actual=dict(mimic=float(e.termination_manager.get_term_cfg('mimic').params['threshold']),closure=float(e.termination_manager.get_term_cfg('closure').params['threshold']),physics_dt=float(e.cfg.sim.dt),decimation=int(e.cfg.decimation),episode_seconds=float(e.cfg.episode_length_s),num_envs=int(e.num_envs))
 assert actual['mimic']==.01 and actual['closure']==.002 and actual['episode_seconds']>=15 and actual['num_envs']==80
 CONTEXT['actual_eval_integrity_guard']=actual;CONTEXT['save']('ACTUAL_RUNTIME_CONFIG_READBACK.json',dict(actual=actual,declared=CONTEXT['declared_eval_integrity_guard']))
 CONTEXT['save']('H1_ACTUAL_SDK_REWARD_DT_READBACK.json',isolated_actual_SDK_dt_probe(e))
 e._retention_native_witness=Witness(e,args);w=e._retention_native_witness
 e.h1_witness_ids=torch.arange(e.num_envs,device=e.device);e.h1_capture=True
 update=e.scene.update
 def observed_update(dt):
  before=len(w.sub);update(dt)
  if not w.active:return
  assert len(w.sub)==before+1 and len(e.h1_physical_rows)==1
  physical=e.h1_physical_rows.pop();w.sub[-1].update({'H1_'+key:cpu(value) for key,value in physical.items()})
  for key,value in w.sub[-1].items():
   if np.asarray(value).dtype.kind in 'fc':assert np.isfinite(value).all(),('H1 physical nonfinite',key)
 e.scene.update=observed_update
 termination=e.termination_manager.compute
 def observed_termination(*args,**kwargs):
  value=termination(*args,**kwargs)
  if w.active:
   assert e.h1_control_frame is not None
   w.phase.update({'H1_'+key:cpu(value) for key,value in e.h1_control_frame.items()})
   w.phase.update({'H1_phase_'+key:cpu(value) for key,value in e.h1_phase.tensors().items()})
  return value
 e.termination_manager.compute=observed_termination
 reward=e.reward_manager.compute
 def observed_reward(*args,**kwargs):
  value=reward(*args,**kwargs)
  if w.active:
   assert e.h1_control_frame is not None and 'event_applied' in e.h1_control_frame and 'progress_applied' in e.h1_control_frame
   w.phase.update({'H1_'+key:cpu(value) for key,value in e.h1_control_frame.items()});e.h1_control_frame=None
  return value
 e.reward_manager.compute=observed_reward
 return e
def build_observed_frozen_policy(vec,path,device):
 from h1_retention_single04_adapter_v1 import build_retention_single
 assert CONTEXT['router_mode']=='single_eval'
 return build_retention_single(vec,path,device)
def finalize_observer(env,result):env._retention_native_witness.finish(result)
