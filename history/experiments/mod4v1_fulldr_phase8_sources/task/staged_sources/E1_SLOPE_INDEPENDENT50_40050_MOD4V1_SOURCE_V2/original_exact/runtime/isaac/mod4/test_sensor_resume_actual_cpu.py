"""CPU tests against the exact formal checkpoint; no CUDA, simulator or optimizer."""
import sys,json,torch,copy,io
from sensor_mild_math import SensorCorruption,CHANNELS
from sensor_resume_contract import restore_sensor,restore_named
torch.set_num_threads(1);ck=torch.load(sys.argv[1],map_location='cpu',weights_only=False)
assert ck['sensor_DR_state']['n']==20000
passed=[];s=SensorCorruption(20000,'cpu',7,'noise_bias_mild_v1');t=SensorCorruption(20000,'cpu',9,'noise_bias_mild_v1')
assert set(ck['sensor_DR_state']['noise_rng'])==set(CHANNELS) and len(ck['sensor_DR_state']['cache'])==5
assert all(v.dtype==torch.uint8 and v.ndim==1 for v in ck['sensor_DR_state']['noise_rng'].values())
buf=io.BytesIO();torch.save(ck['sensor_DR_state'],buf);buf.seek(0);loaded=torch.load(buf,weights_only=False)
assert torch.equal(loaded['bias_rng'],ck['sensor_DR_state']['bias_rng']) and torch.equal(loaded['bias'],ck['sensor_DR_state']['bias']);passed.append('actual20000_GPU_rng_bytes_and_bias_serialization_exact')
# CPU and CUDA generators have different representations. Do not call CPU restore on GPU RNG bytes.
fixture=copy.deepcopy(ck);fixture['sensor_DR_state']['bias_rng']=s.bias_rng.get_state()
fixture['sensor_DR_state']['noise_rng']={k:g.get_state() for k,g in s.noise_rng.items()}
restore_sensor(s,fixture);restore_sensor(t,fixture);passed.append('CPU_rng_fixture_actual_bias_cache_episode_roundtrip')
x={k:torch.zeros(20000,d) for k,(d,_,_) in CHANNELS.items()}
tick=max(int(a.max()) for a,b in s.cache.values())+1
for k,v in x.items():assert torch.equal(s.apply(k,v,tick),t.apply(k,v,tick))
passed.append('next_draws_exact_after_full_checkpoint_roundtrip')
global0=torch.random.get_rng_state().clone();old=s.episode.clone();oldbias=s.bias.clone()
s.reset(torch.arange(20000));t.reset(torch.arange(20000));assert torch.equal(s.episode,old+1) and torch.equal(s.bias,t.bias) and not torch.equal(s.bias,oldbias)
assert torch.equal(global0,torch.random.get_rng_state());assert all(bool((a==-1).all()) for a,b in s.cache.values());passed.append('new_episode_all_rows_bias_resampled_cache_invalidated_once')
for k,v in x.items():assert torch.equal(s.apply(k,v,0),t.apply(k,v,0))
passed.append('new_zero_tick_no_old_physx_noise_cache')
class Obj:pass
for key in ('sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):
 o=Obj()
 for k,v in ck[key].items():setattr(o,k,torch.Generator().manual_seed(1))
 saved={k:torch.Generator().manual_seed(20+i).get_state() for i,k in enumerate(ck[key])}
 restore_named(o,saved);passed.append(key+'_actual_names_CPU_fixture_state_roundtrip')
o=Obj();o.wrong=torch.Generator()
try:restore_named(o,{})
except AssertionError:passed.append('different_named_rng_schema_rejected')
else:raise AssertionError('Schema mismatch accepted')
bad=dict(fixture);bad['sensor_recipe']=dict(ck['sensor_recipe'],profile='off')
try:restore_sensor(t,bad)
except AssertionError:passed.append('wrong_sensor_profile_rejected')
else:raise AssertionError('Wrong profile accepted')
print(json.dumps(dict(passed=True,contracts=passed,count=len(passed),actual_source=sys.argv[1],actual_GPU_rng_restore_requires_startup_SDK=True,no_CUDA_initialized=not torch.cuda.is_initialized(),no_learning=True)))
