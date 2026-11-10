"""Paired frozen-weight Step7 mass and effort scale adaptation check. No optimizer."""
from pathlib import Path
import argparse,base64,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--support',required=True);p.add_argument('--version',required=True);p.add_argument('--models',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='0.5',SPRING_DAMPING_FRACTION='0.25',EXTERNAL_DR_FRACTION='0.25',OBS_NOISE_FRACTION='0.25')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],a.support]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch,warp as wp,numpy as np
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_material_env import ScutFlatMaterialEnv as ScutFlatPhysicalDelayEnv
 from mod4v3_ppo_v1.physical_delay_checks import TASKS,_ground_start
 TASKS=list(TASKS)+[("forward_2.7_diagnostic",2.7,0.0,.28,None,None)]
 from mod4v3_ppo_v1.sampling import Sampling
 from mod4v1_scut.math_ops import euler_xyz_from_quat
 from isaaclab.utils.math import quat_from_euler_xyz
 from tensordict import TensorDict
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 models=json.loads(Path(a.models).read_text());variants=['nominal0','Step7_DR_plus_bodymass_effort_material'];per=10;small=len(TASKS)*per;n=small*len(variants)*len(models);dev='cuda:0'
 ids=torch.arange(n,device=dev);base_ids=torch.arange(small,device=dev).repeat(len(variants)*len(models));nominal=(ids//small)%len(variants)==0
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatPhysicalDelayEnv(configuration(meta,bank,n,66),meta,bank);env.render_enabled=False
 env.enforce_closure_reset=True
 dr=env.full_dr;nominal_com=dr.com_nominal.clone()
 _ground_start(env,6600);env.sample=Sampling(env)
 def mirror(x):return x[base_ids.to(x.device)].clone()
 masses=mirror(tensor(env.robot.root_view.get_masses()).to(dev));inertias=mirror(tensor(env.robot.root_view.get_inertias()).to(dev));coms=mirror(tensor(env.robot.root_view.get_coms()).to(dev));materials=mirror(tensor(env.robot.root_view.get_material_properties()).cpu())
 fr=tensor(env.robot.root_view.get_dof_friction_properties()).clone().to(dev)[base_ids]
 for target in (dr.leg_gain_scale,dr.wheel_gain_scale,dr.spring_damping_scale,dr.torque_noise_scale,dr.body_mass_scale,dr.total_mass_scale,dr.factor):target.copy_(mirror(target))
 masses[nominal]=dr.mass[nominal];inertias[nominal]=dr.inertia[nominal];coms[nominal]=nominal_com[nominal];materials[nominal.cpu()]=dr.materials[nominal.cpu()]
 dr.body_mass_scale[nominal]=1.;dr.total_mass_scale[nominal]=1.;dr.factor[nominal]=1.
 dr.leg_gain_scale[nominal]=1.;dr.wheel_gain_scale[nominal]=1.;dr.spring_damping_scale[nominal]=1.;dr.torque_noise_scale[nominal]=0.
 fr[nominal,:,0]=dr.static_friction_default[nominal]
 fr[nominal,:,1]=(dr.dynamic_friction_default if dr.dynamic_friction_default is not None else dr.static_friction_default)[nominal]
 fr[nominal,:,2]=(dr.viscous_friction_default if dr.viscous_friction_default is not None else torch.zeros_like(dr.static_friction_default))[nominal]
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
 commands=torch.tensor([[vx,0.,wz] for _,vx,wz,_,_,_ in TASKS],device=dev).repeat_interleave(per,0).repeat(len(variants)*len(models),1)
 heights=torch.tensor([h for _,_,_,h,_,_ in TASKS],device=dev).repeat_interleave(per).repeat(len(variants)*len(models))
 def command():
  env.command.copy_(commands);env.height.copy_(heights);env.command_timer.fill_(10000.);env.heading_env.zero_();env.standing_env.zero_();env.reward.command.copy_(commands);env.reward.height_cmd.copy_(heights)
 command();env._execution_pending.fill_(True);env._sensor_pending.fill_(True);env._sensor_last_tick=-1
 env._action_delay_ticks.copy_(env._action_delay_ticks[base_ids]);env._sensor_delay_ticks.copy_(env._sensor_delay_ticks[base_ids]);env._action_delay_ticks[nominal]=0;env._sensor_delay_ticks[nominal]=0
 env._external_force.zero_();env._external_torque.zero_();env._external_hold.zero_();env._external_timer.fill_(5.5);env._external_timer[nominal]=10000.
 # Independent draws, paired by task/seed at every policy step across conditions.
 raw_observations=env._get_observations;noise_gen=torch.Generator(device=dev).manual_seed(23001)
 ranges=torch.tensor([.01]+[.25]*3+[.05]*3+[.025]*6+[.5]*4+[1.]*2,device=dev)*.25
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
 assert hashes['parent']==plan['parent_sha256']
 mass_read=tensor(env.robot.root_view.get_masses()).to(dev);inertia_read=tensor(env.robot.root_view.get_inertias()).to(dev)
 material_write_read_error=float((tensor(env.robot.root_view.get_material_properties()).cpu()-materials).abs().max())
 mass_readback=dict(mass_write_read_error_kg=float((mass_read-masses).abs().max()),inertia_write_read_error=float((inertia_read-inertias).abs().max()))
 inputdr=dict(materials=materials.tolist(),material_shapes=dr.material_shapes,material_buckets={k:v.tolist() for k,v in dr.material_buckets.items()},effort_scale=dr.effort_scale.cpu().tolist(),body_names=list(env.robot.body_names),body_mass_scale=dr.body_mass_scale.cpu().tolist(),total_mass_scale=dr.total_mass_scale.cpu().tolist(),mass=masses.cpu().tolist(),com=coms[:,dr.base_id,:3].cpu().tolist(),friction=fr.cpu().tolist(),leg_gain=dr.leg_gain_scale.cpu().tolist(),wheel_gain=dr.wheel_gain_scale.cpu().tolist(),action_delay_ticks=env._action_delay_ticks.cpu().tolist(),sensor_delay_ticks=env._sensor_delay_ticks.cpu().tolist())
 readfr=tensor(env.robot.root_view.get_dof_friction_properties()).to(dev);friction_readback=dict(max_write_read_error=float((readfr-fr).abs().max()),leg_static_mean=float(readfr[~nominal][:,dr.leg_active_joint_ids,0].mean()),wheel_static_mean=float(readfr[~nominal][:,dr.wheel_joint_ids,0].mean()),passive_static_mean=float(readfr[~nominal][:,dr.passive_joint_ids,0].mean()))
 # Use common random numbers for physics torque noise and the scheduled 5.5s wrench.
 torque_rng=torch.Generator(device=dev).manual_seed(23002)
 wrench_rng=torch.Generator(device=dev).manual_seed(23003)
 paired_wrench_force=torch.empty((small,3),device=dev).uniform_(-2.5,2.5,generator=wrench_rng)[base_ids]
 paired_wrench_torque=torch.empty((small,3),device=dev).uniform_(-.25,.25,generator=wrench_rng)[base_ids]
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
 trajectory=[];action_error=0.;start=time.time()
 with torch.inference_mode():
  obs=env._get_observations()
  for step in range(300):
   actions=torch.cat([actor(obs['policy'][i*len(variants)*small:(i+1)*len(variants)*small]) for i,actor in enumerate(actors.values())],0).clamp(-6,6);raw,reward,term,timeout,_=env.step(actions);command();obs=raw
   action_error=max(action_error,float((raw['policy'][:,22:28]-env._encode()['policy'][:,22:28]).abs().max()))
   d=env.view.data;trajectory.append(torch.cat((d.root_lin_vel_b[:,:1],d.root_ang_vel_b[:,2:3],env._height_observation()[:,None]),-1).clone())
   if step%40==0:(out/'PROGRESS.json').write_text(json.dumps(dict(step=step,elapsed=time.time()-start,numerical=int(reason_counts['numerical'].sum()))))
  values=torch.stack(trajectory)[180:].mean(0);rows=[]
  for mi,model in enumerate(models):
   for vi,var in enumerate(variants):
    for ti,(name,vx,wz,h,vlimit,wlimit) in enumerate(TASKS):
     begin=mi*len(variants)*small+vi*small+ti*per;sl=slice(begin,begin+per);vals=values[sl];err=(vals-vals.new_tensor([vx,wz,h])).abs();passed=term_count[sl]==0
     if vlimit is not None:passed&=err[:,0]<=vlimit
     if wlimit is not None:passed&=err[:,1]<=abs(wz)*wlimit
     if name.startswith('height'):passed&=err[:,2]<=.02
     rows.append(dict(model=model,variant=var,task=name,mean=vals.mean(0).tolist(),capability_gate=name not in ('combo_0.9_1.2','forward_2.7_diagnostic'),passed=int(passed.sum()) if name not in ('combo_0.9_1.2','forward_2.7_diagnostic') else None,requested=per,resets=int(term_count[sl].sum()),reasons={k:int(v[sl].sum()) for k,v in reason_counts.items()},per_env=vals.tolist(),max_closure_m=float(peak_closure[sl].max())))
  torch.randn_like=original_randn_like
  # Reset-only readback verifies lifetime bugs without another simulated rollout.
  com_nom=(dr.com_nominal.clone() if hasattr(dr,'com_nominal') else nominal_com)
  for _ in range(32):dr(env,ids)
  material_after32=tensor(env.robot.root_view.get_material_properties()).cpu()
  startup_material_reset_max_change=float((material_after32[:,dr.selected_material_shapes]-dr.startup_materials[:,dr.selected_material_shapes]).abs().max())
  comread=tensor(env.robot.root_view.get_coms()).to(dev);com_offset=(comread[:,dr.base_id,:3]-com_nom[:,dr.base_id,:3]).abs().amax(0)
  env._external_timer.fill_(10000.);env._external_hold.zero_();env._external_hold[0]=10;env._external_force.zero_();env._external_force[0,0]=1.;env._external_torque.zero_();holds=[]
  for _ in range(12):env._update_external_wrench();holds.append(int(env._external_hold[0]))
  saved_counter=env._sim_step_counter;env.zero_torque_remaining[:4]=2;env._sim_step_counter=1;env._apply_action();release=float(getattr(env,'applied_motor_torque',env.torque)[:4].abs().max());env._sim_step_counter=saved_counter
 result=dict(version=a.version,protocol='Frozen parent and five-minute material adaptation checkpoints; paired nominal0/Step7DRplusbodymass_effort_material; common properties/10initialstates/torquenoise/wrench;7originaltasks+2.7commanddiagnostic300steps/tail120; no optimizer',input_sha256=hashes,parent_sha256=plan['parent_sha256'],num_envs=n,rows=rows,first_failures=first_fail,physics_dt=float(env.cfg.sim.dt),delay=env.physical_delay_summary(),joint_names=env.order,true_active_velocity_peak=peak_qd.tolist(),motor_envelope_violation_nm=envelope_violation.tolist(),action_slot_max_error=action_error,selected_material_after32resets_max_change=startup_material_reset_max_change,mass_readback=mass_readback,contact_material_readback_max_error=material_write_read_error,friction_readback=friction_readback,after_32_resets_com_offset_abs_m=com_offset.tolist(),external_hold_after_12_calls=holds,zero_torque_release_abs_nm=release,no_optimizer_constructed=True,wall_seconds=time.time()-start)
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(out/'INITIAL_DR.json').write_text(json.dumps(inputdr))
 np.savez_compressed(out/'trajectory.npz',values=torch.stack(trajectory).cpu().numpy())
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
