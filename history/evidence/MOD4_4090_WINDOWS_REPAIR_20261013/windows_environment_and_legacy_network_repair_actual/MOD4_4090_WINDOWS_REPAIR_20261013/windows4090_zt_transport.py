from pathlib import Path
import json,hashlib,paramiko,time
from windows4090_transport import KEY,powershell
D=Path(__file__).resolve().parent;PIN=D/'reports/WINDOWS4090_ZT_HOST_KEY_ACTUAL.json'
def connect():
 expected=json.loads(PIN.read_bytes())['hostkey_sha256'] if PIN.exists() else None
 class Pinned(paramiko.MissingHostKeyPolicy):
  def missing_host_key(self,client,hostname,key):
   actual=hashlib.sha256(key.asbytes()).hexdigest()
   if expected is not None:assert actual==expected,'Remote host key changed'
   client._host_keys.add(hostname,key.get_name(),key)
 c=paramiko.SSHClient();c.set_missing_host_key_policy(Pinned())
 c.connect('172.27.131.74',port=22,username='Win10',pkey=paramiko.Ed25519Key.from_private_key_file(str(KEY)),timeout=15,banner_timeout=15,auth_timeout=15,look_for_keys=False,allow_agent=False)
 actual=hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()
 if expected is None:PIN.write_text(json.dumps(dict(epoch=time.time(),host='172.27.131.74',port=22,username='Win10',hostkey_sha256=actual,user_provided_alternate_host_first_connection=True,private_key_not_recorded=True),indent=2),encoding='utf8')
 else:assert actual==expected
 return c
