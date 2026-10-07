"""Resume stochastic streams, then deliberately start a new physical episode."""
import torch,json,os,time,hashlib
from pathlib import Path
from sensor_mild_math import SensorCorruption,CHANNELS

def restore_named(obj,saved):
 actual={k:v for k,v in vars(obj).items() if isinstance(v,torch.Generator)}
 assert set(actual)==set(saved),('Named RNG schema differs',set(actual),set(saved))
 for k,g in actual.items():g.set_state(saved[k].cpu())
 assert all(torch.equal(g.get_state().cpu(),saved[k].cpu()) for k,g in actual.items())
 return sorted(actual)

def restore_sensor(s,ck):
 assert ck['sensor_recipe']['profile']==s.profile=='noise_bias_mild_v1'
 saved=ck['sensor_DR_state'];assert set(saved['noise_rng'])==set(s.noise_rng)
 # New environment count: retain generator streams, discard every old episode row/cache.
 # env.reset below samples the full new count from those restored streams.
 s.bias_rng.set_state(saved['bias_rng'].cpu())
 for name,g in s.noise_rng.items():g.set_state(saved['noise_rng'][name].cpu())
 assert torch.equal(s.bias_rng.get_state().cpu(),saved['bias_rng'].cpu())
 assert all(torch.equal(g.get_state().cpu(),saved['noise_rng'][k].cpu()) for k,g in s.noise_rng.items())
 return True

def resume_sensor_new_episode(runner,env,path,log_dir):
 from sensor_a0_runtime import state
 ck=torch.load(path,map_location='cpu',weights_only=False);s=state(env)
 # RSL's existing loader restores actor/critic/optimizer/std/iteration first.
 for key,obj in [('actor_state_dict',runner.alg.actor),('critic_state_dict',runner.alg.critic)]:
  actual=obj.state_dict();assert set(actual)==set(ck[key])
  assert all(torch.equal(actual[k].cpu(),v.cpu()) for k,v in ck[key].items()),key
 assert runner.current_learning_iteration==ck['iter']
 assert runner.alg.optimizer.state_dict()['param_groups']==ck['optimizer_state_dict']['param_groups']
 optimizer=runner.alg.optimizer.state_dict()['state'];assert set(optimizer)==set(ck['optimizer_state_dict']['state'])
 for k,v in ck['optimizer_state_dict']['state'].items():
  assert set(optimizer[k])==set(v)
  for name,value in v.items():
   assert torch.equal(optimizer[k][name].cpu(),value.cpu()) if torch.is_tensor(value) else optimizer[k][name]==value
 restore_sensor(s,ck);before=s.episode.clone()
 cmd=restore_named(env.command_manager.get_term('twist'),ck['sensor_command_DR_rng_state'])
 physical=restore_named(env._mild_dr,ck['sensor_physical_DR_rng_state'])
 torch.random.set_rng_state(ck['sensor_global_rng_state']['cpu'].cpu())
 cuda=ck['sensor_global_rng_state']['cuda'];assert len(cuda)==torch.cuda.device_count()
 torch.cuda.set_rng_state_all([x.cpu() for x in cuda])
 assert torch.equal(torch.random.get_rng_state(),ck['sensor_global_rng_state']['cpu'])
 assert all(torch.equal(a.cpu(),b.cpu()) for a,b in zip(torch.cuda.get_rng_state_all(),cuda))
 # Saved PhysX state is not resumed. Restore streams before resampling all episode state.
 env.reset()
 assert torch.equal(s.episode,before+1)
 # reset invalidates each sensor row; subsequent observation may fill the current tick.
 assert all(bool(((last==-1)|(last==env.common_step_counter)).all()) for last,_ in s.cache.values())
 audit=env.sensor_sdk_audit()
 robot=env.scene['robot'];qerr=float((robot.data.joint_pos-env._rescue_reset_q).abs().max())
 assert qerr==0 and bool(torch.isfinite(robot.data.joint_pos).all())
 params=env._mild_dr.audit();assert params['actual_parameters_pass']
 p=Path(path);receipt=dict(epoch=time.time(),pid=os.getpid(),source_path=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
  actor_critic_std_exact=True,optimizer_loaded_original_path=True,stored_iteration=ck['iter'],sensor_streams_restored=True,per_environment_saved_arrays_restored=False,source_environment_count=int(ck["sensor_DR_state"]["bias"].shape[0]),new_environment_count=int(env.num_envs),fresh_episode_array_lifecycle=True,
  command_named_streams=cmd,physical_named_streams=physical,global_CPU_CUDA_streams_restored=True,
  new_physical_episode=True,all_episode_counters_incremented_once=True,history_cache_new_episode=True,
  initial30q_error_rad=qerr,actual_parameter_audit=params,actual_sensor_manager_audit=audit,PhysX_exact_resume_claimed=False)
 Path(log_dir,'SENSOR_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(receipt,indent=2))
 return receipt
