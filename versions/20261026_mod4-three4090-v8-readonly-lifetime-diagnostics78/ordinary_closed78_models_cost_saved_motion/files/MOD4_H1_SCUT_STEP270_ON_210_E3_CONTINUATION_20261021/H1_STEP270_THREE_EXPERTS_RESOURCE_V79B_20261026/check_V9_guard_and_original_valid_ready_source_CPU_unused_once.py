"""Source/metadata/original-controller CPU only. Not actual installed admission."""
from pathlib import Path
import ast,copy,hashlib,json,time
N=Path(__file__).resolve().parent;P=N.parent/'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026';cases=[]
p=N/'candidates/closed_three_H1_V9_reward_CPU_v1.py';tree=ast.parse(p.read_text('utf8'));ns={'ast':ast}
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('strict_same_V8_root_inventory','exact_recovery_step')],type_ignores=[]),str(p),'exec'),ns)
def reject(name,fn):
 try:fn()
 except AssertionError:cases.append(dict(case=name,rejected=True))
 else:raise AssertionError(name)
for key in ('h1','e2','recovery'):
 m=json.loads((P/'payloads'/key/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());before={r['relative']:r for r in m['files']};after=copy.deepcopy(before);role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py';after[role]['SHA']='0'*64
 if key=='h1':
  for name in ('h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'):after[name]['SHA']='1'*64
 if key=='recovery':after['recovery_worker.py']['SHA']='2'*64
 ns['strict_same_V8_root_inventory'](before,after,role,key);cases.append(dict(case=key+'_only_reviewed_role_and_V9_files',accepted=True))
 bad=copy.deepcopy(after);bad['unreviewed.py']={'bytes':1,'SHA':'3'*64};reject(key+'_added_python',lambda:ns['strict_same_V8_root_inventory'](before,bad,role,key))
 if key=='h1':
  for name in ('h1_production_control_prefix_trace_v1.py','h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py','h1_step270_sdk_runtime_candidate.py'):
   bad=copy.deepcopy(after);bad[name]['SHA']='4'*64;reject('H1_unreviewed_'+name,lambda:ns['strict_same_V8_root_inventory'](before,bad,role,key))
# Exercise the untouched actual valid_ready function, including migration-vs-production discrimination.
common=P/'controllers/three_slot_common_v1.py';ct=ast.parse(common.read_text('utf8'));fn=next(x for x in ct.body if isinstance(x,ast.FunctionDef) and x.name=='valid_ready');scope={'hashlib':hashlib,'json':json}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(common),'exec'),scope);valid=scope['valid_ready']
fields=dict(passed=True,source_SHA='a'*64,GPU_UUID='GPU-test',execution_backend='source210',all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_physics_assets_and_PPO_AST=True,same_active_runtime_assets_and_PPO_AST=True)
def row(v,key='h1'):
 return dict(key=key,phase='ready',closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True),manifest_SHA='b'*64,original_error=False)
spec=dict(key='h1',policy_hz=100,source_policy_hz=100,closed_production_continuation=True,reward_migration=True,source_SHA='a'*64,GPU_UUID='GPU-test',execution_backend='source210',manifest_SHA='b'*64)
value=dict(fields,kind='closed_same_backend_reward_migration');assert valid(row(value),spec);cases.append(dict(case='original_H1_reward_migration_valid_ready',accepted=True))
for name in ('passed','all_source_model_runtime_finite_CPU','old_complete_production_checkpoint_actual_EXIT0','same_physics_assets_and_PPO_AST'):
 bad=dict(value);bad[name]=False;assert not valid(row(bad),spec);cases.append(dict(case='original_valid_ready_reject_'+name,rejected=True))
for name,wrong in [('kind','closed_same_backend_production'),('source_SHA','c'*64),('GPU_UUID','GPU-other'),('execution_backend','target72')]:
 bad=dict(value);bad[name]=wrong;assert not valid(row(bad),spec);cases.append(dict(case='original_valid_ready_wrong_'+name,rejected=True))
r=row(value);r['closed_source_CPU']['SHA']='0'*64;assert not valid(r,spec);cases.append(dict(case='original_valid_ready_bad_receipt_SHA',rejected=True))
for key in ('e2','recovery'):
 v=dict(fields,kind='closed_same_backend_policy50_production',explicit_policy_clock_50Hz_admitted=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA='d'*64,same_clock_closed_production=True,execution_backend='target72',original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True)
 s=dict(spec,key=key,policy_hz=50,source_policy_hz=50,reward_migration=False,execution_backend='target72');assert valid(row(v,key),s);cases.append(dict(case=key+'_original50Hz_valid_ready',accepted=True))
base=(P/'DEPLOYER_REUSED_H1_HELPER_EXACT_SOURCE.py').read_text('utf8');old="assert not s.get('reward_migration') and valid_ready(row,s)";new="assert s['reward_migration'] and valid_ready(row,s)";assert base.count(old)==1;patched=base.replace(old,new,1);assert ast.dump(ast.parse(patched.replace(new,old,1)))==ast.dump(ast.parse(base))
result=dict(epoch=time.time(),passed_synthetic_source_CPU=True,cases=cases,original_valid_ready_function_SHA=hashlib.sha256(ast.dump(fn).encode()).hexdigest(),controller_file_SHA=hashlib.sha256(common.read_bytes()).hexdigest(),exact_H1_helper_assert_migration_only=True,source_guard_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),no_model_raw_GPU_remote_or_current78_change=True,not_actual_target_SDK_source_or_GO_admission=True)
with (N/'reports/V9_SOURCE_SCOPE_AND_UNCHANGED_ORIGINAL_VALID_READY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(source_only_V9_original_controller_CPU=True,cases=len(cases))))
