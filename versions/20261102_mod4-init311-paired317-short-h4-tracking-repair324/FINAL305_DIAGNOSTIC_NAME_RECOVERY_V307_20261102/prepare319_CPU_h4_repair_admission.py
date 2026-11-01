"""Prepare the exact318 repair admission from preserved305 CPU fixture."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;D=T/'REFERENCE_SHORT_POLICY_H4_REPAIR_V318_20261102';S=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101'
source=(S/'test305_resume_real_td_CPU_once.py').read_text('utf8')
source=source.replace('One new final300 read for305 resume/EMA/actualTD/survival H32 admission','One necessary final305 read for318 exactresume/EMA/H4 no-step repair admission')
source=source.replace('from tracking_reference305 import Reference305','from tracking_reference315 import Reference315 as Reference305').replace('from tracking_learner305 import TrackingLearner305','from tracking_learner318 import TrackingLearner318 as TrackingLearner305')
source=source.replace("proofpath=T/'REFERENCE_TRACKING_BPTT_V300_20261101/reports/ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'","proofpath=T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json'")
source=source.replace('wm.updates=9712','wm.updates=12468').replace('45533','48257').replace('2593','5317')
source=source.replace("task=json.loads((N/'TASK305_FROZEN.json').read_bytes())", "task=json.loads((T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/TASK305_FROZEN.json').read_bytes())")
source=source.replace('CPU305','CPU319').replace('CPU_'+"'",'CPU_'+"'")
source=source.replace('CPU319_RESUME_AND_NEW_REAL_TD_PURPOSE_CONSUMED','CPU319_FINAL305_H4_REPAIR_PURPOSE_CONSUMED').replace('CPU319_MATCHED_SURVIVAL_REAL_TD_AND_RESUME_NO_STEP','CPU319_RESTORED305_H4_REPAIR_NO_STEP')
source=source.replace('Necessary final300resume/allAdam plus newactualTD+EMAtarget+matchedsurvival integratedH32 no-step','Necessary exactfinal305resume including originalEMAtarget/allAdam; newH4 policy/H32WM+heldrestlabel integratedCPUfixture no optimizer step')
source=source.replace('synthetic_H32_no_step=diag','synthetic_H4_no_step=diag').replace('WM9712=True','WM12468=True')
needle=" assert all(torch.equal(v,ck['student']['critic_state_dict'][k])for k,v in learner.critic.state_dict().items())"
assert needle in source
source=source.replace(needle,needle+"\n assert all(torch.equal(v,ck['student']['target_critic_state_dict'][k])for k,v in learner.target_critic.state_dict().items())")
source=source.replace("assert diag and diag['Pi_updates']", "assert diag and diag['policy_H']==4 and diag['WM_H']==32 and diag['H32']is False\n assert diag['Pi_updates']")
path=D/'test319_final305_H4_no_step_CPU_once.py';ast.parse(source);path.write_bytes(source.encode())
with(D/'reports/SOURCE319_CPU_ADMISSION_READY.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed_static=True,source=str(path),model_reads_max=1,optimizer_steps=0,fixture_synthetic=True,physical_eval=False),f,indent=2)
print(json.dumps(dict(passed=True,reader=str(path))))
