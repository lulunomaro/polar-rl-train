"""Only new unused production root; reuse existing exact static files, no large upload."""
from pathlib import Path
import json,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;B=D/'production_fresh_process_v2_payload';R=D/'reports';OLD='/mnt/mod4_linux_durable_20261013/'+D.name;ROOT=OLD+'/production_fresh_process_v2'
sys.path.insert(0,str(D.parent/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def main():
 c=sf=None
 try:
  c=t.connect();sf=c.open_sftp();sf.get_channel().settimeout(90)
  code=r'''
from pathlib import Path
import json,psutil,shutil,hashlib,time
O=Path(OLD);N=Path(ROOT);assert not N.exists();assert not psutil.pid_exists(477807)
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(C.read_bytes())['active_segment'] is None
N.mkdir();old=json.loads((O/'PAYLOAD_MANIFEST.json').read_bytes())
for row in old['files']:
 p=O/row['relative'];q=N/row['relative'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert hashlib.sha256(q.read_bytes()).hexdigest()==row['SHA']
print(json.dumps(dict(epoch=time.time(),new_unused_root=str(N),original_static_files_copied_without_change=len(old['files']),originals_retained=True)))
'''
  si,so,se=c.exec_command(shlex.quote(t.PY)+' -B -',timeout=90);si.write('OLD='+repr(OLD)+'\nROOT='+repr(ROOT)+'\n'+code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();copied=json.loads(raw);put('FRESH_PRODUCTION_V2_UNUSED_ROOT_STATIC_COPY_ACTUAL.json',copied)
  for n in ('curb35_production_worker_v2.py','curb35_production_owner_v2.py','PRIOR_NATIVE_PRECHECK_AND_CLOSED_COST_ACTUAL.json','PAYLOAD_MANIFEST.json'):sf.put(str(B/n),ROOT+'/'+n)
  code=r'''
from pathlib import Path
import json,hashlib,psutil,subprocess,time
N=Path(ROOT);m=json.loads((N/'PAYLOAD_MANIFEST.json').read_bytes())
for row in m['files']:
 p=N/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
p=subprocess.run([PY,'-B',str(N/'curb35_production_owner_v2.py'),'--execute-new-fresh-CURB35-production-only'],cwd=N,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr;v=json.loads(p.stdout);q=psutil.Process(v['detached_owner_pid']);print(json.dumps(dict(epoch=time.time(),targetfilesSHA=len(m['files']),dispatch=v,actual_owner=dict(pid=q.pid,creation=q.create_time(),argv=q.cmdline(),root=q.cwd()),notyet_production_PPO_pass=True)))
'''
  si,so,se=c.exec_command(shlex.quote(t.PY)+' -B -',timeout=90);si.write('ROOT='+repr(ROOT)+'\nPY='+repr(t.PY)+'\n'+code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw);put('FRESH_PRODUCTION_V2_ACTUAL_OWNER_DISPATCH.json',v);print(json.dumps(v),flush=True)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('FRESH_PRODUCTION_V2_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_readonly_before_any_retry=True));raise
