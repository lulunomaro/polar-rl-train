"""Fudan-style detached, supervised history estimator adapted to RSL5."""
import torch
from rsl_rl.models import MLPModel
from rsl_rl.modules import MLP
from .history_common import HistoryEncoder
class HistoryMLPModel(MLPModel):
 def __init__(self,obs,obs_groups,obs_set,output_dim,hidden_dims=(256,128,64),activation='elu',**kwargs):
  super().__init__(obs,obs_groups,obs_set,output_dim,hidden_dims,activation,**kwargs)
  assert self.obs_dim==35 and obs['obs_history'].shape[-1]==420
  self.mlp=MLP(40,self.distribution.input_dim if self.distribution else output_dim,hidden_dims,activation);self.encoder=HistoryEncoder()
 def get_latent(self,obs,masks=None,hidden_state=None):
  return torch.cat((obs['policy'],self.encoder(obs['obs_history']).detach()),-1)
