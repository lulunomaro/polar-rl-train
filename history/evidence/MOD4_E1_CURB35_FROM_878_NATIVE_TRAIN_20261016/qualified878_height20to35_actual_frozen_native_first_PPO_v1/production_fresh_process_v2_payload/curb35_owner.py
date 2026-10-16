"""One detached finite CURB35 owner, original canonical only, no restart or other jobs."""
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python';C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');LIMIT=2700.;HEADROOM=240.
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def ident(p):
 import psutil
 try:q=psutil.Process(p);return dict(pid=p,creation=q.create_time(),argv=q.cmdline(),root=q.cwd())
 except psutil.Error:return None
def owner():
 locks=[];child=None;active=False;charged=0.;rows=[];m=json.loads((B/'PAYLOAD_MANIFEST.json').read_bytes())
 for row in m['files']:assert hashlib.sha256((B/row['relative']).read_bytes()).hexdigest()==row['SHA']
 proof=json.loads((B/'FROZEN35_3060_ADMISSION_ACTUAL.json').read_bytes());assert proof['passed'] and proof['controls']==1500 and proof['parent_child_actual_absent_lock_free']
 def budget_start(kind):
  nonlocal active
  v=json.loads(C.read_bytes());assert v['active_segment'] is None and v['authorized_training_seconds']==1188000 and len(v['budget_extensions'])==7 and v['remaining_training_seconds']>LIMIT+9400.860692501068+64800
  now=time.time();v['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_CURB35_FROM_QUALIFIED878_'+kind+'_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_seconds=0.,max_combined_new_scope_seconds=LIMIT,no_new_budget_or_ledger=True,source_SHA='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1');put(C,v);active=True;return now
 def account(end=False):
  nonlocal active,charged
  v=json.loads(C.read_bytes());a=v['active_segment'];assert a['owner_parent_pid']==os.getpid();now=time.time();dt=now-a['accounted_through_epoch'];assert dt>=0;a['charged_seconds']+=dt;a['accounted_through_epoch']=now;v['charged_training_seconds']+=dt;v['remaining_training_seconds']-=dt
  if end:a['ended_epoch']=now;a['actual_child_wait_exit']=child.returncode;charged+=a['charged_seconds'];rows.append(dict(a));v['completed_segments'].append(a);v['active_segment']=None;active=False
  assert abs(v['charged_training_seconds']+v['remaining_training_seconds']-1188000)<1e-5;put(C,v)
 def spawn(mode):
  task=json.loads((J/'TASK_CURB35.json').read_bytes());env=dict(os.environ)
  for k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
  for n in ('home','tmp','cache','config','data'):(J/n).mkdir(exist_ok=True)
  env.update(CUDA_VISIBLE_DEVICES=task['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',HOME=str(J/'home'),TMPDIR=str(J/'tmp'),XDG_CACHE_HOME=str(J/'cache'),XDG_CONFIG_HOME=str(J/'config'),XDG_DATA_HOME=str(J/'data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
  p=subprocess.Popen([PY,'-u','-B',str(B/'curb35_worker.py'),'--mode',mode],cwd=B,env=env,stdout=(J/(mode+'.log')).open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(B/(mode+'_STARTED_ACTUAL.json'),ident(p.pid));return p
 try:
  for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
   f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  assert json.loads(C.read_bytes())['active_segment'] is None;put(B/'OWNER_IDENTITY.json',ident(os.getpid()))
  budget_start('DISCARDED128x2');child=spawn('precheck128')
  while child.poll() is None:account();put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),phase='discarded128x2',child=ident(child.pid),original_canonical_active=True));time.sleep(3)
  account(True);put(B/'PRECHECK128_EXIT_ACTUAL.json',dict(epoch=time.time(),exit=child.returncode))
  assert child.returncode==0 and not list((J/'precheck128').glob('WORKER_ORIGINAL_ERROR*.json'))
  p=json.loads((J/'precheck128/FINAL.json').read_bytes());assert p['passed'] and p['discarded'] and p['final']['Adam_step']==660440
  child=spawn('native20k_then_production');out=J/'native20k_then_production';cpu=False;go=False;started=time.time()
  while child.poll() is None:
   if (out/'NATIVE144_COMPLETE.json').exists() and not cpu:
    cpu=True;r=subprocess.run([PY,'-B',str(B/'verify_CURB35_native_CPU.py'),'--job','0'],cwd=B,env={**os.environ,'CUDA_VISIBLE_DEVICES':''},capture_output=True,text=True);put(B/'NATIVE_CPU_COMMAND_ACTUAL.json',dict(epoch=time.time(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Independent native CPU rejected; no learning'))
   if (out/'INDEPENDENT_NATIVE_CPU_ADMITTED.json').exists() and not go:
    assert json.loads((out/'INDEPENDENT_NATIVE_CPU_ADMITTED.json').read_bytes())['passed'];remaining=LIMIT-charged;assert remaining>HEADROOM+300;start=budget_start('DISCARDED20k4_THEN_PRODUCTION');put(out/'GO_LEARN.json',dict(learning_started_epoch=start,save_deadline=start+remaining-HEADROOM,combined_limit_seconds=LIMIT,already_charged128_seconds=charged,exit_headroom_seconds=HEADROOM));go=True
   if active:account()
   put(B/'OWNER_CURRENT.json',dict(epoch=time.time(),phase='native20k_then_production',child=ident(child.pid),native_CPU_done=cpu,learning_admitted=go,already_closed_precheck_cost=charged,original_canonical_active=active))
   if time.time()-started>1700 and not go and not (out/'STOP_AFTER_SAVE.json').exists():put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Finite native admission timeout; no PPO'))
   time.sleep(3)
  if active:account(True)
  put(B/'PRODUCTION_CHILD_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=child.pid,exit=child.returncode,actual_waited=True));assert child.returncode==0 and not list(out.glob('WORKER_ORIGINAL_ERROR*.json'))
  final=json.loads((out/'FINAL.json').read_bytes());assert final['passed'] and final['final']['phase']=='production'
  put(B/'OWNER_FINAL.json',dict(epoch=time.time(),final=final,original_canonical_intervals=rows,total_actual_learning_seconds=charged,nominal2700_bound_passed=charged<=LIMIT,no_automatic_new_window=True))
 except BaseException:
  put(B/'OWNER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_not_falsely_cleared=active))
  if child and child.poll() is None:
   out=J/('native20k_then_production' if (J/'native20k_then_production').exists() else 'precheck128');put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own finite owner exception; save-stop only'))
   while child.poll() is None:
    if active:account()
    time.sleep(3)
  if active:account(True)
  raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  put(B/'OWNER_EXIT_ACTUAL.json',dict(epoch=time.time(),canonical_settled=not active,own_locks_released=True))
def main():
 assert '--execute-new-CURB35-finite' in sys.argv;assert not (B/'OWNER_IDENTITY.json').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_owner_pid=pid,root=str(B))),flush=True);return
 os.setsid();f=os.open(str(B/'OWNER_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);owner()
if __name__=='__main__':main()
