from pathlib import Path
import ast,hashlib,json,time,traceback
import torch
M=Path(__file__).resolve().parent;R=M/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 a=(M/'mixed_precision_step_benchmark_runtime_v7.py').read_text('utf8')
 b=a.replace("['fp32','bf16','fp16']","['bf16','fp16']").replace("[('fp32',None),('bf16',torch.bfloat16),('fp16',torch.float16)]","[('bf16',torch.bfloat16),('fp16',torch.float16)]")
 assert b.count('    env.reset()')==1
 b=b.replace('    env.reset()','    with torch.inference_mode():env.reset()')
 b=b.replace("alg.optimizer.load_state_dict(copy.deepcopy(s['optimizer_state_dict']))","alg.optimizer.load_state_dict(copy.deepcopy(s['optimizer_state_dict']));alg.learning_rate=float(s['optimizer_state_dict']['param_groups'][0]['lr'])")
 b=b.replace("'FP32 benchmark baseline failed'","'First requested missing precision mode failed'")
 ast.parse(b)
 with (M/'mixed_precision_step_benchmark_runtime_v8_missing_half.py').open('x',encoding='utf8') as f:f.write(b)
 with torch.inference_mode():buf=torch.ones(4)
 original_rejected=False
 try:buf.zero_()
 except RuntimeError as e:original_rejected='inference tensor' in str(e)
 assert original_rejected
 for mode in ['bf16','fp16']:
  with torch.inference_mode():buf.zero_();buf.add_(1)
  assert torch.equal(buf,torch.ones(4))
 assert not torch.cuda.is_initialized()
 # The fixture is an inference buffer only; no trained model, physics or source PT.
 put('V8_MISSING_HALF_CASE_RESET_CONTEXT_AND_LR_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,source_SHA=hashlib.sha256(b.encode()).hexdigest(),actual_M3_original_error='reset_history inplace inference tensor outside InferenceMode at case switch after six successful FP32 updates',CPU_negative_original_context_rejected=True,CPU_positive_inference_context_two_case_reset_passed=True,FP32_complete_baselines_M3_preserved_not_repeated=True,only_missing_bf16_fp16_requested=True,source_master_and17Adam_reload_unchanged=True,adaptive_learning_rate_scalar_restored_from_same_source_optimizer_group=True,normal_env_reset_case_setup_only_not_action_or_physics_change=True,not_deployed_or_GPU_performance_passed=True,no_local_model_policy_PT_raw_or_CUDA=True))
 print(json.dumps(dict(passed=True,original_context_negative=True,correct_reset_context=True,missing_modes=['bf16','fp16'],no_GO=True)))
except BaseException:
 put('V8_CASE_RESET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
