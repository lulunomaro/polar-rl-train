"""SOURCE ONLY until root schedules it. One secret stdin, sequential control SSH."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,ipaddress,json,os,secrets,shlex,socket,sys,time,traceback,uuid
import paramiko
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID,ExtendedKeyUsageOID
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
SRC='/home/lc01/Zonglin Li/zonglin2';EXPORT=SRC+'/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1';SERVICE=EXPORT+'/direct_https_probe_v1'
PIN72='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';PIN86='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
PRODUCER='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
PY72=[SRC+'/compat/glibc240/ld-linux-x86-64.so.2','--library-path',SRC+'/compat/glibc240:'+SRC+'/envs/mod4/lib',SRC+'/envs/mod4/bin/python','-S','-B','-u']
PROBE=r'''
from pathlib import Path
import hashlib,hmac,http.client,json,secrets,signal,ssl,time,traceback
R=Path('/data/robemo/polar-rl-train');D=R/'runtime_migrations/proven72_20261028_v1/direct_https_probe_v1';assert R.resolve()==R and not R.is_symlink();marker=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert marker['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700'
assert D.resolve()==D and D.is_relative_to(R) and not D.exists();D.mkdir(parents=True,mode=0o700)
with (D/'OWN_DIRECT_PROBE_MARKER.json').open('x') as f:json.dump(dict(root=str(D),service_id=v['endpoint']['service_id'],producer_SHA=v['producer_SHA'],no_GPU_model_or_global_change=True),f)
endpoint=v['endpoint'];assert endpoint['advertised_host']=='10.24.0.72' and endpoint['actual_OS_selected_port']!=29754 and endpoint['producer_SHA']==v['producer_SHA']
context=ssl.create_default_context(cadata=endpoint['public_certificate_pem']);context.check_hostname=True;context.verify_mode=ssl.CERT_REQUIRED
key=bytes.fromhex(v.pop('hmac_key_hex'));conn=None;start=time.monotonic();result=None
def ten_second_deadline(signum,frame):raise TimeoutError('original ten second direct-route probe bound')
signal.signal(signal.SIGALRM,ten_second_deadline);signal.setitimer(signal.ITIMER_REAL,10)
try:
 conn=http.client.HTTPSConnection(endpoint['advertised_host'],endpoint['actual_OS_selected_port'],timeout=10,context=context);conn.connect();actual_cert=hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest();assert actual_cert==endpoint['certificate_SHA'],'TLS_PIN_MISMATCH_BEFORE_HMAC'
 nonce=secrets.token_hex(16);expires=str(int(time.time()+60));message='GET\n/probe\n\n'+expires+'\n'+nonce+'\n'+v['producer_SHA'];signature=hmac.new(key,message.encode(),hashlib.sha256).hexdigest()
 remaining=10-(time.monotonic()-start);assert remaining>0;conn.sock.settimeout(remaining);conn.request('GET','/probe',headers={'X-Mod4-Nonce':nonce,'X-Mod4-Expires':expires,'X-Mod4-HMAC':signature});response=conn.getresponse();raw=response.read(65537);assert len(raw)<=65536 and response.status==200
 body=json.loads(raw);assert body['passed_probe_only'] and body['producer_SHA']==v['producer_SHA'] and body['certificate_SHA']==actual_cert and body['service_id']==endpoint['service_id']
 result=dict(passed_direct_route_TLS_HMAC_probe=True,epoch=time.time(),elapsed_seconds=time.monotonic()-start,known_source_address=endpoint['advertised_host'],actual_port=endpoint['actual_OS_selected_port'],certificate_SHA=actual_cert,producer_SHA=v['producer_SHA'],source_response=body,no_archive_data_or_model_or_GPU_or_secondSSH=True)
except BaseException:result=dict(passed_direct_route_TLS_HMAC_probe=False,epoch=time.time(),elapsed_seconds=time.monotonic()-start,error=traceback.format_exc(),known_source_address=endpoint['advertised_host'],actual_port=endpoint['actual_OS_selected_port'],no_retry_other_IP_port_firewall_or_system_change=True)
finally:
 signal.setitimer(signal.ITIMER_REAL,0)
 key=None
 if conn:conn.close()
with (D/'ACTUAL_DIRECT_TLS_HMAC_PROBE_OR_ORIGINAL_ERROR.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
'''
def put(n,v):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 R.mkdir(parents=True,exist_ok=True);put('DIRECT_PROBE_ENTRY_ENTERED_BEFORE_STDIN_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),source_only_until_scheduled=True,maximum_control_seconds_after_stdin=180,probe_seconds=10,probe_only_no_bulk_transfer=True,credentials_and_private_key_RAM_STDIN_memfd_only=True));print('READY_FOR_SINGLE_STDIN_JSON',flush=True)
 req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo';password86=req.pop('password');hkey=secrets.token_bytes(32);service_id=uuid.uuid4().hex;certificate=None;private=None;client=None;sf=None;endpoint=None;probe=None;deadline=time.monotonic()+180
 key=rsa.generate_private_key(public_exponent=65537,key_size=2048);name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'MOD4 owned bundle probe')]);now=datetime.datetime.now(datetime.timezone.utc);publickey=key.public_key()
 certificate=x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(publickey).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(seconds=60)).not_valid_after(now+datetime.timedelta(minutes=35)).add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address('10.24.0.72'))]),critical=False).add_extension(x509.BasicConstraints(ca=True,path_length=0),critical=True).add_extension(x509.SubjectKeyIdentifier.from_public_key(publickey),critical=False).add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(publickey),critical=False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),critical=False).add_extension(x509.KeyUsage(True,False,True,False,False,True,True,False,False),critical=True).sign(key,hashes.SHA256()).public_bytes(serialization.Encoding.PEM).decode()
 private=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()).decode();key=None
 wrapper=module('same_compressed_for_owned_direct_probe',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 def connect(host,user,secret,pin):
  sock=socket.create_connection((host,22),timeout=10);c=paramiko.Transport(sock)
  try:
   c.banner_timeout=10;c.auth_timeout=10;c.start_client(timeout=10);assert hashlib.sha256(c.get_remote_server_key().asbytes()).hexdigest()==pin,'SSH_PIN_MISMATCH_BEFORE_AUTH';c.auth_password(user,secret,fallback=False);return c
  except BaseException:c.close();raise
 def source_connect():
  m=module('same72_secret_memory_for_direct_probe',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=m.recover()
  try:return connect('10.24.0.72','lc01',secret,PIN72)
  finally:secret=None
 def run(c,python,code,args):
  remaining=deadline-time.monotonic();assert remaining>0;ch=c.open_session(timeout=min(10,remaining));cmd=' '.join(shlex.quote(x) for x in python+['-c',"import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"]);ch.exec_command(cmd);ch.settimeout(min(30,max(1,deadline-time.monotonic())));inp=ch.makefile_stdin('wb');inp.write((json.dumps(dict(args,code=code))+'\n').encode());inp.flush();ch.shutdown_write();out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(err,out);return json.loads(out)
 try:
  helper=B/'owned_bundle_only_TLS_memfd_service_v1.py';raw=helper.read_bytes();frozen=json.loads((B/'FROZEN_DIRECT_TLS_PROBE_SOURCE_INDEX_V1.json').read_bytes());assert hashlib.sha256(raw).hexdigest()==frozen['service_SHA']
  client=source_connect();guard="from pathlib import Path\nimport json\nB=Path(v['root']);E=Path(v['export']);assert B.resolve().is_relative_to(E) and not B.exists();assert json.loads((E/'PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json').read_bytes())['producer_SHA']==v['producer_SHA']\nB.mkdir(mode=0o700)\nwith (B/'OWN_BUNDLE_TLS_SERVICE_MARKER.json').open('x') as f:json.dump(dict(root=str(B),service_id=v['service_id'],probe_only=True),f)\nprint(json.dumps(dict(passed=True,new_service_root=str(B))))"
  put('SOURCE_OWN_TLS_NAMESPACE_ACTUAL.json',run(client,PY72,guard,dict(root=SERVICE,export=EXPORT,producer_SHA=PRODUCER,service_id=service_id)));sf=paramiko.SFTPClient.from_transport(client)
  with sf.open(SERVICE+'/'+helper.name,'wx') as f:f.write(raw)
  sf.close();sf=None
  launch="from pathlib import Path\nimport json,os,subprocess,time,hashlib\nB=Path(v['root']);P=B/v['filename'];assert hashlib.sha256(P.read_bytes()).hexdigest()==v['source_SHA'];env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1');env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None);env.pop('LD_LIBRARY_PATH',None)\nfor k,n in {'HOME':'home','TMPDIR':'tmp','XDG_CACHE_HOME':'cache'}.items():\n p=B/n;p.mkdir();env[k]=str(p)\nwith (B/'TLS_SERVICE_FULL.log').open('xb') as f:p=subprocess.Popen(v['python']+[str(P)],cwd=B,env=env,stdin=subprocess.PIPE,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)\np.stdin.write((json.dumps(v['memory_config'])+'\\n').encode());p.stdin.flush();p.stdin.close()\nfor _ in range(100):\n if (B/'TLS_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json').exists():break\n assert p.poll() is None,'owned probe TLS service startup failed';time.sleep(.05)\nassert (B/'TLS_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json').exists();print((B/'TLS_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json').read_text())"
  memory=dict(service_id=service_id,maximum_seconds=1800,probe_only=True,hmac_key_hex=hkey.hex(),public_certificate_pem=certificate,private_key_pem=private)
  endpoint=run(client,PY72,launch,dict(root=SERVICE,filename=helper.name,source_SHA=hashlib.sha256(raw).hexdigest(),python=PY72,memory_config=memory));memory.clear();private=None;put('SOURCE_PUBLIC_TLS_ENDPOINT_RETURNED_ACTUAL.json',endpoint);client.close();client=None
  client=connect('10.50.0.86','robemo',password86,PIN86);password86=None;probe=run(client,['/usr/bin/python3','-B'],PROBE,dict(endpoint=endpoint,producer_SHA=PRODUCER,hmac_key_hex=hkey.hex()));put('TARGET86_DIRECT_TEN_SECOND_PROBE_RETURNED_ACTUAL.json',probe);client.close();client=None
  client=source_connect();stop="from pathlib import Path\nimport json,time\nB=Path(v['root']);m=json.loads((B/'OWN_BUNDLE_TLS_SERVICE_MARKER.json').read_bytes());assert m['service_id']==v['service_id']\np=B/'TLS_SERVICE_TERMINAL_ACTUAL.json'\nif not p.exists():\n with (B/'OWN_STOP_REQUEST.json').open('x') as f:json.dump(dict(service_id=v['service_id']),f)\nfor _ in range(100):\n if p.exists():break\n time.sleep(.05)\nprint(json.dumps(dict(terminal=json.loads(p.read_bytes()) if p.exists() else None,own_stop_requested_only=True)))"
  ending=run(client,PY72,stop,dict(root=SERVICE,service_id=service_id));put('SOURCE_PROBE_ONLY_SERVICE_ENDING_ACTUAL.json',ending);client.close();client=None
  put('DIRECT_TLS_HMAC_ROUTE_PROBE_COMPLETE_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=probe['passed_direct_route_TLS_HMAC_probe'],probe=probe,endpoint=endpoint,service_ending=ending,source_and_target_SSH_sequential_closed=True,no_bulk_copy_or_GPU_model_or_canonical_operation=True,no_credentials_or_private_key_on_disk=True));print(json.dumps(dict(passed_network_probe_only=probe['passed_direct_route_TLS_HMAC_probe'],no_bulk_transfer_yet=True,source_service_ending_observed=ending['terminal'] is not None)))
 finally:
  password86=None;private=None;hkey=None;certificate=None
  if sf:sf.close()
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('DIRECT_ROUTE_PROBE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_other_host_port=True));raise
