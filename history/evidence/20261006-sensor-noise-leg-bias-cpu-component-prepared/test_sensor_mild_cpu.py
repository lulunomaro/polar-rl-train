"""Real CPU lifecycle contract; no simulator or policy performance claim."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'isaac/mod4'))
import torch
from sensor_mild_math import SensorCorruption,CHANNELS,EPISODE_LEG_BIAS_RAD

def run():
    torch.manual_seed(42);before=torch.random.get_rng_state().clone()
    s=SensorCorruption(8,'cpu',20261006,'noise_bias_mild_v1');off=SensorCorruption(8,'cpu',20261006,'off')
    ids=torch.arange(8);s.reset(ids);off.reset(ids);bias=s.bias.clone();assert torch.isfinite(bias).all() and bias.abs().max()<=EPISODE_LEG_BIAS_RAD
    for key,(width,bound,_) in CHANNELS.items():
        clean=torch.arange(8*width,dtype=torch.float32).reshape(8,width)/7
        original=clean.clone();a=s.apply(key,clean,1);b=s.apply(key,clean,1)
        assert torch.equal(a,b) and torch.equal(clean,original) and torch.equal(off.apply(key,clean,1),clean)
        residual=a-clean-(bias if key=='leg_pos' else 0.)
        assert residual.abs().max()<=bound+1e-6 and s.draw_counts[key]==8
        second=s.apply(key,clean,2);assert not torch.equal(a,second) and s.draw_counts[key]==16
        assert torch.equal(s.bias,bias)
    untouched=s.bias[1:].clone();old=s.apply('leg_pos',torch.zeros(8,4),2).clone();s.reset([0])
    assert torch.equal(s.bias[1:],untouched) and not torch.equal(s.bias[0],bias[0])
    new=s.apply('leg_pos',torch.zeros(8,4),2);assert torch.equal(new[1:],old[1:]) and s.draw_counts['leg_pos']==17
    assert torch.equal(torch.random.get_rng_state(),before),'Corruption consumed global physics RNG'
    try:s.apply('base_ang_vel',torch.full((8,3),float('nan')),3)
    except AssertionError:pass
    else:raise AssertionError('Nonfinite real input accepted')
    out=dict(pass_=True,contracts=10,shape_units_and_bounds=True,repeat_same_tick_cached=True,
        episode_bias_persistent_and_partial_reset=True,unreset_same_tick_rows_unchanged=True,
        clean_input_unchanged=True,off_exact=True,global_RNG_untouched=True,real_nonfinite_input_rejected=True,
        scope='CPU component only; no actual SDK/physics/training/performance proof',receipt=s.receipt())
    return out

if __name__=='__main__':print(json.dumps(run()))
