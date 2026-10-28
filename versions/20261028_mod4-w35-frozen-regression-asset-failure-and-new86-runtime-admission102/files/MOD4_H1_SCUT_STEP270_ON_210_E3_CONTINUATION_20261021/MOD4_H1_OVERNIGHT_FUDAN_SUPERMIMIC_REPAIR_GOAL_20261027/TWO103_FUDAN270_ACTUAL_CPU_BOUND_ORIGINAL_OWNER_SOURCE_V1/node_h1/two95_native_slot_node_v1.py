"""A finite independent slot; H1 strictly reuses actual same-source/backend native."""

from pathlib import Path

import os,sys,time,json,hmac,hashlib,urllib.request,traceback,fcntl

import three_slot_common_v1 as b

B=Path(__file__).resolve().parent;put=b.put

def send(spec,row):
 from forwarded_original_owner_control_v1 import send as local_send
 return local_send(spec,row,b.PORT)
def node(spec):

 b.J=Path(spec['job_root'])
 p=None;lock=None;phase='admission';native=None;closed=None;go=None;error=None;children=[];row={};last=time.time();begin=time.time();put(B/'NODE_IDENTITY.json',b.ident(os.getpid()))

 try:

  b.validate_payload(spec);from two95_native_resource_guard_v1 import acquire;lock=acquire(spec,B)

  if spec.get('nativeflat90'):
   from mixed72_next_protocol_v1 import module_for
   closed=module_for(spec).load_actual_flat_preinstalled_CPU(spec,B);phase='ready'
  elif spec.get('native88_changed_plant'):
   from native88_closed_source_CPU_v1 import load
   closed=load(spec,B);phase='ready'
  elif spec.get('native87_policy_only'):

   from native87_closed_source_CPU_v1 import load

   closed=load(spec,B);phase='ready'

  elif spec.get('policy_hz')==50:

   from original_account_policy50_source_CPU import load

   closed=load(spec,B);phase='ready'

  elif spec.get('closed_production_continuation'):

   from closed_production_continuation_CPU_v2 import load

   closed=load(spec,B);phase='ready'

  elif spec.get('reuse_completed_native'):

   from admitted_existing_same_source_native_CPU_v1 import load

   native=load(spec,B);phase='ready'

  else:

   p=b.spawn(spec,'native');children.append(p);phase='native'

  while True:

   row={**b.state(spec,phase,p),**dict(native_CPU=native,closed_source_CPU=closed,manifest_SHA=spec['manifest_SHA'],native_GPU_waited_EXIT0=native is not None,actual_validation_fcntl_held=True)}

   try:reply=send(spec,row);last=time.time()

   except BaseException:reply={};put(B/('NODE_CONTROL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))

   stop=bool(reply.get('stop') or time.time()-last>120 or time.time()-begin>10800 or (go and time.time()>=go['save_deadline']))

   if p and p.poll() is not None:

    done=b.state(spec,phase,p);assert done['returncode']==0 and done['final'] and not done['errors'],done

    if spec['key']=='h1' and phase=='native':assert done['final']['passed_worker_not_independent_CPU']

    else:assert done['final']['passed']

    if phase=='native':

     from native_CPU_status_bridge_v1 import run_CPU_with_status

     native=run_CPU_with_status(spec,b.native_CPU,send,put,B);p=None;phase='ready'

    else:break

   if phase=='ready' and reply.get('go') and go is None:

    assert not stop;go=reply['go'];assert go['source_SHA']==spec['source_SHA'] and go['max_parent_seconds']==b.CAPS[spec['key']] and go['exit_headroom_seconds']==300;put(b.J/'job0/GO_PRODUCTION.json',go)

    if spec.get('nativeflat90'):assert go['actual_H1_flat05_scope_admitted'] and not go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted'];put(B/'GO_PRODUCTION.json',go)

    p=b.spawn(spec,'production');children.append(p);phase='production'

   if stop:

    if p and p.poll() is None:

     out=b.outdir(phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite original grant/source stop; fullsave no signal'))

    elif p is None:raise RuntimeError('Own finite source stop before production; no new grant')

   put(B/'NODE_CURRENT.json',dict(epoch=time.time(),row=row,reply=reply));time.sleep(3)

 except BaseException:

  error=traceback.format_exc();put(B/'NODE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_automatic_retry=True))

  if p and p.poll() is None:out=b.outdir(phase);out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own exception complete validprefix saved-stop'))

 finally:

  for child in children:child.wait()

  row={**b.state(spec,phase,p),**dict(manifest_SHA=spec['manifest_SHA'],native_CPU=native,closed_source_CPU=closed,original_error=error is not None,terminal_all_own_children_waited=True,returncode=p.returncode if p else 1)};put(B/'NODE_TERMINAL_ACTUAL.json',dict(epoch=time.time(),row=row));ack=False

  for attempt in range(3):

   try:send(spec,row);ack=True;break

   except BaseException:put(B/('NODE_TERMINAL_HANDOFF_ORIGINAL_ERROR_'+str(attempt)+'.json'),dict(epoch=time.time(),error=traceback.format_exc()));time.sleep(5)

  from forwarded_original_owner_control_v1 import close as close_owned_control
  close_owned_control()
  if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()

  put(B/'NODE_EXIT_ACTUAL.json',dict(epoch=time.time(),actual_all_own_children_waited=True,validation_fcntl_released_if_acquired=True,terminal_received_by_source=ack))

 if error:raise RuntimeError('Original node error preserved')

if __name__=='__main__':

 spec=json.loads(sys.stdin.readline());assert spec['role']=='node';assert not (B/'node_CONSOLE.log').exists();pid=os.fork()

 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='node')),flush=True)

 else:

  os.setsid();fd=os.open(str(B/'node_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);node(spec)

