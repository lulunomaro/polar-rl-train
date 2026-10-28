"""Temporary bundle-only TLS/HMAC endpoint; key/certificate-private material RAM only."""
from pathlib import Path
import hashlib,hmac,http.server,json,os,socket,ssl,sys,threading,time,traceback
EXPORT=Path('/home/lc01/Zonglin Li/zonglin2/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1')
B=Path(__file__).resolve().parent;PRODUCER='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def emit(**v):
 with (B/'TLS_SERVICE_PUBLIC_PROGRESS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(epoch=time.time(),**v))+chr(10))
def identity():
 p=Path('/proc/self');raw=(p/'stat').read_text();v=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));return dict(pid=os.getpid(),creation=boot+int(v[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],root=os.getcwd())
def main():
 assert B.resolve().is_relative_to(EXPORT) and not B.is_symlink();cfg=json.loads(sys.stdin.readline());assert cfg['maximum_seconds']==1800 and cfg['probe_only'] is True
 marker=json.loads((B/'OWN_BUNDLE_TLS_SERVICE_MARKER.json').read_bytes());assert marker['root']==str(B) and marker['service_id']==cfg['service_id']
 producer=json.loads((EXPORT/'PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json').read_bytes());terminal=json.loads((EXPORT/'EXPORT_SUPERVISOR_TERMINAL_ACTUAL.json').read_bytes());assert producer['passed'] and producer['producer_SHA']==PRODUCER and terminal['passed']
 key=bytes.fromhex(cfg.pop('hmac_key_hex'));assert len(key)==32;cert=cfg.pop('public_certificate_pem').encode();private=cfg.pop('private_key_pem').encode();certDER=ssl.PEM_cert_to_DER_cert(cert.decode());certSHA=hashlib.sha256(certDER).hexdigest();start=time.time();deadline=start+1800;stop=threading.Event();lock=threading.Lock();used={};reason=['original1800s_bound']
 cfd=os.memfd_create('mod4_public_tls_certificate',os.MFD_CLOEXEC);kfd=os.memfd_create('mod4_private_tls_key',os.MFD_CLOEXEC)
 try:
  os.write(cfd,cert);os.write(kfd,private);context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_2;context.load_cert_chain('/proc/self/fd/'+str(cfd),'/proc/self/fd/'+str(kfd))
 finally:os.close(cfd);os.close(kfd);private=None
 class Handler(http.server.BaseHTTPRequestHandler):
  protocol_version='HTTP/1.1'
  def log_message(self,fmt,*args):emit(stage='PUBLIC_HTTP_STATUS_NO_HEADERS',message=fmt%args)
  def response(self,code,payload):
   raw=json.dumps(payload).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw);self.wfile.flush()
  def authorized(self):
   try:
    expires=self.headers['X-Mod4-Expires'];nonce=self.headers['X-Mod4-Nonce'];signature=self.headers['X-Mod4-HMAC'];epoch=int(expires);rangevalue=self.headers.get('Range','');assert time.time()<=epoch<=min(deadline,time.time()+300) and len(nonce)==32 and all(x in '0123456789abcdef' for x in nonce)
    message='GET\n'+self.path+'\n'+rangevalue+'\n'+expires+'\n'+nonce+'\n'+PRODUCER;expected=hmac.new(key,message.encode(),hashlib.sha256).hexdigest()
    assert hmac.compare_digest(signature,expected)
    with lock:
     for n,t in list(used.items()):
      if t<time.time():used.pop(n,None)
     assert nonce not in used;used[nonce]=epoch
    return True
   except Exception:return False
  def do_GET(self):
   if not self.authorized():self.response(403,dict(error='denied'));return
   if self.path=='/probe':
    self.response(200,dict(passed_probe_only=True,producer_SHA=PRODUCER,compressed_bytes=producer['compressed_bytes'],chunks=len(producer['chunks']),certificate_SHA=certSHA,service_id=cfg['service_id'],no_archive_bytes_or_models_read=True));reason[0]='authenticated_probe_completed';stop.set();return
   self.response(403,dict(error='large artifact data disabled in this probe-only stage'))
 class Server(http.server.HTTPServer):
  def get_request(self):
   sock,address=super().get_request();sock.settimeout(10)
   try:return context.wrap_socket(sock,server_side=True),address
   except BaseException:sock.close();raise
 server=Server(('0.0.0.0',0),Handler);assert server.server_port!=29754;server.timeout=1
 public=dict(passed_endpoint_startup_only=True,epoch=start,service_id=cfg['service_id'],identity=identity(),advertised_host='10.24.0.72',actual_OS_selected_port=server.server_port,certificate_SHA=certSHA,public_certificate_pem=cert.decode(),producer_SHA=PRODUCER,maximum_seconds=1800,probe_only=True,private_key_memory_memfd_only=True,HMAC_key_STDIN_RAM_only=True,no_GPU_model_source_env_or_canonical_change=True)
 put('TLS_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json',public)
 try:
  while not stop.is_set() and time.time()<deadline:
   p=B/'OWN_STOP_REQUEST.json'
   if p.exists() and json.loads(p.read_bytes())['service_id']==cfg['service_id']:reason[0]='authorized_own_stop_request';break
   server.handle_request()
 finally:
  server.server_close();key=None;put('TLS_SERVICE_TERMINAL_ACTUAL.json',dict(epoch=time.time(),passed_service_function=True,identity=public['identity'],reason=reason[0],service_id=cfg['service_id'],probe_only=True,listener_closed=True,no_unknown_process_or_source_files_changed=True,no_secret_written_or_reported=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('TLS_SERVICE_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_secret_in_report=True));raise
