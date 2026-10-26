"""Pin the real upstream learner; adapt action/state dimension and a pre-action audit hook."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

H=Path(__file__).resolve().parent;T=H.parent
U=T/'MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026/upstream'
D=H/'source/supermimic_vendor';D.mkdir()
def once(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b,1)
records=[]
for name in ('geometry.py','networks.py','replay.py','learner.py'):
    p=U/'src/unisupermimic/rl/algos/supermimic'/name
    raw=p.read_bytes();s=raw.decode('utf8')
    (D/(name+'.upstream_original_bytes.txt')).write_bytes(raw)
    if name=='networks.py':
        s=once(s,'        context_dim: int = 33,\n','        context_dim: int = 33,\n        action_dim: int | None = None,\n')
        s=once(s,'self.in_dim = 13 + 3 * num_joints + context_dim','self.in_dim = 13 + 2 * num_joints + (num_joints if action_dim is None else action_dim) + context_dim')
    if name=='replay.py':
        s=once(s,'    context_dim: int,\n','    context_dim: int,\n    action_dim: int | None = None,\n')
        s=once(s,'"a": (num_joints, torch.float32)','"a": (num_joints if action_dim is None else action_dim, torch.float32)')
        s=once(s,'"a_prev": (num_joints, torch.float32)','"a_prev": (num_joints if action_dim is None else action_dim, torch.float32)')
        s=once(s,'        context_dim: int = 33,\n','        context_dim: int = 33,\n        action_dim: int | None = None,\n')
        s=once(s,'self.fields = _make_fields(num_joints, context_dim)','self.fields = _make_fields(num_joints, context_dim, action_dim)')
    if name=='learner.py':
        s=once(s,'from unilab.rl.contracts.env import EnvProtocol','from typing import Any as EnvProtocol  # annotation-only dependency; our real Isaac bridge implements the protocol')
        s=once(s,'            context_dim=self.mdp.context_dim,\n','            context_dim=self.mdp.context_dim,\n            action_dim=getattr(self.mdp,"action_dim",self.mdp.num_joints),\n')
        s=once(s,'            "context_dim": self.mdp.context_dim,','            "context_dim": self.mdp.context_dim,\n            "action_dim": getattr(self.mdp,"action_dim",self.mdp.num_joints),')
        # Policy output dimension only; physical state and error floors remain30 joints.
        start=s.index('    def _make_policy(');end=s.index('    def _state_info(',start)
        part=s[start:end].replace('num_joints=self.mdp.num_joints','num_joints=getattr(self.mdp,"action_dim",self.mdp.num_joints)').replace('                self.mdp.num_joints,','                getattr(self.mdp,"action_dim",self.mdp.num_joints),')
        s=s[:start]+part+s[end:]
        s=once(s,'        action = self.pi(obs_hist, goal)\n','        action = torch.clamp(self.pi(obs_hist, goal), -6, 6)\n')
        s=once(s,'            action = self.pi(self.obs_hist, goal)\n','            if hasattr(self.env,"before_action"):\n                self.env.before_action()\n            action = self.pi(self.obs_hist, goal)\n')
    # Preserve actual upstream package import paths inside a small isolated package.
    s=s.replace('from unisupermimic.rl.contracts.supermimic import','from supermimic_vendor.contract import').replace('from unisupermimic.rl.logging import','from supermimic_vendor.logging import')
    ast.parse(s)
    (D/name).write_text(s,'utf8')
    records.append(dict(name=name,original_SHA=hashlib.sha256(raw).hexdigest(),adapted_SHA=hashlib.sha256((D/name).read_bytes()).hexdigest()))
shutil.copy2(U/'src/unisupermimic/rl/contracts/supermimic.py',D/'contract.py')
shutil.copy2(U/'src/unisupermimic/rl/logging.py',D/'logging.py')
(D/'__init__.py').write_text('"""Isolated pinned SuperMimic tensor learner with explicit MOD4 adapter."""\n','utf8')
for name in ('LICENSE','NOTICE'):
    shutil.copy2(U/name,D/name)
with (H/'reports/PINNED_UPSTREAM_LEARNER_ACTION_DIM_AND_AUDIT_HOOK_ADAPTER_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',files=records,changes=['action dimension independent of30 joint states','imagination uses original MOD4 execution clip6','single audit hook before policy forward and noise','annotation-only EnvProtocol import and isolated package paths'],native_world_update_policy_update_critic_update_trainloop_bodies_unchanged=True,no_GPU_or_online_training_or_budget_action=True,not_unmodified_G1_reproduction=True),f,indent=2)
print(json.dumps(dict(native_tensor_learner_source_prepared=True,files=len(records))))
