"""One local CURB admission; wait actual original owner handoff before any PPO charge."""
from pathlib import Path
import os,sys,time,json,hashlib,traceback,fcntl,psutil
import three_expert_helpers_v2 as b
B=Path(__file__).resolve().parent;C=b.C;put=b.put
def main(cfg):
 assert cfg['key']=='curb' and cfg['max_parent_seconds']==1800 and cfg['native_controls']==144 and len(str(B/'job0/tmp'))<100;b.validate_payload(cfg);children=[];locks=[];private=None;active=False;p=None;phase='native';row={};go={};begin=time.time()
 def account(end=False):
  nonlocal active
  c=b.read(C);a=c['active_segment'];assert a['owner_parent_pid']==os.getpid();c,a=b.charge_values(c,a,go,dict(curb=row),time.time());c['active_segment']=a
  if end:
   assert row.get('terminal_all_own_children_waited') and p.poll() is not None;a['ended_epoch']=time.time();a['actual_terminal_rows']=dict(curb=row);c['completed_segments'].append(a);c['active_segment']=None;active=False
  put(C,c)
 try:
  put(B/'PARENT_IDENTITY.json',b.ident(os.getpid()));private=(B/'OWN_SOURCE_GPU_VALIDATION.lock').open('xb+');fcntl.flock(private,fcntl.LOCK_EX|fcntl.LOCK_NB);v=b.read(Path(cfg['previous_case'])/'job0/native_WAITED_EXIT_ACTUAL.json');assert v['actual_waited'] and v['returncode']==0
  for q in psutil.process_iter(['pid','cmdline']):
   try:assert not any(cfg['previous_case']+'/' in s for s in q.info['cmdline'] or [])
   except psutil.Error:pass
  owner=psutil.Process(576492);assert abs(owner.create_time()-1792163115.08)<.01 and any('/v9/curb/three_expert_finite_owner_node_v9.py' in s for s in owner.cmdline());put(B/'KNOWN_EXISTING_ORIGINAL_OWNER_NATIVE_OVERLAP_NO_ACCOUNTING_ACTUAL.json',dict(epoch=time.time(),known_original_owner=b.ident(owner.pid),native_has_no_canonical_write=True,independent_source_GPU_only_previous_case_all_processes_out=True,one_local_next_owner_no_host_coordinator_or_watcher=True))
  p=b.spawn(cfg,'native');children.append(p)
  while p.poll() is None:
   put(B/'PARENT_CURRENT.json',dict(epoch=time.time(),phase='native',worker=b.ident(p.pid),native_CPU=None,PPO_granted=False));time.sleep(3)
  row=b.state(cfg,'native',p);assert row['returncode']==0 and row['final'] and row['final']['passed'] and not row['errors'],row;native=b.native_CPU(cfg);put(B/'OWN_NATIVE_CPU_ADMITTED_ACTUAL.json',native);phase='waiting_original_owner_actual_complete_and_locks'
  while True:
   assert time.time()-begin<7200,'Finite native and original owner handoff wait expired; no new automatic window';c=b.read(C)
   put(B/'PARENT_CURRENT.json',dict(epoch=time.time(),phase=phase,native_CPU_SHA=native['SHA'],original_active_owner=(c['active_segment'] or {}).get('owner_parent_pid'),PPO_granted=False))
   if c['active_segment'] is not None:time.sleep(6);continue
   attempt=[]
   try:
    for q in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
     f=q.open('rb+');attempt.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:
    for f in attempt:f.close()
    time.sleep(6);continue
   locks=attempt;c=b.read(C);assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7 and c['remaining_training_seconds']>1800+9400.860692501068+64800;break
  now=time.time();grant=dict(learning_started_epoch=now,save_deadline=now+1500,nominal_end_epoch=now+1800,max_parent_seconds=1800,exit_headroom_seconds=300,source_SHA=cfg['source_SHA'],source_native_CPU_SHA=native['SHA'],original_owner_pid=os.getpid(),original_owner_creation=b.ident(os.getpid())['creation']);go['curb']=grant
  c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_CURB275_INTERMEDIATE_BRIDGE_NATIVE_ADMITTED_1800_'+str(time.time_ns()),started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},charge_contract='Original single writer only after actual previous owner handoff; own production loadlearnsaveclosechildwait actual interval once.');put(C,c);active=True;put(B/'GO_PRODUCTION_ACTUAL.json',grant);phase='production';p=b.spawn(cfg,phase);children.append(p)
  while True:
   row=b.state(cfg,phase,p)
   if p.poll() is not None:row.update(terminal_all_own_children_waited=True)
   account();put(B/'PARENT_CURRENT.json',dict(epoch=time.time(),phase=phase,row=row,go=grant,original_two_fcntl_held=True))
   if p.poll() is not None:break
   if time.time()>=grant['save_deadline']:put(b.outdir('curb','production')/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own original1800 finite saved-stop no signal'))
   time.sleep(3)
  account(True);assert row['returncode']==0 and row['final'] and row['final']['passed'] and not row['errors'],row;put(B/'PARENT_FINAL.json',dict(epoch=time.time(),passed=True,row=row,own_actual_cost_settled=True))
 except BaseException:
  put(B/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_false_preserved=True))
  if p and p.poll() is None:
   out=b.outdir('curb',phase if phase=='production' else 'native');out.mkdir(exist_ok=True);put(out/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own parent exception fullprefix saved-stop'))
  if p:p.wait()
  if active:row=b.state(cfg,'production',p);row.update(terminal_all_own_children_waited=True);account(True)
  raise
 finally:
  for child in children:child.wait()
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
  if private:fcntl.flock(private,fcntl.LOCK_UN);private.close()
  put(B/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),actual_all_own_children_waited=True,own_original_two_fcntl_were_acquired=bool(locks),own_original_two_fcntl_released_if_acquired=True,other_original_owner_may_still_hold_them=True,canonical_not_falsely_cleared=not active))
if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B),native_only_until_actual_original_lock_handoff=True)),flush=True)
 else:
  os.setsid();f=os.open(str(B/'PARENT_CONSOLE.log'),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(f,1);os.dup2(f,2);os.close(f);f=os.open('/dev/null',os.O_RDONLY);os.dup2(f,0);os.close(f);main(cfg)
