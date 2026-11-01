import torch
from types import SimpleNamespace
from e1_reset_evidence import bind_expected_reset_q
assert not torch.cuda.is_initialized()
q=torch.arange(300,dtype=torch.float32).reshape(10,30)/100
env=SimpleNamespace(num_envs=10,device='cpu',_rough_probe_expected_q=q.clone(),scene={'robot':SimpleNamespace(data=SimpleNamespace(joint_pos=q.clone()))})
bind_expected_reset_q(env,None);assert torch.equal(env._rescue_reset_q,q) and env._rescue_reset_q.data_ptr()!=env._rough_probe_expected_q.data_ptr()
ids=torch.tensor([1,4,7]);others=torch.tensor([0,2,3,5,6,8,9]);old=env._rescue_reset_q.clone();global_rng=torch.random.get_rng_state().clone()
env._rough_probe_expected_q[ids]+=1;env.scene['robot'].data.joint_pos[ids]+=1
bind_expected_reset_q(env,ids);assert torch.equal(env._rescue_reset_q[others],old[others]) and torch.equal(env._rescue_reset_q[ids],env._rough_probe_expected_q[ids]);assert torch.equal(torch.random.get_rng_state(),global_rng)
env.scene['robot'].data.joint_pos[1,0]+=.01
try:bind_expected_reset_q(env,ids);raise RuntimeError('Actual reset mismatch accepted')
except AssertionError:pass
env.scene['robot'].data.joint_pos[1,0]=float('nan')
try:bind_expected_reset_q(env,ids);raise RuntimeError('Nonfinite actual reset accepted')
except AssertionError:pass
bind_expected_reset_q(env,[])
assert not torch.cuda.is_initialized()
print('CPU6 expectedbank-copy/selectedrows/independentstorage/globalRNG/mismatch/nonfinite contracts passed; no plant setter')
