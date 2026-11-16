from pathlib import Path
import sys,json,torch,numpy as np
from types import SimpleNamespace
from tensordict import TensorDict
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.teacher_retention import TeacherRetention
torch.set_num_threads(1);torch.manual_seed(0)
class Actor(torch.nn.Module):
 def __init__(self):
  super().__init__();self.mlp=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6));ck=torch.load(T/'parent_010m.pt',map_location='cpu',weights_only=False);self.mlp.load_state_dict({k.removeprefix('mlp.'):v for k,v in ck['actor_state_dict'].items()if k.startswith('mlp.')},strict=True)
 def forward(self,td,stochastic_output=False):return self.mlp(td['policy'])
plan=json.loads((T/'PLAN.json').read_text());algo=SimpleNamespace(actor=Actor());retention=TeacherRetention(algo,plan);obs=torch.from_numpy(np.load(T/'normal_bank.npz')['obs'][:192]);before={k:v.clone()for k,v in algo.actor.state_dict().items()}
loss=retention.compute(algo,TensorDict({'policy':obs,'teacher_keep':torch.ones(len(obs),1)},batch_size=[len(obs)]));loss.backward();assert torch.isfinite(loss)and all(torch.isfinite(p.grad).all()for p in algo.actor.parameters())and all(p.grad is None for p in retention.keep_teacher.parameters())and all(torch.equal(v,before[k])for k,v in algo.actor.state_dict().items())
result=dict(passed=True,optimizer_created=False,optimizer_updates=0,actual_tensordict_auxiliary_forward_backward=True,auxiliary_loss=float(loss.detach()),teacher_max_parameter_change=retention.summary()['keep_teacher_max_parameter_change'],separate_student_keep_sha=True,first_skill_coefficient=retention.skill_bc.coefficients[0]);print(json.dumps(result))
