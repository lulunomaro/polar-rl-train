from pathlib import Path
import ast,copy,hashlib,json,shutil,time
M=Path(__file__).resolve().parent;R=M/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());assert set(q['specs'])=={'h1','recovery'}
assert json.loads((R/'AMP_BENCHMARK_V3_SCALER_ALLOWLIST_AND_CPU_SYNTHETIC_ACTUAL.json').read_bytes())['passed']
runtime=M/'mixed_precision_step_benchmark_runtime_v3.py';changes=[]
for key in ('h1','recovery'):
 B=Path(q['payloads'][key]);oldmanifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());known={r['relative']:r for r in oldmanifest['files']}
 source=B/('h1_step270_production_worker_v1.py' if key=='h1' else 'recovery_worker.py');tree=ast.parse(source.read_text('utf8'));before=copy.deepcopy(tree)
 main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 fn=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name==('learn' if key=='h1' else 'work'))
 output='out' if key=='h1' else 'OUT'
 body=f"""from mixed_precision_step_benchmark_runtime_v3 import run as run_precision_benchmark
run_precision_benchmark(runner,src,task,json.loads((B/'GO_PRODUCTION.json').read_bytes()) if {key!r}=='h1' else json.loads((J/'GO_PRODUCTION.json').read_bytes()),{output},{key!r})
receipt=json.loads(({output}/'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json').read_bytes())
assert receipt['suite_execution_complete'] and receipt['not_a_qualified_continuation_source']
put({output}/'FINAL.json',dict(epoch=time.time(),passed=True,benchmark_execution_receipt_only=True,benchmark_result_path=str({output}/'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json'),final=None,not_a_training_FINAL_model=True,not_a_qualified_continuation_source=True,not_270mm_or_recovery_skill_pass=True))
"""
 fn.body=ast.parse(body).body;ast.fix_missing_locations(tree)
 name='h1_precision_step_benchmark_worker_v1.py' if key=='h1' else 'recovery_precision_step_benchmark_worker_v1.py';p=B/name
 with p.open('x',encoding='utf8') as f:f.write(ast.unparse(tree)+'\n')
 def normalized(t):
  t=copy.deepcopy(t);m=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='main');f=next(n for n in m.body if isinstance(n,ast.FunctionDef) and n.name==('learn' if key=='h1' else 'work'));f.body=[ast.Pass()];return ast.dump(t)
 assert normalized(before)==normalized(tree)
 shutil.copy2(runtime,B/runtime.name)
 task=json.loads((B/'job0/TASK.json').read_bytes());task.update(performance_benchmark_only=True,benchmark_modes=['fp32','bf16','fp16'],independent_source_clones_per_mode=True,benchmark_complete_updates_per_mode=6,benchmark_warmup_updates_per_mode=2,benchmark_models_not_qualified_continuation_sources=True,original_physics_command_goal_reward_PPO_base_unchanged=True,benchmark_only_MLP_autocast_and_FP16_loss_scaler_copy=True)
 (B/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 q['specs'][key].update(production_script=name,performance_benchmark_only=True)
 rows=[]
 for f in sorted(B.rglob('*')):
  if not f.is_file() or f.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in f.parts:continue
  rel=f.relative_to(B).as_posix()
  if f.suffix=='.py':ast.parse(f.read_text('utf8'))
  if f.suffix in ('.pt','.npz','.usd','.stl'):
   assert rel in known and f.stat().st_size==known[rel]['bytes'];sha=known[rel]['SHA']
  else:sha=H(f)
  rows.append(dict(relative=rel,bytes=f.stat().st_size,SHA=sha))
 manifest=dict(oldmanifest,files=rows,performance_benchmark_only=True,benchmark_models_not_qualified_sources=True)
 (B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');q['specs'][key]['manifest_SHA']=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 changes.append(dict(key=key,benchmark_worker=str(p),SHA=H(p),original_worker_preserved=str(source),original_worker_SHA=H(source),only_inner_learning_callback_AST_replaced=True,task_mode_explicit_benchmark_only=True,source_SHA=q['specs'][key]['source_SHA'],source_Adam=q['specs'][key]['source_Adamstep']))
q.update(performance_benchmark_only=True,no_benchmark_model_source_promotion=True)
(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(q,indent=2),encoding='utf8')
for mode in ('paired_controllers','controllers'):
 for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_real_gpu_resource_v1.py'):
  base=M.parent/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025'/mode/name
  assert base.read_bytes()==(M/mode/name).read_bytes()
with (R/'BENCHMARK_PAYLOAD_SOURCE_QUALIFICATION_AND_NO_PROMOTION_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,changes=changes,runtime=str(runtime),runtime_SHA=H(runtime),original_owner_node_account_caps_resources_byteexact=True,benchmark_FINAL_json_is_execution_receipt_with_final_null_not_checkpoint=True,dedicated_collector_required_not_normal_pair_model_collector=True,normal_source67_remains_latestqualified=True,no_remote_Task_or_GO_yet=True),f,indent=2)
print(json.dumps(dict(passed=True,keys=list(q['specs']),same_complete67_sources=q['sources'],benchmark_only=True,no_GO=True)))

