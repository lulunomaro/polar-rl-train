"""One memory-only stdin, source SSH closes before target foreground HTTPS pull."""
from pathlib import Path
import datetime,hashlib,importlib.util,ipaddress,json,os,secrets,shlex,socket,sys,threading,time,traceback,uuid
import paramiko
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID,ExtendedKeyUsageOID
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
SRC='/home/lc01/Zonglin Li/zonglin2';EXPORT=SRC+'/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1';SERVICE=EXPORT+'/direct_https_data_v1'
BASE='/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1';ATTEMPT=BASE+'/direct_pull_attempt_v1'
PIN72='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';PIN86='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
PRODUCER='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
PROBE=L/'NEW_HOST_DIRECT_HTTPS_BUNDLE_PROBE_SOURCE_V1/reports/DIRECT_TLS_HMAC_ROUTE_PROBE_COMPLETE_RETURNED_ACTUAL.json';PROBE_SHA='33c7566c392a9bb36c8cda476b1682457e23c7a3990bc824c0237c52c26ae670'
SOURCE_REPORT=L/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_READONLY_COLLECTION_SOURCE_V1/reports/PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION_FOOTPRINT_ABI_ACTUAL.json'
PY72=[SRC+'/compat/glibc240/ld-linux-x86-64.so.2','--library-path',SRC+'/compat/glibc240:'+SRC+'/envs/mod4/lib',SRC+'/envs/mod4/bin/python','-S','-B','-u']
SOURCE_PRE=r'''
from pathlib import Path
import json
B=Path(v['root']);E=Path(v['export']);assert B.resolve()==B and B.is_relative_to(E) and not B.exists()
assert json.loads((E/'PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json').read_bytes())==v['producer'] and json.loads((E/'EXPORT_SUPERVISOR_TERMINAL_ACTUAL.json').read_bytes())['passed']
B.mkdir(mode=0o700)
with (B/'OWN_BUNDLE_TLS_DATA_SERVICE_MARKER.json').open('x') as f:json.dump(dict(root=str(B),service_id=v['service_id'],producer_SHA=v['producer']['producer_SHA'],data_enable=True),f)
print(json.dumps(dict(passed=True,root=str(B),source_env_unchanged=True)))
'''
SOURCE_START=r'''
from pathlib import Path
import hashlib,json,os,subprocess,time
B=Path(v['root']);P=B/v['filename'];assert hashlib.sha256(P.read_bytes()).hexdigest()==v['source_SHA'];env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
for k in ['PYTHONPATH','PYTHONHOME','LD_LIBRARY_PATH','LD_PRELOAD']:env.pop(k,None)
for k,n in {'HOME':'home','TMPDIR':'tmp','XDG_CACHE_HOME':'cache'}.items():
 p=B/n;p.mkdir(mode=0o700);env[k]=str(p)
with (B/'TLS_DATA_SERVICE_FULL.log').open('xb') as f:p=subprocess.Popen(v['python']+[str(P)],cwd=B,env=env,stdin=subprocess.PIPE,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
p.stdin.write((json.dumps(v['memory_config'])+chr(10)).encode());p.stdin.flush();p.stdin.close()
for _ in range(100):
 if (B/'TLS_DATA_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json').exists():break
 assert p.poll() is None,'owned data service startup failed';time.sleep(.05)
assert (B/'TLS_DATA_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json').exists();print((B/'TLS_DATA_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json').read_text())
'''
TARGET_PRE=r'''
from pathlib import Path
import json,shutil
R=Path('/data/robemo/polar-rl-train');BASE=R/'runtime_migrations/proven72_20261028_v1';B=Path(v['root']);assert R.resolve()==R and BASE.resolve()==BASE and B.resolve()==B and B.is_relative_to(BASE) and not B.exists()
m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['authorized_root']==str(R) and m['host']=='10.50.0.86' and m['username']=='robemo'
assert json.loads((BASE/'OWN_PROVEN72_RUNTIME_RECEIVER.json').read_bytes())['producer_SHA']==v['producer_SHA']
free=shutil.disk_usage(R).free;required=v['compressed_bytes']+v['logical_input_bytes']+1024**3;assert free>required
B.mkdir(mode=0o700)
with (B/'OWN_DIRECT_PULL_ATTEMPT_MARKER.json').open('x') as f:json.dump(dict(root=str(B),run_id=v['run_id'],producer_SHA=v['producer_SHA'],old_artifacts_unchanged=True),f)
for n in ['home','tmp','cache','config','data','state']:(B/n).mkdir(mode=0o700)
print(json.dumps(dict(passed=True,root=str(B),actual_free_bytes=free,required_capacity_bytes=required,old_partial_files_untouched=True)))
'''
TARGET_VERIFY=r'''
from pathlib import Path
import hashlib,json
B=Path(v['root']);P=B/v['filename'];assert P.resolve()==P and hashlib.sha256(P.read_bytes()).hexdigest()==v['source_SHA']
print(json.dumps(dict(passed=True,source_SHA=v['source_SHA'],no_SDK_or_GPU=True)))
'''
COLLECT_OWN_TEXT=r'''
from pathlib import Path
import hashlib,json
B=Path(v['root']);assert B.resolve()==B
marker=json.loads((B/v['marker']).read_bytes());assert marker[v['identity_key']]==v['identity_value']
rows=[]
for p in sorted(B.iterdir()):
 if not p.is_file() or p.suffix not in {'.json','.jsonl','.log'}:continue
 assert p.resolve()==p and not p.is_symlink();before=p.stat();assert before.st_size<=16*1024**2;raw=p.read_bytes();after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),stable=True))
print(json.dumps(dict(root=str(B),complete_original_UTF8=rows,no_binary_chunks_read=True)))
'''
SOURCE_STOP=r'''
from pathlib import Path
import json,time
B=Path(v['root']);assert B.resolve()==B and json.loads((B/'OWN_BUNDLE_TLS_DATA_SERVICE_MARKER.json').read_bytes())['service_id']==v['service_id'];p=B/'TLS_DATA_SERVICE_TERMINAL_ACTUAL.json'
if not p.exists():
 with (B/'OWN_STOP_REQUEST.json').open('x') as f:json.dump(dict(service_id=v['service_id']),f)
for _ in range(150):
 if p.exists():break
 time.sleep(.1)
print(json.dumps(dict(terminal=json.loads(p.read_bytes()) if p.exists() else None,only_own_stop_request=True)))
'''

