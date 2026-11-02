"""Saved407 learned residual comparison only; no new simulation or inference."""
from pathlib import Path
import json
import math
import statistics
import time

P=Path(__file__).resolve().parent;T=P.parent
E=T/'RL389_MATCHED_RESIDUAL_SCALE_DIAG_V407_20261102'
value=json.loads((E/'reports/ROOT407_EVALUATION_FULL_RETURNED.json').read_bytes())
result=value['result'];assert not value['wrapper_error']and result and result['passed']
assert result['RL_residual']and not result['online_MPC']and result['DR_paired']
rows=result['results'];assert len(rows)==80
groups=[]
for start,name in((0,'full_residual'),(40,'quarter_residual')):
 group=rows[start:start+40]
 groups.append(dict(group=name,cases=40,strict=sum(row['strict270_stable']for row in group),
    wholeclear=sum(row['first_flight_whole_footprint_clear']for row in group),
    leading_cross=sum(row['first_flight_both_cross']for row in group),
    full8s=sum(row['full_window']for row in group),
    orientation=sum(bool((row['episode_terminal']or{}).get('flags',{}).get('bad_orientation'))for row in group),
    mean_seconds=statistics.mean(row['seconds']for row in group),
    median_seconds=statistics.median(row['seconds']for row in group),
    mean_tracking_cost=statistics.mean(row['tracking_cost_mean']for row in group)))
both=sum(rows[i]['strict270_stable']and rows[i+40]['strict270_stable']for i in range(40))
fullonly=sum(rows[i]['strict270_stable']and not rows[i+40]['strict270_stable']for i in range(40))
quarteronly=sum(not rows[i]['strict270_stable']and rows[i+40]['strict270_stable']for i in range(40))
discordant=fullonly+quarteronly
p=1. if discordant==0 else min(1.,2*sum(math.comb(discordant,k)for k in range(min(fullonly,quarteronly)+1))/2**discordant)
texts={Path(row['path']).name:row['UTF8']for row in value['full_UTF8']}
initial=json.loads(texts['ACTUAL407_FIRST_RL_INPUT_AND_SCALE_INTERVENTION.json'])
dr=json.loads(texts['ACTUAL407_MATCHED_D0_D7_INITIAL_NOISE_ADMISSION.json'])
assert dr['passed']and all(row['paired_exact']for row in dr['backend_readback'].values())
decision=('Quarterresidual showsactualstrictcandidates: auditmanifold/nativeposesbeforeproductioncandidate'
    if groups[1]['strict'] else 'Neitherfullnorquarterreachesstrict: residualscalingisnotaskillrepair; do notrepeatunchanged389training')
summary=dict(epoch=time.time(),passed=True,groups=groups,
    paired=dict(both=both,fullonly=fullonly,quarteronly=quarteronly,bothfail=40-both-fullonly-quarteronly,
        exactbinomial_p=p,mean_survival_delta_seconds=statistics.mean(rows[i+40]['seconds']-rows[i]['seconds']for i in range(40))),
    initial_input_differences={key:initial[key]for key in('policy_max_pair_delta','depth_max_pair_delta','goal_max_pair_delta','root_relative_max_pair_delta')},
    actual_backend_DR_readback=dr['backend_readback'],
    caveat='MatchedDR/noise/initialstate does not make contactedfloat32PhysXtrajectories bitwiseidentical; inputs differences reported',
    decision=decision,RL=True,onlineMPC=False,modelreads=0,physics=0,network=0,
    prior404=dict(strict=0,wholeclear=0,orientation=77,full8s=3,mean_seconds=1.375))
path=P/'reports/ANALYSIS408_ACTUAL407_RL_MATCHED_RESIDUAL_SCALE_FACTS.json'
with path.open('x',encoding='utf8')as stream:json.dump(summary,stream,indent=2,allow_nan=False)
print(json.dumps(summary),flush=True)
