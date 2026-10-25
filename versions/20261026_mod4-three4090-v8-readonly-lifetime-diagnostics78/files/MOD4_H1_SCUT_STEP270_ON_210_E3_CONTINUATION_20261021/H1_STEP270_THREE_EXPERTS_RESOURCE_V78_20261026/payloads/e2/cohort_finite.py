"""Two existing expert scopes: own native/CPU, then original summed accounting.

Never touches the prior H1 job. One source original ledger owner; no next block.
"""
from pathlib import Path
import os,sys,json,time,hashlib,hmac,http.server,threading,urllib.request,subprocess,traceback,fcntl
B=Path(__file__).resolve().parent;J=B/'job0';PORT=29736;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def put(p,x):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(x,indent=2));q.replace(p)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:return None
def environment(cfg,cpu=False):
 v=dict(os.environ)
 for key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):v.pop(key,None)
 for n in ('home','tmp','cache','config','data'):(J/n).mkdir(exist_ok=True)
 v.update(CUDA_VISIBLE_DEVICES='' if cpu else cfg['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(J/'home'),TMPDIR=str(J/'tmp'),XDG_CACHE_HOME=str(J/'cache'),XDG_CONFIG_HOME=str(J/'config'),XDG_DATA_HOME=str(J/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');return v
def outdir(key,phase):return J/('production_only' if key=='curb' else 'production') if phase=='production' else J/('native20k_then_production' if key=='curb' else 'native')
def spawn(cfg,phase):
 key=cfg['key'];assert not outdir(key,phase).exists();args=[cfg['python'],'-u','-B',str(B/('native_admission_worker.py' if phase=='native' else 'production_worker.py'))]
 import psutil,shutil
 snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in snapshot.splitlines() if cfg['GPU_UUID'] in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3;put(J/(phase+'_ACTUAL_GPU_RAM_DURABLE_RESOURCE.json'),dict(epoch=time.time(),actual_GPU_line=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(B).free,no_other_process_action=True))
 if key=='curb':
  if phase=='native':args+=['--mode','native20k_then_production']
 else:args+=['--job','0','--phase','native' if phase=='native' else 'production']
 p=subprocess.Popen(args,cwd=B,env=environment(cfg),stdout=(J/(phase+'_WORKER.log')).open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(J/(phase+'_STARTED_ACTUAL.json'),ident(p.pid));return p
def state(cfg,phase,p):
 out=outdir(cfg['key'],phase);rc=p.poll() if p else None;exitrow=J/(phase+'_WAITED_EXIT_ACTUAL.json')
 if p and rc is not None and not exitrow.exists():put(exitrow,dict(epoch=time.time(),pid=p.pid,returncode=rc,actual_waited=True))
 return dict(key=cfg['key'],phase=phase,worker=ident(p.pid) if p else None,returncode=rc,final=read(out/'FINAL.json'),latest_save=read(out/'latest_complete.json'),actual_exit=read(exitrow),errors=[str(q) for q in out.glob('*ORIGINAL_ERROR*.json')])
def native_CPU(cfg):
 p=subprocess.Popen([cfg['python'],'-u','-B',str(B/'native_CPU.py'),'--job','0'],cwd=B,env=environment(cfg,True),stdout=(J/'native_CPU.log').open('xb'),stderr=subprocess.STDOUT,close_fds=True);put(J/'native_CPU_STARTED_ACTUAL.json',ident(p.pid));rc=p.wait();put(J/'native_CPU_WAITED_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=rc,actual_waited=True));assert rc==0;out=outdir(cfg['key'],'native');path=out/('INDEPENDENT_NATIVE_CPU_ADMITTED.json' if cfg['key']=='curb' else 'NATIVE_ALL_ROWS_CPU_ADMITTED.json');v=read(path);assert v and v['passed'] and v['source_SHA']==cfg['source_SHA'] and v['controls']==144 and v['callbacks']==576;return dict(value=v,path=str(path),SHA=H(path),actual_CPU_waited_EXIT0=True)
def validate_payload(cfg):
 manifest=B/'CONTINUATION_COMPLETE_MANIFEST_V2.json';assert H(manifest)==cfg['manifest_SHA'];m=read(manifest);assert m['source_SHA']==cfg['source_SHA'] and m['key']==cfg['key']
 for row in m['files']:
  p=B/row['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==row['bytes'] and H(p)==row['SHA'],row['relative']
def valid_ready(row,cfg):
 n=row.get('native_CPU') or {};v=n.get('value') or {};return bool(row.get('phase')=='ready' and row.get('native_GPU_waited_EXIT0') and n.get('actual_CPU_waited_EXIT0') and n.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest() and v.get('passed') and v.get('source_SHA')==cfg['source_SHA'] and v.get('controls')==144 and v.get('callbacks')==576 and row.get('manifest_SHA')==cfg['manifest_SHA'] and not row.get('original_error'))
def send(cfg,row):
 token=cfg['token'].encode();raw=json.dumps(dict(epoch=time.time(),run_id=cfg['run_id'],row=row)).encode();assert len(raw)<2000000;req=urllib.request.Request('http://10.24.4.210:'+str(PORT)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()})
 with urllib.request.urlopen(req,timeout=15) as response:body=response.read();sig=response.headers['X-Own-Signature']
 assert hmac.compare_digest(sig,hmac.new(token,body,hashlib.sha256).hexdigest());return json.loads(body)
def terminal(row):return bool(row.get('terminal_all_own_children_waited') and row.get('returncode') is not None)
def charge_values(c,active,go,rows,now):
 for key,g in go.items():
  a=active['experts'].setdefault(key,dict(started_epoch=g['learning_started_epoch'],accounted_through_epoch=g['learning_started_epoch'],charged_seconds=0.,max_parent_seconds=2700))
  row=rows.get(key) or {};exitrow=row.get('actual_exit') or {};upper=row.get('owner_received_terminal_epoch',exitrow.get('epoch',now)) if row.get('returncode') is not None else now;upper=max(upper,a['accounted_through_epoch']);dt=upper-a['accounted_through_epoch'];assert dt>=0;a['charged_seconds']+=dt;a['accounted_through_epoch']=upper;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt;active['charged_expert_seconds']+=dt
  if row.get('returncode') is not None:a.update(ended_epoch=upper,actual_returncode=row['returncode'],duration_bound_passed=a['charged_seconds']<=2700)
 active['accounted_through_epoch']=now;assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5;return c,active
def node(cfg):
 validate_payload(cfg);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert B.resolve().is_relative_to(owned);lock=(owned/'state/finite_environment_validation.lock').open('rb+');p=None;phase='waiting_validation_lock';native=None;error=None;go=None;children=[];begun=time.time();last=time.time();row={}
 try:
  while True:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
   except BlockingIOError:
    assert time.time()-begun<3600;put(B/'NODE_CURRENT.json',dict(epoch=time.time(),phase=phase,no_old_H1_stop_or_lock_removal=True));send(cfg,dict(key=cfg['key'],phase=phase));time.sleep(5)
  put(B/'NODE_IDENTITY.json',ident(os.getpid()));p=spawn(cfg,'native');children.append(p);phase='native'
  while True:
   row={**state(cfg,phase,p),**dict(native_CPU=native,manifest_SHA=cfg['manifest_SHA'],native_GPU_waited_EXIT0=native is not None,actual_validation_fcntl_held=True)}
   try:reply=send(cfg,row);last=time.time()
   except BaseException:reply={};put(B/('NODE_CONTROL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
   stop=bool(reply.get('stop') or time.time()-last>120 or time.time()-begun>10800 or (go and time.time()>=go['save_deadline']))
   if p and p.poll() is not None:
    done=state(cfg,phase,p);assert done['returncode']==0 and done['final'] and done['final']['passed'] and not done['errors'],done
    if phase=='native':native=native_CPU(cfg);p=None;phase='ready'
    else:break
   if phase=='ready' and reply.get('go') and go is None:
    assert not stop;go=reply['go'];assert go['source_SHA']==cfg['source_SHA'] and go['max_parent_seconds']==2700 and go['exit_headroom_seconds']==300;put(J/'GO_PRODUCTION.json',go);p=spawn(cfg,'production');children.append(p);phase='production'
   if stop:
    if p and p.poll() is None:out=outdir(cfg['key'],phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite source saved-stop, no signal'))
    elif p is None:raise RuntimeError('Source finite stop before new learning')
   put(B/'NODE_CURRENT.json',dict(epoch=time.time(),row=row,reply=reply));time.sleep(3)
 except BaseException:
  error=traceback.format_exc();put(B/'NODE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_automatic_retry=True))
  if p and p.poll() is None:out=outdir(cfg['key'],phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own exception full-prefix save-stop'))
 finally:
  for child in children:child.wait()
  row={**state(cfg,phase,p),**dict(native_CPU=native,original_error=error is not None,terminal_all_own_children_waited=True,returncode=p.returncode if p else 1)};put(B/'NODE_TERMINAL_ACTUAL.json',dict(epoch=time.time(),row=row));ack=False
  for attempt in range(3):
   try:send(cfg,row);ack=True;break
   except BaseException:put(B/('NODE_TERMINAL_HANDOFF_ORIGINAL_ERROR_'+str(attempt)+'.json'),dict(epoch=time.time(),error=traceback.format_exc()));time.sleep(5)
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put(B/'NODE_EXIT_ACTUAL.json',dict(epoch=time.time(),actual_all_own_children_waited=True,validation_fcntl_released=True,terminal_received_by_source=ack))
 if error:raise RuntimeError('Original node error preserved')
def owner(cfg):
 local=cfg['curb'];remote=cfg['e2'];validate_payload(local);token=cfg['token'].encode();shared=dict(remote={},last_remote=time.time(),stop=False,go={});mutex=threading.Lock();locks=[];p=None;phase='native';native=None;active=False;server=None;children=[];begun=time.time();rows={}
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    size=int(self.headers['Content-Length']);assert 0<size<2000000;raw=self.rfile.read(size);assert hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,raw,hashlib.sha256).hexdigest());v=json.loads(raw);assert v['run_id']==cfg['run_id'] and abs(v['epoch']-time.time())<60
    with mutex:
     row=v['row']
     if terminal(row):row['owner_received_terminal_epoch']=shared['remote'].get('owner_received_terminal_epoch',time.time())
     shared['remote']=row;shared['last_remote']=time.time();reply=dict(go=shared['go'].get('e2'),stop=shared['stop'])
    body=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,body,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(body)
   except BaseException:self.send_error(403)
 def account(end=False):
  nonlocal active
  c=read(C);a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();c,a=charge_values(c,a,shared['go'],rows,time.time());c['active_segment']=a
  if end:assert terminal(rows['curb']) and terminal(rows['e2']);a['ended_epoch']=time.time();a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None;active=False
  put(C,c)
 try:
  put(B/'OWNER_IDENTITY.json',ident(os.getpid()));put(B/'HUMAN_TWO_HEALTHY_SAME_SCOPE_CONTINUATION_ACCOUNTING_CONTRACT.json',dict(epoch=time.time(),human='现在显卡就在空闲为什么不安排任务？',prior_human_three_independent_experts_and_approved_plan_health_overlap=True,engineering_bounded2700_each_sum_actual_distinct_expert_seconds=True,headroom300=True,new_budget_or_curriculum_or_DR_or_reward=False,original_canonical=str(C),wait_actual_old_H1_complete_and_locks_before_new_charge=True));server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();p=spawn(local,'native');children.append(p)
  while True:
   own={**state(local,phase,p),**dict(native_CPU=native,manifest_SHA=local['manifest_SHA'],native_GPU_waited_EXIT0=native is not None)}
   if p and p.poll() is not None:
    assert own['returncode']==0 and own['final'] and own['final']['passed'] and not own['errors'],own
    if phase=='native':native=native_CPU(local);p=None;phase='ready';own=dict(own,phase='ready',worker=None,returncode=None,native_CPU=native,native_GPU_waited_EXIT0=True)
   if phase=='production' and p and p.poll() is not None:own.update(terminal_all_own_children_waited=True)
   with mutex:remote_row=dict(shared['remote'])
   rows=dict(curb=own,e2=remote_row)
   if own.get('original_error') or remote_row.get('original_error'):shared['stop']=True
   for key,spec in (('curb',local),('e2',remote)):
    if not valid_ready(rows[key],spec) or key in shared['go'] or shared['stop']:continue
    if not locks:
     c=read(C)
     if c['active_segment'] is not None:continue
     attempted=[]
     try:
      for q in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
       f=q.open('rb+');attempted.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
     except BlockingIOError:
      for f in attempted:f.close()
      continue
     locks=attempted;c=read(C);assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>5400+9400.860692501068+64800
    if not active:
     c=read(C);now=time.time();assert c['active_segment'] is None;c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_TWO_DISTINCT_CURB35_E2_HEALTHY_CONTINUATIONS_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Sum each new independent expert actual production load/learn/fullsave/SDKclose/child wait-exit. No native/CPU charge, no shared-job wall accounting, no new budget.');put(C,c);active=True
    now=time.time();go=dict(learning_started_epoch=now,save_deadline=now+2400,nominal_end_epoch=now+2700,max_parent_seconds=2700,exit_headroom_seconds=300,source_SHA=spec['source_SHA'],source_native_CPU_SHA=rows[key]['native_CPU']['SHA'],original_owner_pid=os.getpid(),original_owner_creation=ident(os.getpid())['creation'],run_id=cfg['run_id']);shared['go'][key]=go;account()
    if key=='curb':put(B/'GO_PRODUCTION_ACTUAL.json',go);p=spawn(local,'production');children.append(p);phase='production'
   if active:account()
   if time.time()-shared['last_remote']>120 or time.time()-begun>7200:shared['stop']=True
   if shared['stop'] and p and p.poll() is None:out=outdir('curb',phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite coordinator stop; preserve all valid prefixes'))
   if shared['stop'] and p is None:own.update(terminal_all_own_children_waited=True,returncode=1);rows['curb']=own
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),rows=rows,go=shared['go'],stop=shared['stop'],original_canonical_active=active,original_two_fcntl_held=bool(locks)))
   if terminal(rows['curb']) and terminal(rows['e2']):
    if active:account(True)
    put(B/'COHORT_FINAL.json',dict(epoch=time.time(),rows=rows,go=shared['go'],original_cost_settled=True,no_automatic_next_window=True));break
   if shared['stop'] and not active and not shared['go'] and (p is None or p.poll() is not None):put(B/'NO_GRANT_REMOTE_UNOBSERVED_FINITE_EXIT.json',dict(epoch=time.time(),no_PPO_granted_or_charged=True,own_child_actual_waited=True,remote_native_exit_not_falsely_inferred=True));break
   time.sleep(3)
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active));shared['stop']=True
  if p and p.poll() is None:out=outdir('curb',phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own error complete saved-stop, no signals'))
  while True:
   own=state(local,phase,p);remote_row=shared['remote'];rows=dict(curb=own,e2=remote_row)
   if active:account()
   if (p is None or p.poll() is not None) and terminal(remote_row):
    own.update(terminal_all_own_children_waited=True,returncode=own['returncode'] if p else 1);rows['curb']=own
    if active:account(True)
    break
   time.sleep(3)
  raise
 finally:
  for child in children:child.wait()
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),original_canonical_settled=not active,original_two_fcntl_released=True))
  if server:server.shutdown()
def main():
 cfg=json.loads(sys.stdin.readline());role=cfg['role'];assert role in ('owner','node');assert not (B/(role+'_CONSOLE.log')).exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role=role)),flush=True);return
 os.setsid();f=os.open(str(B/(role+'_CONSOLE.log')),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
 if role=='owner':owner(cfg)
 else:node(cfg)
if __name__=='__main__':main()
