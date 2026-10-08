"""Read the new CPU-only world's actual publisher and completed evidence."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import json,time,sys
D=Path('/home/egde/rl_candidates/MOD4_D4_WORLD_DISPATCH_REVIEW_20261008');P=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008')
sys.path.insert(0,str(P));sys.path.insert(0,str(P/'isaac/mod4'));import supervise_d4_full_contract as w
files={p.name:w.read(p) for p in (D/'reports').glob('*.json')};started=files.get('PUBLISHER_STARTED.json');identity=w.identity(started['identity']['pid']) if started else None
st=w.read(P/'reports/D4_STATE.json');owner=w.identity(st['owner']['pid']);child=w.identity(st['child']['pid']) if st.get('child') else None
blocks={str(n):w.read(P/'reports'/('d4_stable_block'+str(n)+'_PASSED.json')) for n in (1,2,3) if (P/'reports'/('d4_stable_block'+str(n)+'_PASSED.json')).exists()}
outputs=[]
for label in ('45-d4world-anchor','55-d4world-b1','55-d4world-b2','55-d4world-b3'):
    folder=w.s.q.ER.parent/'eval_results'/('clk2500-closure-episode-d3-'+label+'-world')
    if (folder/'result.json').exists():outputs.append(dict(label=label,result=w.read(folder/'result.json'),probe=w.read(folder/'probe.json') if (folder/'probe.json').exists() else None))
print(json.dumps(dict(epoch=time.time(),files=files,publisher_actual_identity=identity,production_state=st,production_actual_owner=owner,production_actual_child=child,blocks=blocks,returned_corrected_world_cases=outputs,canonical={k:w.s.q.base.budget_state()[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')})))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'WORLD_PUBLICATION_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    for n,row in v['files'].items():(R/n).write_text(json.dumps(row,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],publisher=v['publisher_actual_identity'],attention=v['files'].get('PUBLICATION_ATTENTION.json'),phase=v['production_state']['phase'],production_child=v['production_actual_child'],blocks=[dict(block=k,checkpoint=x['checkpoint'],health=x['health'],updates=x['actual_updates']) for k,x in v['blocks'].items()],corrected_world=[dict(label=x['label'],exit_code=x['result']['exit_code'],has_D4_audit=bool((x['probe'] or {}).get('physical_action_delay_audit'))) for x in v['returned_corrected_world_cases']],budget=v['canonical'])))
finally:c.close()
