"""Original HMAC control protocol over local loopback or one original-pinned SSH transport."""
from pathlib import Path
import base64,hashlib,hmac,http.client,json,sys,time,urllib.request
HOST='10.24.5.27'
SSH_PORT=4090
HOST_KEY_BASE64='__PINNED_ORIGINAL210_ED25519_BASE64__'
DEPS=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_forwarded_owner_control_deps_20261025')
DEPS_RECEIPT_SHA='770a17505e6c25cd70477690d48acd0ae0bb167cc7bad109e48e2ce597b3fd14'
_client=None
_dependencies_checked=False

def close():
 global _client
 if _client is not None:
  _client.close();_client=None

def verify_dependencies():
 global _dependencies_checked
 if _dependencies_checked:return
 raw=(DEPS/'INSTALLED_SOURCE_CPU_RECEIPT.json').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==DEPS_RECEIPT_SHA
 receipt=json.loads(raw);assert receipt['returncode']==0 and receipt['paramiko_version']=='5.0.0'
 for row in receipt['installed_files']:
  p=DEPS/row['relative'];assert p.resolve().is_relative_to(DEPS.resolve()) and p.is_file() and not p.is_symlink()
  assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 sys.path.insert(0,str(DEPS/'site_packages'))
 import paramiko
 assert paramiko.__version__=='5.0.0' and Path(paramiko.__file__).resolve().is_relative_to(DEPS.resolve())
 _dependencies_checked=True

def _ssh(spec):
 global _client
 if _client is not None:
  t=_client.get_transport()
  if t and t.is_active() and t.is_authenticated():return _client
  close()
 verify_dependencies()
 import paramiko
 assert spec['key']=='recovery' and isinstance(spec.get('owner_ssh_password'),str) and spec['owner_ssh_password']
 key=paramiko.Ed25519Key(data=base64.b64decode(HOST_KEY_BASE64))
 client=paramiko.SSHClient();client.set_missing_host_key_policy(paramiko.RejectPolicy())
 client.get_host_keys().add('['+HOST+']:'+str(SSH_PORT),'ssh-ed25519',key)
 try:
  client.connect(HOST,port=SSH_PORT,username='egde',password=spec['owner_ssh_password'],look_for_keys=False,allow_agent=False,timeout=10,banner_timeout=10,auth_timeout=10)
  t=client.get_transport();assert t.is_authenticated() and t.get_remote_server_key().asbytes()==key.asbytes();t.set_keepalive(15)
 except BaseException:
  client.close();raise
 _client=client;return client

def send(spec,row,port):
 assert row['key']==spec['key'] and port==29754
 token=spec['token'].encode();raw=json.dumps(dict(epoch=time.time(),run_id=spec['run_id'],row=row)).encode()
 assert len(raw)<2000000
 headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()}
 if spec['key']=='h1':
  req=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers=headers)
  with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=15) as response:
   body=response.read();signature=response.headers['X-Own-Signature']
 else:
  assert spec['key']=='recovery'
  channel=connection=None
  try:
   channel=_ssh(spec).get_transport().open_channel('direct-tcpip',('127.0.0.1',port),('127.0.0.1',0),timeout=12)
   channel.settimeout(15);connection=http.client.HTTPConnection('127.0.0.1',port,timeout=15);connection.sock=channel
   connection.request('POST','/',body=raw,headers=headers)
   response=connection.getresponse();body=response.read();signature=response.getheader('X-Own-Signature');assert response.status==200
  except BaseException:
   close();raise
  finally:
   if connection is not None:connection.close()
   elif channel is not None:channel.close()
 assert signature and hmac.compare_digest(signature,hmac.new(token,body,hashlib.sha256).hexdigest())
 return json.loads(body)
