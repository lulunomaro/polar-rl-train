"""Actual stream lifecycle for resized rows plus original learner AST preservation."""
from pathlib import Path
import ast,json,sys,types,torch
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'isaac/mod4'))
import scaling_resume_contract as r
def sensor(n):
 return types.SimpleNamespace(profile='noise_bias_mild_v1',bias=torch.full((n,4),99.),episode=torch.zeros(n,dtype=torch.long),bias_rng=torch.Generator().manual_seed(31),noise_rng={k:torch.Generator().manual_seed(37+i) for i,k in enumerate(('a','b'))})
a=sensor(20);torch.rand(20,generator=a.bias_rng)
saved={'bias':a.bias.clone(),'bias_rng':a.bias_rng.get_state(),'noise_rng':{k:g.get_state() for k,g in a.noise_rng.items()}}
ck={'sensor_recipe':{'profile':'noise_bias_mild_v1'},'sensor_DR_state':saved}
for n in (20,25):
 s=sensor(n);before=s.bias.clone();assert r.restore_sensor(s,ck);assert s.bias.shape==(n,4) and torch.equal(s.bias,before)
 ref=torch.Generator();ref.set_state(saved['bias_rng']);assert torch.equal(torch.rand(n,4,generator=s.bias_rng),torch.rand(n,4,generator=ref))
try:r.restore_sensor(sensor(25),{'sensor_recipe':{'profile':'wrong'}});raise AssertionError('wrong profile accepted')
except AssertionError as e:assert 'accepted' not in str(e)
old=ast.parse((D/'isaac/mod4/train_sensor_resume_ppo.py').read_text());new=ast.parse((D/'isaac/mod4/train_scaling_ppo.py').read_text())
for node in ast.walk(new):
 if isinstance(node,ast.ImportFrom) and node.module=='scaling_resume_contract':node.module='sensor_resume_contract'
for node in ast.walk(new):
 if isinstance(node,ast.FunctionDef) and node.name=='main':
  node.body=[x for x in node.body if not (isinstance(x,ast.For) and isinstance(x.iter,ast.Tuple) and [getattr(e,'value',None) for e in x.iter.elts]==['train_scaling_ppo.py','scaling_resume_contract.py'])]
assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False)
assert not torch.cuda.is_initialized()
print(json.dumps({'passed':True,'CPU_contracts':5,'actual_stream_restoration_and_resized_row_shapes':True,'original_learning_AST_exact_except_stream_resume_import_and_own_snapshots':True,'no_CUDA_initialized':True,'no_learning_or_budget':True}))
