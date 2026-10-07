"""Read reusable actual dispatcher/authority boundary, never launch or write budget."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,time,json
D=Path('/home/egde/rl_candidates/MOD4_D3_1MS_FULL_CONTRACT_20261008');R=D/'reports';sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d3_saved_boundary as w
launched=w.read(R/'D3_DISPATCH_LAUNCHED.json');i=w.identity(launched['dispatcher']['pid']);assert i and i['start_ticks']==launched['dispatcher']['start_ticks'] and i['ppid']==1 and i['argv'][1]==str(D/'supervise_d3_saved_boundary.py')
assert not (R/'D3_ATTENTION.json').exists();w.verify();state=w.read(R/'D3_STATE.json');b=w.s.q.base.budget_state()
children=[]
for p in Path('/proc').glob('[0-9]*/stat'):
 try:
  if int(p.read_text().rsplit(')',1)[1].split()[1])==i['pid']:children.append(w.identity(int(p.parent.name)))
 except (OSError,ValueError):pass
if state['phase'].startswith('waiting_'):
 assert not children and not (R/'D3_INSTALL_BOUNDARY.json').exists() and not (R/'D3_GUARDIAN_STARTED.json').exists()
 assert b['active_segment'] and b['active_segment']['pid']!=i['pid']
for key in ('D3_DISPATCH_STARTED.json','D3_WAIT_STARTED.json'):assert (R/key).exists()
print(json.dumps(dict(epoch=time.time(),dispatcher=i,children=children,state=state,budget_active=b['active_segment'],source_count=231,CPU_contracts=w.read(R/'D3_FULL_CONTROLLER_CPU_CONTRACT.json'),SDK_review=w.read(R/'D3_1MS_ACTUAL_SDK_REVIEW.json'),source=w.read(R/'SELECTED_D1D2_BEHAVIOR_SOURCE.json'),new_GPU_authority_started=(R/'D3_INSTALL_BOUNDARY.json').exists(),attention=None)))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'D3_DISPATCH_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as sf:
  for n in ('D3_DISPATCH_STARTED.json','D3_WAIT_STARTED.json'):sf.get('/home/egde/rl_candidates/MOD4_D3_1MS_FULL_CONTRACT_20261008/reports/'+n,str(R/n))
 print(json.dumps(dict(epoch=v['epoch'],dispatcher=v['dispatcher'],phase=v['state']['phase'],children=v['children'],new_GPU_authority_started=v['new_GPU_authority_started'],active_trainer=v['budget_active']['pid'] if v['budget_active'] else None)))
finally:c.close()
