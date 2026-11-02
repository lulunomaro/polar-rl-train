from pathlib import Path
import importlib.util,json,sys,torch
D=Path(sys.argv[1]);runtime=Path(sys.argv[2]);sys.path[:0]=[str(runtime),str(D/'source')]
from action_delay_physics_queue import PhysicsActionQueue
from planned_hold363 import seed_planned_leg_hold
q=PhysicsActionQueue(80,'cpu',9137,True);neutral=torch.zeros(80,4)
ids=torch.arange(80);q.reset('legs',ids,neutral);q.reset('wheels',ids,torch.zeros(80,2))
before=q.state_dict();actual=torch.tensor([-.04044726,.45523674,-.04044726,.45523674]).expand(40,4).clone()
globalrng=torch.get_rng_state().clone();seed_planned_leg_hold(q,torch.arange(40,80),actual);after=q.state_dict()
assert torch.equal(globalrng,torch.get_rng_state())
for group in before['groups']:
 for field,old in before['groups'][group].items():
  now=after['groups'][group][field]
  if group=='legs'and field in('applied','pending'):
   assert torch.equal(now[:40],old[:40])and torch.equal(now[40:],actual)
  else:assert torch.equal(now,old),(group,field)
 assert torch.equal(before['rng'][group],after['rng'][group])
selected=q.apply('legs',0);hold=q.groups['legs']['lag_steps']>0
assert torch.equal(selected[40:][hold[40:]],actual[hold[40:]])
assert torch.equal(selected[:40],torch.zeros(40,4))
print(json.dumps(dict(passed=True,changed_only_two_selected_target_buffers=True,lag_rng_episode_clock_exact=True,physics=0,SDK=0,NN=0)))
