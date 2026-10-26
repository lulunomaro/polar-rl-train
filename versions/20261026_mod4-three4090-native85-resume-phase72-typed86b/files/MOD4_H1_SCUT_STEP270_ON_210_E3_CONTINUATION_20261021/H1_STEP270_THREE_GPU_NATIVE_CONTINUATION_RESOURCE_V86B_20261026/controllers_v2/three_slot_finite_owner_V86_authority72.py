"""One original canonical writer, three independent finite expert slots."""

from pathlib import Path

import os,sys,time,json,threading,http.server,hmac,hashlib,fcntl,traceback

import three_slot_common_v1 as b
from single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_original_extension_count,authority_budget_GO_allowed
from mixed86_protocol_v1 import validate_schedule

B=Path(__file__).resolve().parent;put=b.put

def owner(cfg):

 specs=cfg['experts'];assert set(specs)=={'h1','e2','recovery'} and all(s['key']==k and s['max_parent_seconds']==b.CAPS[k] and s['exit_headroom_seconds']==300 for k,s in specs.items());assert cfg['scheduling_authority']=='human_requested_available_experts' and cfg['deferred_experts']==[];validate_schedule(cfg);token=cfg['token'].encode();shared=dict(rows={},last={},go={},stop={k:False for k in specs});mu=threading.Lock();locks=[];active=False;server=None;started=time.time();rows={}

 class Handler(http.server.BaseHTTPRequestHandler):

  def log_message(self,*a):pass

  def do_POST(self):

   try:

    n=int(self.headers['Content-Length']);assert 0<n<3000000;raw=self.rfile.read(n);key,row=b.authenticated_row(raw,self.headers.get('X-Own-Signature',''),token,cfg['run_id'],specs,time.time())

    with mu:

     prev=shared['rows'].get(key,{})

     if b.terminal(row):row['owner_received_terminal_epoch']=prev.get('owner_received_terminal_epoch',time.time())

     shared['rows'][key]=row;shared['last'][key]=time.time();reply=dict(go=shared['go'].get(key),stop=shared['stop'][key])

    raw=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,raw,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(raw)

   except BaseException:self.send_error(403)

 def account(end=False):

  nonlocal active,rows

  # Terminal receipt time cannot race behind a later accounted-through time.

  with mu:

   rows={k:dict(shared['rows'].get(k,{})) for k in specs};now=time.time();c=b.read(b.C);a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();c,a=b.charge_values(c,a,shared['go'],rows,now);c['active_segment']=a

   if end:

    assert all(b.terminal(rows[k]) for k in specs);a['ended_epoch']=now;a['actual_terminal_rows']=rows;c['completed_segments'].append(a);c['active_segment']=None;active=False

   put(b.C,c)

 try:

  put(B/'OWNER_IDENTITY.json',b.ident(os.getpid()));put(B/'THREE_SLOT_ORIGINAL_FINITE_ACCOUNTING_CONTRACT.json',dict(epoch=time.time(),slots={k:dict(source_SHA=s['source_SHA'],GPU_UUID=s['GPU_UUID'],cap_seconds=s['max_parent_seconds'],headroom300=True) for k,s in specs.items()},existing_human_independent_experts_and_master_healthy_continuation=True,one_original_twofcntl_writer_sum_distinct_actual_loadlearnsaveclosechildwait_terminal=True,no_native_CPU_charge_new_budget_ledger_clearactive_refund_or_tail=True,all_scheduled_nodes_registered_before_first_GO_each_source_CPU_required=True,deferred_experts_without_GO=cfg['deferred_experts'],independent_slot_failure_other_healthy_slots_continue=True));server=http.server.ThreadingHTTPServer(('127.0.0.1',b.PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()

  while True:

   with mu:rows={k:dict(shared['rows'].get(k,{})) for k in specs};all_registered=all(rows.values())

   if not all_registered and not active and not shared['go'] and time.time()-started>120:

    with mu:shared['stop']={k:True for k in specs}

    put(B/'NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json',dict(epoch=time.time(),observed=list(shared['rows']),unobserved=[k for k in specs if not rows[k]],no_PPO_or_original_locks_or_canonical_write=True,unobserved_child_exit_unknown_not_faked=True));break

   for key,spec in specs.items():

    if not all_registered or key in shared['go'] or shared['stop'][key] or not b.valid_ready(rows[key],spec):continue

    if not locks:

     c=b.read(b.C)

     if c['active_segment'] is not None:continue

     attempt=[]

     try:

      for path in b.LOCKS:f=path.open('rb+');attempt.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)

     except BlockingIOError:

      for f in attempt:f.close()

      continue

     locks=attempt;c=b.read(b.C);assert c['active_segment'] is None and authority_tracking_schema_admitted(c) and authority_original_extension_count(c)==9 and authority_budget_GO_allowed(c) and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'

    if not active:

     c=b.read(b.C);assert c['active_segment'] is None;now=time.time();c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_H1_STEP270_E3_' +str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='One original writer; sum independent actual production load learn save SDKclose childwait and owner terminal receipt.');put(b.C,c);active=True

    now=time.time();shared['go'][key]=dict(manifest_SHA=spec['manifest_SHA'],bootstrap_SHA=spec.get('bootstrap_source_SHA'),bootstrap_Adam=(spec['source_Adamstep'] if spec.get('native_continuation') else None),native_continuation_restore_required=bool(spec.get('native_continuation')),source_native_iteration=spec.get('source_native_iteration'),window_start_world_updates=spec.get('window_start_world_updates'),window_start_policy_updates=spec.get('window_start_policy_updates'),learning_started_epoch=now,save_deadline=now+spec['max_parent_seconds']-300,nominal_end_epoch=now+spec['max_parent_seconds'],max_parent_seconds=spec['max_parent_seconds'],exit_headroom_seconds=300,source_SHA=spec['source_SHA'],source_native_CPU_SHA=(rows[key].get('native_CPU') or {}).get('SHA'),source_CPU_SHA=(rows[key].get('closed_source_CPU') or rows[key].get('native_CPU') or {})['SHA'],source_qualification_kind=(rows[key].get('closed_source_CPU') or rows[key].get('native_CPU'))['value'].get('kind','H1_STEP270_SOURCE_AND_NATIVE_CPU'),original_owner_pid=os.getpid(),original_owner_creation=b.ident(os.getpid())['creation'],run_id=cfg['run_id'],actual_H1_prelaunch_v2_scope_admitted=False,actual_H1_step270_scope_admitted=key=='h1');account()

   if active:account()

   with mu:

    for key in specs:

     if rows[key].get('original_error') or (key in shared['last'] and time.time()-shared['last'][key]>120 and not b.terminal(rows[key])):shared['stop'][key]=True

    if time.time()-started>10800:shared['stop']={k:True for k in specs}

   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),rows=rows,go=shared['go'],stop_by_slot=shared['stop'],original_canonical_active=active,original_two_fcntl_held=bool(locks),one_slot_failure_not_other_expert_failure=True,scheduled_experts=list(specs),deferred_experts_without_GO=cfg['deferred_experts']))

   if all(b.terminal(rows[k]) for k in specs):

    if active:account(True)

    put(B/'COHORT_FINAL.json',dict(epoch=time.time(),rows=rows,go=shared['go'],original_cost_settled=True,no_automatic_extra_window=True,scheduled_experts=list(specs),deferred_experts_without_GO=cfg['deferred_experts']));break

   time.sleep(3)

 except BaseException:

  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active));shared['stop']={k:True for k in specs}

  while active:

   with mu:rows={k:dict(shared['rows'].get(k,{})) for k in specs}

   account()

   if all(b.terminal(rows[k]) for k in specs):account(True);break

   time.sleep(3)

  raise

 finally:

  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()

  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),original_cost_settled=not active,own_original_two_fcntl_released_if_held=True))

  if server:server.shutdown()

if __name__=='__main__':

 cfg=json.loads(sys.stdin.readline());assert cfg['role']=='owner';assert not (B/'owner_CONSOLE.log').exists();pid=os.fork()

 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='owner')),flush=True)

 else:

  os.setsid();fd=os.open(str(B/'owner_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);owner(cfg)

