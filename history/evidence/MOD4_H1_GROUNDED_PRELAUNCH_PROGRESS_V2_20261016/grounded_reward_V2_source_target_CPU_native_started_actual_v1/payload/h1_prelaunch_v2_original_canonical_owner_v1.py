"""One original canonical H1 interval; never opens a second ledger or native case."""
from pathlib import Path
import os,sys,json,time,fcntl,threading,http.server,hmac,hashlib,traceback
B=Path(__file__).resolve().parent
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
PORT=29734
def put(p,v):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
def ident(pid):
 import psutil
 p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
def terminal(row):
 return bool(row.get('node_terminal_after_actual_children_exit') and row.get('actual_all_children_waited') and row.get('returncode') is not None)
def ready(row,cfg):
 n=row.get('native_CPU') or {};raw=json.dumps(n,indent=2).encode();expected=hashlib.sha256(raw).hexdigest()
 return bool(row.get('phase')=='ready' and row.get('native_GPU_returncode')==0 and row.get('native_CPU_returncode')==0 and row.get('native_CPU_report_SHA')==expected and n.get('passed') and n.get('source_SHA')==cfg['source_SHA'] and n.get('controls')==180 and n.get('callbacks')==720 and n.get('all17Adam_step639760') and n.get('sourceactor9critic8STD17Adam_literal_exact') and n.get('prelaunch_proxy_total_credit',0)>0 and n.get('prelaunch_proxy_actual_live_term_maxabs',1)<=1e-6 and n.get('all20k_source_phase_CPU_event_reconstruction_maxabs',1)<=1e-6 and row.get('target_payload_manifest_SHA')==cfg['payload_manifest_SHA'] and row.get('target_actual_validation_fcntl_held') and row.get('new_ready_GPU_resource_passed') and not row.get('original_error'))
def grant(now,cfg,pid):
 return dict(actual_H1_prelaunch_v2_scope_admitted=True,max_parent_seconds=1800,exit_headroom_seconds=300,parent_learning_started_epoch=now,save_deadline=now+1500,nominal_end_epoch=now+1800,source_SHA=cfg['source_SHA'],original_owner_pid=pid,original_owner_creation=ident(pid)['creation'],run_id=cfg['run_id'])
def main(cfg):
 token=cfg['token'].encode();mutex=threading.Lock();s=dict(row={},go=None,stop=False,last=time.time());locks=[];active=False;server=None
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    size=int(self.headers['Content-Length']);assert 0<size<2000000;body=self.rfile.read(size);assert hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,body,hashlib.sha256).hexdigest());v=json.loads(body);assert v['run_id']==cfg['run_id'] and abs(v['epoch']-time.time())<60
    with mutex:s['row']=v['row'];s['last']=time.time();reply=dict(go=s['go'],stop=s['stop'])
    raw=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,raw,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(raw)
   except BaseException:self.send_error(403)
 def account(end=False):
  nonlocal active
  c=json.loads(C.read_bytes());a=c['active_segment'];assert a['owner_parent_pid']==os.getpid() and a['kind'].startswith('Linux_HOST72_H1_GROUND_PRELAUNCH_V2_FIRST1800_');now=time.time();dt=now-a['accounted_through_epoch'];assert dt>=0;a['accounted_through_epoch']=now;a['charged_seconds']+=dt;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt
  if end:
   assert terminal(s['row']);a['ended_epoch']=now;a['actual_remote_terminal_child_handoff']=s['row'];a['duration_bound_passed']=a['charged_seconds']<=1800;c['completed_segments'].append(a);c['active_segment']=None;active=False
  assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5;put(C,c)
 try:
  for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
   f=p.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>1800+9400.860692501068+64800
  put(B/'OWNER_IDENTITY.json',ident(os.getpid()));put(B/'HUMAN_H1_PRELAUNCH_V2_CONTINUE_ORIGINAL_CANONICAL_CONTRACT.json',dict(epoch=time.time(),human_scope='2026-10-16 人类继续；已批准H1平地小跳的单轴起跳前奖励修复' ,one_H1_flat_public_request_first1800=True,includes_actual_fresh_production_load_learn_save_waitexit=True,native_GPU_CPU0PPO_uncharged_before_actual_GO=True,engineering_selected_one1800_within_original_budget_not_new_budget_authorization=True,exit_headroom_seconds=300,no_new_budget_no_H2_H3_S8_or_extra_window=True,source_SHA=cfg['source_SHA'],target_root=cfg['target_root'],native_protocol_payload_manifest_SHA=cfg['payload_manifest_SHA'],local_CPU_receipt_SHA=cfg['local_CPU_receipt_SHA']))
  server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();begun=time.time()
  while True:
   with mutex:row=dict(s['row'])
   if row.get('original_error'):s['stop']=True
   if ready(row,cfg) and s['go'] is None and not s['stop']:
    c=json.loads(C.read_bytes());assert c['active_segment'] is None;now=time.time();g=grant(now,cfg,os.getpid());c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),owner_identity=ident(os.getpid()),kind='Linux_HOST72_H1_GROUND_PRELAUNCH_V2_FIRST1800_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_seconds=0.,remote_root=cfg['target_root'],max_parent_seconds=1800,charge_contract='One H1 V2 parent actual production load/learn/fullsave/SDKclose/actual child wait-exit; nativeGPU and CPU are0PPO/uncharged. No second automatic window.',source_SHA=cfg['source_SHA']);put(C,c);active=True;s['go']=g
   if active:account()
   if time.time()-s['last']>120 or (s['go'] and time.time()>=s['go']['save_deadline']) or time.time()-begun>3600:s['stop']=True
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),row=row,go=s['go'],stop=s['stop'],original_two_fcntl_held=True,original_canonical_active=active))
   if terminal(row):
    if active:account(True)
    put(B/'OWNER_FINAL.json',dict(epoch=time.time(),terminal_handoff=row,go=s['go'],canonical_settled=True,production_complete=row.get('production_complete',False) and not row.get('original_error'),no_automatic_next_window=True));break
   if not active and s['stop'] and not s['go']:
    put(B/'OWNER_NOT_GRANTED_TERMINAL.json',dict(epoch=time.time(),no_learning_granted_or_charged=True,node_must_observe_stop=True));break
   time.sleep(3)
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active));s['stop']=True
  while active:
   if terminal(s['row']):account(True);break
   account();time.sleep(3)
  raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),canonical_settled=not active,own_locks_released=True))
  if server:server.shutdown()
if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert not (B/'OWNER_IDENTITY.json').exists() and not (B/'OWNER_CONSOLE.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='H1_source_original_owner')),flush=True)
 else:
  os.setsid();f=os.open(str(B/'OWNER_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);main(cfg)
