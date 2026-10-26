from pathlib import Path
import importlib.util,json,time,traceback
from types import SimpleNamespace
import torch
F=Path(__file__).resolve().parent;R=F/'reports';A=F/('cpu_phase_attempt_'+str(time.time_ns()));A.mkdir()
spec=importlib.util.spec_from_file_location('phase_source',F/'source/native_policy_phase_coverage_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results=[]
def case(name,fn):
 try:fn();results.append(dict(name=name,passed=True))
 except BaseException:results.append(dict(name=name,passed=False,error=traceback.format_exc()))

def count_boundaries():
 d=m.NativePolicyPhaseCoverage(A/'boundary.json',window_start_iteration=68)
 d.record([0,49,50,84,99,100,135,136,179,180],iteration=68,horizon=16)
 s=d.snapshot();assert list(s['bands'].values())==[2,3,2,2,1] and s['imagined_horizon_intersects_request']==5
 assert s['counts_attempted_starts_not_completed_optimizer_updates'] and s['not_a_training_or_model_or_skill_gate']

class Carrier:
 def __init__(self,frames):
  self.iteration=68;self.cfg=SimpleNamespace(horizon=16);self.result=({'f':frames,'sentinel':object()},{'history':object()});self.calls=0
 def _sample_valid_starts(self,batch):self.calls+=1;return self.result

def forwarding():
 c=Carrier(torch.tensor([95,100,160,300]));old=c.result
 d=m.attach_optional_policy_phase_coverage(c,A/'forward.json')
 result=c._sample_valid_starts(4)
 assert result is old and result[0] is old[0] and result[1] is old[1] and c.calls==1
 assert d.calls==1 and d.samples==4

def rng_exact():
 class RandomCarrier(Carrier):
  def _sample_valid_starts(self,batch):return ({'f':torch.randint(0,400,(batch,))},{'history':object()})
 c=RandomCarrier(torch.tensor([]));torch.manual_seed(20261026);before=torch.random.get_rng_state().clone()
 original=c._sample_valid_starts(32)[0]['f'];expected=torch.random.get_rng_state().clone()
 torch.random.set_rng_state(before);m.attach_optional_policy_phase_coverage(c,A/'rng.json')
 actual=c._sample_valid_starts(32)[0]['f'];assert torch.equal(original,actual) and torch.equal(expected,torch.random.get_rng_state())

def original_error():
 failure=RuntimeError('original sampler failure')
 c=Carrier(torch.tensor([100]))
 def fail(batch):raise failure
 c._sample_valid_starts=fail;d=m.attach_optional_policy_phase_coverage(c,A/'original_error.json')
 try:c._sample_valid_starts(1)
 except RuntimeError as error:assert error is failure
 else:raise AssertionError('masked original failure')
 assert d.calls==0 and not (A/'original_error.json').exists()

def optional_transfer_error():
 class BadFrames:
  def detach(self):raise RuntimeError('optional CPU transfer failure')
 c=Carrier(BadFrames());d=m.attach_optional_policy_phase_coverage(c,A/'transfer_error.json')
 assert c._sample_valid_starts(1) is c.result and not d.valid and d.errors

def io_failure():
 path=A/'occupied_directory.json';path.mkdir();c=Carrier(torch.tensor([100]));d=m.attach_optional_policy_phase_coverage(c,path)
 assert c._sample_valid_starts(1) is c.result and d.io_errors and d.samples==1

def invalid_rows():
 d=m.NativePolicyPhaseCoverage(A/'invalid_rows.json',window_start_iteration=68)
 d.record([100,120],iteration=68,horizon=16)
 for value in ([100,-1],[float('nan')],[True]):d.record(value,iteration=69,horizon=16)
 assert d.calls==1 and d.samples==2 and not d.valid and len(d.errors)==3

def duplicate():
 c=Carrier(torch.tensor([100]));m.attach_optional_policy_phase_coverage(c,A/'duplicate.json')
 try:m.attach_optional_policy_phase_coverage(c,A/'second_duplicate.json')
 except ValueError:pass
 else:raise AssertionError('double instrumentation admitted')

for name,fn in [('boundary_counts_and_horizon',count_boundaries),('identical_objects_forwarded',forwarding),('same_original_CPU_RNG',rng_exact),('original_error_identity_and_no_new_diagnostic',original_error),('optional_transfer_error_nonfatal',optional_transfer_error),('optional_IO_error_nonfatal',io_failure),('invalid_rows_no_partial_counts',invalid_rows),('double_attach_rejected',duplicate)]:case(name,fn)
out=dict(epoch=time.time(),passed=all(x['passed'] for x in results),results=results,scope='synthetic CPU sampler only, no actual model/policy/optimizer/plant/SDK/GPU/remote',actual_target86_installed=False,no_training_or_budget=True)
(A/'PHASE_SAMPLING_READONLY_FORWARDING_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2),'utf8')
print(json.dumps(out));assert out['passed']
