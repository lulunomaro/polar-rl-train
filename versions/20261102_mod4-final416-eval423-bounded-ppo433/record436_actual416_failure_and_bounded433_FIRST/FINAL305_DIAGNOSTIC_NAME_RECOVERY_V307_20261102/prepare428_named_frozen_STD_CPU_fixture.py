"""Correct427fixture expectation: frozenSTD retains42940, eightactorMLPstates advance."""
from pathlib import Path
import ast
import json
import shutil
import time
P=Path(__file__).resolve().parent
T=P.parent
O=T/'RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V427_20261102'
C=T/'RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V428_20261102'
assert not C.exists() and list((O/'reports').glob('CPU427_ORIGINAL_ERROR_*.json'))
C.mkdir();(C/'reports').mkdir()
shutil.copytree(O/'source',C/'source',ignore=shutil.ignore_patterns('__pycache__'))
for name in('feedforward389.json','reference389.npz'):shutil.copyfile(O/name,C/name)
test=(O/'test427_actual_saved_rollout_trust_step_CPU_once.py').read_text('utf8')
test=test.replace('CPU427','CPU428')
test=test.replace("    assert all(int(slot['step'])==56305 for slot in learner.actor_optimizer.state.values())",
    "    put('CPU428_PROPOSED_TRUST_STEP_DIAGNOSTIC.json',dict(original_nominal_KL=unbounded_KL,original_nominal_delta=unbounded_delta,candidate=accepted))\n    assert all(int(learner.actor_optimizer.state[p]['step'])==(42940 if name=='distribution.std_param'else56305) for name,p in learner.actor.named_parameters())")
test=test.replace("'else56305","'else 56305")
ast.parse(test)
(C/'test428_actual_saved_rollout_trust_step_CPU_once.py').write_bytes(test.encode('utf8'))
task=json.loads((O/'TASK427_CANDIDATE.json').read_bytes())
task.update(epoch=time.time(),independent428_namedSTDfixture=True,original427errorpreserved=True,
    frozenSTD_Adam42940_not_actorMLP56305=True,learner_bytes_unchanged=True)
with(C/'TASK428_CANDIDATE.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2,ensure_ascii=False)
print(json.dumps(dict(passed=True,root=str(C),modelreads=0,SDK=0,physics=0)))
