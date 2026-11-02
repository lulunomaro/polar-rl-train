"""Explicit initial D0-D7 matching and common D1 noise for forty first-episode pairs.

The second forty receive the first forty's sampled full DR through the original
parameter adapters. No simulator clocks, actuator force path, controller gains,
queue period or acceptance criteria change. Post-termination resets are outside
the first-episode comparison. D1 remains uniform with its original bounds;
independent per-pair/channel/tick draws are shared within each pair.
"""
import types
import torch

def install_common_noise377(sensor,seed,start_tick,max_feedback_ticks=1100):
 from sensor_mild_math import CHANNELS
 assert sensor.n==80 and sensor.profile=='noise_bias_mild_v1'
 tables={};checks={k:0 for k in CHANNELS};draws={k:0 for k in CHANNELS}
 for key,(width,bound,offset) in CHANNELS.items():
  rng=torch.Generator(device=sensor.device).manual_seed(int(seed)+3770000+offset)
  tables[key]=(2*torch.rand((max_feedback_ticks,40,width),device=sensor.device,generator=rng)-1)*bound
 def apply(this,key,value,tick):
  assert key in CHANNELS and value.shape==(80,CHANNELS[key][0]) and bool(torch.isfinite(value).all())
  if this.profile=='off':return value
  index=int(tick)-start_tick;assert 0<=index<max_feedback_ticks
  if key not in this.cache:
   this.cache[key]=(torch.full((80,),-1,device=this.device,dtype=torch.long),torch.zeros_like(value))
  last,noise=this.cache[key];due=torch.where(last!=int(tick))[0]
  if len(due):
   noise[due]=tables[key][index,due%40];last[due]=int(tick)
   this.draw_counts[key]+=len(due);draws[key]+=len(due)
  assert torch.equal(noise[:40],noise[40:])
  checks[key]+=1
  return value+noise+(this.bias if key=='leg_pos'else 0.)
 sensor.cache={};sensor.apply=types.MethodType(apply,sensor)
 def receipt():
  return dict(passed=True,start_feedback_tick=start_tick,table_feedback_ticks=max_feedback_ticks,shared_pair_noise_exact=True,channel_calls=checks,noise_row_draws=draws,original_uniform_bounds={k:v[1]for k,v in CHANNELS.items()},noise_schedule='new377 independent pair/channel/absolute100Hz tick; within-pair common random numbers',global_RNG_not_used=True,no_future_observation=True)
 return receipt

