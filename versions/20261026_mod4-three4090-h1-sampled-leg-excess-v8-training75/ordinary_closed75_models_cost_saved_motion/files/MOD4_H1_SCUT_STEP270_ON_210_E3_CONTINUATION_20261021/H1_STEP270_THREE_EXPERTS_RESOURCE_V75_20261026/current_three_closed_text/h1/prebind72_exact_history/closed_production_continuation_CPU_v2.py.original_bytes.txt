"""Qualified closed71 -> reviewed three-expert controller and H1 reward-only V7 admission."""
from pathlib import Path
import ast,hashlib,json,os
from same_optimized_source_contract_metadata_candidate_v1 import validate_closed69_metadata,validate_same_optimized_protected_inventory
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())

def exact_recovery_step(before,after,old_step,new_step):
 import copy
 a=ast.parse(before);b=ast.parse(after);old=ast.parse(str(old_step)+'+20*updates',mode='eval').body;new=ast.parse(str(new_step)+'+20*updates',mode='eval').body;found=[]
 class Rewrite(ast.NodeTransformer):
  def visit_Assert(self,node):
   if isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name) and node.test.left.id=='steps' and len(node.test.ops)==1 and isinstance(node.test.ops[0],ast.Eq) and len(node.test.comparators)==1 and isinstance(node.test.comparators[0],ast.Set) and len(node.test.comparators[0].elts)==1 and ast.dump(node.test.comparators[0].elts[0])==ast.dump(old):found.append(node.lineno);node.test.comparators[0].elts[0]=copy.deepcopy(new)
   return self.generic_visit(node)
 a=Rewrite().visit(a);assert len(found)==1 and ast.dump(a)==ast.dump(b)

def exact_v7_reward(before,after):
 a=ast.parse(before);b=ast.parse(after)
 recipe=next(x for x in b.body if isinstance(x,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='RECIPE' for k in x.targets)).value
 rules={'version':('step270_near_edge_takeoff_gate_v7_reward_only','step270_sagittal_tuck_geometry_v6a_unused'),'takeoff_gate_start_front_x_m':(.10,-.05),'takeoff_gate_full_front_x_m':(.25,.15)}
 found=[]
 for k in recipe.keywords:
  if k.arg in rules:
   new,old=rules[k.arg];assert ast.literal_eval(k.value)==new;k.value=ast.parse(repr(old),mode='eval').body;found.append(k.arg)
 assert set(found)==set(rules) and ast.dump(a)==ast.dump(b)

def load(spec,B):
 import psutil
 B=Path(B);key=spec['key'];assert key in ('h1','recovery')
 auth=read(B/'THREE_EXPERT_CONTINUATION_SOURCE_AUTH_ACTUAL.json');assert auth['approved'] and auth['kind']=='actual_closed71_to_three_experts72' and auth['source_SHA']==spec['source_SHA']
 role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
 assert H(B/role)==auth['new_guard_SHA'] and H(B/'same_optimized_source_contract_metadata_candidate_v1.py')==auth['metadata_contract_SHA']
 old=Path(spec['previous_runtime_root']);prior=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json');current=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 proof=read(B/'CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json');qualified=validate_closed69_metadata(proof,key,prior['source_Adamstep'])
 assert qualified['source_SHA']==spec['source_SHA'] and qualified['source_Adam']==spec['source_Adamstep']
 exit=read(old/'NODE_EXIT_ACTUAL.json');terminal=read(old/'NODE_TERMINAL_ACTUAL.json')['row'];assert exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired'] and terminal['terminal_all_own_children_waited'] and terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['final']['passed'] and terminal['final']['final']['SHA']==spec['source_SHA']
 assert not any(p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 validate_same_optimized_protected_inventory(prior,current)
 controllers=read(B/'THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json');assert controllers['approved'] and controllers['tests']['actual_three_expert_independent_sumonce'] and controllers['tests']['terminal_slots_not_charged_twice']
 allowed=set(controllers['new_sources'])|{role}
 if key=='h1':allowed|={'h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'}
 else:allowed.add('recovery_worker.py')
 before={x['relative']:x for x in prior['files']};after={x['relative']:x for x in current['files']}
 for name,row in controllers['new_sources'].items():assert H(B/name)==row['SHA']
 for name,row in before.items():
  if name.endswith('.py') and name not in allowed:assert name in after and after[name]['SHA']==row['SHA'] and after[name]['bytes']==row['bytes'],name
 assert not {x for x in after if x.endswith('.py') and x not in before}
 old_control=(old/'forwarded_original_owner_control_v1.py').read_text('utf8');new_control=(B/'forwarded_original_owner_control_v1.py').read_text('utf8');assert old_control.count("spec['key']=='recovery'")==2
 assert ast.dump(ast.parse(new_control))==ast.dump(ast.parse(old_control.replace("spec['key']=='recovery'","spec['key'] in ('e2','recovery')")))
 for name in ('H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json','H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json','H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json','SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json') if key=='h1' else ('SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json',):assert H(B/name)==H(old/name)
 cpu=read(B/('TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json' if key=='h1' else 'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json'))
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json') and cpu['sampling_acceleration_CPU']['passed']
 if key=='h1':
  assert spec['reward_migration'] and spec['policy_hz']==spec['source_policy_hz']==100
  reward_auth=read(B/'H1_V7_REWARD_ONLY_AUTH_AND_CPU_ACTUAL.json');assert reward_auth['approved'] and reward_auth['passed'] and H(B/'h1_step270_path_reward_v1.py')==reward_auth['source_SHA'] and H(B/'step270_reward_installed_CPU_v1.py')==reward_auth['checker_SHA']
  exact_v7_reward((old/'h1_step270_path_reward_v1.py').read_text('utf8'),(B/'h1_step270_path_reward_v1.py').read_text('utf8'))
  assert cpu['boundary_repair_integration_CPU']['passed'] and cpu['new_reward_integration_CPU']['passed'] and cpu['new_reward_integration_CPU']['actual_installed_SDK_reward_compute_tested']
  kind='closed_same_backend_reward_migration'
 else:
  exact_recovery_step((old/'recovery_worker.py').read_text('utf8'),(B/'recovery_worker.py').read_text('utf8'),prior['source_Adamstep'],spec['source_Adamstep'])
  assert spec['policy_hz']==spec['source_policy_hz']==50 and cpu['source_schema_counts']==[173,96] and cpu['sampling_acceleration_CPU']['fresh_bank_physical_read_count']==1
  clock=read(old/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json');assert clock['policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8
  kind='closed_same_backend_policy50_production'
 v=dict(kind=kind,key=key,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=True,same_physics_assets_and_PPO_AST=True,source_original_cost_settled=True,explicit_policy_clock_50Hz_admitted=key=='recovery',same_clock_closed_production=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,reviewed_three_expert_single_original_writer=True,only_H1_V7_reward_gate_changed=key=='h1',not_skill_graduation=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
