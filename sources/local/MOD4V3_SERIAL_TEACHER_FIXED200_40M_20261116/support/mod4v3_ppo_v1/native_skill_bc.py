"""Frozen native MOD4 skill samples; actor-only BC in the existing PPO optimizer."""
from pathlib import Path
import hashlib,json
import numpy as np
import torch
from tensordict import TensorDict
class NativeSkillBC:
 def __init__(self,algorithm,spec):
  self.spec=spec;root=Path(spec['dataset']);self.manifest=json.loads((root/'MANIFEST.json').read_text());path=root/'qualified_mod4_skills.npz'
  self.sha=hashlib.sha256(path.read_bytes()).hexdigest();assert self.sha==self.manifest['sha256']
  assert all(e['qualified']for e in self.manifest['episodes'])and self.manifest['teacher_actor_inference_calls']==0
  device=next(algorithm.actor.parameters()).device;a=np.load(path)
  assert a['obs'].shape[1:]==(35,)and a['actions'].shape==(len(a['obs']),6)
  assert np.isfinite(a['obs']).all()and np.isfinite(a['actions']).all()and np.abs(a['actions']).max()<=6.
  self.obs=torch.as_tensor(a['obs'],device=device);self.actions=torch.as_tensor(a['actions'],device=device);self.weights=torch.as_tensor(a['sampling_weight'],device=device)
  self.window=[];self.actual_optimizer_minibatches=0;self.last={}
 def compute(self,algorithm):
  ids=torch.multinomial(self.weights,int(self.spec['batch_size']),replacement=True)
  y=algorithm.actor(TensorDict({'policy':self.obs[ids]},batch_size=[len(ids)]),stochastic_output=False).clamp(-6.,6.)
  loss=(y-self.actions[ids]).square().sum(-1).mean();assert torch.isfinite(loss)
  if torch.is_grad_enabled():self.window.append(float(loss.detach()));self.actual_optimizer_minibatches+=1
  return float(self.spec['lambda_bc'])*loss
 def finish(self):
  self.last=dict(native_skill_bc_mse=float(sum(self.window)/max(1,len(self.window))),native_skill_samples=len(self.window)*int(self.spec['batch_size']),native_skill_minibatches=len(self.window),actual_optimizer_minibatches_total=self.actual_optimizer_minibatches)
  self.window=[];return self.last
 def summary(self):
  return dict(spec=self.spec,dataset_sha256=self.sha,qualified_episodes=len(self.manifest['episodes']),frames=len(self.obs),last=self.last,actual_optimizer_minibatches_total=self.actual_optimizer_minibatches,teacher_assisted_rollout=False)
