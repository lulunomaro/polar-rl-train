"""Actual reviewed geometry/DR, with independent expert bookkeeping only."""
import torch
from e1_terrain_runtime import E1ChassisTerrainEnv,configure_intro
class E1TerrainLearningEnv(E1ChassisTerrainEnv):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs)
  self._e1_episode=torch.zeros(self.num_envs,device=self.device,dtype=torch.long)
 def _reset_idx(self,ids):
  super()._reset_idx(ids)
  if hasattr(self,'_e1_episode'):
   self._e1_episode[ids]+=1
   self._rough_query_tick=None
