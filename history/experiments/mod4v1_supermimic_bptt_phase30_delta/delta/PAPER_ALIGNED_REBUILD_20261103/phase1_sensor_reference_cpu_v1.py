"""Real original SensorCorruption/FeedbackDelay CPU reference contract, synthetic input.
No SDK/environment/actor/checkpoint. This does NOT test the unfinished passive tap.
"""
from pathlib import Path
import argparse,json,hashlib,importlib.util,os,random,sys
os.environ['CUDA_VISIBLE_DEVICES']='';sys.dont_write_bytecode=True
PINS={'sensor_mild_math.py':'aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8','feedback_delay_mild.py':'90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()and a.output.parent.is_dir();mods={};sources={}
 for name,sha in PINS.items():
  path=(a.source_dir/name).resolve();raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;sp=importlib.util.spec_from_file_location('_reference_'+path.stem,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);mods[name]=m;sources[name]=dict(path=str(path),bytes=len(raw),SHA256=sha)
 import torch as t
 t.set_num_threads(1);assert not t.cuda.is_initialized();rng=t.random.get_rng_state().clone();prng=random.getstate();S=mods['sensor_mild_math.py'];D=mods['feedback_delay_mild.py'];n=8
 def pair(profile='noise_bias_mild_v1',enabled=True):
  s=S.SensorCorruption(n,'cpu',20261103,profile);d=D.FeedbackDelay(n,'cpu',20261103,enabled);ids=t.arange(n);s.reset(ids);d.reset(ids);return s,d
 sa,da=pair();sb,db=pair();checks=[];calls=0;records=[];age_counts={0:0,10000:0};fresh_reset=False;duplicate_no_draw=True
 def equal(x,y):
  if t.is_tensor(x):return t.equal(x,y)
  if type(x)is dict:return x.keys()==y.keys()and all(equal(x[k],y[k])for k in x)
  if type(x)in(list,tuple):return type(x)is type(y)and len(x)==len(y)and all(equal(u,v)for u,v in zip(x,y))
  return x==y
 def feed(tick,epoch_shift=0.):
  nonlocal calls,duplicate_no_draw
  for key,width in D.WIDTHS.items():
   clean=t.arange(n*width,dtype=t.float32).reshape(n,width)*.001+tick*.01+epoch_shift;last_before=da.cache[key]['last'].clone()if key in da.cache else t.full((n,),-1,dtype=t.long);cur_before=da.cache[key]['cur'].clone()if key in da.cache else clean.clone();out_before=da.cache[key]['out'].clone()if key in da.cache else clean.clone();noise_before=sa.draw_counts[key]
   noisy=sa.apply(key,clean,tick);drawn=sa.cache[key][1].clone();assert t.equal(noisy,clean+drawn+(sa.bias if key=='leg_pos'else 0.));out=da.apply(key,noisy,tick);fresh_out=t.where(((da.delay==1)&(last_before>=0))[:,None],cur_before,noisy);expected=t.where((last_before!=tick)[:,None],fresh_out,out_before);assert t.equal(out,expected)
   noisy_b=sb.apply(key,clean,tick);out_b=db.apply(key,noisy_b,tick);assert t.equal(out,out_b);assert equal(sa.state_dict(),sb.state_dict())and equal(da.state_dict(),db.state_dict());calls+=1
   r=da.receipt(key,tick);ages=r['actual_age_us'];assert bool(((ages==0)|(ages==10000)).all());age_counts[0]+=int((ages==0).sum());age_counts[10000]+=int((ages==10000).sum())
   before_draw=sa.draw_counts[key];before_rng=sa.noise_rng[key].get_state().clone();again=sa.apply(key,clean+1.,tick);again_out=da.apply(key,again,tick);assert t.equal(again_out,out)and sa.draw_counts[key]==before_draw and t.equal(sa.noise_rng[key].get_state(),before_rng)
   # Baseline side gets the same existing original calls, with no instrumentation.
   again_b=sb.apply(key,clean+1.,tick);again_out_b=db.apply(key,again_b,tick);assert t.equal(again_out_b,out_b)
   records.append(dict(channel=key,feedback_tick=tick,synthetic_physics_tick=tick*4,control=(tick-1)//2,slot='MID'if tick%2 else'END',raw_unit=S.SensorCorruption.receipt(sa)['raw_units'][key],fresh_draw_envs=sa.draw_counts[key]-noise_before))
 for control in range(16):
  for tick in (2*control+1,2*control+2):feed(tick)
  if control==7:
   ids=t.tensor([1,3]);old_episode=sa.episode.clone();old_draw=sa.draw_counts.copy();sa.reset(ids);da.reset(ids);sb.reset(ids);db.reset(ids);assert t.equal(sa.episode,old_episode+t.tensor([0,1,0,1,0,0,0,0]));feed(2*control+2,epoch_shift=3.)
   for key in D.WIDTHS:
    assert sa.draw_counts[key]-old_draw[key]==2;assert bool((da.cache[key]['sample_tick'][ids]==2*control+2).all())and not bool(da.cache[key]['ready'][ids].any())
   fresh_reset=True
 checks+=['actual five-channel clean plus stored noise/bias formula','actual lag0/1 previous-sample selection and warmup','MID/END synthetic source-clock schedule, not native proof','same-tick changed raw leaves delay cached output unchanged','same-tick partial reset gets fresh two-env noise and new-episode warmup','private generators/drawcounts/full queue states identical across original paths']
 so,do=pair('off',False);x=t.zeros(n,3);assert so.apply('base_ang_vel',x,1)is x and do.apply('base_ang_vel',x,1)is x;checks.append('disabled sensor/delay original return identity')
 before={k:sa.draw_counts[k]for k in D.WIDTHS}
 try:sa.apply('UNKNOWN',t.zeros(n,1),33)
 except AssertionError:pass
 else:raise AssertionError('Original unknown-channel validation lost')
 assert before==sa.draw_counts;checks.append('original invalid-input exception and no new draws')
 assert equal(sa.state_dict(),sb.state_dict())and equal(da.state_dict(),db.state_dict());assert t.equal(rng,t.random.get_rng_state())and prng==random.getstate()and not t.cuda.is_initialized();checks+=['global Torch/Python RNG unchanged','all original source and complete synthetic state unchanged by observation']
 value=dict(kind='PHASE1_ACTUAL_SOURCE_TORCH_CPU_REFERENCE_V1',status='PASS',source_pins=sources,N=n,controls=16,feedback_regular_ticks=32,physical_ticks_per_feedback=4,feedback_samples_per_control=2,per_channel_actual_draw_counts=sa.draw_counts,observed_age_us_counts=age_counts,checks=checks,check_count=len(checks),original_call_groups=calls,same_tick_partial_reset_covered=fresh_reset,clean_feedback_dim=16,full_clean35_mid_end=None,clean_mid35_exact=False,actor35_native_bitwise_tested=False,passive_tap_installed_or_tested=False,SDK_or_env_or_selected_PT_or_raw_or_GPU_or_canonical_operations=0,native_BPTT_updates=0,global_RNG_unchanged=True,interpretation='SYNTHETIC_INPUT_REAL_ORIGINAL_CLASSES_NOT_NATIVE_INTERFACE_PASS')
 with a.output.open('x',encoding='utf-8')as f:json.dump(value,f,indent=2,allow_nan=False)
 print(json.dumps(value,indent=2))
if __name__=='__main__':main()
