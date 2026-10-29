"""NEW finite source111 controller, actual CPU-bound and pre-sealed readers."""
from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
P=T/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029/prepare_TWO106_actual20s_CPU_bound_original_writer_and_readers_SOURCE_ONLY_once.py'
s=P.read_text(encoding='utf8')
s=s.replace('TWO106_FUDAN270_20S_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1','TWO111_FUDAN270_COHERENT_REWARD_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1')
s=s.replace('TWO106_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1','TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1')
s=s.replace('TWO106_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json','TWO111_SOURCE_PAYLOADS_PREPARED_NO_GO_ACTUAL.json').replace('TWO106_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json','TWO111_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json')
s=s.replace('TWO106_FUDAN270_USER_EPISODE20_','TWO111_FUDAN270_COHERENT_REWARD_').replace('MOD4_TWO106_FUDAN270_EPISODE20_2610v106','MOD4_TWO111_FUDAN270_COHERENT_REWARD_2610v111')
s=s.replace('expected_closed_remaining=509633.3206150532',"expected_closed_remaining=admitted['results']['seed27']['resource']['remaining_snapshot']")
s=s.replace('mod4.native104_to_fudan270.target106.episode20.v1','mod4.native107_to_fudan270.target111.coherent_reward.v1')
s=s.replace("N=T/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029';B=N/'payloads/","N=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029';B=N/'payloads_v2/")
s=s.replace('MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029','MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029')
s=s.replace('continue_qualified104_fudan270_clock_aligned20s','continue_qualified107_coherent_world_task_reward111')
s=s.replace('native106_fudan20s_pins_v1','native111_coherent_reward_pins_v1')
s=s.replace('TWO106','TWO111').replace('NATIVE106','NATIVE111').replace('NEW106','NEW111').replace('closed106','closed111')
# A writer hook inserts the new actual-before-use proof check before protocol
# hashes/manifests are generated, leaving original accounting/common bytes exact.
tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='write');lines=s.splitlines(keepends=True)
hook='''def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.name in ('h1_next72_protocol_actual95_v2.py','h1_seed28_next72_protocol_v100.py'):
  needle=" require(v.get('fudan_step_task')==s['fudan_step_task']"
  assert s.count(needle)==1
  check=" require(v.get('reward111_actual_installed_readback',{}).get('passed') is True and v['reward111_actual_installed_readback']['source_own_bank_poses']==133 and v['reward111_actual_installed_readback']['maximum_heading_normalized_input']<=1.1,'actual installed111 reward/FK/inherited heading norm proof')\\n"
  s=s.replace(needle,check+needle)
 with p.open('x',encoding='utf8') as f:f.write(s)
'''
s=''.join(lines[:node.lineno-1])+hook+''.join(lines[node.end_lineno:])
# The final-formal reviewer uses the new qualified107 INPUT progress/schema.
s=s.replace('input104 PT0','input107 PT0')
ast.parse(s);exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
