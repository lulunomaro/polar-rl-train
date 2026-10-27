"""Source-only wrapper derivation. Does not execute reviewer or inspect PT."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;T=D.parent.parent;N=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027'
old=N/'review_actual_native88C_bound_formal_fullstate_CPU_unused_once.py';raw=old.read_bytes()
new=raw
anchor=b"N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent"
assert new.count(anchor)==1
new=new.replace(anchor,b"N=Path(__file__).resolve().parents[2]/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027';R=N/'reports';T=N.parent")
before=b'NATIVE88_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json';after=b'NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json'
assert new.count(before)==2;new=new.replace(before,after)
ast.parse(new)
name='review_actual_native88C_case_safe_V2_bound_formal_CPU_unused_once.py'
with (D/name).open('xb') as f:f.write(new)
entry=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88C_exact_reset_bank_lifecycle_source_v1/review_native88_finals_initial_CPU_unused_once.py'
assert hashlib.sha256(entry.read_bytes()).hexdigest()=='a97587c3ee6ff7015949d06aa429851026f8d3837ab65bda56f69a048906bbb9'
with (D/'BOUND_WRAPPER_SOURCE_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,old_wrapper=str(old),old_SHA=hashlib.sha256(raw).hexdigest(),new_wrapper=name,new_SHA=hashlib.sha256(new).hexdigest(),reviewer_source_SHA_unchanged='a97587c3ee6ff7015949d06aa429851026f8d3837ab65bda56f69a048906bbb9',
 changes=['bind original N explicitly from new preparation-directory placement','change only collected receipt path and its existence assertion to V2'],
 actual_reviewer_or_wrapper_executed=False,model_stat_read_or_hash=False),f,indent=2)
print(json.dumps(dict(prepared=True,wrapper=name,SHA=hashlib.sha256(new).hexdigest())))
