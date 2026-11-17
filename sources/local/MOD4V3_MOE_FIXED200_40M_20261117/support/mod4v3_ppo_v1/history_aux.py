"""PPO trains only a neural MoE router and critic; complete experts stay immutable."""
import ast,inspect,textwrap,types,copy
from pathlib import Path
import numpy as np,torch
from torch import nn
from tensordict import TensorDict
class HistoryAux:
 def __init__(self,alg,plan):
  self.spec=plan;self.device=next(alg.actor.parameters()).device;d=np.load(Path(plan['root'])/'skill_dataset/history_skills.npz')
  self.data={k:torch.as_tensor(d[k],device=self.device) for k in ['obs','history','actions','sampling_weight','semantic_id','gate_target']};self.data['history']=self.data['history'].flatten(1)
  self.reference_gate=copy.deepcopy(alg.actor.mlp.gate).requires_grad_(False).eval()
  self.teacher=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6)).to(self.device);ck=torch.load(plan['teacher_retention']['keep_teacher'],map_location=self.device,weights_only=False);self.teacher.load_state_dict({k.removeprefix('mlp.'):v for k,v in ck['actor_state_dict'].items()if k.startswith('mlp.')});self.teacher.requires_grad_(False)
  self.steps=0;self.updates=0;self.window=[];self.last={};self.counts=torch.zeros(10,device=self.device,dtype=torch.long)
 def policy(self,alg,x,h):return alg.actor(TensorDict({'policy':x,'obs_history':h},batch_size=[len(x)])).clamp(-6,6)
 def compute(self,alg,obs):
  actor=alg.actor;mask=obs['teacher_keep'].flatten()>.5;x=obs['policy'][mask];h=obs['obs_history'][mask]
  with torch.no_grad():normal_x=x.clone();normal_x[:,28:35]=normal_x.new_tensor([1,0,0,0,0,0,0]);target=self.teacher(normal_x).clamp(-6,6)
  keep=(self.policy(alg,x,h)-target).square().sum(-1).mean()if len(x)else next(actor.mlp.gate.parameters()).sum()*0
  ids=torch.multinomial(self.data['sampling_weight'],256,replacement=True);sx=self.data['obs'][ids];sh=self.data['history'][ids]
  bc=(self.policy(alg,sx,sh)-self.data['actions'][ids]).square().sum(-1).mean()
  logits=actor.mlp.gate_logit(sh);offline_gate=nn.functional.binary_cross_entropy_with_logits(logits,self.data['gate_target'][ids,None])
  pairmask=obs['paired_keep'].flatten()>.5;ph=obs['obs_history'][pairmask].clone().reshape(-1,12,35);ph[:,:,28:35]=ph.new_tensor([0,1,0,0,0,1,0])
  online_gate=nn.functional.binary_cross_entropy_with_logits(actor.mlp.gate_logit(ph.flatten(1)),torch.zeros(len(ph),1,device=self.device))if len(ph)else keep*0
  hh=sh.reshape(-1,12,35);normalized=((hh-actor.mlp.history_mean)/actor.mlp.history_scale).clamp(-10,10).flatten(1)
  with torch.no_grad():prior=self.reference_gate(normalized).sigmoid()
  anchor=(logits.sigmoid()-prior).square().mean()
  loss=keep+bc+.25*offline_gate+.5*online_gate+.05*anchor
  if torch.is_grad_enabled():
   self.steps+=1;self.window.append([float(v.detach())for v in [keep,bc,offline_gate,online_gate,anchor]]);self.counts+=torch.bincount(self.data['semantic_id'][ids].long(),minlength=10)
  assert bool(torch.isfinite(loss));return loss
 def finish_update(self):
  self.updates+=1;a=np.asarray(self.window);self.last=dict(zip(['teacher_keep_mse','moe_action_bc_mse','moe_gate_BCE','moe_flat_negative_BCE','moe_gate_anchor'],a.mean(0).tolist()))if len(a)else{};self.last.update(actual_optimizer_minibatches=self.steps,semantic_samples=self.counts.tolist());self.window=[];return self.last
 def summary(self):return dict(experts_frozen=True,encoder_frozen=True,STD_frozen=True,normal_source='original010m/37dbe178',c874_keep_lambda=1.,trainable='neural MoE router and78D critic',gate_policy_gradient=True,teacher_assistance_at_inference=False,actual_optimizer_minibatches=self.steps,last=self.last,history_H=12,critic_dim=78)
def install_history_aux(algorithm,plan,job):
 aux=HistoryAux(algorithm,plan);original=algorithm.update.__func__;tree=ast.parse(textwrap.dedent(inspect.getsource(original)));fn=tree.body[0];losses=returns=0
 for i,node in reversed(list(enumerate(fn.body))):
  if isinstance(node,ast.For):
   node.body[0:0]=ast.parse('self._check_training_deadline()').body
   for j,item in reversed(list(enumerate(node.body))):
    if isinstance(item,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='loss'for t in item.targets):node.body[j+1:j+1]=ast.parse('loss = loss + self._history_aux.compute(self,batch.observations)').body;losses+=1
  if isinstance(node,ast.Return)and isinstance(node.value,ast.Name)and node.value.id=='loss_dict':fn.body[i:i]=ast.parse('loss_dict.update(self._history_aux.finish_update())').body;returns+=1
 assert(losses,returns)==(1,1);ast.fix_missing_locations(tree);namespace=dict(original.__globals__);exec(compile(tree,'<moe-ppo-router-only>','exec'),namespace);algorithm._history_aux=aux;algorithm.update=types.MethodType(namespace[fn.name],algorithm);return aux
