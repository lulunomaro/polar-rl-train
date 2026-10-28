from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';p=L/'TWO100_TWO_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1/observe_two100_actual20cm_two_native_first_policy_metadata_once.py';s=p.read_text()
a='TWO100_TARGET20_TWO_NATIVE_ORIGINAL_OWNER_SOURCE_V1';assert s.count(a)==1;s=s.replace(a,'ORIGINAL_CONTROLLER_PATH_PLACEHOLDER').replace('TWO100','TWO101').replace('ORIGINAL_CONTROLLER_PATH_PLACEHOLDER','TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1');ast.parse(s)
B=L/'TWO101_PRODUCER_FIXED_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1';B.mkdir();(B/'reports').mkdir();entry=B/'observe_two101_producer_fixed_actual20cm_first_policy_once.py';entry.write_text(s,encoding='utf8')
(B/'FROZEN_UNUSED_TWO101_EXACT_FIRST_OBSERVER_INDEX_V1.json').write_text(json.dumps(dict(epoch=time.time(),unused=True,entry=str(entry),SHA=hashlib.sha256(entry.read_bytes()).hexdigest(),original20cm_checks_and_100schema_unchanged_only101_root_bound=True),indent=2),encoding='utf8');print(json.dumps(dict(prepared=True,entry=str(entry))))
