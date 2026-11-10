"""Read back cumulative mass/output-scale DR and execute frozen-policy physics."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--num-envs',type=int,default=64);p.add_argument('--steps',type=int,default=80);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],JOINT_FRICTION_SCALE='0.5',SPRING_DAMPING_FRACTION='0.25',EXTERNAL_DR_FRACTION='0.25',OBS_NOISE_FRACTION='0.25',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_velocity_push_env import ScutFlatVelocityPushEnv as ScutFlatBodyMassEnv
 from mod4v3_ppo_v1.scut_flat_material_env import MATERIAL_GROUPS
 from mod4v3_ppo_v1.scut_flat_env import ScutFlatEnv
 from mod4v3_ppo_v1.physical_delay_checks import _ground_start
 from mod4v3_ppo_v1.sampling import Sampling
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatBodyMassEnv(configuration(meta,bank,a.num_envs,66),meta,bank);env.render_enabled=False
 dr=env.full_dr
 # Exercise the actual native interval event, including per-env selection and reset semantics.
 ids=torch.arange(env.num_envs,device=env.device);selected=ids[::2]
 before=tensor(env.robot.data.root_vel_w).clone();env.velocity_push_time_left.fill_(100.)
 env.velocity_push_time_left[selected]=.01
 env.event_manager.apply(mode="interval",dt=.02)
 after=tensor(env.robot.data.root_vel_w).clone();delta=after-before
 assert bool((env.velocity_push_count[selected]==1).all()) and bool((env.velocity_push_count[1::2]==0).all())
 assert bool((delta[selected,:2].abs()<=.25001).all()) and float(delta[selected,:2].abs().max())>.05
 assert float(delta[selected,2:].abs().max())==0. and float(delta[1::2].abs().max())==0.
 assert bool(((env.velocity_push_time_left[selected]>=5.)&(env.velocity_push_time_left[selected]<=10.)).all())
 timer_before=env.velocity_push_time_left.clone();env._reset_idx(selected)
 assert bool(((env.velocity_push_time_left[selected]>=5.)&(env.velocity_push_time_left[selected]<=10.)).all())
 assert torch.equal(env.velocity_push_time_left[1::2],timer_before[1::2])
 push_checks=dict(delta_xy_min=delta[selected,:2].amin(0).tolist(),delta_xy_max=delta[selected,:2].amax(0).tolist(),unchanged_z_angular=True,unselected_unchanged=True,per_env_interval=True,reset_resamples_selected_timer_only=True,function="target native push_by_setting_velocity",operation="add uniform world XY delta")
 material_initial=tensor(env.robot.root_view.get_material_properties()).clone().cpu()
 material_checks={}
 for group,spec in MATERIAL_GROUPS.items():
  shapes=dr.material_shapes[group];values=material_initial[:,shapes];buckets=dr.material_buckets[group]
  assert torch.equal(values,dr.startup_materials[:,shapes])
  assert torch.equal(values,buckets[dr.material_bucket_ids[group]])
  assert bool((values[...,1]<=values[...,0]).all())
  for col,bounds in enumerate(spec[1:4]):assert bool(((values[...,col]>=bounds[0])&(values[...,col]<=bounds[1])).all())
  material_checks[group]=dict(shapes=shapes,bodies=[env.robot.body_names[i] for i in dr.material_bodies[group]],bucket_count=len(buckets),actual_min=values.amin((0,1)).tolist(),actual_max=values.amax((0,1)).tolist(),unique_bucket_indices=int(dr.material_bucket_ids[group].unique().numel()))
 scale=dr.body_mass_scale.clone();expected_mass=dr.mass*scale;expected_inertia=dr.inertia*scale[...,None]
 def readback():
  return tensor(env.robot.root_view.get_masses()).to(env.device).clone(),tensor(env.robot.root_view.get_inertias()).to(env.device).clone()
 initial_mass,initial_inertia=readback();mass_error=float((initial_mass-expected_mass).abs().max());inertia_error=float((initial_inertia-expected_inertia).abs().max())
 assert mass_error<1e-5 and inertia_error<1e-6,(mass_error,inertia_error)
 ids=torch.arange(env.num_envs,device=env.device)
 for _ in range(8):dr(env,ids)
 material_after=tensor(env.robot.root_view.get_material_properties()).clone().cpu()
 material_reset_change=float((material_after[:,dr.selected_material_shapes]-material_initial[:,dr.selected_material_shapes]).abs().max())
 assert material_reset_change==0.
 obs_check=env._encode()
 from mod4v1_scut.config import observation_component
 expected_material_obs=observation_component(env.reward.cfg,"body_material",dr.wheel_material_values,"critic")
 critic_material_error=float((obs_check['critic'][:,72:78]-expected_material_obs).abs().max());assert critic_material_error<1e-6
 reset_mass,reset_inertia=readback();reset_mass_change=float((reset_mass-initial_mass).abs().max());reset_inertia_change=float((reset_inertia-initial_inertia).abs().max())
 (out/'RESET_READBACK.json').write_text(json.dumps(dict(mass_max_change=reset_mass_change,inertia_max_change=reset_inertia_change,initial_mass=initial_mass.cpu().tolist(),reset_mass=reset_mass.cpu().tolist(),initial_inertia=initial_inertia.cpu().tolist(),reset_inertia=reset_inertia.cpu().tolist(),expected_mass=expected_mass.cpu().tolist(),body_names=list(env.robot.body_names)),indent=2))
 assert reset_mass_change<1e-6 and reset_inertia_change<1e-7,(reset_mass_change,reset_inertia_change)
 checks={}
 for group,indices in dr.mass_groups.items():
  lo,hi=dr.mass_ranges[group];values=scale[:,indices];assert bool(((values>=lo)&(values<=hi)).all())
  checks[group]=dict(body_names=[env.robot.body_names[i] for i in indices],min=float(values.min()),max=float(values.max()))
 chosen=[i for ids_group in dr.mass_groups.values() for i in ids_group];unselected=[i for i in range(len(dr.mass_body_names)) if i not in chosen]
 assert bool((scale[:,unselected]==1).all())
 left=env.robot.body_names.index('left_front1_link');right=env.robot.body_names.index('right_front1_link')
 pair_abs_difference=(scale[:,left]-scale[:,right]).abs();assert float(pair_abs_difference.max())>.01
 # Verify reset cooldown, selected environment writes and independent actuator samples.
 initial_effort=dr.effort_scale.clone();initial_count=dr.effort_sample_count.clone()
 assert bool(((initial_effort[:,:4]>=.8)&(initial_effort[:,:4]<=1.1)).all())
 assert bool(((initial_effort[:,4:]>=.9)&(initial_effort[:,4:]<=1.1)).all())
 assert bool((initial_count==1).all())
 generator_state=dr.effort_generator.get_state();last_steps=dr.effort_last_sample_step.clone()
 before=dr.effort_scale.clone();selection=torch.arange(0,env.num_envs,2,device=env.device)
 assert dr.sample_effort(ids,719).numel()==0
 assert bool((dr.effort_scale==before).all())
 accepted=dr.sample_effort(selection,720)
 assert accepted.numel()==selection.numel()
 assert bool((dr.effort_sample_count[selection]==2).all())
 assert bool((dr.effort_scale[1::2]==before[1::2]).all())
 assert float((dr.effort_scale[selection]-before[selection]).abs().max())>.01
 assert dr.sample_effort(selection,1439).numel()==0
 dr.effort_scale.copy_(initial_effort);dr.effort_sample_count.copy_(initial_count)
 dr.effort_last_sample_step.copy_(last_steps);dr.effort_generator.set_state(generator_state)
 # Algebra probe of full PD scaling before clipping, at low and saturated torque.
 saved_targets=env.targets.clone();saved_torque=env.torque.clone();saved_counter=env._sim_step_counter
 saved_noise=env.full_dr_torque_noise_enabled;saved_release=env.zero_torque_remaining.clone()
 env.full_dr_torque_noise_enabled=False;env.zero_torque_remaining.zero_();env._sim_step_counter=1
 q=tensor(env.robot.data.joint_pos)[:,env.active_ids];v=tensor(env.robot.data.joint_vel)[:,env.active_ids]
 motor_checks={}
 for label,desired in [('small',[.5,-.6,.7,-.8,.2,-.3]),('saturated',[1000.,-1000.,1000.,-1000.,1000.,-1000.])]:
  desired=v.new_tensor(desired).expand_as(v)
  env.targets[:,:4]=q[:,:4]+(desired[:,:4]+2.*v[:,:4])/(60.*dr.leg_gain_scale)
  env.targets[:,4:]=v[:,4:]+desired[:,4:]/(.6*dr.wheel_gain_scale)
  ScutFlatEnv._apply_action(env)
  raw=torch.cat((60.*(env.targets[:,:4]-q[:,:4])*dr.leg_gain_scale-2.*v[:,:4],.6*(env.targets[:,4:]-v[:,4:])*dr.wheel_gain_scale),-1)
  scaled=raw*dr.effort_scale
  stall=v.new_tensor([53.333333333333336]*4+[28.18525375641699]*2)
  no_load=v.new_tensor([16.755160819145562]*4+[55.35573187814664]*2)
  peak=v.new_tensor([40.]*4+[5.775909774436091]*2)
  upper=(stall*(1-v/no_load)).clamp_min(0).minimum(peak);lower=(-stall*(1+v/no_load)).clamp_max(0).maximum(-peak)
  raw_error=float((env.motor_raw_pd_effort-scaled).abs().max())
  output_error=float((env.applied_motor_torque-scaled.minimum(upper).maximum(lower)).abs().max())
  assert raw_error<1e-6 and output_error<1e-6,(raw_error,output_error)
  motor_checks[label]=dict(raw_scaled_max_error=raw_error,clipped_output_max_error=output_error)
 env.zero_torque_remaining.fill_(10);ScutFlatEnv._apply_action(env)
 release_error=float(env.applied_motor_torque.abs().max());assert release_error==0.
 env.targets.copy_(saved_targets);env.torque.copy_(saved_torque);env._sim_step_counter=saved_counter
 env.full_dr_torque_noise_enabled=saved_noise;env.zero_torque_remaining.copy_(saved_release)
 with torch.inference_mode():_ground_start(env,6600)
 env.sample=Sampling(env)
 digest=hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest();assert digest==plan['parent_sha256']
 ck=torch.load(plan['parent'],map_location=env.device,weights_only=False);state=ck['actor_state_dict'];dims=[state['mlp.0.weight'].shape[1]]+[state[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
 for i in range(4):
  layers.append(torch.nn.Linear(dims[i],dims[i+1]))
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers).to(env.device);actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});actor.eval()
 def command():
  env.command.zero_();env.command[:,0]=2.2;env.height.fill_(.28);env.heading_env.zero_();env.standing_env.zero_();env.command_timer.fill_(10000.);env.reward.command.copy_(env.command);env.reward.height_cmd.copy_(env.height)
 command();max_closure=0.;resets=0;finite=True
 with torch.inference_mode():
  obs=env._get_observations()
  for step in range(a.steps):
   actions=actor(obs['policy']).clamp(-6,6);obs,reward,term,timeout,_=env.step(actions);command();resets+=int((term|timeout).sum());max_closure=max(max_closure,float(env.closure_error.max()))
   finite=finite and bool(torch.isfinite(reward).all()) and all(bool(torch.isfinite(v).all()) for v in obs.values())
   assert obs['policy'].shape==(a.num_envs,35) and obs['critic'].shape==(a.num_envs,78)
 assert finite and env.done_totals['numerical']==0
 result=dict(passed=True,push_checks=push_checks,push_total_events=int(env.velocity_push_count.sum()),material_checks=material_checks,material_reset_change=material_reset_change,critic_material_max_error=critic_material_error,parent_sha256=digest,num_envs=a.num_envs,steps=a.steps,effort_scale=initial_effort.cpu().tolist(),effort_sample_count=initial_count.cpu().tolist(),cooldown719_no_sample=True,cooldown720_selected_reset_only=True,motor_checks=motor_checks,zero_torque_release_abs_nm=release_error,body_mass_groups=checks,mass_write_read_max_error_kg=mass_error,inertia_write_read_max_error=inertia_error,after8reset_mass_max_change_kg=reset_mass_change,after8reset_inertia_max_change=reset_inertia_change,unselected_body_scale_one=True,left_right_front1_mass_scale_difference_max=float(pair_abs_difference.max()),mass_scale=scale.cpu().tolist(),body_names=env.robot.body_names,actual_mass_kg=initial_mass.cpu().tolist(),critic_mass_ratio=dr.factor.cpu().tolist(),finite=finite,done_totals=env.done_totals,max_closure_m=max_closure,actor_dim=35,critic_dim=78,no_optimizer_constructed=True,active_dr=dr.summary())
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
