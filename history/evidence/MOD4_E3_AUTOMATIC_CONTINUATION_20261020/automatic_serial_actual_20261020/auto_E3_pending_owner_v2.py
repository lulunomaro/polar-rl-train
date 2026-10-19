"""One E3 window with a durable pending-cost receipt. Requires separate explicit approval.

This owner never opens, copies, clears or settles the offline original canonical ledger.
The reservation is deliberately retained after exit so another window cannot auto-start.
"""
from pathlib import Path
import fcntl,hashlib,hmac,http.server,json,os,sys,threading,time,traceback
import three_slot_common_v1 as b
B=Path(__file__).resolve().parent
RESERVATION=B/'WINDOW_OFFLINE_COST_RESERVATION.json'
APPROVAL_ID='auto-E3-existing-budget-20261020'
HOST='127.0.0.1'

def advance_cost(cost,go,row,now):
 """Same GO-to-owner-terminal-receipt interval convention; no budget balance here."""
 if go is None:return dict(cost)
 out=dict(cost);start=go['learning_started_epoch'];last=out.get('accounted_through_epoch',start)
 end=row.get('owner_received_terminal_epoch',now) if b.terminal(row) else now
 end=max(end,last);delta=end-last;assert delta>=0
 out.update(started_epoch=start,accounted_through_epoch=end,actual_production_seconds=out.get('actual_production_seconds',0.)+delta)
 if b.terminal(row):out.update(ended_epoch=end,actual_returncode=row['returncode'],duration_bound_passed=out['actual_production_seconds']<=3900)
 return out

def owner(cfg):
 spec=cfg['experts']['recovery'];assert set(cfg['experts'])=={'recovery'}
 assert cfg['approval_id']==APPROVAL_ID and cfg['explicit_offline_cost_approval'] is True
 assert spec['key']=='recovery' and spec['max_parent_seconds']==3900 and spec['exit_headroom_seconds']==300
 assert spec['source_SHA']==cfg['expected_source_SHA']
 assert cfg['deferred_experts']==['h1','e2']
 assert not (B/'OWNER_IDENTITY.json').exists() and not RESERVATION.exists()
 token=cfg['token'].encode();mu=threading.Lock();state=dict(row={},last=None,go=None,stop=False,cost={});server=None;reservation_fd=None;start=time.time();finished=False
 def persist():
  with mu:
   state['cost']=advance_cost(state['cost'],state['go'],state['row'],time.time())
   receipt=dict(epoch=time.time(),run_id=cfg['run_id'],approval_id=APPROVAL_ID,owner_identity=b.ident(os.getpid()),GO=state['go'],cost=state['cost'],row=state['row'],canonical_settled=False,pending_original_canonical_reconciliation=True,reservation_ceiling_seconds=3900,owner_does_not_launch_next_window=True,serial_parent_may_continue_after_full_close_CPU=True,deferred_experts_without_GO=cfg['deferred_experts'])
   b.put(B/'PENDING_COST_CURRENT.json',receipt)
   return receipt
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    n=int(self.headers['Content-Length']);assert 0<n<3000000;raw=self.rfile.read(n);key,row=b.authenticated_row(raw,self.headers.get('X-Own-Signature',''),token,cfg['run_id'],cfg['experts'],time.time());assert key=='recovery'
    with mu:
     if b.terminal(row):row['owner_received_terminal_epoch']=state['row'].get('owner_received_terminal_epoch',time.time())
     state['row']=row;state['last']=time.time();reply=dict(go=state['go'],stop=state['stop'])
    raw=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,raw,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(raw)
   except BaseException:self.send_error(403)
 try:
  # O_EXCL is the durable once gate. Its pathname is never replaced or removed by this owner.
  reservation_fd=os.open(RESERVATION,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);fcntl.flock(reservation_fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  reservation=dict(epoch=time.time(),run_id=cfg['run_id'],approval_id=APPROVAL_ID,owner_root=str(B),source_SHA=spec['source_SHA'],reserved_maximum_seconds=3900,canonical_settled=False,retain_until_once_original_canonical_reconciliation=True)
  data=json.dumps(reservation,indent=2).encode();os.write(reservation_fd,data);os.fsync(reservation_fd)
  b.put(B/'OWNER_IDENTITY.json',b.ident(os.getpid()));b.put(B/'OFFLINE_COST_RESERVATION_ACTUAL.json',reservation)
  server=http.server.ThreadingHTTPServer((HOST,b.PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
  while True:
   with mu:
    row=dict(state['row']);last=state['last']
    if state['go'] is None and b.valid_ready(row,spec) and not state['stop']:
     now=time.time();state['go']=dict(learning_started_epoch=now,save_deadline=now+3600,nominal_end_epoch=now+3900,max_parent_seconds=3900,exit_headroom_seconds=300,source_SHA=spec['source_SHA'],source_native_CPU_SHA=None,source_CPU_SHA=row['closed_source_CPU']['SHA'],source_qualification_kind='closed_same_backend_production',original_owner_pid=os.getpid(),original_owner_creation=b.ident(os.getpid())['creation'],run_id=cfg['run_id'],actual_H1_prelaunch_v2_scope_admitted=False,accounting_kind='explicitly_approved_pending_cost_original_canonical_offline',canonical_settled=False)
    if row.get('original_error') or (last and time.time()-last>120) or time.time()-start>10800:state['stop']=True
    if state['go'] is None and time.time()-start>120:state['stop']=True
   receipt=persist();b.put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),rows={'recovery':row},go={'recovery':state['go']} if state['go'] else {},stop_by_slot={'recovery':state['stop']},pending_cost=receipt,original_canonical_active=False,original_two_fcntl_held=False))
   if b.terminal(row):
    b.put(B/'COHORT_FINAL.json',dict(epoch=time.time(),rows={'recovery':row},go={'recovery':state['go']} if state['go'] else {},pending_cost=receipt,original_cost_settled=False,pending_cost_record_complete=True,owner_does_not_launch_next_window=True,serial_parent_may_continue_after_full_close_CPU=True));finished=True;break
   if not row and state['stop'] and state['go'] is None:
    b.put(B/'NO_GO_REGISTRATION_EXPIRED_ACTUAL.json',dict(epoch=time.time(),no_GO_no_PPO=True,unregistered_node_exit_unknown_not_faked=True));break
   time.sleep(3)
 except BaseException:
  b.put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),canonical_not_written=True,pending_reservation_retained=True))
  with mu:state['stop']=True
  # A live node receives saved-stop or its existing 120s disconnect saved-stop;
  # continue to record its actual terminal receipt. Never kill it or mark it out by time alone.
  while state['go'] is not None and not b.terminal(state['row']):
   persist();time.sleep(3)
  if state['go'] is not None:persist()
  raise
 finally:
  if server:server.shutdown()
  if reservation_fd is not None:fcntl.flock(reservation_fd,fcntl.LOCK_UN);os.close(reservation_fd)
  b.put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),original_cost_settled=False,pending_cost_record_complete=finished,reservation_retained=True,original_canonical_and_two_locks_never_opened=True))

if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert cfg['role']=='owner';assert not (B/'owner_CONSOLE.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='owner')),flush=True)
 else:
  os.setsid();fd=os.open(str(B/'owner_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);owner(cfg)
