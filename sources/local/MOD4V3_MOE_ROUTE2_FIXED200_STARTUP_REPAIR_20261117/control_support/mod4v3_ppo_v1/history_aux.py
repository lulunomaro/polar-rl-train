"""One PPO optimizer: c874 normal retention, semantic BC, paired startup, physical encoder supervision."""
import ast,inspect,textwrap,types,json,time
from pathlib import Path
import torch,numpy as np
from torch import nn
from tensordict import TensorDict
class HistoryAux:
 def __init__(self,alg,plan):
  self.spec=plan;self.device=next(alg.actor.parameters()).device;data=np.load(Path(plan['root'])/'skill_dataset/history_skills.npz')
  self.data={k:torch.as_tensor(data[k],device=self.device)for k in ['obs','history','actions','targets','sampling_weight','semantic_id']};self.data['history']=self.data['history'].flatten(1)
  self.teacher=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6)).to(self.device)
  frozen=torch.load(plan['teacher_retention']['keep_teacher'],map_location=self.device,weights_only=False);self.teacher.load_state_dict({k.removeprefix('mlp.'):v for k,v in frozen['actor_state_dict'].items()if k.startswith('mlp.')},strict=True);self.teacher.requires_grad_(False);self.teacher.eval()
  self.success_replay=None;self.steps=0;self.updates=0;self.window=[];self.last={};self.counts=torch.zeros(10,device=self.device,dtype=torch.long)
 def policy(self,alg,x,h):return alg.actor(TensorDict({'policy':x,'obs_history':h},batch_size=[len(x)])).clamp(-6,6)
 def compute(self,alg,obs):
  mask=obs['teacher_keep'].flatten()>.5;x=obs['policy'][mask];h=obs['obs_history'][mask]
  with torch.no_grad():target=self.teacher(x).clamp(-6,6)
  keep=(self.policy(alg,x,h)-target).square().sum(-1).mean()if len(x)else next(alg.actor.parameters()).sum()*0
  pairmask=obs['paired_keep'].flatten()>.5;ph=obs['obs_history'][pairmask].clone().reshape(-1,12,35);ph[:,:,28:35]=ph.new_tensor([0,1,0,0,0,1,0])
  online_gate=torch.nn.functional.binary_cross_entropy_with_logits(alg.actor.mlp.gate_logit(ph.flatten(1)),torch.zeros(len(ph),1,device=self.device)) if len(ph) else keep*0
  ids=torch.multinomial(self.data['sampling_weight'],256,replacement=True);sx=self.data['obs'][ids];sh=self.data['history'][ids];bc=(self.policy(alg,sx,sh)-self.data['actions'][ids]).square().sum(-1).mean()
  online_target=torch.cat((obs['critic'][:,28:31],obs['critic'][:,69:71]),-1).detach();z=alg.actor.encoder(obs['obs_history']);zt=alg.actor.encoder(sh);targets=self.data['targets'][ids]
  encoder=(z[:,:3]-online_target[:,:3]).square().mean()+.5*(z[:,3:]-online_target[:,3:]).square().mean()+.5*(zt[:,:3]-targets[:,:3]).square().mean()+.25*(zt[:,3:]-targets[:,3:]).square().mean()
  sid=self.data['semantic_id'][ids];gate_target=((sid>=3)&(sid<=8)).float().unsqueeze(-1)
  offline_gate=torch.nn.functional.binary_cross_entropy_with_logits(alg.actor.mlp.gate_logit(sh),gate_target)
  gate_loss=offline_gate+.5*online_gate
  coefficient=1.;loss=keep+coefficient*bc+encoder+gate_loss
  if torch.is_grad_enabled():
   self.steps+=1;self.window.append([float(t.detach())for t in (keep,gate_loss,bc,encoder)]+[coefficient]);self.counts+=torch.bincount(self.data['semantic_id'][ids].long(),minlength=10)
  assert torch.isfinite(loss);return loss
 def finish_update(self):
  self.updates+=1;a=np.asarray(self.window);self.last=dict(zip(['teacher_keep_mse','history_contact_gate_BCE','skill_bc_mse','encoder_loss','skill_coefficient'],a.mean(0).tolist()))if len(a)else{};self.last.update(actual_optimizer_minibatches=self.steps,semantic_samples=self.counts.tolist());self.window=[];return self.last
 def summary(self):return dict(keep_lambda=1.,paired_action_loss_lambda=0.,gate_supervision_lambda=1.,normal_preservation="frozen original010m weights and frozen action STD",gate_policy_gradient=False,encoder_lambda=1.,skill_lambda=1.,warmup_minibatches=0,actual_optimizer_minibatches=self.steps,last=self.last,history_H=12,latent_dim=5,critic_dim=78,teacher_actor_gradients=False)

def install_history_aux(algorithm,plan,job):
 aux=HistoryAux(algorithm,plan);original=algorithm.update.__func__;tree=ast.parse(textwrap.dedent(inspect.getsource(original)));fn=tree.body[0];losses=returns=0
 for i,node in reversed(list(enumerate(fn.body))):
  if isinstance(node,ast.For):
   # Guard each minibatch; discard a partial update only before its optimizer starts.
   node.body[0:0]=ast.parse('self._check_training_deadline()').body
   for j,item in reversed(list(enumerate(node.body))):
    if isinstance(item,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='loss'for t in item.targets):node.body[j+1:j+1]=ast.parse('loss = loss + self._history_aux.compute(self,batch.observations)').body;losses+=1
  if isinstance(node,ast.Return)and isinstance(node.value,ast.Name)and node.value.id=='loss_dict':fn.body[i:i]=ast.parse('loss_dict.update(self._history_aux.finish_update())').body;returns+=1
 assert(losses,returns)==(1,1);ast.fix_missing_locations(tree);namespace=dict(original.__globals__);exec(compile(tree,'<history-ppo-with-supervised-encoder>','exec'),namespace);algorithm._history_aux=aux;algorithm.update=types.MethodType(namespace['update'],algorithm);algorithm._check_training_deadline=lambda:None
 (Path(job)/'PPO_HISTORY_UPDATE.py').write_text(ast.unparse(tree)+'\n');return aux
