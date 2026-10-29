"""Complete source-only closure/constructor/denominator/reader tests; no policy IO."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1';EARLY=L/'E0_EARLY_ORIGINAL_RESAMPLE_LIFECYCLE_SOURCE_20261029_V1'
WORKER='evaluate_E0_adapted82_new86_frozen1000_once_v2_early.py';SUP='detached_E0_new86_frozen_profile_supervisor_once_v2_early.py';CODE='E0_frozen_actual_receipts_readonly_CODE_v2_early.py';CPU='E0_new86_target_source_SDK_metadata_admission_v2_early.py'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 # Supervisor requires the NEW observation receipt structurally, without declaring adoption a skill threshold.
 p=B/SUP;s=p.read_text(encoding='utf8');old="and (out/'ACTUAL_NATIVE24_E0_40050_CLOCK_QUEUE.json').exists() and not errs";new="and (out/'ACTUAL_NATIVE24_E0_40050_CLOCK_QUEUE.json').exists() and (out/'ACTUAL_E0_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json').exists() and (out/'early_original_resample/E0_REAL_POSTRESTORE_ORIGINAL_RESAMPLE_OBSERVER_ACTUAL.json').exists() and not errs";assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n')
 oldmf=OLD/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';oldraw=oldmf.read_bytes();old=json.loads(oldraw);oldrows={r['relative']:r for r in old['files']}
 # Retain exact original binary metadata, never stat/open those inputs here.
 selected_names={p.name for p in B.iterdir() if p.is_file() and (p.suffix=='.py' and not p.name.startswith(('build_NEW','bind_NEW','test_and_bind')) or p.name in ('GROUND_PROVIDER_SOURCE_CONTRACT.json','REQUIRED_TARGET_COMMANDTERM_METHOD_SOURCE_CONTRACT_V1.json','E0_PREVIOUS_SAMEHOST_FULL1000_WITNESS.json'))}
 rows=[dict(r,reuse_prior_samehost=True) for r in old['files'] if r['relative'].startswith(('runtime/','lib/','source/')) or r['relative'] in ('original_run_manifest.json','E0_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json')]
 for name in sorted(selected_names):
  p=B/name;raw=p.read_bytes();rows.append(dict(relative=name,local_path=str(p),bytes=len(raw),SHA=H(raw),reuse_prior_samehost=name in oldrows and oldrows[name]['SHA']==H(raw) and oldrows[name]['bytes']==len(raw)))
 assert len({r['relative'] for r in rows})==len(rows)
 manifest={k:v for k,v in old.items() if k!='files'};manifest.update(kind='MOD4_E0_ADAPTED82_NEW86_EARLY_SOURCE_INPUT_V2',files=rows,samehost_V1_witness_SHA=H((B/'E0_PREVIOUS_SAMEHOST_FULL1000_WITNESS.json').read_bytes()),early_observer_SHA=H((B/'e0_early_original_resample_passthrough_observer_v1.py').read_bytes()),typed_JSONL_collection='producer_path_bytes_SHA_index_only_no_contents',old_input_manifest_SHA=H(oldraw),new_model_CPU_not_performed_for_source_prep=True)
 put('E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json',manifest)
 maps={r['relative']:Path(r['local_path']) for r in rows};sys.path.insert(0,str(B))
 for p in B.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
 parser=ast.parse((B/CODE).read_bytes());code=next(ast.literal_eval(x.value) for x in parser.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='CODE' for y in x.targets));rt=ast.parse(code)
 closure=load('e0_declared_entry_receipt_cli_contract_v1',B/'e0_declared_entry_receipt_cli_contract_v1.py');cli=closure.validate_entry_cli_learn_hook(maps[closure.ENTRY].read_bytes(),(B/WORKER).read_bytes());graph=closure.selected_receipt_graph((B/WORKER).read_bytes(),(B/SUP).read_bytes(),(B/CODE).read_bytes());deps=closure.declared_import_closure(manifest,lambda rel:maps[rel].read_bytes())
 guard=load('e0_frozen_worker_call_guard_v1',B/'e0_frozen_worker_call_guard_v1.py');call_guard=guard.validate_frozen_worker_calls(ast.parse((B/WORKER).read_bytes()))
 names=['runner.alg.update()','optimizer.step()','actor.train()','runner.learn(1)','loss.backward()','env.update(UNKNOWN=1)'];rejected=[]
 for name in names:
  try:guard.validate_frozen_worker_calls(ast.parse((B/WORKER).read_bytes()+b'\n'+name.encode()))
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Forbidden source call accepted')
 # Real early writer -> supervisor existence -> first & normal CODE literal path graph.
 wt=ast.parse((B/WORKER).read_bytes());calls=[x for x in ast.walk(wt) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='put'];early_name=next(x.args[0].value for x in calls if isinstance(x.args[0],ast.Constant) and 'EARLY_POSTRESTORE' in x.args[0].value)
 actual_read=closure.literal_path_tail(closure.assignment(rt,'early_path'));assert early_name==actual_read=='ACTUAL_E0_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json' and early_name in (B/SUP).read_text(encoding='utf8')
 # Installation/order is actual selected source: runpy -> early install -> ns.main; adopt before For.
 main=next(x for x in wt.body if isinstance(x,ast.FunctionDef) and x.name=='main');install=next(x for x in ast.walk(main) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='early' and x.func.attr=='install');invoke=next(x for x in ast.walk(main) if isinstance(x,ast.Call) and isinstance(x.func,ast.Subscript) and isinstance(x.func.value,ast.Name) and x.func.value.id=='ns');assert install.lineno<invoke.lineno
 work=next(x for x in ast.walk(main) if isinstance(x,ast.FunctionDef) and x.name=='work');adopt=next(x for x in ast.walk(work) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='adopt_only_actually_observed_start');loop=next(x for x in ast.walk(work) if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=='i');assert adopt.lineno<loop.lineno
 base=ast.parse((OLD/'evaluate_E0_adapted82_new86_frozen1000_once_v1.py').read_bytes());oldloop=next(x for x in ast.walk(base) if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=='i');assert ast.dump(loop,include_attributes=False)==ast.dump(oldloop,include_attributes=False)
 # Actual Task dict code from installed remote source must satisfy actual selected worker guard.
 remote=ast.parse((B/'remote_E0_new86_early_command_install_and_detach_v2.py').read_bytes());run=next(x for x in remote.body if isinstance(x,ast.FunctionDef) and x.name=='run');taskexpr=next(x.value for x in ast.walk(run) if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='task' for y in x.targets))
 abstract={}
 for kw in taskexpr.keywords:
  try:abstract[kw.arg]=ast.literal_eval(kw.value)
  except (ValueError,TypeError):abstract[kw.arg]='actual-runtime-bound-pending'
 abstract['actual_private_GPU_EX_held_by_parent']=True
 guard_fn=next(x for x in wt.body if isinstance(x,ast.FunctionDef) and x.name=='guard');scope={'MODEL_SHA':old['typed_source_SHA']};exec(compile(ast.Module(body=[guard_fn],type_ignores=[]),'<selected guard>','exec'),scope);scope['guard'](abstract)
 for key,bad in [('num_envs',4096),('controls',2000),('original_Adam',641201),('original_LR',.0001)]:
  wrong=dict(abstract);wrong[key]=bad
  try:scope['guard'](wrong)
  except AssertionError:rejected.append('actual selected Task '+key)
  else:raise AssertionError('Wrong actual Task accepted')
 # SOURCE text install only for original source functions. Do not copy old binaries.
 local=B/'reports/FRESH_LOCAL_SOURCE_TEXT_INSTALL';local.mkdir()
 for row in rows:
  rel=Path(row['relative'])
  if rel.suffix=='.py' or rel.name in ('GROUND_PROVIDER_SOURCE_CONTRACT.json','REQUIRED_TARGET_COMMANDTERM_METHOD_SOURCE_CONTRACT_V1.json'):
   raw=maps[row['relative']].read_bytes();assert H(raw)==row['SHA'];p=local/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 import torch
 assert not torch.cuda.is_initialized()
 fixture=load('selected_telemetry_constructor_API_fixture_v1',B/'selected_telemetry_constructor_API_fixture_v1.py');constructor=fixture.run_selected_constructor_fixture(local,'E0',torch,output=B/'reports/FRESH_SELECTED_CONSTRUCTOR_API_V2')
 live=load('E0_actual_target_method_lifecycle_CPU_fixture_v2',B/'E0_actual_target_method_lifecycle_CPU_fixture_v2.py')
 command=(EARLY/'REFERENCE_OLD210_EXACT_UTF8_command_manager.py.txt').read_bytes();velocity=(EARLY/'REFERENCE_OLD210_EXACT_UTF8_velocity_command.py.txt').read_bytes()
 early_proof=live.run_fixture(local,torch,command,velocity,B/'reports/FRESH_METHOD_REFERENCE_CPU_V2')
 assert early_proof['passed'] and early_proof['acted10_zero5_complete5_reset3_window2_fresh_fixture'] and not torch.cuda.is_initialized()
 # Execute ONLY selected actual metadata producer-stat block with fresh synthetic JSONL.
 branch=next(x for x in rt.body if isinstance(x,ast.If) and any(isinstance(y,ast.Constant) and y.value=='*.jsonl.PRODUCER_INDEX_ACTUAL.json' for y in ast.walk(x)))
 root=B/'reports/FRESH_METHOD_REFERENCE_CPU_V2';producer_scope=dict(F=root,J=root,mode='terminal',Path=Path,MODEL=old['typed_source_SHA'],read=lambda p:json.loads(p.read_bytes()),large=[],jsonl_indexes=[])
 original_read=Path.read_bytes
 def no_raw_read(p):
  assert p.suffix!='.jsonl','Collector attempted raw JSONL content read';return original_read(p)
 Path.read_bytes=no_raw_read
 try:exec(compile(ast.Module(body=[branch],type_ignores=[]),'<actual selected producer index metadata-only collector>','exec'),producer_scope)
 finally:Path.read_bytes=original_read
 assert len(producer_scope['jsonl_indexes'])==2 and sum(x['rows'] for x in producer_scope['jsonl_indexes'])==41
 put('reports/COMPLETE_SELECTED_E0_V2_SOURCE_TASK_CONSTRUCTOR_METHODS_READERS_CPU_ACTUAL.json',dict(passed=True,scope='LOCAL SOURCE + fresh CPU only, not actual target SDK/GPU',local_torch=torch.__version__,target_actual_method_binding_pending=True,entry_CLI_hook=cli,old_and_new_mean_numerical_For_AST_exact=True,original_numerical_For_AST_SHA=H(ast.dump(loop,include_attributes=False).encode()),restore_native_final_receipt_graph=graph,early_receipt_graph=dict(writer=early_name,supervisor_exists=early_name,first_and_normal_CODE=actual_read),actual_Task_selected_worker_guard_passed=True,negative_cases=rejected,dependency_closure=deps,worker_call_guard=call_guard,actual_selected_constructor_lifecycle=constructor,actual_source_method_reference_lifecycle=early_proof,actual_selected_JSONL_metadata_collector_two_indexes41rows_without_any_JSONL_content_read=True,samehost_reuse_count=sum(bool(r['reuse_prior_samehost']) for r in rows),samehost_reuse_original_SHA_bytes_metadata_only=True,source_model_or_raw_or_SDK_or_remote_reads=0))
 print(json.dumps(dict(passed=True,source_only=True,files=len(rows),reuse=sum(bool(r['reuse_prior_samehost']) for r in rows),actual_mean_For_AST_exact=True,actual_selected_constructor_and_early_source_methods=True,JSONL_stat_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('reports/ORIGINAL_COMPLETE_E0_V2_SOURCE_FIXTURE_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_model_raw_SDK_or_remote_reads=True));raise
