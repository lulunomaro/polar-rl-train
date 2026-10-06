"""Read the new authority and own evidence; no signals or ledger writes."""
from pathlib import Path
import json,shlex,sys
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007');sys.path.insert(0,str(D));import continue_clock1000_worker_manifest_review_once as q
q.verify();read=lambda p:q.w.read(p) if p.exists() else None
s=read(q.R/'SELECTED_CLOCK_STATE.json') or {};b=q.base.budget_state();a=b['active_segment'];launch=read(q.R/'SELECTED_CLOCK_LAUNCHED.json');guard=read(q.R/'SELECTED_CLOCK_GUARDIAN_STARTED.json')
own=q.helpers.identity(launch['owner']['pid']);g=q.helpers.identity(guard['pid']) if guard else None
ci=a or s.get('child');child=q.helpers.identity(ci['pid']) if ci else None
if child and ci.get('start_ticks') and child['start_ticks']!=ci['start_ticks']:child=None
reports={}
for n in ('ALIGNED_SDK_PASSED.json','NATIVE20K_PASSED.json','SELECTED_CLOCK_BEHAVIOR_REVIEW.json','SELECTED_CLOCK_PPO_PREFLIGHT_PASSED.json','SELECTED_CLOCK_ADOPTION.json','SELECTED_CLOCK_REVIEW_READY.json','FORMAL_CLOCK_HEALTH_REVIEW.json','SELECTED_CLOCK_ATTENTION.json','CLOCK1000_LONGRUN_HEALTHY.json'):
 reports[n]=read(q.R/n)
latest=None;checkpoint=None;manifest=None;health=None
if a:
 for root in (q.P/'logs',q.P/'autonomy_preflight_logs'):
  try:run=q.w.rate.trainer_run(root,a['pid'])
  except (AssertionError,FileNotFoundError):continue
  latest=read(run/'latest_complete.json');manifest=read(run/'run_manifest.json');health=read(run/'CLOCK_TRAINING_HEALTH.json')
  if latest:checkpoint=q.base.checkpoint(Path(latest['checkpoint']))
  break
log=Path(a['log']) if a else (q.D/('aligned_sdk.log' if s.get('phase')=='frozen_aligned_sdk' else 'native20k.log' if s.get('phase')=='frozen_native20k' else 'supervisor.log'))
v=dict(epoch=time.time(),phase=s.get('phase'),owner=own,guardian=g,child=child,active_segment=a,active_training=q.w.read(q.ctl.STATE_PATH).get('active_training'),
 remaining=b['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0),reports=reports,
 own_latest=latest,own_checkpoint=checkpoint,own_manifest=manifest,own_health=health,log_tail=log.read_text(errors='replace')[-2000:] if log.exists() else None)
print(json.dumps(v))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'CLOCK1000_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps({k:v[k] for k in ('epoch','phase','owner','guardian','child','active_segment','remaining','own_checkpoint','own_health','log_tail')}))
 print(json.dumps({'report_status':{k:bool(x) for k,x in v['reports'].items()}}))
finally:c.close()
