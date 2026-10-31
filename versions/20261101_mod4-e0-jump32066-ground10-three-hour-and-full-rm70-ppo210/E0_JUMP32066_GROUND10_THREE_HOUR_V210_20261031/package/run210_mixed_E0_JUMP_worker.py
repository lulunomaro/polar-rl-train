"""Typed literalJUMP195/own400N50D0-D7. Admission0PT or one finite full-state PPO.
Source E0_82 actor/critic/learnedSTD/Adam are retained; all target DR is explicitly new.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,shutil,sys,time,traceback
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('admission','train'),required=True)
parser.add_argument('--num-envs',type=int,required=True);parser.add_argument('--run-id',required=True);parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args();OUT=args.out;OUT.mkdir(parents=True,exist_ok=False)
def put(name,v):
 p=OUT/name;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf8');q.replace(p)
def read(p):return json.loads(Path(p).read_bytes())
task=read(P/'TASK210.json');train=args.mode=='train';n=args.num_envs
assert n==(20000 if train else 80) and task['source_SHA']=='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
assert task['literal_reward_snapshot']=='jump/wheel_legged_gym/envs/base/legged_robot.py'
go=read(P/'GO_PRODUCTION.json') if train else None
if train:
 from mixed210_task_protocol import validate_go
 assert validate_go(go,args.run_id,task,time.time())
deadline=go['save_deadline'] if train else time.time()+840
payload=P/'payload';runtime=payload/'job0/runtime/isaac/mod4'
for key in list(os.environ):
 if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
original=read(P/'E0_original_run_manifest_frozen_v1.json')['env']
os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
os.environ.update(RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='0',RM_HEADING_CMD='0',RM_HEIGHT_MIN='.25',RM_HEIGHT_MAX='.25',RM_EPISODE_S='20',RM_HIDDEN_DIMS='256,128,64',RM_VALUE_LOSS_COEF='2.0',RM_SCHEDULE='adaptive',RM_ENTROPY_COEF='.005',RM_DESIRED_KL='.01',RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'))
os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}')
os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)
sys.path[:0]=[str(P),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]
entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py'
sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs',str(n),'--seed','27','--learning_rate','.0003','--steps_per_env','24','--save_interval','25','--log_root',str(OUT/'rsl_logs')]
ns=None;real=None;runner=None;updates=0;controls=0;physics0=None;feedback0=None;last_saved=0.;first=None
def cpu(v):
 if torch.is_tensor(v):return v.detach().cpu().clone()
 if isinstance(v,dict):return {k:cpu(x) for k,x in v.items()}
 if isinstance(v,list):return [cpu(x) for x in v]
 if isinstance(v,tuple):return tuple(cpu(x) for x in v)
 return v
def finite(v,path='state'):
 if torch.is_tensor(v):
  if v.is_floating_point() or v.is_complex():assert torch.isfinite(v).all(),path
 elif isinstance(v,dict):
  for k,x in v.items():finite(x,path+'.'+str(k))
 elif isinstance(v,(list,tuple)):
  for i,x in enumerate(v):finite(x,path+'.'+str(i))
def fresh_dr_state():
 mild=real._mild_dr
 return dict(sensor=cpu(real._sensor_mild.state_dict()),feedback=cpu(real._feedback_delay_mild.state_dict()),
  physical_action=cpu(real._physics_action_delay.state_dict()),spring=cpu(real._spring_pressure.component.state_dict()),
  damping=cpu(real._gas_damping.state_dict()),COM=cpu(real._chassis_com.state_dict()),PD=cpu(real._explicit_pd.state_dict()),
  mild=dict(factor=cpu(mild.factor),nominal=cpu(mild.nominal),mu=cpu(mild.mu),reset_count=cpu(mild.reset_count),
   private_GPU_rng=mild.generator.get_state().cpu(),private_CPU_rng=mild.cpu_generator.get_state(),
   motor_output={key:cpu(value) for key,value in mild.output.items()}),
  global_CPU_rng=torch.random.get_rng_state(),global_CUDA_rng=torch.cuda.get_rng_state_all(),
  command_rngs={name:obj.get_state().cpu() for name,obj in vars(real.command_manager.get_term('twist')).items() if isinstance(obj,torch.Generator)})
def mixed_state():
 cmd=real.command_manager.get_term('twist')
 fields=('vel_command_b','time_left','command_counter','is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','command_uid209')
 command={key:cpu(getattr(cmd,key)) for key in fields if hasattr(cmd,key)}
 command['private_E0_mode_rng']=cmd._mode_rng.get_state().cpu()
 stateful={}
 for name in real.reward_manager.active_terms:
  fn=real.reward_manager.get_term_cfg(name).func
  inner=getattr(fn,'original',None)
  tracker=getattr(inner,'tracker',None)
  if tracker is not None:stateful[name]={k:cpu(v) for k,v in vars(tracker).items()}
 return dict(flat_mask=cpu(real._mixed209_flat),mode=cpu(real._mod4_mode_bit),height=cpu(real._mod4_height_cmd),command=command,
  ground_reward_episode_sums=cpu(real.reward_manager._episode_sums),stateful_ground_rewards=stateful,
  physical_history_scope='Fresh mixed episodes/queues, no exact PhysX checkpoint continuation',frozen_E0_reference_immutable=True)

def save(label):
 global last_saved
 state=runner.alg.save();finite(state)
 state.update(iter=32066+updates,infos=None,typed_MIX210_task=task,source_parent_branch_SHA=task['source_SHA'],
  actual_new_PPO_updates=updates,target_DR_state=fresh_dr_state(),mixed_ground_JUMP_state=mixed_state(),
  original_jump_reward_memory=dict(episode_sums=cpu(real.literal.episode_sums),base_air_time=cpu(real.literal.base_air_time),last_contacts=cpu(real.literal.last_contacts),contact_filt=cpu(real.literal.contact_filt),was_in_flight=cpu(real.literal.was_in_flight),last_actions=cpu(real.last_actions),last_root=cpu(real.last_root)),
  target_runtime_scope='Full E0_82 actor/critic/STD/Adam inherited; explicitly new400N50D0-D7 streams and literal pinned FudanJUMP reward/plane on72; fresh mixed physics, no exact PhysX resume.')
 dest=OUT/(label+'.pt');tmp=dest.with_suffix('.pt.partial');torch.save(state,tmp);os.replace(tmp,dest)
 with dest.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 steps=[float(x['step']) for x in state['optimizer_state_dict']['state'].values()]
 row=dict(epoch=time.time(),path=str(dest),bytes=dest.stat().st_size,SHA=sha,source_SHA=task['source_SHA'],actual_new_PPO_updates=updates,saved_iteration=32066+updates,Adam_min=min(steps),Adam_max=max(steps),full_core_STD_optimizer_and_targetDR_saved=True)
 put('latest_complete.json',row);last_saved=time.time();return row
class SavedStop(Exception):pass
try:
 ns=runpy.run_path(str(entry),run_name='source210_config_only_no_old_main')
 import torch
 from importlib import metadata
 from spring_nominal_sdk_readback import tensor
 # Restore the actual frozen E0 command class after the historical H1 import alias.
 sys.modules.pop('directional_spin_runtime',None)
 import mixed209_sdk as sdk
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=n;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)
 real=sdk.Mixed209Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000
 vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8
 assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
 obs=vec.get_observations()
 flat=real._mixed209_flat;cmd=real.command_manager.get_term('twist')
 assert int(flat.sum())==n//10 and torch.equal(real._mod4_mode_bit,(~flat).long())
 assert torch.equal(obs['policy'][:,28:35].argmax(1),real._mod4_mode_bit)
 assert (real._mod4_height_cmd[flat]==.25).all() and ((real._mod4_height_cmd[~flat]>=.12)&(real._mod4_height_cmd[~flat]<=.15)).all()
 assert (cmd.time_left[~flat]<=20.).all() and not (cmd.is_pure_spin[~flat]|cmd.is_moving_spin[~flat]|cmd.is_standing_env[~flat]).any()
 assert obs['policy'].shape==(n,35) and obs['critic'].shape==(n,38)
 assert torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all()
 put('ACTUAL_SOURCE210_LITERAL_REWARD_AND_TARGET_PLANT_BEFORE_ACTION.json',dict(epoch=time.time(),passed=True,num_envs=n,
  literal_reward_functions=real.literal.reward_names,original_reward_scales_per_second={k:v/.02 for k,v in real.literal.reward_scales.items()},
  original_clip_single_reward=2.5,original_total_positive_clip=False,outer_SDK_dt_cancelled_only=True,
  physics_dt=.0025,policy_hz=50,feedback_hz=100,TGS=[32,4],
  source_input_training_hz=50,discount_gamma=.9801,discount_lam=.9025,
  spring=real.spring_pressure_recipe(),damping=real.gas_damping_recipe(),chassisPD=real.chassis_pd_recipe(),
  sensor=real._sensor_mild.receipt(),feedback=real.feedback_delay_recipe(),action_delay=real.action_delay_recipe(),
  actual_gas_k_N_m=tensor(real.scene['robot'].root_view.get_dof_stiffnesses())[:,real._spring_pressure.ids].tolist(),
  Fudan_terrain=dict(mesh_type='plane',static_friction=.5,dynamic_friction=.5,restitution=.5),measured_mapping=real.binding_receipt(),
  unchanged_motor6_action_and_2mm_perenv_guard=True,
  measured_state_bridge=real.binding_receipt(),
  no_scripted_forces_root_or_velocity_injection=True))
 physics0=int(real._integrated_contact.tick);feedback0=int(real._feedback_100hz_tick)
 if not train:
  with torch.inference_mode():
   for i in range(8):
    obs,reward,done,extra=vec.step(torch.zeros(n,6,device=real.device));controls+=1
    assert torch.isfinite(obs['policy']).all() and torch.isfinite(reward).all()
  assert torch.equal(real._mod4_mode_bit,(~flat).long())
  assert int(flat.sum())==8 and int((~flat).sum())==72
  assert len(real.reward_manager.active_terms)>16 and 'original_jump209' in real.reward_manager.active_terms
  # The actual stateful E0 and literal kernels were both called by the original
  # RewardManager at the existing policy clock; neither is a custom reward.
  assert real.literal.calls==8 and int(real._integrated_contact.tick)-physics0==64 and int(real._feedback_100hz_tick)-feedback0==16
  put('ACTUAL210_0PT_SOURCE_SDK_NATIVE8_ADMISSION.json',dict(passed=True,controls=8,physics_callbacks=64,feedback_samples=16,num_envs=80,literal_original_reward_calls=8,source_reward_no_edits=True,measured_mapping=real.binding_receipt(),model_loads=0,NN_constructors=0,optimizer_steps=0,account_writes=0,not_skill_or_policy_success=True))
  put('FUNCTION_RETURNED.json',dict(passed=True,mode='admission',model_loads=0,actual_controls=8,errors=[]))
 else:
  config=ns['runner_config']();config=ns['handle_deprecated_rsl_rl_cfg'](config,metadata.version('rsl-rl-lib'))
  assert config.algorithm.gamma==.9801 and config.algorithm.lam==.9025
  runner=ns['OnPolicyRunner'](vec,config.to_dict(),log_dir=str(OUT/'rsl_logs'),device='cuda:0')
  model=Path(task['formal_source_model']);st=model.stat()
  with model.open('rb') as f:raw=f.read()
  assert len(raw)==17519967 and hashlib.sha256(raw).hexdigest()==task['source_SHA']
  assert model.stat().st_mtime_ns==st.st_mtime_ns
  ck=torch.load(io.BytesIO(raw),map_location='cuda:0',weights_only=True);del raw
  assert ck['iter']==32066 and runner.alg.load(ck,None,True)
  # Restore learning/sampling RNG from this branch; newly mixed episodes and
  # command/physical/DR histories are explicitly fresh.
  prior_rng=ck['target_DR_state']
  torch.random.set_rng_state(prior_rng['global_CPU_rng'].cpu())
  torch.cuda.set_rng_state_all([x.cpu() for x in prior_rng['global_CUDA_rng']])
  restored=runner.alg.save();finite(restored)
  for name in ('actor_state_dict','critic_state_dict'):
   assert set(restored[name])==set(ck[name]) and all(torch.equal(value,ck[name][key]) for key,value in restored[name].items()),name
  steps=[float(x['step']) for x in restored['optimizer_state_dict']['state'].values()];assert len(steps)==17 and min(steps)==max(steps)==642840
  std=restored['actor_state_dict']['distribution.std_param'].cpu().tolist();assert len(std)==6  # full actor comparison above includes literal saved STD
  runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr'];runner.current_learning_iteration=32067
  put('ACTUAL210_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json',dict(epoch=time.time(),passed=True,source_SHA=task['source_SHA'],source_byte_reads=1,source_GPU_decodes=1,source_actor_critic_exact=True,learned_STD6=std,Adam_steps=steps,optimizer_LR=runner.alg.learning_rate,next_iteration=32067,fresh_D0_D7_not_inherited_or_exact_physics_resume=True))
  del ck,restored
  original_update=runner.alg.update
  def update():
   global updates,first
   losses=original_update();updates+=1;finite(losses)
   if updates==1:
    first=save('model_first_complete')
    assert first['Adam_min']==first['Adam_max']==642860
    put('FIRST_ACTUAL_NEW_PPO_UPDATE.json',dict(epoch=time.time(),passed=True,actual_new_PPO_updates=1,num_envs=20000,steps_per_env=24,new_environment_transitions=480000,source_SHA=task['source_SHA'],initial_Adam_step=642840,new_Adam_step=642860,first_complete=first,original_JUMP_reward_and_plane=True,ground_envs=2000,jump_envs=18000,original_E0_ground_reward_and_commands=True,target400N50_D0_D7=True,not_270skill_success=True))
   elif time.time()-last_saved>=120:save('model_latest_complete')
   put('LATEST_PROGRESS.json',dict(epoch=time.time(),new_PPO_updates=updates,new_environment_transitions=updates*24*n,original_jump_diagnostic=real.stats194,source_reward_names=real.literal.reward_names))
   if time.time()>=deadline or (OUT/'STOP_AFTER_SAVE.json').exists() or shutil.disk_usage(P).free<8*1024**3:
    save('model_final_complete');raise SavedStop()
   return losses
  runner.alg.update=update
  try:runner.learn(num_learning_iterations=100000,init_at_random_ep_len=True)
  except SavedStop:pass
  assert updates>0
  final=save('model_final_complete')
  put('FINAL.json',dict(epoch=time.time(),passed=True,actual_new_PPO_updates=updates,final=final,no_270skill_success_claim=True,original_finite_owner_GO=go))
except BaseException:
 put('ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),complete_new_updates=updates,no_automatic_retry=True))
 if train and runner is not None:
  try:save('model_failed_valid_prefix')
  except BaseException:put('FAILED_PREFIX_SAVE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 raise
finally:
 if real is not None:
  try:real.close()
  except BaseException:put('ENV_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:ns['app'].close()
