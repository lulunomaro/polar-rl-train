"""Prepare only new77 saved readers, exact transport120 and ordinary archive. No remote action."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026'
U0=T/'H1_STEP270_CLOSED76_SAVED_REPLAY_AFTER_V8_20261026'
U=T/'H1_STEP270_CLOSED77_SAVED_REPLAY_AFTER_V8_20261026'
F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026'
M=T/'H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026'
B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
assert not U.exists();U.mkdir();(U/'reports').mkdir()
written=[]
def put(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 written.append(str(p))
for p in U0.glob('*.py'):
 s=p.read_text('utf8').replace('CLOSED76','CLOSED77').replace('closed76','closed77').replace('saved76','saved77').replace('V76_','V77_').replace('2610v76','2610v77').replace('Unused76','Unused77').replace('Closed76','Closed77').replace('complete76','complete77').replace('New76','New77').replace('Unused until complete76','Unused until complete77')
 put(U/p.name.replace('closed76','closed77').replace('saved76','saved77'),s)
for name in ('read_closed76_saved_text_throughput_and_health_unused_once.py','read_closed76_three_expert_task_metrics_text_CPU_unused_once.py'):
 s=(P/name).read_text('utf8').replace('CLOSED76','CLOSED77').replace('closed76','closed77').replace('V76_','V77_').replace('Closed76','Closed77')
 put(N/name.replace('closed76','closed77'),s)
s=(B/'same_authorized_session_compressed_transport_v119.py').read_text('utf8')
needle="        'collect_actual_three77_finals_original_cost_unused_once.py',"
assert s.count(needle)==1
extra=[
 'extract_closed77_last_two_saved_prefixes_CPU_unused_once.py',
 'deploy_actual_three_experts78_V8_lifetime_diag_original_writer_unused_once.py',
 'collect_three_experts78_V8_lifetime_diag_first_PPO_finite_unused_once.py',
 'collect_actual_three78_finals_original_cost_unused_once.py']
s=s.replace(needle,needle+'\n'+''.join('        '+repr(n)+',\n' for n in extra),1)
put(B/'same_authorized_session_compressed_transport_v120.py',s)
s=(P/'archive_closed76_models_and_saved_motion_ordinary_unused_once.py').read_text('utf8')
s=s.replace('20261026_mod4-three4090-same-v8-qualified75-continuation76','20261026_mod4-three4090-same-v8-qualified76-continuation77')
s=s.replace('4da472385d8d1d9b302f2bfc97e6b17be426a343','86bdb9bc6c60b2e20eb91f0b96203026c179a5ea')
s=s.replace('CLOSED76','CLOSED77').replace('closed76','closed77').replace('Complete76','Complete77').replace('completed76','completed77').replace('consumed76','consumed77').replace('V77_','V78_').replace('1448','1449').replace('transport_v119.py','transport_v120.py')
s=s.replace("roots=[N,U,F]", "M=T/'H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026'\nroots=[N,U,F,M]")
s=s.replace("Saved-only motion and production speed descriptive reports retain their exact sampling limitations;", "Readonly lifetime-counter source preparation and both original failed CPU candidates are retained as source-only evidence, not runtime or frozen evaluation. Saved-only motion and production speed descriptive reports retain their exact sampling limitations;")
put(N/'archive_closed77_models_and_saved_motion_ordinary_unused_once.py',s)
with (N/'reports/CLOSED77_READERS_TRANSPORT120_ORDINARY_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),source_only=True,created=written,no_remote_or_model_raw_read_or_training_change=True),f,indent=2)
print(json.dumps(dict(source_only=True,created_count=len(written))))
