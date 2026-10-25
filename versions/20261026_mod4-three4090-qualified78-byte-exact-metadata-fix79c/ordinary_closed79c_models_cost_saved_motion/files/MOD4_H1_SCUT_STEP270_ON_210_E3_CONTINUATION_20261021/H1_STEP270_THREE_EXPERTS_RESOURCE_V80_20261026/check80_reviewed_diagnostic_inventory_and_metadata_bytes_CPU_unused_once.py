"""Synthetic source metadata only; actual80 target source admission remains required."""
from pathlib import Path
import ast,copy,hashlib,json,time
N=Path(__file__).resolve().parent;P=N.parent/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79C_20261026';p=N/'candidates/closed_three_V8_landing_journal_source_CPU_v1.py';tree=ast.parse(p.read_text('utf8'));ns={'ast':ast}
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('strict_same_V8_root_inventory','exact_recovery_step')],type_ignores=[]),str(p),'exec'),ns);cases=[]
def reject(name,fn):
 try:fn()
 except AssertionError:cases.append(dict(case=name,rejected=True))
 else:raise AssertionError(name)
name='same_optimized_source_contract_metadata_candidate_v1.py';meta=(N/'candidates'/name).read_bytes()
for key in ('h1','e2','recovery'):
 assert (P/'payloads'/key/name).read_bytes()==meta
 m=json.loads((P/'payloads'/key/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());before={r['relative']:r for r in m['files']};after=copy.deepcopy(before);role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py';after[role]['SHA']='0'*64
 if key=='h1':
  for f in ('h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py'):after[f]['SHA']='1'*64
 if key=='recovery':after['recovery_worker.py']['SHA']='2'*64
 ns['strict_same_V8_root_inventory'](before,after,role,key);cases.append(dict(case=key+'_reviewed_diagnostic_scope',accepted=True))
 bad=copy.deepcopy(after);bad['unknown.py']={'bytes':1,'SHA':'3'*64};reject(key+'_new_python',lambda:ns['strict_same_V8_root_inventory'](before,bad,role,key))
 bad=copy.deepcopy(after);bad[name]['SHA']=hashlib.sha256(meta.replace(b'\r\n',b'\n')).hexdigest();bad[name]['bytes']=len(meta.replace(b'\r\n',b'\n'));reject(key+'_CRLF_normalization',lambda:ns['strict_same_V8_root_inventory'](before,bad,role,key))
 if key=='h1':
  for f in ('h1_production_control_prefix_trace_v1.py','h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py','h1_step270_sdk_runtime_candidate.py'):
   bad=copy.deepcopy(after);bad[f]['SHA']='4'*64;reject('H1_unreviewed_'+f,lambda:ns['strict_same_V8_root_inventory'](before,bad,role,key))
result=dict(epoch=time.time(),passed_source_only_CPU=True,cases=cases,byte_exact_metadata_SHA=hashlib.sha256(meta).hexdigest(),metadata_bytes=len(meta),only_reviewed_H1_counter_sampler_and_reference_change=True,no_new_Python_trace_reward_runtime_or_actor_change=True,no_PT_raw_GPU_remote_or_current79c_action=True,not_actual_target_SDK_or_GO_admission=True)
with (N/'reports/SOURCE_ONLY80_DIAGNOSTIC_SCOPE_AND_METADATA_BYTE_GUARD_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(source_only80_guard_cases=len(cases),metadata_exact_bytes=len(meta))))
