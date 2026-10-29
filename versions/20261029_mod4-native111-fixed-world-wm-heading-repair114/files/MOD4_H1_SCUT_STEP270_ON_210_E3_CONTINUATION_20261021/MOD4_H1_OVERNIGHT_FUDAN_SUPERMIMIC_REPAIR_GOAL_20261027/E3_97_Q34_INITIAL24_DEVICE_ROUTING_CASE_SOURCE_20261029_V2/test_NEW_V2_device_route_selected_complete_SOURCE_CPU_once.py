"""New V2 source proof. CPU tensors and label-spies only; no CUDA/SDK/model."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;OLD=B.parent/'E3_97_Q34_INITIAL24_ORIGINAL_QUERY_CASE_SOURCE_20261029_V1'
HOOK='e3_declared_fall_existing_query_observer_v1.py';WORK='evaluate_E3_adapted97_source210_initial24_original_queries_once_v1.py'
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,x):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2,allow_nan=False)
def load(n):
 p=B/(n+'.py');s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 sys.path.insert(0,str(B))
 for p in B.glob('*.py'):ast.parse(p.read_bytes(),str(p))
 hraw=(B/HOOK).read_bytes();wraw=(B/WORK).read_bytes();h0=(OLD/HOOK).read_bytes();w0=(OLD/WORK).read_bytes()
 deriv=json.loads((B/'EXACT_V2_DIAGNOSTIC_INDEX_AND_NAMESPACE_SOURCE_INVERSE_OPERATIONS.json').read_bytes())
 for name,source in ((HOOK,h0),(WORK,w0)):
  row=next(r for r in deriv['files'] if r['name']==name);s=(B/name).read_text()
  for op in reversed(row['operations']):assert s.count(op['new'])==op['count'],op;s=s.replace(op['new'],op['old'])
  assert s.encode()==source and H(source)==row['source_SHA']
 oldtree=ast.parse(h0);newtree=ast.parse(hraw)
 for name in ('closure_overlay_source','install_before_resume'):
  f=lambda tree:next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
  assert ast.dump(f(oldtree),include_attributes=False)==ast.dump(f(newtree),include_attributes=False)
 def method(tree,name):return next(n for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name==name)
 for name in ('bind_original_limit_read','snapshot','finish'):
  assert ast.dump(method(oldtree,name),include_attributes=False)==ast.dump(method(newtree,name),include_attributes=False)
 original_physical_calls={}
 for tree,key in ((oldtree,'old'),(newtree,'new')):
  original_physical_calls[key]=[ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('original_joint','original_root','original_apply')]
 assert original_physical_calls['old']==original_physical_calls['new'] and len(original_physical_calls['new'])==3
 guard=load('e3_initial_query_integration_contract_v1');integration=guard.validate_selected_worker(wraw)
 dg=load('diagnostic_device_route_fixture_v2');route_guard=dg.validate_index_route_source(hraw);negative=[]
 for label,old,new in [('wrong_index_dtype_from_float_target','dtype=index.dtype','dtype=value.dtype'),('unrouted_direct_index','value[index.to(device=value.device,dtype=index.dtype)]','value[index]'),('missing_comparison_route','compare_q=q.to(device=limits.device)','compare_q=q')]:
  assert hraw.decode().count(old)==1
  try:dg.validate_index_route_source(hraw.decode().replace(old,new).encode())
  except (AssertionError,StopIteration):negative.append(label)
  else:raise AssertionError('Rejected route source accepted: '+label)
 # Actual selected entry/CLI/learnhook, source import closure, receipt ABI.
 m=json.loads((B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());rows={r['relative']:r for r in m['files']}
 entry=load('e3_declared_entry_receipt_cli_contract_v1');cli=entry.validate_entry_cli_learn_hook(Path(rows[entry.ENTRY]['local_path']).read_bytes(),wraw);receipt=entry.selected_receipt_graph(wraw,(B/entry.SUP).read_bytes(),(B/entry.CODE).read_bytes());closure=entry.declared_import_closure(m,lambda rel:Path(rows[rel]['local_path']).read_bytes())
 calls=load('e3_frozen_worker_call_guard_v1').validate_frozen_worker_calls(ast.parse(wraw))
 oldm=json.loads((OLD/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());oldrows={r['relative']:r for r in oldm['files']};protected=[r for r in oldrows if r.startswith(('runtime/','source/'))];assert all(rows[r]==oldrows[r] for r in protected)
 # Source-only API lifecycle includes REAL CPU tensors plus explicit device-label proxies.
 fresh=load('selected_original_query_API_fixture_v1').run_selected_fixture(B)
 # V1 snapshot is evidence of physical24 even though its aggregate query gate failed.
 actual=json.loads((OLD/'reports/E3_SOURCE210_FIRST_ORIGINAL_RETURNED_ACTUAL.json').read_bytes())
 code=ast.literal_eval(next(n.value for n in ast.parse((B/entry.CODE).read_bytes()).body if isinstance(n,ast.Assign)));ct=ast.parse(code);fn=next(n for n in ct.body if isinstance(n,ast.FunctionDef) and n.name=='full_coverage');scope={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'source_only_pure_full_coverage','exec'),scope)
 result=actual['original_terminal']['result'];assert scope['full_coverage'](True,result) and not scope['full_coverage'](False,result)
 short=copy.deepcopy(result);short['controls']=23;assert not scope['full_coverage'](True,short)
 assert 'requested24_controls_physically_completed=physical24' in code and 'physical24_does_not_imply_diagnostic_valid=True' in code
 assert '360 if mode==\'first\' else 850' in code and 'nominal-time.time()<=900' in code
 report=dict(passed=True,scope='LOCAL SOURCE + real CPU synthetic tensors and symbolic device-label spy, NOT actual CUDA/SDK',actual_CUDA_device_execution_tested=False,hook_SHA=H(hraw),worker_SHA=H(wraw),exact_hook_inverse_original_SHA=H(h0),exact_worker_inverse_original_SHA=H(w0),worker_only_namespace_and_typed_kind_changes_no_numeric_loop_change=True,original_full20k_loop_and_actor_VECstep_and_2mm_guard_unchanged=True,original_closure_overlay_install_and_limit_clone_snapshot_finish_AST_unchanged=True,original_joint_root_queue_calls_each_once_and_identical_AST=True,device_route_source_guard=route_guard,selected_hook_install_limit_bind_finish_contract=integration,fresh_API_fixture=fresh,rejected_negative_route_sources=negative,base_original_V1_physical24_true_query_false_still_preserved=True,new_reader_actual_physical24_field_separate_without_weakening_diagnostic_gate=True,declared_entry_CLI_hook=cli,worker_sup_first_normal_receipt_graph=receipt,declared_import_source_closure=closure,strict_no_learning_call_guard=calls,unchanged_original_runtime_model_asset_manifest_rows=len(protected),PT_NPZ_USD_raw_model_GPU_SDK_remote_calls=False,target_new_actual_admission_pending=True)
 put('ACTUAL_NEW_V2_DEVICE_ROUTE_COMPLETE_SOURCE_CPU_PROOF.json',report)
 print(json.dumps(dict(passed=True,negative_routes=negative,protected_rows=len(protected),hook_SHA=H(hraw),no_CUDA_execution=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_NEW_V2_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_GPU_model_or_remote=True));raise
