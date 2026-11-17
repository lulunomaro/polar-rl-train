"""Use the same sequence actor in existing frozen local regressions without editing their sources."""
from pathlib import Path
import sys,weakref
import torch
T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(T/'support'));from mod4v3_ppo_v1.history_common import LocalHistoryActor,HistoryQueue
instances=weakref.WeakSet()
class ReplayHistoryActor(LocalHistoryActor):
 def __init__(self):super().__init__();self.queue=HistoryQueue();instances.add(self)
 def load_state_dict(self,state_dict,strict=True,assign=False):
  return super().load_state_dict({k:v for k,v in state_dict.items()if k!='distribution.std_param'},strict=True,assign=assign)
 def reset_history(self):self.queue=HistoryQueue()
 def forward(self,obs):return super().forward(obs,self.queue.append(obs))
def install(legacy=False):
 # Every import route uses this module name. Only in-process classes are replaced.
 sys.path.insert(0,str(R.parent/'runs3060/mod4v3_play_20261107' if legacy else R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core'))
 import play_ppo_flatv1_control as control
 control.ActorMLP=ReplayHistoryActor;original=control.Simulation.reset_standing
 def reset(sim,*args,**kwargs):
  for actor in list(instances):actor.reset_history()
  return original(sim,*args,**kwargs)
 control.Simulation.reset_standing=reset
