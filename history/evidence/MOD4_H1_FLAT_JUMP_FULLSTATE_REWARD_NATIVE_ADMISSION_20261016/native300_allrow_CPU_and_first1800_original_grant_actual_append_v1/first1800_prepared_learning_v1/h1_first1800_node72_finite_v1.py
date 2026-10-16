"""One admitted H1 GPU1 fresh-process chain; no native replay or extra window."""
from pathlib import Path
import os,sys,json,time,hashlib,hmac,urllib.request,subprocess,traceback,fcntl
B=Path(__file__).resolve().parent;PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh';PORT=29732
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:return None
def env():
 j=B/'job0';e=dict(os.environ)
 for n in ('home','tmp','cache','config','data'):(j/n).mkdir(exist_ok=True)
 for n in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):e.pop(n,None)
 e.update(CUDA_VISIBLE_DEVICES=json.loads((j/'TASK.json').read_bytes())['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(j/'home'),TMPDIR=str(j/'tmp'),XDG_CACHE_HOME=str(j/'cache'),XDG_CONFIG_HOME=str(j/'config'),XDG_DATA_HOME=str(j/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');return e
def send(cfg,row):
 token=cfg['token'].encode();body=json.dumps(dict(run_id=cfg['run_id'],epoch=time.time(),row=row)).encode();assert len(body)<2000000;r=urllib.request.Request('http://10.24.4.210:'+str(PORT)+'/',data=body,headers={'X-Own-Signature':hmac.new(token,body,hashlib.sha256).hexdigest(),'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=15) as response:raw=response.read();sig=response.headers['X-Own-Signature']
 assert hmac.compare_digest(sig,hmac.new(token,raw,hashlib.sha256).hexdigest());return json.loads(raw)
def collect(phase,p):
 out=B/'job0'/phase;rc=p.poll();latest=read(out/'latest_complete.json');final=read(out/'FINAL.json');errors=[q.name for q in out.glob('*ORIGINAL_ERROR*.json')]
 if rc is not None and not (out/'WORKER_EXIT_ACTUAL.json').exists():put(out/'WORKER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=p.pid,returncode=rc,actual_waited=True,phase=phase))
 return dict(phase=phase,worker=ident(p.pid),returncode=rc,latest_save=latest,final=final,errors=errors,actual_exit=read(out/'WORKER_EXIT_ACTUAL.json'))
def main(cfg):
 lock=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+');p=None;phase=None;last=time.time();go=None;original_error=None;row={}
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put(B/'NODE_IDENTITY.json',ident(os.getpid()));cert=read(B/'H1_ACTUAL_ADMISSION_CERTIFICATE.json');assert cert['source_SHA']==cfg['source_SHA'] and cert['native_CPU_report_SHA']==cfg['native_CPU_report_SHA'] and cert['local_CPU_receipt_SHA']==cfg['local_CPU_receipt_SHA'] and cert['passed'];assert H(B/'job0/source/H1_admitted_full_source.pt')==cfg['source_SHA']
  manifest=read(B/'H1_FIRST1800_PAYLOAD_MANIFEST.json')
  for x in manifest['files']:
   q=B/x['relative'];assert q.stat().st_size==x['bytes'] and H(q)==x['SHA'],x['relative']
  base=dict(actual_native_CPU_local_model_admitted=True,source_SHA=cfg['source_SHA'],native_CPU_report_SHA=cfg['native_CPU_report_SHA'],local_CPU_receipt_SHA=cfg['local_CPU_receipt_SHA'],target_payload_exact=True,target_actual_validation_fcntl_held=True)
  def spawn(next_phase):
   assert not (B/'job0'/next_phase).exists();q=subprocess.Popen([PY,'-u','-B',str(B/'h1_learning_phase_worker_v1.py'),'--phase',next_phase],cwd=B,env=env(),stdout=(B/'job0'/(next_phase+'_worker.log')).open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(B/'job0'/(next_phase+'_WORKER_STARTED.json'),ident(q.pid));return q
  while True:
   row={**base,**(collect(phase,p) if p else dict(phase='admitted_waiting_original_grant',returncode=None))};reply=send(cfg,row);last=time.time()
   if reply.get('go') and go is None:
    go=reply['go'];assert go['actual_H1_first1800_scope_admitted'] and go['source_SHA']==cfg['source_SHA'] and go['max_parent_seconds']==1800 and go['exit_headroom_seconds']==300
    for name in ('precheck128','precheck20k','production'):put(B/('GO_'+name.upper()+'.json'),go)
    phase='precheck128';p=spawn(phase)
   stop=bool(reply.get('stop') or (go and time.time()>=go['save_deadline']))
   if p and p.poll() is not None:
    row={**base,**collect(phase,p)};assert row['returncode']==0 and row['final'] and row['final']['passed'] and not row['errors'],row
    if phase=='production':break
    if stop or time.time()>=go['save_deadline']-240:raise RuntimeError('No time for the next fresh phase within original first1800 parent; closed precheck retained, no production issued')
    phase='precheck20k' if phase=='precheck128' else 'production';p=spawn(phase)
   if stop:
    if p and p.poll() is None:
     q=B/'job0'/phase;q.mkdir(exist_ok=True);put(q/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Original owner saved-stop deadline; no signal or kill'))
    if p is None:break
   put(B/'NODE_CURRENT.json',dict(epoch=time.time(),row=row,reply=reply,one_H1_GPU1_only=True))
   time.sleep(3)
 except BaseException:
  original_error=traceback.format_exc();put(B/'NODE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=original_error,no_auto_retry=True))
  if p and p.poll() is None:
   q=B/'job0'/phase;q.mkdir(exist_ok=True);put(q/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite node exception; full valid-prefix save and natural exit only'))
 finally:
  if p:p.wait();row={**row,**collect(phase,p)}
  row.update(node_terminal_after_actual_children_exit=True,actual_all_children_waited=True,returncode=p.returncode if p else 0,original_error=bool(original_error),production_complete=bool(phase=='production' and p and p.returncode==0 and (row.get('final') or {}).get('passed')))
  put(B/'NODE_TERMINAL_ALL_OWN_CHILDREN_EXIT_ACTUAL.json',dict(epoch=time.time(),row=row))
  acknowledged=False
  for attempt in range(3):
   try:reply=send(cfg,row);acknowledged=True;break
   except BaseException:put(B/('TERMINAL_HANDOFF_ORIGINAL_ERROR_'+str(attempt)+'.json'),dict(epoch=time.time(),error=traceback.format_exc()));time.sleep(5)
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put(B/'NODE_EXIT_ACTUAL.json',dict(epoch=time.time(),all_own_children_actual_waited=True,validation_fcntl_released=True,terminal_received_by_original_owner=acknowledged))
 if original_error:raise RuntimeError('Own original node error retained in NODE_ORIGINAL_ERROR.json')
if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert not (B/'NODE_IDENTITY.json').exists() and not (B/'NODE_CONSOLE.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='H1_first1800_node72')),flush=True)
 else:
  os.setsid();f=os.open(str(B/'NODE_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);main(cfg)
