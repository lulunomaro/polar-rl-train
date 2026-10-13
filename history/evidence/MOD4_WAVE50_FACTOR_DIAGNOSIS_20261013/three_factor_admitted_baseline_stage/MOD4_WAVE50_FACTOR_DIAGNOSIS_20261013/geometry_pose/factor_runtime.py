"""Original 50mm route/query/contact contracts with disclosed diagnostic pose.

Only this independent worker owns the temporary diagnostic event and commands.
"""
from pathlib import Path
import json,time,hashlib,numpy as np,torch
def cpu(x):return x.detach().cpu().numpy().copy()
def js(x):return x.detach().cpu().tolist()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def root_cpu(x):
 y=cpu(x);y[...,3:7]=y[...,[4,5,6,3]];return y
def params(e):
 r=e.scene['robot'];v=r.root_view
 return dict(mass=js(v.get_masses()),inertia=js(v.get_inertias()),materials=js(v.get_material_properties()),COM=js(r.data.body_com_pos_b),
  motors={n:{k:js(getattr(a,k)) for k in ('stiffness','damping','episode_scale','step_scale')} for n,a in r.actuators.items() if n in ('legs','wheels')},
  spring=js(e._spring_pressure.component.factor),gas=js(e._gas_damping.component.factor),PD={k:js(x) for k,x in e._explicit_pd.component.factor.items()},
  action={k:dict(lag=js(g['lag_steps']),episode=js(g['episode'])) for k,g in e._physics_action_delay.queue.groups.items()},
  feedback_requested_us=js(e._feedback_delay_mild.delay*10000),sensor_bias=js(e._sensor_mild.bias),sensor_episode=js(e._sensor_mild.episode),
  mild_factor=js(e._mild_dr.factor),mild_nominal=js(e._mild_dr.nominal),mild_mu=js(e._mild_dr.mu),mild_outputs={k:js(v) for k,v in e._mild_dr.output.items()},
  private_RNG_SHA=private_rng(e))
def private_rng(e):
 out={}
 def walk(v,path,depth):
  if isinstance(v,torch.Generator):out[path]=hashlib.sha256(v.get_state().cpu().numpy().tobytes()).hexdigest()
  elif isinstance(v,dict) and depth>0:
   for k,x in v.items():walk(x,path+'/'+str(k),depth-1)
  elif depth>0 and hasattr(v,'__dict__'):
   for k,x in vars(v).items():
    if k not in ('env','_env','robot','sensor'):walk(x,path+'/'+k,depth-1)
 for k in ('_mild_dr','_sensor_mild','_feedback_delay_mild','_physics_action_delay','_spring_pressure','_gas_damping','_chassis_com','_explicit_pd'):
  walk(getattr(e,k),k,3)
 return out

