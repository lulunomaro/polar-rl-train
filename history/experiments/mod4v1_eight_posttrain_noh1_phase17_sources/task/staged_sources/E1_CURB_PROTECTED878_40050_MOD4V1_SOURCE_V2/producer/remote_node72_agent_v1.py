"""Finite own rank1/2 supervisor, durable after human laptop powers off."""
from pathlib import Path
import hashlib,hmac,json,os,subprocess,sys,time,traceback,urllib.request
BASE=Path(__file__).resolve().parent;ROOT=Path('/home/lc01/Zonglin Li/zonglin2')
from remote_single_ppo_owner_v1 import atomic,identity,env_for,collect
def main(config):
 token=config['auth_token'].encode();workers={};mode='probe';last_success=time.time();learning_end=None
 def start(mode):
  for rank in (1,2):
   out=BASE/('rank'+str(rank));out.mkdir(exist_ok=True);argv=[str(ROOT/'run-python.sh'),'-u','-B',str(BASE/'distributed_rank_worker_v1.py'),'--rank',str(rank),'--mode',mode]
   p=subprocess.Popen(argv,cwd=BASE,env=env_for(rank),stdout=(out/(mode+'_worker.log')).open('xb'),stderr=subprocess.STDOUT,close_fds=True,start_new_session=True);workers[rank]=p;atomic(out/(mode+'_PROCESS_STARTED.json'),identity(p.pid))
 start(mode);atomic(BASE/'NODE72_AGENT_IDENTITY.json',identity(os.getpid()))
 while True:
  rows=[collect(rank,p,mode) for rank,p in workers.items()];req=dict(run_id=config['run_id'],epoch=time.time(),ranks=rows);b=json.dumps(req).encode();request=urllib.request.Request('http://10.24.4.210:29616/',data=b,headers={'X-Own-Signature':hmac.new(token,b,hashlib.sha256).hexdigest(),'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(request,timeout=15) as response:raw=response.read();signature=response.headers['X-Own-Signature']
   assert hmac.compare_digest(hmac.new(token,raw,hashlib.sha256).hexdigest(),signature);reply=json.loads(raw);last_success=time.time()
  except BaseException:
   reply=dict(phase='stop' if time.time()-last_success>120 else mode,reason='Own source-owner control unavailable',deadline=learning_end)
   atomic(BASE/'NODE72_CONTROL_LAST_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),will_stop_own_after120s=True))
  phase=reply['phase']
  if mode=='probe' and phase=='train_native':
   assert all(p.poll()==0 for p in workers.values());mode='train';workers={};start(mode)
  if phase=='learn':
   learning_end=reply['deadline']
   for rank in (1,2):
    q=BASE/('rank'+str(rank))/'GO_SINGLE_PPO.json'
    if not q.exists():atomic(q,dict(save_deadline_epoch=learning_end,original_owner='10.24.4.210'))
  if phase=='stop' or (learning_end and time.time()>=learning_end):
   for rank in (1,2):
    q=BASE/('rank'+str(rank))/'STOP_AFTER_SAVE.json'
    if not q.exists():atomic(q,dict(epoch=time.time(),reason=reply.get('reason','Own bounded end')))
   if all(p.poll() is not None for p in workers.values()):break
  if mode=='train' and all(p.poll() is not None for p in workers.values()):
   # Send exits to the original canonical owner once more before leaving.
   if phase in ('learn','stop'):continue
  atomic(BASE/'NODE72_CURRENT_ACTUAL.json',dict(epoch=time.time(),mode=mode,owner_phase=phase,rows=rows,deadline=learning_end));time.sleep(3)
 atomic(BASE/'NODE72_AGENT_EXIT_ACTUAL.json',dict(epoch=time.time(),rows=rows,no_other_process_signal=True,no_restart=True))
if __name__=='__main__':
 config=json.loads(sys.stdin.readline());pid=os.fork()
 if pid:print(json.dumps(dict(remote_detached_pid=pid,root=str(BASE))),flush=True)
 else:
  os.setsid();fd=os.open(str(BASE/'node72_stdout_stderr.log'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd)
  try:main(config)
  except BaseException:atomic(BASE/'NODE72_AGENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
