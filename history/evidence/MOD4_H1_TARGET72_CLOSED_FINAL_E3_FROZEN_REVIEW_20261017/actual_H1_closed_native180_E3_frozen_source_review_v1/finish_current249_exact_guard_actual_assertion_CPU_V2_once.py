"""Update only exact signed desktop identity evidence after rejection; no runtime/UI changes."""
from pathlib import Path
import ast,json,copy,time,hashlib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';G=W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017'
v=json.loads((R/'E3_FROZEN_249_CHANGED_DESKTOP_EXACT_SIGNATURES_2145_READONLY_ACTUAL.json').read_bytes());assert not v.get('original_error')
publishers={'workbuddy.exe':'Tencent','deepseek harness.exe':'DeepSeek','copilotapp.exe':'Microsoft','copilotapphost.exe':'Microsoft','qq.exe':'Tencent','gameviewerserver.exe':'NetEase','gameviewer.exe':'NetEase'};expected={};cases=[]
for row in v['exact_new_desktop_roles']:
 name=row['name'];assert row['authenticode']['Status']=='Valid' and publishers[name] in row['authenticode']['Subject']
 assert not any(Path(c['exe'].replace('\\','/')).name.lower().startswith(('python','kit.exe','jupyter')) for c in row['children']+row['parent_children'])
 if name in ('deepseek harness.exe','workbuddy.exe','qq.exe','copilotapp.exe'):assert '--type=gpu-process' in row['process']['argv'] and not any(a.startswith('--type=') for a in row['parent']['argv'])
 if name=='copilotapphost.exe':assert 'connect-to-browser' in row['process']['argv'] and '--browser-owned' in row['process']['argv'] and Path(row['parent']['exe'].replace('\\','/')).name.lower()=='copilotapp.exe'
 expected[name]={k:row[k] for k in ('process','parent','binary_SHA')}
assert len(expected)==4
s=(G/'transport_249_E2closed109_exact_desktop_0820_v4.py').read_text('utf8').replace('E2_CLOSED109_249_CHANGED_DESKTOP_EXACT_SIGNATURES_0820_READONLY_ACTUAL.json','E3_FROZEN_249_CHANGED_DESKTOP_EXACT_SIGNATURES_2145_READONLY_ACTUAL.json');ast.parse(s);p=B/'transport_249_E3_current_exact_desktop_2145_v1.py';assert p.read_text('utf8')==s
# Execute the guard's actual equality assertion for each tampered identity field.
tree=ast.parse(s);fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='guard_code');assign=next(n for n in fun.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='insert' for x in n.targets));call=assign.value;template=ast.literal_eval(call.func.value);assertion=next(line.strip() for line in template.splitlines() if line.strip().startswith('assert actual=='));g=ast.parse(assertion.replace('FRESH_EXACT_SIGNED_DESKTOP','expected'));check=g.body[0];compiled=compile(ast.Module(body=[check],type_ignores=[]),'actual_guard_equality_CPU','exec')
for name,good in expected.items():
 exec(compiled,dict(actual=good,expected=expected,name=name))
 for field in ('pid','creation','exe','parent','binary_SHA','argv'):
  bad=copy.deepcopy(good)
  if field=='parent':bad['parent']=None
  elif field=='binary_SHA':bad[field]='0'*64
  elif field=='argv':bad['process']['argv'].append('unexpected-worker.py')
  elif field in ('pid','creation'):bad['process'][field]+=1
  else:bad['process'][field]='C:/untrusted/worker.exe'
  try:exec(compiled,dict(actual=bad,expected=expected,name=name))
  except AssertionError:cases.append(name+':'+field)
  else:raise AssertionError('Actual guard accepted changed process')
s=(B/'dispatch_E3closed85_V2_unused_native120_actual_resource_source_SDK_once.py').read_text('utf8').replace('import transport_249_E2closed109_exact_desktop_0820_v4 as t','import transport_249_E3_current_exact_desktop_2145_v1 as t').replace("E3_CLOSED85_FROZEN_V2';t.ROOT=ROOT","E3_CLOSED85_FROZEN_V3';t.ROOT=ROOT").replace('e3closed85_public03_native120_v2','e3closed85_public03_native120_v3').replace('PUBLIC03_NATIVE120_V2','PUBLIC03_NATIVE120_V3').replace('E3_CLOSED85_NATIVE120_V2','E3_CLOSED85_NATIVE120_V3').replace('E3closed85_native120_V2_unused_once.py','E3closed85_native120_V3_unused_once.py');s=s.replace('E3_CLOSED85_NATIVE120_V3_EXACT_DEPLOY_BINDINGS_CPU_PREPARED.json','E3_CLOSED85_NATIVE120_V2_EXACT_DEPLOY_BINDINGS_CPU_PREPARED.json');ast.parse(s);q=B/'dispatch_E3closed85_unused_V3_native120_sealedV2_current_guard_once.py';q.write_text(s,encoding='utf8',newline='\n')
out=dict(epoch=time.time(),actual_new_exact_signed_roles=list(expected),actual_guard_equality_negative_cases=cases,original_V2_resource_rejected_before_root_lease_Task_GPU=True,new_unused_V3_case_uses_same_sealed_V2_payload_no_physics_or_source_change=True,no_UI_process_SDK_or_GPU_mutation=True,transport_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),deployer_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),unknown_compute_still_rejected=True,no_evaluation_pass_or_ownership_claim_from_desktop_signatures=True)
with (R/'E3_UNUSED_V3_CURRENT_EXACT_DESKTOP_GUARD_24NEGATIVE_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(exact_roles=len(expected),actual_guard_negatives=len(cases),new_Task_not_yet_dispatched=True)))
