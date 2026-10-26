"""Uninstalled strict same-V8/same-optimized triple continuation from a fully closed three-expert proof."""
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
def strict_same_V8_root_inventory(before,after,role,key):
 allowed={role}
 if key=='recovery':allowed.add('recovery_worker.py')
 for name,row in before.items():
  if name.endswith('.py') and name not in allowed:assert name in after and after[name]['SHA']==row['SHA'] and after[name]['bytes']==row['bytes'],name
 assert not {name for name in after if name.endswith('.py') and name not in before}


def validate_same_landing_journal_lineage(B,old,diag):
 B=Path(B);old=Path(old)
 name='H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json'
 assert H(B/name)==H(old/name)
 journal=read(B/name)
 assert journal['approved'] and journal['no_reward_actor_command_physics_or_success_change']
 assert set(journal['candidate_files'])=={'h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py','reference_sources/actual79c_counter_original_bytes.txt'}
 assert diag['candidate_files']['h1_lifetime_goal_counter_v1.py']==journal['base_counter_SHA']
 assert diag['candidate_files']['sampling_acceleration_installed_CPU_v2.py']==journal['base_sampler_SHA']
 for name,digest in journal['candidate_files'].items():assert H(B/name)==H(old/name)==digest
 assert H(B/'reference_sources/actual79c_counter_original_bytes.txt')==journal['base_counter_SHA']
 assert H(B/'h1_production_control_prefix_trace_v1.py')==H(old/'h1_production_control_prefix_trace_v1.py')==diag['candidate_files']['h1_production_control_prefix_trace_v1.py']
 return True

def load(spec,B):
 import psutil
 B=Path(B);key=spec['key'];assert key in ('h1','e2','recovery') and not spec.get('cross_host_qualified_source') and not spec.get('reward_migration')
 old=Path(spec['previous_runtime_root']);prior=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json');current=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 auth=read(B/'NORMAL_THREE_83_PRODUCTION_SOURCE_AUTH_ACTUAL.json');assert auth['approved'] and auth['kind']=='actual_closed_production_pair_native_diagnostic_all3_cost_same_V8' and auth['source_SHA']==spec['source_SHA']
 role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
 assert H(B/role)==auth['guard_SHA'] and H(B/'same_optimized_source_contract_metadata_candidate_v1.py')==auth['metadata_SHA']
 proof=read(B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json');assert key in ('h1','recovery') and proof['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic' and set(proof['models'])=={'h1','recovery'} and set(proof['original_slots_cost'])=={'h1','e2','recovery'} and proof['native_method']['original_terminal']['original_error'] and proof['native_method']['present'] is False and abs(proof['actual_cost_sumonce']-sum(v['charged_seconds'] for v in proof['original_slots_cost'].values()))<1e-5 and all(v['duration_bound_passed'] for v in proof['original_slots_cost'].values())
 qualified=validate_closed69_metadata(proof,key,prior['source_Adamstep']);assert qualified['source_SHA']==spec['source_SHA'] and qualified['source_Adam']==spec['source_Adamstep']
 exit=read(old/'NODE_EXIT_ACTUAL.json');terminal=read(old/'NODE_TERMINAL_ACTUAL.json')['row'];assert exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired'] and terminal['terminal_all_own_children_waited'] and terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['final']['passed'] and terminal['final']['final']['SHA']==spec['source_SHA']
 assert not any(p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 validate_same_optimized_protected_inventory(prior,current)
 before={x['relative']:x for x in prior['files']};after={x['relative']:x for x in current['files']}
 strict_same_V8_root_inventory(before,after,role,key)
 for name in ('H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json','H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json','H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json','H1_V7_REWARD_ONLY_AUTH_AND_CPU_ACTUAL.json','H1_V8_SAMPLED_LEG_EXCESS_SOURCE_AND_CPU_AUTH_ACTUAL.json','SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json') if key=='h1' else (('SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json',) if key=='recovery' else ()):
  assert H(B/name)==H(old/name)
 cpu=read(B/('TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json' if key=='h1' else 'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json'))
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json') and cpu['actual_SDK_math']['SHA']==current['expected_actual_SDK_math_SHA'] and len(cpu['actual_RSL_sources'])==2
 if key=='h1':
  assert spec['policy_hz']==spec['source_policy_hz']==100 and cpu['new_reward_integration_CPU']['passed'] and cpu['new_reward_integration_CPU']['actual_installed_SDK_reward_compute_tested'] and cpu['boundary_repair_integration_CPU']['passed'] and cpu['sampling_acceleration_CPU']['passed']
  v8=read(B/'H1_V8_SAMPLED_LEG_EXCESS_SOURCE_AND_CPU_AUTH_ACTUAL.json');assert v8['approved'] and v8['implementation_under_existing_reward_repair_authorization']
  diag=read(B/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json');assert diag['approved'] and diag['no_reward_actor_command_PPO_physics_or_success_change']
  assert set(diag['candidate_files'])=={'h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py','h1_lifetime_goal_counter_v1.py'}
  validate_same_landing_journal_lineage(B,old,diag)
  assert H(B/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json')==H(old/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json')
  for name,digest in v8['candidate_files'].items():
   if name=='h1_production_control_prefix_trace_v1.py':assert digest==diag['base_trace_SHA']
   elif name=='sampling_acceleration_installed_CPU_v2.py':assert digest==diag['base_sampler_checker_SHA']
   else:assert H(B/name)==H(old/name)==digest
  for name,digest in diag['candidate_files'].items():
   if name=='h1_production_control_prefix_trace_v1.py':assert H(B/name)==H(old/name)==digest
  assert cpu['sampling_acceleration_CPU']['landing_event_journal_CPU']['passed']
  from h1_lifetime_goal_counter_v1 import ORIGINAL_V8_TRACE_SHA
  assert ORIGINAL_V8_TRACE_SHA==diag['base_trace_SHA']
  assert H(old/'h1_step270_path_reward_v1.py')==H(B/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']
  assert read(B/'job0/TASK.json')['reward_recipe_version']==read(old/'job0/TASK.json')['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only'
  from step270_reward_installed_CPU_v1 import allowlist
  allowlist(B/'h1_step270_path_reward_v1.py',B/'reference_sources/V5_h1_step270_path_reward_v1.py')
  from sampling_acceleration_installed_CPU_v2 import validate_V8_trace_reward_publication_only
  validate_V8_trace_reward_publication_only(B/'h1_production_control_prefix_trace_v1.py')
  assert cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested'] and cpu['sampling_acceleration_CPU']['V8_reward_publication_AST']['passed']
  assert cpu['sampling_acceleration_CPU']['lifetime_goal_diagnostic_CPU']['passed']
  kind='closed_same_backend_production'
 else:
  assert spec['policy_hz']==spec['source_policy_hz']==50 and cpu['source_schema_counts']==([175,98] if key=='e2' else [173,96])
  clock=read(old/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json');assert clock['policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8
  if key=='recovery':
   exact_recovery_step((old/'recovery_worker.py').read_text('utf8'),(B/'recovery_worker.py').read_text('utf8'),prior['source_Adamstep'],spec['source_Adamstep']);assert cpu['sampling_acceleration_CPU']['passed'] and cpu['sampling_acceleration_CPU']['fresh_bank_physical_read_count']==1
  kind='closed_same_backend_policy50_production'
 v=dict(kind=kind,key=key,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=True,same_physics_assets_and_PPO_AST=True,source_original_cost_settled=True,explicit_policy_clock_50Hz_admitted=key!='h1',same_clock_closed_production=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_skill_graduation=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
