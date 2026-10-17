"""One owned source85 native336/CPU validation; never sends learning GO or touches budget."""
from pathlib import Path
import os,sys,time,json,fcntl,traceback
import three_slot_common_v1 as b
B=Path(__file__).resolve().parent;put=b.put
def run(spec):
 assert spec['key']=='h1' and spec['role']=='native_only';lock=None;children=[];error=None;native=None;p=None
 put(B/'NATIVE_ONLY_PARENT_IDENTITY.json',b.ident(os.getpid()))
 try:
  b.validate_payload(spec);from three_slot_resource_v1 import acquire;lock=acquire(spec,B);p=b.spawn(spec,'native');children.append(p);start=time.time()
  while p.poll() is None:
   put(B/'NATIVE_ONLY_CURRENT.json',dict(epoch=time.time(),worker=b.ident(p.pid),state=b.state(spec,'native',p),no_production_GO_or_PPO_or_charge=True))
   if time.time()-start>7200:
    put(b.outdir('native')/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own native-only finite7200s limit; preserve failed prefix no signal'))
   time.sleep(3)
  p.wait();state=b.state(spec,'native',p);assert p.returncode==0 and state['final']['passed_worker_not_independent_CPU'] and not state['errors'],state
  native=b.native_CPU(spec);assert native['actual_CPU_waited_EXIT0'] and native['value']['passed'] and native['value']['source_SHA']==spec['source_SHA']
  put(B/'NATIVE_ONLY_FINAL_ACTUAL.json',dict(epoch=time.time(),passed_native_GPU_and_full_CPU=True,source_SHA=spec['source_SHA'],native_CPU=native,actual_GPU_worker_EXIT0=True,controls180_callbacks720=True,no_production_GO_or_PPO_or_canonical_charge=True,not_frozen_jump_skill_qualification=True))
 except BaseException:
  error=traceback.format_exc();put(B/'NATIVE_ONLY_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=error,no_automatic_retry=True))
  if p and p.poll() is None:put(b.outdir('native')/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own native-only exception complete validprefix saved-stop'))
 finally:
  for p in children:p.wait()
  if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  put(B/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),all_actual_own_GPU_children_waited=True,private_GPU_fcntl_released_if_acquired=True,passed_native_CPU=bool(native and not error),original_error=bool(error),no_PPO_or_canonical_or_production_GO=True))
 if error:raise RuntimeError('Original native-only error retained')
if __name__=='__main__':
 spec=json.loads(sys.stdin.readline());assert spec['role']=='native_only' and not (B/'native_only_CONSOLE.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),role='native_only')),flush=True)
 else:
  os.setsid();fd=os.open(str(B/'native_only_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);run(spec)
