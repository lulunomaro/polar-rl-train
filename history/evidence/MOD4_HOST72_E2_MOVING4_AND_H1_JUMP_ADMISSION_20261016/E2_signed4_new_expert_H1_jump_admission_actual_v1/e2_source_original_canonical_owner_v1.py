"""Wait actual old owner's natural lock release; one E2 interval, H1 native remains free."""
from pathlib import Path
import os,sys,json,time,fcntl,threading,http.server,hmac,hashlib,traceback
B=Path(__file__).resolve().parent;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');PORT=29730
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def ident(pid):
 import psutil
 p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
def owner(config):
 state={'rows':{},'go':None,'stop':False,'last':time.time()};token=config['token'].encode();mutex=threading.Lock();locks=[];active=False;begun=time.time()
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    body=self.rfile.read(int(self.headers['Content-Length']));assert len(body)<2000000 and hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,body,hashlib.sha256).hexdigest());v=json.loads(body);assert v['run_id']==config['run_id'] and abs(time.time()-v['epoch'])<60
    with mutex:state['rows']=v['rows'];state['last']=time.time();state['node_terminal']=v.get('node_terminal_after_actual_children_exit',False);state['node_error']=v.get('node_original_error',False);reply=dict(go=state['go'],stop=state['stop'])
    raw=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,raw,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(raw)
   except BaseException:self.send_error(403)
 server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();put(B/'OWNER_IDENTITY.json',ident(os.getpid()))
 def account(end=False):
  nonlocal active
  c=json.loads(C.read_bytes());a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();now=time.time();dt=now-a['accounted_through_epoch'];assert dt>=0;a['accounted_through_epoch']=now;a['charged_seconds']+=dt;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt
  if end:a['ended_epoch']=now;a['actual_remote_child_exit_received']=state['rows'].get('0');c['completed_segments'].append(a);c['active_segment']=None;active=False
  assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5;put(C,c)
 try:
  put(B/'HUMAN_E2_TRAIN_H1_NATIVE_ONLY_ACCOUNTING_CONTRACT.json',dict(epoch=time.time(),human_selected='E2旋转平移扩速；先做跳跃准入，自救随后',E2_max_parent_load_learn_save_exit_seconds=2700,includes_discarded128x2_20kx4=True,H1_GPU1_native_only_no_learning_cost=True,no_new_budget_or_ledger=True,existing_CURB35_owner480021_natural_exit_before_locks=True))
  while True:
   if not locks:
    held=[]
    try:
     for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
      f=p.open('rb+');held.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
     c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7;locks=held
    except BlockingIOError:
     for f in reversed(held):fcntl.flock(f,fcntl.LOCK_UN);f.close()
   with mutex:rows=dict(state['rows'])
   x=rows.get('0',{});errors=bool(x.get('errors') or (x.get('returncode') not in (None,0)) or state.get('node_error'))
   if errors:state['stop']=True
   n=rows.get('0',{});ready=n.get('native_CPU',{});ready=ready or {}
   if locks and ready.get('passed') and n.get('returncode')==0 and not active and state['go'] is None and not state['stop']:
    c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['remaining_training_seconds']>2700+9400.860692501068+64800;now=time.time();c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_HOST72_E2_WORLD_MOVING4_FIRST2700_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_seconds=0.,charge_contract='One E2 parent interval admission/load,discarded128x2,discarded20kx4,fresh production/save/wait-exit; H1 native and old CURB35 not recharged',remote_root=config['target_root'],max_parent_seconds=2700);put(C,c);active=True;state['go']=dict(parent_learning_started_epoch=now,save_deadline=now+2400,nominal_end_epoch=now+2700,exit_headroom_seconds=300,original_owner_pid=os.getpid(),max_parent_seconds=2700)
   if active:account()
   if time.time()-state['last']>120 or time.time()-begun>7200:state['stop']=True
   production_done=n.get('phase')=='production' and n.get('returncode') is not None
   if production_done and active:account(True)
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),rows=rows,go=state['go'],stop=state['stop'],original_two_fcntl_held=bool(locks),original_canonical_active=active,waiting_original_CURB35_natural_handoff=not bool(locks)))
   if production_done or (state['stop'] and state.get('node_terminal') and rows and all(x.get('returncode') is not None for x in rows.values())):break
   time.sleep(3)
  if active:account(True)
  put(B/'OWNER_FINAL.json',dict(epoch=time.time(),rows=rows,go=state['go'],original_canonical_settled=True,E2_production_passed=bool(n.get('final')) and not errors,H1_native_only=True,no_automatic_next_window=True))
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active));state['stop']=True
  while active:
   with mutex:rows=state['rows']
   n=rows.get('0',{})
   if state.get('node_terminal') and n.get('returncode') is not None:account(True);break
   account();time.sleep(3)
  raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),canonical_settled=not active,own_locks_released=True));server.shutdown()
if __name__=='__main__':
 config=json.loads(sys.stdin.readline());assert not (B/'OWNER_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='source_owner')),flush=True)
 else:
  os.setsid();f=os.open(str(B/'OWNER_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);owner(config)
