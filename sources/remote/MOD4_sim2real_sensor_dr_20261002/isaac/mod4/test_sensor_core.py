import torch
from sensor_core import SensorCore, NOISE, BIAS

n=128; ids=torch.arange(n); nominal=(ids%5)==0
c=SensorCore(n,'cpu',20261002); c.reset(ids,nominal)
value=torch.ones(n,4)
saved=value.clone(); a=c.sample('_mod4_leg_bias',value,0).clone()
assert torch.equal(value,saved) and torch.equal(a[nominal],value[nominal])
assert torch.equal(a,c.sample('_mod4_leg_bias',value*10,0)), 'Repeated compute advanced packet'
b=c.sample('_mod4_leg_bias',value*2,1).clone()
assert torch.equal(b[c.lag==1],a[c.lag==1]), 'Lag did not use previous packet'
subset=ids[::3]; c.reset(subset,nominal[subset]); z=c.sample('_mod4_leg_bias',value*7,1).clone()
assert bool((z[subset]>6).all()), 'Reset leaked old episode or zero packet'
remaining=torch.ones(n,dtype=torch.bool);remaining[subset]=False
assert torch.equal(z[remaining],b[remaining]), 'Partial reset advanced other environments'
gravity=torch.zeros(n,3);gravity[:,2]=-1
g=c.sample('projected_gravity',gravity,1)
assert torch.equal(g[nominal],gravity[nominal]) and torch.allclose(g.norm(dim=1),torch.ones(n),atol=1e-6)
for key in ('base_ang_vel','leg_vel','wheel_vel'):
 x=torch.zeros(n,3 if key=='base_ang_vel' else 4 if key=='leg_vel' else 2)
 out=c.sample(key,x,1);assert torch.equal(out[nominal],x[nominal])
 assert float(out.abs().max())<=NOISE[key]+BIAS.get(key,0)+1e-7
# Isolated RNG does not alter global torch reset/pose sampling sequence.
torch.manual_seed(5);reference=torch.rand(8);torch.manual_seed(5)
d=SensorCore(n,'cpu',99);d.reset(ids,nominal);d.sample('leg_vel',torch.zeros(n,4),0)
assert torch.equal(torch.rand(8),reference)
assert c.audit()['nominal_bias_zero'] and c.audit()['nominal_lag_zero']
print('PASS: clean nominal, bounded noise/bias, causal shared lag, same-tick cache, partial reset, no stale history, normalized gravity, isolated RNG, no input mutation')
