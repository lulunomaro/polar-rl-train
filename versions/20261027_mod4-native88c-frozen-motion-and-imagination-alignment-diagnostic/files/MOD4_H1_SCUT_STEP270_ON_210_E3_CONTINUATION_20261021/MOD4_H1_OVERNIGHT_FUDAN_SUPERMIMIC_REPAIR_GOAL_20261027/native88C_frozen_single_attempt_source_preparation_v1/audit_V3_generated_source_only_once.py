"""Final source audit; no old fixture, model, SDK, actor or physics execution."""
from pathlib import Path
import ast,json,hashlib,symtable,builtins
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;OLD=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/code'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fns(p):return {n.name:ast.dump(n) for n in ast.parse(p.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
checks={}
checks['environment_function_AST_exact']=fns(OLD/'native87R5_eval_environment_v1.py')['environment']==fns(D/'native88C_eval_environment_v1.py')['environment']
checks['own_PID_guard_all_definition_AST_exact']=fns(OLD/'native87R5_own_pid_out_guard_v1.py')==fns(D/'native88C_own_pid_out_guard_v1.py')
checks['own_PID_guard_normalized_LF_exact']=(OLD/'native87R5_own_pid_out_guard_v1.py').read_text('utf8')==(D/'native88C_own_pid_out_guard_v1.py').read_text('utf8')
checks['history_padding_AST_exact']=fns(OLD/'native87R5_frozen_acceptance_driver_v1.py')['fresh_history']==fns(D/'native88C_frozen_acceptance_driver_v1.py')['fresh_history']
checks['termination_cache_contract_AST_exact']=fns(OLD/'native87R5_frozen_acceptance_driver_v1.py')['termination_cache_contract']==fns(D/'native88C_frozen_acceptance_driver_v1.py')['termination_cache_contract']
core=('native88C_frozen_single_sdk_entry_unused_once.py','native88C_frozen_acceptance_driver_v1.py','native88C_frozen_acceptance_contract_v1.py','native88C_eval_environment_v1.py','native88C_own_pid_out_guard_v1.py','native88C_readonly_authority72_guard_v1.py')
names={};bad_calls=[]
for name in core:
 raw=(D/name).read_bytes();tree=ast.parse(raw);st=symtable.symtable(raw.decode(),'newsource','exec');bound={s.get_name() for s in st.get_symbols() if s.is_assigned() or s.is_imported() or s.is_namespace()};known=bound|set(dir(builtins))|{'__file__','__name__','__package__','__builtins__'};missing=[]
 def walk(t,path):
  for s in t.get_symbols():
   if s.is_global() and s.is_referenced() and s.get_name() not in known:missing.append(dict(scope=path,name=s.get_name()))
  for child in t.get_children():walk(child,path+'/'+child.get_name())
 walk(st,'module');names[name]=missing
 for n in ast.walk(tree):
  if isinstance(n,ast.Call):
   text=ast.unparse(n.func)
   if text in ('learner.collect','learner.train','optimizer.step','wm','self.wm') or text.endswith(('obs_norm.update','goal_norm.update','in_norm.update','out_norm.update')):bad_calls.append(dict(file=name,call=text))
checks['no_source_unresolved_globals']=not any(names.values());checks['no_learning_WM_or_normalizer_update_calls']=not bad_calls
entry=(D/core[0]).read_text('utf8');driver=(D/core[1]).read_text('utf8')
checks['selected_GPU_only_no_process_iteration']='process_iter' not in entry and "['nvidia-smi','-i',q['GPU_UUID'],'--query-compute-apps=gpu_uuid'" in entry
checks['one_model_deserialization_entry']=entry.count('torch.load(')==1
checks['configuration_factory_only_no_training_main']="run_name='native88C_frozen_N1_configuration_only'" in entry and "ns['main'](" not in entry
checks['source_C_400N_and_V2_explicit']='check_runtime_source' in entry and 'check_actual_new_gas' in entry and 'OwnStepDifferentiableMdpV2' in entry and 'expected_native_contract' in driver
checks['exact_single_case_caps_preserved']='range(500)' in driver and "self.count<=2000" in driver and 'if bool(done[0])' in driver
assert all(checks.values()),(checks,names,bad_calls)
with (D/'FINAL_SOURCE_AUDIT_V3_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,checks=checks,unresolved_globals=names,bad_calls=bad_calls,
 V2_failure_classification='Entry generated and retained, subsequent overly strict own-PID byteidentity assertion failed only due to CRLF→LF source serialization; normalized text and all function AST are exact. No evaluation ran.',
 old_actual_R2_source_pins={p.name:H(p) for p in OLD.glob('*.py')},new_core_pins={n:H(D/n) for n in core},
 actual_model_GPU_SDK_actor_or_physics_run=False,source_only_not_runtime_qualification=True),f,indent=2)
print(json.dumps(dict(passed=True,checks=len(checks),unresolved_source_names=names)))
