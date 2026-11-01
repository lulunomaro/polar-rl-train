"""New240 interfaces only: saved JSON/source AST/synthetic refusals, no PT/SDK."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,time
T=Path(__file__).resolve().parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';P=N/'package';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
put('ROOT240_NEW_INTERFACE_SOURCE_CPU_ONCE_CONSUMED.json',dict(epoch=time.time(),PT_model_ONNX_raw_NPZ_USD_Torch_SDK_GPU_remote=0,old_reward_fixtures_rerun=0))
spec=importlib.util.spec_from_file_location('protocol240',P/'model2050_task240.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
task=read(P/'TASK240.json');cpu=read(R/'ROOT240_SELECTED2050_FULLPPO_SOURCE_AND_ONNX_CPU_QUALIFIED_ACTUAL.json')
assert task['source_SHA']==cpu['source_SHA'] and task['source_CPU_report_SHA']==H(R/'ROOT240_SELECTED2050_FULLPPO_SOURCE_AND_ONNX_CPU_QUALIFIED_ACTUAL.json')
assert cpu['passed'] and cpu['finite_tensors']==68 and cpu['source_iteration']==2050 and cpu['Adam17_step']==41240
assert task['source_hidden']==cpu['hidden']==[128,64,32] and task['source_learned_STD6']==cpu['learned_STD6']
s=dict(task,key='jump_72',execution_backend='target72',manifest_SHA='a'*64,literal_original_fudan_JUMP=True)
assert m.validate_schedule(dict(experts={'jump_72':s}))
v=dict(passed=True,kind=m.READY_KIND,manifest_SHA=s['manifest_SHA'],source_SHA=m.SHA,source_iteration=2050,Adam_step=m.ADAM,source_LR=m.LR,
 source_hidden=[128,64,32],source_ONNX_actor_identity_passed=True,all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,
 source_CPU_report_SHA=task['source_CPU_report_SHA'],target_GPU0PT_actual_waited_RC=0,actual_native_controls=8,actual_physics_callbacks=64,
 actual_feedback_samples=16,literal_reward_text_identity19=True,target80_private_and_validation_EX_released=True,ground_envs=2000,jump_envs=18000,
 fresh_CNone_CIM_resources_actual=True,mimic_rad=.01)
def row(value):return dict(key='jump_72',phase='ready',manifest_SHA=s['manifest_SHA'],original_error=False,
 closed_source_CPU=dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest()))
assert m.valid_ready(row(v),s)
negatives=0
for k,bad in dict(source_SHA='0'*64,source_iteration=4999,Adam_step=100020,source_LR=.0003,source_hidden=[256,128,64],
 source_ONNX_actor_identity_passed=False,source_CPU_report_SHA='f'*64,target_GPU0PT_actual_waited_RC=1,actual_native_controls=7,
 actual_physics_callbacks=63,actual_feedback_samples=15,literal_reward_text_identity19=False,target80_private_and_validation_EX_released=False,
 ground_envs=0,jump_envs=20000,fresh_CNone_CIM_resources_actual=False,mimic_rad=.05).items():
 x=copy.deepcopy(v);x[k]=bad;assert not m.valid_ready(row(x),s),k;negatives+=1
go=dict(m.flat_go_fields(task),run_id='LOCAL240_INTERFACE_FIXTURE',source_SHA=m.SHA,learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,max_parent_seconds=3900,exit_headroom_seconds=300)
assert m.validate_go(go,go['run_id'],task,101.)
for k,bad in dict(max_parent_seconds=7500,save_deadline=7300.,nominal_end_epoch=7600.,input_Adam=100020,source_iteration=4999,policy_hz=100,feedback_hz=50,nominal_gas_k_N_m=3500,discount_gamma=.99,ground_envs=0,hidden=[256,128,64],literal_original_fudan_JUMP=False).items():
 x=copy.deepcopy(go);x[k]=bad
 try:m.validate_go(x,go['run_id'],task,101.)
 except(AssertionError,KeyError):negatives+=1
 else:raise AssertionError(('GO refusal missing',k))
original=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/train_package'
for name in ('literal_original_methods.py','literal_original_config.py','jump194_boundary.py','jump194_sdk.py'):
 assert(P/name).read_bytes()==(original/name).read_bytes(),name
methods=ast.parse((P/'literal_original_methods.py').read_bytes())
assert len([x for c in methods.body if isinstance(c,ast.ClassDef) for x in c.body if isinstance(x,ast.FunctionDef)])==19
worker=(P/'run240_model2050_mixed_literal_worker.py').read_text('utf8');w=ast.parse(worker)
assert "RM_HIDDEN_DIMS='128,64,32'" in worker and "import mixed240_sdk as sdk" in worker
assert "ck['target_DR_state']" not in worker and 'typed_MODEL2050_MIX240_task' in worker
assert "literal_equal(restored['optimizer_state_dict'],ck['optimizer_state_dict'])" in worker
assert 'pc==192 and fb==48' in worker and 'APP240_CLOSING.json' in worker
target=json.loads((P/'E0_original_run_manifest_frozen_v1.json').read_bytes())['env']
assert target['RM_MILD_DR_PROFILE']=='white_v3' and str(target['RM_DR_OFF'])=='1'
result=dict(epoch=time.time(),passed=True,groups=5,negative_refusals=negatives,saved_actual_source_CPU_join=True,
 source_actor35_critic38_STD6_and_all17Adam_retained=True,original_literal_methods19_and_config_byte_identical=True,
 target_original_white_v3_full_D1_D7_recipe_reused=True,legacy_DR_OFF1_not_claimed_all_off=True,
 new_sampler_and_target_DR_not_from_selected_68tensor_PPO=True,rollout48x.01_equals24x.02=True,
 PT_ONNX_raw_NPZ_USD_Torch_SDK_GPU_remote_reads_or_calls=0,actual_target0PT_still_pending=True)
put('ROOT240_NEW_SOURCE_TaskGO_CPU_RETURNED_ACTUAL.json',result);print(json.dumps(result))
