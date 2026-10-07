from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_S1A_FROZEN_SAVED_SCHEMA_REVIEW_20261007'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('ROOT');sys.path.insert(0,str(D));import continue_frozen_saved_schema_review_once as x
x.verify();rows={p.name:x.q.q.w.read(p) for p in (D/'reports').glob('*.json') if p.name.startswith(('FROZEN_','behavior_'))}
start=rows['FROZEN_PROTOCOL_REVIEW_LAUNCHED.json'];s=rows.get('FROZEN_PROTOCOL_REVIEW_STATE.json',{})
print(json.dumps(dict(epoch=time.time(),owner=x.q.q.helpers.identity(start['owner']['pid']),child=x.q.q.helpers.identity(s['child']['pid']) if s.get('child') else None,state=s,receipts=rows,budget=x.q.q.base.budget_state())))
'''.replace("Path('ROOT')","Path("+repr(ROOT)+")")
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'FROZEN_PROTOCOL_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 dest=R/'native_frozen';dest.mkdir(exist_ok=True)
 with c.open_sftp() as s:
  for n,row in v['receipts'].items():
   if n.startswith('behavior_') and n.endswith('_COMPLETE.json'):
    remote=row['output'];name=remote.rsplit('/',1)[-1];s.get(remote,str(dest/name))
 print(json.dumps(dict(epoch=v['epoch'],owner=v['owner'],child=v['child'],phase=v['state'].get('phase'),attention=v['receipts'].get('FROZEN_PROTOCOL_REVIEW_ATTENTION.json'),completed=[n for n in v['receipts'] if n.endswith('_COMPLETE.json')],ready=bool(v['receipts'].get('FROZEN_MATCHED_REPLAY_READY.json')))))
finally:c.close()
