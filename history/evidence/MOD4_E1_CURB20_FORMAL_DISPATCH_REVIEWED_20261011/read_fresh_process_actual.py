"""Bounded actual own receipts, logs, dynamic state, ledger; never a launcher."""
from stage_fresh_process_resume_once import D,R,E,B,NEW,connect_both,cleanup,linux_json,save
import json,time,traceback
def main():
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import json,time,hashlib,fcntl
D=Path(ROOT);B=Path(BUDGET);R=D/'reports';j=lambda p:json.loads(p.read_bytes());reports={}
for p in R.glob('*.json'):
 if p.name in ('SOURCE_FREEZE.json','CURB132_COMPLETE_ACTUAL_REVIEW.json','CURB_FOUR_CASE_TEMPLATES.json'):continue
 if p.stat().st_size<800000:reports[p.name]=j(p)
def proc(loc):
 if not loc:return None
 p=Path('/proc')/str(loc['pid'])
 if not p.exists():return None
 a=(p/'stat').read_text().split(') ',1)[1].split()
 return dict(pid=loc['pid'],state=a[0],start_ticks=int(a[19]),cwd=str((p/'cwd').resolve()),argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\0') if x])
s=reports.get('E1_STATE.json');owner=reports.get('FRESH_PROCESS_DISPATCH_ACTUAL_RECEIPT.json',{}).get('owner')
loc=[owner,reports.get('E1_GUARDIAN_STARTED.json'),s.get('child') if s else None]
logs={}
for p in D.glob('*.log'):logs[p.name]=dict(bytes=p.stat().st_size,tail=p.read_text(errors='replace')[-3500:])
runs={}
for root in ('discard_logs','learning_logs'):
 for run in (D/root).glob('*'):
  if not run.is_dir():continue
  value={}
  for name in ('latest_complete.json','run_manifest.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SENSOR_RESUME_STARTUP_VERIFIED.json','CLOCK_TRAINING_HEALTH.json','OWN_SAME_CURB_FULL_RESUME_PASSED.json','RETENTION_COMMAND_ACTUAL.json'):
   p=run/name
   if p.is_file():value[name]=j(p)
  runs[str(run)]=value
l=j(B);a=l['active_segment'];remaining=l['authorized_training_seconds']-l['charged_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0)
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 try:
  with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  held=False
 except BlockingIOError:held=True
 locks.append(dict(path=str(p),held=held))
completed=[x for x in l['completed_segments'] if str(D) in x.get('log','')]
print(json.dumps(dict(epoch=time.time(),root=str(D),reports=reports,actual_processes=[dict(locator=v,actual=proc(v)) for v in loc if v],runs=runs,logs=logs,OS_locks=locks,canonical=dict(sha256=hashlib.sha256(B.read_bytes()).hexdigest(),authorized_seconds=l['authorized_training_seconds'],remaining_tail_adjusted_seconds=remaining,active_segment=a,own_completed_segments=completed),read_only=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(B))
  v=linux_json(n,code);p=save('FRESH_PROCESS_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(epoch=v['epoch'],phase=v['reports'].get('E1_STATE.json',{}).get('phase'),processes=v['actual_processes'],attention={k:x for k,x in v['reports'].items() if 'ATTENTION' in k},passed=[k for k in v['reports'] if k.endswith('_PASSED.json')],runs={k:list(x) for k,x in v['runs'].items()},canonical=v['canonical'],report=str(p)),ensure_ascii=True))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ACTUAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_signals_or_mutation=True));raise
