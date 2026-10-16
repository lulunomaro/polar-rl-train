"""Owned72 finite two-GPU admission; only E2 may receive an original-owner learning grant."""
from pathlib import Path
import os,sys,json,time,subprocess,hashlib,hmac,urllib.request,traceback
B=Path(__file__).resolve().parent;PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh';PORT=29730
OWN_WORKERS={};OWN_PHASES={}
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:return None
def env(job):
 j=B/('job'+str(job));e=dict(os.environ)
 for n in ('home','tmp','cache','config','data'):(j/n).mkdir(exist_ok=True)
 for k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):e.pop(k,None)
 e.update(CUDA_VISIBLE_DEVICES=json.loads((j/'TASK.json').read_bytes())['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(j/'home'),TMPDIR=str(j/'tmp'),XDG_CACHE_HOME=str(j/'cache'),XDG_CONFIG_HOME=str(j/'config'),XDG_DATA_HOME=str(j/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');return e
def spawn(job,phase):
 j=B/('job'+str(job));assert not (j/phase).exists();p=subprocess.Popen([PY,'-u','-B',str(B/'e2_h1_phase_worker_v1.py'),'--job',str(job),'--phase',phase],cwd=B,env=env(job),stdout=(j/(phase+'_worker.log')).open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(j/(phase+'_WORKER_STARTED.json'),ident(p.pid));return p
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
def collect(job,phase,p):
 j=B/('job'+str(job));out=j/phase;v=dict(job=job,phase=phase,worker=ident(p.pid),returncode=p.poll(),final=read(out/'FINAL.json'),latest_save=read(out/'latest_complete.json'),native_CPU=read(j/'native/NATIVE_ALL_ROWS_CPU_ADMITTED.json'),errors=[dict(path=str(q),value=read(q)) for q in out.glob('WORKER_ORIGINAL_ERROR*.json')])
 if p.poll() is not None:
  receipt=j/(phase+'_WORKER_EXIT_ACTUAL.json')
  if not receipt.exists():put(receipt,dict(epoch=time.time(),pid=p.pid,returncode=p.returncode,actual_waited=True,job=job,phase=phase))
  v['exit']=read(receipt)
 return v
def main(config):
 token=config['token'].encode();put(B/'NODE_IDENTITY.json',ident(os.getpid()));workers=OWN_WORKERS;phases=OWN_PHASES
 for i in (0,1):phases[i]='native';workers[i]=spawn(i,'native')
 last=time.time();granted=False;lastreply={};begun=time.time()
 while True:
  rows={str(i):collect(i,phases[i],p) for i,p in workers.items()}
  for i in (0,1):
   j=B/('job'+str(i));r=rows[str(i)]
   if phases[i]=='native' and r['returncode'] is not None and not (j/'NATIVE_CPU_COMMAND_ACTUAL.json').exists():
    if r['returncode']!=0 or not r['final'] or r['errors']:
     put(j/'NATIVE_CPU_COMMAND_ACTUAL.json',dict(epoch=time.time(),not_run_native_worker_rejected=True,original_state=r))
     if i==0:raise AssertionError(r)
     continue
    p=subprocess.run([PY,'-B',str(B/'verify_e2_h1_native_CPU_v1.py'),'--job',str(i)],cwd=B,env={**env(i),'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True);put(j/'NATIVE_CPU_COMMAND_ACTUAL.json',dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if i==0:assert p.returncode==0,p.stderr
  rows={str(i):collect(i,phases[i],p) for i,p in workers.items()};body=json.dumps(dict(run_id=config['run_id'],epoch=time.time(),rows=rows)).encode();reply={}
  try:
   request=urllib.request.Request('http://10.24.4.210:'+str(PORT)+'/',data=body,headers={'X-Own-Signature':hmac.new(token,body,hashlib.sha256).hexdigest(),'Content-Type':'application/json'})
   with urllib.request.urlopen(request,timeout=15) as response:raw=response.read();sig=response.headers['X-Own-Signature']
   assert hmac.compare_digest(sig,hmac.new(token,raw,hashlib.sha256).hexdigest());reply=json.loads(raw);last=time.time();lastreply=reply
  except BaseException:put(B/'NODE_CONTROL_LAST_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),own_save_stop_after120s=True))
  if reply.get('go') and not granted:
   assert rows['0']['native_CPU']['passed'] and rows['0']['returncode']==0;go=reply['go'];granted=True
   for phase in ('precheck128','precheck20k','production'):put(B/'job0'/('GO_'+phase.upper()+'.json'),go)
   phases[0]='precheck128';workers[0]=spawn(0,phases[0])
  if granted and workers[0].poll() is not None:
   row=collect(0,phases[0],workers[0]);assert row['returncode']==0 and row['final'] and row['final']['passed'] and not row['errors'],row
   phase=phases[0]
   if phase in ('precheck128','precheck20k'):
    assert time.time()<lastreply['go']['save_deadline']-180
    phases[0]='precheck20k' if phase=='precheck128' else 'production';workers[0]=spawn(0,phases[0])
  stop=reply.get('stop') or time.time()-last>120 or time.time()-begun>7200
  if stop:
   for i,p in workers.items():
    if p.poll() is None:
     q=B/('job'+str(i))/phases[i];q.mkdir(exist_ok=True)
     if not (q/'STOP_AFTER_SAVE.json').exists():put(q/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite control stop; no signals'))
  put(B/'NODE_CURRENT.json',dict(epoch=time.time(),rows=rows,reply=reply,granted_E2_only=granted,H1_PPO_forbidden=True))
  if granted and phases[0]=='production' and all(p.poll() is not None for p in workers.values()):break
  if stop and all(p.poll() is not None for p in workers.values()):break
  time.sleep(3)
 rows={str(i):collect(i,phases[i],p) for i,p in workers.items()};put(B/'NODE_FINAL.json',dict(epoch=time.time(),rows=rows,E2_production_complete=phases[0]=='production' and bool(rows['0']['final']),H1_native_only=True));return rows
def run(config):
 try:main(config)
 except BaseException:
  error=traceback.format_exc();put(B/'NODE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_auto_retry=True))
  for i,p in OWN_WORKERS.items():
   if p.poll() is None:
    out=B/('job'+str(i))/OWN_PHASES[i];out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own node exception; durable save-stop, no kill'))
  for p in OWN_WORKERS.values():p.wait()
  rows={str(i):collect(i,OWN_PHASES[i],p) for i,p in OWN_WORKERS.items()};put(B/'NODE_FAILURE_ALL_OWN_CHILDREN_EXIT_ACTUAL.json',dict(epoch=time.time(),rows=rows,all_own_children_actual_waited=True))
  token=config['token'].encode();body=json.dumps(dict(run_id=config['run_id'],epoch=time.time(),rows=rows,node_terminal_after_actual_children_exit=True,node_original_error=True)).encode()
  try:
   request=urllib.request.Request('http://10.24.4.210:'+str(PORT)+'/',data=body,headers={'X-Own-Signature':hmac.new(token,body,hashlib.sha256).hexdigest(),'Content-Type':'application/json'})
   with urllib.request.urlopen(request,timeout=15) as response:response.read()
  except BaseException:put(B/'NODE_FINAL_HANDOFF_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_claim_source_canonical_closed=True))
  raise
 finally:put(B/'NODE_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid()))
if __name__=='__main__':
 config=json.loads(sys.stdin.readline());assert not (B/'NODE_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='node72')),flush=True)
 else:
  os.setsid();f=os.open(str(B/'NODE_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);run(config)
