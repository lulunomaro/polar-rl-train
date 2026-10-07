"""Read actual current source authority and CPU publisher without launch authority."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
S=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007');P=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_ASYNC_DEPENDENCY_PUBLICATION_20261007');N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007')
sys.path.insert(0,str(N));import continue_clock1000_worker_manifest_review_once as q
def identity(pid):
 i=q.helpers.identity(pid)
 if i:
  stat=(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();i['ppid']=int(stat[1])
 return i
state=q.w.read(S/'reports/E0_SENSOR_DR_STATE.json');rows={p.name:q.w.read(p) for p in (S/'reports').glob('*.json') if p.stat().st_size<2000000}
pub={p.name:q.w.read(p) for p in (P/'reports').glob('*.json')}
logs={p.name:[x[:500] for x in p.read_text(errors='replace').splitlines()[-5:]] for p in S.glob('*.log')}
budget=q.base.budget_state();a=budget['active_segment'];remaining=budget['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0)
v=dict(epoch=time.time(),state=state,owner=identity(state['owner']['pid']),child=identity(state['child']['pid']) if state.get('child') else None,receipts=rows,
 publisher=pub,publisher_actual=identity(pub['STARTED.json']['pid']) if pub.get('STARTED.json') else None,publisher_log_tail=(P/'publisher.log').read_text(errors='replace').splitlines()[-5:],
 budget=budget,actual_remaining_seconds=remaining,S_active_training=q.w.read(q.ctl.STATE_PATH).get('active_training'),logs=logs)
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_DEPENDENCY_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2))
 print(json.dumps(dict(epoch=v['epoch'],phase=v['state']['phase'],owner=v['owner'],child=v['child'],attention=v['receipts'].get('E0_SENSOR_ATTENTION.json'),completed=[n for n in v['receipts'] if n.endswith('_COMPLETE.json')],publisher_phase=(v['publisher'].get('STATE.json') or {}).get('phase'),publisher=v['publisher_actual'],publisher_attention=v['publisher'].get('ATTENTION.json'),remaining_seconds=v['actual_remaining_seconds'],active=v['budget']['active_segment'],logs=v['logs'])))
finally:c.close()
