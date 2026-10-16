from pathlib import Path
import tempfile,json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'isaac/mod4'))
from types import SimpleNamespace
import torch
from clock_training_health import ClockTrainingHealth,learning_health_pass

tests=[]
class Env:
 def __init__(self):
  self.num_envs=3;self.device='cpu';self.physics_dt=.0025;self.step_dt=.01
  self._integrated_contact=SimpleNamespace(tick=0);self._mod4_max_closure=.001;self._mod4_max_mimic=.001
  self.next_term=None
  tm=SimpleNamespace(active_terms=['time_out','bad_orientation','base_contact','closure','mimic','low_base'])
  tm.flags={n:torch.zeros(3,dtype=torch.bool) for n in tm.active_terms}
  tm.terminated=torch.zeros(3,dtype=torch.bool);tm.get_term=lambda n:tm.flags[n]
  self.termination_manager=tm
  data=SimpleNamespace(root_state_w=torch.zeros(3,13),joint_pos=torch.zeros(3,30),joint_vel=torch.zeros(3,30))
  self.scene={'robot':SimpleNamespace(data=data)}
 def step(self,a):
  self._integrated_contact.tick+=4
  tm=self.termination_manager
  for v in tm.flags.values():v.zero_()
  tm.terminated.zero_()
  if self.next_term:
   tm.flags[self.next_term][1]=True
   if self.next_term!='time_out':tm.terminated[1]=True
   self.next_term=None
  return 'same_step_result'
def run(e,n=24):
 for _ in range(n):assert e.step(torch.zeros(3,6))=='same_step_result'
def check(ok,name):assert ok,name;tests.append(name)
with tempfile.TemporaryDirectory() as t:
 for term in ('bad_orientation','base_contact','low_base','time_out'):
  d=Path(t)/term;d.mkdir();e=Env();h=ClockTrainingHealth(e,d);e.next_term=term;run(e)
  v=h.write();check(not (d/'STOP_AFTER_SAVE').exists(),term+'_does_not_stop_global_training')
  check(learning_health_pass(v),term+'_integrity_admission_pass')
  check(v['actual_task_reset_events']==(0 if term=='time_out' else 1),term+'_count_preserved')
  if term!='time_out':check(v['last_actual_termination_events'][0]['env_id']==1,term+'_real_env_and_reason_recorded')
 for term in ('closure','mimic'):
  d=Path(t)/term;d.mkdir();e=Env();h=ClockTrainingHealth(e,d);e.next_term=term;run(e)
  check((d/'STOP_AFTER_SAVE').exists() and not learning_health_pass(h.write()),term+'_own_save_stop')
 for name,attr,val in (('closure_limit','_mod4_max_closure',.00201),('mimic_limit','_mod4_max_mimic',.01001)):
  d=Path(t)/name;d.mkdir();e=Env();h=ClockTrainingHealth(e,d);setattr(e,attr,val);run(e)
  check((d/'STOP_AFTER_SAVE').exists() and not learning_health_pass(h.write()),name+'_unchanged_hard_limit')
 d=Path(t)/'nonfinite';d.mkdir();e=Env();h=ClockTrainingHealth(e,d);e.scene['robot'].data.joint_vel[0,0]=float('nan');run(e)
 check((d/'STOP_AFTER_SAVE').exists() and not learning_health_pass(h.write()),'nonfinite_stop')
 d=Path(t)/'periodic';d.mkdir();e=Env();h=ClockTrainingHealth(e,d);run(e,600)
 check((d/'CLOCK_TRAINING_HEALTH.json').exists(),'active_periodic_health_is_written')
 v=h.write();v['actual_physics_callbacks']-=1;check(not learning_health_pass(v),'callback_loss_rejected')
 v=h.write();v['termination_reason_coverage_exact']=False;check(not learning_health_pass(v),'unaccounted_termination_rejected')
print(json.dumps(dict(passed=True,contracts=tests,count=len(tests),no_GPU_or_PPO=True)))
