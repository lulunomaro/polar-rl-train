from pathlib import Path
import json,hashlib,base64,paramiko,time
D=Path(__file__).resolve().parent
KEY=Path('C:/Users/lulu/.ssh/id_ed25519_remote_4090_win_20261013')
PIN=D/'reports/WINDOWS4090_HOST_KEY_ACTUAL.json'
def connect():
 expected=json.loads(PIN.read_bytes())['hostkey_sha256'] if PIN.exists() else None
 class Pinned(paramiko.MissingHostKeyPolicy):
  def missing_host_key(self,client,hostname,key):
   actual=hashlib.sha256(key.asbytes()).hexdigest()
   if expected is not None:assert actual==expected,'Remote host key changed'
   client._host_keys.add(hostname,key.get_name(),key)
 c=paramiko.SSHClient();c.set_missing_host_key_policy(Pinned())
 c.connect('10.24.4.210',port=22,username='Win10',pkey=paramiko.Ed25519Key.from_private_key_file(str(KEY)),timeout=15,banner_timeout=15,auth_timeout=15,look_for_keys=False,allow_agent=False)
 actual=hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()
 if expected is None:
  PIN.write_text(json.dumps(dict(epoch=time.time(),host='10.24.4.210',port=22,username='Win10',hostkey_sha256=actual,user_provided_host_first_connection=True,private_key_not_recorded=True),indent=2),encoding='utf8')
 else:assert actual==expected
 return c
def powershell(c,code,timeout=45):
 enc=base64.b64encode(code.encode('utf-16-le')).decode()
 _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+enc,timeout=timeout)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:raise RuntimeError('Remote PowerShell returned '+str(rc)+': '+err.decode('utf8','replace'))
 return raw.decode('utf-8-sig','replace').strip()
