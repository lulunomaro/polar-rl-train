"""Add actual exit/locks/unique-account closeout to the prepared own-formal CPU reader."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'read_entry_own_formal_cpu_actual.py').read_text()
anchor="assert not torch.cuda.is_initialized()\nprint(json.dumps(dict(epoch=time.time(),formal_complete=True"
extra='''assert not torch.cuda.is_initialized()
import fcntl
owner=own.identity(st['owner']['pid']);guardian=own.identity(j(R/'E1_GUARDIAN_STARTED.json')['pid']);child=own.identity(rec['pid'])
gone=lambda actual,expected:actual is None or actual['state']=='Z' or actual['start_ticks']!=expected
owner_gone=gone(owner,st['owner']['start_ticks']);guardian_gone=gone(guardian,j(R/'E1_GUARDIAN_STARTED.json')['start_ticks']);child_gone=child is None or child['state']=='Z'
locks=[]
for q in (own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock'):
 with q.open('r') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:free=False
  else:free=True;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(q),actual_fcntl_free=free))
budget=j(own.s.q.ctl.CANONICAL);segments=[x for x in budget['completed_segments'] if x['pid']==rec['pid']]
assert len(segments)==1 and segments==row['unique_completed_segment']
closeout=owner_gone and guardian_gone and child_gone and all(x['actual_fcntl_free'] for x in locks) and budget['active_segment'] is None and not j(own.s.q.ctl.STATE_PATH).get('active_training') and st['phase']=='E1_WAVE50_entry_saved_review_ready'
print(json.dumps(dict(epoch=time.time(),passed=True,closeout_ready=closeout,actual_source_count=410,actual_finite_tensor_count=info['finite_tensors'],two_fcntl_locks=locks,actual_parent_guardian_child_exits=closeout,unique_accounted_segment=segments,formal_complete=True'''
assert s.count(anchor)==1;s=s.replace(anchor,extra)
exec(compile(s,'<own410-final-closeout-CPU-reader>','exec'),{'__file__':str(D/'read_entry_own_formal_cpu_actual.py'),'__name__':'__main__'})
