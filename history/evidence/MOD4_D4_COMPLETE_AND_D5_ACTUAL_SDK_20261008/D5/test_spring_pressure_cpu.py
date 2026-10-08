"""CPU state/lifecycle tests; actual SDK and CUDA remain separate contracts."""
from pathlib import Path
import json,time,hashlib,tempfile
import torch
from spring_pressure_component import SpringPressure
torch.set_num_threads(1)
assert not torch.cuda.is_initialized()
before=torch.get_rng_state().clone()
p=SpringPressure(32,'cpu',20261002);p.reset(torch.arange(32))
assert p.factor.shape==(32,2) and bool(((p.factor>=.9)&(p.factor<=1.1)).all())
assert not torch.equal(p.factor[:,0],p.factor[:,1])
assert torch.equal(before,torch.get_rng_state())
held=p.factor.clone();st=p.state_dict();ids=torch.tensor([1,4,7]);other=torch.tensor([i for i in range(32) if i not in ids.tolist()])
assert torch.equal(p.factor,held) # no step-time resampling method
p.reset(ids);assert torch.equal(p.factor[other],st['factor'][other]) and torch.equal(p.episode[other],st['episode'][other])
assert torch.equal(p.episode[ids],st['episode'][ids]+1)
with tempfile.TemporaryDirectory() as t:
    path=Path(t)/'CPU_pressure.pt';torch.save(p.state_dict(),path)
    new=SpringPressure(32,'cpu',9);new.load_state_dict(torch.load(path,map_location='cpu',weights_only=False))
    assert torch.equal(new.factor,p.factor) and torch.equal(new.episode,p.episode)
    p.reset(ids);new.reset(ids);assert torch.equal(p.factor,new.factor)
off=SpringPressure(32,'cpu',2,False);streams=[g.get_state().clone() for g in off.rng];off.reset(ids)
assert torch.equal(off.factor,torch.ones_like(off.factor)) and all(torch.equal(a,g.get_state()) for a,g in zip(streams,off.rng))
assert torch.equal(off.actual_stiffness([3500,3500]),torch.full((32,2),3500.))
errors=[]
for action in (lambda:off.actual_stiffness([float('nan'),3500]),lambda:p.reset([1,1]),lambda:p.reset([32])):
    try:action()
    except ValueError:errors.append(True)
    else:raise AssertionError('invalid input accepted')
assert len(errors)==3 and torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
D=Path(__file__).resolve().parent
v=dict(epoch=time.time(),torch_version=torch.__version__,passed=True,CPU_only=True,CUDA_initialized=False,
    contracts=['bounds_shape_units','independent_two_spring_streams','globalRNG_untouched','episode_hold',
       'selected_reset_only','selected_episode_increment','CPU_disk_rng_roundtrip_and_next_draw',
       'off_exact_nominal_no_private_draw','nonfinite_invalid_input_rejected','CPU_notCUDA_resume_proof'],
    source_sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('spring_pressure_component.py','test_spring_pressure_cpu.py')},
    actual_SDK_or_DR_learning_deployed=False,nominal_preload_damping_model_changed=False,
    hardware_calibration_available=False)
(D/'reports/SPRING_PRESSURE_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps(v))
