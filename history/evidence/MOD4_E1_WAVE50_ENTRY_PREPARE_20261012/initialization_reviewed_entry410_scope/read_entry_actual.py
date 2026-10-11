"""Read actual own processes, receipts and stage. Never launches or writes canonical."""
from entry_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,hashlib,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')]
import supervise_wave50_entry_scope_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports={}
for p in (D/'reports').glob('*.json'):
 raw=p.read_bytes();reports[p.name]=dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),value=json.loads(raw))
st=reports.get('E1_STATE.json',{}).get('value');actual=[]
if st:
 for loc in (st.get('owner'),st.get('child'),reports.get('E1_GUARDIAN_STARTED.json',{}).get('value')):
  if loc:actual.append(dict(recorded=loc,actual=own.identity(loc['pid'])))
indices=[];logs=[]
for p in list(D.glob('*.json'))+list(D.glob('*.log'))+list(D.glob('*.error')):
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
 if p.suffix in ('.log','.error'):logs.append(dict(path=str(p),tail=p.read_text(errors='replace')[-6000:]))
b=own.s.q.base.budget_state();lockrows=[]
for p in (own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 lockrows.append(dict(path=str(p),actual_fcntl_held=held))
print(json.dumps(dict(epoch=time.time(),root=str(D),reports=reports,actual_processes=actual,current_state=st,output_indices=indices,log_tails=logs,canonical_SHA=h(own.s.q.ctl.CANONICAL),actual_budget=b,two_OS_locks=lockrows,readonly=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  path=save('ENTRY_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(path),phase=(v['current_state'] or {}).get('phase'),attention=v['reports'].get('E1_ATTENTION.json'),actual_processes=v['actual_processes'],passed_stages=[k for k in v['reports'] if k.endswith('PASSED.json')],budget_remaining=v['actual_budget']['remaining_training_seconds'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ACTUAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
