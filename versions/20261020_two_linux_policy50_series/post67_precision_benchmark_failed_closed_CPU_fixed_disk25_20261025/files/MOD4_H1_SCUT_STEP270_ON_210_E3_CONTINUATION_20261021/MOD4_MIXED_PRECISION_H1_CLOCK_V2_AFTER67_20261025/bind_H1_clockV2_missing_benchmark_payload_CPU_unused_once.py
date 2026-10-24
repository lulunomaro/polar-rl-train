from pathlib import Path
import ast,copy,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;R=N/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();p=R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json';q=json.loads(p.read_bytes());assert set(q['specs'])=={'h1'} and q['performance_benchmark_only']
with (R/'PRE_BIND_BENCHMARK_PAYLOAD_CONFIG_EXACT.json').open('xb') as f:f.write(p.read_bytes())
B=Path(q['payloads']['h1']);mp=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'
with (R/'PRE_BIND_BENCHMARK_MANIFEST_EXACT.json').open('xb') as f:f.write(mp.read_bytes())
old=json.loads(mp.read_bytes());known={r['relative']:r for r in old['files']};source=B/'h1_step270_production_worker_v1.py';tree=ast.parse(source.read_text('utf8'));base=copy.deepcopy(tree);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');fn=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='learn')
fn.body=ast.parse("""from mixed_precision_step_benchmark_runtime_v6 import run as run_precision_benchmark
run_precision_benchmark(runner,src,task,json.loads((B/'GO_PRODUCTION.json').read_bytes()),out,'h1')
receipt=json.loads((out/'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json').read_bytes())
assert receipt['suite_execution_complete'] and receipt['not_a_qualified_continuation_source']
put(out/'FINAL.json',dict(epoch=time.time(),passed=True,benchmark_execution_receipt_only=True,benchmark_result_path=str(out/'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json'),final=None,not_a_training_FINAL_model=True,not_a_qualified_continuation_source=True,not_270mm_or_recovery_skill_pass=True))
""").body;ast.fix_missing_locations(tree)
def norm(t):
 t=copy.deepcopy(t);m=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='main');f=next(n for n in m.body if isinstance(n,ast.FunctionDef) and n.name=='learn');f.body=[ast.Pass()];return ast.dump(t)
assert norm(base)==norm(tree)
name='h1_precision_clockV2_missing_benchmark_worker_v1.py'
with (B/name).open('x',encoding='utf8') as f:f.write(ast.unparse(tree)+'\n')
shutil.copy2(N/'mixed_precision_step_benchmark_runtime_v6.py',B/'mixed_precision_step_benchmark_runtime_v6.py')
taskp=B/'job0/TASK.json'
with (R/'PRE_BIND_BENCHMARK_TASK_EXACT.json').open('xb') as f:f.write(taskp.read_bytes())
task=json.loads(taskp.read_bytes());task.update(performance_benchmark_only=True,benchmark_modes=['fp32','bf16','fp16'],benchmark_complete_updates_per_mode=6,benchmark_warmup_updates_per_mode=2,benchmark_models_not_qualified_continuation_sources=True,original_H1_trace_and_approved_retention_preserved=True,benchmark_only_correct_H1_integrated4_clock_no_E3_feedback_attribute=True)
taskp.write_text(json.dumps(task,indent=2),encoding='utf8');q['specs']['h1'].update(production_script=name,performance_benchmark_only=True);rows=[]
for f in sorted(B.rglob('*')):
 if not f.is_file() or f.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in f.parts:continue
 rel=f.relative_to(B).as_posix()
 if f.suffix=='.py':ast.parse(f.read_text('utf8'))
 if f.suffix in ('.pt','.npz','.usd','.stl'):assert rel in known and f.stat().st_size==known[rel]['bytes'];sha=known[rel]['SHA']
 else:sha=H(f)
 rows.append(dict(relative=rel,bytes=f.stat().st_size,SHA=sha))
mp.write_text(json.dumps(dict(old,files=rows,performance_benchmark_only=True),indent=2),encoding='utf8');q['specs']['h1']['manifest_SHA']=H(mp);q.update(no_benchmark_model_source_promotion=True)
p.write_text(json.dumps(q,indent=2),encoding='utf8')
with (R/'H1_CLOCKV2_MISSING_BENCHMARK_PAYLOAD_BINDING_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,old_worker=str(source),old_worker_SHA=H(source),new_worker=str(B/name),new_worker_SHA=H(B/name),only_inner_learning_callback_AST_replaced=True,original_task_manifest_payload_config_exact_before_versions_preserved=True,source_SHA=q['sources']['h1']['SHA'],source_Adam=q['sources']['h1']['Adam'],E3_not_repeated=True,new_runtime_SHA=H(B/'mixed_precision_step_benchmark_runtime_v6.py'),benchmark_execution_receipt_not_training_FINAL=True,original_owner_caps3900_reserve7800_guard82512_unchanged=True,no_GO_yet=True),f,indent=2)
print(json.dumps(dict(passed=True,H1_only=True,source=q['sources']['h1'],benchmark_only=True,no_GO=True)))

