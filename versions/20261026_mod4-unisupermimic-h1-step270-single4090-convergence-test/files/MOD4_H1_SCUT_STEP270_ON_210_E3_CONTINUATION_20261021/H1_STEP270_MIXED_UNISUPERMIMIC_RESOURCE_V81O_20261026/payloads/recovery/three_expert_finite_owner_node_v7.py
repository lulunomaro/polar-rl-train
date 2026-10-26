"""Three independent experts, one original canonical writer; failure isolated per expert."""
from pathlib import Path
import os,sys,json,time,threading,http.server,hashlib,hmac,fcntl,traceback
import three_expert_helpers_v2 as b
B=Path(__file__).resolve().parent;C=b.C;PORT=b.PORT;put=b.put;read=b.read;ident=b.ident;terminal=b.terminal
def owner(cfg):
 specs=cfg['experts'];assert set(specs)=={'curb','e2','recovery'};b.validate_payload(specs['curb']);token=cfg['token'].encode();shared=dict(remote={},last={k:time.time() for k in ('e2','recovery')},go={},stop=False);mutex=threading.Lock();locks=[];active=False;server=None;p=None;children=[];phase='native';native=None;local_error=None;rows={};started=time.time()
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    n=int(self.headers['Content-Length']);assert 0<n<3000000;raw=self.rfile.read(n);assert hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,raw,hashlib.sha256).hexdigest());v=json.loads(raw);assert v['run_id']==cfg['run_id'] and abs(v['epoch']-time.time())<60;row=v['row'];key=row['key'];assert key in ('e2','recovery')
    with mutex:
     previous=shared['remote'].get(key,{})
     if terminal(row):row['owner_received_terminal_epoch']=previous.get('owner_received_terminal_epoch',time.time())
     shared['remote'][key]=row;shared['last'][key]=time.time();reply=dict(go=shared['go'].get(key),stop=shared['stop'])
    body=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,body,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(body)
   except BaseException:self.send_error(403)
 def account(end=False):
  nonlocal active
  c=read(C);a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();c,a=b.charge_values(c,a,shared['go'],rows,time.time());c['active_segment']=a
  if end:assert all(terminal(rows[k]) for k in specs);a['ended_epoch']=time.time();a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None;active=False
  put(C,c)
 try:
  put(B/'OWNER_IDENTITY.json',ident(os.getpid()));put(B/'HUMAN_THREE_INDEPENDENT_EXPERTS_FINITE_ACCOUNTING_CONTRACT.json',dict(epoch=time.time(),human='那赶紧充分利用啊',three_independent_experts_no_NCCL=True,one_original_canonical_writer=True,caps={k:s['max_parent_seconds'] for k,s in specs.items()},headroom300=True,native_and_CPU0PPO_uncharged=True,sum_each_actual_production_load_learn_save_SDKclose_childwait_terminal_interval=True,failed_expert_does_not_stop_other_independent_experts=True,no_new_budget_ledger_refund_tail_or_clearactive=True));server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();p=b.spawn(specs['curb'],'native');children.append(p)
  while True:
   own={**b.state(specs['curb'],phase,p),**dict(native_CPU=native,manifest_SHA=specs['curb']['manifest_SHA'],native_GPU_waited_EXIT0=native is not None,original_error=local_error is not None)}
   if local_error:own.update(terminal_all_own_children_waited=p is None or p.poll() is not None,returncode=p.returncode if p else 1)
   elif p and p.poll() is not None:
    try:
     assert own['returncode']==0 and own['final'] and own['final']['passed'] and not own['errors'],own
     if phase=='native':native=b.native_CPU(specs['curb']);p=None;phase='ready';own.update(phase='ready',worker=None,returncode=None,native_CPU=native,native_GPU_waited_EXIT0=True)
     else:own.update(terminal_all_own_children_waited=True)
    except BaseException:
     local_error=traceback.format_exc();put(B/'CURB_ORIGINAL_ERROR_ISOLATED.json',dict(epoch=time.time(),error=local_error,other_experts_not_stopped=True));own.update(original_error=True,terminal_all_own_children_waited=True,returncode=own['returncode'] if own['returncode'] is not None else 1)
   with mutex:remote={k:dict(v) for k,v in shared['remote'].items()}
   rows=dict(curb=own,e2=remote.get('e2',{}),recovery=remote.get('recovery',{}))
   for key,spec in specs.items():
    if not b.valid_ready(rows[key],spec) or key in shared['go'] or shared['stop']:continue
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
     locks=attempted;c=read(C);assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>sum(s['max_parent_seconds'] for s in specs.values())+9400.860692501068+64800
    if not active:
     c=read(C);assert c['active_segment'] is None;now=time.time();c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_THREE_INDEPENDENT_HEALTHY_BLOCKS_CORRECTED_E3_V7_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Single original writer sums three distinct actual production parent intervals; each nativeCPU uncharged.');put(C,c);active=True
    now=time.time();shared['go'][key]=dict(learning_started_epoch=now,save_deadline=now+spec['max_parent_seconds']-300,nominal_end_epoch=now+spec['max_parent_seconds'],max_parent_seconds=spec['max_parent_seconds'],exit_headroom_seconds=300,source_SHA=spec['source_SHA'],source_native_CPU_SHA=rows[key]['native_CPU']['SHA'],original_owner_pid=os.getpid(),original_owner_creation=ident(os.getpid())['creation'],run_id=cfg['run_id']);account()
    if key=='curb':put(B/'GO_PRODUCTION_ACTUAL.json',shared['go'][key]);p=b.spawn(spec,'production');children.append(p);phase='production'
   if active:account()
   if any(time.time()-shared['last'][k]>120 and not terminal(rows[k]) for k in ('e2','recovery')) or time.time()-started>10800:shared['stop']=True
   if shared['stop']:
    if p and p.poll() is None:
     out=b.outdir('curb',phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite transport timeout, save validprefix'))
    elif p is None:rows['curb'].update(terminal_all_own_children_waited=True,returncode=1)
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),rows=rows,go=shared['go'],stop=shared['stop'],original_canonical_active=active,original_two_fcntl_held=bool(locks),per_expert_failure_isolation=True))
   if all(terminal(rows[k]) for k in specs):
    if active:account(True)
    put(B/'COHORT_FINAL.json',dict(epoch=time.time(),rows=rows,go=shared['go'],original_cost_settled=True,no_automatic_extra_window=True));break
   time.sleep(3)
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active));shared['stop']=True
  if p and p.poll() is None:
   out=b.outdir('curb',phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own source exception saved-stop'))
  while True:
   own=b.state(specs['curb'],phase,p)
   if p is None or p.poll() is not None:own.update(terminal_all_own_children_waited=True,returncode=p.returncode if p else 1)
   rows=dict(curb=own,e2=shared['remote'].get('e2',{}),recovery=shared['remote'].get('recovery',{}))
   if active:account()
   if all(terminal(rows[k]) for k in specs):
    if active:account(True)
    break
   time.sleep(3)
  raise
 finally:
  for child in children:child.wait()
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),original_cost_settled=not active,original_two_fcntl_released=True))
  if server:server.shutdown()
def main():
 cfg=json.loads(sys.stdin.readline());assert cfg['role'] in ('owner','node') and not (B/(cfg['role']+'_CONSOLE.log')).exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role=cfg['role'])),flush=True);return
 os.setsid();f=os.open(str(B/(cfg['role']+'_CONSOLE.log')),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
 if cfg['role']=='owner':owner(cfg)
 else:b.node(cfg)
if __name__=='__main__':main()
