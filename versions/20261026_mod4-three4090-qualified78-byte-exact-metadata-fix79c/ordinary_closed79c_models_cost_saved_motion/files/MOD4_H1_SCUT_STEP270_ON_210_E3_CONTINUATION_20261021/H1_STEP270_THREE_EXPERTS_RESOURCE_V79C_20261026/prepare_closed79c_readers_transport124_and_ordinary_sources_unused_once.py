"""New79c-only closed readers and80 exact transport/source archive. No remote action."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026';U0=T/'H1_STEP270_CLOSED78_SAVED_REPLAY_AFTER_V8_20261026';U=T/'H1_STEP270_CLOSED79C_SAVED_REPLAY_AFTER_V8_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
assert not U.exists();U.mkdir();(U/'reports').mkdir();made=[]
def put(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 made.append(str(p))
for p in U0.glob('*.py'):
 s=p.read_text('utf8').replace('CLOSED78','CLOSED79C').replace('closed78','closed79c').replace('saved78','saved79c').replace('V78_','V79C_').replace('2610v78','2610v79c').replace('Unused78','Unused79c').replace('Closed78','Closed79c').replace('complete78','complete79c').replace('New78','New79c')
 put(U/p.name.replace('closed78','closed79c').replace('saved78','saved79c'),s)
for name in ('read_closed78_saved_text_throughput_and_health_unused_once.py','read_closed78_three_expert_task_metrics_text_CPU_unused_once.py'):
 s=(P/name).read_text('utf8').replace('CLOSED78','CLOSED79C').replace('closed78','closed79c').replace('V78_','V79C_').replace('Closed78','Closed79c')
 put(N/name.replace('closed78','closed79c'),s)
s=(B/'same_authorized_session_compressed_transport_v123.py').read_text('utf8');needle="        'collect_actual_three79c_finals_original_cost_unused_once.py',";assert s.count(needle)==1
names=('extract_closed79c_last_two_saved_prefixes_CPU_unused_once.py','deploy_actual_three_experts80_V8_readonly_landing_journal_original_writer_unused_once.py','collect_three_experts80_readonly_landing_journal_first_PPO_finite_unused_once.py','collect_actual_three80_finals_original_cost_unused_once.py')
s=s.replace(needle,needle+'\n'+''.join('        '+repr(n)+',\n' for n in names),1);put(B/'same_authorized_session_compressed_transport_v124.py',s)
s=(P/'archive_closed78_models_lifetime_and_saved_motion_ordinary_unused_once.py').read_text('utf8')
s=s.replace('20261026_mod4-three4090-v8-readonly-lifetime-diagnostics78','20261026_mod4-three4090-qualified78-byte-exact-metadata-fix79c').replace('b684a1ebec0ad739d9e64a2c073d680d6c12733f','0849546c521dc6b2e6c5306073cc9883a430fe44').replace('V79_','V80_').replace('V78_','V79C_').replace('CLOSED78','CLOSED79C').replace('closed78','closed79c').replace('Complete78','Complete79c').replace('completed78','completed79c').replace('consumed78','consumed79c').replace('1450','1451').replace('transport_v121.py','transport_v124.py')
s=s.replace("V=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79B_20261026'\nroots=[N,U,F,M,V]","roots=[N,U,F,M]").replace('H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026','H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026')
s=s.replace(",T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v122.py'",'')
s=s.replace('Same79 continuation protocol and a V9 extended-clearance-carry reward-math candidate with local CPU/saved-SDK validation are source-only preparation; V9 is not installed or proven as a learning improvement.','New80 protocol and readonly landing journal are source-only preparation, with original action/reward/trace/physics retained. V9 remains unselected and uninstalled.')
put(N/'archive_closed79c_models_lifetime_saved_motion_and80_preparation_ordinary_unused_once.py',s)
with (N/'reports/CLOSED79C_READERS_TRANSPORT124_ORDINARY_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_only=True,created=made,no_remote_GPU_or_current_training_action=True),f,indent=2)
print(json.dumps(dict(source_only79c_readers80_transport=True,created=len(made))))
