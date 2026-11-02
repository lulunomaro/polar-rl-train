"""Independent453 actual launch-to-landing return window, unchanged reward/physical/deterministic action."""
from pathlib import Path
import ast
import hashlib
import json

P=Path(__file__).resolve().parent;T=P.parent
O=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102'
C=T/'RL_LAUNCH_LANDING_RETURN_REPAIR_V453_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert not C.exists();C.mkdir();(C/'source').mkdir();(C/'reports').mkdir()
for path in sorted((O/'source').rglob('*.py')):
    dest=C/'source'/path.relative_to(O/'source');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
for name in('feedforward389.json','reference389.npz'):(C/name).write_bytes((O/name).read_bytes())
source=(O/'source/actual_transition_learner442.py').read_text('utf8')
source=source.replace('ActualTransitionLearner442','ActualTransitionLearner453').replace('(56465, 13525, 30731)','(56634, 13694, 36159)')
source=source.replace('self.rollout_controls = 32','self.rollout_controls = 128\n        self.gae_lambda = 1.0')
source=source.replace("put('ACTUAL442_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json'", "put('ACTUAL453_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json'")
source=source.replace('rollout_controls=32,latent_std_floor', 'rollout_controls=self.rollout_controls,GAE_lambda=self.gae_lambda,latent_std_floor')
source=source.replace("batch['next_value'],batch['done'])", "batch['next_value'],batch['done'],lam=self.gae_lambda)")
source=source.replace('actor_horizon_actual_controls=32','actor_horizon_actual_controls=self.rollout_controls')
source=source.replace("actor_training='actual onpolicy residualPPO/GAE gamma.99lambda.95clip.2/oneepoch/32controls'", "actor_training='actual onpolicy residualPPO/full128controlreturn gamma.99lambda1clip.2/oneepoch',GAE_lambda=self.gae_lambda")
assert 'self.rollout_controls = 128'in source and 'lam=self.gae_lambda'in source
assert 'rollout_controls=32'not in source and 'actor_horizon_actual_controls=32'not in source
ast.parse(source);path=C/'source/actual_transition_learner453.py';path.write_bytes(source.encode('utf8'))
task=dict(kind='ACTUAL_LAUNCH_LANDING_RETURN_PPO_CANDIDATE453',sourceSHA='056410f592d07ff63c3acc6adac4d1ebb0357bc154e817568bec56ba155f18ed',
    source_offsets=[56634,13694,36159],learnerSHA=H(path),rollout_controls=128,seconds=2.56,gamma=.99,GAE_lambda=1.,
    WM_horizon=32,WM_replay64_independent=True,unchanged_reward=True,unchanged_deterministic_action=True,
    unchanged_fullGaussian_exploration=True,unchanged_postAdamKL_residualbound=True,physics_changes=False,productionGO=False,
    rationale=str(P/'reports/DIAG452_ACTUAL446_NATIVE_EARLY_YAW_PITCH_AND_GAE_TIMING.json'))
with(C/'TASK453_CANDIDATE.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2)
print(json.dumps(dict(passed=True,root=str(C),learnerSHA=H(path),modelreads=0,SDK=0,physics=0)),flush=True)
