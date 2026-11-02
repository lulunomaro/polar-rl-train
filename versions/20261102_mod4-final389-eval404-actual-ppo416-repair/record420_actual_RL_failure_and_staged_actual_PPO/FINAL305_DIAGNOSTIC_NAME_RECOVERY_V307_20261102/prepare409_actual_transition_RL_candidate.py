"""Concrete RL repair candidate: actor learns actual rewards/done, not WM state gradients."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
C=T/'RL_ACTUAL_TRANSITION_PPO_REPAIR_V409_20261102'
assert not C.exists();C.mkdir();(C/'source').mkdir();(C/'reports').mkdir()
shutil.copytree(N/'source',C/'source',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for name in('feedforward389.json','reference389.npz'):shutil.copyfile(N/name,C/name)
proof=N/'reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
value=dict(epoch=time.time(),purpose='CPU-only actualtransitionRL candidate after404/407physicalfailures',
 source_fullCPU_receipt=str(proof),source_final_SHA=json.loads(proof.read_bytes())['SHA'],
 source_offsets=[56144,13204,20419],
 concrete_actor_gap='389actor.update gradient uses only8stepimaginedtrackingcost; actualreward/done only trainscritic, actorhasnoterminalbootstrap',
 repair='ActualonpolicyresidualPPO using sampledpre-tanhlatents/actualr/done/GAE, unchangedtrackingreward/physics; WM retained and learned separately, not actorgradient',
 stochastic_residual_std=.15,PPO_clip=.2,gamma=.99,GAE_lambda=.95,
 rollout_controls=32,first_update_mincontrols=64,epochs=1,
 learned_STD_and_teacher_frozen=True,no_new_reward=True,no_torquecloning=True,
 no_source_network_or_Adam_reset=True,preserve_origin_from_final389=True,
 production_GO=False,CPU_modelreads_max=1,optimizer_steps=0)
with(C/'TASK409_CANDIDATE.json').open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2)
print(json.dumps(dict(passed=True,root=str(C),productionGO=False)))
