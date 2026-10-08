"""Actual target Torch CPU semantic/RNG/state contracts; no SDK or CUDA."""
from pathlib import Path
import torch,json,hashlib,tempfile,time,copy
from gas_damping_factor import GasDamping
from spring_pressure_component import SpringPressure
D=Path(__file__).resolve().parent
assert not torch.cuda.is_initialized();checks=[]
def passed(name,condition):assert condition,name;checks.append(name)
a=GasDamping(12,'cpu',987);global_before=torch.random.get_rng_state().clone();a.reset(torch.arange(12))
passed('shape_and_SI_bounds',a.factor.shape==(12,2) and bool(((a.actual_damping_Ns_per_m()>=2.7)&(a.actual_damping_Ns_per_m()<=3.3)).all()))
passed('global_RNG_untouched',torch.equal(global_before,torch.random.get_rng_state()))
before=a.state_dict();ids=torch.tensor([1,4,7]);a.reset(ids);others=torch.ones(12,dtype=torch.bool);others[ids]=False
passed('selected_episode_reset',torch.equal(a.episode[ids],before['episode'][ids]+1))
passed('unselected_factor_episode_exact',torch.equal(a.factor[others],before['factor'][others]) and torch.equal(a.episode[others],before['episode'][others]))
s=a.state_dict()
with tempfile.TemporaryDirectory() as temp:
 path=Path(temp)/'state.pt';torch.save(s,path);loaded=torch.load(path,weights_only=False,map_location='cpu');b=GasDamping(12,'cpu',1);b.load_state_dict(loaded)
passed('CPU_disk_state_roundtrip',torch.equal(b.factor,a.factor) and torch.equal(b.episode,a.episode) and all(torch.equal(x.get_state(),y.get_state()) for x,y in zip(b.rng,a.rng)))
a.reset(ids);b.reset(ids);passed('next_selected_draw_exact',torch.equal(a.factor,b.factor))
pressure=SpringPressure(12,'cpu',987);pressure.reset(torch.arange(12));fresh=GasDamping(12,'cpu',987);fresh.reset(torch.arange(12))
passed('D5_D6_RNG_namespace_separate',not torch.equal(pressure.factor,fresh.factor))
try:b.load_state_dict(pressure.state_dict());raise AssertionError('Accepted wrong physical parameter')
except ValueError:checks.append('wrong_parameter_state_rejected')
off=GasDamping(12,'cpu',3,False);offstreams=[g.get_state().clone() for g in off.rng];off.reset(ids);passed('off_exact_nominal_and_no_draw',torch.equal(off.actual_damping_Ns_per_m(),torch.full((12,2),3.)) and all(torch.equal(g.get_state(),s) for g,s in zip(off.rng,offstreams)))
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,checks=checks,count=len(checks),Torch=torch.__version__,CPU_only=True,CUDA_initialized=False,
 source_sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('gas_damping_factor.py','test_gas_damping_cpu.py','spring_pressure_component.py')},
 actual_CUDA_or_SDK_or_learning_contract_completed=False,not_full_D6_joint_friction_coverage=True)
(D/'reports/GAS_DAMPING_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
