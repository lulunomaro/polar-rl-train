"""RSL5 adapters with independent exploration distributions and independent78D critics."""
import torch
from torch import nn
from torch.distributions import Normal
from rsl_rl.models import MLPModel
from rsl_rl.modules.distribution import GaussianDistribution
from .route2_common import Route2Body
class RoutedGaussian(GaussianDistribution):
 def __init__(self):
  super().__init__(6);del self.std_param;self.e0_std=nn.Parameter(torch.ones(6),requires_grad=False);self.e1_log_std=nn.Parameter(torch.tensor([.25,.25,.25,.25,.4,.4]).log());self.route=None
 def update(self,mean):
  assert self.route is not None;std=torch.where(self.route,self.e1_log_std.exp().expand_as(mean),self.e0_std.expand_as(mean));self._distribution=Normal(mean,std)
class Route2PolicyModel(MLPModel):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);assert self.obs_dim==35 and not self.obs_normalization;self.mlp=Route2Body();self.distribution=RoutedGaussian()
 def get_latent(self,obs,masks=None,hidden_state=None):
  self.distribution.route=obs['policy'][...,29:30]>.5;return torch.cat((obs['policy'],obs['obs_history']),-1)
class Route2CriticBody(nn.Module):
 def __init__(self):
  super().__init__();make=lambda:nn.Sequential(nn.Linear(78,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,1));self.e0=make();self.e0.requires_grad_(False);self.e1=make()
 def forward(self,x):return torch.where(x[...,33:34]>.5,self.e1(x),self.e0(x))
class Route2CriticModel(MLPModel):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);assert self.obs_dim==78 and self.distribution is None;self.mlp=Route2CriticBody()
