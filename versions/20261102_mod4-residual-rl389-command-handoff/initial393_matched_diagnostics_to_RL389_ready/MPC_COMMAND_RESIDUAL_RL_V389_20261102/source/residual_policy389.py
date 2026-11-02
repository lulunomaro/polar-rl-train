"""Fixed processed-target feedforward + trainable actor residual; no MPC solver."""
from pathlib import Path
import hashlib,json
import torch

class ResidualPolicy389:
 def __init__(self,path,device):
  raw=Path(path).read_bytes();data=json.loads(raw)
  table=torch.tensor(data['commands'],device=device,dtype=torch.float32)
  assert table.shape==(250,6)and torch.isfinite(table).all()
  # Source motor order hip,crank,wheel / hip,crank,wheel -> policy crank,hip,crank,hip,wheel,wheel.
  self.table=table[:,[1,0,4,3,2,5]]/table.new_tensor([.5,.5,.5,.5,10.,10.])
  self.radius=1.
  self.protocol=dict(kind='FIXED347_PROCESSED_TARGET_PLUS_RL_RESIDUAL389',feedforwardSHA=hashlib.sha256(raw).hexdigest(),samples=250,dt=.02,radius=self.radius,leg_residual_max_rad=.5,wheel_residual_max_rad_s=10.,online_MPC=False,source100Hzfaithful=False,residual='radius*tanh(actor_output-frozen_source_actor_output);origin_parameters_frozen,input_gradient_retained',learned_weights_not_reset=True,original_PD_delay_clip_preserved=True)
 def baseline(self,phase):
  phase=phase.long();out=self.table[phase.clamp(0,249)].clone()
  out[:,4:]=torch.where((phase>249)[:,None],torch.zeros_like(out[:,4:]),out[:,4:])
  return out
 def raw(self,actor_output,origin_output,phase):
  assert actor_output.shape==origin_output.shape and actor_output.shape[1]==6
  return self.baseline(phase)+self.radius*torch.tanh(actor_output-origin_output)
 def action(self,actor_output,origin_output,phase):return self.raw(actor_output,origin_output,phase).clamp(-6,6)