def install_matched_pairs377(env,seed,max_feedback_ticks=1100):
 import warp as wp
 from spring_nominal_sdk_readback import tensor
 assert env.num_envs==80 and env.physics_dt==.0025 and env.step_dt==.02
 robot=env.scene['robot'];ids=torch.arange(40,80,device=env.device);src=ids-40
 cpuids=ids.to('cpu',torch.int32);cpusrc=src.to('cpu',torch.long)
 def pair(value):
  value[ids.to(value.device)]=value[src.to(value.device)].clone()
 def exact(value):return torch.equal(value[:40],value[40:])
 dr=env._mild_dr
 for name in ('factor','nominal','reset_count','mu'):pair(getattr(dr,name))
 robot.set_masses_index(masses=dr.mass[ids]*dr.factor[ids,None],env_ids=ids)
 robot.set_inertias_index(inertias=dr.inertia[ids]*dr.factor[ids,None,None],env_ids=ids)
 materials=tensor(robot.root_view.get_material_properties()).clone().cpu()
 materials[cpuids.long()]=materials[cpusrc].clone()
 robot.root_view.set_material_properties(wp.from_torch(materials,dtype=wp.float32),wp.from_torch(cpuids,dtype=wp.int32))
 for key in ('legs','wheels'):
  pair(robot.actuators[key].episode_scale);pair(robot.actuators[key].step_scale)
 for obj in (env._spring_pressure,env._gas_damping):
  pair(obj.component.factor);pair(obj.component.episode);obj.apply(ids)
 com=env._chassis_com;pair(com.component.delta_m);pair(com.component.episode)
 com.orientation_after_parent_reset=tensor(robot.root_view.get_coms()).to(env.device)[...,3:].clone()
 com.apply(ids)
 pd=env._explicit_pd
 for value in pd.component.factor.values():pair(value)
 pair(pd.component.episode);pd.apply(ids)
 sensor=env._sensor_mild;delay=env._feedback_delay_mild
 pair(sensor.bias);pair(sensor.episode);pair(delay.delay);pair(delay.episode)
 # Warmup uses the actual new episode's current reading, then original0/10ms.
 delay.cache={}
 for g in env._physics_action_delay.queue.groups.values():
  for value in g.values():pair(value)
 noise_receipt=install_common_noise377(sensor,seed,int(env._feedback_100hz_tick),max_feedback_ticks)
 env._matched377_receipt=noise_receipt
 # Planned state writes do not advance SDK time. Refresh derived IMU values
 # from the current measured root pose/velocity, then original D1-D3 applies.
 refreshed=[]
 for name in ('_root_com_ang_vel_b','_root_link_ang_vel_b','_projected_gravity_b'):
  assert hasattr(robot.data,name),name
  getattr(robot.data,name).timestamp=-float('inf');refreshed.append(name)
 policy=env.observation_manager.compute_group('policy').clone()
 sensor_pair_delta=float((policy[:40,4:22]-policy[40:,4:22]).abs().max())
 assert sensor_pair_delta<1e-6,('Initial measured D1-D3 channels differ',sensor_pair_delta)

 backend=dict(masses=tensor(robot.root_view.get_masses()),inertias=tensor(robot.root_view.get_inertias()),materials=tensor(robot.root_view.get_material_properties()),COM=tensor(robot.root_view.get_coms())[...,:3],stiffness=tensor(robot.root_view.get_dof_stiffnesses()),damping=tensor(robot.root_view.get_dof_dampings()),armature=tensor(robot.root_view.get_dof_armatures()),force_caps=tensor(robot.root_view.get_dof_max_forces()))
 backend_checks={k:dict(paired_exact=exact(v),max_abs_pair_delta=float((v[:40]-v[40:]).abs().max()))for k,v in backend.items()}
 assert all(v['paired_exact']for v in backend_checks.values()),backend_checks
 memory=dict(D0factor=dr.factor,D0nominal=dr.nominal,D0mu=dr.mu,D2bias=sensor.bias,D3delay=delay.delay,D5=env._spring_pressure.component.factor,D6=env._gas_damping.component.factor,D7COM=com.component.delta_m)
 for key in ('legs','wheels'):
  actuator=robot.actuators[key]
  for field in ('stiffness','damping','episode_scale','step_scale'):memory[key+'_'+field]=tensor(getattr(actuator,field))
  for field,value in env._physics_action_delay.queue.groups[key].items():memory['D4_'+key+'_'+field]=value
 memory_checks={k:exact(v)for k,v in memory.items()};assert all(memory_checks.values()),memory_checks
 q=tensor(robot.data.joint_pos);dq=tensor(robot.data.joint_vel);root=tensor(robot.data.root_state_w).clone();root[:,:3]-=env.scene.env_origins
 assert exact(q)and exact(dq)and float((root[:40]-root[40:]).abs().max())<1e-5
 return dict(passed=True,pairs=[[i,i+40]for i in range(40)],first_episode_only=True,DR_population='first40 native fullD0whitev3/D1-D7 samples copied to partner through original setters',backend_readback=backend_checks,memory_pair_checks=memory_checks,initial_q_exact=True,initial_dq_exact=True,derived_IMU_caches_refreshed=refreshed,first_policy_feedback_max_delta=sensor_pair_delta,relative_root_max_delta=float((root[:40]-root[40:]).abs().max()),root_translation_dtype_tolerance_m=1e-5,noise=noise_receipt(),D3_warmup='fresh current sample then original0/10ms',D4_control_us=env._physics_action_delay.queue.control_us,physics_dt=env.physics_dt,policy_dt=env.step_dt,NN=0,optimizer=0,account_writes=0)
