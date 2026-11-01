import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json,time,torch
from copy import deepcopy
from bounded_actor292 import bounded_actor_step
torch.manual_seed(292);torch.set_num_threads(4)
N=Path(__file__).resolve().parent
actor=torch.nn.Sequential(torch.nn.Linear(44,32),torch.nn.ELU(),torch.nn.Linear(32,6))
opt=torch.optim.Adam(actor.parameters(),lr=1.)
x=torch.randn(64,44);ground=x[:16]
with torch.no_grad():before=actor(x).clone();target=actor(ground).clone()
loss=-actor(x).sum();loss.backward()
result=bounded_actor_step(actor,opt,actor,x,ground,target)
assert result['applied'] and result['parameter_interpolation_alpha']<1
assert float((actor(x)-before).abs().max())<=.05
assert float((actor(ground)-target).abs().max())<=.5
weights={k:v.detach().clone() for k,v in actor.state_dict().items()}
state=deepcopy(opt.state_dict());no_step=bounded_actor_step(actor,opt,actor,x,ground,target,apply_step=False)
assert not no_step['applied'] and all(torch.equal(v,weights[k]) for k,v in actor.state_dict().items())
loss=actor(x).square().sum();opt.zero_grad();loss.backward()
reject=bounded_actor_step(actor,opt,actor,x,ground,target,radius=0.)
assert not reject['applied'] and all(torch.equal(v,weights[k]) for k,v in actor.state_dict().items())
for k,v in state['state'].items():
    assert all(torch.equal(t,opt.state_dict()['state'][k][n]) for n,t in v.items())
row=dict(passed=True,epoch=time.time(),real_model_reads=0,CUDA=torch.cuda.is_initialized(),synthetic_CPU_source_only=True,projected_large_step=result,no_step=no_step,rejected_proposal_optimizer_and_weights_restored=reject)
with (N/'reports/CPU292_BOUNDED_UPDATE_SOURCE_TEST.json').open('x',encoding='utf8') as f:json.dump(row,f,indent=2)
print(json.dumps(row))
