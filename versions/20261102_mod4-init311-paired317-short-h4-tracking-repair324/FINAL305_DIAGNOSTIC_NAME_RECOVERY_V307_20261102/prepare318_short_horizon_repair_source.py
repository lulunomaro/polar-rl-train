"""Prepare an independent evidence-backed short-policy-horizon repair, no GO.

Actual317 measured increasing open-loop drift. WM training remains H32; only the
actor imagination is shortened to four controls (80ms), with actual-TD EMA value.
"""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;S=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101'
D=T/'REFERENCE_SHORT_POLICY_H4_REPAIR_V318_20261102';assert not D.exists();D.mkdir();(D/'reports').mkdir()
shutil.copytree(S/'source',D/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(S/'reference305.npz',D/'reference305.npz')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=(S/'source/tracking_learner305.py').read_text('utf8')
source=source.replace('Reference-conditioned H32 BPTT actor','Reference-conditioned H4 BPTT actor, H32 WM unchanged').replace('TrackingLearner305','TrackingLearner318')
source=source.replace('from tracking_reference305 import GOAL_DIM,tracking_cost305','from tracking_reference315 import GOAL_DIM,tracking_cost315 as tracking_cost305')
old="self.actor_offset=42940+carrier['actual_new_Pi_updates'];self.critic_offset=carrier['actual_new_critic_updates']\n        assert self.actor_offset==45533 and self.critic_offset==2593"
new="self.actor_offset=saved['actor_Adam_offset']+saved['Pi_updates'];self.critic_offset=saved['critic_Adam_offset']+saved['critic_updates']\n        assert self.actor_offset==48257 and self.critic_offset==5317"
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace('self.target_critic=deepcopy(self.critic).eval()','self.target_critic=deepcopy(self.critic).eval()\n        self.target_critic.load_state_dict(saved[\'target_critic_state_dict\'],strict=True)')
source=source.replace("'ACTUAL_RESTORED300_ACTOR_FULL_ADAM'","'ACTUAL_RESTORED305_ACTOR_FULL_ADAM'").replace("'ACTUAL_RESTORED300_CRITIC_FULL_ADAM'","'ACTUAL_RESTORED305_CRITIC_FULL_ADAM'")
source=source.replace('b=wm.buffer;k=32;slots=', 'b=wm.buffer;k=4;slots=').replace('H32=k,batch=', 'H32=False,policy_H=k,WM_H=32,batch=')
source=source.replace('ACTUAL305_TRACKING_THREE_OPTIMIZER_IDENTITIES','ACTUAL318_TRACKING_THREE_OPTIMIZER_IDENTITIES').replace('restored300_all_three_optimizers=True','restored305_all_three_optimizers_and_EMAtarget=True')
source=source.replace('LATEST_ACTOR305_CONSTRAINT','LATEST_ACTOR318_CONSTRAINT').replace('REJECTED_ACTOR305_PROPOSAL','REJECTED_ACTOR318_PROPOSAL')
source=source.replace("goal_dim=GOAL_DIM,tracking_objective=", "goal_dim=GOAL_DIM,policy_horizon=4,WM_supervision_horizon=32,repair_source='actual317H32drift.340485mvsH4.021868m;shortenactoronly',tracking_objective=")
ast.parse(source);(D/'source/tracking_learner318.py').write_bytes(source.encode())
ref=T/'REFERENCE_TERMINAL_HOLD_LABEL_REPAIR_V315_20261102/source/tracking_reference315.py';shutil.copyfile(ref,D/'source/tracking_reference315.py')
classification=T/'FINAL_REPORT_CLASSIFICATION_REPAIR_V312_20261102/source'
(D/'future_control').mkdir()
for p in classification.glob('*.py'):shutil.copyfile(p,D/'future_control'/p.name)
protocol=dict(kind='UNUSED_REFERENCE_TRACKING_H4_REPAIR318_SOURCE_ONLY',status='CPU_VALIDATE_BEFORE_NEW_TASK_OR_GO',source_final_SHA='02b6de0af7da488ea459ef01da36e1cfec1cd72009ed9399e9e02f9646020958',source_model_bytes=32695597,source_WM_updates=12468,source_actor_Adam_step=48257,source_critic_Adam_step=5317,source_teacher_Adam_step=42940,actor_obs=103,critic_obs=106,planned_reference_goal59=True,policy_H=4,WM_training_H=32,objective='same exp(-weightedtrackingcost/5), real own TD/Huber critic, EMA.01 targetcritic,discount.99',terminal_bootstrap='restored exact305EMA, clamp0..100; direct state derivative retained, no claim of calibratedvaluegradients',reference_change='original250endpointlabels unchanged; phase>249 heldpose targets zero allvelocities as validated315',final_report_fix='validated312 source included for future independently versioned node/collector/worker; not deployed',learner_SHA=H(D/'source/tracking_learner318.py'),reference_SHA=H(ref),optimizer_restore='allthreeexactAdam/moments/norm/dedicatedRNG/teacherSTD preserved; freshphysicalepisodes/DRqueue/replay on eventualtraining',actorLR=1e-4,criticLR=1e-4,actor_sampled_action_step_radius=.05,reward_weights_unchanged=True,physics_unchanged=True,canonical_budget_change=False,new_GO=False,deployed=False,source_only_not_launchable=True,evidence317='one-step.00605m,H4.02187m,H16.14915m,H32.34049m; before-resetmaskedactualsame-start owntransitions; notgradientfidelityproof',reason_no_rollback='resume exactfinal305 withcompletehistory; donotrollback2135orresetoptimizers',earlyphysicalinit='311notasufficientfix, donotadopt referenceinitasvalidated',scope='Plannedreference tracker, not autonomous depth-only student; no force/torqueclone or futuredepth/GTmap')
(D/'REPAIR318_SOURCE_PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
print(json.dumps(dict(passed_static=True,root=str(D),policy_H=4,WM_H=32,new_GO=False)))
