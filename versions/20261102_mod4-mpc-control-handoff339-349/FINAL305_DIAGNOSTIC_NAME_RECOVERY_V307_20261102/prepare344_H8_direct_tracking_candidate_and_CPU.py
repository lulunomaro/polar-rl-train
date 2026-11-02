"""Targeted actor candidate after actual339 failure and342 prediction diagnosis."""
from pathlib import Path
import ast, hashlib, json, shutil, time

P=Path(__file__).resolve().parent
T=P.parent
N=T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102'
E=T/'REFERENCE_H8_DIRECT_TRACKING_REPAIR_V344_20261102'
R=P/'reports'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
E.mkdir(exist_ok=False);(E/'reports').mkdir()
shutil.copytree(N/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(N/'reference324.npz',E/'reference324.npz')
learner=(N/'source/tracking_learner324.py').read_text('utf8').replace('TrackingLearner324','TrackingLearner344')
learner=learner.replace('H4 BPTT actor','H8 direct-error BPTT actor').replace('self.actor_offset==48257 and self.critic_offset==5317','self.actor_offset==52636 and self.critic_offset==9696')
learner=learner.replace('wm=self.wm;b=wm.buffer;k=4;','wm=self.wm;b=wm.buffer;k=8;')
learner=learner.replace('total=total+(.99**i)*alive*reward','total=total-(.99**i)*cost/5.  # direct tracking error; no exp attenuation or alive cost deletion')
learner=learner.replace('tracking_loss=-total.mean();terminal_loss=-terminal.mean();loss=tracking_loss+terminal_loss','tracking_loss=-total.mean();terminal_loss=-terminal.mean();loss=tracking_loss+terminal_loss')
learner=learner.replace('policy_horizon=4','policy_horizon=8').replace("repair_source='317H32drift.340485mvsH4.021868m;319terminalgrad29.87vstracking.5309;H4trackingonly'","repair_source='3390cross/24full8swithspindrift;342H8position.018897m/yawtracked;H8directsameweightedcost/noexpattenuation/noactorvalue'")
learner=learner.replace("tracking_objective='exp(-cost/5); same declared weighted tracking plus small regularization'","tracking_objective='actor sumdiscountedweightedcost/5 overH8;noexp/noalivecostdeletion/noactorbootstrap;actualTDcriticusesexpdiagnosticreturn'")
learner=learner.replace('actor_terminal_bootstrap=False,terminal_value_diagnostic_mean=',"actor_terminal_bootstrap=False,actor_direct_tracking_cost=True,actor_alive_mask_applied=False,actual_reward_remains_exp_for_diagnostics=True,terminal_value_diagnostic_mean=")
learner=learner.replace("'ACTUAL324_TRACKING_THREE_OPTIMIZER_IDENTITIES.json'","'ACTUAL344_TRACKING_THREE_OPTIMIZER_IDENTITIES.json'")
ast.parse(learner)
with (E/'source/tracking_learner344.py').open('x',encoding='utf8')as f:f.write(learner)
cpu=(T/'REFERENCE_H4_TRACKING_ONLY_REPAIR_V320_20261102/test320_final305_H4_tracking_no_step_CPU_once.py').read_text('utf8')
cpu=cpu.replace('CPU320','CPU344').replace('CPU320','CPU344')
cpu=cpu.replace('from tracking_reference315 import Reference315 as Reference305','from tracking_reference324 import Reference324 as Reference305')
cpu=cpu.replace('from tracking_learner320 import TrackingLearner320 as TrackingLearner305','from tracking_learner344 import TrackingLearner344 as TrackingLearner305')
cpu=cpu.replace('from tracking_wm305 import TrackingWM305','from tracking_wm324 import TrackingWM324 as TrackingWM305')
cpu=cpu.replace("T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json'","T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102/reports/ROOT324_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'")
cpu=cpu.replace('wm.updates=12468','wm.updates=16879')
cpu=cpu.replace("T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/TASK305_FROZEN.json'","T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102/TASK324_FROZEN.json'")
cpu=cpu.replace("N/'reference305.npz'","N/'reference324.npz'")
cpu=cpu.replace('target305=torch.tensor','target324=torch.tensor')
cpu=cpu.replace("('actor',48257),('critic',5317)","('actor',52636),('critic',9696)")
cpu=cpu.replace("diag['policy_H']==4","diag['policy_H']==8")
cpu=cpu.replace("assert diag['actor_terminal_bootstrap']is False", "assert diag['actor_direct_tracking_cost'] and not diag['actor_alive_mask_applied']\n assert diag['actor_terminal_bootstrap']is False")
cpu=cpu.replace('(42940,48257)','(42940,52636)').replace("==5317 for v in learner.critic_optimizer.state.values()","==9696 for v in learner.critic_optimizer.state.values()")
cpu=cpu.replace('actoroffset48257=True,criticoffset5317=True,WM12468=True,synthetic_H4_no_step=diag','actoroffset52636=True,criticoffset9696=True,WM16879=True,synthetic_H8_direct_no_step=diag')
cpu=cpu.replace('CPU344_RESTORED305_H4_REPAIR_NO_STEP.json','CPU344_RESTORED324_H8_DIRECT_NO_STEP.json')
ast.parse(cpu)
with (E/'test344_final324_H8_direct_no_step_CPU_once.py').open('x',encoding='utf8')as f:f.write(cpu)
report=dict(epoch=time.time(),status='UNUSED_CANDIDATE_CPU_PENDING',root=str(E),source_final324_SHA='841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050',
    actor_H=8,WM_H=32,actor_loss='sum discounted sameweightedtrackingcost/5; no exp attenuation or alive mask; no learnedterminalvalue',
    tracking_components_weights_unchanged=True,actual_environment_reward='exp(-cost/5) unchanged for independentcomparison and criticdiagnostics; actorobjectiveexplicitlydifferent',
    actor_critic_STD_threeAdam_EMA_norm_RNG_fullrestore=True,source_offsets=[52636,9696,16879],noMPCtorquecloning=True,
    physics_unchanged=True,new_budget=0,network=0,SDK=0,model_reads=0,optimizer_steps=0,skill_improvement_not_claimed=True)
with (E/'reports/CANDIDATE344_H8_DIRECT_TRACKING_PROTOCOL.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
