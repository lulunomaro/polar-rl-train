from pathlib import Path
import argparse,getpass,hashlib,json,shlex,sys,time,traceback,paramiko
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,os,sys,time,psutil,subprocess
B=Path(sys.argv[1]);rows=[]
for p in sorted(B.glob('*.json'))+sorted(B.glob('rank*/*.json')):
 if p.stat().st_size<3000000:
  try:rows.append(dict(path=str(p),data=json.loads(p.read_bytes())))
  except Exception:pass
logs=[]
for p in sorted(B.glob('*.log'))+sorted(B.glob('rank*/*.log')):
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-65536));b=f.read()
 logs.append(dict(path=str(p),bytes=p.stat().st_size,tail=b.decode(errors='replace')))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if str(B) in ' '.join(p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
v=dict(epoch=time.time(),root=str(B),files=rows,logs=logs,actual_own_processes=procs)
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
if C.exists():
 c=json.loads(C.read_bytes());v['canonical']={k:c[k] for k in ('active_segment','charged_training_seconds','remaining_training_seconds')}
print(json.dumps(v))
'''
def main():
 a=argparse.ArgumentParser();a.add_argument('--label',required=True);args=a.parse_args();assert args.label.replace('_','').isalnum();p=R/('THREE_RANK_STATE_'+args.label+'_ACTUAL.json');assert not p.exists();rows=[];c=None
 try:
  c=t.connect();root='/mnt/mod4_linux_durable_20261013/'+D.name;si,so,se=c.exec_command(shlex.quote(t.PY)+' -B - '+shlex.quote(root),timeout=30);si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode();rows.append(json.loads(out))
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  root='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;si,so,se=c.exec_command("'/home/lc01/Zonglin Li/zonglin2/run-python.sh' -B - "+shlex.quote(root),timeout=30);si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode();rows.append(json.loads(out))
 finally:pw=None;c.close()
 p.write_text(json.dumps(dict(epoch=time.time(),nodes=rows),indent=2),encoding='utf8')
 print(json.dumps([dict(root=x['root'],processes=len(x['actual_own_processes']),files=[dict(name=Path(y['path']).name,data=y['data']) for y in x['files'] if Path(y['path']).name in ('CURRENT_THREE_RANK_ACTUAL.json','NODE72_CURRENT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','THREE_GPU_NCCL_ACTUAL_PASSED.json','SINGLE_PPO_7H_LEARNING_ADMITTED.json','ORIGINAL_WORKER_ERROR.json','latest_complete.json')],logtails=[dict(path=q['path'],tail=q['tail'][-2000:]) for q in x['logs']]) for x in rows]),flush=True)
if __name__=='__main__':main()
