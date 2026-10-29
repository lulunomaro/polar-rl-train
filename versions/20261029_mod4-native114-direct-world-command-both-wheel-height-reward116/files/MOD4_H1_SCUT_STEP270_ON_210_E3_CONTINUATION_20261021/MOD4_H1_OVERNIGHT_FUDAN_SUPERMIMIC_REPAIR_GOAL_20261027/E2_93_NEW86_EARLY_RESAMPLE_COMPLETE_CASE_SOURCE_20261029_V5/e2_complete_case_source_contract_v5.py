"""Pure source contract for E2 original entry, observer timing, and source closure."""
from pathlib import Path
import ast,hashlib,json
WORK='evaluate_E2_adapted93_new86_frozen900_once_v1.py'
def H(b):return hashlib.sha256(b).hexdigest()
def match(tree,src):
 key=ast.dump(ast.parse(src,mode='eval').body,include_attributes=False);nodes=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.dump(n,include_attributes=False)==key];assert len(nodes)==1,(src,len(nodes));return nodes[0]
def validate_worker_timing(raw):
 tree=ast.parse(raw);install=match(tree,'early.install(DirectionalSpinCommand,sensor_resume_contract,e2_command_checkpoint_v1)');invoke=match(tree,"ns['main']()");finish=match(tree,'early.finish()');close=match(tree,"ns['app'].close()")
 assert install.lineno<invoke.lineno<finish.lineno<close.lineno
 work=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='work');panel=match(work,'E2Panel(real,torch,OUT,task)');adopt=match(work,'early.adopt_actual_written_start(panel,on_observed_start=adopt_initial_packet)');loop=next(n for n in ast.walk(work) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range');assert ast.literal_eval(loop.iter.args[0])==900 and panel.lineno<adopt.lineno<loop.lineno
 actor=match(tree,'runner.alg.actor(obs,stochastic_output=False)');step=match(tree,'vec.step(action)');assert (loop.lineno,loop.col_offset)<(actor.lineno,actor.col_offset)<(step.lineno,step.col_offset)
 assert sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='step' for n in ast.walk(tree))==1
 return dict(passed=True,early_hooks_before_original_ns_main=True,panel_constructed_then_adopts_actual_event_before_first_actor=True,original900_actor_VECstep_loop_once=True,observer_finishes_before_App_close=True)
def validate_installed_complete_case(J,m,sdk_app_launcher):
 J=Path(J);rows={r['relative']:r for r in m['files']}
 from e2_declared_entry_receipt_cli_contract_v5 import validate_installed_entry_contract
 entry=validate_installed_entry_contract(J,m,sdk_app_launcher)
 old=json.loads((J/'E2_PREVIOUS_SAMEHOST_FULL900_WITNESS.json').read_bytes());assert old['passed_actual_samehost_full900'] and old['source_SHA']==m['model_SHA'] and old['actual_waited'] and old['returncode']==0 and old['private_EX_released'] and not old['original_errors'] and not old['integrity']
 assert old['result']['controls']==900 and old['result']['all17_Adam_steps']==859300 and old['result']['actual_LR_unchanged']==.00022500000000000002
 assert old['native24']['controls']==24 and old['native24']['physics_callbacks']==192 and old['native24']['feedback_samples']==48
 helper=J/'e2_early_original_resample_observer_v2_complete.py';instances=J/'e2_observed_command_instances_v1.py'
 assert H(helper.read_bytes())==rows[helper.name]['SHA'] and H(instances.read_bytes())==rows[instances.name]['SHA']
 return dict(passed=True,original_entry_CLI_learnhook_receipt_source_closure=entry,worker_observer_order=validate_worker_timing((J/WORK).read_bytes()),samehost_prior_actual_full900_witness_SHA=H((J/'E2_PREVIOUS_SAMEHOST_FULL900_WITNESS.json').read_bytes()),actual_old_qualification_not_new_model_CPU_decode=True,model_decodes_this_metadata_purpose=0,actual_NEW_GPU_fullrestore_native24_early_event_still_pending=True)
