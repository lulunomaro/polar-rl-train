"""New necessary0PT metadata source; no model/raw/SDK execution at preparation."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;O=T/'E0_ACTION_INPUT_MODE_CLAMP_DIAGNOSTIC_V223_20261101'
N=T/'E0_ACTUAL_ACTION_OPTIMIZER_BINDING_METADATA_V228_20261101';N.mkdir(exist_ok=False);S=N/'source';S.mkdir();R=N/'reports';R.mkdir()
def source(p,s):ast.parse(s);p.write_text(s,encoding='utf8')
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
old=(O/'source/evaluate223_input_mode_clamp_UNUSED_once.py').read_text('utf8')
prefix=old[:old.index(" source=Path(TASK['model_path'])")].replace('223','228').replace('contract228','contract228')
worker=prefix+''' import inspect,math
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
'''
source(S/'evaluate228_action_optimizer_metadata_UNUSED_once.py',worker)
source(S/'contract228.py','''E0_PARENT='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
KIND='NEW228_E0_ORIGINAL_ACTION_TERM_OPTIMIZER_IDENTITY_0PT_METADATA'
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==1 and t['controls_max']==t['physics_callbacks_max']==t['feedback_samples_max']==0
 assert t['model_byte_reads']==t['model_decodes']==0 and t['no_optimizer_or_training_or_budget_write']and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 return True
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
''')
parent=(O/'source/target223_single_N1_parent_UNUSED.py').read_text('utf8').replace('223','228').replace('evaluate228_input_mode_clamp_UNUSED_once.py','evaluate228_action_optimizer_metadata_UNUSED_once.py')
parent=parent.replace('model_byte_reads_by_worker_max=1,model_decodes_max=1','model_byte_reads_by_worker_max=0,model_decodes_max=0').replace('controls_max=32,physics_max=256,NN_actor_only=True','controls_max=0,physics_max=0,NN_constructors_for_optimizer_identity_only=2')
source(S/'target228_single_N1_parent_UNUSED.py',parent)
task=json.loads((O/'source/TASK223.json').read_bytes());task.update(kind='NEW228_E0_ORIGINAL_ACTION_TERM_OPTIMIZER_IDENTITY_0PT_METADATA',epoch=time.time(),controls_max=0,physics_callbacks_max=0,feedback_samples_max=0,model_byte_reads=0,model_decodes=0,
 necessity='Required actual SDK action scales/default offsets/CAD processing and optimizer-ID binding before source225 may transform a separate checkpoint copy. Source model is an identity reference only,not opened.',worker_SHA=hashlib.sha256((S/'evaluate228_action_optimizer_metadata_UNUSED_once.py').read_bytes()).hexdigest())
put(S/'TASK228.json',task)
(S/'zonglin2_app_launcher.py').write_bytes((O/'source/zonglin2_app_launcher.py').read_bytes())
caller=(O/'run_ROOT223_input_mode_action_flow_once.py').read_text('utf8').replace('223','228')
caller=caller.replace('run_ROOT228_input_mode_action_flow_once','run_ROOT228_action_optimizer_metadata_once').replace('MOD4_E0_ACTION_INPUT228_N1_CNONE_20261101','MOD4_E0_ACTION_OPTIMIZER_META228_CNONE_20261101')
caller=caller.replace("read(T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/reports/ROOT219V3_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')", "read(T/'W35_FULL_RM70_CLOSED_SKILL_SOURCE_V222_20261101/reports/ROOT222_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')")
caller=caller.replace('GPU_model_byte_reads=1,GPU_model_decodes=1','GPU_model_byte_reads=0,GPU_model_decodes=0').replace('new_case_controls_max=32,physics_callbacks_max=256,feedback_max=64','new_case_controls_max=0,physics_callbacks_max=0,feedback_max=0')
caller=caller.replace('original_constructor_RESET_NPZ=1','original_constructor_RESET_NPZ=1,NN_constructors_for_optimizer_identity=2,neural_forwards=0')
source(N/'run_ROOT228_action_optimizer_metadata_once.py',caller)
for p in S.glob('*.py'):ast.parse(p.read_text('utf8'))
rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(S.iterdir())if p.is_file()]
put(S/'PACKAGE228_SOURCE_AND_TASK.json',dict(epoch=time.time(),files=rows,model_asset_copies=0))
put(R/'SOURCE228_FROZEN_NECESSARY_METADATA_PURPOSE.json',dict(epoch=time.time(),source_AST_passed=True,models_raw_NPZ_CPU_SDK_GPU_remote_calls_during_preparation=0,
 target_selected_model_reads=0,NN_constructors_expected=2,neural_forward_expected=0,optimizer_steps=0,original_constructor_NPZ='Necessary existing physical constructor only',
 action_source_file_reads=1,required_before_any_real225_copy=True,original_225_candidate_unselected=True))
print(json.dumps(dict(passed=True,source_root=str(N),model_or_SDK_reads=0)))
