"""Real queue state serialization, rejection and first-admission/reset semantics."""
import torch,json,tempfile,copy,sys,types,os
from pathlib import Path
from types import SimpleNamespace as NS
from feedback_delay_mild import FeedbackDelay,WIDTHS
from feedback_delay_checkpoint import exact,validate_delay_state,restore_delay_exact,resume_delay_new_episode
torch.set_num_threads(1);assert not torch.cuda.is_initialized()
n=12;d=FeedbackDelay(n,'cpu',23,True);d.reset(torch.arange(n));global_rng=torch.random.get_rng_state().clone()
for tick in range(5):
 for key,width in WIDTHS.items():d.apply(key,torch.arange(n*width).reshape(n,width).float()+tick,tick)
saved=d.state_dict();assert validate_delay_state(d,saved)
clone=FeedbackDelay(n,'cpu',999,True);assert restore_delay_exact(clone,saved)
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'queue.pt';torch.save(saved,p);assert restore_delay_exact(clone,torch.load(p,weights_only=False))
for key,width in WIDTHS.items():
 x=torch.full((n,width),7.);assert torch.equal(d.apply(key,x,5),clone.apply(key,x,5))
ids=torch.tensor([1,4,7]);d.reset(ids);clone.reset(ids);assert exact(d.state_dict(),clone.state_dict())
assert torch.equal(global_rng,torch.random.get_rng_state())
passed=['all_queue_buffers_and_episode_RNG_serialized_exact','disk_roundtrip_exact','next_sample_after_restore_exact','selected_reset_after_restore_exact','global_RNG_untouched']
for mutate in (lambda s:s.update(n=13),lambda s:s['delay'].fill_(2),lambda s:s['cache'].pop('base_ang_vel'),lambda s:s['cache']['leg_pos']['cur'].fill_(float('nan')),lambda s:s['cache']['leg_vel']['sample_tick'].fill_(999)):
 bad=copy.deepcopy(saved);mutate(bad)
 try:validate_delay_state(clone,bad)
 except AssertionError:pass
 else:raise AssertionError('Invalid queue checkpoint accepted')
passed.append('incompatible_shape_range_missing_channel_nonfinite_and_timestamp_rejected')

# Exercise the actual D3 orchestration around an explicit CPU stand-in for the
# already-tested sensor restore/physics reset. This is not an Isaac SDK claim.
sys.modules['feedback_delay_runtime']=NS(delay_state=lambda env:env.delay)
def reset_sensor(runner,env,path,folder):
 before=env.delay.episode.clone();env.delay.reset(torch.arange(n));env.common_step_counter+=1
 for key,width in WIDTHS.items():env.delay.apply(key,torch.zeros(n,width),env.common_step_counter)
 assert torch.equal(env.delay.episode,before+1)
 return dict(source_sha256='CPU-fixture')
sys.modules['sensor_resume_contract']=NS(resume_sensor_new_episode=reset_sensor)
recipe=dict(profile='control_0_10ms_v1');env=NS(delay=clone,common_step_counter=5,feedback_delay_recipe=lambda:recipe)
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'full.pt';torch.save(dict(feedback_delay_state=saved,feedback_delay_recipe=recipe),p)
 row=resume_delay_new_episode(None,env,p,td);assert row['delay_state_and_RNG_exactly_restored_before_reset']
 torch.save(dict(sensor_DR_state={},sensor_recipe=dict(profile='noise_bias_mild_v1')),p)
 os.environ.pop('RM_DELAY_INITIAL_ADMISSION',None)
 try:resume_delay_new_episode(None,env,p,td)
 except AssertionError:pass
 else:raise AssertionError('Unmarked predecessor accepted')
 os.environ['RM_DELAY_INITIAL_ADMISSION']='D1D2_to_D3';row=resume_delay_new_episode(None,env,p,td)
 assert row['explicitly_new_D3_stream'] and not row['delay_state_and_RNG_exactly_restored_before_reset']
passed+=['restore_before_one_reset_new_episode_warmup_exact','unmarked_missing_delay_state_rejected','first_D1D2_admission_explicit_no_fake_resume']
assert not torch.cuda.is_initialized();print(json.dumps(dict(passed=True,contracts=passed,count=len(passed),CPU_fixture_not_SDK=True,no_CUDA_initialized=True)))
