"""ROOT-only NEW228 N1 observation/mode/action diagnostic;32 executed controls max.



Current ROOT parent owns authority/resources/locks/wait. No optimizer or GUI.

"""

from pathlib import Path

import argparse,hashlib,io,json,os,runpy,sys,time,traceback

sys.path.insert(0,str(Path(__file__).resolve().parent))

from contract228 import validate_task,E0_PARENT,KIND

parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);args=parser.parse_args()

P=args.task.resolve().parent;TASK=json.loads(args.task.read_bytes());validate_task(TASK)

assert os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']

assert TASK['actual_parent_private_EX_and_authority_admitted'] is True

assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']

ROOT=Path(TASK['qualified197_package_root']);payload=ROOT/'payload'

OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)





def put(n,v):

 with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)





deadline=time.time()+840;real=ns=None

try:

 original=json.loads((payload/'job0/original_run_manifest.json').read_bytes())['env']

 for key in list(os.environ):

  if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]

 os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SPIN_STAGE','RM_SLOPE_INITIAL_ADMISSION')})

 os.environ.update(RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',

  RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='1',RM_HEADING_CMD='0',

  RM_HEIGHT_MIN='.23',RM_HEIGHT_MAX='.33',RM_EPISODE_S='20',RM_HIDDEN_DIMS='256,128,64',

  RM_VALUE_LOSS_COEF='2.0',RM_SCHEDULE='adaptive',RM_ENTROPY_COEF='.005',RM_DESIRED_KL='.01',

  RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'UNREQUESTED_STOP.json'))

 os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'

 kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}')

 os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)

 runtime=payload/'job0/runtime/isaac/mod4'

 sys.path[:0]=[str(P),str(ROOT),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]

 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py'

 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','27','--log_root',str(OUT/'unused_learning_logs')]

 ns=runpy.run_path(str(entry),run_name='capture228_config_only_no_old_main')

 import numpy as np

 import torch

 from spring_nominal_sdk_readback import tensor

 import jump194_sdk as sdk

 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=1;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)

 cfg.commands.twist.ranges.ang_vel_z=(0.,0.)  #207 controlled eval-only factor;reward unchanged.

 real=sdk.JumpMod4Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000

 vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.);obs=vec.get_observations();robot=real.scene['robot']

 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8

 assert obs['policy'].shape==(1,35) and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000

 assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01

 assert tuple(cfg.commands.twist.ranges.lin_vel_x)==(-2.1,2.1)

 put('ACTUAL228_LITERAL_PLANT_BEFORE_MODEL.json',dict(passed=True,physics_dt=real.physics_dt,policy_dt=real.step_dt,nominal_spring=real.spring_pressure_recipe(),original_literal_reward_and_DR_binding=real.binding_receipt(),eval_yaw_only0=True,original_MOD4_guards_unchanged=True))

 import inspect,math
 from importlib import metadata
 legs=real.action_manager._terms['legs'];wheels=real.action_manager._terms['wheels']
 leg_names=list(legs._joint_names);wheel_names=list(wheels._joint_names);order=leg_names+wheel_names
 def vector(value,n):
  x=torch.as_tensor(tensor(value),device='cpu',dtype=torch.float32).reshape(-1)
  if x.numel()==1:x=x.repeat(n)
  assert x.numel()==n and torch.isfinite(x).all()
  return x.tolist()
 scales=vector(legs._scale,4);offsets=vector(legs._offset,4)
 diff_min=float(legs.diff_min);diff_max=float(legs.diff_max);assert math.isfinite(diff_min)and math.isfinite(diff_max)
 method=legs.process_actions;source_file=Path(inspect.getsourcefile(method));raw=source_file.read_bytes();text=raw.decode('utf8')
 source_SHA=hashlib.sha256(raw).hexdigest()
 original_guard_present='torch.maximum(pa[:, 0], pa[:, 1] + self.diff_min' in text and 'torch.minimum(pa[:, 0], pa[:, 1] + self.diff_max'in text
 config=ns['handle_deprecated_rsl_rl_cfg'](ns['runner_config'](),metadata.version('rsl-rl-lib'))
 with torch.random.fork_rng(devices=[torch.cuda.current_device()]):
  runner=ns['OnPolicyRunner'](vec,config.to_dict(),log_dir=str(OUT/'unused_training_logs'),device='cuda:0')
  packed=runner.alg.optimizer.state_dict();identity={}
  for live,saved in zip(runner.alg.optimizer.param_groups,packed['param_groups']):
   assert len(live['params'])==len(saved['params'])
   for parameter,pid in zip(live['params'],saved['params']):identity[id(parameter)]=pid
  named=dict(runner.alg.actor.named_parameters());keys=('mlp.6.weight','mlp.6.bias','distribution.std_param')
  bindings={k:identity[id(named[k])]for k in keys}
  actor_shapes={k:list(v.shape)for k,v in named.items()}
  critic_shapes={k:list(v.shape)for k,v in runner.alg.critic.named_parameters()}
  assert len(identity)==17 and len(named)==9
  assert tuple(named['mlp.0.weight'].shape)==(256,35)and tuple(named['mlp.6.weight'].shape)==(6,64)
  distribution_class=type(runner.alg.actor.distribution).__module__+'.'+type(runner.alg.actor.distribution).__name__
  assert distribution_class.endswith('.GaussianDistribution')
  del runner
 proof=dict(actual_original_action_term_verified=original_guard_present and order==['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin']and scales==[.5]*4,
  actual_SDK_source_SHA=source_SHA,source_model_SHA=TASK['model_SHA'],policy_order=order,leg_scales=scales,leg_default_offsets=offsets,diff_min=diff_min,diff_max=diff_max,
  optimizer_parameter_ID_by_actor_key=bindings,optimizer_param_groups_IDs=[g['params']for g in packed['param_groups']],
  actor_parameter_shapes=actor_shapes,critic_parameter_shapes=critic_shapes,actual_distribution_class=distribution_class,
  action_term_class=type(legs).__module__+'.'+type(legs).__name__,method_qualname=method.__qualname__,
  model_file_read=False,model_weights_or_optimizer_state_restored=False,NN_actor_and_critic_constructors=2,optimizer_constructor=1,optimizer_steps=0,neural_forwards=0)
 result=dict(passed=True,kind=KIND,proof=proof,actual_action_source=dict(path=str(source_file),bytes=len(raw),SHA=source_SHA,UTF8=text,byte_reads=1),
  controls=0,physics_callbacks=0,feedback_samples=0,counts_are_controller_calls_not_constructor_simulation=True,
  actual_original_plant_and_task_binding=real.binding_receipt(),source_cache_model_byte_reads=0,model_decodes=0,account_writes=0,
  fixed_source_E0_reference_untouched=True,output_repair_applied=False)
 put('CAPTURE228_ACTUAL_RESULT.json',result)
 print(json.dumps(dict(passed=True,proof_verified=proof['actual_original_action_term_verified'],bindings=bindings,scales=scales,offsets=offsets,diff_min=diff_min)),flush=True)
except BaseException:
 put('ORIGINAL228_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV228_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV228_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:
  put('APP228_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_not_required_or_fabricated=True));ns['app'].close()
  put('APP228_CLOSE_RETURNED_IF_REACHED.json',dict(returned=True))
