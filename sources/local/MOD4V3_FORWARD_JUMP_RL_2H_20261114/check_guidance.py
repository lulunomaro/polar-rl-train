"""Check finite gradients and immutable weights without any optimizer step."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import argparse
import torch
from torch import nn

T=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--dataset',default=str(T/'weights/teacher_demos_r1__successful_demos.pt'))
parser.add_argument('--report',default='R3_GUIDANCE_NO_UPDATE_CHECK.json')
args=parser.parse_args()
sys.path.insert(0,str(T/'support_r3'))
from mod4v3_ppo_v1.jump_bc import JumpGuidance
dataset=Path(args.dataset)
data=torch.load(dataset,map_location='cpu',weights_only=False)
spec=dict(initial=.5,final=.15,decay_seconds=5400.,demo_coefficient=2.,demo_minibatch=1025,
    dataset=str(dataset),dataset_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest())
class Actor(nn.Module):
    def __init__(self):
        super().__init__()
        self.mlp=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),
                               nn.Linear(128,64),nn.ELU(),nn.Linear(64,6))
    def forward(self,observations,stochastic_output=False):
        return self.mlp(observations['policy'])
actor=Actor()
weights=T/'weights/train_cont_r2__model_final.pt'
if not weights.exists():weights=sorted((T/'weights').glob('train_cont_r2__model_*m.pt'))[-1]
state=torch.load(weights,map_location='cpu',weights_only=False)
actor.mlp.load_state_dict({k.removeprefix('mlp.'):v for k,v in state['actor_state_dict'].items() if k.startswith('mlp.')})
before={k:v.clone() for k,v in actor.state_dict().items()}
guidance=JumpGuidance(spec,'cpu')
loss=guidance.compute(SimpleNamespace(actor=actor),dict(policy=data['policy'][:256],jump_target=data['actions'][:256]))
gradients=torch.autograd.grad(loss,tuple(actor.parameters()))
assert all(bool(torch.isfinite(g).all()) for g in gradients)
norm=float(torch.sqrt(sum(g.square().sum() for g in gradients)))
assert norm>0.
assert all(torch.equal(v,actor.state_dict()[k]) for k,v in before.items())
report=dict(loss=float(loss.detach()),gradient_norm=norm,weights_unchanged=True,optimizer_created=False,
    optimizer_updates=0,dataset_sha256=spec['dataset_sha256'],metadata=data['metadata'],
    phase_balanced_minibatch=1025,stats=guidance.finish(),
    source_sha256=hashlib.sha256((T/'support_r3/mod4v3_ppo_v1/jump_bc.py').read_bytes()).hexdigest())
(T/'evidence'/args.report).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
