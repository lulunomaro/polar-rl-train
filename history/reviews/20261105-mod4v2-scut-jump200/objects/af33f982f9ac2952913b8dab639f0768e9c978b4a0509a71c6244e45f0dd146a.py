from pathlib import Path
import hashlib,json,sys,time,torch
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.supermimic_newton import load_sources,FudanPPOResidualPolicy
load_sources(G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json')
from supermimic_vendor_v2.networks import Policy
from tensordict import TensorDict
class Teacher(torch.nn.Module):
 def __init__(self):super().__init__();self.net=torch.nn.Sequential(torch.nn.Linear(35,64),torch.nn.ELU(),torch.nn.Linear(64,6))
 def forward(self,obs,stochastic_output=False):return self.net(obs['policy'])
torch.manual_seed(9140);teacher=Teacher();before={k:v.clone()for k,v in teacher.state_dict().items()}
policy=FudanPPOResidualPolicy(Policy(35,30,hist=10,z_dim=16,num_joints=6,hidden=(64,32)),teacher)
history=torch.randn(16,10,35);goal=torch.randn(16,30)
expected=teacher(TensorDict(dict(policy=history[:,-1]),batch_size=[16])).clamp(-6,6)
initial=policy(history,goal);assert torch.equal(initial,expected)
loss=(initial-.25).square().mean();loss.backward()
assert all(p.grad is None for p in teacher.parameters())
opt=torch.optim.Adam([p for p in policy.parameters()if p.requires_grad],lr=.001);opt.step()
assert not torch.equal(policy(history,goal),initial)
assert all(torch.equal(v,teacher.state_dict()[k])for k,v in before.items())
out=dict(epoch=time.time(),passed=True,synthetic_CPU_interface_test=True,production_PT_reads=0,physics_steps=0,
    original_PPO_mean_actions_initially_equal=True,frozen_teacher_unchanged=True,new_residual_optimizer_updates=True,
    source_PPO_optimizer_not_misrepresented_as_BPTT_optimizer=True)
with(N/'supermimic_compatibility01/WARMSTART_CPU.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
