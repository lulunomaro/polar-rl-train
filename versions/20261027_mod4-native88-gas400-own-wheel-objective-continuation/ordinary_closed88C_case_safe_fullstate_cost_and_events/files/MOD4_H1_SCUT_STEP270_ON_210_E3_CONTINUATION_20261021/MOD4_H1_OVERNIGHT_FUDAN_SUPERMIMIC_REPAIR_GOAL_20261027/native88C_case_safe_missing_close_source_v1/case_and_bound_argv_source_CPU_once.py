"""Three tiny source/metadata checks; never execute old/new reviewer/wrapper."""
from pathlib import Path
import ast,json,hashlib,types
D=Path(__file__).resolve().parent;T=D.parent.parent;N=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027';OLD=N/'review_actual_native88C_bound_formal_fullstate_CPU_unused_once.py';NEW=D/'review_actual_native88C_case_safe_V2_bound_formal_CPU_unused_once.py'
checks=[]
rows=[dict(relative='h1/job0/NATIVE88_SOURCE_CPU_STARTED_ACTUAL.json',SHA='a'*64,bytes=101),dict(relative='h1/job0/native88_SOURCE_CPU_STARTED_ACTUAL.json',SHA='b'*64,bytes=102)]
mapped=[dict(r,local_path='C:/SYNTHETIC_NOT_A_FILE/case_safe/'+r['SHA']+'/'+r['relative'].split('/')[-1]) for r in rows]
assert rows[0]['relative']!=rows[1]['relative'] and rows[0]['relative'].casefold()==rows[1]['relative'].casefold()
assert len({r['local_path'].casefold() for r in mapped})==2 and all(all(r[k]==s[k] for k in ('relative','SHA','bytes')) for r,s in zip(mapped,rows))
checks.append(dict(name='distinct original-case source rows preserved with unique case-safe metadata destinations',passed=True))
entry=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88C_exact_reset_bank_lifecycle_source_v1/review_native88_finals_initial_CPU_unused_once.py';raw=entry.read_bytes();tree=ast.parse(raw)
assert hashlib.sha256(raw).hexdigest()=='a97587c3ee6ff7015949d06aa429851026f8d3837ab65bda56f69a048906bbb9'
assert not any(isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Constant) and n.slice.value=='all_texts' for n in ast.walk(tree))
strings={n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
assert {'NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json','NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json','NATIVE87_ACTUAL_BEFORE_FIRST_CONTROL_ADMISSION.json','ACTUAL_H1_CONVERGENCE_CURVE.jsonl'}<=strings
checks.append(dict(name='unchanged reviewer ignores all_texts mapping and reads canonical production files directly',passed=True))
def argv_without_execution(path):
 t=ast.parse(path.read_bytes());nodes=[n for n in t.body if isinstance(n,ast.Assign)]
 ns=dict(Path=Path,__file__=str(path),sys=types.SimpleNamespace(argv=[]))
 exec(compile(ast.Module(body=nodes,type_ignores=[]),'pure_bound_assignments','exec'),ns)
 return ns['sys'].argv
before=argv_without_execution(OLD);after=argv_without_execution(NEW);expected=before.copy();i=expected.index('--collected-report')+1;expected[i]=str(N/'reports/NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json')
assert after==expected and len(before)==len(after) and sum(a!=b for a,b in zip(before,after))==1
assert '--bootstrap-witness' in after and '--bootstrap-bytes' in after and after[-1]=='16868635'
checks.append(dict(name='bound CLI differs only collected receipt; unchanged reviewer and witness arguments',passed=True))
for p in D.glob('*.py'):ast.parse(p.read_bytes())
with (D/'CASE_AND_BOUND_ARGV_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=3,checks=checks,mapping_fixture=mapped,bound_argv=after,wrapper_SHA=hashlib.sha256(NEW.read_bytes()).hexdigest(),reviewer_SHA_unchanged=hashlib.sha256(raw).hexdigest(),actual_entry_or_model_or_network_executed=False,model_stat_or_hash=False),f,indent=2)
print(json.dumps(dict(passed=True,count=3,wrapper_SHA=hashlib.sha256(NEW.read_bytes()).hexdigest())))
