"""Bounded CPU checks of landing timing, teacher gradients and balanced sampling."""
from pathlib import Path
import importlib.util,sys,types,json,hashlib,ast
import torch
T=Path(__file__).resolve().parent;torch.set_num_threads(1)
# Local replay venv has no TensorDict; use a dictionary adapter only for this CPU unit test.
# Actual RSL/TensorDict integration is checked separately in the native frozen2048 probe.
try:from tensordict import TensorDict
except ModuleNotFoundError:
 class TensorDict(dict):
  def __init__(self,*args,batch_size=None,**kwargs):super().__init__(*args,**kwargs)
 module=types.ModuleType('tensordict');module.TensorDict=TensorDict;sys.modules['tensordict']=module

def load(name):
 p=T/'support/mod4v3_ppo_v1'/(name+'.py');spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
credit=load('stair_landing_credit').landing_credit
already=torch.zeros(3,2,dtype=torch.bool);active=torch.tensor([True,True,False])
a=credit(torch.tensor([[True,False],[False,False],[True,True]]),already,active);assert torch.allclose(a,torch.tensor([.15,0.,0.]))
b=credit(torch.tensor([[True,False],[True,True],[True,True]]),already,active);assert torch.allclose(b,torch.tensor([0.,.3,0.]))
c=credit(torch.tensor([[True,True],[True,True],[True,True]]),already,active);assert torch.allclose(c,torch.tensor([.15,0.,0.]))
assert abs(float(a[0]+b[0]+c[0])+.2-.5)<1e-7
assert torch.equal(credit(torch.ones(3,2,dtype=torch.bool),already,active),torch.zeros(3))
class Actor(torch.nn.Module):
 def __init__(self):
  super().__init__();self.mlp=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6))
 def forward(self,observations,stochastic_output=False):return self.mlp(observations['policy'])
plan=json.loads((T/'PLAN.json').read_text());spec=plan['teacher_retention'];spec['keep_teacher']=str(T/'comprehensive_keep_teacher.pt');spec['dataset']=str(T/'teacher_movement_balanced_demos.pt');spec['high_stance_dataset']=str(T/'high_stance_comprehensive_anchors.pt')
actor=Actor();student=torch.load(plan['current_repair']['starting_checkpoint']['source'],map_location='cpu',weights_only=False);actor.load_state_dict({k:v for k,v in student['actor_state_dict'].items() if k in actor.state_dict()},strict=True)
algorithm=types.SimpleNamespace(device='cpu',actor=actor)
retention=load('teacher_retention').TeacherRetention(algorithm,plan)
x=retention.high_obs[:64].clone();obs=TensorDict(dict(policy=x,teacher_keep=torch.ones(64,1),teacher_high_stance=torch.ones(64,1)),batch_size=[64]);loss=retention.compute(algorithm,obs);loss.backward();stats=retention.finish_update();summary=retention.summary()
assert sum(float(p.grad.square().sum()) for p in actor.parameters() if p.grad is not None)>0
assert summary['keep_teacher_max_parameter_change']==0.0 and summary['keep_teacher_no_grad']
assert retention.last_sample_counts['specialist_preparation_samples']==0 and stats['teacher_high_anchor_samples']==256
phases=[sum(value for key,value in retention.seed_sampled.items() if ast.literal_eval(key)[0]==p) for p in (0,1)];assert phases==[512,512]
angle_counts=[sum(v for k,v in retention.seed_sampled.items() if ast.literal_eval(k)[1]==a) for a in range(5)];available=[a for a in range(5) if any(k[1]==a for k in retention.seed_groups)];assert all(angle_counts[a]==0 for a in range(5) if a not in available);assert max(angle_counts[a] for a in available)-min(angle_counts[a] for a in available)<=2
pool=load('success_replay').SuccessfulStairReplay(types.SimpleNamespace(device='cpu',continuous_stair_mask=torch.ones(2,dtype=torch.bool)),plan['online_success_replay'])
for g in range(20):pool.counts[g]=2;pool.bank_obs[g,:2]=g;pool.bank_actions[g,:2]=g
xx,yy=pool.sample(400);assert xx.shape==(400,35) and yy.shape==(400,6) and pool.sampled==[20]*20
assert pool.state_dict()['version']==2
for file in T.rglob('*.py'):ast.parse(file.read_text(encoding='utf8'))
result=dict(passed=True,scope='CPU unit checks only; actual native runtime/protection results separately required',landing_credit_once_per_wheel=True,total_stage_landing_return=.5,inactive_no_reward=True,actual_actor_gradients=True,frozen_teacher_change=0.,phase_counts=phases,angle_counts=angle_counts,online20strata_samples=pool.sampled,teacher_losses=stats,high_stance_anchor_frames=len(retention.high_obs),specialist_moving_frames=len(retention.demo_obs),no_PPO_optimizer_or_weights_saved=True)
(T/'evidence/CPU_REPAIR_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result),flush=True)
