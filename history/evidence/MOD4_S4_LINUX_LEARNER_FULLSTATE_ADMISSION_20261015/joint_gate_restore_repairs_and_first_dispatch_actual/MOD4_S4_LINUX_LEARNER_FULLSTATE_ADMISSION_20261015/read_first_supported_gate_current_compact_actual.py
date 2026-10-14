"""One bounded read of the actual first gate learner; no launch or polling loop."""
from pathlib import Path
import sys,json,time,shlex
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_FIRST_SUPPORTED_GATE45M_V1_20261015'
def main():
 c=None;stamp=str(time.time_ns())
 try:
  c=t.connect();code='''from pathlib import Path
import json,time,psutil,fcntl,hashlib
r=Path('''+repr(ROOT)+''');out=dict(epoch=time.time(),root=str(r),markers={})
for name in ('PARENT_IDENTITY_ACTUAL.json','CURRENT_ACTUAL.json','GUARDIAN_CURRENT_ACTUAL.json','DISPATCH_ACTUAL.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_ACTUAL.json','GUARDIAN_EXIT_ACTUAL.json','CHILD_EXIT_AND_UNIQUE_COST_ACTUAL.json','FORMAL_COMPLETE_REVIEW_READY_ACTUAL.json'):
 p=r/name
 if p.exists():out['markers'][name]=json.loads(p.read_bytes())
owner=out['markers'].get('PARENT_IDENTITY_ACTUAL.json');out['actual_parent']=None
if owner:
 try:
  p=psutil.Process(owner['pid']);out['actual_parent']=dict(pid=p.pid,created=p.create_time(),same_creation=p.create_time()==owner['created'],argv=p.cmdline(),cwd=p.cwd(),children=[dict(pid=q.pid,created=q.create_time(),argv=q.cmdline(),cwd=q.cwd()) for q in p.children(recursive=True)])
 except psutil.Error:pass
out['own']={};a=r/'learning_logs'
for name in ('S4_LEARNING_STARTUP_ADMITTED_ACTUAL.json','latest_complete.json','CLOCK_TRAINING_HEALTH.json','S4_FORMAL_ORIGINAL_ERROR.json','S4_FORMAL_FINAL_ACTUAL.json'):
 p=a/name
 if p.exists():out['own'][name]=json.loads(p.read_bytes())
latest=out['own'].get('latest_complete.json')
if latest:
 p=Path(latest['checkpoint']);out['latest_actual_file']=dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
p=r/'worker_stdout.log'
if p.exists():
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-6000));out['stdout_tail']=f.read().decode('utf8','replace')
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');ledger=json.loads(b.read_bytes());out['canonical']=dict(sha256=hashlib.sha256(b.read_bytes()).hexdigest(),active=ledger['active_segment'],charged=ledger['charged_training_seconds'],remaining=ledger['remaining_training_seconds'])
out['locks']=[]
for p in (b.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 out['locks'].append(dict(path=str(p),held=held))
print(json.dumps(out))
'''
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_FIRST_GATE_READONLY_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace')),indent=2));assert rc==0,str(p)
  v=json.loads(raw);p=D/'reports'/('S4_FIRST_GATE_CURRENT_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(v,indent=2))
  print(json.dumps(dict(report=str(p),actual_parent=v['actual_parent'],markers=list(v['markers']),own=v['own'],latest=v.get('latest_actual_file'),locks=v['locks'],canonical=v['canonical'])))
 finally:t.close(c)
if __name__=='__main__':main()
