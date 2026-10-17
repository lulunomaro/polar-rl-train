"""One new H1 grounded reward axis: actual native/CPU first, one bounded PPO last."""
from pathlib import Path
import os,sys,json,time,hashlib,hmac,urllib.request,subprocess,traceback,fcntl
B=Path(__file__).resolve().parent;PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh';PORT=29734
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:return None
def env(cpu=False):
 j=B/'job0';e=dict(os.environ)
 for n in ('home','tmp','cache','config','data'):(j/n).mkdir(exist_ok=True)
 for k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):e.pop(k,None)
 e.update(CUDA_VISIBLE_DEVICES='' if cpu else read(j/'TASK.json')['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(j/'home'),TMPDIR=str(j/'tmp'),XDG_CACHE_HOME=str(j/'cache'),XDG_CONFIG_HOME=str(j/'config'),XDG_DATA_HOME=str(j/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');return e
def send(cfg,row):
 token=cfg['token'].encode();raw=json.dumps(dict(epoch=time.time(),run_id=cfg['run_id'],row=row)).encode();assert len(raw)<2000000;req=urllib.request.Request('http://10.24.4.210:'+str(PORT)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest(),'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=15) as response:body=response.read();sig=response.headers['X-Own-Signature']
 assert hmac.compare_digest(sig,hmac.new(token,body,hashlib.sha256).hexdigest());return json.loads(body)
def spawn(phase):
 j=B/'job0';names={'native_GPU':'h1_ground_prelaunch_v2_native_worker_v1.py','native_CPU':'review_H1_prelaunch_v2_native_allrows_CPU_v1.py','production':'h1_prelaunch_v2_production_worker_v1.py'};args=[PY,'-u','-B',str(B/names[phase])]
 if phase=='native_GPU':assert not (j/'native').exists()
 if phase=='production':assert not (j/'production').exists();args+=['--phase','production']
 p=subprocess.Popen(args,cwd=B,env=env(phase=='native_CPU'),stdout=(j/(phase+'_WORKER.log')).open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(j/(phase+'_WORKER_STARTED_ACTUAL.json'),ident(p.pid));return p
def row_for(phase,p):
 out=B/'job0'/('production' if phase=='production' else 'native');rc=p.poll() if p else None
 if p and rc is not None and not (B/'job0'/(phase+'_EXIT_ACTUAL.json')).exists():put(B/'job0'/(phase+'_EXIT_ACTUAL.json'),dict(epoch=time.time(),pid=p.pid,returncode=rc,actual_waited=True))
 return dict(phase=phase,worker=ident(p.pid) if p else None,returncode=rc,final=read(out/'FINAL.json'),latest_save=read(out/'latest_complete.json'),errors=[x.name for x in out.glob('*ORIGINAL_ERROR*.json')],actual_exit=read(B/'job0'/(phase+'_EXIT_ACTUAL.json')))
def main(cfg):
 lock=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+');p=None;phase='waiting_source';error=None;native_rc=None;cpu_rc=None;native_cpu=None;native_cpu_SHA=None;resource=None;go=None;row={};children=[]
 try:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put(B/'NODE_IDENTITY.json',ident(os.getpid()));m=read(B/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json');assert H(B/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json')==cfg['payload_manifest_SHA']
  for a in m['files']:
   q=B/a['relative'];assert q.resolve().is_relative_to(B.resolve()) and q.stat().st_size==a['bytes'] and H(q)==a['SHA'],a['relative']
  assert H(B/'job0/source/H1_final10_protected.pt')==cfg['source_SHA'];base=dict(source_SHA=cfg['source_SHA'],target_payload_manifest_SHA=cfg['payload_manifest_SHA'],target_actual_validation_fcntl_held=True);reply=send(cfg,{**base,'phase':'waiting_source'});assert not reply['stop'];phase='native_GPU';p=spawn(phase);children.append(p);last=time.time();begun=time.time()
  while True:
   row={**base,**row_for(phase,p),**dict(native_GPU_returncode=native_rc,native_CPU_returncode=cpu_rc,native_CPU=native_cpu,native_CPU_report_SHA=native_cpu_SHA,new_ready_GPU_resource_passed=resource is not None)}
   try:reply=send(cfg,row);last=time.time()
   except BaseException:reply={};put(B/('NODE_CONTROL_READ_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_signal_save_stop_if_stale120=True))
   stop=bool(reply.get('stop') or time.time()-last>120 or time.time()-begun>7200 or (go and time.time()>=go['save_deadline']))
   if p and p.poll() is not None:
    actual=row_for(phase,p);assert actual['returncode']==0 and not actual['errors'],actual
    if phase=='native_GPU':
     assert read(B/'job0/native/NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json') and actual['final'] and actual['final']['passed_worker_not_independent_CPU'];native_rc=0;phase='native_CPU';p=spawn(phase);children.append(p)
    elif phase=='native_CPU':
     cpu_rc=0;q=B/'job0/native/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json';native_cpu=read(q);assert native_cpu and native_cpu['passed'] and native_cpu['prelaunch_proxy_total_credit']>0;native_cpu_SHA=H(q);snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in snapshot.splitlines() if 'c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>7000;resource=dict(epoch=time.time(),line=line,native_GPU_actual_waited_out=True,CPU_actual_waited_out=True);put(B/'READY_ACTUAL_NATIVE_CPU_AND_GPU_RESOURCE.json',dict(epoch=time.time(),native_CPU_report_SHA=native_cpu_SHA,native_CPU=native_cpu,actual_resource=resource));phase='ready';p=None
    elif phase=='production':assert actual['final'] and actual['final']['passed'];break
   if phase=='ready' and reply.get('go') and go is None:
    assert not stop;go=reply['go'];assert go['actual_H1_prelaunch_v2_scope_admitted'] and go['source_SHA']==cfg['source_SHA'] and go['max_parent_seconds']==1800 and go['exit_headroom_seconds']==300;put(B/'GO_PRODUCTION.json',go);phase='production';p=spawn(phase);children.append(p)
   if stop:
    if p and p.poll() is None:
     q=B/'job0'/('production' if phase=='production' else 'native');q.mkdir(exist_ok=True)
     if not (q/'STOP_AFTER_SAVE.json').exists():put(q/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own source/finite deadline; full valid-prefix saved-stop without signals'))
    if p is None:raise RuntimeError('Source finite stop before any new learning grant')
   put(B/'NODE_CURRENT.json',dict(epoch=time.time(),row=row,reply=reply,native0PPO_then_one_actual_admitted_production_window=True));time.sleep(3)
 except BaseException:
  error=traceback.format_exc();put(B/'NODE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_automatic_relaunch_or_next_window=True))
  if p and p.poll() is None:
   out=B/'job0'/('production' if phase=='production' else 'native');out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own exception valid-prefix saved-stop; no signals'))
 finally:
  for child in children:child.wait()
  row={**row,**row_for(phase,p)};row.update(node_terminal_after_actual_children_exit=True,actual_all_children_waited=True,returncode=p.returncode if p else (0 if error is None else 1),original_error=error is not None,production_complete=bool(phase=='production' and error is None and (row.get('final') or {}).get('passed')));put(B/'NODE_TERMINAL_ALL_OWN_CHILDREN_EXIT_ACTUAL.json',dict(epoch=time.time(),row=row));ack=False
  for attempt in range(3):
   try:send(cfg,row);ack=True;break
   except BaseException:put(B/('TERMINAL_HANDOFF_ORIGINAL_ERROR_'+str(attempt)+'.json'),dict(epoch=time.time(),error=traceback.format_exc()));time.sleep(5)
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put(B/'NODE_EXIT_ACTUAL.json',dict(epoch=time.time(),all_own_children_actual_waited=True,validation_fcntl_released=True,terminal_received_by_original_owner=ack))
 if error:raise RuntimeError('Original node error saved, no retry')
if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert not (B/'NODE_IDENTITY.json').exists() and not (B/'NODE_CONSOLE.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='H1_ground_prelaunch_v2_finite_node')),flush=True)
 else:
  os.setsid();f=os.open(str(B/'NODE_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);main(cfg)
