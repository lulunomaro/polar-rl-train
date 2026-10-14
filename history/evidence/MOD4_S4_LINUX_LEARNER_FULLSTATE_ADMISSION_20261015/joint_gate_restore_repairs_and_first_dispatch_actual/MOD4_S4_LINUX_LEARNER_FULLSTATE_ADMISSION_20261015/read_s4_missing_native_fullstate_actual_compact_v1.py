"""One bounded actual read. No polling loop or mutation."""
from pathlib import Path
import sys,json,time,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_LINUX_NATIVE_FULLSTATE_V1_20261015'
CODE='''from pathlib import Path
import json,time,psutil,fcntl,hashlib
r=Path('''+repr(ROOT)+''');out=dict(epoch=time.time(),root=str(r),markers={})
for name in ('ROOT_GPU_FIXED_TWO_DISPATCH_ACTUAL.json','PARENT_IDENTITY_ACTUAL.json','CURRENT_ACTUAL.json','PIPELINE_COMPLETE_ACTUAL.json','PIPELINE_ORIGINAL_ERROR.json','PARENT_EXIT_ACTUAL.json'):
 p=r/name
 if p.exists():out['markers'][name]=json.loads(p.read_bytes())
identity=out['markers'].get('PARENT_IDENTITY_ACTUAL.json',{});out['actual_parent']=None
if identity:
 try:
  p=psutil.Process(identity['pid']);out['actual_parent']=dict(pid=p.pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd(),same_creation=p.create_time()==identity['created'],children=[dict(pid=c.pid,created=c.create_time(),argv=c.cmdline(),cwd=c.cwd()) for c in p.children(recursive=True)])
 except psutil.Error:pass
out['stages']={}
for phase in ('own_native120','own_fullrestore0'):
 a=r/phase/'attempt';v={}
 for name in ('DISPATCH_ACTUAL.json','EXIT_ACTUAL.json','GUARDIAN_CURRENT_ACTUAL.json','S4_PROGRESS_ACTUAL.json','S4_COMPLETE_ACTUAL.json','S4_ORIGINAL_ERROR.json'):
  p=a/name
  if p.exists():v[name]=json.loads(p.read_bytes())
 p=a/'worker_stdout.log'
 if p.exists():
  with p.open('rb') as f:f.seek(max(0,p.stat().st_size-6000));tail=f.read().decode('utf8','replace')
  v['stdout_tail']=tail
 out['stages'][phase]=v
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');out['canonical_SHA']=hashlib.sha256(b.read_bytes()).hexdigest();out['canonical_active']=json.loads(b.read_bytes())['active_segment']
out['locks']=[]
for p in (b.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 out['locks'].append(dict(path=str(p),held=held))
print(json.dumps(out))
'''
def main():
 c=None;stamp=str(time.time_ns())
 try:
  c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(t.PY)+' -',timeout=60);si.write(CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports'/('S4_NATIVE_FULLSTATE_READONLY_TRANSPORT_'+stamp+'.json');p.write_text(json.dumps(dict(rc=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),no_retry=True),indent=2),encoding='utf8');assert rc==0,str(p)
  v=json.loads(raw);p=D/'reports'/('S4_NATIVE_FULLSTATE_CURRENT_ACTUAL_'+stamp+'.json');p.write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(p),actual_parent=v['actual_parent'],markers=list(v['markers']),phase=v['markers'].get('CURRENT_ACTUAL.json'),stages=v['stages'],locks=v['locks'],canonical_active=v['canonical_active'])))
 finally:t.close(c)
if __name__=='__main__':main()
