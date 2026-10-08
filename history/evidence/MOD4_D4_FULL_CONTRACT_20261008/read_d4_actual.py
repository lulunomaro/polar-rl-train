"""Read actual new authority, native/PPO/own saves; no launches or ledger writes."""
from pathlib import Path
import sys,json,shlex,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008'
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d4_full_contract as w
w.verify();st=w.read(R/'D4_STATE.json') if (R/'D4_STATE.json').exists() else None
files={p.name:w.read(p) for p in R.glob('*.json') if p.name.startswith(('D4_','d4_'))}
own=w.identity(st['owner']['pid']) if st else None;child=w.identity(st['child']['pid']) if st and st.get('child') else None
log=Path(st['active_log']) if st and st.get('active_log') else D/'controller.log'
tail=log.read_text(errors='replace').splitlines()[-45:] if log.exists() else []
current=files.get('D4_CURRENT_SAVE.json');source=None
if current:
 run=Path(current['own_run']);m=w.read(run/'run_manifest.json');rec=w.read(run/'latest_complete.json')
 assert m['source_map']==w.read(R/'SOURCE_FREEZE.json')['sha256'] and w.read(run/'rolling_source_freeze.json')['sha256']==m['source_map']
 for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
 source=dict(run=str(run),latest=rec,checkpoint=w.fullsave(Path(rec['checkpoint']),count=m['num_envs']),manifest=m,snapshots=len(m['src_sha256']))
v=dict(epoch=time.time(),phase=st,owner=own,child=child,files=files,own_save=source,log_tail=tail,controller_tail=(D/'controller.log').read_text(errors='replace').splitlines()[-15:],budget={k:w.s.q.base.budget_state()[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')})
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'D4_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2))
 with c.open_sftp() as f:
  for n,row in v['files'].items():
   if n not in ('D4_CURRENT_SAVE.json','D4_ACTIVE_HEALTH.json'):(R/n).write_text(json.dumps(row,indent=2))
 print(json.dumps(dict(epoch=v['epoch'],phase=v['phase'],owner=v['owner'],child=v['child'],own_save={k:v['own_save'][k] for k in ('run','latest','checkpoint','snapshots')} if v['own_save'] else None,attention=v['files'].get('D4_ATTENTION.json'),log_tail=v['log_tail'],controller_tail=v['controller_tail'])))
finally:c.close()
