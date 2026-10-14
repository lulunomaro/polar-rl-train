"""Read-only native3060 witnesses added around original three skill loops.

No policy feedback is recomputed by observers. The old probes' numeric gates,
commands, reset, DR and rewards are kept in the generated main functions.
"""
from pathlib import Path
import hashlib,json,time,math,numpy as np,torch,warp as wp
from factor_runtime_3060_reference17b_v1 import tensor,cpu,js,params,actual_substep_hardware_and_COM
SMALL_EVAL_CAPACITY=dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20)
CONTEXT={}

def plane_query_actual(e,phase):
 """Actual enabled PhysX plane query; all original hit evidence is persisted."""
 from isaaclab.sim import get_current_stage
 from pxr import UsdGeom,UsdPhysics
 from omni.physx import get_physx_scene_query_interface
 from raycast_hit_serializer_v5 import serialize_raycast_hit
 import os
 stage=get_current_stage();plane_path='/World/ground/geometry/mesh';p=stage.GetPrimAtPath(plane_path)
 assert p and p.GetTypeName()=='Plane' and p.HasAPI(UsdPhysics.CollisionAPI)
 assert p.GetAttribute('axis').Get()=='Z'
 tf=UsdGeom.XformCache().GetLocalToWorldTransform(p)
 point=tf.Transform((0.,0.,0.));normal=tf.TransformDir((0.,0.,1.))
 assert abs(float(point[2]))<=1e-6 and np.max(abs(np.asarray(normal)-[0.,0.,1.]))<=1e-6
 scene=stage.GetPrimAtPath(e.cfg.sim.physics_prim_path)
 actual_query_flag=scene.GetAttribute('physxScene:enableSceneQuerySupport').Get()
 assert e.cfg.sim.enable_scene_query_support is True and actual_query_flag is True,('Actual scene-query support not enabled',actual_query_flag)
 evidence=dict(phase=phase,actual_requested_query_support=e.cfg.sim.enable_scene_query_support,actual_physics_scene_path=e.cfg.sim.physics_prim_path,actual_USD_scene_query_support=actual_query_flag,authored_plane=dict(path=str(p.GetPath()),type=p.GetTypeName(),axis=p.GetAttribute('axis').Get(),point=list(point),normal=list(normal)),tolerance_m=1e-6,all_rays=[],no_physical_step_no_cache_forward_no_RNG=True)
 destination=Path(CONTEXT['output_dir'])/('QUERY_'+phase+'_ALLHITS_ACTUAL.json');assert not destination.exists()
 def persist():
  temporary=destination.with_suffix(destination.suffix+'.partial')
  with temporary.open('wb') as out:out.write(json.dumps(evidence,indent=2).encode('utf8'));out.flush();os.fsync(out.fileno())
  os.replace(temporary,destination)
 def value(x):
  if x is None or isinstance(x,(bool,int,float,str)):return x
  try:return [float(v) for v in x]
  except (TypeError,ValueError):return str(x)
 actual=cpu(e.scene['robot'].data.root_pos_w);rows=[];query=get_physx_scene_query_interface()
 for i,xy in enumerate(actual[:,:2]):
  allhits=[]
  def callback(hit):
   allhits.append(serialize_raycast_hit(hit));return True
  returned=query.raycast_all((float(xy[0]),float(xy[1]),10.),(0.,0.,-1.),20.,callback)
  ray=dict(env_id=i,origin=[float(xy[0]),float(xy[1]),10.],direction=[0.,0.,-1.],maximum_distance=20.,query_return=value(returned),all_reported_hits=allhits,selected_plane_hits=[])
  for hit in allhits:
   collision=str(hit.get('collision',''))
   if collision==plane_path or collision.startswith(plane_path+'/'):
    ray['selected_plane_hits'].append(dict(hit=hit,resolved_plane_path=plane_path,identity_resolution='reported path exact or child of actual USD Plane'))
   elif collision and plane_path.startswith(collision+'/'):
    ancestor=stage.GetPrimAtPath(collision)
    colliders=[x for x in UsdGeom.PrimRange(ancestor) if x.HasAPI(UsdPhysics.CollisionAPI)] if hasattr(UsdGeom,'PrimRange') else None
    if colliders is None:
     from pxr import Usd
     colliders=[x for x in Usd.PrimRange(ancestor) if x.HasAPI(UsdPhysics.CollisionAPI)]
    if len(colliders)==1 and str(colliders[0].GetPath())==plane_path:
     ray['selected_plane_hits'].append(dict(hit=hit,resolved_plane_path=plane_path,identity_resolution='reported ancestor has exactly one actual collision shape, the frozen USD Plane'))
  ray['serializer_errors']=[h for h in allhits if h.get('_serializer_error')]
  evidence['all_rays'].append(ray);persist()
  assert not ray['serializer_errors'],('Actual typed hit serialization failed',phase,i,ray['serializer_errors'])
  assert ray['selected_plane_hits'],('Actual plane query missing',phase,i,allhits)
  selected=min(ray['selected_plane_hits'],key=lambda x:x['hit']['distance']);h=selected['hit']
  assert abs(float(h['position'][2]))<=1e-6 and abs(float(h['normal'][2])-1.)<=1e-6,('Actual plane query violates original tolerance',phase,i,h)
  rows.append(dict(env_id=i,origin=ray['origin'],hit=h,resolved_plane_path=selected['resolved_plane_path'],identity_resolution=selected['identity_resolution']))
 evidence['complete_all_envs']=True;persist()
 return dict(phase=phase,query_rows=rows,authored_plane=evidence['authored_plane'],tolerance_m=1e-6,no_physical_step_no_RNG=True,scene_query_support_requested=True,actual_USD_scene_query_support=True,allhits_evidence=dict(path=str(destination),bytes=destination.stat().st_size,sha256=hashlib.sha256(destination.read_bytes()).hexdigest()))


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
  self.names=tuple(e.termination_manager.active_terms)
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
   self.rows.append(row);self.episode+=(row['terminated']|row['truncated']).astype(np.int64);self.phase=None;self.obs=None;self.raw_action=None
   return result
  e.step=measured_step

 def finish(self,result):
  assert len(self.rows)==self.args.steps and len(self.sub)==4*self.args.steps
  e=self.e;r=e.scene['robot'];source=torch.load(self.args.checkpoint,map_location='cpu',weights_only=False)
  assert source['E1_terrain_state']['num_envs']==20000
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
  report=dict(case_id=self.args.case_id,kind=self.args.kind,checkpoint_sha256=self.args.checkpoint_sha,source_saved_envs=20000,fixture_envs=e.num_envs,steps=self.args.steps,callbacks=self.args.steps*4,seed=self.args.seed,DR_profile='white_v3',first_physics_initial=self.initial,final_physical_parameters=params(e),raw=dict(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),shapes={k:list(x.shape) for k,x in arrays.items()}),actual_plane_query=dict(path=str(query),sha256=hashlib.sha256(query.read_bytes()).hexdigest()),reason_names=self.names,reason_time_out=self.reason_time_out,hardware_model_constants=self.hardware_constants,action_callback_delta=callbacks,ordinary_actual=int(arrays['terminated'].sum()),truncation_actual=int(arrays['truncated'].sum()),independent_mean_load_error_N=float(arrays['independent_control_mean_load_error_N'].max()),COM_frame_error_m=float(arrays['substep_COM_frame_error_m'].max()),only_actor_loaded=True,no_PPO=True,initial_source_DR_not_restored=True,original_numeric_gates_retained=True,old_original_flags={k:result[k] for k in ('strict_pass','spin_skill_pass','spin_skill_pass_legacy_reference','physical_smoke_pass','strict_pass_window','physics_pass') if k in result},pending_qualification=True)
  result['native_readonly_witness']=report
  Path(self.args.output).write_text(json.dumps(result,indent=2),encoding='utf8')
  CONTEXT['save']('COMPLETE_ACTUAL.json',dict(passed_data_contract=True,case_id=self.args.case_id,kind=self.args.kind,checkpoint_sha256=self.args.checkpoint_sha,steps=self.args.steps,num_envs=e.num_envs,callbacks=self.args.steps*4,raw=report['raw'],probe=dict(path=self.args.output,sha256=hashlib.sha256(Path(self.args.output).read_bytes()).hexdigest()),ordinary=report['ordinary_actual'],no_PPO=True,qualification_claimed=False,new_scope_native120_only=self.args.steps==120))
  e.close()

