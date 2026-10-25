"""Report actual finite CPU-admission status inside the existing node; no extra process."""
import threading,time,traceback
def run_CPU_with_status(cfg,audit,send,put,root,period=3.,max_ack_gap=120.):
 begin=time.monotonic();last_ack=[begin];acks=[0];stopped=[False];errors=[];done=threading.Event();succeeded=False
 def pulse():
  while not done.is_set():
   row=dict(key=cfg['key'],phase='native_CPU_review_running',worker=None,returncode=None,native_CPU=None,manifest_SHA=cfg['manifest_SHA'],native_GPU_waited_EXIT0=True,actual_CPU_review_running=True,not_CPU_admitted_or_PPO=True)
   try:
    reply=send(cfg,row);last_ack[0]=time.monotonic();acks[0]+=1;stopped[0]=stopped[0] or bool(reply.get('stop'))
   except BaseException:
    if len(errors)<3:errors.append(traceback.format_exc())
   if done.wait(period):break
 thread=threading.Thread(target=pulse,name='own-finite-CPU-admission-status',daemon=False);thread.start()
 try:
  result=audit(cfg);assert not stopped[0],'Original source requested saved-stop during CPU admission; no new PPO';assert time.monotonic()-last_ack[0]<=max_ack_gap,'No actual authenticated source acknowledgement within original transport timeout';succeeded=True;return result
 finally:
  done.set();thread.join(timeout=20);assert not thread.is_alive(),'Finite source status call did not return within original bounded transport';put(root/'NATIVE_CPU_ACTUAL_STATUS_BRIDGE_RECEIPT.json',dict(epoch=time.time(),elapsed=time.monotonic()-begin,actual_authenticated_status_acknowledgements=acks[0],actual_ack_age=time.monotonic()-last_ack[0],original_transport_timeout_seconds=max_ack_gap,source_stop_observed=stopped[0],CPU_function_succeeded=succeeded,original_status_errors=errors,no_fake_ready_or_GO_or_GPU_or_optimizer=True,no_extra_process_or_SSH_or_watchdog=True))
