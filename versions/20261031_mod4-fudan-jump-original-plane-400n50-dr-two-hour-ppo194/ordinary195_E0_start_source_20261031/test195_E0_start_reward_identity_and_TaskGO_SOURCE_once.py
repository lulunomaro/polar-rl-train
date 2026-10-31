from pathlib import Path
import ast,copy,hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';D=N/'train_package'
O=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
with (R/'ROOT195_NEW_SOURCE_CPU_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),checkpoint_reads=0,remote_SDK_GPU=0),f)
groups=[]
try:
 task=json.loads((D/'TASK195.json').read_bytes())
 for name in ('literal_original_methods.py','literal_original_config.py','mod4_literal_math184.py','mod4_literal_math184_v2.py'):
  assert (D/name).read_bytes()==(O/'train_package'/name).read_bytes(),name
 for name in ('jump195_sdk.py','jump195_boundary.py'):
  new=(D/name).read_text('utf8').replace('195','194')
  old=(O/'train_package'/name.replace('195','194')).read_text('utf8')
  assert ast.dump(ast.parse(new),include_attributes=False)==ast.dump(ast.parse(old),include_attributes=False),name
 groups.append(dict(name='unchanged_literal_JUMP_methods_config_measured_bridge_and_FK',passed=True,reference19_method_text_proof=str(O/'reports/ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json')))
 source=json.loads(Path(task['source_fullstate_CPU_report']).read_bytes())
 assert source['passed'] and source['model']['SHA']==task['source_SHA'] and source['model']['bytes']==14031973
 assert source['review']['actor9_critic8_STD6_actor35_critic38'] and source['review']['Adam_states']==17
 assert source['review']['Adam_step']==task['source_Adam_step']==641200 and source['review']['stored_RSL_iteration']==task['source_iteration']==31984
 assert source['review']['final_adaptive_optimizer_LR']==task['source_adaptive_LR']
 worker=(D/'run195_literal_jump_plane_worker.py').read_text('utf8');ast.parse(worker)
 for text in ["ck['iter']==31984","==14031973","==641200","==641220","runner.current_learning_iteration=31985","iter=31984+updates","source_E0_SHA=task['source_SHA']"]:assert text in worker,text
 assert "assert std==task['learned_STD6']" not in worker and 'torch.equal(value,ck[name][key])' in worker
 assert "shutil.disk_usage(P).free<8*1024**3" in worker and "go['max_parent_seconds']==3900" in worker
 groups.append(dict(name='E0_82_qualified_400N50_fullstate_counter_LR_and_STD_restore_contract',passed=True,checkpoint_reads=0))
 current=json.loads((N/'TRAIN195_COMPLETE_MANIFEST.json').read_bytes())
 original=json.loads((O/'TRAIN194_COMPLETE_MANIFEST.json').read_bytes())
 prev={x['relative']:x for x in original['files']}
 for row in current['files']:
  if not row['relative'].startswith('payload/'):continue
  assert row['SHA']==prev[row['relative']]['SHA'] and row['bytes']==prev[row['relative']]['bytes']
 install=ast.parse((N/'install195_literal_jump_plane_admission_once.py').read_bytes());main=next(x for x in install.body if isinstance(x,ast.FunctionDef) and x.name=='main')
 assert isinstance(main.body[0],ast.Assign) and isinstance(main.body[1],ast.Assign) and isinstance(main.body[2],ast.Assert)
 assert 'ROOT194_COMPLETE_FINAL_OR_FAILURE' in ast.unparse(main.body[0]) and 'ROOT194_NEW_FORMAL_INITIAL_CPU' in ast.unparse(main.body[1])
 assert current['deferred_input_model']['actual_uploads']==0 and current['deferred_input_model']['CPU_model_reads']==0
 groups.append(dict(name='physical_payload_identical_and195_install_requires_actual194_closure_first',passed=True,no_new_binary_reads=True))
 sys.path.insert(0,str(N/'control'));import jump195_protocol as p
 manifest=H(N/'TRAIN195_COMPLETE_MANIFEST.json')
 spec=dict(key='h1_210',execution_backend='source210',max_parent_seconds=3900,exit_headroom_seconds=300,source_SHA=task['source_SHA'],num_envs=20000,literal_jump195_400N50=True,no_comparison_arms=True,manifest_SHA=manifest)
 assert p.validate_schedule(dict(experts={'h1_210':spec}))
 v=dict(passed=True,kind='JUMP195_LITERAL_400N50_ACTUAL_CPU_NATIVE8_AND_DELIVERY31984_FULLSTATE_REUSE',source_SHA=task['source_SHA'],source_iteration=31984,Adam_step=641200,
  all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,target_CPU_actual_waited_RC=0,target_GPU0PT_actual_waited_RC=0,actual_native_controls=8,actual_physics_callbacks=64,literal_reward_text_identity19=True,manifest_SHA=manifest,target64_private_EX_released=True)
 def row(v):return dict(key='h1_210',manifest_SHA=manifest,phase='ready',original_error=False,closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()))
 assert p.valid_ready(row(v),spec)
 negative=[]
 for name,bad in dict(passed=False,kind='OLD_DELIVERY4999',source_SHA='0'*64,source_iteration=4999,Adam_step=100020,all_actor_critic_optimizer_tensors_finite=False,actual_35_38_6_shapes=False,target_CPU_actual_waited_RC=1,target_GPU0PT_actual_waited_RC=1,actual_native_controls=0,actual_physics_callbacks=32,literal_reward_text_identity19=False,manifest_SHA='0'*64,target64_private_EX_released=False).items():
  assert not p.valid_ready(row({**v,name:bad}),spec),name;negative.append(name)
 for name,bad in [('max_parent_seconds',7500),('num_envs',4096),('source_SHA','0'*64),('literal_jump195_400N50',False)]:
  try:p.validate_schedule(dict(experts={'h1_210':{**spec,name:bad}}))
  except AssertionError:negative.append('schedule.'+name)
  else:raise AssertionError(name)
 groups.append(dict(name='E0_specific_TaskGO_readiness_and_old_jump_actor_refusals',passed=True,negative_cases=negative))
 report=dict(epoch=time.time(),passed=True,groups=groups,negative_count=len(negative),
  scope='Source and prior qualified metadata only. No new checkpoint read,SDK,remote,GPU,training or actual target fullstate restore.',
  next_required='After194 qualified closure, install195 and obtain actual target0PT/CUDA fullstate/FIRST receipts before claiming195 started')
except BaseException:
 report=dict(epoch=time.time(),passed=False,groups=groups,error=traceback.format_exc(),not_physical_policy_failure=True);raise
finally:
 with (R/'ROOT195_E0_START_LITERAL_REWARD_SOURCE_AND_TaskGO_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,groups=len(groups),negative_cases=len(negative),models_read=0)))