def create_observed_env(args,cfg):
 from chassis_pd_training_env import ChassisPDMod4Env
 assert cfg.sim.dt==.0025 and cfg.decimation==4 and cfg.scene.num_envs==({'flat':80,'spin':88,'world':88}[args.kind])
 e=ChassisPDMod4Env(cfg=cfg);e._retention_native_witness=Witness(e,args);return e

def build_observed_frozen_policy(vec,path,device):
 from frozen_history_policy import build_frozen_policy
 wrapped,policy,observer=build_frozen_policy(vec,path,device)
 original=wrapped.get_observations
 def observed():
  values=original();wrapped.env._retention_native_witness.obs=cpu(values['policy']);return values
 wrapped.get_observations=observed
 source=torch.load(path,map_location='cpu',weights_only=False);closures=dict(zip(policy.__code__.co_freevars,[x.cell_contents for x in policy.__closure__ or ()]));assert 'actor' in closures;actor=closures['actor']
 assert len(actor.state_dict())==9 and all(torch.equal(v.cpu(),source['actor_state_dict'][k]) for k,v in actor.state_dict().items())
 def observed_policy(values):
  output=policy(values);wrapped.env._retention_native_witness.raw_action=cpu(output);return output
 return wrapped,observed_policy,observer

def finalize_observer(env,result):env._retention_native_witness.finish(result)
