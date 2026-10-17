"""Exercise the exact update AST on synthetic toy parameters, not production weights."""
from pathlib import Path
import os,ast,types,time,json,traceback,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
from h1_action_mean_overflow_loss_v1 import mean_overflow_loss
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
def update(path,coefficient):
 tree=ast.parse(path.read_text('utf8'));cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='PPO');f=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='update');ns=dict(torch=torch,nn=torch.nn,mean_overflow_loss=lambda x:mean_overflow_loss(x,coefficient))
 exec(compile(ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[])),str(path),'exec'),ns);return ns['update']
class Actor(torch.nn.Module):
 is_recurrent=False
 def __init__(self):
  super().__init__();self.mean=torch.nn.Parameter(torch.tensor([-100.,-4.,0.,2.,5.,9.]));self.std=torch.nn.Parameter(torch.ones(6)*24)
 def forward(self,obs,**kw):
  self.dist=torch.distributions.Normal(self.mean.expand(32,6),self.std.expand(32,6));return self.dist.sample() if kw.get('stochastic_output') else self.dist.mean
 def get_output_log_prob(self,a):return self.dist.log_prob(a).sum(-1)
 @property
 def output_distribution_params(self):return (self.dist.mean,self.dist.stddev)
 @property
 def output_entropy(self):return self.dist.entropy().sum(-1)
class Critic(torch.nn.Module):
 is_recurrent=False
 def __init__(self):super().__init__();self.bias=torch.nn.Parameter(torch.tensor(0.))
 def forward(self,obs,**kw):return self.bias.expand(32,1)
class Storage:
 def __init__(self,batch):self.batch=batch;self.cleared=False
 def mini_batch_generator(self,batches,epochs):
  for _ in range(batches*epochs):yield self.batch
 def clear(self):self.cleared=True
def fixture(fn):
 actor=Actor();critic=Critic();obs=types.SimpleNamespace(batch_size=[32]);actor(obs);actions=actor.dist.mean.detach().clone();values=torch.zeros(32,1)
 batch=types.SimpleNamespace(observations=obs,actions=actions,old_actions_log_prob=actor.get_output_log_prob(actions).detach().unsqueeze(-1),values=values,returns=values,advantages=values,masks=None,hidden_states=[None,None])
 optimizer=torch.optim.Adam([*actor.parameters(),*critic.parameters()],lr=.0001)
 test=types.SimpleNamespace(actor=actor,critic=critic,optimizer=optimizer,rnd=None,rnd_optimizer=None,symmetry=None,num_mini_batches=4,num_learning_epochs=5,storage=Storage(batch),normalize_advantage_per_mini_batch=False,desired_kl=None,schedule='fixed',clip_param=.2,use_clipped_value_loss=True,value_loss_coef=1.,entropy_coef=0.,is_multi_gpu=False,max_grad_norm=1.)
 before={k:v.clone() for k,v in actor.state_dict().items()};result=fn(test);assert test.storage.cleared
 assert all(int(x['step'])==20 for x in optimizer.state_dict()['state'].values())
 return dict(actor={k:v.detach().clone() for k,v in actor.state_dict().items()},before=before,result=result,diagnostic=getattr(test,'owned_mean_overflow_last',None))
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();base=W/'MOD4_POWER_RESTORED_THREE_HOST_READONLY_CHECK_20261018/actual_installed_RSL72_sources/rsl_rl/algorithms/ppo.py';owned=B/'payload_h1_native/job0/runtime/isaac/mod4/owned_h1_mean_overflow_ppo_v1.py';assert hashlib.sha256(base.read_bytes()).hexdigest()=='a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c'
 with torch.random.fork_rng(devices=[]):
  torch.manual_seed(60928);old=fixture(update(base,.001));torch.manual_seed(60928);zero=fixture(update(owned,0.));torch.manual_seed(60928);repair=fixture(update(owned,.001))
 assert all(torch.equal(old['actor'][k],zero['actor'][k]) for k in old['actor'])
 assert repair['actor']['mean'][0]>repair['before']['mean'][0] and repair['actor']['mean'][5]<repair['before']['mean'][5]
 assert torch.equal(repair['actor']['mean'][1:5],repair['before']['mean'][1:5]) and torch.equal(repair['actor']['std'],repair['before']['std'])
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),actual_original_and_owned_update_AST_exercised_on_synthetic_CPU=True,twenty_Adam_steps_per_fixture=True,zero_coefficient_actor_and_STD_bitexact_to_original_update=True,auxiliary_gradient_moves_only_overflow_mean_in_zero_advantage_fixture=True,inside_mean_unchanged=True,STD_no_direct_auxiliary_gradient_or_reset=True,before_mean=repair['before']['mean'].tolist(),after_mean=repair['actor']['mean'].tolist(),owned_last_loss_diagnostic=repair['diagnostic'],CPU_RNG_restored=True,no_actual_model_checkpoint_optimizer_GPU_trajectory_or_budget_used=True,not_physical_or_training_improvement_proof=True)
 with (R/'ACTUAL_PPO_UPDATE_AST_SYNTHETIC_CPU_MEAN_REPAIR_POSITIVE_ZERO_COEFFICIENT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('OWNED_PPO_SYNTHETIC_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_production_model_change=True),f,indent=2)
  raise
