from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;N=T/'CURRENT_ACTION_CFG_CLIP_AND_PD_SDK_METADATA_V234_20261101';S=N/'source';R=N/'reports';S.mkdir(parents=True,exist_ok=False);R.mkdir()
OLD=T/'E0_ORIGINAL_ACTION_CLOSURE_METADATA_V229_20261101'
def phase(s):
 for x,y in [('contract229','contract234'),('ACTUAL229','ACTUAL234'),('CAPTURE229','CAPTURE234'),('ORIGINAL229','ORIGINAL234'),('ENV229','ENV234'),('APP229','APP234'),('PARENT229','PARENT234'),('PACKAGE229','PACKAGE234'),('TASK229','TASK234'),('capture229_','capture234_'),('target229_','target234_'),('evaluate229_','evaluate234_')]:s=s.replace(x,y)
 return s
worker=phase((OLD/'source/evaluate229_action_optimizer_metadata_UNUSED_once.py').read_text('utf8'))
start=worker.index(' import inspect,math');end=worker.index('\nexcept BaseException:',start)
body=r''' import inspect,math
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
  return dict(class_name=type(term).__module__+'.'+type(term).__name__,joint_names=list(term._joint_names),cfg_clip_actual=small(getattr(term.cfg,'clip',None)),members=members,methods=methods,MRO=[dict(name=c.__module__+'.'+c.__name__,source=source_for(c))for c in type(term).__mro__if c.__module__.startswith(('isaaclab','mod4'))])
 leg=term_info(legs);wheel=term_info(wheels);actuators={}
 for name,obj in robot.actuators.items():
  actuators[name]=dict(class_name=type(obj).__module__+'.'+type(obj).__name__,MRO=[dict(name=c.__module__+'.'+c.__name__,source=source_for(c))for c in type(obj).__mro__if c.__module__.startswith(('isaaclab','mod4'))],resolved_cfg={k:small(getattr(obj.cfg,k))for k in('stiffness','damping','effort_limit','effort_limit_sim','velocity_limit','velocity_limit_sim','saturation_effort')if hasattr(obj.cfg,k)},actual_members={k:small(getattr(obj,k))for k in('stiffness','damping','effort_limit','velocity_limit','saturation_effort')if hasattr(obj,k)})
 components={}
 for name in('_physics_action_delay','_explicit_pd','_mild_dr'):
  obj=getattr(real,name);components[name]=dict(class_name=type(obj).__module__+'.'+type(obj).__name__,source=source_for(type(obj)))
 limits=tensor(robot.root_view.get_dof_limits()).cpu()  #One additional declared read-only getter.
 result=dict(passed=True,kind=KIND,num_envs=1,controls=0,physics_callbacks=0,NN_constructors=0,model_byte_reads=0,model_decodes=0,optimizer_steps=0,account_writes=0,
  legs=leg,wheels=wheel,actuators=actuators,components=components,joint_names=list(robot.joint_names),actual_joint_limits_N1=limits.tolist(),additional_get_dof_limits_calls=1,
  current_unique_source_files=list(sources.values()),unique_source_file_byte_reads=len(sources),physical_target_clip_or_motor_torque_observation='NOT_MEASURED_NO_ACTION_EXECUTED;this is actual resolved config and consumed method source only',
  original_policy_weight_reward_physics_or_guards_changed=False,GUI=False)
 put('CAPTURE234_ACTUAL_RESULT.json',result);print(json.dumps(dict(passed=True,cfg_clip_legs=leg['cfg_clip_actual'],unique_source_files=len(sources),model_reads=0,controls=0)),flush=True)
'''
worker=worker[:start]+body+worker[end:];ast.parse(worker);(S/'evaluate234_action_optimizer_metadata_UNUSED_once.py').write_text(worker,encoding='utf8')
parent=phase((OLD/'source/target229_single_N1_parent_UNUSED.py').read_text('utf8'));ast.parse(parent);(S/'target234_single_N1_parent_UNUSED.py').write_text(parent,encoding='utf8')
task=json.loads((OLD/'source/TASK229.json').read_bytes());task.update(kind='NEW234_CURRENT_ACTION_CFG_CLIP_PD_DC_METADATA',worker_SHA=hashlib.sha256(worker.encode()).hexdigest(),necessity='Actualactionreview lacks inheritedcurrentSDK baseapply/PD/DC and resolvedcfg.clip;necessary before furtheroutputrepair,notforstats/Git',source_status='FROZEN_NEW0NN_CURRENT_SDK_CFG_SOURCE_PURPOSE',model_byte_reads=0,model_decodes=0,controls_max=0,physics_callbacks_max=0,feedback_samples_max=0,SDK_source_files_byte_reads_max=16,extra_get_dof_limits=1)
contract="""KIND='NEW234_CURRENT_ACTION_CFG_CLIP_PD_DC_METADATA'
E0_PARENT='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert binding['kind']=='FRESH_CNONE'and c['active_segment']is None
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==1 and t['controls_max']==t['physics_callbacks_max']==t['feedback_samples_max']==0
 assert t['model_byte_reads']==t['model_decodes']==0 and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and t['SDK_source_files_byte_reads_max']==16 and t['extra_get_dof_limits']==1
 assert t['no_optimizer_or_training_or_budget_write']and not t['training_reward_changed']
 return True
""";(S/'contract234.py').write_text(contract,encoding='utf8')
(S/'TASK234.json').write_text(json.dumps(task,indent=2),encoding='utf8')
rows=[]
for p in sorted(S.iterdir()):
 b=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
(S/'PACKAGE234_SOURCE_AND_TASK.json').write_text(json.dumps(dict(files=rows,source_only=True),indent=2),encoding='utf8')
caller=(OLD/'run_ROOT229_original_action_closure_metadata_once.py').read_text('utf8');caller=phase(caller).replace('ROOT229','ROOT234').replace('case229_','case234_').replace('MOD4_E0_ACTION_OPTIMIZER_META229_CNONE_20261101','MOD4_CURRENT_ACTION_CFG_PD_META234_CNONE_20261101')
caller=caller.replace('run_ROOT229_original_action_closure_metadata_once','run_ROOT234_current_action_cfg_PD_metadata_once')
caller=caller.replace("T/'E0_ACTUAL_ACTION_OPTIMIZER_BINDING_METADATA_V228_20261101/reports/ROOT228V2_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'", "T/'E2_READER_ORDER_REPAIR_AND_FULL_WORLD_CASE_V232_20261101/reports/ROOT233_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'")
caller=caller.replace('own_loaded_wheel_geometry_metadata_queries_max=0','own_loaded_wheel_geometry_metadata_queries_max=0,additional_get_dof_limits_calls_max=1,selected_unique_PY_source_byte_reads_max=16')
ast.parse(caller);(N/'run_ROOT234_current_action_cfg_PD_metadata_once.py').write_text(caller,encoding='utf8')
(R/'ROOT234_NEW_NECESSARY0NN_CFG_SOURCE_PURPOSE_FROZEN.json').write_text(json.dumps(dict(epoch=time.time(),passed_source_AST=True,source_files_max=16,current_resolved_cfg_clip_and_PD_DC=True,one_additional_get_dof_limits=True,model_raw_NPZ_GPU_neural_reads=0,own_constructor_reset_NPZ=1,actions_or_physics_steps=0,no_policy_or_reward_or_physics_write=True),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,source=str(N),files=len(rows))))
