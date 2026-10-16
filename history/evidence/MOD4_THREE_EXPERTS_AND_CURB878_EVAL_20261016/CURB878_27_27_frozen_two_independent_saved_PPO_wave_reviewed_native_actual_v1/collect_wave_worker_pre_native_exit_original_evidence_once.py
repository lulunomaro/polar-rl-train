"""One bounded own job2 post-exit evidence collection; no restart or mutation."""
from pathlib import Path
import getpass,hashlib,json,paramiko,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/train'
CODE=r'''
from pathlib import Path
import json,sys,time,psutil,hashlib
B=Path(sys.argv[1]);root=B/'job2';rows=[]
for p in sorted(root.rglob('*')):
 if p.is_file() and p.suffix in ('.json','.txt','.log') and 'src_snapshot' not in p.parts and p.stat().st_size<3000000:
  rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),text=p.read_text(errors='replace')))
print(json.dumps(dict(epoch=time.time(),root=str(root),files=rows,worker_identity=next((p.info for p in psutil.process_iter(['pid','create_time','cmdline']) if p.pid==3097639),None))))
'''
def main():
 out=D/'actual_wave_native_exit_original';assert not out.exists();pw=getpass.getpass('Host72 SSH password (hidden, never saved): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  si,so,se=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B - '+shlex.quote(ROOT),timeout=45);si.write(CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 finally:pw=None;c.close()
 out.mkdir();vpath=R/'WAVE_JOB2_EXIT0_WITHOUT_NATIVE_OR_PPO_ORIGINAL_EVIDENCE_ACTUAL.json';vpath.write_text(json.dumps(v,indent=2),encoding='utf8')
 for f in v['files']:
  p=out/Path(f['path']).relative_to(ROOT+'/job2');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(f['text'],encoding='utf8')
 print(json.dumps(dict(report=str(vpath),actual_worker=v['worker_identity'],files=[dict(path=x['path'],bytes=x['bytes']) for x in v['files']],log_tail=next((x['text'][-15000:] for x in v['files'] if x['path'].endswith('/worker.log')),None))),flush=True)
if __name__=='__main__':main()
