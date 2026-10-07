import torch
from history_runtime_checkpoint import named_generators,restore_independent_rng
class Owner:pass
env=Owner();env.common_step_counter=0;env._command_rng=torch.Generator().manual_seed(31)
env._dr={'gain':torch.Generator().manual_seed(62)}
env.command_manager=Owner();term=Owner();term.generator=torch.Generator().manual_seed(93)
env.command_manager._terms={'twist':term}
gens=named_generators(env);assert len(gens)==3
states={k:g.get_state() for k,g in gens.items()}
values={k:torch.rand(7,generator=g) for k,g in gens.items()}
for g in gens.values():torch.rand(12,generator=g)
restore_independent_rng(states,env)
assert all(torch.equal(v,torch.rand(7,generator=gens[k])) for k,v in values.items())
try:restore_independent_rng({},env);raise AssertionError('Missing RNG registry accepted')
except ValueError:pass
assert not torch.cuda.is_initialized()
print('Independent command/DR/runtime RNG roundtrip and mismatched registry refusal passed; no CUDA')
