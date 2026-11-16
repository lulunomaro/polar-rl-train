"""External Serial skill BC plus frozen c874 retention, for a separate native PPO job.

This module does not launch a job or change actor observations. A future job must
activate the already existing7mode slots for its stair/jump rollouts. It is not
installed into the owner's existing course job.
"""
from pathlib import Path
import json,hashlib,copy
import numpy as np,torch
T=Path(__file__).resolve().parent

class SkillSupervision:
 def __init__(self,actor_mlp,keep_checkpoint,dataset_dir=None,lambda_keep=1.,lambda_skill=1.,batch_size=192):
  root=Path(dataset_dir or T/'skill_dataset');manifest=json.loads((root/'MANIFEST.json').read_text())
  path=root/'qualified_mod4_skills.npz';assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['sha256']
  keep=Path(keep_checkpoint);self.keep_sha=hashlib.sha256(keep.read_bytes()).hexdigest()
  assert self.keep_sha=='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'
  state=torch.load(keep,map_location='cpu',weights_only=False)['actor_state_dict']
  self.keep_teacher=copy.deepcopy(actor_mlp).eval().requires_grad_(False)
  self.keep_teacher.load_state_dict({k.removeprefix('mlp.'):v for k,v in state.items()if k.startswith('mlp.')},strict=True)
  device=next(actor_mlp.parameters()).device;a=np.load(path)
  self.obs=torch.as_tensor(a['obs'],device=device);self.actions=torch.as_tensor(a['actions'],device=device);self.weights=torch.as_tensor(a['sampling_weight'],device=device)
  self.lambda_keep=float(lambda_keep);self.lambda_skill=float(lambda_skill);self.batch_size=int(batch_size);self.manifest=manifest
 def loss(self,predict,policy_observations,keep_mask):
  indices=torch.multinomial(self.weights,self.batch_size,replacement=True)
  skill=(predict(self.obs[indices]).clamp(-6.,6.)-self.actions[indices]).square().sum(-1).mean()
  keep_x=policy_observations[keep_mask.reshape(-1)>.5]
  if len(keep_x):
   with torch.no_grad():target=self.keep_teacher(keep_x).clamp(-6.,6.)
   retention=(predict(keep_x).clamp(-6.,6.)-target).square().sum(-1).mean()
  else:retention=skill*0.
  value=self.lambda_keep*retention+self.lambda_skill*skill
  if not torch.isfinite(value):raise ValueError('Nonfinite skill supervision loss')
  return dict(loss=value,keep_loss=retention,skill_loss=skill,keep_samples=len(keep_x),skill_samples=len(indices))
 def native_ppo_loss(self,algorithm,observations):
  from tensordict import TensorDict
  def predict(x):return algorithm.actor(TensorDict({'policy':x},batch_size=[len(x)]),stochastic_output=False)
  return self.loss(predict,observations['policy'],observations['teacher_keep'])['loss']
