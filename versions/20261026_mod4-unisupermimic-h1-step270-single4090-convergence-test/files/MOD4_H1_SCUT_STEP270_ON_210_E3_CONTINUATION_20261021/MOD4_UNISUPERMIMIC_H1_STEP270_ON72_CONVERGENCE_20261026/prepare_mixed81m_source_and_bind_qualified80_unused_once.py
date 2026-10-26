"""Bind source80 H1/E3 only, using the latest original failed-test closure for accounting."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess
import time

H=Path(__file__).resolve().parent;T=H.parent
A=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026'
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
J=T/'MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026'
F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81M_20261026'
assert not F.exists();F.mkdir();(F/'reports').mkdir();(F/'candidates').mkdir()
shutil.copy2(A/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py')
s=(A/'candidates/same_three_closed_source_V8_landing_journal_CPU_v1.py').read_text('utf8').replace('AUTH_81_ACTUAL.json','AUTH_81M_ACTUAL.json')
(F/'candidates/same_three_closed_source_V8_landing_journal_CPU_v1.py').write_text(s,'utf8')
s=(A/'bind_complete80_sources_same_V8_exact_journal_unused_once.py').read_text('utf8')
s=s.replace('2610v81','mixed_2610v81m').replace('AUTH_81_ACTUAL.json','AUTH_81M_ACTUAL.json')
s=s.replace('H1step270_three_experts_mixed_2610v81m','H1step270_mixed_supermimic_2610v81m')
assert s.count(" for key in ('h1','e2','recovery'):")==1
s=s.replace(" for key in ('h1','e2','recovery'):"," for key in ('h1','recovery'):",1)
needle=" rec.update(remaining_after=proof['remaining_actual_snapshot'],"
assert s.count(needle)==1
s=s.replace(needle," latest_method=read(T/'MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026/reports/ONE_CARD_METHOD_TEST_FULL_TEXT_ORIGINAL_COST_RETURNED_ACTUAL.json');assert latest_method['actual_finite_returned'] and latest_method['original_canonicalNone'] and latest_method['original_fee']['duration_bound_passed']\n rec.update(remaining_after=latest_method['original_closed_remaining_snapshot'],latest_original_method_cost_and_closing=latest_method,",1)
needle="previous_owner_root=oldq['owner_root']"
assert s.count(needle)==1
s=s.replace(needle,"previous_owner_root=read(T/'MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026/reports/ONE_CARD_METHOD_TEST_ORIGINAL_OWNER_AND_NODE_DETACHED_ACTUAL.json')['owner_root']",1)
s=s.replace('bound_actual80_sources=True','bound_actual80_H1_E3_only=True')
ast.parse(s)
entry=F/'bind_actual80_H1_E3_and_latest_original_test_cost_unused_once.py'
entry.write_text(s,'utf8')
for source,target in [('deploy_actual_three_experts81_same_V8_journal_original_writer_unused_once.py','deploy_actual_mixed81m_original_writer_unused_once.py'),('collect_actual_three81_finals_original_cost_unused_once.py','collect_actual_mixed81m_finals_original_cost_unused_once.py')]:
    s=(A/source).read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V81_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81M_20261026')
    (F/target).write_text(s,'utf8')
result=subprocess.run([__import__('sys').executable,'-B','-X','utf8',str(entry)],capture_output=True,text=True)
with (F/'reports/H1_E3_BIND_STDOUT_ACTUAL.txt').open('x',encoding='utf8') as f:f.write(result.stdout)
with (F/'reports/H1_E3_BIND_STDERR_ACTUAL.txt').open('x',encoding='utf8') as f:f.write(result.stderr)
assert result.returncode==0,result.stderr
q=json.loads((F/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes())
assert set(q['specs'])=={'h1','recovery'} and 'mixed_supermimic_2610v81m' in q['owner_root']
with (H/'reports/MIXED81M_H1_E3_QUALIFIED80_AND_LATEST_TEST_BUDGET_BOUND_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),mixed_root=str(F),H1_E3_sources=q['sources'],latest_original_owner=q['previous_owner_root'],no_E2_source_model_or_Task_copy=True,no_GO=True,H1_E3_same_V8_reward_sampling_physics_and_original_valid_ready_retained=True),f,indent=2)
print(json.dumps(dict(H1_E3_actual80_bound=True,no_GO=True,mixed_root=str(F))))
