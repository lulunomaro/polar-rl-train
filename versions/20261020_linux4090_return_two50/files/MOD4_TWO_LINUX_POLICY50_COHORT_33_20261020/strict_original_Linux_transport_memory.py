from pathlib import Path
import json,shlex,sys
import paramiko
W=Path(__file__).resolve().parent.parent
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def connect():
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 secret,_=recover('RM_SSH_PASSWORD');assert secret
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.RejectPolicy());assert c._system_host_keys.lookup('10.24.4.210')
 try:c.connect('10.24.4.210',username='egde',password=secret,look_for_keys=False,allow_agent=False,timeout=15,banner_timeout=15,auth_timeout=15);c.get_transport().set_keepalive(15);key=c.get_transport().get_remote_server_key();assert c._system_host_keys.lookup('10.24.4.210')[key.get_name()].asbytes()==key.asbytes();return c
 finally:secret=None
def code(c,source,payload=None,timeout=90):
 v=dict(payload or {},code=source);i,o,e=c.exec_command(shlex.quote(PY)+' -u -B -c '+shlex.quote("import json,sys;v=json.loads(sys.stdin.readline());exec(v['code'])"),timeout=timeout);i.write(json.dumps(v)+'\n');i.flush();i.channel.shutdown_write();v.clear();raw=o.read().decode();error=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,error,raw);return json.loads(raw)
