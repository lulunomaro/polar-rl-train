"""Durable original canonical owner and authenticated finite two-node supervisor."""
from pathlib import Path
import hashlib,hmac,http.server,json,os,subprocess,sys,threading,time,traceback,urllib.request,fcntl,socket
BASE=Path(__file__).resolve().parent;PORT=29616;RUNPY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
def atomic(p,v):
 q=p.with_suffix(p.suffix+'.partial')
 with q.open('w') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
 q.replace(p)
def identity(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
 except psutil.Error:return None
def env_for(rank):
 v=dict(os.environ);v.update(RANK=str(rank),WORLD_SIZE='3',LOCAL_RANK='0',MASTER_ADDR='10.24.4.210',MASTER_PORT='29617',NCCL_SOCKET_IFNAME='enp4s0' if rank==0 else 'eno1',GLOO_SOCKET_IFNAME='enp4s0' if rank==0 else 'eno1',NCCL_IB_DISABLE='1',NCCL_DEBUG='WARN',TORCH_NCCL_ASYNC_ERROR_HANDLING='1',CUDA_VISIBLE_DEVICES=['GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e','GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'][rank],PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 if rank==0:
  for name in ('home','tmp','cache','config','data'):(BASE/name).mkdir(exist_ok=True)
  v.update(HOME=str(BASE/'home'),TMPDIR=str(BASE/'tmp'),XDG_CACHE_HOME=str(BASE/'cache'),XDG_CONFIG_HOME=str(BASE/'config'),XDG_DATA_HOME=str(BASE/'data'))
 return v
def spawn(rank,mode):
 out=BASE/('rank'+str(rank));out.mkdir(exist_ok=True);p=subprocess.Popen([RUNPY,'-u','-B',str(BASE/'distributed_rank_worker_v1.py'),'--rank',str(rank),'--mode',mode],cwd=BASE,env=env_for(rank),stdout=(out/(mode+'_worker.log')).open('xb'),stderr=subprocess.STDOUT,close_fds=True,start_new_session=True);atomic(out/(mode+'_PROCESS_STARTED.json'),identity(p.pid));return p
def collect(rank,p,mode):
 root=BASE/('rank'+str(rank));v=dict(rank=rank,mode=mode,worker=identity(p.pid),returncode=p.poll())
 for n in ('NCCL_PROBE_COMPLETE.json','READY_FOR_SINGLE_PPO.json','latest_complete.json','SHARED_PPO_ALL_RANK_PARAMETERS_EXACT_ACTUAL.json','FINAL_SINGLE_PPO.json','ORIGINAL_WORKER_ERROR.json'):
  q=root/n
  if q.exists():
   try:v[n]=json.loads(q.read_bytes())
   except (ValueError,OSError):pass
 return v
def daemonize(config):
 pid=os.fork()
 if pid:print(json.dumps(dict(remote_detached_pid=pid,root=str(BASE))),flush=True);return False
 os.setsid();fd=os.open(str(BASE/'owner_stdout_stderr.log'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);return True
def main(config):
 token=config['auth_token'].encode();state={'phase':'probe','ranks':{},'deadline':None,'reason':None};mutex=threading.Lock()
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    b=self.rfile.read(int(self.headers['Content-Length']));sig=hmac.new(token,b,hashlib.sha256).hexdigest();assert hmac.compare_digest(sig,self.headers.get('X-Own-Signature',''))
    req=json.loads(b);assert req['run_id']==config['run_id'];assert time.time()-req['epoch']<60
    with mutex:
     for row in req.get('ranks',[]):state['ranks'][str(row['rank'])]=row
     state['node72_seen']=time.time();reply={k:state[k] for k in ('phase','deadline','reason')}
    data=json.dumps(reply).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,data,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(data)
   except BaseException:self.send_error(403)
 server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 atomic(BASE/'ORIGINAL_OWNER_IDENTITY.json',identity(os.getpid()));atomic(BASE/'HUMAN_7H_THREE_GPU_ACCOUNTING_CONTRACT.json',dict(epoch=time.time(),human_explicit_three_GPU_one_PPO_seven_hours=True,scope='E1_CURB20_original_entry',world_size=3,per_rank_envs=20000,global_envs=60000,solecanonical_original_path=str(B),one_shared_job_parent_wall_interval_seconds=25200,nominal_GPU_resource_seconds=75600,not_added_budget=True,no_duplicate_per_rank_charge=True,other_compute_coexistence_authorized_no_process_interference=True,preflight_no_PPO_uncharged=True,initial_source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',independent_rank_stream_fork_disclosed=True))
 locks=[];charged=False;proc=None;mode='probe';begin=None;kind=None
 def account(start=False,end=False):
  nonlocal charged,begin,kind
  b=json.loads(B.read_bytes())
  if start:
   assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['remaining_training_seconds']>25200+9400.860692501068+64800
   begin=time.time();kind='Linux_DDPPO_CURB20_WORLD3_7H_'+str(time.time_ns());b['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind=kind,started_epoch=begin,accounted_through_epoch=begin,world_size=3,one_shared_PPO=True,source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',human_new_concurrent_three_rank_contract=str(BASE/'HUMAN_7H_THREE_GPU_ACCOUNTING_CONTRACT.json'),max_parent_wall_seconds=25200);charged=True
  a=b['active_segment'];assert a['owner_parent_pid']==os.getpid();now=time.time();dt=now-a['accounted_through_epoch'];assert dt>=0;b['charged_training_seconds']+=dt;b['remaining_training_seconds']-=dt;a['accounted_through_epoch']=now
  assert abs(b['charged_training_seconds']+b['remaining_training_seconds']-1188000)<1e-5
  if end:a['ended_epoch']=now;a['end_evidence']='Actual own three-rank exits observed, no duplicate learning job charge';b['completed_segments'].append(a);b['active_segment']=None;charged=False
  atomic(B,b)
 try:
  for f in LOCKS:
   h=f.open('rb+');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(h)
  b=json.loads(B.read_bytes());assert b['active_segment'] is None
  proc=spawn(0,'probe');wait=time.time();next_account=0
  while True:
   own=collect(0,proc,mode)
   with mutex:state['ranks']['0']=own;rows=[state['ranks'].get(str(i)) for i in range(3)];phase=state['phase']
   bad=[r for r in rows if r and (r.get('returncode') not in (None,0) or r.get('ORIGINAL_WORKER_ERROR.json'))]
   if bad:state['phase']='stop';state['reason']='Own rank original failure; preserve previous complete checkpoint';atomic(BASE/'RANK_FAILURE_ACTUAL.json',dict(epoch=time.time(),rows=bad))
   if phase=='probe' and all(r and r.get('returncode')==0 and 'NCCL_PROBE_COMPLETE.json' in r for r in rows):
    atomic(BASE/'THREE_GPU_NCCL_ACTUAL_PASSED.json',dict(epoch=time.time(),rows=rows,all_reduce_shared_fixture_exact=True));state['phase']='train_native';mode='train';state['ranks']={};proc=spawn(0,'train');wait=time.time()
   elif phase=='train_native' and all(r and 'READY_FOR_SINGLE_PPO.json' in r for r in rows):
    account(start=True);state['phase']='learn';state['deadline']=begin+25200-120;atomic(BASE/'rank0/GO_SINGLE_PPO.json',dict(started_epoch=begin,save_deadline_epoch=state['deadline'],canonical_segment=kind));atomic(BASE/'SINGLE_PPO_7H_LEARNING_ADMITTED.json',dict(epoch=time.time(),rows=rows,canonical_segment=kind,nominal_parent_end_epoch=begin+25200,reserved_save_exit_seconds=120))
   elif phase=='learn':
    if time.time()>=state['deadline']:state['phase']='stop';state['reason']='Human seven-hour window approaching; synchronize own save-stop'
   if state['phase']=='stop':
    q=BASE/'rank0/STOP_AFTER_SAVE.json'
    if not q.exists():atomic(q,dict(epoch=time.time(),reason=state['reason']))
    if all(r and r.get('returncode') is not None for r in rows):break
    if not charged and proc.poll() is not None and time.time()-wait>480:break
   if phase in ('probe','train_native') and time.time()-wait>(240 if phase=='probe' else 1200):state['phase']='stop';state['reason']='Bounded own admission timeout; no automatic replay'
   if phase=='learn' and all(r and r.get('returncode')==0 for r in rows):break
   if charged and time.time()>=next_account:account();next_account=time.time()+15
   atomic(BASE/'CURRENT_THREE_RANK_ACTUAL.json',dict(epoch=time.time(),phase=state['phase'],deadline=state['deadline'],ranks=state['ranks'],canonical_charged=charged,node72_last_seen=state.get('node72_seen'),reason=state['reason']))
   if time.time()-state.get('node72_seen',time.time())>120:state['phase']='stop';state['reason']='Own node72 coordinator heartbeat missing; save-stop rather than stale rollout'
   time.sleep(3)
  if charged:account(end=True)
  atomic(BASE/'THREE_RANK_FINAL_ACTUAL.json',dict(epoch=time.time(),rows=rows,complete=all(r and r.get('returncode')==0 and r.get('FINAL_SINGLE_PPO.json') for r in rows),unique_original_cost_settled=True,no_auto_restart=True))
 except BaseException:
  atomic(BASE/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),canonical_active_not_falsely_cleared=charged));state['phase']='stop';state['reason']='Own owner exception; stop after own saved update'
  if proc and proc.poll() is None:
   atomic(BASE/'rank0/STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason=state['reason']))
   while proc.poll() is None:
    if charged:account()
    time.sleep(5)
  if charged:
   # Wait for explicit own remote-rank exits before settling the original segment.
   while not all(state['ranks'].get(str(i),{}).get('returncode') is not None for i in (1,2)):account();time.sleep(5)
   account(end=True)
  raise
 finally:
  for h in reversed(locks):fcntl.flock(h,fcntl.LOCK_UN);h.close()
  atomic(BASE/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),own_locks_released=True,canonical_active_settled=not charged));server.shutdown()
if __name__=='__main__':
 config=json.loads(sys.stdin.readline())
 if daemonize(config):main(config)
