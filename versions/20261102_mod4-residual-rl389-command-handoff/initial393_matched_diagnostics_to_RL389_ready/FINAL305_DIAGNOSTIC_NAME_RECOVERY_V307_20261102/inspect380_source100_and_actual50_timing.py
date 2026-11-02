"""CPU schedule facts only. No speculative physical prediction or new gain search."""
from pathlib import Path
import hashlib,json,time
P=Path(__file__).resolve().parent;T=P.parent;N=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102'
b=json.loads((N/'source353_gains.json').read_bytes());duration=b['config']['push_for']
def schedule(dt):
 rows=[];k=0
 while k*dt<duration:
  rows.append(dict(elapsed=round(k*dt,12),alpha=k*dt/duration,hold_seconds=dt));k+=1
 return dict(command_period_s=dt,push_samples=len(rows),last_push_elapsed=rows[-1]['elapsed'],last_push_alpha=rows[-1]['alpha'],first_flight_command_time=k*dt,rows=rows)
source=schedule(.01);actual=schedule(.02)
assert source['push_samples']==10 and actual['push_samples']==5 and source['first_flight_command_time']==actual['first_flight_command_time']==.1
v=dict(epoch=time.time(),kind='ACTUAL380_SOURCE100_AND_CURRENT50_COMMAND_TIMING_FACTS',passed=True,source_MPC_config=b['config'],source_schedule=source,current_schedule=actual,findings=['Source requested push_for0.0908961797s; aligned100Hz and50Hz both issue firstflight command at100ms. Do not claim push duration doubled/halved.','100Hz issues10pushcommands alpha0..0.99014;50Hz issues5 alpha0..0.88012, each heldtwice aslong. Intermediatefeedback/event/targetcommands are absent.','Real source triggers launch on currentmeasuredx/vx every10ms; currentbridge checks every20ms, with original100Hz feedback sampling. Triggerpose/time can differ.','Currentbridge prediction Ad/Bd is actual20ms/H8; source10ms/H15. No physical causal claim from schedule algebra.','ActualD4queue contract requires20ms commands. A sourcefaithful100Hz port must be separateexplicitversion/admission; do not mutate frozenqueueorPD/physicalsolver. A declared20mshold/virtualevent experiment is an approximation, notsourcefaithful100Hz.'],decision='Next scope is precise100Hz-vs50Hz handoff design with initialmeasuredcachefix andactualmanifold. No newtrainingwindow, no replay373377, no blindgain/reward/horizonsearch. Candidatepreboundhasnotprovenrobustsuccess.',checkpoint_reads=0,NN=0,SDK=0,physics=0,network=0,account_writes=0)
with(P/'reports/ACTUAL380_SOURCE100_ACTUAL50_CLOCK_FACTS.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,push_for=duration,source=source,current=actual,decision=v['decision']),indent=2))
