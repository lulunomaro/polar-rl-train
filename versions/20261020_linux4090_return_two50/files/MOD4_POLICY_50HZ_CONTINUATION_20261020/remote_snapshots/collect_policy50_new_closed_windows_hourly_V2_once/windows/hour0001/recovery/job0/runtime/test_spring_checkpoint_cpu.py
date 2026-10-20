"""D5 CPU schema/mutation guard; actual CUDA restore is a separate SDK/startup proof."""
import torch,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'isaac/mod4'))
from spring_pressure_component import SpringPressure
from spring_pressure_checkpoint import exact,validate_saved_pressure
q=SpringPressure(16,'cpu',928);q.reset(torch.arange(16));state=q.state_dict()
cpu=torch.random.get_rng_state().clone();other=state['factor'][[0,2,3]].clone()
q.reset(torch.tensor([1,4,7]));assert torch.equal(q.factor[[0,2,3]],other)
assert torch.equal(cpu,torch.random.get_rng_state())
q.load_state_dict(state);assert exact(q.state_dict(),state)
disk=D/'reports/CPU_PRESSURE_FIXTURE.pt';torch.save(state,disk)
q.load_state_dict(torch.load(disk,weights_only=False));assert exact(q.state_dict(),state)
schema=dict(state,rng_device_type='cuda');assert validate_saved_pressure(schema,16)
for bad in (dict(schema,n=20),dict(schema,factor=torch.full((16,2),float('nan'))),dict(schema,rng=[]),dict(schema,episode=torch.full((16,),-1,dtype=torch.long))):
    try:validate_saved_pressure(bad,16)
    except AssertionError:pass
    else:raise AssertionError('invalid pressure state accepted')
try:q.load_state_dict(schema)
except ValueError:pass
else:raise AssertionError('CUDA RNG codec must not be loaded by CPU generator')
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,contracts=9,CUDA_initialized=False,CPU_schema_not_actual_CUDA_resume=True)))
