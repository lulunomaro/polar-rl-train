"""Sole72 HMAC endpoint: target72 loopback, source210 strict-pinned72 SSH.

No credentials in files/argv; caller supplies the approved password in memory.
This source does not install dependencies or initialize any budget authority.
"""
from pathlib import Path
import hashlib,hmac,http.client,json,sys,time,urllib.request
HOST='10.24.0.72'
SSH_PORT=22
HOST_KEY_SHA256='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
DEPS=Path('/mnt/mod4_linux_durable_20261013/mod4_owner72_control_deps_v86_20261026')
ORIGINAL_DEPENDENCIES_RECEIPT_SHA='770a17505e6c25cd70477690d48acd0ae0bb167cc7bad109e48e2ce597b3fd14'
_client=None
_dependencies_checked=False

def close():
 global _client
 if _client is not None:
  _client.close();_client=None

def verify_dependencies(spec):
 global _dependencies_checked
 if _dependencies_checked:return
 B=Path(__file__).resolve().parent;path=B/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'
 raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==spec['owner_control_dependency_binding_SHA']
 binding=json.loads(raw)
 assert binding['schema']=='mod4.owner72.source210.control_dependencies.v1'
 assert binding['actual_target210_CPU_passed'] is True and binding['host72_original_pin_SHA256']==HOST_KEY_SHA256 and binding['DEPS_root']==str(DEPS)
 raw=(DEPS/'INSTALLED_SOURCE_CPU_RECEIPT.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==ORIGINAL_DEPENDENCIES_RECEIPT_SHA
 receipt=json.loads(raw);assert receipt['returncode']==0 and receipt['paramiko_version']=='5.0.0'
 for row in receipt['installed_files']:
  p=DEPS/row['relative'];assert p.resolve().is_relative_to(DEPS.resolve()) and p.is_file() and not p.is_symlink()
  assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 target_raw=(DEPS/'TARGET210_DEPENDENCIES_CPU_ACTUAL.json').read_bytes()
 assert hashlib.sha256(target_raw).hexdigest()==binding['target_CPU_receipt_SHA']
 target=json.loads(target_raw);assert target['passed'] and target['paramiko_version']=='5.0.0' and target['root']==str(DEPS)
 sys.path.insert(0,str(DEPS/'site_packages'))
 import paramiko
 assert paramiko.__version__=='5.0.0' and Path(paramiko.__file__).resolve().is_relative_to(DEPS.resolve())
 _dependencies_checked=True

def _ssh(spec):
 global _client
 assert spec['key']=='h1_210' and spec['execution_backend']=='source210' and isinstance(spec.get('owner_ssh_password'),str) and spec['owner_ssh_password']
 if _client is not None:
  transport=_client.get_transport()
  if transport and transport.is_active() and transport.is_authenticated():return _client
  close()
 verify_dependencies(spec)
 import paramiko
 class Pinned72Only(paramiko.MissingHostKeyPolicy):
  def missing_host_key(self,client,hostname,key):
   if hostname!=HOST or hashlib.sha256(key.asbytes()).hexdigest()!=HOST_KEY_SHA256:
    raise paramiko.SSHException('Original72 host key mismatch before password authentication')
 client=paramiko.SSHClient();client.set_missing_host_key_policy(Pinned72Only())
 try:
  client.connect(HOST,port=SSH_PORT,username='lc01',password=spec['owner_ssh_password'],look_for_keys=False,allow_agent=False,timeout=10,banner_timeout=10,auth_timeout=10)
  transport=client.get_transport()
  assert transport.is_authenticated() and hashlib.sha256(transport.get_remote_server_key().asbytes()).hexdigest()==HOST_KEY_SHA256
  transport.set_keepalive(15)
 except BaseException:
  client.close();raise
 _client=client;return client

class _ResponseOwnedChannelSocket:
 """HTTP borrows the channel; send retains it through full HMAC body read."""
 def __init__(self,channel):self.channel=channel
 def sendall(self,data):return self.channel.sendall(data)
 def makefile(self,*args,**kwargs):return self.channel.makefile(*args,**kwargs)
 def close(self):pass

def send(spec,row,port):
 assert row['key']==spec['key'] and spec['key'] in ('h1','h1_210','e2','restart') and port==29754
 token=spec['token'].encode();raw=json.dumps(dict(epoch=time.time(),run_id=spec['run_id'],row=row)).encode();assert len(raw)<2000000
 headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()}
 if spec['key']=='h1_210':
  assert spec['execution_backend']=='source210'
  channel=_ssh(spec).get_transport().open_channel('direct-tcpip',('127.0.0.1',port),('127.0.0.1',0),timeout=10)
  connection=None
  try:
   channel.settimeout(15)
   connection=http.client.HTTPConnection('127.0.0.1',port,timeout=15);connection.sock=_ResponseOwnedChannelSocket(channel)
   connection.request('POST','/',body=raw,headers=headers)
   response=connection.getresponse();assert response.status==200
   body=response.read();signature=response.getheader('X-Own-Signature')
   assert signature and hmac.compare_digest(signature,hmac.new(token,body,hashlib.sha256).hexdigest())
   return json.loads(body)
  finally:
   try:
    if connection is not None:connection.close()
   finally:channel.close()
 assert spec['execution_backend']=='target72'
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers=headers)
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request,timeout=15) as response:
  body=response.read();signature=response.headers['X-Own-Signature']
 assert signature and hmac.compare_digest(signature,hmac.new(token,body,hashlib.sha256).hexdigest())
 return json.loads(body)
