"""Uninstalled same-V7/same-optimized triple continuation from a fully closed72 proof."""
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
def exact_metadata_extension(before,after):
 needle="assert key in ('h1','recovery')";assert before.count(needle)==1
 assert ast.dump(ast.parse(after))==ast.dump(ast.parse(before.replace(needle,"assert key in ('h1','e2','recovery')")))
def metadata_exact_origin(text):
 needle="assert key in ('h1','e2','recovery')";assert text.count(needle)==1
 normalized=text.replace(needle,"assert key in ('h1','recovery')")
 assert hashlib.sha256(normalized.encode('utf8')).hexdigest()=='1295b32505185ed041b559213d20dc9f5d440076ed6f2b5490accbd8c3719ec8'
def load(spec,B):
 import psutil
 B=Path(B);key=spec['key'];assert key in ('h1','e2','recovery') and not spec.get('cross_host_qualified_source') and not spec.get('reward_migration')
 old=Path(spec['previous_runtime_root']);prior=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json');current=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 auth=read(B/'THREE_EXPERT_SAME_V7_CONTINUATION_AUTH_ACTUAL.json');assert auth['approved'] and auth['kind']=='actual_closed72_same_V7_three_experts_continuation' and auth['source_SHA']==spec['source_SHA']
 role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
 assert H(B/role)==auth['guard_SHA'] and H(B/'same_optimized_source_contract_metadata_candidate_v1.py')==auth['metadata_SHA']
 proof=read(B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json');assert set(proof['models'])=={'h1','e2','recovery'} and proof['actual_cost_sumonce']==sum(v['actual_cost']['charged_seconds'] for v in proof['models'].values())
 qualified=validate_closed69_metadata(proof,key,prior['source_Adamstep']);assert qualified['source_SHA']==spec['source_SHA'] and qualified['source_Adam']==spec['source_Adamstep']
 exit=read(old/'NODE_EXIT_ACTUAL.json');terminal=read(old/'NODE_TERMINAL_ACTUAL.json')['row'];assert exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired'] and terminal['terminal_all_own_children_waited'] and terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['final']['passed'] and terminal['final']['final']['SHA']==spec['source_SHA']
 assert not any(p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 validate_same_optimized_protected_inventory(prior,current)
 before={x['relative']:x for x in prior['files']};after={x['relative']:x for x in current['files']};allowed={role,'same_optimized_source_contract_metadata_candidate_v1.py'}
 if key=='recovery':allowed.add('recovery_worker.py')
 for name,row in before.items():
  if name.endswith('.py') and name not in allowed:assert name in after and after[name]['SHA']==row['SHA'] and after[name]['bytes']==row['bytes'],name
 assert {x for x in after if x.endswith('.py') and x not in before}==({'same_optimized_source_contract_metadata_candidate_v1.py'} if key=='e2' else set())
 for name in ('H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json','H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json','H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json','H1_V7_REWARD_ONLY_AUTH_AND_CPU_ACTUAL.json','SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json') if key=='h1' else (('SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json',) if key=='recovery' else ()):
  assert H(B/name)==H(old/name)
 exact_metadata_extension((old/'same_optimized_source_contract_metadata_candidate_v1.py').read_text('utf8'),(B/'same_optimized_source_contract_metadata_candidate_v1.py').read_text('utf8')) if key!='e2' else None
 if key=='e2':metadata_exact_origin((B/'same_optimized_source_contract_metadata_candidate_v1.py').read_text('utf8'))
 cpu=read(B/('TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json' if key=='h1' else 'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json'))
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json') and cpu['actual_SDK_math']['SHA']==current['expected_actual_SDK_math_SHA'] and len(cpu['actual_RSL_sources'])==2
 if key=='h1':
  assert spec['policy_hz']==spec['source_policy_hz']==100 and cpu['new_reward_integration_CPU']['passed'] and cpu['new_reward_integration_CPU']['actual_installed_SDK_reward_compute_tested'] and cpu['boundary_repair_integration_CPU']['passed'] and cpu['sampling_acceleration_CPU']['passed']
  kind='closed_same_backend_production'
 else:
  assert spec['policy_hz']==spec['source_policy_hz']==50 and cpu['source_schema_counts']==([175,98] if key=='e2' else [173,96])
  clock=read(old/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json');assert clock['policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8
  if key=='recovery':
   exact_recovery_step((old/'recovery_worker.py').read_text('utf8'),(B/'recovery_worker.py').read_text('utf8'),prior['source_Adamstep'],spec['source_Adamstep']);assert cpu['sampling_acceleration_CPU']['passed'] and cpu['sampling_acceleration_CPU']['fresh_bank_physical_read_count']==1
  kind='closed_same_backend_policy50_production'
 v=dict(kind=kind,key=key,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=True,same_physics_assets_and_PPO_AST=True,source_original_cost_settled=True,explicit_policy_clock_50Hz_admitted=key!='h1',same_clock_closed_production=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_skill_graduation=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
