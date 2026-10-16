"""Fresh production parent after actual failed-owner closure; remaining original scope cap."""
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:return None
def owner():
 locks=[];child=None;active=False
 def account(end=False):
  nonlocal active
  c=json.loads(C.read_bytes());a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();now=time.time();dt=now-a['accounted_through_epoch'];assert dt>=0;a['charged_seconds']+=dt;a['accounted_through_epoch']=now;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt
  if end:a['ended_epoch']=now;a['actual_child_returncode']=child.returncode;c['completed_segments'].append(a);c['active_segment']=None;active=False
  assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5;put(C,c)
 try:
  for row in json.loads((B/'PAYLOAD_MANIFEST.json').read_bytes())['files']:assert hashlib.sha256((B/row['relative']).read_bytes()).hexdigest()==row['SHA']
  for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
   f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  prior=json.loads((B/'PRIOR_NATIVE_PRECHECK_AND_CLOSED_COST_ACTUAL.json').read_bytes());c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7
  old=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==477807];assert len(old)==2;spent=sum(x['charged_seconds'] for x in old);assert abs(spent-prior['actual_already_charged_seconds'])<1e-6;remaining=2700-spent;assert remaining>600 and c['remaining_training_seconds']>remaining+9400.860692501068+64800
  now=time.time();c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_CURB35_FROM_QUALIFIED878_FRESH_PRODUCTION_REMAINDER_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_seconds=0.,actual_prior_scope_charged=spent,max_remaining_parent_seconds=remaining,no_native_or_preflight_replay=True);put(C,c);active=True;put(B/'GO_PRODUCTION_ACTUAL.json',dict(epoch=now,save_deadline=now+remaining-240,remaining_scope_parent_seconds=remaining,prior_scope_charged=spent,exit_headroom_seconds=240));put(B/'OWNER_IDENTITY.json',ident(os.getpid()))
  task=json.loads((J/'TASK_CURB35.json').read_bytes());env=dict(os.environ)
  for n in ('home','tmp','cache','config','data'):(J/n).mkdir(exist_ok=True)
  for k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
  env.update(CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(J/'home'),TMPDIR=str(J/'tmp'),XDG_CACHE_HOME=str(J/'cache'),XDG_CONFIG_HOME=str(J/'config'),XDG_DATA_HOME=str(J/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  child=subprocess.Popen([PY,'-u','-B',str(B/'curb35_production_worker_v2.py')],cwd=B,env=env,stdout=(J/'production_worker.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(B/'WORKER_STARTED_ACTUAL.json',ident(child.pid))
  while child.poll() is None:account();put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),child=ident(child.pid),phase='fresh_source_fullrestore_then_production',original_canonical_active=True,prior_scope_charged=spent));time.sleep(3)
  account(True);put(B/'WORKER_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=child.pid,returncode=child.returncode,actual_waited=True));assert child.returncode==0 and not list((J/'production_only').glob('WORKER_ORIGINAL_ERROR*.json'));final=json.loads((J/'production_only/FINAL.json').read_bytes());assert final['passed'];put(B/'OWNER_FINAL.json',dict(epoch=time.time(),final=final,original_canonical_settled_once=True,no_automatic_next_window=True))
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active))
  if child and child.poll() is None:
   out=J/'production_only';out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite production parent exception; save-stop only'))
   while child.poll() is None:
    if active:account()
    time.sleep(3)
  if active:account(True)
  raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),canonical_settled=not active,own_locks_released=True))
def main():
 assert '--execute-new-fresh-CURB35-production-only' in sys.argv and not (B/'OWNER_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_owner_pid=pid,root=str(B))),flush=True);return
 os.setsid();f=os.open(str(B/'OWNER_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);owner()
if __name__=='__main__':main()
