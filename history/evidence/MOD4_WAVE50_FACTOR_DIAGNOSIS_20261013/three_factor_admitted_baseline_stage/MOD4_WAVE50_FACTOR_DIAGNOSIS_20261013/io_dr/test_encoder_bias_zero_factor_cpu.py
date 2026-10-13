"""D2 factor real-source CPU paired fixture, including physicalepisode queuewarmup."""
from pathlib import Path
import hashlib,json,time,traceback
import torch
from test_feedback_current_factor_cpu import source_feedback_module,SensorCorruption,FeedbackDelay,CHANNELS,types,exact,R
from encoder_bias_zero_factor import install
D=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=types.SimpleNamespace(common_step_counter=0,sensor=SensorCorruption(8,'cpu',20260928,'noise_bias_mild_v1'),delay=FeedbackDelay(8,'cpu',20260928,True))
 b=types.SimpleNamespace(common_step_counter=0,sensor=SensorCorruption(8,'cpu',20260928,'noise_bias_mild_v1'),delay=FeedbackDelay(8,'cpu',20260928,True))
 baseline=source_feedback_module(a);treatment=source_feedback_module(b);hook=install(b,treatment)
 fullstatechecks=0;changedleg=0;unchangedother=0;maxformula=0.
 for tick in range(24):
  a.common_step_counter=b.common_step_counter=tick
  if tick in (0,7,13):
   ids=torch.arange(8) if tick==0 else torch.tensor([2,5])
   for e in (a,b):e.sensor.reset(ids);e.delay.reset(ids)
  for key,(width,_,_) in CHANNELS.items():
   raw=torch.arange(8*width,dtype=torch.float32).reshape(8,width)*.017+tick*.013
   qa=baseline.feedback(a,key,raw);qb=treatment.feedback(b,key,raw)
   expected=qa-b.sensor.bias if key=='leg_pos' else qa
   error=float((expected-qb).abs().max());maxformula=max(maxformula,error);assert error==0
   if key=='leg_pos':changedleg+=int(bool((qa!=qb).any()))
   else:assert torch.equal(qa,qb);unchangedother+=1
   assert exact(a.sensor.state_dict(),b.sensor.state_dict()) and exact(a.delay.state_dict(),b.delay.state_dict());fullstatechecks+=1
 assert changedleg==24 and unchangedother==96 and maxformula==0
 report=dict(id='D2_encoder_bias_only_CPU_fixture',epoch=time.time(),passed=True,no_SDK_GPU_PPO=True,
  source={str(p):H(p) for p in [R/'feedback_delay_runtime.py',R/'sensor_mild_math.py',R/'feedback_delay_mild.py',D/'encoder_bias_zero_factor.py',D/'test_feedback_current_factor_cpu.py',Path(__file__)]},
  controls=24,environments=8,complete_original_sensor_and_delay_state_eachcall_exact=fullstatechecks,
  only_leg_pos_changed_calls=changedleg,all_other_channel_output_exact_calls=unchangedother,leg_output_original_queued_minus_fixed_sameepisode_bias_maxerror=maxformula,
  selected_physical_resets_and_warmup_checked=True,production_validator_not_changed=True,GPU_factor_not_yet_run=True,
  queued_output_original_sensor_audit_not_relabelled_as_pass=True,hook_receipt=hook.receipt())
 p=D/'ENCODER_BIAS_ZERO_FACTOR_CPU_PASSED.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('ENCODER_BIAS_CPU_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_sha=H(Path(__file__)),preGPU=True),indent=2),encoding='utf-8');raise
