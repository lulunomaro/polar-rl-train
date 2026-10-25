"""Synthetic metadata/AST tests only; never installed source or checkpoint admission."""
from pathlib import Path
import ast,copy,hashlib,json,time
N=Path(__file__).resolve().parent;P=N.parent/'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026'
path=N/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py';source=path.read_text('utf8');tree=ast.parse(source)
ns={'ast':ast};nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('strict_same_V8_root_inventory','exact_recovery_step')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
cases=[]
def reject(name,fn):
 try:fn()
 except AssertionError:cases.append(dict(case=name,rejected=True))
 else:raise AssertionError('Unexpected accept: '+name)
for key in ('h1','e2','recovery'):
 m=json.loads((P/'payloads'/key/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());before={r['relative']:r for r in m['files']};after=copy.deepcopy(before)
 role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py';after[role]['SHA']='0'*64
 if key=='recovery':after['recovery_worker.py']['SHA']='1'*64
 ns['strict_same_V8_root_inventory'](before,after,role,key);cases.append(dict(case=key+'_role_only',accepted=True))
 changed=copy.deepcopy(after);changed['unreviewed.py']={'SHA':'2'*64,'bytes':2};reject(key+'_added_python',lambda:ns['strict_same_V8_root_inventory'](before,changed,role,key))
 names=('h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py','h1_lifetime_goal_counter_v1.py','h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py') if key=='h1' else ('mod4_task.py',)
 for name in names:
  if name not in before:continue
  changed=copy.deepcopy(after);changed[name]['SHA']='3'*64;reject(key+'_changed_'+name,lambda:ns['strict_same_V8_root_inventory'](before,changed,role,key))
old=(P/'payloads/recovery/recovery_worker.py').read_text('utf8');m=json.loads((P/'payloads/recovery/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());step=m['source_Adamstep'];needle='{'+str(step)+'+20*updates}';assert old.count(needle)==1
new=old.replace(needle,'{1234567+20*updates}',1);ns['exact_recovery_step'](old,new,step,1234567);cases.append(dict(case='exact_saved_Adam_assert_only',accepted=True))
reject('wrong_saved_Adam',lambda:ns['exact_recovery_step'](old,new,step,1234568))
reject('extra_recovery_statement',lambda:ns['exact_recovery_step'](old,new+'\nextra=1\n',step,1234567))
reject('wrong_update_multiplier',lambda:ns['exact_recovery_step'](old,new.replace('1234567+20*updates','1234567+19*updates'),step,1234567))
result=dict(epoch=time.time(),passed_source_only_synthetic_CPU=True,cases=cases,guard_SHA=hashlib.sha256(path.read_bytes()).hexdigest(),original78_trace_counter_checker_reward_all_exact=True,no_model_raw_GPU_remote_or_current78_mutation=True,not_actual_installed_SDK_or_runtime_admission=True)
with (N/'reports/SAME79_STRICT_SOURCE_INVENTORY_AND_EXACT_ADAM_AST_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(source_only79_CPU=True,cases=len(cases))))
