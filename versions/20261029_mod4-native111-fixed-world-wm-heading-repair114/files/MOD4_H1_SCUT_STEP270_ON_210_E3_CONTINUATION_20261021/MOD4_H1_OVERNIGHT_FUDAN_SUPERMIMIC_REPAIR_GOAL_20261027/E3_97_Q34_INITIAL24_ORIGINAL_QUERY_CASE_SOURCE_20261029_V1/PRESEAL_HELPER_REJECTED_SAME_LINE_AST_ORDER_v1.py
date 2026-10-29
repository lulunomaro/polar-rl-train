"""Pure text/source contract. Does not import SDK, policy or checkpoint readers."""
from pathlib import Path
import ast,hashlib,json
WORK='evaluate_E3_adapted97_source210_initial24_original_queries_once_v1.py'
HOOK='e3_declared_fall_existing_query_observer_v1.py'
HOOK_SHA='b7cf6da873ab661563f5b924108f23ca4d36636da8caace4eb1174864bcf2c48'
def H(b):return hashlib.sha256(b).hexdigest()
def call(tree,text):
 key=ast.dump(ast.parse(text,mode='eval').body,include_attributes=False)
 found=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.dump(n,include_attributes=False)==key]
 assert len(found)==1,(text,len(found));return found[0]
def validate_selected_worker(raw):
 tree=ast.parse(raw)
 install=call(tree,"install_before_resume(RecoveryEnv,mod4_task,(mod/'mod4_task.py').read_bytes(),observer_factory)")
 invoke=call(tree,"ns['main']()")
 finish=call(tree,'finish_queries()');close=call(tree,"ns['app'].close()")
 bind=call(tree,'bind_original_limits(real,limits[:,gas_ids])')
 original_read=call(tree,'tensor(robot.root_view.get_dof_limits())')
 work=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='work')
 loop=next(n for n in ast.walk(work) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range')
 assert ast.literal_eval(loop.iter.args[0])==24
 assert install.lineno<invoke.lineno<finish.lineno<close.lineno
 assert original_read.lineno<=bind.lineno<loop.lineno
 assert sum(isinstance(n,ast.Attribute) and n.attr=='get_dof_limits' for n in ast.walk(tree))==1
 assert sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='step' for n in ast.walk(tree))==1
 actor=call(tree,'runner.alg.actor(obs,stochastic_output=False)');step=call(tree,'vec.step(action)')
 assert loop.lineno<actor.lineno<step.lineno
 finally_blocks=[n for n in ast.walk(tree) if isinstance(n,ast.Try) and n.finalbody and any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='finish_queries' for f in n.finalbody for x in ast.walk(f))]
 assert len(finally_blocks)==1
 assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='closure_errors' for n in ast.walk(tree))
 return dict(passed=True,hook_installed_before_original_ns_main=True,one_original_limit_read_bound_before_first_actor=True,original_actor_and_vecstep_each_once_per_control=True,controls24=True,finish_in_finally_before_original_app_close=True,no_new_closure_call_in_worker=True)
def validate_installed_query_contract(J,manifest,run_fixture=True):
 J=Path(J);rows={r['relative']:r for r in manifest['files']}
 contract=json.loads((J/'E3_INITIAL_QUERY_SOURCE_CONTRACT.json').read_bytes())
 assert contract['job_root']==str(J) and contract['num_envs']==20000 and contract['controls']==24 and contract['maximum_worker_seconds']==1680 and contract['maximum_supervisor_seconds']==1800
 assert contract['hook_SHA']==HOOK_SHA and H((J/HOOK).read_bytes())==HOOK_SHA
 for rel,sha in [('runtime/isaac/mod4/mod4_task.py',contract['original_task_SHA']),('runtime/isaac/mod4/e3_recovery_runtime_v1.py',contract['original_recovery_SHA'])]:assert rows[rel]['SHA']==sha and H((J/rel).read_bytes())==sha
 cpu_raw=(J/'BASE_E3_V4_SOURCE_SDK_CPU_ACTUAL.json').read_bytes();wait_raw=(J/'BASE_E3_V4_CPU_ORIGINAL_WAIT_ACTUAL.json').read_bytes()
 assert H(cpu_raw)==contract['base_actual_CPU_SHA'] and H(wait_raw)==contract['base_actual_CPU_wait_SHA']
 cpu=json.loads(cpu_raw);wait=json.loads(wait_raw)
 assert cpu['passed'] and cpu['source_SHA']==contract['source_SHA'] and cpu['model_loads_this_metadata_admission']==0
 assert wait['passed'] and wait['actual_waited'] and wait['returncode']==0 and not wait['deadline_terminated'] and wait['report_SHA']==H(cpu_raw)
 assert wait['actual_worker_identity']==contract['base_target_actual_CPU_original_identity']
 assert cpu['versions']=={'torch':'2.10.0+cu128','rsl-rl-lib':'5.0.1','isaacsim':'6.0.1.0','isaaclab':'6.1.14','tensordict':'0.14.1'}
 proof=validate_selected_worker((J/WORK).read_bytes())
 fresh=None
 if run_fixture:
  from selected_original_query_API_fixture_v1 import run_selected_fixture
  fresh=run_selected_fixture(J)
 return dict(passed=True,selected_worker_source=proof,base_actual_same_target_CPU_SHA=H(cpu_raw),base_original_actual_wait_SHA=H(wait_raw),old_target_identity_preserved_not_relabelled=True,model_loads_this_source_metadata_purpose=0,NPZ_reads_this_purpose=0,hook_original_numeric_inverse_and_fresh_API_fixture=fresh,actual_postwrite_substep_or_GPU_diagnostic_still_pending=True)
