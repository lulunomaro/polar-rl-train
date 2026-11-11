"""Paired frozen-weight R2 landing: plane/tiny grid,5/10cm,4commands,10starts. No optimizer."""
from pathlib import Path
import argparse,base64,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--support',required=True);p.add_argument('--version',required=True);p.add_argument('--models',required=True);p.add_argument('--model-ids',required=True);a=p.parse_args()
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
 TASKS=[(f"{family}__drop{int(drop*100):02d}_{label}",vx,wz,.28,drop,None) for family in ('plane_for_rm_rot','tiny_step_rot') for drop in (.05,.10) for label,vx,wz in [('stand',0.,0.),('forward',.9,0.),('backward',-1.,0.),('turn',0.,1.2)]]
 from mod4v3_ppo_v1.sampling import Sampling
 from mod4v1_scut.math_ops import euler_xyz_from_quat
 from isaaclab.utils.math import quat_from_euler_xyz
 from tensordict import TensorDict
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 all_models=json.loads(Path(a.models).read_text());models={key:all_models[key] for key in a.model_ids.split(',')};assert len(models)==3,'Fixed3model batches keep identical startup DR draws';variants=['nominal0','Step7_all_remaining_DR'];per=10;small=len(TASKS)*per;n=small*len(variants)*len(models);dev='cuda:0'
 ids=torch.arange(n,device=dev);base_ids=torch.arange(small,device=dev).repeat(len(variants)*len(models));nominal=(ids//small)%len(variants)==0
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatPhysicalDelayEnv(configuration(meta,bank,n,66,terrain_selection='rough_r1'),meta,bank);env.render_enabled=False
 env.enforce_closure_reset=True
 dr=env.full_dr;nominal_com=dr.com_nominal.clone()
 # Fixed type/level/offset/initial states are paired across every model and condition.
 family_id=torch.tensor([FAMILIES.index(t[0].split('__')[0]) for t in TASKS],device=dev).repeat_interleave(per)
 family_cols=[];offset=0
 for count in COUNTS:
  family_cols.append(offset);offset+=count
 env.terrain=env.scene['terrain']
 env.terrain.terrain_types[:]=torch.tensor(family_cols,device=dev)[family_id[base_ids]]
 env.terrain.terrain_levels.zero_()
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
 root[:,2]+=torch.tensor([t[4] for t in TASKS],device=dev).repeat_interleave(per)[base_ids]
 root[:,3:7]=quat_from_euler_xyz(uniform(-.03,.03),uniform(-.03,.03),uniform(-3.14159,3.14159));root[:,7:]=0.;root[:,7]=uniform(-.1,.1);root[:,8]=uniform(-.1,.1)
 env.robot.write_root_state_to_sim(root,env_ids=ids);env.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
 env.actions.zero_();env.torque.zero_();env.zero_torque_remaining.zero_();env.episode_length_buf.zero_();env.reward.reset(ids);env.reward._invalidate_step_caches()
 initial_positions=root[:,:3].clone()
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
  digest=hashlib.sha256(Path(path).read_bytes()).hexdigest();data=torch.load(path,map_location=dev,weights_only=False);state=data['actor_state_dict'];dims=[state['mlp.0.weight'].shape[1]]+[state[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
  for i in range(4):
   layers.append(torch.nn.Linear(dims[i],dims[i+1]));
   if i<3:layers.append(torch.nn.ELU())
  actor=torch.nn.Sequential(*layers).to(dev);actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});actor.eval();actors[label]=actor;hashes[label]=digest
 assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan['parent_sha256']
 mass_read=tensor(env.robot.root_view.get_masses()).to(dev);inertia_read=tensor(env.robot.root_view.get_inertias()).to(dev)
 material_write_read_error=float((tensor(env.robot.root_view.get_material_properties()).cpu()-materials).abs().max())
 mass_readback=dict(mass_write_read_error_kg=float((mass_read-masses).abs().max()),inertia_write_read_error=float((inertia_read-inertias).abs().max()))
 inputdr=dict(materials=materials.tolist(),material_shapes=dr.material_shapes,material_buckets={k:v.tolist() for k,v in dr.material_buckets.items()},effort_scale=dr.effort_scale.cpu().tolist(),body_names=list(env.robot.body_names),body_mass_scale=dr.body_mass_scale.cpu().tolist(),total_mass_scale=dr.total_mass_scale.cpu().tolist(),mass=masses.cpu().tolist(),com=coms[:,dr.base_id,:3].cpu().tolist(),friction=fr.cpu().tolist(),leg_gain=dr.leg_gain_scale.cpu().tolist(),wheel_gain=dr.wheel_gain_scale.cpu().tolist(),kp_scale=dr.kp_scale.cpu().tolist(),kd_scale=dr.kd_scale.cpu().tolist(),native_damping=native_damping.cpu().tolist(),action_delay_ticks=env._action_delay_ticks.cpu().tolist(),sensor_delay_ticks=env._sensor_delay_ticks.cpu().tolist())
 relative_root=root[:len(variants)*small].clone();relative_root[:,:3]-=env.scene.env_origins[:len(variants)*small]
 inputdr.update(initial_root_relative=relative_root.cpu().tolist(),initial_joint_position=q[:len(variants)*small].cpu().tolist(),initial_commands=commands[:len(variants)*small].cpu().tolist(),models=list(models),batch_envs=n)
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
 # First physical episode only: no credit after a guard/reset.
 alive=torch.ones(n,device=dev,dtype=torch.bool)
 cleared=torch.zeros_like(alive);landed=cleared.clone();recovered=cleared.clone();tracked=cleared.clone()
 contact_tick=torch.full((n,),-1,device=dev,dtype=torch.long)
 recovery_tick=contact_tick.clone();tracking_tick=contact_tick.clone()
 posture_run=torch.zeros(n,device=dev,dtype=torch.long);tracking_run=posture_run.clone()
 impact=torch.zeros(n,device=dev);first_closure=impact.clone()
 contact_clearance=torch.full((n,2),float('nan'),device=dev)
 landing_trace=[];trajectory=[];old_done=env._get_dones;tick=0
 survived2=alive.clone()
 def landing_done():
  term,timeout=old_done();r=env.reward;d=env.view.data
  gaps=d.body_pos_w[:,r._wheel_link_idx,2]-r.ground_wheels-.0625
  force=r._get_wheel_contact_force_peaks(r.contact_sensor.data.net_forces_w_history)
  airborne=alive&(gaps>.01).all(-1)&(force<1.).all(-1)
  cleared.logical_or_(airborne)
  touch=alive&cleared&~landed&(force>1.).any(-1)
  contact_tick[touch]=tick;contact_clearance[touch]=gaps[touch];landed.logical_or_(touch)
  impact.copy_(torch.maximum(impact,force.amax(-1)*(alive&landed&((tick-contact_tick)<=25))))
  roll,pitch,_=euler_xyz_from_quat(d.root_quat_w)
  stable=alive&landed&~term&(gaps.abs()<.025).all(-1)&(roll.abs()<.2)&(pitch.abs()<.2)&((env._height_observation()-heights).abs()<.05)
  posture_run.copy_(torch.where(stable,posture_run+1,0))
  new=~recovered&(posture_run>=25);recovery_tick[new]=tick-24;recovered.logical_or_(new)
  tracking=stable&((d.root_lin_vel_b[:,0]-commands[:,0]).abs()<.3)&((d.root_ang_vel_b[:,2]-commands[:,2]).abs()<.5)
  tracking_run.copy_(torch.where(tracking,tracking_run+1,0))
  new=~tracked&(tracking_run>=25);tracking_tick[new]=tick-24;tracked.logical_or_(new)
  first_closure.copy_(torch.maximum(first_closure,env.closure_error*alive))
  landing_trace.append(torch.stack((gaps[:,0],gaps[:,1],force[:,0],force[:,1],roll,pitch,(alive&~(term|timeout)).float(),landed.float()),-1).clone())
  trajectory.append(torch.cat((d.root_lin_vel_b[:,:1],d.root_ang_vel_b[:,2:3],env._height_observation()[:,None]),-1).clone())
  alive.logical_and_(~(term|timeout))
  return term,timeout
 env._get_dones=landing_done
 start=time.time();action_error=0.
 with torch.inference_mode():
  obs=env._get_observations()
  for tick in range(400):
   actions=torch.cat([actor(obs['policy'][i*len(variants)*small:(i+1)*len(variants)*small]) for i,actor in enumerate(actors.values())],0).clamp(-6,6)
   obs,reward,term,timeout,_=env.step(actions);command()
   action_error=max(action_error,float((obs['policy'][:,22:28]-env._encode()['policy'][:,22:28]).abs().max()))
   if tick==99:survived2=alive.clone()
   if tick%40==0:(out/'PROGRESS.json').write_text(json.dumps(dict(step=tick,elapsed=time.time()-start,numerical=int(reason_counts['numerical'].sum()))))
 torch.randn_like=original_randn_like
 rows=[];traj=torch.stack(trajectory);trace=torch.stack(landing_trace)
 for mi,model in enumerate(models):
  for vi,var in enumerate(variants):
   for ti,(name,vx,wz,h,drop,_) in enumerate(TASKS):
    begin=mi*len(variants)*small+vi*small+ti*per;sl=slice(begin,begin+per)
    impacts=impact[sl][landed[sl]]
    recovery_s=[float((recovery_tick[i]-contact_tick[i])*.02) if bool(recovered[i]) else None for i in range(begin,begin+per)]
    tracking_s=[float((tracking_tick[i]-contact_tick[i])*.02) if bool(tracked[i]) else None for i in range(begin,begin+per)]
    valid=trace[100:250,sl,6]>0
    count=int(valid.sum());mean_error=float(((traj[100:250,sl,0]-vx).abs()*valid).sum()/max(1,count)) if count else None
    rows.append(dict(model=model,variant=var,task=name,family=name.split('__')[0],drop_m=drop,command=[vx,wz,h],requested=per,cleared_count=int(cleared[sl].sum()),landed_count=int(landed[sl].sum()),posture_recovered_count=int(recovered[sl].sum()),command_recovered_count=int(tracked[sl].sum()),survived_first2s=int(survived2[sl].sum()),posture_recovery_s=recovery_s,command_recovery_s=tracking_s,first_contact_s=[float(x*.02) if x>=0 else None for x in contact_tick[sl].tolist()],landing_force_p95_n=float(torch.quantile(impacts,.95)) if len(impacts) else None,landing_force_peak_n=float(impacts.max()) if len(impacts) else None,pre_wrench_2to5s_forward_mae=mean_error,eligible_error_samples=count,first_episode_closed_loop_peak_m=float(first_closure[sl].max()),resets_over8s=int(term_count[sl].sum()),reason_events_over8s={k:int(v[sl].sum()) for k,v in reason_counts.items()}))
 result=dict(version=a.version,protocol='plane/tiny_step level0 x5/10cm extra drop xstand/forward/backward/turn x10starts; nominal/fullDR paired across models;400steps8s; first physical episode only,never count recovery afterreset; posture:nearwheels+-25mm/rollpitch<.2/height+-50mm for.5s; command:additionalvxerror<.3/wzerror<.5; diagnostic comparison,not added graduation gate',input_sha256=hashes,parent_sha256=plan['parent_sha256'],num_envs=n,rows=rows,first_failures=first_fail,physics_dt=float(env.cfg.sim.dt),delay=env.physical_delay_summary(),motor_envelope_violation_nm=envelope_violation.tolist(),action_slot_max_error=action_error,no_optimizer_constructed=True,wall_seconds=time.time()-start,reference='existing SCUT fixed-DR paired physics replay framework; project README R2 local-height reset')
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(out/'INITIAL_DR.json').write_text(json.dumps(inputdr))
 np.savez_compressed(out/'trajectory.npz',values=traj.cpu().numpy(),landing=trace.cpu().numpy(),contact_tick=contact_tick.cpu().numpy(),recovery_tick=recovery_tick.cpu().numpy(),tracking_tick=tracking_tick.cpu().numpy(),impact_n=impact.cpu().numpy(),first_closure_m=first_closure.cpu().numpy())

except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
