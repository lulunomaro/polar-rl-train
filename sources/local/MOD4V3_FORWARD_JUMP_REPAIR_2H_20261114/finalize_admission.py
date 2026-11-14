"""Freeze native demonstration SHA and test gradients without taking a step."""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import torch
from torch import nn

T=Path(__file__).resolve().parent
sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.jump_bc import JumpGuidance
sys.path.insert(0,sys.argv[1])
from ssh72 import connect
plan=json.loads((T/'PLAN.json').read_bytes())
demo_name=Path(plan['jump_bc']['dataset']).parent.name
result=json.loads((T/'evidence'/demo_name/'RESULT.json').read_bytes())
nominal=[r for r in result['episodes'] if r['nominal']]
assert len(nominal)==51 and all(r['retracted'] for r in nominal)
assert any(r['success'] and not r['terminated'] for r in nominal)
assert json.loads((T/'evidence/admit_repair/ADMISSION.json').read_bytes())['passed']
dataset=T/'weights'/(demo_name+'__successful_demos.pt')
digest=hashlib.sha256(dataset.read_bytes()).hexdigest()
assert digest==result['dataset_sha256']
plan['jump_bc']['dataset_sha256']=digest
data=torch.load(dataset,map_location='cpu',weights_only=False)
spec=dict(plan['jump_bc'],dataset=str(dataset))
class Actor(nn.Module):
    def __init__(self):
        super().__init__()
        self.mlp=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6))
    def forward(self,observations,stochastic_output=False):return self.mlp(observations['policy'])
actor=Actor()
state=torch.load(T/'weights/parent_r3_080m.pt',map_location='cpu',weights_only=False)
actor.mlp.load_state_dict({k.removeprefix('mlp.'):v for k,v in state['actor_state_dict'].items() if k.startswith('mlp.')})
before={k:v.clone() for k,v in actor.state_dict().items()}
torch.manual_seed(66)
ids=torch.cat([(data['phase']==i).nonzero().flatten()[:64] for i in range(5)])
guidance=JumpGuidance(spec,'cpu')
loss=guidance.compute(SimpleNamespace(actor=actor),dict(policy=data['policy'][ids],jump_target=data['actions'][ids]))
grads=torch.autograd.grad(loss,tuple(actor.parameters()))
assert all(bool(torch.isfinite(g).all()) for g in grads)
norm=float(torch.sqrt(sum(g.square().sum() for g in grads)))
assert norm>0 and all(torch.equal(v,actor.state_dict()[k]) for k,v in before.items())
report=dict(loss=float(loss.detach()),gradient_norm=norm,optimizer_created=False,optimizer_updates=0,
    weights_unchanged=True,dataset_sha256=digest,metadata=data['metadata'],stats=guidance.finish(),
    nominal_teacher_complete=f'{sum(r["success"] and not r["terminated"] for r in nominal)}/{len(nominal)}',native_checks='admit_repair/STARTUP.json and RESULT.json')
(T/'evidence/GUIDANCE_NO_UPDATE.json').write_text(json.dumps(report,indent=2)+'\n')
(T/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
client=connect()
try:
    s=client.open_sftp();s.put(str(T/'PLAN.json'),plan['root']+'/PLAN.json');s.close()
finally:client.close()
print(json.dumps(report,indent=2))
