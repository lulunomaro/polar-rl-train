"""Check paired RNG and exact unchanged full-profile behavior before GPU probes."""
import importlib.util
from pathlib import Path
import torch
from sensor_core import SensorCore

spec = importlib.util.spec_from_file_location('original_sensor_core', Path(__file__).with_name('sensor_core_before_ablation.py'))
old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
n=80; ids=torch.arange(n); nominal=ids%5==0
cores=[old.SensorCore(n,'cpu',20261002), SensorCore(n,'cpu',20261002),
       SensorCore(n,'cpu',20261002,'sensor_noise_v1'), SensorCore(n,'cpu',20261002,'sensor_delay_v1')]
for c in cores: c.reset(ids,nominal)
previous={}
for step in range(6):
    if step==3:
        for c in cores: c.reset(ids[::3],nominal[::3])
    for key,width in [('base_ang_vel',3),('projected_gravity',3),('_mod4_leg_bias',4),('leg_vel',4),('wheel_vel',2)]:
        value=torch.full((n,width),float(step+1))
        if key=='projected_gravity': value/=value.norm(dim=1,keepdim=True)
        out=[c.sample(key,value,step).clone() for c in cores]
        assert torch.equal(out[0],out[1]), 'Full profile changed'
        assert torch.equal(cores[1].generator.get_state(),cores[2].generator.get_state())
        assert torch.equal(cores[1].generator.get_state(),cores[3].generator.get_state())
        fresh=torch.ones(n,dtype=torch.bool) if step==0 else torch.zeros(n,dtype=torch.bool)
        if step==3: fresh[::3]=True
        expected=value.clone()
        if step:
            delayed=(cores[3].lag==1)&~fresh
            expected[delayed]=previous[key][delayed]
        assert torch.equal(out[3],expected), 'Delay-only must use clean causal packets'
        assert torch.equal(out[2][nominal],value[nominal])
        for c,y in zip(cores,out): assert torch.equal(c.sample(key,value*9,step),y)
        previous[key]=value
assert cores[2].audit()['lag_steps_max']==0
assert all(v==0 for v in cores[3].audit()['observed_packet_error_max'].values())
assert all(v==0 for v in cores[3].audit()['persistent_bias_bound_raw_units'].values())
print('PASS: original full profile bit-exact, paired RNG, clean causal delay, noise-only zero lag, reset and same-tick cache')
