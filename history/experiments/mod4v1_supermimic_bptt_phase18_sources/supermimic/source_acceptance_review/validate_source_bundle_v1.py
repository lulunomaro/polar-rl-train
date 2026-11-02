"""Exclusive-create final SOURCE_ONLY receipt; no future result/model/raw paths."""
from pathlib import Path
import ast
import hashlib
import json

D=Path(__file__).resolve().parent
ROOT=D.parents[1]
NAMES=[
 'EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json',
 'EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.md',
 'build_contract_source_v1.py',
 'acceptance_aggregate_cpu_source_v1.py',
 'test_acceptance_aggregate_synthetic_v1.py',
 'SYNTHETIC_TEST_RECEIPT_V1.json',
 'validate_source_bundle_v1.py',
]
contract=json.loads((D/NAMES[0]).read_text(encoding='utf8'))
tests=json.loads((D/'SYNTHETIC_TEST_RECEIPT_V1.json').read_text(encoding='utf8'))
expected=['E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50']
assert contract['role_order']==list(contract['experts'])==expected
assert contract['excluded_roles']==['H1']
assert contract['new_user_target_not_an_old_graduation_rule']['actual_new_rates'] is None
assert contract['experts']['E0']['original_atomic_predicate'] is None
assert contract['experts']['SLOPE_INDEPENDENT50']['original_atomic_predicate'] is None
assert tests['tests_run']==54 and tests['tests_ok'] and tests['failures']==tests['errors']==0
for k in ('actual_new_policy_updates','actual_physical_rollouts','actual_new_acceptance_results'):
 assert tests[k]==0
for ref in contract['sources'].values():
 p=Path(ref['path']).resolve(strict=True)
 assert p.is_relative_to(ROOT) and p.suffix in ('.py','.md','.json')
 raw=p.read_bytes()
 assert len(raw)==ref['bytes'] and hashlib.sha256(raw).hexdigest()==ref['SHA256']
files=[]
for name in NAMES:
 p=D/name;raw=p.read_bytes()
 if p.suffix=='.py':ast.parse(raw,filename=name)
 files.append(dict(path=str(p),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest()))
receipt=dict(kind='SOURCE_ONLY_BUNDLE_INTEGRITY_NOT_SKILL_ACCEPTANCE',experts=8,H1_excluded=True,source_text_refs_unchanged=len(contract['sources']),synthetic_tests=54,synthetic_failures=0,synthetic_errors=0,actual_new_policy_updates=0,actual_new_physical_runs=0,actual_new_acceptance_results=0,existing_consumer_source_modified=False,original_source_hashes_unchanged=True,files=files,local_revision_notes=[dict(item='curb113 reference line range',before='1-100 (entire 51-line source was read)',after='1-51',semantic_effect='Citation metadata only; original source unchanged.'),dict(item='initial JSON citation edit attempt',outcome='File-observation prerequisite required read before edit; read generated JSON then retried same citation-only edit. No sandbox escalation or alternate access. Original source unaffected.')],future_results_executed=False,skill_graduation=None)
p=D/'SOURCE_BUNDLE_INTEGRITY_V1.json'
with p.open('x',encoding='utf8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(str(p))
print(json.dumps({k:v for k,v in receipt.items() if k not in ('files','local_revision_notes')},ensure_ascii=False))
