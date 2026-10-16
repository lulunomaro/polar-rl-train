"""Unused WAVE repair: native first; single-expert learning only after prior owner handoff."""
from pathlib import Path
import argparse,os,sys,json,time,subprocess,threading,http.server,urllib.request,hmac,hashlib,traceback
B=Path(__file__).resolve().parent;PORT=29717;RUN=B/'job3/run';J=B/'job3'
CANON=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')

def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)

def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
 except psutil.Error:return None

def node(config):
 py='/home/lc01/Zonglin Li/zonglin2/run-python.sh';token=config['token'].encode();task=json.loads((J/'TASK.json').read_bytes());v=dict(os.environ)
 for k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):v.pop(k,None)
 for name in ('home','tmp','cache','config','data'):(J/name).mkdir(exist_ok=True)
 v.update(CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(J/'home'),TMPDIR=str(J/'tmp'),XDG_CACHE_HOME=str(J/'cache'),XDG_CONFIG_HOME=str(J/'config'),XDG_DATA_HOME=str(J/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 p=subprocess.Popen([py,'-u','-B',str(B/'expert_independent_worker_v3.py'),'--job','3'],cwd=B,env=v,stdout=(J/'worker.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(J/'WORKER_STARTED.json',ident(p.pid));last=time.time();cpu_done=False
 while True:
  if (RUN/'NATIVE120_COMPLETE.json').exists() and not cpu_done and p.poll() is None:
   cpu_done=True;rr=subprocess.run([py,'-B',str(B/'verify_independent_native_cpu_gate_v1.py'),'--job','3'],cwd=B,env={**os.environ,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True);put(J/'NATIVE_CPU_COMMAND_ACTUAL.json',dict(epoch=time.time(),returncode=rr.returncode,stdout=rr.stdout,stderr=rr.stderr))
   if rr.returncode:put(J/'NATIVE_CPU_REJECTED.json',dict(epoch=time.time(),returncode=rr.returncode));put(RUN/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='New WAVE native CPU rejected; no automatic retry'))
  row=dict(epoch=time.time(),job=3,worker=ident(p.pid),returncode=p.poll())
  for name in ('NATIVE120_COMPLETE.json','INDEPENDENT_NATIVE_CPU_ADMITTED.json','PPO_POSITIVE_CURRENT.json','latest_complete.json','FINAL.json'):
   q=RUN/name
   if q.exists():row[name]=json.loads(q.read_bytes())
  for name in ('WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','WORKER_ORIGINAL_ERROR.json','NATIVE_CPU_REJECTED.json'):
   q=J/name
   if q.exists():row[name]=json.loads(q.read_bytes())
  if p.poll() is not None:
   q=J/'WORKER_EXIT_ACTUAL.json'
   if not q.exists():put(q,dict(epoch=time.time(),pid=p.pid,returncode=p.returncode,actual_waited=True))
   row['exit']=json.loads(q.read_bytes())
  body=json.dumps(dict(run_id=config['run_id'],epoch=time.time(),row=row)).encode();reply={}
  try:
   req=urllib.request.Request('http://10.24.4.210:'+str(PORT)+'/',data=body,headers={'X-Own-Signature':hmac.new(token,body,hashlib.sha256).hexdigest()})
   with urllib.request.urlopen(req,timeout=15) as z:raw=z.read();sig=z.headers['X-Own-Signature']
   assert hmac.compare_digest(sig,hmac.new(token,raw,hashlib.sha256).hexdigest());reply=json.loads(raw);last=time.time()
  except BaseException:put(B/'NODE_CONTROL_LAST_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()))
  if reply.get('go') and not (RUN/'GO_LEARN.json').exists():put(RUN/'GO_LEARN.json',reply['go'])
  if (reply.get('stop') or time.time()-last>120) and RUN.exists() and not (RUN/'STOP_AFTER_SAVE.json').exists():put(RUN/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite source owner unavailable; complete own save and stop'))
  put(B/'NODE_CURRENT.json',dict(epoch=time.time(),row=row,reply=reply))
  if p.poll() is not None:break
  time.sleep(3)
 put(B/'NODE_FINAL.json',dict(epoch=time.time(),row=row))

def owner(config):
 import fcntl
 token=config['token'].encode();state={};go=None;stop=False;locks=[];active=None;started=time.time()
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   b=self.rfile.read(int(self.headers['Content-Length']))
   if not hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,b,hashlib.sha256).hexdigest()):self.send_error(403);return
   x=json.loads(b);assert x['run_id']==config['run_id'] and abs(time.time()-x['epoch'])<60;state['row']=x['row'];state['last']=time.time();raw=json.dumps(dict(go=go,stop=stop)).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,raw,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(raw)
 server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();put(B/'OWNER_IDENTITY.json',ident(os.getpid()))
 def settle(end=False):
  nonlocal active
  c=json.loads(CANON.read_bytes());assert c['active_segment']['owner_parent_pid']==os.getpid();a=c['active_segment'];upper=state['row'].get('exit',{}).get('epoch',time.time());dt=upper-a['accounted_through_epoch'];assert dt>=0;a['charged_seconds']=a.get('charged_seconds',0.)+dt;a['accounted_through_epoch']=upper;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt
  if end:a['ended_epoch']=upper;a['actual_child_exit']=state['row']['exit'];c['completed_segments'].append(a);c['active_segment']=None
  assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5;put(CANON,c);active=None if end else a
 try:
  while True:
   row=state.get('row',{});terminal=row.get('returncode') is not None
   if row.get('INDEPENDENT_NATIVE_CPU_ADMITTED.json',{}).get('passed') and go is None and not terminal:
    # Existing two-expert cohort owns both original locks until it exits. Do not clear or steal them.
    try:
     for q in (CANON.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
      f=q.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
     for f in locks:f.close()
     locks=[]
    if len(locks)==2:
     c=json.loads(CANON.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>1800+9400.860692501068+64800
     now=time.time();active=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_WAVE35_INDEPENDENT_REVIEWED_EPISODE_FIRST1800_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,source_scope='New unused WAVE episode-reader repair; old WAVE pre-native failure never charged or replayed',max_parent_seconds=1800,charge_contract='One distinct WAVE actual admitted parent interval through own child exit; prior independent cohort already settled; no new budget or ledger');c['active_segment']=active;put(CANON,c);go=dict(learning_started_epoch=now,save_deadline=now+1740,max_parent_seconds=1800,independent_expert=True,original_canonical_owner=os.getpid());put(B/'GO_ACTUAL.json',go)
   if active:settle()
   if time.time()-started>3500 and go is None:stop=True
   if state.get('last') and time.time()-state['last']>120:stop=True
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),row=row,go=go,stop=stop,wait_prior_original_owner_handoff=go is None,charged=active is not None))
   if terminal:
    if active:settle(True)
    put(B/'OWNER_FINAL.json',dict(epoch=time.time(),row=row,go=go,old_failure_preserved=True,original_cost_settled=True));break
   time.sleep(3)
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active is not None));stop=True
  while state.get('row',{}).get('returncode') is None:
   if active:settle()
   time.sleep(5)
  if active:settle(True)
  raise
 finally:
  for f in locks:fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),original_cost_settled=active is None));server.shutdown()

def main():
 p=argparse.ArgumentParser();p.add_argument('--role',choices=('owner','node72'),required=True);a=p.parse_args();config=json.loads(sys.stdin.readline());pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,role=a.role,root=str(B))),flush=True);return
 os.setsid();f=os.open(str(B/(a.role+'_stdout_stderr.log')),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
 if a.role=='owner':owner(config)
 else:node(config)
if __name__=='__main__':main()
