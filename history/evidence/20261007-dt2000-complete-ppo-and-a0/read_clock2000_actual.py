from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
code=r'''
from pathlib import Path
import json,sys,time
D=Path('ROOT');sys.path.insert(0,str(D));import continue_clock2000_practical_review_once as q
read=lambda p:json.loads(p.read_text()) if p.exists() else None
s=read(D/'reports/SELECTED_CLOCK_STATE.json') or {};b=q.base.budget_state();a=b['active_segment'];aut=read(q.ctl.STATE_PATH)
launch=read(D/'reports/SELECTED_CLOCK_LAUNCHED.json');own=q.helpers.identity(launch['owner']['pid']);child=q.helpers.identity(a['pid']) if a else q.helpers.identity(s['child']['pid']) if s.get('child') else None
g=read(D/'reports/SELECTED_CLOCK_GUARDIAN_STARTED.json');guard=q.helpers.identity(g['pid']) if g else None
log=Path(a['log']) if a else Path(s['output']).with_suffix('.log') if s.get('output') else D/'supervisor.log'
latest=None;checkpoint=None;health=None
if a:
 for folder in [q.P/'logs',q.P/'autonomy_preflight_logs']:
  try:
   run=q.w.rate.trainer_run(folder,a['pid']);latest=read(run/'latest_complete.json');health=read(run/'CLOCK_TRAINING_HEALTH.json')
   if latest:checkpoint=q.base.checkpoint(Path(latest['checkpoint']))
   break
  except (AssertionError,TypeError,KeyError,FileNotFoundError):continue
facts=read(D/'reports/SELECTED_CLOCK_BEHAVIOR_REVIEW.json');brief=None
if facts:
 rows=facts['world']['rows'];brief=dict(world_passed=sum(x['pass_'] for x in rows),world_total=len(rows),worst_abs_cross=max(abs(x['cross_m_s']) for x in rows),pure4pi=facts['pure4pi'],straight=facts['straight'],strict_sufficient_evidence=facts['strict_sufficient_evidence'])
v=dict(epoch=time.time(),phase=s.get('phase'),owner=own,guardian=guard,child=child,active_segment=a,remaining=b['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0),
 SDK=read(D/'reports/CROSSBIN_SDK_PASSED.json'),native20k=read(D/'reports/NATIVE20K_PASSED.json'),behavior=brief,preflight=read(D/'reports/SELECTED_CLOCK_PPO_PREFLIGHT_PASSED.json'),adoption=read(D/'reports/SELECTED_CLOCK_ADOPTION.json'),
 own_latest=latest,own_checkpoint=checkpoint,own_health=health,review_ready=read(D/'reports/SELECTED_CLOCK_REVIEW_READY.json'),attention=read(D/'reports/SELECTED_CLOCK_ATTENTION.json'),tail=log.read_text(errors='replace')[-1800:] if log.exists() else None)
print(json.dumps(v))
'''.replace('ROOT',root)
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 (R/'DT2000_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8');brief=dict(v);brief['review_ready']={'present':True,'keys':list(v['review_ready'])} if v.get('review_ready') else None
 brief['preflight']={'passed':True,'task_events':[x['physical_health']['actual_task_reset_events'] for x in v['preflight']['exact_physical_health']]} if v.get('preflight') else None
 brief['adoption']={'physics_dt_s':v['adoption']['clock']['physics_dt_s'],'complete_PPO_passed':True,'provisional45min':True} if v.get('adoption') else None
 print(json.dumps(brief))
 with c.open_sftp() as s:
  for n in ['SELECTED_CLOCK_STATE.json','SELECTED_CLOCK_STARTED.json','CROSSBIN_SDK_PASSED.json','NATIVE20K_PASSED.json','SELECTED_CLOCK_BEHAVIOR_REVIEW.json','SELECTED_CLOCK_PPO_PREFLIGHT_PASSED.json','SELECTED_CLOCK_ADOPTION.json','SELECTED_CLOCK_REVIEW_READY.json','SELECTED_CLOCK_ATTENTION.json','FORMAL_CLOCK_HEALTH_REVIEW.json','SOURCE_FREEZE.json']:
   try:s.stat(root+'/reports/'+n)
   except FileNotFoundError:continue
   s.get(root+'/reports/'+n,str(R/('DT2000_'+n)))
finally:c.close()
