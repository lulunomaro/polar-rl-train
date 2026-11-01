"""ROOT-only NEW229 N1 observation/mode/action diagnostic;32 executed controls max.



Current ROOT parent owns authority/resources/locks/wait. No optimizer or GUI.

"""

from pathlib import Path

import argparse,hashlib,io,json,os,runpy,sys,time,traceback

sys.path.insert(0,str(Path(__file__).resolve().parent))

from contract234 import validate_task,E0_PARENT,KIND

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

 ns=runpy.run_path(str(entry),run_name='capture234_config_only_no_old_main')

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

 put('ACTUAL234_LITERAL_PLANT_BEFORE_MODEL.json',dict(passed=True,physics_dt=real.physics_dt,policy_dt=real.step_dt,nominal_spring=real.spring_pressure_recipe(),original_literal_reward_and_DR_binding=real.binding_receipt(),eval_yaw_only0=True,original_MOD4_guards_unchanged=True))

 import inspect,math
 legs=real.action_manager._terms['legs'];wheels=real.action_manager._terms['wheels'];sources={}
 def source_for(cls):
  try:p=Path(inspect.getsourcefile(cls))
  except (TypeError,OSError):return dict(status='NO_PY_SOURCE',object=str(cls))
  key=str(p)
  if key not in sources:
   assert len(sources)<16 and p.suffix=='.py';raw=p.read_bytes();assert len(raw)<=250000
   sources[key]=dict(path=key,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),physical_byte_reads=1)
  return dict(path=key,SHA=sources[key]['SHA'])
 def small(v):
  if v is None or isinstance(v,(str,bool,int,float)):return v
  if isinstance(v,dict):return {str(k):small(x)for k,x in v.items()}
  if isinstance(v,(list,tuple)):return [small(x)for x in v]
  try:
   x=torch.as_tensor(tensor(v),device='cpu').detach()
   return dict(shape=list(x.shape),values=x.tolist()if x.numel()<=256 else 'SHAPE_ONLY_BOUND')
  except Exception:return dict(type=type(v).__module__+'.'+type(v).__name__,value_not_assumed=True)
 def term_info(term):
  members={k:small(getattr(term,k))for k in('_scale','_offset','_clip','diff_min','diff_max')if hasattr(term,k)}
  methods={}
  for name in('process_actions','apply_actions'):
   method=getattr(term,name);f=getattr(method,'__func__',method);cells=getattr(f,'__closure__',None)
   named=dict(zip(getattr(f,'__code__',None).co_freevars,[c.cell_contents for c in cells]))if cells else{}
   methods[name]=dict(qualname=getattr(f,'__qualname__',str(f)),source=source_for(f),closure_callables={k:dict(qualname=getattr(x,'__qualname__',type(x).__name__),source=source_for(x))for k,x in named.items()if callable(x)})
  return dict(class_name=type(term).__module__+'.'+type(term).__name__,joint_names=list(term._joint_names),cfg_clip_actual=small(getattr(term.cfg,'clip',None)),members=members,methods=methods,MRO=[dict(name=c.__module__+'.'+c.__name__,source=source_for(c))for c in type(term).__mro__ if c.__module__.startswith(('isaaclab','mod4'))])
 leg=term_info(legs);wheel=term_info(wheels);actuators={}
 for name,obj in robot.actuators.items():
  actuators[name]=dict(class_name=type(obj).__module__+'.'+type(obj).__name__,MRO=[dict(name=c.__module__+'.'+c.__name__,source=source_for(c))for c in type(obj).__mro__ if c.__module__.startswith(('isaaclab','mod4'))],resolved_cfg={k:small(getattr(obj.cfg,k))for k in('stiffness','damping','effort_limit','effort_limit_sim','velocity_limit','velocity_limit_sim','saturation_effort')if hasattr(obj.cfg,k)},actual_members={k:small(getattr(obj,k))for k in('stiffness','damping','effort_limit','velocity_limit','saturation_effort')if hasattr(obj,k)})
 components={}
 for name in('_physics_action_delay','_explicit_pd','_mild_dr'):
  obj=getattr(real,name);components[name]=dict(class_name=type(obj).__module__+'.'+type(obj).__name__,source=source_for(type(obj)))
 limits=tensor(robot.root_view.get_dof_limits()).cpu()  #One additional declared read-only getter.
 result=dict(passed=True,kind=KIND,num_envs=1,controls=0,new_action_step_calls=0,constructor_contact_tick=int(real._integrated_contact.tick),NN_constructors=0,model_byte_reads=0,model_decodes=0,optimizer_steps=0,account_writes=0,
  legs=leg,wheels=wheel,actuators=actuators,components=components,joint_names=list(robot.joint_names),actual_joint_limits_N1=limits.tolist(),additional_get_dof_limits_calls=1,
  current_unique_source_files=list(sources.values()),unique_source_file_byte_reads=len(sources),physical_target_clip_or_motor_torque_observation='NOT_MEASURED_NO_ACTION_EXECUTED;this is actual resolved config and consumed method source only',
  original_policy_weight_reward_physics_or_guards_changed=False,GUI=False)
 put('CAPTURE234_ACTUAL_RESULT.json',result);print(json.dumps(dict(passed=True,cfg_clip_legs=leg['cfg_clip_actual'],unique_source_files=len(sources),model_reads=0,controls=0)),flush=True)

except BaseException:
 put('ORIGINAL234_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV234_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV234_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:
  put('APP234_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_not_required_or_fabricated=True));ns['app'].close()
  put('APP234_CLOSE_RETURNED_IF_REACHED.json',dict(returned=True))