def put(n,v):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m

def main():
 probe_raw=PROBE.read_bytes();assert hashlib.sha256(probe_raw).hexdigest()==PROBE_SHA;probe=json.loads(probe_raw);assert probe['passed'] and probe['probe']['passed_direct_route_TLS_HMAC_probe'] and probe['probe']['known_source_address']=='10.24.0.72' and probe['service_ending']['terminal']['listener_closed'] and probe['source_and_target_SSH_sequential_closed']
 original=json.loads(SOURCE_REPORT.read_bytes());assert original['bundle_passed'] and original['all_original_recorded_out'];producer=original['producer'];assert producer['producer_SHA']==PRODUCER;inputs=[x for x in original['full_original_texts'] if x['path'].endswith('/PROVEN72_RUNTIME_EXPORT_INPUT_SCOPE_ACTUAL.json')];assert len(inputs)==1 and inputs[0]['stable'];logical=json.loads(inputs[0]['UTF8'])['logical_input_bytes']
 frozen=json.loads((B/'FROZEN_DIRECT_HTTPS_DATA_PULL_SOURCE_INDEX_V1.json').read_bytes());service=B/'owned_bundle_only_TLS_Range_data_service_candidate_v1.py';worker=B/'target86_owned_direct_HTTPS_pull_candidate_v1.py';service_raw=service.read_bytes();worker_raw=worker.read_bytes();assert hashlib.sha256(service_raw).hexdigest()==frozen['service_SHA'] and hashlib.sha256(worker_raw).hexdigest()==frozen['worker_SHA']
 put('DIRECT_ALL29_ENTRY_ENTERED_BEFORE_STDIN_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),actual_probe_PASS_SHA=PROBE_SHA,producer_SHA=PRODUCER,source_service_seconds=1800,target_worker_seconds=1800,maximum_local_control_seconds=1900,one_source_then_target_then_cleanup_SSH=True,no_GPU_model_SDK_or_canonical=True));print('READY_FOR_SINGLE_STDIN_JSON',flush=True)
 req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo';password=req.pop('password');hkey=secrets.token_bytes(32);sid=uuid.uuid4().hex;run_id='PROVEN72_DIRECT_PULL_'+str(time.time_ns());client=None;sf=None;endpoint=None;waited=None;target_text=None;ending=None;primary=None;deadline=time.monotonic()+1900
 key=rsa.generate_private_key(public_exponent=65537,key_size=2048);name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'MOD4 owned bundle direct data')]);now=datetime.datetime.now(datetime.timezone.utc);pubkey=key.public_key();certificate=x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(pubkey).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(seconds=60)).not_valid_after(now+datetime.timedelta(minutes=35)).add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address('10.24.0.72'))]),critical=False).add_extension(x509.BasicConstraints(ca=True,path_length=0),critical=True).add_extension(x509.SubjectKeyIdentifier.from_public_key(pubkey),critical=False).add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(pubkey),critical=False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),critical=False).add_extension(x509.KeyUsage(True,False,True,False,False,True,True,False,False),critical=True).sign(key,hashes.SHA256()).public_bytes(serialization.Encoding.PEM).decode();private=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()).decode();key=None
 wrapper=module('compressed_memory_for_proven_direct_all29',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 def left():
  q=deadline-time.monotonic();assert q>0,'original1900s control bound';return q
 def connect(host,user,secret,pin):
  sock=socket.create_connection((host,22),timeout=min(10,left()));c=paramiko.Transport(sock)
  try:
   c.banner_timeout=min(10,left());c.auth_timeout=min(10,left());c.start_client(timeout=min(10,left()));assert hashlib.sha256(c.get_remote_server_key().asbytes()).hexdigest()==pin,'SSH_PIN_MISMATCH_BEFORE_AUTH';c.auth_password(user,secret,fallback=False);return c
  except BaseException:c.close();raise
 def source_connect():
  m=module('same72_memory_for_proven_direct_all29',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=m.recover()
  try:return connect('10.24.0.72','lc01',secret,PIN72)
  finally:secret=None
 def run(c,python,code,args):
  ch=c.open_session(timeout=min(10,left()));ch.exec_command(' '.join(shlex.quote(x) for x in python+['-c',"import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"]));ch.settimeout(min(30,left()));inp=ch.makefile_stdin('wb');inp.write((json.dumps(dict(args,code=code))+chr(10)).encode());inp.flush();ch.shutdown_write();out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(err,out);return json.loads(out)
 def upload(c,root,p,raw):
  nonlocal sf
  sf=paramiko.SFTPClient.from_transport(c);sf.get_channel().settimeout(min(30,left()))
  with sf.open(root+'/'+p.name,'wx') as f:f.write(raw)
  sf.close();sf=None
 try:
  binding=dict(passed=True,actual_probe_receipt=str(PROBE),actual_probe_SHA=PROBE_SHA,known_source_address='10.24.0.72',probe_elapsed_seconds=probe['probe']['elapsed_seconds'])
  client=source_connect();put('SOURCE_TLS_DATA_NAMESPACE_ADMISSION_ACTUAL.json',run(client,PY72,SOURCE_PRE,dict(root=SERVICE,export=EXPORT,producer=producer,service_id=sid)));upload(client,SERVICE,service,service_raw)
  config=dict(maximum_seconds=1800,data_enable=True,service_id=sid,actual_probe_pass_binding=binding,hmac_key_hex=hkey.hex(),public_certificate_pem=certificate,private_key_pem=private)
  endpoint=run(client,PY72,SOURCE_START,dict(root=SERVICE,filename=service.name,source_SHA=hashlib.sha256(service_raw).hexdigest(),python=PY72,memory_config=config));config.clear();private=None;put('SOURCE_TLS_DATA_PUBLIC_ENDPOINT_RETURNED_ACTUAL.json',endpoint);client.close();client=None
  client=connect('10.50.0.86','robemo',password,PIN86);password=None;put('TARGET86_NEW_DIRECT_ATTEMPT_ADMISSION_ACTUAL.json',run(client,['/usr/bin/python3','-B'],TARGET_PRE,dict(root=ATTEMPT,run_id=run_id,producer_SHA=PRODUCER,compressed_bytes=producer['compressed_bytes'],logical_input_bytes=logical)));upload(client,ATTEMPT,worker,worker_raw);put('TARGET86_DIRECT_WORKER_SOURCE_RECONCILIATION_ACTUAL.json',run(client,['/usr/bin/python3','-B'],TARGET_VERIFY,dict(root=ATTEMPT,filename=worker.name,source_SHA=hashlib.sha256(worker_raw).hexdigest())))
  env={'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','HOME':ATTEMPT+'/home','TMPDIR':ATTEMPT+'/tmp','XDG_CACHE_HOME':ATTEMPT+'/cache','XDG_CONFIG_HOME':ATTEMPT+'/config','XDG_DATA_HOME':ATTEMPT+'/data','XDG_STATE_HOME':ATTEMPT+'/state'}
  cmd='cd '+shlex.quote(ATTEMPT)+' && '+ ' '.join(shlex.quote(x) for x in ['/usr/bin/env','-u','PYTHONPATH','-u','PYTHONHOME','-u','LD_LIBRARY_PATH','-u','LD_PRELOAD']+[k+'='+v for k,v in env.items()]+['/usr/bin/python3','-u','-B',ATTEMPT+'/'+worker.name]);ch=client.open_session(timeout=min(10,left()));ch.set_combine_stderr(True);ch.exec_command(cmd);ch.settimeout(1)
  cfg=dict(maximum_seconds=1800,actual_probe_pass_binding=binding,producer=producer,run_id=run_id,endpoint=endpoint,logical_input_bytes=logical,hmac_key_hex=hkey.hex());inp=ch.makefile_stdin('wb');inp.write((json.dumps(cfg)+chr(10)).encode());inp.flush();ch.shutdown_write();cfg.clear();outbytes=0;last=0;started=time.time();timer=threading.Timer(left(),client.close);timer.daemon=True;timer.start()
  try:
   with (R/'TARGET86_DIRECT_PULL_COMPLETE_ORIGINAL_STDOUT_STDERR_UTF8.log').open('xb') as log:
    while True:
     left()
     try:block=ch.recv(65536)
     except socket.timeout:block=None
     if block:
      outbytes+=len(block);assert outbytes<=16*1024**2;log.write(block);log.flush();print(block.decode('utf8'),end='',flush=True)
     elif block==b'':break
     if time.time()-last>=30:print(json.dumps(dict(stage='OWN_FOREGROUND_DIRECT_PULL_SAME_SSH_HANDLE',epoch=time.time(),elapsed_seconds=time.time()-started,no_other_SSH=True)),flush=True);last=time.time()
    rc=ch.recv_exit_status();waited=dict(epoch=time.time(),actual_waited=True,returncode=rc,exact_command=cmd,run_id=run_id,root=ATTEMPT,source72_SSH_closed_before_target=True,full_stdout_stderr_bytes=outbytes);put('TARGET86_FOREGROUND_DIRECT_PULL_ACTUAL_WAITED.json',waited)
  finally:timer.cancel()
  target_text=run(client,['/usr/bin/python3','-B'],COLLECT_OWN_TEXT,dict(root=ATTEMPT,marker='OWN_DIRECT_PULL_ATTEMPT_MARKER.json',identity_key='run_id',identity_value=run_id));put('TARGET86_DIRECT_PULL_COMPLETE_ORIGINAL_UTF8_REPORTS_ACTUAL.json',target_text);client.close();client=None
 except BaseException:
  primary=traceback.format_exc();put('DIRECT_HTTPS_PRIMARY_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=primary,old_and_new_partial_bytes_preserved=True,no_retry_or_other_host_port=True))
 finally:
  if sf:sf.close();sf=None
  if client:client.close();client=None
  password=None;private=None;hkey=None
 try:
  if endpoint:
   client=source_connect();ending=run(client,PY72,SOURCE_STOP,dict(root=SERVICE,service_id=sid));put('SOURCE_TLS_DATA_OWN_ENDING_RETURNED_ACTUAL.json',ending);texts=run(client,PY72,COLLECT_OWN_TEXT,dict(root=SERVICE,marker='OWN_BUNDLE_TLS_DATA_SERVICE_MARKER.json',identity_key='service_id',identity_value=sid));put('SOURCE_TLS_DATA_COMPLETE_ORIGINAL_UTF8_REPORTS_ACTUAL.json',texts);client.close();client=None
 except BaseException:put('SOURCE_OWN_TLS_SERVICE_ENDING_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),original1800s_bound_retained=True))
 finally:
  if client:client.close()
  transport.SESSION=previous;certificate=None
 values={Path(x['path']).name:json.loads(x['UTF8']) for x in (target_text or {}).get('complete_original_UTF8',[]) if x['path'].endswith('.json')};complete=values.get('DIRECT_RECEIVER_ALL29_CHUNKS_FULL_SHA_COMPLETE_ACTUAL.json');term=values.get('DIRECT_PULL_TERMINAL_ACTUAL.json');passed=bool(not primary and waited and waited['actual_waited'] and waited['returncode']==0 and complete and complete['passed_all_artifact_chunks_only'] and complete['whole_ordered_archive_SHA']==PRODUCER and term and term['passed_artifact_only'] and ending and ending['terminal'] and ending['terminal']['listener_closed'])
 put('DIRECT_ALL29_ARTIFACT_PULL_AND_ORIGINAL_ENDING_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed_all_artifacts_only=passed,run_id=run_id,producer_SHA=PRODUCER,worker_waited=waited,receiver_complete=complete,receiver_terminal=term,source_service_ending=ending,source_and_target_SSH_sequential_and_closed=True,primary_error=primary,no_SDK_CUDA_model_or_training_readiness_claim=True,all_original_partial_files_retained=True));print(json.dumps(dict(passed_all_artifacts_only=passed,no_SDK_ready=True,source_and_target_SSH_closed=True)),flush=True)
 if not passed:raise SystemExit(2)

if __name__=='__main__':
 try:main()
 except SystemExit:raise
 except BaseException:put('DIRECT_ALL29_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
