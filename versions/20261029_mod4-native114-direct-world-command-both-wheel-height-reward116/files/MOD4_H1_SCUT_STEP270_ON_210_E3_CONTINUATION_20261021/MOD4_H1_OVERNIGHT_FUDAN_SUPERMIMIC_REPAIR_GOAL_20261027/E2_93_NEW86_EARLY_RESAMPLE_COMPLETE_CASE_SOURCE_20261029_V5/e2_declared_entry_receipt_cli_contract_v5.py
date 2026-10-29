"""Pure source AST contract: original E2 entry/CLI/learn hook/receipt closure."""
from pathlib import Path,PurePosixPath
import ast,hashlib,sys
ENTRY='runtime/isaac/mod4/train_E2_full_resume_v1.py'
ENTRY_SHA='e002234d12146cba31e6350e3ede6b362a66a5644b9404429d863512c6183812'
WORKER='evaluate_E2_adapted93_new86_frozen900_once_v1.py'
SUP='detached_E2_new86_frozen_profile_supervisor_once_v1.py'
CODE='E2_frozen_actual_receipts_readonly_CODE_v4.py'
def K(n):return ast.dump(n,include_attributes=False)
def assignment(tree,name):return next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
def literal_path_tail(n):
 assert isinstance(n,ast.BinOp) and isinstance(n.op,ast.Div) and isinstance(n.right,ast.Constant) and isinstance(n.right.value,str);return n.right.value
def put_calls(tree):return [n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='put' and n.args and isinstance(n.args[0],ast.Constant)]
def dict_keywords(n):return {x.arg:x.value for x in n.keywords} if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict' else {}
def selected_receipt_graph(worker_raw,sup_raw,code_raw):
 wt=ast.parse(worker_raw);st=ast.parse(sup_raw);container=ast.parse(code_raw);code=ast.literal_eval(assignment(container,'CODE'));rt=ast.parse(code)
 calls=put_calls(wt)
 restore=next(n.args[0].value for n in calls if len(n.args)>1 and 'Adam_step' in dict_keywords(n.args[1]))
 native=next(n.args[0].value for n in calls if len(n.args)>1 and {'controls','physics_callbacks','feedback_samples','legs_queue_apply','wheels_queue_apply'}<=set(dict_keywords(n.args[1])))
 final=next(n.args[0].value for n in calls if len(n.args)>1 and 'requested_controls' in dict_keywords(n.args[1]))
 sup_native=next(literal_path_tail(n.func.value) for n in ast.walk(st) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='exists' and isinstance(n.func.value,ast.BinOp) and str(literal_path_tail(n.func.value)).startswith('ACTUAL_NATIVE'))
 sup_final_path=literal_path_tail(assignment(st,'result'));assert PurePosixPath(sup_final_path).parent==PurePosixPath('frozen_regression');sup_final=PurePosixPath(sup_final_path).name;sup_terminal=next(n.args[0].value for n in put_calls(st) if n.args[0].value.endswith('ORIGINAL_WAITED_TERMINAL_ACTUAL.json'))
 read_restore=literal_path_tail(assignment(rt,'restore'));read_native=literal_path_tail(assignment(rt,'native'));read_terminal=literal_path_tail(assignment(rt,'terminal'))
 assert restore==read_restore,(restore,read_restore)
 assert native==sup_native==read_native=='ACTUAL_NATIVE24_E2_40050_CLOCK_QUEUE.json',(native,sup_native,read_native)
 assert final==sup_final and sup_terminal==read_terminal
 return dict(passed=True,writer_fullrestore=restore,reader_fullrestore=read_restore,writer_native=native,supervisor_native=sup_native,first_and_normal_CODE_native=read_native,writer_final=final,supervisor_final=sup_final,supervisor_terminal=sup_terminal,first_and_normal_CODE_terminal=read_terminal)
