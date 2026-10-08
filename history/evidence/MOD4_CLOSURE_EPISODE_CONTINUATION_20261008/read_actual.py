from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008');R=D/'reports';sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_closure_episode_continuation as w
w.verify();read=w.read
reports={p.name:read(p) for p in R.glob('*.json') if p.name in ['SWITCH_STARTED.json','OWN_FULL_SAVE_REQUESTED.json','SWITCH_ATTENTION.json','BOUNDARY_LAUNCH_RACE_RETAINED.json','SAVED_BOUNDARY_SOURCE.json','HANDOVER_COMPLETED.json','CONTINUATION_LAUNCHED.json','D3_STATE.json','D3_DISPATCH_STARTED.json','D3_GUARDIAN_STARTED.json','D3_ATTENTION.json','D3_CURRENT_SAVE.json','D3_ACTIVE_HEALTH.json']}
RR=D.parent/'MOD4_CLOSURE_SWITCH_READER_REVIEW_20261008/reports';review={p.name:read(p) for p in RR.glob('*.json')} if RR.exists() else {}
v=dict(epoch=time.time(),reports=reports,reader_review=review,budget=w.s.q.base.budget_state(),attention=review.get('SWITCH_ATTENTION.json') or reports.get('D3_ATTENTION.json'),historical_first_reader_error=reports.get('SWITCH_ATTENTION.json'))
if 'D3_STATE.json' in reports:
 st=reports['D3_STATE.json'];v['parent']=w.identity(st['owner']['pid']);v['child']=w.identity(st['child']['pid']) if st.get('child') else None
 if v['child']:
  argv=v['child']['argv'];name=argv[argv.index('--run_name')+1];runs=list((D/'learning_logs').glob('*_'+name));assert len(runs)<=1
  if runs:
   run=runs[0];v['active_log_tail']=Path(st['active_log']).read_text(errors='replace')[-2200:];m=read(run/'run_manifest.json') if (run/'run_manifest.json').exists() else None
   if m:
    assert m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256'] and m['env']['RM_PHYSICS_DT_S']=='0.0025' and m['env']['RM_SOLVER_POS']=='32'
    for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
   ck=read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None
   if ck:assert ck['pid']==v['child']['pid'];v['own_checkpoint']=w.fullsave(Path(ck['checkpoint']));v['own_receipt']=ck
   if (run/'rolling_source_freeze.json').exists():assert read(run/'rolling_source_freeze.json')['sha256']==read(R/'SOURCE_FREEZE.json')['sha256'];v['own_run_source_frozen']=True
   for n in ['CLOCK_TRAINING_HEALTH.json','DELAY_RESUME_STARTUP_VERIFIED.json']:
    if (run/n).exists():v[n]=read(run/n)
v['budget']={k:v['budget'][k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')}
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as sf:
  for n in v['reports']:sf.get('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/reports/'+n,str(R/n))
 print(json.dumps(dict(epoch=v['epoch'],attention=v['attention'],parent=v.get('parent'),child=v.get('child'),phase=v['reports'].get('D3_STATE.json',{}).get('phase'),own=v.get('own_checkpoint'),active_log_tail=v.get('active_log_tail'),health=v.get('CLOCK_TRAINING_HEALTH.json'),handover=v['reports'].get('HANDOVER_COMPLETED.json'),budget=v['budget'])))
finally:c.close()
