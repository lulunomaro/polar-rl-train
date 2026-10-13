from pathlib import Path
import sys,os,json,time,hashlib,paramiko
from windows4090_transport import KEY,powershell
D=Path(__file__).resolve().parent;W=D.parent;PIN=D/'reports/WINDOWS4090_VIA3060_HOST_KEY_ACTUAL.json'
def connect():
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
 from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
 from eval_remote_io import connect_eval
 gateway=connect_eval();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
 expected=json.loads(PIN.read_bytes())['hostkey_sha256'] if PIN.exists() else None
 class Pinned(paramiko.MissingHostKeyPolicy):
  def missing_host_key(self,client,hostname,key):
   actual=hashlib.sha256(key.asbytes()).hexdigest()
   if expected is not None:assert actual==expected,'Remote host key changed'
   client._host_keys.add(hostname,key.get_name(),key)
 try:
  channel=gateway.get_transport().open_channel('direct-tcpip',('10.24.4.210',22),('127.0.0.1',0),timeout=15)
  c=paramiko.SSHClient();c.set_missing_host_key_policy(Pinned())
  c.connect('10.24.4.210',port=22,username='Win10',sock=channel,pkey=paramiko.Ed25519Key.from_private_key_file(str(KEY)),timeout=15,banner_timeout=15,auth_timeout=15,look_for_keys=False,allow_agent=False)
  actual=hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()
  if expected is None:PIN.write_text(json.dumps(dict(epoch=time.time(),host='10.24.4.210',via='10.24.4.249',port=22,username='Win10',hostkey_sha256=actual,user_authorized_computers_only=True,private_key_not_uploaded_to_gateway=True),indent=2),encoding='utf8')
  else:assert actual==expected
  c._MOD4_gateway_keepalive=gateway
  return c
 except BaseException:gateway.close();raise
