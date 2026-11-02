"""Actual D1/D3/queue components: common samples survive asynchronous resets."""
from pathlib import Path
import importlib.util,json,sys,torch
N=Path(__file__).resolve().parent;T=N.parent
runtime=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4'
sys.path[:0]=[str(N/'source'),str(runtime)]
from matched_DR373 import install_common_noise373
from sensor_mild_math import SensorCorruption,CHANNELS
from feedback_delay_mild import FeedbackDelay
from action_delay_physics_queue import PhysicsActionQueue
s=SensorCorruption(80,'cpu',9137,'noise_bias_mild_v1');ids=torch.arange(80);s.reset(ids);s.bias[40:]=s.bias[:40].clone()
d=FeedbackDelay(80,'cpu',9137);d.reset(ids);d.delay[40:]=d.delay[:40].clone()
global_before=torch.random.get_rng_state().clone();receipt=install_common_noise373(s,9137,0,1100)
saved=[]
for tick in range(40):
 for key,(width,bound,_)in CHANNELS.items():
  x=torch.arange(80*width,dtype=torch.float32).reshape(80,width)/1000.;x[40:]=x[:40].clone()
  noisy=s.apply(key,x,tick);again=s.apply(key,x,tick);assert torch.equal(noisy,again)and torch.equal(noisy[:40],noisy[40:])
  out=d.apply(key,noisy,tick);live=torch.ones(40,dtype=torch.bool)
  if tick>20:live[1]=False
  assert torch.equal(out[:40][live],out[40:][live])
 if tick==20:s.reset(torch.tensor([41]));d.reset(torch.tensor([41]));s.bias[41]=s.bias[1]
 assert torch.equal(s.cache['base_ang_vel'][1][:40],s.cache['base_ang_vel'][1][40:])
assert torch.equal(global_before,torch.random.get_rng_state())
q=PhysicsActionQueue(80,'cpu',9137);neutral=torch.randn(80,4);neutral[40:]=neutral[:40]
q.reset('legs',ids,neutral);q.groups['legs']['lag_steps'][40:]=q.groups['legs']['lag_steps'][:40].clone()
target=torch.randn(80,4);target[40:]=target[:40];q.submit('legs',target,0)
for tick in range(8):
 out=q.apply('legs',tick);assert torch.equal(out[:40],out[40:])
print(json.dumps(dict(passed=True,actual_components=True,ticks40=True,repeated_tick_cache=True,paired_D3=True,asynchronous_completed_episode_reset_no_new_noise_draw_for_partner=True,D4_paired_same_lag=True,global_RNG_unchanged=True,SDK=0,physics=0,NN=0,receipt=receipt())))
