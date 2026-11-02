"""Independent saturation-aware exploration candidate; same deterministic policy, reward and physical interface."""
from pathlib import Path
import ast
import hashlib
import json
import time

P=Path(__file__).resolve().parent
T=P.parent
N=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102'
C=T/'RL_SATURATION_EXPLORATION_REPAIR_V442_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert not C.exists()
C.mkdir();(C/'source').mkdir();(C/'reports').mkdir()
for path in sorted((N/'source').rglob('*.py')):
    dest=C/'source'/path.relative_to(N/'source');dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(path.read_bytes())
for name in('feedforward389.json','reference389.npz'):
    (C/name).write_bytes((N/name).read_bytes())
source=(N/'source/actual_transition_learner427.py').read_text('utf8')
source=source.replace('ActualTransitionLearner427','ActualTransitionLearner442')
source=source.replace('(56304, 13364, 25556)','(56465, 13525, 30731)')
source=source.replace("self.rollout_controls = 32\n        self.latent_std = .15", "self.rollout_controls = 32\n        self.latent_std = .15\n        self.exploration_gain = .6\n        self.exploration_max_std = 2.")
source=source.replace("put('ACTUAL427_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json'", "put('ACTUAL442_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json'")
source=source.replace("rollout_controls=32,latent_std=self.latent_std,actual_reward_done_GAE=True,", "rollout_controls=32,latent_std_floor=self.latent_std,exploration_gain=self.exploration_gain,exploration_max_std=self.exploration_max_std,actual_reward_done_GAE=True,")
old='''    def log_prob(self, latent, mean):
        return (-.5*((latent-mean)/self.latent_std).square()
                - math.log(self.latent_std) - .5*math.log(2*math.pi)).sum(-1)
'''
new='''    def exploration_std(self, mean):
        # A per-channel policy distribution. Its variance is recomputed and
        # differentiated in the likelihood; no stale fixed-std PPO ratio.
        return torch.sqrt(self.latent_std**2+(self.exploration_gain*mean).square()).clamp_max(self.exploration_max_std)

    def log_prob(self, latent, mean):
        std = self.exploration_std(mean)
        return (-.5*((latent-mean)/std).square()-std.log()-.5*math.log(2*math.pi)).sum(-1)

    def policy_KL(self, old_mean, updated):
        old_std = self.exploration_std(old_mean)
        new_std = self.exploration_std(updated)
        return (torch.log(new_std/old_std)+(old_std.square()+(old_mean-updated).square())/(2*new_std.square())-.5).sum(-1).mean()
'''
assert old in source
source=source.replace(old,new)
source=source.replace('latent = mean + self.latent_std*noise','latent = mean + self.exploration_std(mean)*noise')
source=source.replace("old_log_prob=self.log_prob(latent,mean).detach(),old_value=", "old_log_prob=self.log_prob(latent,mean).detach(),latent_std=self.exploration_std(mean).detach().clone(),old_value=")
oldKL='actual_KL = .5*((updated-old_mean)/self.latent_std).square().sum(-1).mean()'
assert oldKL in source
source=source.replace(oldKL,'actual_KL = self.policy_KL(old_mean,updated)')
source=source.replace("latent_std=self.latent_std,ratio_mean=float(ratio.detach().mean()),", "latent_std_floor=self.latent_std,latent_std_mean=float(batch['latent_std'].mean()),latent_std_max=float(batch['latent_std'].max()),exploration_gain=self.exploration_gain,exploration_max_std=self.exploration_max_std,ratio_mean=float(ratio.detach().mean()),")
source=source.replace("residual_sampling_rng=self.generator.get_state(),residual_latent_std=self.latent_std,", "residual_sampling_rng=self.generator.get_state(),residual_latent_std=self.latent_std,\n            exploration_protocol=dict(kind='SATURATION_AWARE_LATENT_GAUSSIAN',floor=self.latent_std,gain=self.exploration_gain,max_std=self.exploration_max_std,fullGaussianKL=True,deterministic_action_unchanged=True),")
ast.parse(source)
(C/'source/actual_transition_learner442.py').write_bytes(source.encode('utf8'))
proof=N/'reports/ROOT433_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
task=dict(kind='SATURATION_AWARE_ACTUAL_RESIDUAL_PPO_CANDIDATE442',sourceSHA=json.loads(proof.read_bytes())['SHA'],
          source_offsets=[56465,13525,30731],source_CPU_receipt=str(proof),source_CPU_receiptSHA=H(proof),
          learnerSHA=H(C/'source/actual_transition_learner442.py'),reward_changed=False,deterministic_action_changed=False,
          fixed_learned_STD_frozen=True,SDK=0,physics=0,productionGO=False,
          exploration=dict(floor=.15,gain=.6,max_std=2.,fullGaussianlogprob=True,fullGaussianKL=True),
          actor_trust=dict(KL_limit=.01,max_action_delta=.05,max_backtracks=12),
          evidence=str(P/'reports/DIAG441_ACTUAL437_SATURATED_RESIDUAL_NATIVE_AND_EXPLORATION.json'))
with(C/'TASK442_CANDIDATE.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2)
print(json.dumps(dict(passed=True,root=str(C),learnerSHA=task['learnerSHA'],modelreads=0,SDK=0,physics=0)),flush=True)
