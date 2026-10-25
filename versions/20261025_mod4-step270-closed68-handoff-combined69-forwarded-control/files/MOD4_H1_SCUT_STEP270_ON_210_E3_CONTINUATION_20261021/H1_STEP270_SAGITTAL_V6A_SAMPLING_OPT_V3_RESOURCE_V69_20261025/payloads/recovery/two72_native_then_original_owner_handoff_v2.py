"""One finite coordinator for two independent72 experts; original owner handoff first."""
from pathlib import Path
import os,sys,json,time,threading,http.server,hmac,hashlib,fcntl,traceback
import three_expert_helpers_v2 as b
B=Path(__file__).resolve().parent;C=b.C;put=b.put
def owner(cfg):
 specs=cfg['experts'];assert set(specs)=={'e2','recovery'} and all(x['max_parent_seconds']==3600 and x['exit_headroom_seconds']==300 for x in specs.values());token=cfg['token'].encode();shared=dict(remote={},last={k:time.time() for k in specs},go={},stop=False);mutex=threading.Lock();locks=[];active=False;server=None;rows={};started=time.time()
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    n=int(self.headers['Content-Length']);assert 0<n<3000000;raw=self.rfile.read(n);assert hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,raw,hashlib.sha256).hexdigest());v=json.loads(raw);assert v['run_id']==cfg['run_id'] and abs(v['epoch']-time.time())<60;row=v['row'];key=row['key'];assert key in specs
    with mutex:
     previous=shared['remote'].get(key,{})
     if b.terminal(row):row['owner_received_terminal_epoch']=previous.get('owner_received_terminal_epoch',time.time())
     shared['remote'][key]=row;shared['last'][key]=time.time();reply=dict(go=shared['go'].get(key),stop=shared['stop'])
    body=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,body,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(body)
   except BaseException:self.send_error(403)
 def account(end=False):
  nonlocal active
  c=b.read(C);a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();c,a=b.charge_values(c,a,shared['go'],rows,time.time());c['active_segment']=a
  if end:assert all(b.terminal(rows[k]) for k in specs);a['ended_epoch']=time.time();a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None;active=False
  put(C,c)
 try:
  put(B/'OWNER_IDENTITY.json',b.ident(os.getpid()));put(B/'ORIGINAL_ACCOUNTING_HANDOFF_CONTRACT.json',dict(epoch=time.time(),existing_human_three_independent_experts_continuous_use_and_master_healthy_same_stage_blocks=True,wait_actual_current_CURB275_original_activeNone_twofcntl_before_any_GO=True,new_native_CPU0PPO_not_charged=True,independent_each3600_headroom300_sum_real_load_learn_save_SDKclose_childwait_terminal=True,original1188000_7extensions_no_increase=True,no_other_current_owner_or_job_mutation=True));server=http.server.ThreadingHTTPServer(('10.24.4.210',b.PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
  while True:
   if not active and not shared['go'] and not shared['remote'] and time.time()-started>120:
    put(B/'EMPTY_UNOBSERVED_NODE_ADMISSION_EXPIRED_NO_GO.json',dict(epoch=time.time(),no_observed_node_status=True,no_GO_no_canonical_write_no_original_locks=True,not_claiming_unobserved_remote_child_out=True));break
   with mutex:rows={k:dict(shared['remote'].get(k,{})) for k in specs}
   for key,spec in specs.items():
    if not b.valid_ready(rows[key],spec) or key in shared['go'] or shared['stop']:continue
    if not locks:
     c=b.read(C)
     if c['active_segment'] is not None:continue
     attempt=[]
     try:
      for q in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
       f=q.open('rb+');attempt.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
     except BlockingIOError:
      for f in attempt:f.close()
      continue
     locks=attempt;c=b.read(C);assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>7200+9400.860692501068+64800
    if not active:
     c=b.read(C);assert c['active_segment'] is None;now=time.time();c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_TWO72_CLOSED152_90_HEALTHY_SAME_SCOPE_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Single original writer only after actual CURB275 owner handoff; sum independent experts actual intervals once.');put(C,c);active=True
    now=time.time();shared['go'][key]=dict(learning_started_epoch=now,save_deadline=now+3300,nominal_end_epoch=now+3600,max_parent_seconds=3600,exit_headroom_seconds=300,source_SHA=spec['source_SHA'],source_native_CPU_SHA=rows[key]['native_CPU']['SHA'],original_owner_pid=os.getpid(),original_owner_creation=b.ident(os.getpid())['creation'],run_id=cfg['run_id']);account()
   if active:account()
   if any(time.time()-shared['last'][k]>120 and not b.terminal(rows[k]) for k in specs) or time.time()-started>10800:shared['stop']=True
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),rows=rows,go=shared['go'],stop=shared['stop'],original_canonical_active=active,original_two_fcntl_held=bool(locks),not_other_expert_success_from_one_ready=True))
   if all(b.terminal(rows[k]) for k in specs):
    if active:account(True)
    put(B/'COHORT_FINAL.json',dict(epoch=time.time(),rows=rows,go=shared['go'],original_cost_settled=True,no_automatic_extra_window=True));break
   time.sleep(3)
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active));shared['stop']=True
  while True:
   with mutex:rows={k:dict(shared['remote'].get(k,{})) for k in specs}
   if active:account()
   if all(b.terminal(rows[k]) for k in specs):
    if active:account(True)
    break
   time.sleep(3)
  raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),own_original_two_fcntl_were_held=bool(locks),own_original_two_fcntl_released_if_held=True,original_cost_settled=not active))
  if server:server.shutdown()
if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert cfg['role'] in ('owner','node');pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role=cfg['role'])),flush=True)
 else:
  os.setsid();f=os.open(str(B/(cfg['role']+'_CONSOLE.log')),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
  if cfg['role']=='owner':owner(cfg)
  else:b.node(cfg)
