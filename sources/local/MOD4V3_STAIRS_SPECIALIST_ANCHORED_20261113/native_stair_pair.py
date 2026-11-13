"""Frozen parent/teacher native stair comparison with the project's existing paired-DR fixture."""
from pathlib import Path
import os,sys,json,argparse,hashlib,time,traceback,math
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--support',required=True);p.add_argument('--models',required=True);p.add_argument('--out',required=True);a=p.parse_args()
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
 from mod4v3_ppo_v1.continuous_stair_env import ContinuousStairEnv
 from mod4v3_ppo_v1.sampling import Sampling
 from isaaclab.utils.math import quat_from_euler_xyz
 from tensordict import TensorDict
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 models=json.loads(Path(a.models).read_text());assert list(models)==['parent','teacher']
 variants=['nominal0','fullDR'];tasks=[(angle,side,speed) for angle in [0.,-15.,15.,-30.,30.] for side in [-1.,1.] for speed in [1.8,2.2]]
 per=5;small=len(tasks)*per;n=small*len(variants)*len(models);dev='cuda:0'
 ids=torch.arange(n,device=dev);base_ids=torch.arange(small,device=dev).repeat(len(variants)*len(models));nominal=(ids//small)%len(variants)==0
 # Sample source entries from genuinely fullDR startup slots, excluding the training mixture's nominal modulo5 slots.
 source_ids=torch.div(torch.arange(small,device=dev),4,rounding_mode='floor')*5+torch.arange(small,device=dev)%4
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ContinuousStairEnv(configuration(meta,bank,n,66,terrain_selection='rough_scut_v1'),meta,bank);env.render_enabled=False;env.reset();env.sample=Sampling(env)
 dr=env.full_dr;nominal_com=dr.com_nominal.clone()
 def mirror(x):return x[source_ids[base_ids].to(x.device)].clone()
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
 dr.effort_scale.copy_(mirror(dr.effort_scale));dr.effort_scale[nominal]=1.

 dr.nominal_env_mask.copy_(nominal)
 env.terrain.terrain_levels.fill_(3)
 from rough_scut_v1_terrain import SPECIAL_START
 env.terrain.terrain_types[:]=SPECIAL_START+(base_ids//per)%20
 env.terrain.r1_offsets.zero_();center=env._center().clone();env.terrain.env_origins[:]=center;env.scene.env_origins[:]=center
 angles=torch.tensor([x[0] for x in tasks],device=dev).repeat_interleave(per)[base_ids]*math.pi/180.
 sides=torch.tensor([x[1] for x in tasks],device=dev).repeat_interleave(per)[base_ids]
 speeds=torch.tensor([x[2] for x in tasks],device=dev).repeat_interleave(per)[base_ids]
 distance=torch.tensor([3.90,3.75,3.60,3.99,3.80],device=dev)[base_ids%per]
 landing_y=torch.tensor([0.,-.08,.08,.04,-.04],device=dev)[base_ids%per]
 gen=torch.Generator(device=dev).manual_seed(6600);options=((env._bank_h>=.24)&(env._bank_h<=.272)).nonzero().flatten();pick=options[torch.randint(len(options),(small,),device=dev,generator=gen)][base_ids]
 q=env._bank_q[pick][:,env._bank_ids].clone();root=tensor(env.robot.data.default_root_state).clone();root[:,:3]=center
 root[:,0]+=sides*distance;root[:,1]+=landing_y+sides*(distance-1.1)*torch.tan(angles);root[:,2]=env._bank_h[pick]+.01
 yaw=torch.where(sides<0,0.,math.pi)+angles;root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw);root[:,7:]=0.
 env.robot.write_root_state_to_sim(root,env_ids=ids);env.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
 env.stair_up.fill_(True);env.stair_mid.zero_();env.stair_side.copy_(sides);env.stair_start.copy_(distance);env.stair_progress.zero_();env.stair_stage.zero_();env.stair_initial_stage.zero_();env.stair_first_time.fill_(-1.);env.stair_second_time.fill_(-1.);env.stair_goal_hold.zero_();env.lift_best.zero_();env.lift_armed.zero_()
 env.stair_height.fill_(.42);env.stair_speed.copy_(speeds);env.stair_approach_yaw.copy_(angles);env.stair_edge_contact_seen.zero_();env.stair_edge_contact_yaw.zero_()
 env.actions.zero_();env.torque.zero_();env.zero_torque_remaining.zero_();env.episode_length_buf.zero_();env._ground_command_until.zero_();env.r2_air_reset.zero_();env.command.zero_();env.height.fill_(.28);env.command_timer.fill_(10000.);env.heading_env.zero_();env.standing_env.zero_();env.reward.reset(ids);env.reward.ground_z_est.zero_();env.reward._invalidate_step_caches()
 env._execution_pending.fill_(True);env._sensor_pending.fill_(True);env._sensor_last_tick=-1
 env._action_delay_ticks.copy_(mirror(env._action_delay_ticks));env._sensor_delay_ticks.copy_(mirror(env._sensor_delay_ticks));env._action_delay_ticks[nominal]=0;env._sensor_delay_ticks[nominal]=0
 env._external_force.zero_();env._external_torque.zero_();env._external_hold.zero_();env._external_timer.fill_(5.5);env._external_timer[nominal]=10000.
 env.scene.write_data_to_sim();env.scene.update(dt=0.)
 inputdr=dict(mass=masses.cpu().tolist(),com=coms.cpu().tolist(),friction=fr.cpu().tolist(),materials=materials.tolist(),kp=dr.kp_scale.cpu().tolist(),kd=dr.kd_scale.cpu().tolist(),leg_gain=dr.leg_gain_scale.cpu().tolist(),wheel_gain=dr.wheel_gain_scale.cpu().tolist(),effort=dr.effort_scale.cpu().tolist(),action_delay=env._action_delay_ticks.cpu().tolist(),sensor_delay=env._sensor_delay_ticks.cpu().tolist(),root=root.cpu().tolist(),joint_pose=q.cpu().tolist(),source_slots=source_ids.cpu().tolist())
 # Independent draws, paired by task/seed at every policy step across conditions.
 raw_observations=env._get_observations;noise_gen=torch.Generator(device=dev).manual_seed(23001)
 ranges=torch.tensor([.01]+[.25]*3+[.05]*3+[.025]*6+[.5]*4+[1.]*2,device=dev)
 def paired_observations():
  obs=raw_observations();clean=env._encode()['policy'];sensor=torch.cat([env._gather(env._sensor_history,env._sensor_delay_ticks[:,i],lo,hi) for i,(lo,hi) in enumerate([(0,3),(3,6),(6,12),(12,18)])],-1)
  noise=torch.empty((small,19),device=dev).uniform_(-1,1,generator=noise_gen)[base_ids]*ranges
  noise[nominal]=0.;obs['policy']=clean.clone();obs['policy'][:,4:22]=sensor;obs['policy'][:,3:22]+=noise
  return obs
 env._get_observations=paired_observations
 actors={};hashes={}
 for label,path in models.items():
  digest=hashlib.sha256(Path(path).read_bytes()).hexdigest();data=torch.load(path,map_location=dev,weights_only=False);state=data['actor_state_dict'];dims=[state['mlp.0.weight'].shape[1]]+[state[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
  for i in range(4):
   layers.append(torch.nn.Linear(dims[i],dims[i+1]));
   if i<3:layers.append(torch.nn.ELU())
  actor=torch.nn.Sequential(*layers).to(dev);actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});actor.eval();actors[label]=actor;hashes[label]=digest
 assert hashes['parent']==plan['parent_sha256']
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

 started=time.time();finished=torch.zeros(n,device=dev,dtype=torch.bool);success=finished.clone();failed=finished.clone();timed_out=finished.clone();contact_seen=finished.clone();contact_yaw=torch.zeros(n,device=dev)
 first_time=torch.full((n,),-1.,device=dev);second_time=first_time.clone();completion_time=first_time.clone();closure_peak=torch.zeros(n,device=dev)
 sample_obs=[];sample_actions=[];sample_valid=[];sample_phase=[];trajectory=[];teacher_start=small*len(variants);teacher_ids=ids[teacher_start:]
 obs=env._get_observations()
 with torch.inference_mode():
  for step in range(1000):
   actions=torch.cat([actor(obs['policy'][i*len(variants)*small:(i+1)*len(variants)*small]) for i,actor in enumerate(actors.values())],0).clamp(-6,6)
   valid=(~finished[teacher_ids])&(env.episode_length_buf[teacher_ids]>=150)
   sample_obs.append(obs['policy'][teacher_ids].clone());sample_actions.append(actions[teacher_ids].clone());sample_valid.append(valid);sample_phase.append((env.stair_stage[teacher_ids]==1).clone())
   raw,reward,term,timeout,_=env.step(actions);active=~finished
   closure_peak=torch.maximum(closure_peak,env.closure_error)
   saw=active&env.stair_edge_contact_seen&(~contact_seen);contact_yaw[saw]=env.stair_edge_contact_yaw[saw];contact_seen|=saw
   first=active&(env.stair_first_time>=0)&(first_time<0);first_time[first]=env.stair_first_time[first]
   second=active&(env.stair_second_time>=0)&(second_time<0);second_time[second]=env.stair_second_time[second]
   completed=active&(env.stair_goal_hold>=.3)&(~term);success|=completed;completion_time[completed]=(step+1)*env.step_dt
   failed|=active&term;timed_out|=active&timeout&(~completed);finished|=completed|term|timeout;obs=raw
   if step%5==0:trajectory.append(torch.cat([env.view.data.root_pos_w,env.view.data.root_lin_vel_b,env.stair_stage[:,None].float(),finished[:,None].float(),success[:,None].float(),env.stair_edge_contact_yaw[:,None]],-1).cpu())
   if step%100==0 or bool(finished.all()):
    (out/'PROGRESS.json').write_text(json.dumps(dict(step=step+1,wall_seconds=time.time()-started,finished=int(finished.sum()),success=int(success.sum()),by_model={name:int(success[i*2*small:(i+1)*2*small].sum()) for i,name in enumerate(models)},done_totals=env.done_totals)))
   if bool(finished.all()):break
 rows=[]
 for mi,name in enumerate(models):
  for vi,variant in enumerate(variants):
   for ti,(angle,side,speed) in enumerate(tasks):
    begin=mi*2*small+vi*small+ti*per;sl=slice(begin,begin+per);interval=second_time[sl]-first_time[sl];eligible=success[sl]&(first_time[sl]>=0)&(second_time[sl]>=0)
    rows.append(dict(model=name,variant=variant,angle_deg=angle,side=side,speed=speed,requested=per,whole_two_step_passed=int(success[sl].sum()),near_edge_oblique_passed=int((success[sl]&contact_seen[sl]&(contact_yaw[sl].abs()>=math.pi/18.)).sum()),first_landed=int((first_time[sl]>=0).sum()),second_landed=int((second_time[sl]>=0).sum()),mean_first_to_second_s=float(interval[eligible].mean()) if bool(eligible.any()) else None,success=success[sl].cpu().tolist(),first_landing_s=first_time[sl].cpu().tolist(),second_landing_s=second_time[sl].cpu().tolist(),contact_seen=contact_seen[sl].cpu().tolist(),near_edge_contact_yaw_deg=(contact_yaw[sl]*180/math.pi).cpu().tolist(),terminal_failure=failed[sl].cpu().tolist(),timeout=timed_out[sl].cpu().tolist(),max_closure_m=float(closure_peak[sl].max())))
 summaries={}
 for name in models:
  summaries[name]={}
  for variant in variants:
   summaries[name][variant]={}
   for label,want_oblique in [('straight',False),('oblique',True)]:
    rr=[r for r in rows if r['model']==name and r['variant']==variant and ((r['angle_deg']!=0)==want_oblique)]
    summaries[name][variant][label]=dict(passed=sum(r['whole_two_step_passed'] for r in rr),requested=sum(r['requested'] for r in rr),near_edge_oblique_passed=sum(r['near_edge_oblique_passed'] for r in rr),first_landed=sum(r['first_landed'] for r in rr),second_landed=sum(r['second_landed'] for r in rr))
 valid=torch.stack(sample_valid)&success[teacher_ids][None,:];x=torch.stack(sample_obs)[valid].float().cpu().clone();y=torch.stack(sample_actions)[valid].float().cpu().clone();phase=torch.stack(sample_phase)[valid].cpu();frame=torch.arange(len(valid),device=dev)[:,None].expand_as(valid)[valid].cpu();env_id=teacher_ids[None,:].expand_as(valid)[valid].cpu()
 meta=dict(teacher_sha256=hashes['teacher'],collection='Frozen deterministic specialist, first episode only, successful whole two-step both-wheel landing+0.3s hold; actual executed clipped actions',native_successful_full=int(success[teacher_ids].sum()),native_successful_mid=0,success_DR=int((success[teacher_ids]&~nominal[teacher_ids]).sum()),success_nominal=int((success[teacher_ids]&nominal[teacher_ids]).sum()),observations=len(x),policy_dim=35,action_dim=6,no_optimizer_update=True,paired_fixed_protocol=True)
 if len(x):torch.save(dict(policy=x,actions=y,phase=phase,endpoint=frame,env_id=env_id,metadata=meta),out/'teacher_success_demos.pt')
 dataset=dict(meta,sha256=hashlib.sha256((out/'teacher_success_demos.pt').read_bytes()).hexdigest() if len(x) else None)
 result=dict(protocol='Native PhysX fixed weights;200mmx2;angles0/+-15/+-30, two faces, speeds1.8/2.2,five starts each;nominal/fullDR;first20s physical episode;paired initial mechanicalDR,pose,sensor/torque noise,wrench,push;original per-env guard; near-edge heading proxy distinct from exact MuJoCo side-face contact yaw',models=hashes,summaries=summaries,rows=rows,num_envs=n,steps=step+1,wall_seconds=time.time()-started,done_totals=env.done_totals,teacher_dataset=dataset,no_optimizer_constructed=True)
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(out/'INITIAL_DR.json').write_text(json.dumps(inputdr));np.savez_compressed(out/'trajectory.npz',values=torch.stack(trajectory).numpy())
 torch.randn_like=original_randn_like
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
