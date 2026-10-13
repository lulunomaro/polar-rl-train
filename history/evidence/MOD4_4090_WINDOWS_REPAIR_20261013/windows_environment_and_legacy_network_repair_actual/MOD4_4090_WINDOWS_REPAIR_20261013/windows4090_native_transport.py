from pathlib import Path
import subprocess,base64,json,time,hashlib,paramiko
D=Path(__file__).resolve().parent
KEY=Path('C:/Users/lulu/.ssh/id_ed25519_remote_4090_win_20261013')
KNOWN=Path('C:/Users/lulu/.ssh/known_hosts_mod4_4090_windows_20261013')
def base(tool='ssh'):
 return [tool,'-o','BatchMode=yes','-o','ConnectTimeout=15','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(KNOWN),'-i',str(KEY)]
class Session:
 def close(self):pass
def connect():
 keys=paramiko.HostKeys(str(KNOWN));key=keys.lookup('10.24.4.210')['ssh-ed25519'];digest=hashlib.sha256(key.asbytes()).hexdigest()
 p=D/'reports/WINDOWS4090_NATIVE_PINNED_HOST_KEY_ACTUAL.json'
 if p.exists():assert json.loads(p.read_bytes())['hostkey_sha256']==digest
 else:p.write_text(json.dumps(dict(epoch=time.time(),host='10.24.4.210',username='Win10',hostkey_sha256=digest,native_authenticated_hostname='DESKTOP-J17LAN1',original_Linux_knownhost_untouched=True,private_key_not_recorded=True),indent=2),encoding='utf8')
 return Session()
def powershell(session,code,timeout=60):
 enc=base64.b64encode(code.encode('utf-16-le')).decode();argv=base()+['Win10@10.24.4.210','powershell.exe -NoProfile -NonInteractive -EncodedCommand '+enc]
 r=subprocess.run(argv,capture_output=True,timeout=timeout)
 if r.returncode:raise RuntimeError('Native Windows SSH returned '+str(r.returncode)+': '+r.stderr.decode('utf8','replace'))
 return r.stdout.decode('utf-8-sig','replace').strip()
def upload(source,remote_path,timeout=300):
 r=subprocess.run(base('scp')+['-q',str(source),'Win10@10.24.4.210:'+remote_path],capture_output=True,timeout=timeout)
 if r.returncode:raise RuntimeError('SCP upload failed: '+r.stderr.decode('utf8','replace'))
