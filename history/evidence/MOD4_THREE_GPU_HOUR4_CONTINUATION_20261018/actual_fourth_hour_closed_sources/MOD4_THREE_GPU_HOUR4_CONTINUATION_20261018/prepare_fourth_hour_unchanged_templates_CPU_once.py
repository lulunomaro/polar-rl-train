"""Local templates only; no model audit, source copy, transport, GPU, or accounting."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True);V=B.parent/'MOD4_THREE_GPU_HOUR3_CONTINUATION_20261018'
def write(n,s):
 ast.parse(s)
 with (B/n).open('x',encoding='utf8') as f:f.write(s)
def main():
 d=json.loads((V/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());assert d['owner']['detached_pid']==162530
 write('closed_production_continuation_CPU_v2.py',(V/'closed_production_continuation_CPU_v2.py').read_text('utf8'))
 s=(V/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8').replace("T=W/'MOD4_THREE_GPU_HOUR2_CONTINUATION_20261018'","T=W/'MOD4_THREE_GPU_HOUR3_CONTINUATION_20261018'").replace('T3h3_1810v3/','T3h4_1810v4/').replace('THREE_GPU_CLOSED_HOUR3_','THREE_GPU_CLOSED_HOUR4_');write('prepare_next_three_closed_sources_one_hour_CPU_once.py',s)
 s=(V/'deploy_three_next_closed_source_hours_once.py').read_text('utf8').replace("SOURCE='/mnt/mod4_linux_durable_20261013/T3h3_1810v3/owner'","SOURCE='/mnt/mod4_linux_durable_20261013/T3h4_1810v4/owner'").replace("A=Path('/mnt/mod4_linux_durable_20261013/T3h2_1810v2/owner')","A=Path('/mnt/mod4_linux_durable_20261013/T3h3_1810v3/owner')").replace('150567','162530');write('deploy_three_next_closed_source_hours_once.py',s)
 write('collect_next_three_actual_learning_metadata_finite_once.py',(V/'collect_next_three_actual_learning_metadata_finite_once.py').read_text('utf8'))
 with (R/'FOURTH_HOUR_UNCHANGED_TEMPLATE_LOCAL_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_AST_only=True,prior_actual_owner162530_bound=True,all_three_already_direct_production_source_filename_Adam_only=True,actual_third_hour_final_not_assumed=True,no_source_copy_or_model_audit_or_transport_or_GPU_or_budget_change=True),f,indent=2)
if __name__=='__main__':main()
