"""Prepare new78-only saved readers and same79 continuation transport; source-only."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026';U0=T/'H1_STEP270_CLOSED77_SAVED_REPLAY_AFTER_V8_20261026';U=T/'H1_STEP270_CLOSED78_SAVED_REPLAY_AFTER_V8_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
assert not U.exists();U.mkdir();(U/'reports').mkdir();made=[]
def put(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 made.append(str(p))
for p in U0.glob('*.py'):
 s=p.read_text('utf8').replace('CLOSED77','CLOSED78').replace('closed77','closed78').replace('saved77','saved78').replace('V77_','V78_').replace('2610v77','2610v78').replace('Unused77','Unused78').replace('Closed77','Closed78').replace('complete77','complete78').replace('New77','New78')
 put(U/p.name.replace('closed77','closed78').replace('saved77','saved78'),s)
for name in ('read_closed77_saved_text_throughput_and_health_unused_once.py','read_closed77_three_expert_task_metrics_text_CPU_unused_once.py'):
 s=(P/name).read_text('utf8').replace('CLOSED77','CLOSED78').replace('closed77','closed78').replace('V77_','V78_').replace('Closed77','Closed78')
 put(N/name.replace('closed77','closed78'),s)
s=(B/'same_authorized_session_compressed_transport_v120.py').read_text('utf8');needle="        'collect_actual_three78_finals_original_cost_unused_once.py',";assert s.count(needle)==1
names=('extract_closed78_last_two_saved_prefixes_CPU_unused_once.py','deploy_actual_three_experts79_same_V8_lifetime_diag_original_writer_unused_once.py','collect_three_experts79_same_V8_lifetime_diag_first_PPO_finite_unused_once.py','collect_actual_three79_finals_original_cost_unused_once.py')
s=s.replace(needle,needle+'\n'+''.join('        '+repr(v)+',\n' for v in names),1);put(B/'same_authorized_session_compressed_transport_v121.py',s)
s=(P/'archive_closed77_models_and_saved_motion_ordinary_unused_once.py').read_text('utf8')
s=s.replace('20261026_mod4-three4090-same-v8-qualified76-continuation77','20261026_mod4-three4090-v8-readonly-lifetime-diagnostics78').replace('86bdb9bc6c60b2e20eb91f0b96203026c179a5ea','b684a1ebec0ad739d9e64a2c073d680d6c12733f')
s=s.replace('V78_','V79_').replace('V77_','V78_').replace('CLOSED77','CLOSED78').replace('closed77','closed78').replace('completed77','completed78').replace('Complete77','Complete78').replace('consumed77','consumed78').replace('1449','1450').replace('transport_v120.py','transport_v121.py').replace('H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026','H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026')
s=s.replace('Readonly lifetime-counter source preparation and both original failed CPU candidates are retained as source-only evidence, not runtime or frozen evaluation.','Actual readonly lifetime-counter output is separate from model and skill qualification. Same79 continuation protocol and a V9 extended-clearance-carry reward-math candidate with local CPU/saved-SDK validation are source-only preparation; V9 is not installed or proven as a learning improvement.')
put(N/'archive_closed78_models_lifetime_and_saved_motion_ordinary_unused_once.py',s)
with (N/'reports/CLOSED78_READERS_TRANSPORT121_ORDINARY_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_only=True,created=made,no_remote_query_or_current78_mutation=True,V9_hypothesis_not_deployed_or_in79_source=True),f,indent=2)
print(json.dumps(dict(source_only=True,created=len(made))))
