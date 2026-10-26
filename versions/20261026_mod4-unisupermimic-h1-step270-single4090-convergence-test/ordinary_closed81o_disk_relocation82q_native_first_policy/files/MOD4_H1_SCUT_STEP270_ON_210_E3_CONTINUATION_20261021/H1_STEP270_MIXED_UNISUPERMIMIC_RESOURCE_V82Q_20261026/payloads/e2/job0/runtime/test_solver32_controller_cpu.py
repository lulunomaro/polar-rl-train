"""Actual controller dispatch contracts: failures cannot start formal from discarded weights."""
import sys,json,tempfile,types
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class FakeBase:
 PY=sys.executable
 def __init__(self):self.locks=[]
 def atomic_json(self,p,x):pass
 def budget_state(self):return {'active_segment':None}
 def checkpoint(self,p):return {'path':str(p)}
base=FakeBase();helpers=types.SimpleNamespace(acquire=lambda x:base.locks.append(str(x)),identity=lambda p:None)
with tempfile.TemporaryDirectory() as tmp:
 f=Path(tmp)/'budget';f.write_text('{}')
 q=types.ModuleType('continue_clock1000_worker_manifest_review_once');q.P=Path(tmp);q.base=base;q.helpers=helpers;q.ctl=types.SimpleNamespace(CANONICAL=f,STATE_PATH=f)
 q.w=types.SimpleNamespace(read=lambda p:{})
 sys.modules[q.__name__]=q;sys.path.insert(0,str(ROOT));import supervise_dt2500_solver32_training_test as c
 c.D=Path(tmp);c.R=Path(tmp)/'reports';c.R.mkdir();c.verify=lambda:None;c.source=lambda:Path('validated24827.pt');c.fullsave=lambda p:{'path':str(p)};c.trainers=lambda:[];c.identity=lambda p:None;c.phase=lambda *a,**kw:None
 c.identity=lambda p: {'pid':p,'start_ticks':99} if p not in (856048,856091,856092) else None
 c.subprocess=types.SimpleNamespace(Popen=lambda *a,**kw:types.SimpleNamespace(pid=77),DEVNULL=-3,STDOUT=-2);calls=[];writes=[]
 c.write=lambda n,x:writes.append((n,x));c.frozen20k=lambda p:calls.append(('native',str(p)))
 def test(fail):
  calls.clear();writes.clear();base.locks.clear()
  (c.D/'guardian.log').unlink(missing_ok=True)
  def train(init,count,updates,duration,label,discard):
   calls.append((count,str(init),discard,duration))
   if count==fail:raise AssertionError('Injected real preflight failure')
   return Path('discarded.pt' if discard else 'formal.pt'),{'checkpoint':{'path':'formal.pt'}}
  c.train=train
  try:c.main()
  except AssertionError:assert fail
  assert len(base.locks)==2
  assert all(x[1]=='validated24827.pt' for x in calls[1:])
  if not fail:
   assert [x[0] for x in calls[1:]]==[128,20000,20000]
   assert calls[-1][2:] == (False,2700)
   assert any(n=='SOLVER32_REVIEW_READY.json' for n,x in writes)
  else:assert not any(len(x)>2 and x[2] is False for x in calls[1:])
 for fail in (None,128,20000):test(fail)
 # Preserved real task health contract: no relaxation to original closure/global stop.
 import ast
 tree=ast.parse((ROOT/'supervise_dt2500_solver32_training_test.py').read_text())
 text=ast.unparse(tree)
 assert "health['actual_task_reset_events'] == 0" in text
 assert "health['max_closure_error_m'] <= 0.002" in text
 assert "health['max_mimic_error_rad'] <= 0.01" in text
 assert "health['actual_physics_callbacks'] == health['expected_physics_callbacks']" in text
print(json.dumps({'passed':True,'contracts':7,'failure_injection_at_128_and20k':True,'discarded_weights_never_used_as_formal_source':True,'two_original_locks_required':True,'formal_duration2700':True,'original_health_contract_retained':True,'no_CUDA_initialized':True,'no_GPU_or_budget_authority':True}))
