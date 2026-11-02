"""Saved actual404 facts only; no model reads, network, SDK, or new physics."""
from pathlib import Path
import json
import statistics
import time

P=Path(__file__).resolve().parent;T=P.parent
E=T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102'
returned=json.loads((E/'reports/ROOT404_EVALUATION_FULL_RETURNED.json').read_bytes())
result=returned['result']
assert not returned['wrapper_error'] and result and result['passed']
assert result['RL_residual'] and not result['online_MPC'] and result['first_episodes']==80
rows=result['results'];assert len(rows)==80
strict=[row for row in rows if row['strict270_stable']]
full=[row for row in rows if row['first_flight_whole_footprint_clear']]
leading=[row for row in rows if row['first_flight_both_cross']]
files={Path(row['path']).name:row['UTF8']for row in returned['full_UTF8']}
manifold=json.loads(files['ACTUAL404_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json'])
audits=[]
for row in strict:
 env=row['env'];longest=0;run=0;interval=None;end=None;topmax=0.;points=0
 for tick in manifold['rows']:
  if tick['active'][env] and tick['steady'][env]:
   run+=1
   if run>longest:longest=run;end=tick['tick']
  else:run=0
  topmax=max(topmax,min(tick['top_force_N'][env]))
 if longest:interval=[(end-longest+1)*.0025,end*.0025]
 for packet in manifold['selected_solver_contact_points']:
  points+=sum(len(contact['position_relative'])for contact in packet['contacts']if contact['env']==env)
 assert row['first_flight_whole_footprint_clear'] and not row['ground_return_after_clear'] and not row['edge_return_after_clear']
 assert longest>=200 and row['longest_stable_seconds']>=.5
 audits.append(dict(env=env,strict_run_ticks=longest,seconds=longest*.0025,interval_seconds=interval,
   max_doublewheel_top_support_N=topmax,selected_raw_contact_points=points,
   actual400Hzmanifold=True,wholefootprint_clear=True,groundedge_return=False))
control=json.loads(files['ACTUAL404_CURRENT_STATE_MPC_CONTROL_TRACE.json'])
residual=[row['learned_residual_mean_abs']for row in control['rows']]
summary=dict(epoch=time.time(),passed=True,scope='Independent actualfinal389 learnedRL on fixedreference270course/newDRseed9137',
 modelSHA=result['model_SHA'],controls=result['controls'],physics=result['physics_callbacks'],
 first_episodes=80,strict=len(strict),strict_envs=[row['env']for row in strict],
 whole_footprint_clear=len(full),leading_cross=len(leading),
 airborne_cases=sum(row['airborne_ever']for row in rows),
 full8s=sum(row['full_window']for row in rows),
 mean_seconds=statistics.mean(row['seconds']for row in rows),
 median_seconds=statistics.median(row['seconds']for row in rows),
 terminations=result['terminations'],
 mean_tracking_cost=statistics.mean(row['tracking_cost_mean']for row in rows),
 mean_tracking_components={key:statistics.mean(row['tracking_components'][key]for row in rows)for key in rows[0]['tracking_components']},
 mean_learned_residual_control=statistics.mean(residual),max_learned_residual_control=max(residual),
 strict_manifold_audits=audits,
 old_RL339=dict(strict=0,full8s=24,orientation=56,mean_seconds=3.35625,
   caveat='Historical324differentactionbaselineandinitialstate; descriptiveonly, not matchedcausalcomparison'),
 RL=True,online_MPC=False,autonomous_depthonly=False,model_reads=0,physics_steps=0,network=0,
 next='Inspect nativeactualposeframes; ifstrict0 do not repeat unchangedonehour; diagnose actualphase/residual versus preservedcommandbaseline from savedfacts')
path=P/'reports/ANALYSIS405_ACTUAL_FINAL389_EVAL404_FACTS_AND_MANIFOLD.json'
with path.open('x',encoding='utf8')as stream:json.dump(summary,stream,indent=2,allow_nan=False)
print(json.dumps(summary),flush=True)
