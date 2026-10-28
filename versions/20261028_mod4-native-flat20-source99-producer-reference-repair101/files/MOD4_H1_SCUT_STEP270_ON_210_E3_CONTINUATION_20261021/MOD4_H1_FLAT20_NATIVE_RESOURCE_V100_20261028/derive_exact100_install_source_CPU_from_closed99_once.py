from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028'
p=O/'install_two99_exact_sources_SDK_initial_CPU_once.py';s=p.read_text();tree=ast.parse(s);node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRE' for t in x.targets));pre=ast.literal_eval(node.value)
for a,b in [('MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1','MOD4_H1_STANCE_START_COMPARE_2610v99/continue97'),('MOD4_TWO97_H1_E3_2610v97','MOD4_TWO99_NATIVE_START_COMPARE_2610v99'),('531527.5335400105','524298.0874166489'),('595647','604005'),('1793175876.15','1793184720.95'),('7259.734082698822','7229.4461233615875'),('3615.187491416931','3616.467855453491'),('3644.546591281891','3612.9782679080963'),("'e3'","'restart'"),("v['mode']=='continue97'","v['mode'] in ('seed27','seed28')")]:
 assert a in pre,a;pre=pre.replace(a,b)
ast.parse(pre);assert '37e34522213d' in pre and '37restart' not in pre
lines=s.splitlines(keepends=True);s=''.join(lines[:node.lineno-1])+'PRE='+repr(pre)+'\n'+''.join(lines[node.end_lineno:])
s=s.replace('TWO99_EXACT_START_PAYLOADS_PREPARED_ACTUAL.json','TWO100_TARGET20_EXACT_QUALIFIED99_PAYLOADS_PREPARED_V2_ACTUAL.json').replace('TWO97_H1_E3_NEW_FULL_CPU_OWNER_SOURCE_V1/reports/TWO97_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json','TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1/reports/TWO99_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json')
s=s.replace("['continue97','restart0']","['seed27','seed28']").replace("('continue97','restart0')","('seed27','seed28')").replace('TWO99_INSTALL','TWO100_INSTALL').replace('NATIVE99_','NATIVE100_').replace('TWO99_SOURCE','TWO100_SOURCE').replace('TWO99_ACTUAL_TWO_SOURCE','TWO100_ACTUAL_TWO_SOURCE').replace('TWO99_SOURCE_INSTALL','TWO100_SOURCE_INSTALL').replace('TWO99_SOURCE_SDK_CPU','TWO100_SOURCE_SDK_CPU').replace('two99_','two100_')
ast.parse(s);entry=N/'install_two100_target20_exact_saved99_sources_SDK_initial_CPU_once.py';entry.write_text(s,encoding='utf8')
(N/'reports/FROZEN_UNUSED_TARGET20_INSTALLER_SOURCE_INDEX_V1.json').write_text(json.dumps(dict(epoch=time.time(),entry=str(entry),SHA=hashlib.sha256(entry.read_bytes()).hexdigest(),source99_original_closed_fees_and_identities_bound=True,UUID_literals_unchanged=True,unused=True,no_remote_or_model_read=True),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,entry=str(entry))))
