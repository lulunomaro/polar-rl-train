"""Durable independent experts; one original ledger owner, sum actual per-expert intervals."""
from pathlib import Path
import argparse,json,os,sys,time,subprocess,threading,hashlib,hmac,http.server,urllib.request,traceback
B=Path(__file__).resolve().parent;PORT=29716;BUDGET=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def put(p,x):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(x,indent=2));q.replace(p)
def identity(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
 except psutil.Error:return None
def env(job):
 task=json.loads((B/('job'+str(job))/'TASK.json').read_bytes());v=dict(os.environ)
 for k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):v.pop(k,None)
 root=B/('job'+str(job))
 for n in ('home','tmp','cache','config','data'):(root/n).mkdir(exist_ok=True)
 v.update(CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',HOME=str(root/'home'),TMPDIR=str(root/'tmp'),XDG_CACHE_HOME=str(root/'cache'),XDG_CONFIG_HOME=str(root/'config'),XDG_DATA_HOME=str(root/'data'))
 return v
def spawn(job,py):
 root=B/('job'+str(job));p=subprocess.Popen([py,'-u','-B',str(B/'expert_independent_worker_v1.py'),'--job',str(job)],cwd=B,env=env(job),stdout=(root/'worker.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(root/'WORKER_STARTED.json',identity(p.pid));return p
def collect(job,p):
 root=B/('job'+str(job));v=dict(job=job,worker=identity(p.pid),returncode=p.poll())
 for name in ('NATIVE120_COMPLETE.json','INDEPENDENT_NATIVE_CPU_ADMITTED.json','latest_complete.json','PPO_POSITIVE_CURRENT.json','FINAL.json'):
  q=root/'run'/name
  if q.exists():
   try:v[name]=json.loads(q.read_bytes())
   except (ValueError,OSError):pass
 for q in (root/'WORKER_ORIGINAL_ERROR.json',root/'NATIVE_CPU_REJECTED.json'):
  if q.exists():v['ORIGINAL_ERROR']=json.loads(q.read_bytes())
 if p.poll() is not None:
  q=root/'WORKER_EXIT_ACTUAL.json'
  if not q.exists():put(q,dict(epoch=time.time(),job=job,pid=p.pid,returncode=p.returncode,actual_child_waited=True))
  v['exit']=json.loads(q.read_bytes())
 return v
def cpu_gate(job,py):
 root=B/('job'+str(job));q=root/'run/INDEPENDENT_NATIVE_CPU_ADMITTED.json'
 if q.exists() or (root/'NATIVE_CPU_REJECTED.json').exists():return
 p=subprocess.run([py,'-B',str(B/'verify_independent_native_cpu_gate_v1.py'),'--job',str(job)],cwd=B,env={**os.environ,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True)
 put(root/'NATIVE_CPU_COMMAND_ACTUAL.json',dict(epoch=time.time(),argv='verify_independent_native_cpu_gate_v1.py --job '+str(job),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:put(root/'NATIVE_CPU_REJECTED.json',dict(epoch=time.time(),reason='Own independent CPU gate rejected; no automatic GPU replay',returncode=p.returncode));put(root/'run/STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own native CPU rejected; no learning'))
def node(config):
 token=config['token'].encode();py='/home/lc01/Zonglin Li/zonglin2/run-python.sh';workers={i:spawn(i,py) for i in (1,2)};last=time.time();put(B/'NODE72_IDENTITY.json',identity(os.getpid()))
 while True:
  rows=[collect(i,p) for i,p in workers.items()]
  for r in rows:
   if r.get('NATIVE120_COMPLETE.json') and not r.get('INDEPENDENT_NATIVE_CPU_ADMITTED.json') and r['returncode'] is None:cpu_gate(r['job'],py)
  rows=[collect(i,p) for i,p in workers.items()];msg=dict(run_id=config['run_id'],epoch=time.time(),rows=rows);body=json.dumps(msg).encode();reply={}
  try:
   req=urllib.request.Request('http://10.24.4.210:'+str(PORT)+'/',data=body,headers={'X-Own-Signature':hmac.new(token,body,hashlib.sha256).hexdigest(),'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=15) as response:raw=response.read();sig=response.headers['X-Own-Signature']
   assert hmac.compare_digest(sig,hmac.new(token,raw,hashlib.sha256).hexdigest());reply=json.loads(raw);last=time.time()
  except BaseException:put(B/'NODE_CONTROL_LAST_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),will_own_save_stop_after120s=True))
  for i in workers:
   out=B/('job'+str(i))/'run';go=reply.get('go',{}).get(str(i))
   if go and not (out/'GO_LEARN.json').exists():put(out/'GO_LEARN.json',go)
   if reply.get('stop') or time.time()-last>120:
    out.mkdir(exist_ok=True)
    if not (out/'STOP_AFTER_SAVE.json').exists():put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite source coordinator stopped/unavailable'))
  put(B/'NODE72_CURRENT.json',dict(epoch=time.time(),rows=rows,reply=reply))
  if all(p.poll() is not None for p in workers.values()):break
  time.sleep(3)
 put(B/'NODE72_EXIT_ACTUAL.json',dict(epoch=time.time(),rows=[collect(i,p) for i,p in workers.items()],no_other_process_action=True))
def owner(config):
 import fcntl
 locks=[];charged=False;active=None;go={};state={'remote':{},'stop':False};token=config['token'].encode();mutex=threading.Lock();started=time.time();proc=None
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   try:
    b=self.rfile.read(int(self.headers['Content-Length']));assert hmac.compare_digest(self.headers.get('X-Own-Signature',''),hmac.new(token,b,hashlib.sha256).hexdigest());x=json.loads(b);assert x['run_id']==config['run_id'] and abs(time.time()-x['epoch'])<60
    with mutex:
     for r in x['rows']:state['remote'][str(r['job'])]=r
     state['last_remote']=time.time();v=dict(go=go,stop=state['stop'])
    raw=json.dumps(v).encode();self.send_response(200);self.send_header('X-Own-Signature',hmac.new(token,raw,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(raw)
   except BaseException:self.send_error(403)
 server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 def account(rows,end=False):
  nonlocal charged,active
  c=json.loads(BUDGET.read_bytes());now=time.time()
  if not charged:
   assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>5400+9400.860692501068+64800
   active=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_THREE_INDEPENDENT_E1_EXPERTS_FIRST1800_20261016_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charge_contract='Sum each distinct independent expert actual admitted learning through own child exit; not threefold prior shared PPO charge; no new budget',experts={},charged_expert_seconds=0.);charged=True
  else:assert c['active_segment']['owner_parent_pid']==os.getpid();active=c['active_segment']
  for key,admit in go.items():
   entry=active['experts'].setdefault(key,dict(started_epoch=admit['learning_started_epoch'],accounted_through_epoch=admit['learning_started_epoch'],charged_seconds=0.,max_parent_seconds=1800))
   row=rows.get(key,{});upper=row.get('exit',{}).get('epoch',now);upper=max(entry['accounted_through_epoch'],upper);dt=upper-entry['accounted_through_epoch'];assert dt>=0;entry['charged_seconds']+=dt;entry['accounted_through_epoch']=upper;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt;active['charged_expert_seconds']+=dt
   if row.get('returncode') is not None:entry['ended_epoch']=upper;entry['returncode']=row['returncode']
  active['accounted_through_epoch']=now;c['active_segment']=active;assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5
  if end:active['ended_epoch']=now;active['end_evidence']='All three distinct own workers exited; separate actual expert intervals retained';c['completed_segments'].append(active);c['active_segment']=None;charged=False
  put(BUDGET,c)
 try:
  for q in (BUDGET.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
   f=q.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  c=json.loads(BUDGET.read_bytes());assert c['active_segment'] is None
  put(B/'OWNER_IDENTITY.json',identity(os.getpid()));put(B/'HUMAN_INDEPENDENT_EXPERTS_ACCOUNTING_CONTRACT.json',dict(epoch=time.time(),human='3060负责评测，三张4090负责不同专家训练',first_per_expert_max_seconds=1800,first_aggregate_max_expert_seconds=5400,independent_20k_each_no_NCCL=True,original_canonical=str(BUDGET),no_budget_extension=True,charge_sum_distinct_experts_actual_intervals=True,no_prior_shared_PPO_recharge=True,other_processes_untouched=True))
  proc=spawn(0,'/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python');lastaccount=0
  while True:
   own=collect(0,proc)
   if own.get('NATIVE120_COMPLETE.json') and not own.get('INDEPENDENT_NATIVE_CPU_ADMITTED.json') and own['returncode'] is None:cpu_gate(0,'/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python');own=collect(0,proc)
   with mutex:rows={**state['remote'],'0':own}
   for key,row in rows.items():
    if row.get('INDEPENDENT_NATIVE_CPU_ADMITTED.json',{}).get('passed') and row['returncode'] is None and key not in go:
     if key=='0' and not (B/'CURB_FROZEN_RESULT_REVIEW.json').exists():continue
     now=time.time();go[key]=dict(learning_started_epoch=now,save_deadline=now+1800-60,max_parent_seconds=1800,independent_expert=True,original_canonical_owner=os.getpid());account(rows)
     if key=='0':put(B/'job0/run/GO_LEARN.json',go[key])
   if charged and time.time()-lastaccount>=10:account(rows);lastaccount=time.time()
   if time.time()-started>2100 and not go:state['stop']=True
   if time.time()-state.get('last_remote',time.time())>120:state['stop']=True
   if state['stop']:
    out=B/'job0/run';out.mkdir(exist_ok=True)
    if not (out/'STOP_AFTER_SAVE.json').exists():put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite coordinator source stop'))
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),rows=rows,go=go,stop=state['stop'],original_canonical_active=charged,each_expert_has_own_actor_optimizer=True))
   if len(rows)==3 and all(x.get('returncode') is not None for x in rows.values()):break
   time.sleep(3)
  if charged:account(rows,end=True)
  put(B/'COHORT_FINAL.json',dict(epoch=time.time(),rows=rows,go=go,all_native_or_training_results_actual_not_future=True,original_cost_settled=True,no_automatic_repeat=True))
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),canonical_active_not_falsely_cleared=charged));state['stop']=True
  if proc:
   out=B/'job0/run';out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own owner exception; saved stop'))
  while proc and proc.poll() is None:
   if charged:account({**state['remote'],'0':collect(0,proc)})
   time.sleep(5)
  while charged and not all(state['remote'].get(str(i),{}).get('returncode') is not None for i in (1,2)):account({**state['remote'],'0':collect(0,proc)});time.sleep(5)
  if charged:account({**state['remote'],'0':collect(0,proc)},end=True)
  raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),canonical_settled=not charged,own_locks_released=True));server.shutdown()
def main():
 p=argparse.ArgumentParser();p.add_argument('--role',choices=('owner','node72'),required=True);a=p.parse_args();config=json.loads(sys.stdin.readline());pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,role=a.role,root=str(B))),flush=True);return
 os.setsid();f=os.open(str(B/(a.role+'_stdout_stderr.log')),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f)
 if a.role=='owner':owner(config)
 else:node(config)
if __name__=='__main__':main()