def validate_entry_cli_learn_hook(entry_raw,worker_raw,sdk_launcher_raw=None):
 assert hashlib.sha256(entry_raw).hexdigest()==ENTRY_SHA
 et=ast.parse(entry_raw);wt=ast.parse(worker_raw);main=next(n for n in et.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 assert literal_path_tail(assignment(wt,'entry'))==PurePosixPath(ENTRY).name
 own_flags={a.value for n in ast.walk(et) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' for a in n.args if isinstance(a,ast.Constant) and isinstance(a.value,str) and a.value.startswith('--')}
 assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='AppLauncher' and n.func.attr=='add_app_launcher_args' for n in ast.walk(et))
 argv=next(n.value for n in ast.walk(wt) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='sys' and t.attr=='argv' for t in n.targets));assert isinstance(argv,ast.List) and K(argv.elts[0])==K(ast.parse('str(entry)',mode='eval').body)
 flags={};i=1
 while i<len(argv.elts):
  n=argv.elts[i];assert isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('--');flag=n.value;assert flag not in flags;i+=1
  if flag=='--headless':flags[flag]=None;continue
  assert i<len(argv.elts);flags[flag]=argv.elts[i];i+=1
 inherited=set(flags)-own_flags;assert inherited=={'--headless','--device'}
 if sdk_launcher_raw is not None:
  sdk=ast.parse(sdk_launcher_raw);assert any(isinstance(n,ast.FunctionDef) and n.name=='add_app_launcher_args' for n in ast.walk(sdk));declared={n.value for n in ast.walk(sdk) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('--')};assert inherited<=declared
 for name,value in {'--num_envs':'20000','--steps_per_env':'24','--learning_rate':'.00022500000000000002','--additional_iterations':'1','--device':'cuda:0'}.items():assert ast.literal_eval(flags[name])==value
 assert K(flags['--init_checkpoint'])==K(ast.parse('str(source)',mode='eval').body)
 hook=next(n for n in ast.walk(main) if isinstance(n,ast.ImportFrom) and n.module=='rescue_training' and any(x.name=='learn' and x.asname=='bounded_learn' for x in n.names));call=next(n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='bounded_learn');assert hook.lineno<call.lineno
 assert not any(isinstance(n,ast.ImportFrom) and n.module=='rescue_training' for n in et.body),'Learner alias must bind INSIDE main after worker patch'
 wmain=next(n for n in wt.body if isinstance(n,ast.FunctionDef) and n.name=='main');patch=next(n for n in ast.walk(wmain) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='rescue_training' and t.attr=='learn' for t in n.targets));assert isinstance(patch.value,ast.Name) and patch.value.id=='work'
 invoke=next(n for n in ast.walk(wmain) if isinstance(n,ast.Call) and isinstance(n.func,ast.Subscript) and isinstance(n.func.value,ast.Name) and n.func.value.id=='ns' and isinstance(n.func.slice,ast.Constant) and n.func.slice.value=='main');assert patch.lineno<invoke.lineno
 run=next(n for n in ast.walk(wt) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='runpy' and n.func.attr=='run_path');run_name=next(x.value for x in run.keywords if x.arg=='run_name');assert isinstance(run_name,ast.Constant) and run_name.value!='__main__'
 return dict(passed=True,declared_original_entry=ENTRY,entry_SHA=ENTRY_SHA,own_parser_flags=sorted(own_flags),selected_worker_flags=sorted(flags),SDK_inherited_flags=sorted(inherited),actual_target_SDK_parser_source_checked=sdk_launcher_raw is not None,runpy_nonmain=True,worker_patch_precedes_ns_main=True,entry_learn_alias_import_inside_main_after_patch=True,no_production_learner_called_by_worker=True)
def declared_import_closure(manifest,read_relative):
 rows={r['relative']:r for r in manifest['files']};assert ENTRY in rows and rows[ENTRY]['SHA']==ENTRY_SHA
 roots=['runtime/isaac/','runtime/isaac/mod4/','','lib/','runtime/'];modules={}
 for prefix in reversed(roots):
  for relative,row in rows.items():
   if relative.startswith(prefix) and relative.endswith('.py'):
    tail=relative[len(prefix):]
    if '/' not in tail:modules[tail[:-3]]=relative
 modules['zonglin2_app_launcher']='lib/zonglin2_app_launcher.py';modules['directional_spin_runtime']='runtime/isaac/mod4/e2_directional_spin_runtime_v1.py'
 pending=[ENTRY,WORKER,SUP,'E2_new86_target_source_SDK_metadata_admission_v1.py'];visited={};external=set();stdlib=set(sys.stdlib_module_names)|{'__future__'}
 while pending:
  relative=pending.pop()
  if relative in visited:continue
  raw=read_relative(relative);assert hashlib.sha256(raw).hexdigest()==rows[relative]['SHA'];tree=ast.parse(raw);visited[relative]=rows[relative]['SHA']
  for node in ast.walk(tree):
   imports=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else []
   for name in imports:
    if name in modules:pending.append(modules[name])
    elif name not in stdlib:
     assert not name.startswith(('e2_','E2_')),'Missing declared internal E2 module: '+name
     external.add(name)
 disabled={'terrain_cfg':'RM_MOD4_MAP empty: attach_rmuc2026_terrain returns before import','route_commands':'delivered rmuc2026 route factory not selected by empty map/flat E2 original command','shared_raycast':'TERRAIN flat: original ground getter/flat return, no field raycast'}
 return dict(passed=True,declared_input_count=len(rows),entry_and_internal_import_source_SHA_closure=visited,external_SDK_or_package_roots_explicit=sorted(external-set(disabled)),unselected_conditional_incoming_map_imports={k:v for k,v in disabled.items() if k in external},selected_domain='original E2_WORLD_MOVING_SIGNED4 / RM_MOD4_MAP empty / RM_MOD4_TERRAIN flat',SDK_late_imports_not_executed_before_App=True,all_declared_input_files_still_require_original_postcopy_fullSHA=True)
def validate_installed_entry_contract(J,manifest,sdk_launcher_path):
 J=Path(J);rows={r['relative']:r for r in manifest['files']}
 for rel in (ENTRY,WORKER,SUP,CODE):assert rel in rows and (J/rel).is_file(),rel
 result=dict(entry_CLI_learn_hook=validate_entry_cli_learn_hook((J/ENTRY).read_bytes(),(J/WORKER).read_bytes(),Path(sdk_launcher_path).read_bytes()),receipt_graph=selected_receipt_graph((J/WORKER).read_bytes(),(J/SUP).read_bytes(),(J/CODE).read_bytes()),dependency_closure=declared_import_closure(manifest,lambda relative:(J/relative).read_bytes()),actual_SDK_parser_source=str(sdk_launcher_path),actual_SDK_parser_source_SHA=hashlib.sha256(Path(sdk_launcher_path).read_bytes()).hexdigest())
 return dict(passed=True,kind='original_E2_fullstate_entry_declared_dependency_CLI_hook_and_receipt_contract_v1',**result)
