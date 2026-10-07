import torch,json
from feedback_delay_mild import FeedbackDelay,WIDTHS
torch.set_num_threads(1);passed=[];s=FeedbackDelay(12,'cpu',5);global0=torch.random.get_rng_state().clone();s.reset(torch.arange(12))
assert torch.equal(global0,torch.random.get_rng_state());passed.append('independent_episode_latency_rng')
s.delay[:6]=0;s.delay[6:]=1
for tick in range(5):
 for k,d in WIDTHS.items():
  x=torch.full((12,d),float(tick));out=s.apply(k,x,tick)
  assert torch.equal(out[:6],x[:6]) and torch.equal(out[6:],torch.full((6,d),float(max(0,tick-1))))
  receipt=s.receipt(k,tick);assert receipt['actual_age_us'][:6].sum()==0
  assert bool((receipt['actual_age_us'][6:]==(0 if tick==0 else 10000)).all())
passed+=['zero_latency_exact_all_five_raw_channels','one_control_tick_is_10000us_not_physics_step','new_episode_warmup_actual_age_zero_disclosed']
snap=s.state_dict();k='leg_pos';out=s.apply(k,torch.full((12,4),999.),4);assert torch.equal(out,snap['cache'][k]['out']);passed.append('same_tick_cached_once')
others=torch.tensor([0,2,3,4,6,7,8,9,10,11]);s.reset(torch.tensor([1,5]));s.apply(k,torch.full((12,4),90.),4)
assert all(torch.equal(s.cache[k][name][others],value[others]) for name,value in snap['cache'][k].items());passed.append('selected_reset_same_tick_other_rows_exact')
assert bool((s.receipt(k,4)['actual_age_us'][[1,5]]==0).all());passed.append('selected_reset_no_old_episode_values')
t=FeedbackDelay(12,'cpu',999);t.load_state_dict(s.state_dict())
for k,d in WIDTHS.items():assert torch.equal(s.apply(k,torch.full((12,d),5.),5),t.apply(k,torch.full((12,d),5.),5))
s.reset(torch.tensor([2,7]));t.reset(torch.tensor([2,7]));assert torch.equal(s.delay,t.delay);passed.append('full_queue_rng_episode_roundtrip')
off=FeedbackDelay(12,'cpu',9,False);off.reset(torch.arange(12))
for k,d in WIDTHS.items():
 x=torch.arange(12*d).reshape(12,d).float();assert off.apply(k,x,0) is x
passed.append('off_returns_clean_input_without_touching_it')
try:s.apply('base_ang_vel',torch.zeros(12,3),8)
except AssertionError:passed.append('skipped_sample_timestamp_rejected')
else:raise AssertionError('Skipped samples accepted')
try:s.apply('leg_pos',torch.full((12,4),float('nan')),6)
except AssertionError:passed.append('nonfinite_actual_feedback_rejected')
else:raise AssertionError('Nonfinite accepted')
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,contracts=passed,count=len(passed),no_CUDA_initialized=True,only_CPU_component=True,SDK_or_training_deployed=False)))
