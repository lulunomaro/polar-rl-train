"""One healthy same-signed4 E2 continuation, no further curb learning grant."""
from pathlib import Path
import os,sys,json,time,threading,http.server,hmac,hashlib,fcntl,traceback
import cohort_exact_prior_template as b
B=Path(__file__).resolve().parent;C=b.C;PORT=b.PORT
put=b.put;read=b.read;ident=b.ident;terminal=b.terminal
def owner(cfg):
 spec=cfg['e2'];shared=dict(row={},last=time.time(),go=None,stop=False);mutex=threading.Lock();locks=[];active=False;server=None;start=time.time()
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    n=int(self.headers['Content-Length']);assert 0<n<2000000;raw=self.rfile.read(n);token=cfg['token'].encode();assert hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,raw,hashlib.sha256).hexdigest());v=json.loads(raw);assert v['run_id']==cfg['run_id'] and abs(v['epoch']-time.time())<60
    with mutex:
     row=v['row'];assert row['key']=='e2'
     if terminal(row):row['owner_received_terminal_epoch']=shared['row'].get('owner_received_terminal_epoch',time.time())
     shared['row']=row;shared['last']=time.time();reply=dict(go=shared['go'],stop=shared['stop'])
    body=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,body,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(body)
   except BaseException:self.send_error(403)
 def account(end=False):
  nonlocal active
  c=read(C);a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();go={'e2':shared['go']};rows={'e2':shared['row']};c,a=b.charge_values(c,a,go,rows,time.time());c['active_segment']=a
  if end:
   assert terminal(rows['e2']);a['ended_epoch']=time.time();a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None;active=False
  put(C,c)
 try:
  put(B/'OWNER_IDENTITY.json',ident(os.getpid()));put(B/'HUMAN_HEALTHY_E2_CONTINUATION_ACCOUNTING_CONTRACT.json',dict(epoch=time.time(),human_maximum_meaningful_three4090_utilization_and_master_v13_same_stage_health_overlap=True,source_SHA=spec['source_SHA'],same_signed4_worldVpoint5_no_expansion=True,curb_new_learning_not_granted_pending_actual_frozen_results=True,engineering_cap2700_headroom300=True,original_one_canonical_actual_remote_parent_interval_only=True,no_new_budget_or_ledger=True));server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
  while True:
   with mutex:row=dict(shared['row'])
   if row.get('original_error') or time.time()-shared['last']>120 or time.time()-start>7200:shared['stop']=True
   if b.valid_ready(row,spec) and shared['go'] is None and not shared['stop']:
    c=read(C)
    if c['active_segment'] is None:
     attempted=[]
     try:
      for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
       f=p.open('rb+');attempted.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
     except BlockingIOError:
      for f in attempted:f.close()
     else:
      locks=attempted;c=read(C);assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>2700+9400.860692501068+64800;now=time.time();c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_E2_FROM58_PLUS75_SAME4_HEALTHY_CONTINUATION_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='One remote independent E2 actual production load/learn/fullsave/SDKclose/child wait-exit and terminal handoff; nativeCPU0PPO uncharged.');put(C,c);active=True;shared['go']=dict(learning_started_epoch=now,save_deadline=now+2400,nominal_end_epoch=now+2700,max_parent_seconds=2700,exit_headroom_seconds=300,source_SHA=spec['source_SHA'],source_native_CPU_SHA=row['native_CPU']['SHA'],original_owner_pid=os.getpid(),original_owner_creation=ident(os.getpid())['creation'],run_id=cfg['run_id']);put(B/'GO_PRODUCTION_ACTUAL.json',shared['go']);account()
   if active:account()
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),row=row,go=shared['go'],stop=shared['stop'],original_canonical_active=active,original_two_fcntl_held=bool(locks)))
   if terminal(row):
    if active:account(True)
    put(B/'OWNER_FINAL.json',dict(epoch=time.time(),row=row,go=shared['go'],actual_terminal_received=True,original_cost_settled=True,no_automatic_next_window=True));break
   if shared['stop'] and shared['go'] is None:put(B/'NO_GO_FINITE_EXIT_ACTUAL.json',dict(epoch=time.time(),no_PPO_granted_or_charged=True,remote_native_exit_not_falsely_inferred=True));break
   time.sleep(3)
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_cleared=active));shared['stop']=True
  while active:
   account()
   if terminal(shared['row']):account(True);break
   time.sleep(3)
  raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),original_canonical_settled=not active,original_two_fcntl_released=True))
  if server:server.shutdown()
def main():
 cfg=json.loads(sys.stdin.readline());role=cfg['role'];assert role in ('owner','node') and not (B/(role+'_CONSOLE.log')).exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role=role)),flush=True);return
 os.setsid();f=os.open(str(B/(role+'_CONSOLE.log')),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
 if role=='owner':owner(cfg)
 else:b.node(cfg)
if __name__=='__main__':main()
