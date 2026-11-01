"""Independent320 removes uncalibrated terminal gradient found by CPU319.

Tracking reward/cost and reference pose labels remain the task. The critic still
learns actual own TD and is saved completely, but supplies no actor bootstrap.
"""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;S=T/'REFERENCE_SHORT_POLICY_H4_REPAIR_V318_20261102'
D=T/'REFERENCE_H4_TRACKING_ONLY_REPAIR_V320_20261102';assert not D.exists();D.mkdir();(D/'reports').mkdir()
shutil.copytree(S/'source',D/'source',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(S/'future_control',D/'future_control')
shutil.copyfile(S/'reference305.npz',D/'reference305.npz')
text=(S/'source/tracking_learner318.py').read_text('utf8').replace('TrackingLearner318','TrackingLearner320').replace('ACTUAL318','ACTUAL320').replace('ACTOR318','ACTOR320')
old="terminal=(.99**k)*alive*forward(self.target_critic,cx).squeeze(-1).clamp(0.,100.)"
new="terminal_value_diagnostic=forward(self.target_critic,cx).squeeze(-1).detach()\n            terminal=total*0.  # Explicitly no learned terminal-value actor gradient."
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('tracking_components=component_sums,','tracking_components=component_sums,actor_terminal_bootstrap=False,terminal_value_diagnostic_mean=float(terminal_value_diagnostic.mean()),')
text=text.replace("repair_source='actual317H32drift.340485mvsH4.021868m;shortenactoronly'", "actor_terminal_bootstrap=False,repair_source='317H32drift.340485mvsH4.021868m;319terminalgrad29.87vstracking.5309;H4trackingonly'")
ast.parse(text);(D/'source/tracking_learner320.py').write_bytes(text.encode())
protocol=json.loads((S/'REPAIR318_SOURCE_PROTOCOL.json').read_bytes());protocol.update(kind='UNUSED_REFERENCE_H4_TRACKING_ONLY_REPAIR320',status='CPU_VALIDATE_BEFORE_NEW_TASK_OR_GO',actor_terminal_bootstrap=False,terminal_bootstrap='explicit0actorcoefficient; actualTD critic andEMA saved/updated only, diagnosticnotdrivingactor',learner_SHA=hashlib.sha256((D/'source/tracking_learner320.py').read_bytes()).hexdigest(),CPU319_observation='syntheticCPUfixture terminal gradient29.86993 vs tracking.53091, not actualgradientproof; sufficient reason to testtrackingonly rather than claimH4alonefixed',source_only_not_launchable=True)
(D/'REPAIR320_SOURCE_PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
test=(S/'test319_final305_H4_no_step_CPU_once.py').read_text('utf8').replace('tracking_learner318','tracking_learner320').replace('TrackingLearner318','TrackingLearner320').replace('CPU319','CPU320')
test=test.replace("assert diag and diag['policy_H']==4 and diag['WM_H']==32 and diag['H32']is False", "assert diag and diag['policy_H']==4 and diag['WM_H']==32 and diag['H32']is False\n assert diag['actor_terminal_bootstrap']is False and diag['first_actual_gradient_components']['terminal_only']==0. and diag['terminal_loss']==0.")
ast.parse(test);(D/'test320_final305_H4_tracking_no_step_CPU_once.py').write_bytes(test.encode())
print(json.dumps(dict(passed_static=True,root=str(D),policy_H=4,WM_H=32,actor_terminal_bootstrap=False,new_GO=False)))
