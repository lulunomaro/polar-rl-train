"""Paired fixed-weight Step7 repair check. No PPO or optimizer is constructed."""
from pathlib import Path
import argparse,base64,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--support',required=True);p.add_argument('--version',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],PHYSICAL_ACTION_DELAY_MIN_MS='0',PHYSICAL_ACTION_DELAY_MAX_MS='5',PHYSICAL_SENSOR_DELAY_MIN_MS='0',PHYSICAL_SENSOR_DELAY_MAX_MS='5',JOINT_FRICTION_SCALE='0.5',SPRING_DAMPING_FRACTION='0.25',EXTERNAL_DR_FRACTION='0.25',OBS_NOISE_FRACTION='0.25')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],a.support]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch,warp as wp,numpy as np
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_physical_delay_env import ScutFlatPhysicalDelayEnv
 from mod4v3_ppo_v1.physical_delay_checks import TASKS,_ground_start
 from mod4v3_ppo_v1.sampling import Sampling
 from mod4v1_scut.math_ops import euler_xyz_from_quat
 from isaaclab.utils.math import quat_from_euler_xyz
 from tensordict import TensorDict
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 variants=['random_training_commands'];per=4096;small=4096;n=4096;dev='cuda:0'
 ids=torch.arange(n,device=dev);base_ids=ids;nominal=torch.zeros(n,device=dev,dtype=torch.bool)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatPhysicalDelayEnv(configuration(meta,bank,n,66),meta,bank);env.render_enabled=False
 env.enforce_closure_reset=True
 dr=env.full_dr;nominal_com=tensor(env.robot.root_view.get_coms()).to(dev).clone()
 # guard-only baseline fix: same valid numeric selection in both versions.
 # The before support snapshot already carries this single isolated correction.
 env.reset();env.sample=Sampling(env)
 def mirror(x):return x[base_ids.to(x.device)].clone()
 masses=mirror(tensor(env.robot.root_view.get_masses()).to(dev));inertias=mirror(tensor(env.robot.root_view.get_inertias()).to(dev));coms=mirror(tensor(env.robot.root_view.get_coms()).to(dev));materials=mirror(tensor(env.robot.root_view.get_material_properties()).cpu())
 fr=tensor(env.robot.root_view.get_dof_friction_properties()).clone().to(dev)[base_ids]
 for target in (dr.leg_gain_scale,dr.wheel_gain_scale,dr.spring_damping_scale,dr.torque_noise_scale):target.copy_(mirror(target))
 masses[nominal]=dr.mass[nominal];inertias[nominal]=dr.inertia[nominal];coms[nominal]=nominal_com[nominal];materials[nominal.cpu()]=dr.materials[nominal.cpu()]
 dr.leg_gain_scale[nominal]=1.;dr.wheel_gain_scale[nominal]=1.;dr.spring_damping_scale[nominal]=1.;dr.torque_noise_scale[nominal]=0.
 fr[nominal,:,0]=dr.static_friction_default[nominal]
 fr[nominal,:,1]=(dr.dynamic_friction_default if dr.dynamic_friction_default is not None else dr.static_friction_default)[nominal]
 fr[nominal,:,2]=(dr.viscous_friction_default if dr.viscous_friction_default is not None else torch.zeros_like(dr.static_friction_default))[nominal]
 env.robot.set_masses_index(masses=masses,env_ids=ids);env.robot.set_inertias_index(inertias=inertias,env_ids=ids)
 env.robot.set_coms_index(coms=wp.from_torch(coms[:,[dr.base_id],:].contiguous(),dtype=wp.transformf),body_ids=[dr.base_id],env_ids=ids,full_data=False)
 env.robot.root_view.set_material_properties(wp.from_torch(materials.contiguous(),dtype=wp.float32),wp.from_torch(ids.to('cpu',torch.int32),dtype=wp.int32))
 env.robot.write_joint_friction_coefficient_to_sim(joint_friction_coeff=fr[:,:,0],joint_dynamic_friction_coeff=fr[:,:,1],joint_viscous_friction_coeff=fr[:,:,2],joint_ids=dr.joint_ids,env_ids=ids)
 env._external_force.zero_();env._external_torque.zero_();env._external_hold.zero_()
 # Exercise the inherited command/reset distribution at the original scale.
 # Independent draws, paired by task/seed at every policy step across conditions.
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
 digest=hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest();assert digest==plan['parent_sha256']
 data=torch.load(plan['parent'],map_location=dev,weights_only=False);state=data['actor_state_dict'];dims=[state['mlp.0.weight'].shape[1]]+[state[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
 for i in range(4):
  layers.append(torch.nn.Linear(dims[i],dims[i+1]));
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers).to(dev);actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});actor.eval()
 inputdr=dict(mass_factor_range=[float(dr.factor.min()),float(dr.factor.max())],leg_gain_range=[float(dr.leg_gain_scale.min()),float(dr.leg_gain_scale.max())],wheel_gain_range=[float(dr.wheel_gain_scale.min()),float(dr.wheel_gain_scale.max())],action_delay_values=env._action_delay_ticks.unique().tolist(),sensor_delay_values=env._sensor_delay_ticks.unique().tolist())
 readfr=tensor(env.robot.root_view.get_dof_friction_properties()).to(dev);friction_readback=dict(max_write_read_error=float((readfr-fr).abs().max()),leg_static_mean=float(readfr[~nominal][:,dr.leg_active_joint_ids,0].mean()),wheel_static_mean=float(readfr[~nominal][:,dr.wheel_joint_ids,0].mean()),passive_static_mean=float(readfr[~nominal][:,dr.passive_joint_ids,0].mean()))
 trajectory=[];action_error=0.;critic_errors={};start=time.time()
 with torch.inference_mode():
  obs=env._get_observations()
  for step in range(300):
   actions=actor(obs['policy']).clamp(-6,6);raw,reward,term,timeout,_=env.step(actions);obs=raw
   action_error=max(action_error,float((raw['policy'][:,22:28]-env._encode()['policy'][:,22:28]).abs().max()))
   assert raw['policy'].shape==(n,35) and raw['critic'].shape==(n,78)
   assert all(bool(torch.isfinite(x).all()) for x in raw.values()) and bool(torch.isfinite(reward).all())
   if step==0:
    from mod4v1_scut.config import observation_component
    from mod4v3_ppo_v1.physical_delay_checks import run_timing_probe
    critic=raw['critic'];checks={'mass':(critic[:,71:72],observation_component(env.reward.cfg,'body_mass_scale',dr.factor[:,None],'critic')),'sensor_delay':(critic[:,57:61],env._sensor_delay_ticks*(env._delay_dt/.005)),'action_delay':(critic[:,61:63],env._action_delay_ticks*(env._delay_dt/.005)),'wheel_damping':(critic[:,49:51],.6*dr.wheel_gain_scale)}
    critic_errors={key:float((x-y).abs().max()) for key,(x,y) in checks.items()};assert max(critic_errors.values())<1e-6,critic_errors
   d=env.view.data;trajectory.append(torch.cat((d.root_lin_vel_b[:,:1],d.root_ang_vel_b[:,2:3],env._height_observation()[:,None]),-1).clone())
   if step%40==0:(out/'PROGRESS.json').write_text(json.dumps(dict(step=step,elapsed=time.time()-start,numerical=int(reason_counts['numerical'].sum()))))
  values=torch.stack(trajectory)[180:].mean(0);rows=[]
  rows=[dict(variant='random_training_commands',num_envs=n,termination_events=int(term_count.sum()),unique_envs_terminated=int((term_count>0).sum()),reasons={k:int(v.sum()) for k,v in reason_counts.items()},max_closure_m=float(peak_closure.max()),tail_mean=values.mean(0).tolist())]
  # Reset-only readback verifies lifetime bugs without another simulated rollout.
  com_nom=(dr.com_nominal.clone() if hasattr(dr,'com_nominal') else nominal_com)
  for _ in range(32):dr(env,ids)
  comread=tensor(env.robot.root_view.get_coms()).to(dev);com_offset=(comread[:,dr.base_id,:3]-com_nom[:,dr.base_id,:3]).abs().amax(0)
  env._external_timer.fill_(10000.);env._external_hold.zero_();env._external_hold[0]=10;env._external_force.zero_();env._external_force[0,0]=1.;env._external_torque.zero_();holds=[]
  for _ in range(12):env._update_external_wrench();holds.append(int(env._external_hold[0]))
  env.zero_torque_remaining[:4]=2;env._sim_step_counter=1;env._apply_action();release=float(getattr(env,'applied_motor_torque',env.torque)[:4].abs().max())
  timing=run_timing_probe(env)
 result=dict(version=a.version,critic_checks_max_error=critic_errors,timing_probe=timing,protocol='fixed parent; repaired environment; inherited random commands/resets; 4096 envs x300 steps; closure2mm',parent_sha256=digest,parent_iteration=data.get('iter'),num_envs=n,rows=rows,first_failures=first_fail,physics_dt=float(env.cfg.sim.dt),delay=env.physical_delay_summary(),joint_names=env.order,true_active_velocity_peak=peak_qd.tolist(),motor_envelope_violation_nm=envelope_violation.tolist(),action_slot_max_error=action_error,friction_readback=friction_readback,after_32_resets_com_offset_abs_m=com_offset.tolist(),external_hold_after_12_calls=holds,zero_torque_release_abs_nm=release,no_optimizer_constructed=True,wall_seconds=time.time()-start)
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(out/'INITIAL_DR.json').write_text(json.dumps(inputdr))
 np.savez_compressed(out/'trajectory.npz',values=torch.stack(trajectory).cpu().numpy())
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
