"""CPU-only handover: old controller settles its own segment; never writes ledger."""
from pathlib import Path
import os,sys,json,time,signal,subprocess,traceback
D=Path('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008');R=D/'reports';CODE=D/'isaac/mod4';RD=Path(__file__).resolve().parent;RR=RD/'reports';OLD=Path('/home/egde/rl_candidates/MOD4_D3_1MS_FULL_CONTRACT_20261008')
sys.path.insert(0,str(D));sys.path.insert(0,str(CODE))
import supervise_closure_episode_continuation as w
read=w.read
def write(n,v):
 w.s.q.base.atomic_json(RR/n,v)
 if n not in ('SWITCH_STARTED.json','SWITCH_ATTENTION.json'):w.s.q.base.atomic_json(R/n,v)
def same(row):
 a=w.identity(row['pid']);return a if a and a['start_ticks']==row['start_ticks'] and a['state']!='Z' else None
def own_stop(a):
 child=w.identity(a['pid'])
 if not child or child['state']=='Z':return # The owning parent uniquely settles this exited child; no ledger mutation.
 assert child['argv'][1]==str(OLD/'isaac/mod4/train_delay_resume_ppo.py')
 name=child['argv'][child['argv'].index('--run_name')+1];runs=list((OLD/'learning_logs').glob('*_'+name))
 if not runs or not (runs[0]/'run_manifest.json').exists():return
 run=runs[0];manifest=read(run/'run_manifest.json');assert manifest['source_map']==read(OLD/'reports/SOURCE_FREEZE.json')['sha256']
 rec=read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None
 if rec:assert rec['pid']==child['pid'];w.fullsave(Path(rec['checkpoint']))
 # Request at the actual PID-bound run; the trainer creates its own complete final save before exit.
 stop=run/'STOP_AFTER_SAVE'
 if not stop.exists():stop.write_text('Human-authorized saved boundary switch: known2.5ms/32-4; no repeated45min trial\n')
 write('OWN_FULL_SAVE_REQUESTED.json',dict(epoch=time.time(),actual_trainer=child,run=str(run),own_receipt=rec,old_controller_keeps_unique_accounting=True,no_force_kill=True))
def main():
 import torch;torch.set_num_threads(1)
 assert not (RR/'SWITCH_STARTED.json').exists();assert (R/'SWITCH_ATTENTION.json').exists();w.verify()
 parent=read(OLD/'reports/D3_DISPATCH_STARTED.json')['owner'];guard=read(OLD/'reports/D3_GUARDIAN_STARTED.json')
 write('SWITCH_STARTED.json',dict(epoch=time.time(),owner=w.identity(os.getpid()),old_parent=parent,old_guardian=guard,canonical_write_authority=False))
 limit=time.time()+1200
 while True:
  assert time.time()<limit,'Saved boundary timeout; no blind clear/restart'
  assert not (OLD/'reports/D3_ATTENTION.json').exists(),'Old actual integrity failure requires audit'
  a=w.s.q.base.budget_state()['active_segment'];actual=same(parent)
  if a:
   own_stop(a);time.sleep(.1);continue
  assert not read(w.s.q.ctl.STATE_PATH).get('active_training')
  if not actual:break
  assert actual['argv'][1]==str(OLD/'supervise_d3_saved_boundary.py') and actual['ppid']==1
  os.kill(parent['pid'],signal.SIGSTOP)
  for _ in range(100):
   actual=same(parent)
   if actual and actual['state']=='T':break
   time.sleep(.01)
  assert actual and actual['state']=='T','No confirmed launch hold'
  a=w.s.q.base.budget_state()['active_segment']
  if a or w.trainers():
   # A launch raced the observed empty boundary. Protect its own save, restore
   # only this verified parent so it can finish exactly once, then retry.
   write('BOUNDARY_LAUNCH_RACE_RETAINED.json',dict(epoch=time.time(),active=a,no_budget_mutation=True))
   os.kill(parent['pid'],signal.SIGCONT);time.sleep(.1);continue
  break
 rows=[read(p) for p in (OLD/'reports').glob('d3_formal_block*_PASSED.json')]
 assert rows,'No completed formal D3 source; do not select preflight'
 row=max(rows,key=lambda x:x['epoch']);run=Path(row['run']);rec=read(run/'latest_complete.json');assert rec==row['own_PID_bound_receipt']
 assert row['health']['integrity_task_reset_events']==0 and row['health']['nonfinite_observed'] is False
 assert row['health']['actual_physics_callbacks']==row['health']['expected_physics_callbacks'] and row['actual_updates']>0
 oldf=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];m=read(run/'run_manifest.json');assert m['source_map']==oldf and read(run/'rolling_source_freeze.json')['sha256']==oldf
 for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
 assert w.fullsave(Path(rec['checkpoint']))==row['checkpoint']
 ledger=read(w.s.q.ctl.CANONICAL);seg=[s for s in ledger['completed_segments'] if s['pid']==rec['pid']];assert seg==row['unique_completed_segment'] and len(seg)==1 and ledger['active_segment'] is None
 assert not w.trainers() and not read(w.s.q.ctl.STATE_PATH).get('active_training')
 write('SAVED_BOUNDARY_SOURCE.json',row)
 before=w.s.q.ctl.CANONICAL.read_bytes()
 if same(parent):
  assert same(parent)['state']=='T' and not w.trainers()
  os.kill(parent['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGCONT)
 for _ in range(400):
  if not same(parent) and not same(guard):break
  time.sleep(.1)
 assert not same(parent) and not same(guard),'Old launch owner/guardian not retired'
 assert not w.trainers() and w.s.q.base.budget_state()['active_segment'] is None and not read(w.s.q.ctl.STATE_PATH).get('active_training')
 assert before==w.s.q.ctl.CANONICAL.read_bytes(),'No handover budget transaction permitted'
 write('HANDOVER_COMPLETED.json',dict(epoch=time.time(),old_parent=parent,old_guardian=guard,old_actual_segment=seg,old_source=row['checkpoint'],old_controller_settled_once=True,canonical_bytes_exact_after_saved_boundary=True,new_budget_seconds=0,old_launch_permission_retired=True,requested_save_not_force_kill=True))
 env=dict(os.environ,PYTHONPATH=str(D)+os.pathsep+str(CODE))
 with (D/'controller.log').open('x') as f:p=subprocess.Popen([w.s.q.base.PY,str(D/'supervise_closure_episode_continuation.py')],cwd=w.s.q.P,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('CONTINUATION_LAUNCHED.json',dict(epoch=time.time(),owner=w.identity(p.pid),source=row['checkpoint'],planned_block_seconds=7200,no_new45min_trial=True,new_budget_seconds=0))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('SWITCH_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),actual_active=w.s.q.base.budget_state()['active_segment'],no_blind_clear_or_restart=True));raise
