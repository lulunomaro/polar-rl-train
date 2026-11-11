"""Paired SCUT-to-MOD4 frozen-policy speed diagnostic. Original MOD4 physics; no optimizer."""
from pathlib import Path
import argparse,base64,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--support',required=True);p.add_argument('--version',required=True);p.add_argument('--models',required=True);p.add_argument('--level',type=int,choices=[0,3],default=0);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],a.support]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch,warp as wp,numpy as np
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_remaining_dr_env import ScutFlatRemainingDREnv
 class ScutFlatPhysicalDelayEnv(ScutFlatRemainingDREnv):
  rough_terrain=True
  def _get_dones(self):
   term,timeout=super()._get_dones()
   if hasattr(self,'terrain'):
    center=self.terrain.terrain_origins[self.terrain.terrain_levels,self.terrain.terrain_types]
    timeout|=((self.view.data.root_pos_w[:,:2]-center[:,:2]).abs().amax(-1)>4.)&(~term)
   return term,timeout
 from rough_r1_terrain import FAMILIES,COUNTS
 from isaaclab.utils.warp import raycast_mesh
 from mod4v3_ppo_v1.physical_delay_checks import TASKS,_ground_start
 TASKS=[(f"{family}_{direction}",float(direction),0.,.28,None,None) for family in FAMILIES[:-1] for direction in (-1,1)]
 from mod4v3_ppo_v1.sampling import Sampling
 from mod4v1_scut.math_ops import euler_xyz_from_quat
 from isaaclab.utils.math import quat_from_euler_xyz
 from tensordict import TensorDict
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 models=json.loads(Path(a.models).read_text());variants=['nominal0','fullDR','wheel_mu_nominal','wheel_restitution_zero','guide_mu_nominal','base_mu_nominal','wheel_all_nominal','all_material_nominal','no_material'];per=10;small=len(TASKS)*per;n=small*len(variants)*len(models);dev='cuda:0'
 ids=torch.arange(n,device=dev);base_ids=torch.arange(small,device=dev).repeat(len(variants)*len(models));variant_index=(ids//small)%len(variants);nominal=variant_index==0
 def select(name):return variant_index==variants.index(name)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatPhysicalDelayEnv(configuration(meta,bank,n,66,terrain_selection='rough_r1'),meta,bank);env.render_enabled=False
 env.enforce_closure_reset=True
 # Sample one central 9x9 tile of midstairs and inverted midstairs on the existing collision mesh.
 terrain_for_export=env.scene['terrain'];grid=torch.linspace(-4.5,4.5,181,device='cuda:0');gx,gy=torch.meshgrid(grid,grid,indexing='xy')
 export_profiles={}
 # R1 family column offsets are [0,8,14,20,26,35,41,50,56].
 for family,col in [('mid',26),('inv_mid',41)]:
  center=terrain_for_export.terrain_origins[a.level,col]
  origins=torch.stack((gx+center[0],gy+center[1],torch.full_like(gx,center[2]+10.)),dim=-1).reshape(-1,3)
  directions=torch.zeros_like(origins);directions[:,2]=-1.
  terrain_hits=raycast_mesh(origins,directions,terrain_for_export.r1_wp_mesh,max_dist=30.)[0]
  export_profiles[family]=terrain_hits[:,2].reshape(181,181).cpu().numpy()-float(center[2])
 np.savez_compressed(out/'terrain_heightfields.npz',**export_profiles,grid=grid.cpu().numpy())
 dr=env.full_dr;nominal_com=dr.com_nominal.clone()
 # Fixed type/level/offset/initial states are paired across every model and condition.
 family_id=torch.arange(small,device=dev)//(2*per)
 family_cols=[];offset=0
 for count in COUNTS:
  family_cols.append(offset);offset+=count
 env.terrain=env.scene['terrain']
 env.terrain.terrain_types[:]=torch.tensor(family_cols,device=dev)[family_id[base_ids]]
 env.terrain.terrain_levels.fill_(a.level)
 env.terrain.r1_offsets.zero_()
 # Ten close but distinct starts at each tile center, same for all models.
 jitter=torch.linspace(-.20,.20,per,device=dev).repeat(len(TASKS))[base_ids]
 env.terrain.r1_offsets[:,0]=torch.tensor([(-.8 if task[1]>0 else .8) for task in TASKS],device=dev).repeat_interleave(per)[base_ids]
 env.terrain.r1_offsets[:,1]=jitter
 origin=env.terrain.terrain_origins[env.terrain.terrain_levels,env.terrain.terrain_types].clone()+env.terrain.r1_offsets
 starts=origin.clone();starts[:,2]+=5.;down=torch.zeros_like(starts);down[:,2]=-1.
 hits=raycast_mesh(starts,down,env.terrain.r1_wp_mesh,max_dist=10.)[0]
 assert bool(torch.isfinite(hits).all())
 origin[:,2]=hits[:,2];env.terrain.env_origins[:]=origin;env.scene.env_origins[:]=origin
 _ground_start(env,6600);env.sample=Sampling(env)
 def mirror(x):return x[base_ids.to(x.device)].clone()
 masses=mirror(tensor(env.robot.root_view.get_masses()).to(dev));inertias=mirror(tensor(env.robot.root_view.get_inertias()).to(dev));coms=mirror(tensor(env.robot.root_view.get_coms()).to(dev));materials=mirror(tensor(env.robot.root_view.get_material_properties()).cpu())
 fr=tensor(env.robot.root_view.get_dof_friction_properties()).clone().to(dev)[base_ids]
 for target in (dr.leg_gain_scale,dr.wheel_gain_scale,dr.spring_damping_scale,dr.torque_noise_scale,dr.body_mass_scale,dr.total_mass_scale,dr.factor,dr.kp_scale,dr.kd_scale,env._leg_damping_scale):target.copy_(mirror(target))
 masses[nominal]=dr.mass[nominal];inertias[nominal]=dr.inertia[nominal];coms[nominal]=nominal_com[nominal];materials[nominal.cpu()]=dr.materials[nominal.cpu()]
 dr.body_mass_scale[nominal]=1.;dr.total_mass_scale[nominal]=1.;dr.factor[nominal]=1.
 dr.leg_gain_scale[nominal]=1.;dr.wheel_gain_scale[nominal]=1.;dr.spring_damping_scale[nominal]=1.;dr.torque_noise_scale[nominal]=0.
 fr[nominal,:,0]=dr.static_friction_default[nominal]
 fr[nominal,:,1]=(dr.dynamic_friction_default if dr.dynamic_friction_default is not None else dr.static_friction_default)[nominal]
 fr[nominal,:,2]=(dr.viscous_friction_default if dr.viscous_friction_default is not None else torch.zeros_like(dr.static_friction_default))[nominal]
 dr.kp_scale[nominal]=1.;dr.kd_scale[nominal]=1.;env._leg_damping_scale[nominal]=1.
 native_damping=dr.nominal_joint_damping*dr.kd_scale
 native_damping[:,env.active_ids]=0.
 native_damping[:,env.gas_ids]=3.*dr.spring_damping_scale
 env.robot.write_joint_damping_to_sim_index(damping=native_damping,env_ids=ids)
 for actuator in env.robot.actuators.values():
  tensor(actuator.damping).copy_(native_damping[:,actuator.joint_indices])
 # Isolate contact material channels while retaining all other fullDR draws.
 for name,group,channels in [('wheel_mu_nominal','wheel',(0,1)),('wheel_restitution_zero','wheel',(2,)),('guide_mu_nominal','guide',(0,1)),('base_mu_nominal','base',(0,1)),('wheel_all_nominal','wheel',(0,1,2))]:
  rows=select(name).nonzero().flatten().cpu()
  shapes=dr.material_shapes[group]
  for channel in channels:
   materials[rows[:,None],shapes,channel]=dr.materials[rows[:,None],shapes,channel]
 for name in ['all_material_nominal','no_material']:
  mask=select(name);materials[mask.cpu()]=dr.materials[mask.cpu()]
 env.robot.write_joint_damping_to_sim_index(damping=native_damping,env_ids=ids)
 env._ground_command_until.zero_()
 env.robot.set_coms_index(coms=wp.from_torch(coms[:,[dr.base_id],:].contiguous(),dtype=wp.transformf),body_ids=[dr.base_id],env_ids=ids,full_data=False)
 env.robot.set_masses_index(masses=masses,env_ids=ids);env.robot.set_inertias_index(inertias=inertias,env_ids=ids)
 env.robot.root_view.set_material_properties(wp.from_torch(materials.contiguous(),dtype=wp.float32),wp.from_torch(ids.to('cpu',torch.int32),dtype=wp.int32))
 env.robot.write_joint_friction_coefficient_to_sim(joint_friction_coeff=fr[:,:,0],joint_dynamic_friction_coeff=fr[:,:,1],joint_viscous_friction_coeff=fr[:,:,2],joint_ids=dr.joint_ids,env_ids=ids)
 dr.startup_materials.copy_(materials)
 dr.wheel_material_values=torch.cat([materials[:,shapes].mean(1) for shapes in dr.wheel_material_shapes],-1).to(dev)
 dr.material_mu.copy_(dr.wheel_material_values[:,[0,3]].mean(-1))
 dr.effort_scale.copy_(dr.effort_scale[base_ids]);dr.effort_scale[nominal]=1.
 # Same grounded bank pose and root perturbation for every version and DR condition.
 gen=torch.Generator(device=dev).manual_seed(6600);pick=torch.randint(len(env._bank_h),(small,),device=dev,generator=gen)[base_ids]
 q=env._bank_q[pick][:,env._bank_ids].clone();root=tensor(env.robot.data.default_root_state).clone();root[:,:3]+=env.scene.env_origins;root[:,2]=env.scene.env_origins[:,2]+env._bank_h[pick]
 def uniform(lo,hi):return torch.empty(small,device=dev).uniform_(lo,hi,generator=gen)[base_ids]
 root[:,3:7]=quat_from_euler_xyz(uniform(-.01,.01),uniform(-.01,.01),uniform(-.05,.05));root[:,7:]=0.;root[:,7]=uniform(-.01,.01);root[:,12]=uniform(-.01,.01)

 env.robot.write_root_state_to_sim(root,env_ids=ids);env.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
 env.actions.zero_();env.torque.zero_();env.zero_torque_remaining.zero_();env.episode_length_buf.zero_();env.reward.reset(ids);env.reward._invalidate_step_caches()
 initial_positions=root[:,:3].clone()
 # Measure the actual collision-mesh path; reference heightfields interpolate between .1m samples.
 profile_distance=torch.arange(0.,2.501,.025,device=dev)
 path_sign=torch.tensor([task[1] for task in TASKS],device=dev).repeat_interleave(per).sign()[base_ids]
 ray_start=initial_positions[:,None,:].expand(-1,len(profile_distance),-1).clone()
 ray_start[:,:,0]+=path_sign[:,None]*profile_distance[None,:];ray_start[:,:,2]+=5.
 ray_dir=torch.zeros_like(ray_start);ray_dir[:,:,2]=-1.
 profile_hits=raycast_mesh(ray_start.reshape(-1,3),ray_dir.reshape(-1,3),env.terrain.r1_wp_mesh,max_dist=10.)[0].reshape(n,len(profile_distance),3)
 assert bool(torch.isfinite(profile_hits).all()),'R1 path profile ray missed'
 profile_height=profile_hits[:,:,2];family_by_env=family_id[base_ids]
 mid=torch.tensor([('for_rm_mid' in FAMILIES[int(x)]) for x in family_by_env.cpu().tolist()],device=dev)
 step_height=torch.full((n,),.025 if a.level==0 else .035,device=dev)
 cumulative_change=(profile_height[:,1:]-profile_height[:,:-1]).abs().cumsum(-1)
 qualified=cumulative_change>=2.*step_height[:,None]-.001
 assert bool(qualified[mid].any(-1).all()),'Mid stair path lacks two effective height increments'
 clearance_distance=torch.where(mid,(qualified.long().argmax(-1)+1)*.025+.2,torch.zeros(n,device=dev))
 target_distance=torch.maximum(clearance_distance,torch.full_like(clearance_distance,2.))
 wheel_body_ids=[env.robot.body_names.index(name) for name in ('left_wheel_link','right_wheel_link')]
 ground_min=env.scene.env_origins[:,2].clone();ground_max=ground_min.clone()
 commands=torch.tensor([[vx,0.,wz] for _,vx,wz,_,_,_ in TASKS],device=dev).repeat_interleave(per,0).repeat(len(variants)*len(models),1)
 heights=torch.tensor([h for _,_,_,h,_,_ in TASKS],device=dev).repeat_interleave(per).repeat(len(variants)*len(models))
 def command():
  env.command.copy_(commands);env.height.copy_(heights);env.command_timer.fill_(10000.);env.heading_env.zero_();env.standing_env.zero_();env.reward.command.copy_(commands);env.reward.height_cmd.copy_(heights)
 command();env._execution_pending.fill_(True);env._sensor_pending.fill_(True);env._sensor_last_tick=-1
 env._action_delay_ticks.copy_(env._action_delay_ticks[base_ids]);env._sensor_delay_ticks.copy_(env._sensor_delay_ticks[base_ids]);env._action_delay_ticks[nominal]=0;env._sensor_delay_ticks[nominal]=0
 env._external_force.zero_();env._external_torque.zero_();env._external_hold.zero_();env._external_timer.fill_(5.5);env._external_timer[nominal]=10000.
 # Independent draws, paired by task/seed at every policy step across conditions.
 raw_observations=env._get_observations;noise_gen=torch.Generator(device=dev).manual_seed(23001)
 ranges=torch.tensor([.01]+[.25]*3+[.05]*3+[.025]*6+[.5]*4+[1.]*2,device=dev)
 def paired_observations():
  obs=raw_observations();clean=env._encode()['policy'];sensor=torch.cat([env._gather(env._sensor_history,env._sensor_delay_ticks[:,i],lo,hi) for i,(lo,hi) in enumerate([(0,3),(3,6),(6,12),(12,18)])],-1)
  noise=torch.empty((small,19),device=dev).uniform_(-1,1,generator=noise_gen)[base_ids]*ranges
  noise[nominal]=0.;obs['policy']=clean.clone();obs['policy'][:,4:22]=sensor;obs['policy'][:,3:22]+=noise
  return obs
 env._get_observations=paired_observations
 # Keep native guard/root thresholds; gather reason masks before any reset.
 endpoint_cache={}
 done=env._get_dones;reason_counts={k:torch.zeros(n,device=dev,dtype=torch.long) for k in ('numerical','contact','orientation','closure','mimic','fall','timeout','other')};term_count=torch.zeros(n,device=dev,dtype=torch.long)
 peak_qd=torch.zeros(6,device=dev);peak_closure=torch.zeros(n,device=dev);envelope_violation=torch.zeros(6,device=dev);first_fail=[]
 orig_apply=env._apply_action
 def traced_apply():
  orig_apply()
  vel=tensor(env.robot.data.joint_vel)[:,env.active_ids];tau=getattr(env,'applied_motor_torque',env.torque)
  stall=vel.new_tensor([53.333333333333336]*4+[28.18525375641699]*2);no=vel.new_tensor([16.755160819145562]*4+[55.35573187814664]*2);peak=vel.new_tensor([40.]*4+[5.775909774436091]*2)
  hi=(stall*(1-vel/no)).clamp_min(0).minimum(peak);lo=(-stall*(1+vel/no)).clamp_max(0).maximum(-peak)
  envelope_violation.copy_(torch.maximum(envelope_violation,torch.maximum(tau-hi,lo-tau).clamp_min(0).amax(0)))
 env._apply_action=traced_apply
 def traced_done():
  term,timeout=done();r=env.reward;d=env.view.data
  contact=torch.linalg.vector_norm(r.contact_sensor.data.net_forces_w[:,r._reset_contact_link_idx],dim=-1).amax(-1)>1.
  rpy=euler_xyz_from_quat(d.root_quat_w);orient=(rpy[0].abs()>float(getattr(r.cfg,'termination_roll_deg',40.))*np.pi/180)|(rpy[1].abs()>float(getattr(r.cfg,'termination_pitch_deg',40.))*np.pi/180)
  masks=dict(numerical=env.numeric,contact=contact,orientation=orient,closure=env.closure_reset,mimic=env.mimic_reset,fall=env.fall_reset,timeout=timeout)
  endpoint_cache['value']=torch.stack((d.root_lin_vel_b[:,0],rpy[1],d.root_ang_vel_b[:,2],env._height_observation()),-1).clone()
  wheel_pos=tensor(env.robot.data.body_pos_w)[:,wheel_body_ids,:]
  wheel_vel=tensor(env.robot.data.body_lin_vel_w)[:,wheel_body_ids,:]
  active_vel=tensor(env.robot.data.joint_vel)[:,env.active_ids]
  tau=env.applied_motor_torque
  rot=rpy[2]
  endpoint_cache['rich']=torch.cat((d.root_pos_w,rot[:,None],d.root_lin_vel_b[:,2:3],wheel_pos.reshape(n,6),wheel_vel.reshape(n,6),active_vel[:,4:],tau[:,4:],env.motor_raw_pd_effort[:,4:],env.actions[:,4:]),-1).clone()
  endpoint_cache['terminated']=term.clone();endpoint_cache['timeout']=timeout.clone()
  known=torch.zeros_like(term)
  for k,mask in masks.items():reason_counts[k].add_((mask&(term|timeout)).long());known|=mask
  reason_counts['other'].add_((term&~known).long());term_count.add_(term.long());peak_qd.copy_(torch.maximum(peak_qd,tensor(env.robot.data.joint_vel)[:,env.active_ids].abs().amax(0)));peak_closure.copy_(torch.maximum(peak_closure,env.closure_error))
  if len(first_fail)<16:
   for idx in term.nonzero().flatten()[:16-len(first_fail)].tolist():first_fail.append(dict(env=idx,episode_step=int(env.episode_length_buf[idx]),reasons=[k for k,m in masks.items() if bool(m[idx])],joint_vel=tensor(env.robot.data.joint_vel)[idx,env.active_ids].tolist(),closure_m=float(env.closure_error[idx])))
  return term,timeout
 env._get_dones=traced_done
 env.scene.write_data_to_sim();env.scene.update(dt=0.)
 actors={};hashes={}
 for label,path in models.items():
  digest=hashlib.sha256(Path(path).read_bytes()).hexdigest();data=torch.load(path,map_location=dev,weights_only=False)
  if 'actor_state_dict' in data:state=data['actor_state_dict'];prefix='mlp.'
  else:state=data['model_state_dict'];prefix='actor.'
  dims=[state[prefix+'0.weight'].shape[1]]+[state[f'{prefix}{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
  assert dims[0]==35 and dims[-1]==6
  assert digest==plan['models_sha256'][label]
  for i in range(4):
   layers.append(torch.nn.Linear(dims[i],dims[i+1]));
   if i<3:layers.append(torch.nn.ELU())
  actor=torch.nn.Sequential(*layers).to(dev);actor.load_state_dict({k[len(prefix):]:v for k,v in state.items() if k.startswith(prefix)});actor.eval();actors[label]=actor;hashes[label]=digest
 assert hashes['parent']==plan['parent_sha256']
 mass_read=tensor(env.robot.root_view.get_masses()).to(dev);inertia_read=tensor(env.robot.root_view.get_inertias()).to(dev)
 material_write_read_error=float((tensor(env.robot.root_view.get_material_properties()).cpu()-materials).abs().max())
 mass_readback=dict(mass_write_read_error_kg=float((mass_read-masses).abs().max()),inertia_write_read_error=float((inertia_read-inertias).abs().max()))
 inputdr=dict(materials=materials.tolist(),material_shapes=dr.material_shapes,material_buckets={k:v.tolist() for k,v in dr.material_buckets.items()},effort_scale=dr.effort_scale.cpu().tolist(),body_names=list(env.robot.body_names),body_mass_scale=dr.body_mass_scale.cpu().tolist(),total_mass_scale=dr.total_mass_scale.cpu().tolist(),mass=masses.cpu().tolist(),com=coms[:,dr.base_id,:3].cpu().tolist(),friction=fr.cpu().tolist(),leg_gain=dr.leg_gain_scale.cpu().tolist(),wheel_gain=dr.wheel_gain_scale.cpu().tolist(),kp_scale=dr.kp_scale.cpu().tolist(),kd_scale=dr.kd_scale.cpu().tolist(),native_damping=native_damping.cpu().tolist(),action_delay_ticks=env._action_delay_ticks.cpu().tolist(),sensor_delay_ticks=env._sensor_delay_ticks.cpu().tolist())
 damping_readback=float((tensor(env.robot.root_view.get_dof_dampings()).to(dev)-native_damping).abs().max())
 readfr=tensor(env.robot.root_view.get_dof_friction_properties()).to(dev);friction_readback=dict(max_write_read_error=float((readfr-fr).abs().max()),leg_static_mean=float(readfr[~nominal][:,dr.leg_active_joint_ids,0].mean()),wheel_static_mean=float(readfr[~nominal][:,dr.wheel_joint_ids,0].mean()),passive_static_mean=float(readfr[~nominal][:,dr.passive_joint_ids,0].mean()))
 # Use common random numbers for physics torque noise and the scheduled 5.5s wrench.
 torque_rng=torch.Generator(device=dev).manual_seed(23002)
 wrench_rng=torch.Generator(device=dev).manual_seed(23003)
 paired_wrench_force=torch.empty((small,3),device=dev).uniform_(-10.,10.,generator=wrench_rng)[base_ids]
 paired_wrench_torque=torch.empty((small,3),device=dev).uniform_(-1.,1.,generator=wrench_rng)[base_ids]
 paired_wrench_force[nominal]=0.;paired_wrench_torque[nominal]=0.
 original_randn_like=torch.randn_like
 def paired_randn_like(value,*args,**kwargs):
  if value is env.torque:
   return torch.randn((small,6),device=dev,generator=torque_rng)[base_ids]
  return original_randn_like(value,*args,**kwargs)
 torch.randn_like=paired_randn_like
 def paired_update_external_wrench():
  env._external_timer-=env._control_dt
  env._external_hold.sub_(1).clamp_(min=0)
  event=env._external_timer<=0.
  if bool(event.any()):
   env._external_timer[event]=10000.
   env._external_force[event]=paired_wrench_force[event]
   env._external_torque[event]=paired_wrench_torque[event]
   env._external_hold[event]=10
  active=env._external_hold>0
  env._external_force[~active]=0.;env._external_torque[~active]=0.
  env.robot.set_external_force_and_torque(env._external_force[:,None,:],env._external_torque[:,None,:],env_ids=torch.arange(n,device=dev),body_ids=[dr.base_id])
 env._update_external_wrench=paired_update_external_wrench
 # Schedule the native interval event at 6s with common random XY deltas for each model.
 push_gen=torch.Generator(device=dev).manual_seed(23004)
 push_delta=torch.empty((small,6),device=dev).uniform_(-.25,.25,generator=push_gen)[base_ids]
 push_delta[:,2:]=0.;push_delta[nominal]=0.
 env.velocity_push_time_left.fill_(6.);env.velocity_push_time_left[nominal]=10000.
 cfg_event=env.event_manager._mode_term_cfgs['interval'][0]
 native_push=cfg_event.func
 def paired_native_push(environment,env_ids,velocity_range,asset_cfg):
  from isaaclab.utils import math as math_utils
  original_sample=math_utils.sample_uniform
  def paired_sample(lower,upper,size,device):return push_delta[env_ids].clone()
  math_utils.sample_uniform=paired_sample
  try:native_push(environment,env_ids,velocity_range,asset_cfg)
  finally:math_utils.sample_uniform=original_sample
  environment.velocity_push_time_left[env_ids]=10000.
 cfg_event.func=paired_native_push
 trajectory=[];action_error=0.;start=time.time();pre_push_term_count=None
 alive=torch.ones(n,device=dev,dtype=torch.bool);success=torch.zeros_like(alive);first_terminal_failure=torch.zeros_like(alive);first_boundary_timeout=torch.zeros_like(alive);net_progress=torch.zeros(n,device=dev);peak_signed=torch.zeros(n,device=dev);signed_direction=commands[:,0].sign()
 rich_trace=[];rough_trace=[];endpoint_trace=[];alive_before_trace=[];terminal_trace=[];timeout_trace=[];clip_hits=torch.zeros((len(models),6),device=dev,dtype=torch.long);action_samples=0
 cross_tick=torch.full((n,),-1,device=dev,dtype=torch.long)
 settle_run=torch.zeros(n,device=dev,dtype=torch.long);recovery_tick=torch.full_like(cross_tick,-1)
 with torch.inference_mode():
  obs=env._get_observations()
  for step in range(250):
   issued=torch.cat([actor(obs['policy'][i*len(variants)*small:(i+1)*len(variants)*small]) for i,actor in enumerate(actors.values())],0)
   assert bool(torch.isfinite(issued).all()),'nonfinite actor output'
   clip_hits.add_((issued.abs()>6).reshape(len(models),-1,6).sum(1));action_samples+=issued.shape[0]//len(models)
   alive_before_trace.append(alive.clone());actions=issued.clamp(-6,6);raw,reward,term,timeout,_=env.step(actions);command();obs=raw
   rich_trace.append(endpoint_cache['rich']);endpoint_trace.append(endpoint_cache['value']);terminal_trace.append(endpoint_cache['terminated']);timeout_trace.append(endpoint_cache['timeout'])
   action_error=max(action_error,float((raw['policy'][:,22:28]-env._encode()['policy'][:,22:28]).abs().max()))
   first_terminal_failure|=alive&term
   first_boundary_timeout|=alive&timeout
   alive&=~(term|timeout)
   delta_x=(env.view.data.root_pos_w[:,0]-initial_positions[:,0])*signed_direction
   net_progress=torch.where(alive,delta_x,net_progress)
   peak_signed=torch.maximum(peak_signed,torch.where(alive,delta_x,torch.zeros_like(delta_x)))
   ground=env.reward.ground_z_est
   ground_min=torch.where(alive,torch.minimum(ground_min,ground),ground_min)
   ground_max=torch.where(alive,torch.maximum(ground_max,ground),ground_max)
   wheel_x=tensor(env.robot.data.body_pos_w)[:,wheel_body_ids,0]
   wheel_progress=(wheel_x-initial_positions[:,0:1])*signed_direction[:,None]
   crossed=alive&(delta_x>=target_distance)&((ground_max-ground_min)>=.003)&((~mid)|(wheel_progress.amin(-1)>=clearance_distance))
   first_cross=crossed&(cross_tick<0);cross_tick[first_cross]=step
   success|=crossed
   recovering=alive&(cross_tick>=0)&((env.view.data.root_lin_vel_b[:,0]-commands[:,0]).abs()<=.20)
   settle_run=torch.where(recovering,settle_run+1,torch.zeros_like(settle_run))
   recovered=(settle_run>=25)&(recovery_tick<0);recovery_tick[recovered]=step-24
   rough_trace.append(torch.stack((delta_x,ground,alive.float()),-1).clone())
   if step==298:pre_push_term_count=term_count.clone()
   d=env.view.data;trajectory.append(torch.cat((d.root_lin_vel_b[:,:1],d.root_ang_vel_b[:,2:3],env._height_observation()[:,None]),-1).clone())
   if step%40==0:(out/'PROGRESS.json').write_text(json.dumps(dict(step=step,elapsed=time.time()-start,numerical=int(reason_counts['numerical'].sum()))))
  traj=torch.stack(trajectory);rough_values=torch.stack(rough_trace)
  rows=[]
  values=torch.stack(trajectory)[180:299].mean(0)
  for mi,model in enumerate(models):
   for vi,var in enumerate(variants):
    for ti,(name,vx,wz,h,_,_) in enumerate(TASKS):
     begin=mi*len(variants)*small+vi*small+ti*per;sl=slice(begin,begin+per)
     rec=[float((recovery_tick[k]-cross_tick[k])*.02) if int(recovery_tick[k])>=0 else None for k in range(begin,begin+per)]
     after=torch.arange(250,device=dev)[:,None]>=cross_tick[sl][None,:]
     valid=(cross_tick[sl]>=0)[None,:]&after&(rough_values[:,sl,2]>0)
     total_samples=int(valid.sum());after_mae=float(((traj[:,sl,0]-vx).abs()*valid).sum()/max(total_samples,1)) if total_samples else None
     rows.append(dict(model=model,variant=var,task=name,family=FAMILIES[ti//2],level=a.level,direction=vx,requested=per,required_clearance_distance_m=clearance_distance[sl].tolist(),path_cumulative_height_change_m=cumulative_change[sl,-1].tolist(),post_cross_recovered_count=sum(v is not None for v in rec),post_cross_recovery_s=rec,post_cross_forward_MAE=after_mae,post_cross_eligible_samples=total_samples,crossed_count=int(success[sl].sum()),completed_without_termination=int((term_count[sl]==0).sum()),net_progress_mean=float(net_progress[sl].mean()),peak_signed_progress_mean=float(peak_signed[sl].mean()),first_episode_terminal_failures=int(first_terminal_failure[sl].sum()),first_episode_timeouts=int(first_boundary_timeout[sl].sum()),per_env_crossed=success[sl].cpu().tolist(),per_env_net_progress=net_progress[sl].cpu().tolist(),per_env_ground_variation=(ground_max-ground_min)[sl].cpu().tolist(),pre_push_mean_velocity_yaw_height=values[sl].mean(0).tolist(),resets=int(term_count[sl].sum()),reasons={k:int(v[sl].sum()) for k,v in reason_counts.items()},max_closure_m=float(peak_closure[sl].max())))
  torch.randn_like=original_randn_like
 endpoints=torch.stack(endpoint_trace);alive_before=torch.stack(alive_before_trace);end_term=torch.stack(terminal_trace);end_timeout=torch.stack(timeout_trace)
 body_vx=endpoints[:,:,0];pitch=endpoints[:,:,1];horizontal_vx=body_vx*torch.cos(pitch);ticks=(torch.arange(250,device=dev)+1)*.02
 finite=torch.isfinite(endpoints).all(-1)
 def metrics(velocity,sl,start_s,end_s):
  valid=alive_before[:,sl]&finite[:,sl]&(ticks[:,None]>=start_s)&(ticks[:,None]<=end_s)
  error=velocity[:,sl]-commands[sl,0][None,:];directional=error*commands[sl,0].sign()[None,:];counts=valid.sum(0);eligible=counts>0;err=error[valid];signed=directional[valid]
  completed=alive_before[min(249,round(end_s/.02)-1),sl]&(~end_term[min(249,round(end_s/.02)-1),sl])&(~end_timeout[min(249,round(end_s/.02)-1),sl])
  if not len(err):return dict(samples=0,eligible_envs=0,completed_window_count=int(completed.sum()))
  per_mae=(error.abs()*valid).sum(0)/counts.clamp_min(1)
  return dict(samples=len(err),eligible_envs=int(eligible.sum()),completed_window_count=int(completed.sum()),MAE=float(err.abs().mean()),RMSE=float(err.square().mean().sqrt()),bias_actual_minus_command=float(err.mean()),directional_bias_positive_overspeed=float(signed.mean()),P95_abs=float(torch.quantile(err.abs(),.95)),overspeed_gt_0p2_fraction=float((signed>.2).float().mean()),underspeed_gt_0p2_fraction=float((signed<-.2).float().mean()),within_0p2_fraction=float((signed.abs()<=.2).float().mean()),equal_env_MAE=float(per_mae[eligible].mean()),mean_velocity=float(velocity[:,sl][valid].mean()),per_env_MAE=[float(per_mae[k]) if bool(eligible[k]) else None for k in range(len(counts))])
 speed_rows=[]
 for mi,model in enumerate(models):
  for vi,var in enumerate(variants):
   begin=mi*len(variants)*small+vi*small
   groups=[('all',slice(begin,begin+small))]+[(task[0],slice(begin+ti*per,begin+(ti+1)*per)) for ti,task in enumerate(TASKS)]
   for task,sl in groups:
    first_end=torch.where(end_term[:,sl]|end_timeout[:,sl],ticks[:,None],torch.full_like(ticks[:,None].expand(-1,len(ids[sl])),20.)).amin(0)
    row=dict(model=model,variant=var,task=task,level=a.level,requested=len(ids[sl]),first_episode_duration_mean_s=float(first_end.mean()),first_episode_duration_min_s=float(first_end.min()),first_terminal_failures=int(first_terminal_failure[sl].sum()),first_timeouts=int(first_boundary_timeout[sl].sum()),resets=int(term_count[sl].sum()),numerical_resets=int(reason_counts['numerical'][sl].sum()))
    for title,t0,t1 in [('steady_pre_push',.5,3.),('first_episode_after_start',.5,5.)]:
     row[title]={'body_vx':metrics(body_vx,sl,t0,t1),'scut_horizontal_vx':metrics(horizontal_vx,sl,t0,t1)}
    speed_rows.append(row)
 (out/'SPEED_RESULT.json').write_text(json.dumps(dict(protocol='frozen firstepisode 5s paired DR ablations; startup0.5..3s includes acceleration; initial_root_vx intervention is not a physically warmed policy; horizontal=bodyvx*cos(pitch)',rows=speed_rows,action_clip_hits=clip_hits.cpu().tolist(),action_samples_per_model=action_samples,input_sha256=hashes),ensure_ascii=False,indent=2)+'\n')
 result=dict(version=a.version,protocol='5s frozen MOD4 first-episode paired DR ablations, body-only initial vx intervention; no optimizer; excludes scheduled wrench/push; preserve original fullDR baseline',terrain_level=a.level,input_sha256=hashes,parent_sha256=plan['parent_sha256'],num_envs=n,rows=rows,first_failures=first_fail,physics_dt=float(env.cfg.sim.dt),delay=env.physical_delay_summary(),motor_envelope_violation_nm=envelope_violation.tolist(),action_slot_max_error=action_error,no_optimizer_constructed=True,wall_seconds=time.time()-start)
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(out/'INITIAL_DR.json').write_text(json.dumps(inputdr))
 np.savez_compressed(out/'trajectory.npz',values=torch.stack(trajectory).cpu().numpy(),rough_values=torch.stack(rough_trace).cpu().numpy(),path_profile_height=profile_height.cpu().numpy(),path_profile_distance=profile_distance.cpu().numpy(),endpoints=endpoints.cpu().numpy(),alive_before=alive_before.cpu().numpy(),terminated=end_term.cpu().numpy(),timeouts=end_timeout.cpu().numpy(),commands=commands.cpu().numpy(),rich=torch.stack(rich_trace).cpu().numpy())
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
