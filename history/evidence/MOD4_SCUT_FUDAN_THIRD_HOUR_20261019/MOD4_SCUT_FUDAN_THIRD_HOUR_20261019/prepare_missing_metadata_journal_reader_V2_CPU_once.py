"""Only a new bounded missing-metadata reader after the original transport returned."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;R=B/'reports';p=B/'collect_next_three_actual_learning_metadata_finite_once.py';s=p.read_text('utf8')
s=s.replace('THREE_REAL_LEARNING_METADATA_FINITE_COLLECTOR_STARTED_ACTUAL.json','THREE_REAL_LEARNING_MISSING_METADATA_JOURNAL_V2_STARTED_ACTUAL.json').replace('same72_connection_max1800_metadata_then_one_source210','same72_connection_max600_missing_metadata_after_original10054').replace('time.monotonic()-begin>=1800','time.monotonic()-begin>=600')
needle="target=d.a.code(c,d.a.PY,META,json.dumps(targetroots),timeout=90);observations+=1"
replacement=needle+"\n   with (d.R/'MISSING_LEARNING_METADATA_V2_OBSERVATIONS_JOURNAL.txt').open('a',encoding='utf8') as journal:journal.write(json.dumps(dict(observation=observations,actual=target))+'\\n')"
assert s.count(needle)==1;s=s.replace(needle,replacement);ast.parse(s)
with (B/'collect_only_missing_learning_metadata_journal_V2_once.py').open('x',encoding='utf8') as f:f.write(s)
with (R/'MISSING_METADATA_JOURNAL_V2_READER_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original10054_kept=True,change='Bound one fresh metadata connection to600s and append each observed snapshot before subsequent transport calls; retain proof if transport later resets.',keepalive15_already_present_not_claimed_as_cause_or_fix=True,no_remote_job_native_or_PT_replay=True,no_system_SSH_driver_or_budget_change=True),f,indent=2)
print('Prepared bounded missing metadata reader with append-only observations.')
