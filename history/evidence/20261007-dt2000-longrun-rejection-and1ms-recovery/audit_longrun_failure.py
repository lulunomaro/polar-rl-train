from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent; R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''
from pathlib import Path
import json,sys,time,re
D=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007');sys.path.insert(0,str(D));import continue_clock2000_practical_review_once as q
q.verify();before=q.ctl.CANONICAL.read_bytes();budget=q.base.budget_state();raw=json.loads(before)
r=q.w.read(D/'reports/SELECTED_CLOCK_REVIEW_READY.json');health=q.w.read(D/'reports/FORMAL_CLOCK_HEALTH_REVIEW.json')
run=Path(r['run']);latest=q.w.read(run/'latest_complete.json');ck=q.base.checkpoint(Path(latest['checkpoint']))
assert ck==r['checkpoint'] and ck['finite_tensors']==68 and latest['pid']==700234
assert health['actual_health']['actual_task_reset_events']==1 and health['actual_health']['max_closure_error_m']>.002 and not health['adoption_retained']
assert budget['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training') and not q.base.trainers()
launch=q.w.read(D/'reports/SELECTED_CLOCK_LAUNCHED.json')['owner'];g=q.w.read(D/'reports/SELECTED_CLOCK_GUARDIAN_STARTED.json')
for x in (launch,g,dict(pid=latest['pid'],start_ticks=47133319)):
 actual=q.helpers.identity(x['pid']);assert actual is None or actual['state']=='Z' or actual['start_ticks']!=x['start_ticks']
freeze=q.w.read(run/'rolling_source_freeze.json');source=q.w.read(D/'reports/SOURCE_FREEZE.json')
assert freeze['sha256']==source['sha256'] and len(source['sha256'])==184
for n,h in source['sha256'].items():assert q.base.sha(D/n)==h
m=q.w.read(run/'run_manifest.json');assert m['init_checkpoint_sha256']==q.SHA and float(m['env']['RM_PHYSICS_DT_S'])==.002
logs=(q.P/'auto_0405_moe_S1A_A0_selected_clock_learning_cap12.5664_white_v3.log').read_text(errors='replace')
updates=len(re.findall(r'Iteration time:\s*([0-9.]+)s',logs));assert health['actual_health']['control_steps']==updates*24
matches=[]
def scan(obj,path=''):
 if isinstance(obj,dict):
  if obj.get('pid')==700234 and path!='active_segment':matches.append(dict(path=path,value=obj))
  for k,v in obj.items():scan(v,path+'.'+str(k))
 elif isinstance(obj,list):
  for i,v in enumerate(obj):scan(v,path+'['+str(i)+']')
scan(raw)
assert len(matches)==1,('Expected one completed segment for own PID',matches)
segment=matches[0]['value']
assert segment['ended_epoch']==segment['accounted_through_epoch']
assert abs((segment['ended_epoch']-segment['started_epoch'])-r['actual_learning_seconds'])<1e-6
assert q.ctl.CANONICAL.read_bytes()==before
v=dict(epoch=time.time(),phase=q.w.read(D/'reports/SELECTED_CLOCK_STATE.json')['phase'],full_save=ck,PID_bound_receipt=latest,
 run_manifest_sha256=q.base.sha(run/'run_manifest.json'),run_source_freeze_sha256=q.base.sha(run/'rolling_source_freeze.json'),source_count=184,
 formal_health=health,actual_PPO_updates=updates,actual_control_steps=health['actual_health']['control_steps'],new_environment_policy_steps=updates*24*20000,
 unique_completed_segment=matches[0],budget_authorized=budget['authorized_training_seconds'],remaining=budget['remaining_training_seconds'],
 active_segment=None,actual_old_authorities_exited=True,canonical_sha256=q.base.sha(q.ctl.CANONICAL),canonical_bytes_exact_during_audit=True,
 inference='A true closure termination occurred during long stochastic2ms PPO. Short checks were valid but did not establish long-run stability; timestep-only causation is not isolated.',
 next='New isolated1ms validation under approved v1.5 fallback; old1ms entry remains retired; no reuse of failed23875 or preflight weights as source.')
print(json.dumps(v))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  (R/'AUDIT_READER_ERROR.txt').write_bytes(err);raise RuntimeError(err.decode())
 v=json.loads(raw);(R/'DT2000_LONGRUN_FAILURE_AUDIT.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(v))
finally:c.close()
