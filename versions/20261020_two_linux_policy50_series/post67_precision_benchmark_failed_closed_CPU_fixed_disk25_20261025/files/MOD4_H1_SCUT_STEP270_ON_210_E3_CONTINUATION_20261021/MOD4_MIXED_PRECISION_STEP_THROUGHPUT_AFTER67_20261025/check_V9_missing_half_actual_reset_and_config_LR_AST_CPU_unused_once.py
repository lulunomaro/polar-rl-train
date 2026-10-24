from pathlib import Path
import ast,hashlib,json,time,types
import torch
M=Path(__file__).resolve().parent;R=M/'reports';p=M/'mixed_precision_step_benchmark_runtime_v9_missing_half.py'
a=p.read_text('utf8');tree=ast.parse(a);run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run');loop=next(n for n in ast.walk(run) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [getattr(x,'id',None) for x in n.target.elts]==['mode','dtype'])
reset=next(n for n in loop.body if isinstance(n,ast.With) and 'env.reset()' in ast.unparse(n));lr=next(n for n in ast.walk(loop) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='learning_rate' for t in n.targets));assert ast.unparse(lr.value)=='benchmark_initial_learning_rate'
with torch.inference_mode():buf=torch.ones(4)
env=types.SimpleNamespace(reset=lambda:buf.zero_());ns={'torch':torch,'env':env};module=ast.fix_missing_locations(ast.Module(body=[reset],type_ignores=[]))
for mode in ['bf16','fp16']:
 exec(compile(module,'ACTUAL_V9_CASE_RESET_NODE','exec'),ns)
 assert torch.equal(buf,torch.zeros(4))
 with torch.inference_mode():buf.fill_(1)
alg=types.SimpleNamespace(learning_rate=1e-4);ns['alg']=alg;ns['benchmark_initial_learning_rate']=alg.learning_rate
for source_saved_group_lr in [.0008649755859375,.00003375]:
 alg.learning_rate=.005
 exec(compile(ast.fix_missing_locations(ast.Module(body=[lr],type_ignores=[])),'ACTUAL_V9_LR_RESTORE_NODE','exec'),ns)
 assert alg.learning_rate==1e-4 and alg.learning_rate!=source_saved_group_lr
assert not torch.cuda.is_initialized()
q=dict(epoch=time.time(),passed=True,source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),actual_V9_case_reset_AST_executed_twice_on_real_CPU_inference_buffer=True,actual_V9_learning_rate_scalar_restore_AST_preserves_initial_config_not_saved_group=True,V8_source_unused_superseded_for_LR_config_semantics=True,missing_modes_only=['bf16','fp16'],M3_six_complete_FP32_not_repeated=True,no_model_policy_PT_raw_PhysX_or_CUDA=True)
with (R/'V9_MISSING_HALF_RESET_AND_CONFIG_LR_AST_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
print(json.dumps(q))
