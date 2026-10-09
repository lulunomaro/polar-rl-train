"""Read own current stable entry/child/fullsave and canonical; no mutations."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+D.name
try:
 code='''
from pathlib import Path
import sys,json,time
D=Path(ROOT);R=D/'reports';sys.path.insert(0,str(D));import supervise_e1_reviewed_stable_continuation as w
w.verify();st=w.read(R/'E1_STATE.json');parent=w.identity(st['owner']['pid']);child=w.identity(st['child']['pid']) if st.get('child') else None
if parent:assert parent['start_ticks']==st['owner']['start_ticks'] and str(D/'supervise_e1_reviewed_stable_continuation.py') in parent['argv']
if child:assert child['start_ticks']==st['child']['start_ticks'] and str(D/'isaac/mod4/train_e1_route_health_resume_ppo.py') in child['argv']
names=('E1_BEHAVIOR_GATED_ENTRY_STARTED.json','E1_DISPATCH_STARTED.json','E1_INSTALL_BOUNDARY.json','E1_GUARDIAN_STARTED.json','E1_CURRENT_SAVE.json','E1_ACTIVE_HEALTH.json','E1_REVIEW_READY.json','E1_ATTENTION.json','E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json')
receipts={n:w.read(R/n) if (R/n).exists() else None for n in names}
v=dict(epoch=time.time(),root=str(D),state=st,actual_parent=parent,actual_child=child,receipts=receipts,budget=w.s.q.base.budget_state(),Sactive=w.read(w.s.q.ctl.STATE_PATH).get('active_training'),source_count=len(w.read(R/'SOURCE_FREEZE.json')['sha256']),own_run=None,no_GPU_or_canonical_write=True)
if child:
 name=child['argv'][child['argv'].index('--run_name')+1];logs=Path(child['argv'][child['argv'].index('--log_root')+1]);runs=list(logs.glob('*_'+name))
 if len(runs)==1:
  run=runs[0];contracts={n:w.read(run/n) if (run/n).exists() else None for n in ('latest_complete.json','run_manifest.json','rolling_source_freeze.json','CLOCK_TRAINING_HEALTH.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json')}
  v['own_run']=dict(path=str(run),contracts=contracts)
  if contracts['latest_complete.json']:
   rec=contracts['latest_complete.json'];assert rec['pid']==child['pid'];v['own_run']['checkpoint']=w.fullsave(Path(rec['checkpoint']))
   m=contracts['run_manifest.json'];assert m['source_map']==w.read(R/'SOURCE_FREEZE.json')['sha256']
   v['own_run']['snapshot_count']=len(m['src_sha256']);assert all(w.s.q.base.sha(run/'src_snapshot'/n)==h for n,h in m['src_sha256'].items())
   if contracts['rolling_source_freeze.json']:assert contracts['rolling_source_freeze.json']['sha256']==m['source_map']
  for n in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json'):
   p=contracts[n]
   if p:assert p['source_sha256']==st['source']['sha256'] and p['PhysX_exact_resume_claimed'] is False
 if st.get('active_log'):
  p=Path(st['active_log']);text=p.read_text(errors='replace');v['PPO_log_count']=text.count('Learning iteration');v['log_tail']=text[-4500:]
else:v['PPO_log_count']=0
print(json.dumps(v))
'''.replace('ROOT',repr(root))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'E1_GENTLE_STABLE_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],phase=v['state']['phase'],parent=v['actual_parent'],trainer=v['actual_child'],PPO_log_count=v['PPO_log_count'],own_save=(v.get('own_run') or {}).get('checkpoint'),attention=v['receipts']['E1_ATTENTION.json'],remaining=v['budget']['remaining_training_seconds'],deadline=v['state'].get('deadline_epoch'))))
finally:c.close()
