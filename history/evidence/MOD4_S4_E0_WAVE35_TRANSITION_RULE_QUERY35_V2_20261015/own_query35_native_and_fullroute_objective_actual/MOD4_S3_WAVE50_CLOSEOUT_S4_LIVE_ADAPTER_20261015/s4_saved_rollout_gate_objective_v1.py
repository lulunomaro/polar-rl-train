"""Historical sampled-z/raw-a objective, separate from current-tick verification.

Pure differentiable objective only; no optimizer step or training launcher.
Environment/DR/global/private RNG fullstate admission is still mandatory.
"""
import math,torch
class SavedGateObjective:
 def __init__(self,router):self.router=router
 def validate(self,obs,z,raw):
  assert obs.ndim==2 and obs.shape[1]==35 and obs.dtype==torch.float32 and torch.isfinite(obs).all()
  assert z.shape==(len(obs),) and z.dtype==torch.int64 and ((z>=0)&(z<2)).all()
  assert raw.shape==(len(obs),6) and torch.isfinite(raw).all()
  normal=torch.zeros_like(obs[:,28:35]);normal[:,0]=1;assert torch.equal(obs[:,28:35],normal)
 def statistics(self,obs,z,raw):
  self.validate(obs,z,raw)
  means=torch.stack([e(obs) for e in self.router.experts],1);logits=self.router.gate(obs)
  rows=torch.arange(len(obs),device=obs.device);m=means[rows,z];std=self.router.std[z]
  gaussian=(-.5*((raw-m)/std).square()-std.log()-.5*math.log(2*math.pi)).sum(-1)
  logp=logits.log_softmax(-1);prob=logp.exp()
  conditional_entropy=(self.router.std.log()+.5*math.log(2*math.pi*math.e)).sum(-1)
  return dict(joint_log_probability=logp[rows,z]+gaussian,conditional_log_probability=gaussian,logits=logits,latent_joint_entropy=-(prob*logp).sum(-1)+(prob*conditional_entropy).sum(-1),frozen_conditional_means=means)
 def losses(self,obs,critic_obs,z,raw,old_log_probability,old_logits,advantages,returns,old_values,clip=.2):
  stats=self.statistics(obs,z,raw);n=len(obs)
  assert critic_obs.shape==(n,38) and torch.isfinite(critic_obs).all() and old_logits.shape==(n,2)
  for x in (old_log_probability,advantages,returns,old_values):assert x.shape==(n,) and torch.isfinite(x).all()
  assert 0<clip<1 and torch.isfinite(old_logits).all()
  log_ratio=stats['joint_log_probability']-old_log_probability;ratio=torch.exp(log_ratio)
  assert torch.isfinite(ratio).all()
  surrogate=torch.maximum(-advantages*ratio,-advantages*ratio.clamp(1-clip,1+clip)).mean()
  value=self.router.critic(critic_obs).squeeze(-1);clipped_value=old_values+(value-old_values).clamp(-clip,clip)
  value_loss=torch.maximum((value-returns).square(),(clipped_value-returns).square()).mean()
  kl=self.router.frozen_expert_joint_KL(old_logits,stats['logits'])
  return dict(policy_loss=surrogate,value_loss=value_loss,entropy=stats['latent_joint_entropy'].mean(),KL=kl.mean(),ratio=ratio,value=value,statistics=stats)
 def gradients_only(self,loss):
  parameters=list(self.router.gate.parameters())+list(self.router.critic.parameters())
  assert {id(p) for g in self.router.optimizer.param_groups for p in g['params']}=={id(p) for p in parameters}
  grads=torch.autograd.grad(loss,parameters,allow_unused=False)
  assert all(torch.isfinite(g).all() for g in grads) and all(not p.requires_grad for e in self.router.experts for p in e.parameters())
  return grads
