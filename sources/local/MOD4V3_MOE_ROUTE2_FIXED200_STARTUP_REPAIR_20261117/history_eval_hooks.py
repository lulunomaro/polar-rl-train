"""Only this process uses the independently packaged Route2 actor in frozen regressions."""
from pathlib import Path
import sys,weakref
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.route2_common import StatefulRoute2Actor
instances=weakref.WeakSet()
class ReplayHistoryActor(StatefulRoute2Actor):
 def __init__(self):super().__init__();instances.add(self)
def install(legacy=False):
 sys.path.insert(0,str(R.parent/'runs3060/mod4v3_play_20261107'if legacy else R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core'));import play_ppo_flatv1_control as control;control.ActorMLP=ReplayHistoryActor;original=control.Simulation.reset_standing
 def reset(sim,*args,**kwargs):
  for actor in list(instances):actor.reset_history()
  return original(sim,*args,**kwargs)
 control.Simulation.reset_standing=reset
