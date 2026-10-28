"""Candidate only: immutable29-chunk HTTPS service, private keys stdin/memfd RAM."""
from pathlib import Path
import hashlib,hmac,http.server,json,os,re,signal,ssl,stat,sys,time,traceback
EXPORT=Path('/home/lc01/Zonglin Li/zonglin2/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1')
B=Path(__file__).resolve().parent;PRODUCER='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'

def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def emit(**v):
 with (B/'TLS_DATA_PUBLIC_PROGRESS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(epoch=time.time(),**v))+chr(10))

def identity():
 p=Path('/proc/self');raw=(p/'stat').read_text();v=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));return dict(pid=os.getpid(),creation=boot+int(v[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.getcwd())

def main():
 assert B.resolve()==B and B.is_relative_to(EXPORT) and not B.is_symlink();cfg=json.loads(sys.stdin.readline());assert cfg['maximum_seconds']==1800 and cfg['data_enable'] is True and cfg['actual_probe_pass_binding']['passed'] is True
 marker=json.loads((B/'OWN_BUNDLE_TLS_DATA_SERVICE_MARKER.json').read_bytes());assert marker['root']==str(B) and marker['service_id']==cfg['service_id']
 producer=json.loads((EXPORT/'PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json').read_bytes());terminal=json.loads((EXPORT/'EXPORT_SUPERVISOR_TERMINAL_ACTUAL.json').read_bytes());assert producer['passed'] and producer['producer_SHA']==PRODUCER and terminal['passed'] and len(producer['chunks'])==29 and sum(x['bytes'] for x in producer['chunks'])==producer['compressed_bytes']==15158703068
 rows=producer['chunks']
 for i,row in enumerate(rows):assert Path(row['path'])==EXPORT/('runtime72.tar.gz.chunk'+str(i).zfill(4)) and 0<row['bytes']<=512*1024**2 and re.fullmatch('[0-9a-f]{64}',row['SHA'])
 key=bytes.fromhex(cfg.pop('hmac_key_hex'));assert len(key)==32;cert=cfg.pop('public_certificate_pem').encode();private=cfg.pop('private_key_pem').encode();certSHA=hashlib.sha256(ssl.PEM_cert_to_DER_cert(cert.decode())).hexdigest();start=time.time();deadline=start+1800;used={};reason='original1800s_bound';me=identity()
 cfd=os.memfd_create('mod4_public_tls_certificate',os.MFD_CLOEXEC);kfd=os.memfd_create('mod4_private_tls_key',os.MFD_CLOEXEC)
 try:
  os.write(cfd,cert);os.write(kfd,private);context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_2;context.load_cert_chain('/proc/self/fd/'+str(cfd),'/proc/self/fd/'+str(kfd))
 finally:os.close(cfd);os.close(kfd);private=None
 class Handler(http.server.BaseHTTPRequestHandler):
  protocol_version='HTTP/1.1'
  def log_message(self,fmt,*args):emit(stage='PUBLIC_HTTP_STATUS_NO_HEADERS',message=fmt%args)
  def response(self,status,payload):
   raw=json.dumps(payload).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw);self.wfile.flush()
  def authorized(self):
   try:
    expires=self.headers['X-Mod4-Expires'];nonce=self.headers['X-Mod4-Nonce'];signature=self.headers['X-Mod4-HMAC'];epoch=int(expires);assert time.time()<=epoch<=min(deadline,time.time()+300) and re.fullmatch('[0-9a-f]{32}',nonce)
    message='GET\n'+self.path+'\n'+self.headers.get('Range','')+'\n'+expires+'\n'+nonce+'\n'+PRODUCER;assert hmac.compare_digest(signature,hmac.new(key,message.encode(),hashlib.sha256).hexdigest())
    for n,t in list(used.items()):
     if t<time.time():used.pop(n,None)
    assert nonce not in used;used[nonce]=epoch;return True
   except Exception:return False
  def do_GET(self):
   if not self.authorized():self.response(403,dict(error='denied'));return
   if self.path=='/probe':self.response(200,dict(passed=True,producer_SHA=PRODUCER,compressed_bytes=producer['compressed_bytes'],chunks=29,certificate_SHA=certSHA,service_id=cfg['service_id'],data_enable=True));return
   chunk=re.fullmatch(r'/chunk/(\d{4})',self.path);prefix=re.fullmatch(r'/prefix/(\d{4})/(\d{1,9})',self.path)
   if not chunk and not prefix:self.response(403,dict(error='only immutable29 bundle chunks and bounded prefix digests are served'));return
   i=int((chunk or prefix).group(1))
   if not 0<=i<len(rows):self.response(403,dict(error='chunk index denied'));return
   row=rows[i];fd=os.open(row['path'],os.O_RDONLY|os.O_NOFOLLOW)
   with os.fdopen(fd,'rb') as f:
    before=os.fstat(f.fileno());assert stat.S_ISREG(before.st_mode) and before.st_size==row['bytes'];stable=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
    if prefix:
     n=int(prefix.group(2));assert not self.headers.get('Range') and 0<n<=row['bytes'];left=n;digest=hashlib.sha256()
     while left:
      block=f.read(min(1024**2,left));assert block;digest.update(block);left-=len(block)
     assert stable(before)==stable(os.fstat(f.fileno()));self.response(200,dict(producer_SHA=PRODUCER,chunk_index=i,prefix_bytes=n,prefix_SHA=digest.hexdigest(),expected_full_SHA=row['SHA'],source_stat_unchanged=True));return
    rangevalue=self.headers.get('Range','');offset=0
    if rangevalue:
     m=re.fullmatch(r'bytes=(\d+)-',rangevalue);assert m;offset=int(m.group(1));assert 0<offset<row['bytes']
    f.seek(offset);self.send_response(206 if offset else 200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(row['bytes']-offset));self.send_header('Accept-Ranges','bytes');self.send_header('Cache-Control','no-store');self.send_header('X-Mod4-Producer',PRODUCER);self.send_header('X-Mod4-Chunk-SHA',row['SHA'])
    if offset:self.send_header('Content-Range','bytes '+str(offset)+'-'+str(row['bytes']-1)+'/'+str(row['bytes']))
    self.end_headers();left=row['bytes']-offset
    while left:
     block=f.read(min(1024**2,left));assert block;self.wfile.write(block);left-=len(block)
    self.wfile.flush();assert stable(before)==stable(os.fstat(f.fileno()));emit(stage='IMMUTABLE_BUNDLE_CHUNK_RESPONSE_COMPLETED',chunk=i,offset=offset,new_bytes=row['bytes']-offset,expected_full_SHA=row['SHA'])
 class Server(http.server.HTTPServer):
  def get_request(self):
   sock,address=super().get_request();sock.settimeout(min(30,max(.01,deadline-time.time())))
   try:return context.wrap_socket(sock,server_side=True),address
   except BaseException:sock.close();raise
 server=Server(('0.0.0.0',0),Handler);assert server.server_port!=29754;server.timeout=1
 def expired(signum,frame):raise TimeoutError('owned original1800s data service bound')
 signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,1800)
 put('TLS_DATA_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json',dict(passed_endpoint_startup_only=True,epoch=start,deadline_epoch=deadline,service_id=cfg['service_id'],identity=me,advertised_host='10.24.0.72',actual_OS_selected_port=server.server_port,certificate_SHA=certSHA,public_certificate_pem=cert.decode(),producer_SHA=PRODUCER,maximum_seconds=1800,data_enable=True,private_key_memory_memfd_only=True,HMAC_key_STDIN_RAM_only=True,no_GPU_model_source_env_or_canonical_change=True))
 try:
  while time.time()<deadline:
   p=B/'OWN_STOP_REQUEST.json'
   if p.exists() and json.loads(p.read_bytes())['service_id']==cfg['service_id']:reason='authorized_own_stop_request';break
   server.handle_request()
 except TimeoutError:reason='original1800s_bound'
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);server.server_close();key=None;put('TLS_DATA_SERVICE_TERMINAL_ACTUAL.json',dict(epoch=time.time(),identity=me,reason=reason,service_id=cfg['service_id'],listener_closed=True,no_unknown_process_or_source_environment_change=True,not_a_receiver_full_SHA_or_SDK_proof=True))

if __name__=='__main__':
 try:main()
 except BaseException:put('TLS_DATA_SERVICE_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_secret_in_report=True));raise
