"""Fresh source/API proof; no SDK/old model/NPZ/USD/raw/remote/GPU."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback,copy
B=Path(__file__).resolve().parent;L=B.parent
def H(b):return hashlib.sha256(b).hexdigest()
def save(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
def load(n):
 p=B/(n+'.py');s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 for p in B.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
 sys.path.insert(0,str(B))
 helper=load('e3_initial_query_integration_contract_v1');worker=(B/helper.WORK).read_bytes();proof=helper.validate_selected_worker(worker)
 negative=[]
 for label,old,new in [('wrong_control_window','for i in range(24):','for i in range(25):'),('extra_query','bind_original_limits(real,limits[:,gas_ids])','bind_original_limits(real,tensor(robot.root_view.get_dof_limits())[:,gas_ids])'),('missing_finalization','query_results=finish_queries()','query_results=[]')]:
  assert worker.decode().count(old)==1
  try:helper.validate_selected_worker(worker.decode().replace(old,new).encode())
  except (AssertionError,StopIteration):negative.append(label)
  else:raise AssertionError('Rejected source accepted: '+label)
 base=L/'E3_97_SOURCE210_ENTRY_RECEIPT_CLI_CLOSURE_REPAIR_SOURCE_20261029_V4';m=json.loads((B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());rows={r['relative']:r for r in m['files']}
 entry=load('e3_declared_entry_receipt_cli_contract_v1');entry_raw=Path(rows[entry.ENTRY]['local_path']).read_bytes()
 cli=entry.validate_entry_cli_learn_hook(entry_raw,worker)
 graph=entry.selected_receipt_graph(worker,(B/entry.SUP).read_bytes(),(B/entry.CODE).read_bytes())
 closure=entry.declared_import_closure(m,lambda rel:Path(rows[rel]['local_path']).read_bytes())
 guard=load('e3_frozen_worker_call_guard_v1').validate_frozen_worker_calls(ast.parse(worker))
 for label,s in [('learner','runner.alg.update()'),('optimizer','runner.alg.optimizer.step()'),('actor_training','runner.alg.actor.train()')]:
  try:load('e3_frozen_worker_call_guard_v1').validate_frozen_worker_calls(ast.parse(worker+b'\n'+s.encode()))
  except AssertionError:negative.append(label)
  else:raise AssertionError('Forbidden learner operation accepted')
 deriv=json.loads((B/'NEW_WORKER_EXACT_TEXT_DERIVATION_INVERSE_OPERATIONS.json').read_bytes());row=next(x for x in deriv['files'] if x['target_name']==helper.WORK);inverse=worker.decode()
 for op in reversed(row['operations']):
  assert inverse.count(op['new'])==op['count'],op
  inverse=inverse.replace(op['new'],op['old'])
 old_raw=(base/row['source_name']).read_bytes();assert inverse.encode()==old_raw and H(old_raw)==row['source_SHA']
 oldtree=ast.parse(old_raw);newtree=ast.parse(worker)
 def loop(tree):return next(n for f in ast.walk(tree) if isinstance(f,ast.FunctionDef) and f.name=='work' for n in ast.walk(f) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range')
 oldloop=loop(oldtree);newloop=copy.deepcopy(loop(newtree));newloop.iter.args[0]=ast.Constant(value=600)
 assert ast.dump(oldloop,include_attributes=False)==ast.dump(newloop,include_attributes=False)
 # Runtime source/asset rows remain exactly producer metadata; never open assets.
 oldm=json.loads((base/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());oldrows={r['relative']:r for r in oldm['files']}
 protected=[rel for rel in oldrows if rel.startswith('runtime/') or rel.startswith('source/')]
 assert all(rows[rel]==oldrows[rel] for rel in protected)
 from selected_original_query_API_fixture_v1 import run_selected_fixture
 fresh=run_selected_fixture(B)
 # Pure source proves actual caller exports guard, proper queue and new final graph.
 code=ast.literal_eval(next(n.value for n in ast.parse((B/entry.CODE).read_bytes()).body if isinstance(n,ast.Assign)))
 assert "360 if mode=='first' else 850" in code and 'nominal-time.time()<=900' in code
 assert 'E3_RESET_REQUEST_EXISTING_CLOSURE_QUERY_DIAGNOSTIC_ACTUAL.json' in code and 'passed_original_query_diagnostic=query_valid' in code
 import torch
 save('ACTUAL_SELECTED_INITIAL24_COMPLETE_CALLER_SOURCE_CPU_PROOF.json',dict(passed=True,scope='LOCAL fresh CPU synthetic/source only; no target SDK/PhysX/GPU proof',local_torch_version=torch.__version__,local_target_API_not_assumed_identical=True,selected_hook_integration=proof,actual_entry_CLI_learn_hook=cli,worker_supervisor_first_normal_receipt_graph=graph,declared_source_import_closure=closure,strict_no_learner_guard=guard,rejected_negative_sources=negative,exact_worker_inverse_bytes_original_SHA=H(old_raw),original_mean_actor_vecstep_loop_AST_exact_except_declared_600_to24_window=True,protected_original_runtime_model_asset_manifest_rows_equal_count=len(protected),no_original_model_NPZ_USD_raw_stat_hash_or_decode=True,fresh_selected_hook_API_fixture=fresh,first360_normal900_850_original_finite_supervisor1800_worker1680=True,actual_target_fullrestore_native24_original_query_diagnostic_pending=True))
 print(json.dumps(dict(passed=True,negative_cases=len(negative),protected_rows=len(protected),no_remote_or_models=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('LOCAL_SELECTED_CALLER_SOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_remote_or_models=True));raise