@torch.inference_mode()
def run_factor(args,O,L,save):
 import warp as wp
 import mod4_task as task
 from g4_cad_wave_geometry import profile
 from g4_retention_runtime import configure_retention
 from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
 from e1_full_pose_reset import query,full_reset
 from e1_terrain_training_health import declared_truncation_terms,ORDINARY_TERMS,INTEGRITY_TERMS,TRUNCATION_TERMS
 from frozen_history_policy import build_frozen_policy
 from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
 from scipy.spatial.transform import Rotation
 torch.manual_seed(args.seed)
 N=args.num_envs;cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=N;cfg.sim.device=args.device
 recipe=configure_retention(cfg)
 for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(cfg.sim.physx,k,v)
 # Yaw matches world direction times body command sign. No corrective heading control.
 yaw=0. if args.body_sign==args.world_sign else np.pi
 rot=Rotation.from_euler('ZYX',[yaw,np.deg2rad(args.pitch_deg),np.deg2rad(args.roll_deg)]).as_matrix()
 quat=Rotation.from_matrix(rot).as_quat()[[3,0,1,2]]
 def diagnostic_birth(env,ids):
  full_reset(env,ids)
  ids=torch.arange(env.num_envs,device=env.device) if ids is None else ids
  if not len(ids):return
  if 'centers' not in centers_holder:return
  # Full bank, original clearance .002m; no simulated step or progress credit.
  r=env.scene['robot'];bank=env._rough_probe_bank;ray=query(env)
  if args.height_m!=.25:
   from e1_rough_reset_tensor import joint_permutation
   with np.load(L/'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz') as archive:
    index=int(np.argmin(abs(archive['root_height']-args.height_m)))
    assert abs(float(archive['root_height'][index])-args.height_m)<1e-6
    perm=joint_permutation(list(archive['joint_names']),r.joint_names)
    bank=dict(points=torch.tensor(archive['points_root'][index],device=env.device,dtype=torch.float32),q=torch.tensor(archive['q'][index,perm],device=env.device,dtype=torch.float32))
   q=bank['q'][None].repeat(len(ids),1);r.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids);env._rough_probe_expected_q[ids]=q
  offsets=bank['points']@torch.tensor(rot.T,device=env.device,dtype=torch.float32)
  xy=env.scene.env_origins[ids,:2];starts=offsets[None].repeat(len(ids),1,1);starts[:,:,:2]+=xy[:,None]
  starts[:,:,2]=float(ray.geometry.vertices[:,2].max())+2.
  surface=ray.cast(starts.contiguous(),10.)
  assert surface['hit'].all() and (surface['normal'][...,2]>.99).all()
  assert float((surface['height'].amax(1)-surface['height'].amin(1)).max())<=1e-6,'Birth fullfootprint must be flat'
  z=(surface['height']+.002-offsets[None,:,2]).amax(1)
  clear=z[:,None]+offsets[None,:,2]-surface['height'];assert float(clear.min())>=.002-1e-5
  state=r.data.root_state_w[ids].clone();state[:,:2]=xy;state[:,2]=z;state[:,3:7]=torch.tensor(quat,device=env.device,dtype=state.dtype);state[:,7:]=0
  r.write_root_state_to_sim(state,env_ids=ids);task.height_cmd(env)[ids]=args.height_m
  env._rough_query_tick=None
  env._factor_birth_receipt=dict(yaw_rad=yaw,pitch_deg=args.pitch_deg,roll_deg=args.roll_deg,height_m=args.height_m,
   bank_points=int(bank['points'].shape[0]),minimum_clearance_m=float(clear.min()),no_physics_step_or_teleport_progress=True,root_wxyz=js(state),q=js(r.data.joint_pos[ids]))
 cfg.events.consistent_start.func=diagnostic_birth
 centers_holder={}
 def boundary(e):
  xy=e.scene['robot'].data.root_pos_w[:,:2]-centers_holder.get('centers',e.scene.env_origins[:,:2]);return (xy[:,0].abs()>3.5)|(xy[:,1].abs()>3.)
 cfg.terminations.rough_route_boundary.func=boundary
 assert cfg.terminations.rough_route_boundary.time_out is True
 e=E1ResetEvidenceLearningEnv(cfg=cfg);r=e.scene['robot'];assign=e.scene.terrain.retention_assignment
 chosen=[]
 for i in range(N):
  row=15+i%20;candidates=sorted([x for x in assign if x['row']==row and x['family']=='random_uniform_for_rm' and not x['actual_mesh_flat']],key=lambda x:x['column'])
  assert len(candidates)==6;chosen.append(candidates[i//20])
 centers=np.asarray([[(x['bounds'][0][k]+x['bounds'][1][k])*.5 for k in (0,1)] for x in chosen]);half=profile()['span_m']*.5
 starts=centers.copy();starts[:,0]-=args.world_sign*(half+args.entry_margin)
 assert len(np.unique(starts,axis=0))==N
 centers_holder['centers']=torch.tensor(centers,device=e.device,dtype=torch.float32)
 e.scene.env_origins[:,:2]=torch.tensor(starts,device=e.device,dtype=torch.float32)
 e.scene.terrain.env_origins[:,:2]=e.scene.env_origins[:,:2];e.reset()
 assert np.array_equal(cpu(r.data.root_pos_w[:,:2]),starts.astype(np.float32))
 assert torch.equal(r.data.joint_pos,e._rough_probe_expected_q) and e.physics_dt==.0025 and e.step_dt==.01
 source=torch.load(args.checkpoint,map_location='cpu',weights_only=False)
 geometric=e.scene.terrain.exact_partition_receipt
 assert source['E1_terrain_state']['geometry_triangles_sha256']==query(e).geometry.receipt()['triangles_sha256']
 assert source['E1_terrain_state']['ordered_partition_triangles_sha256']==geometric['triangle_world_f32_order_sha256']==geometric['partition_triangle_world_f32_order_sha256']
 assert source['E1_terrain_state']['entry_assignment_sha256']==e.scene.terrain.retention_assignment_sha
 from g4_worldmesh_query_contract import expected_ground
 samples=np.linspace(-half,half,33);queryxy=np.repeat(centers[:,None,:],35,axis=1);queryxy[:,1:34,0]+=samples;queryxy[:,0,0]-=half+args.entry_margin;queryxy[:,34,0]+=half+args.entry_margin
 ray=query(e);raystarts=np.concatenate((queryxy,np.full((N,35,1),float(ray.geometry.vertices[:,2].max())+2.)),axis=-1)
 raytensor=torch.tensor(raystarts,device=e.device,dtype=torch.float32);actual=ray.cast(raytensor,10.)
 expected,receipts,triangles=expected_ground(ray.geometry.vertices,ray.geometry.faces,centers,cpu(raytensor))
 assert actual['hit'].all() and (actual['normal'][...,2]>0).all()
 error=float(np.max(abs(cpu(actual['height'])-expected)));assert error<=1e-6
 qpath=O/'worldmesh_query.npz';np.savez_compressed(qpath,actual_world_ray_origins=cpu(raytensor),actual_sampled_ground=cpu(actual['height']),expected_actual_ground=expected,world_triangles=triangles)
 save('QUERY_ACTUAL.json',dict(ground_error_m=error,tolerance_m=1e-6,receipts=receipts,path=str(qpath),bytes=qpath.stat().st_size,sha256=sha(qpath)))
 vec,policy,observer=build_frozen_policy(RslRlVecEnvWrapper(e,clip_actions=6.),args.checkpoint,e.device)
 assert observer.checkpoint_sha256==args.checkpoint_sha
 feedback_factor=None
 if args.feedback_current:
  import sys
  # Resolve peer CPU-prepared module relative to the fixed shared diagnosis root.
  sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'io_dr'))
  from feedback_current_factor import install
  feedback_factor=install(e)
 policy_factor=None
 if args.policy_factor:
  import sys;sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'policy_reward'))
  from policy_factor import apply_factor
  policy_factor=apply_factor
 legs=e.action_manager.get_term('legs')
 cmd=e.command_manager.get_term('twist');cmd.set_manual_evaluation_mode()
 # Fixed stand cohort is retained. It is never required to complete the route.
 groups=torch.full((N,),0 if args.body_sign==1 else 1,device=e.device,dtype=torch.long);groups[-1]=2
 targets=torch.full((N,),args.body_sign*args.speed,device=e.device);targets[-1]=0.
 initial=dict(root_xyzw=root_cpu(r.data.root_state_w).tolist(),q=js(r.data.joint_pos),parameters=params(e),birth=e._factor_birth_receipt,
  actual_assignments=chosen,assignment_sha256=e.scene.terrain.retention_assignment_sha,geometry=e.scene.terrain.exact_partition_receipt)
 save('INITIAL_ACTUAL.json',initial)
 cap=e._integrated_contact;tick0=cap.tick;calls0=dict(e._physics_action_delay.calls);rawforces=[];phase={};names=tuple(e.termination_manager.active_terms);decl=declared_truncation_terms(e.termination_manager)
 capture=cap.capture
 def measured(dt):
  capture(dt);raw=cap.sensor.contact_view.get_net_contact_forces(dt=cap.dt).view(wp.vec3);rawforces.append(cpu(wp.to_torch(raw).reshape(N,2,3)))
 cap.capture=measured;original=e.termination_manager.compute
 def prereset(*a,**k):
  out=original(*a,**k);tm=e.termination_manager
  phase.update(terminated=cpu(tm.terminated),truncated=cpu(tm.time_outs),reasons=np.stack([cpu(tm.get_term(n)) for n in names],-1),impulse=cpu(cap.impulse),history=cpu(cap.history),
   wheel_force=cpu(e.scene.sensors['wheel_contact'].data.net_forces_w),COM_link_pos=cpu(r.data.body_link_pos_w),COM_link_vel=cpu(r.data.body_link_vel_w),applied_torque=cpu(r.data.applied_torque),joint_vel=cpu(r.data.joint_vel),processed_action=cpu(e.action_manager.action),guarded_leg_targets=cpu(legs.processed_actions))
  return out
 e.termination_manager.compute=prereset
 rows={k:[] for k in ('before_root','root','q','command','action','factor_action','processed_action','guarded_leg_targets','ground','normal','closure','mimic','episode','terminated','truncated','reasons','impulse','history','wheel_force','COM_link_pos','COM_link_vel','applied_torque','joint_vel','policy_obs')};episode=np.zeros(N,dtype=np.int64)
 ground_error=0.;height_error=0.;integral_error=0.;started=time.time()
 for step in range(args.steps):
  cmd.time_left[:]=1e9;cmd.is_standing_env[:]=groups==2
  if hasattr(cmd,'is_heading_env'):cmd.is_heading_env[:]=False
  cmd.is_pure_spin[:]=False;cmd.is_moving_spin[:]=False;cmd.is_transition_spin[:]=False;cmd.command[:]=0.;cmd.command[:,0]=targets;task.height_cmd(e)[:]=args.height_m
  before=root_cpu(r.data.root_state_w);requested=cpu(cmd.command);obs=vec.get_observations()
  if args.sensor_clean:obs['policy']=e.clean_policy()
  action=policy(obs)
  if policy_factor is None:factor_action=action
  else:factor_action=policy_factor(action,diff_min=legs.diff_min,diff_max=legs.diff_max,leg_scale=task.LEG_ACTION_SCALE,offsets=legs._offset)
  _,reward,done,_=vec.step(factor_action);frame=e._e1_pre_reset_frame
  ordinary=phase['reasons'][:,[names.index(n) for n in names if n in ORDINARY_TERMS]].any(-1)
  integrity=phase['reasons'][:,[names.index(n) for n in names if n in INTEGRITY_TERMS]].any(-1)
  unknown=phase['reasons'][:,[names.index(n) for n in names if n not in ORDINARY_TERMS|INTEGRITY_TERMS|TRUNCATION_TERMS]].any(-1) if any(n not in ORDINARY_TERMS|INTEGRITY_TERMS|TRUNCATION_TERMS for n in names) else np.zeros(N,dtype=bool)
  trunc=phase['reasons'][:,[names.index(n) for n in names if n in TRUNCATION_TERMS]].any(-1)
  assert np.array_equal(phase['terminated'],ordinary|integrity|unknown) and np.array_equal(phase['truncated'],trunc)
  assert not integrity.any() and not unknown.any()
  assert e._rough_reward_query_tick==e._rough_termination_query_tick==int(e._sim_step_counter)
  ground_error=max(ground_error,frame['independent_ground_error']);height_error=max(height_error,e._e1_height_formula_error)
  assert ground_error<=1e-6 and height_error<=1e-6
  processed=factor_action.clip(-6.,6.);assert np.array_equal(phase['processed_action'],cpu(processed))
  values=dict(before_root=before,root=root_cpu(frame['root']),q=cpu(frame['q']),command=requested,action=cpu(action),factor_action=cpu(factor_action),ground=cpu(frame['ground']),normal=cpu(frame['normal']),closure=cpu(frame['closure']),mimic=cpu(frame['mimic']),episode=episode.copy(),policy_obs=cpu(obs['policy']),**phase)
  assert all(np.isfinite(x).all() for x in values.values()) and torch.isfinite(reward).all() and np.max(values['mimic'])<=.01
  assert len(rawforces)==(step+1)*4
  independent=np.maximum(np.stack(rawforces[-4:])[...,2],0).sum(0)*.0025
  integral_error=max(integral_error,float(np.max(abs(independent-phase['impulse'])))/.01);assert integral_error<=.1
  for k,v in values.items():rows[k].append(v)
  episode+=phase['terminated']|phase['truncated']
  if (step+1)%120==0:print('FACTOR_PROGRESS '+json.dumps(dict(case=args.case_id,controls=step+1,seconds_per_env=(step+1)*.01,wall=time.time()-started)),flush=True)
 data={k:np.stack(v) for k,v in rows.items()};data['physical_wheel_force_N']=np.stack(rawforces);data['group_ids']=cpu(groups);data['targets_m_s']=cpu(targets)
 raw=O/'route_raw.npz';np.savez_compressed(raw,**data)
 audit=e._physics_action_delay.audit();assert cap.tick-tick0==args.steps*4 and all(v-calls0[k]==args.steps*4 for k,v in e._physics_action_delay.calls.items()) and audit['application_formula_max_error']==0
 if feedback_factor is None:assert e.sensor_sdk_audit()['formula_max_error']<=2e-6
 else:assert feedback_factor.receipt()['current_noisy_vs_actual_original_queue_input_max_error']<=2e-6
 assert e.chassis_pd_audit()['parameter_auditor']['actual_parameters_pass']
 save('COMPLETE_ACTUAL.json',dict(epoch=time.time(),passed_data_contract=True,no_PPO=True,case_id=args.case_id,checkpoint_sha256=args.checkpoint_sha,
  factor=dict(body_sign=args.body_sign,world_sign=args.world_sign,yaw_rad=yaw,pitch_deg=args.pitch_deg,roll_deg=args.roll_deg,height_m=args.height_m,entry_margin=args.entry_margin,sensor_clean=args.sensor_clean,feedback_current=args.feedback_current,policy_factor=args.policy_factor,speed=args.speed),
  seed=args.seed,num_envs=N,steps=args.steps,physical_seconds=args.steps*.01,callbacks=args.steps*4,wall_seconds=time.time()-started,body_names=list(r.body_names),joint_names=list(r.joint_names),
  ground_error_m=ground_error,reward_formula_error=height_error,contact_integral_mean_error_N=integral_error,initial=initial,final_parameters=params(e),
  original_health_tolerances=True,reason_names=names,declared_timeouts=decl,ordinary_union=int(data['terminated'].sum()),truncation_union=int(data['truncated'].sum()),
  closure_max_m=float(data['closure'].max()),mimic_max_rad=float(data['mimic'].max()),raw=dict(path=str(raw),bytes=raw.stat().st_size,sha256=sha(raw),shapes={k:list(v.shape) for k,v in data.items()}),
  feedback_factor=feedback_factor.receipt() if feedback_factor else None,qualification_claimed=False,diagnostic_subset=True,actual_initial_parameters_must_be_exact_compared_before_paired_inference=True,root_raw_quaternion_convention='xyzw',recipe=recipe,actor=observer.audit()))
 e.close()
