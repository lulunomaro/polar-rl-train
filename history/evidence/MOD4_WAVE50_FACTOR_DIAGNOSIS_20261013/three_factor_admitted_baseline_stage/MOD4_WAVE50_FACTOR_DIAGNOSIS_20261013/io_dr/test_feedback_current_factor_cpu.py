"""Real source SensorCorruption/FeedbackDelay CPU fixture; no SDK or GPU initialization."""
from pathlib import Path
import ast,hashlib,json,sys,time,types,traceback
import torch
D=Path(__file__).resolve().parent;W=D.parents[1];R=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/runtime/isaac/mod4'
sys.path.insert(0,str(R))
from sensor_mild_math import SensorCorruption,CHANNELS
from feedback_delay_mild import FeedbackDelay
from feedback_current_factor import install
torch.set_num_threads(1)

def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def source_feedback_module(env):
 p=R/'feedback_delay_runtime.py';t=ast.parse(p.read_text(encoding='utf-8-sig'))
 f=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='feedback'];assert len(f)==1
 globals_dict=dict(sensor_state=lambda e:e.sensor,delay_state=lambda e:e.delay)
 exec(compile(ast.Module(body=f,type_ignores=[]),str(p),'exec'),globals_dict)
 module=types.SimpleNamespace(feedback=globals_dict['feedback'],sensor_state=globals_dict['sensor_state'],delay_state=globals_dict['delay_state'],__file__=str(p))
 return module
def main():
 a=types.SimpleNamespace(common_step_counter=0,sensor=SensorCorruption(8,'cpu',20260928,'noise_bias_mild_v1'),delay=FeedbackDelay(8,'cpu',20260928,True))
 b=types.SimpleNamespace(common_step_counter=0,sensor=SensorCorruption(8,'cpu',20260928,'noise_bias_mild_v1'),delay=FeedbackDelay(8,'cpu',20260928,True))
 baseline=source_feedback_module(a);treatment=source_feedback_module(b);hook=install(b,treatment)
 same0=0;diff10=0;resets=[]
 for tick in range(24):
  a.common_step_counter=b.common_step_counter=tick
  if tick in (0,7,13):
   ids=torch.arange(8) if tick==0 else torch.tensor([2,5])
   for e in (a,b):e.sensor.reset(ids);e.delay.reset(ids)
   resets.append(dict(tick=tick,envs=ids.tolist()))
  for key,(width,_,_) in CHANNELS.items():
   raw=(torch.arange(8*width,dtype=torch.float32).reshape(8,width)*.017+tick*.013).clone()
   qa=baseline.feedback(a,key,raw);qb=treatment.feedback(b,key,raw)
   # Source delay.cur is the independently retained actual current noisy sample.
   assert torch.equal(qb,b.delay.cache[key]['cur'])
   warm=b.delay.cache[key]['ready'];zero=(b.delay.delay==0)|~warm
   assert torch.equal(qa[zero],qb[zero]);same0+=int(zero.sum())
   if (~zero).any():diff10+=int(bool((qa[~zero]!=qb[~zero]).any()))
   assert exact(a.sensor.state_dict(),b.sensor.state_dict()),'Sensor bias/noise/RNG/cache/count side effects changed'
   assert exact(a.delay.state_dict(),b.delay.state_dict()),'Delay assignment/RNG/cache/queue side effects changed'
   oldS=a.sensor.state_dict();oldD=a.delay.state_dict()
   assert torch.equal(qa,baseline.feedback(a,key,raw)) and torch.equal(qb,treatment.feedback(b,key,raw))
   assert exact(oldS,a.sensor.state_dict()) and exact(oldD,a.delay.state_dict())
   assert exact(a.sensor.state_dict(),b.sensor.state_dict()) and exact(a.delay.state_dict(),b.delay.state_dict())
 assert diff10>0 and hook.max_current_formula_error==0.
 out=D/'FEEDBACK_CURRENT_FACTOR_CPU_PASSED.json';assert not out.exists()
 row=dict(id='D3_current_noisy_feedback_only_CPU_fixture',epoch=time.time(),passed=True,no_SDK_GPU_or_PPO=True,
  source={str(p):H(p) for p in [R/'feedback_delay_runtime.py',R/'sensor_mild_math.py',R/'feedback_delay_mild.py',D/'feedback_current_factor.py',Path(__file__)]},
  controls=24,environments=8,channels=list(CHANNELS),repeated_same_tick_reads=2,selected_episode_resets=resets,
  original_feedback_function_AST_executed=True,sensor_complete_state_and_RNG_exact_after_each_call=True,delay_complete_state_and_RNG_exact_after_each_call=True,
  independent_current_sample_equal_to_actual_source_delay_cur=True,zero_delay_or_warmup_samples_exact=same0,nonzero_delay_difference_channel_calls=diff10,
  production_validator_not_changed=True,GPU_factor_not_yet_run=True,hook_receipt=hook.receipt(),
  original_sensor_sdk_audit_scope='Original audit assumes queued output and remains unchanged; factor harness must use this current-vs-originalqueue-input binding as independent diagnostic output audit, never mark original queued audit PASSED for changed output.')
 out.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(row,ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('FEEDBACK_CURRENT_CPU_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_sha=H(Path(__file__)),preGPU=True),indent=2),encoding='utf-8');raise
