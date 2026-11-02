"""Analyze saved368 state/command/DR only; no checkpoint, SDK or network."""
from pathlib import Path
import hashlib,json,time
import numpy as np
P=Path(__file__).resolve().parent;N=P.parent/'MPC_AIR_WHEEL_REQUEST_ENVELOPE_V368_20261102'
path=N/'reports/ROOT368_EVALUATION_FULL_RETURNED.json';raw=path.read_bytes();full=json.loads(raw)
assert full['result']['passed'] and not full['wrapper_error']
get=lambda token:next(json.loads(x['UTF8']) for x in full['full_UTF8'] if x['path'].endswith(token))
trace=get('ACTUAL368_CURRENT_STATE_MPC_CONTROL_TRACE.json');dr=get('ACTUAL368_NAMED_ACTUATOR_AND_RESET_PARAMETER_MEMORY.json')
rows=[[] for _ in range(80)]
for step in trace['rows']:
 for row in step['rows']:rows[row['env']].append(dict(time=step['seconds'],**row))
facts=[]
for result,rr in zip(full['result']['results'],rows):
 i=result['env'];push=next((r for r in rr if r['phase']=='push'),None);air=[r for r in rr if r['phase'] in ('push','flight','extend')]
 first_pitch=next((r['time'] for r in rr if abs(r['source_state14'][2])>.2),None)
 facts.append(dict(env=i,group=result['kind'],strict=result['strict270_stable'],seconds=result['seconds'],full5s=result['full_window'],orientation=bool((result['episode_terminal']or{}).get('flags',{}).get('bad_orientation')),launch=None if push is None else dict(time=push['time'],x=push['source_state14'][0],vx=push['source_state14'][7],pitch=push['source_state14'][2],pitch_rate=push['source_state14'][9],leg_q=push['source_state14'][3:7],leg_dq=push['source_state14'][10:14]),first_abs_pitch_over_point2=first_pitch,air_controls=len(air),air_target60=sum(max(abs(r['processed_target'][k]) for k in (2,5))>=59.999 for r in air),max_source_wheel_request=max([abs(r['tau_source_requested'][k]) for r in air for k in (2,5)]or[0]),DR=dict(mass_factor=dr['D0_factor'][i],nominal_D0=dr['D0_nominal'][i],mu=dr['D0_mu'][i],D2_bias=dr['D2_bias'][i],D3_delay=dr['D3_delay'][i],D4lag={k:g['lag_steps'][i] for k,g in dr['D4'].items()},D5=dr['D5_gas_stiffness'][i],D6=dr['D6_gas_damping'][i],D7COM=dr['D7_COM_delta'][i],motor_gain={k:a['episode_scale'][i] for k,a in dr['actuators'].items() if 'episode_scale' in a})))
groups=[]
for start in (0,40):
 for success in (False,True):
  chosen=[r for r in facts[start:start+40] if r['strict']==success];launch=[r['launch'] for r in chosen if r['launch']]
  mean=lambda seq:None if not len(seq) else np.mean(seq,axis=0).tolist()
  groups.append(dict(group=facts[start]['group'],strict=success,n=len(chosen),mean_life=mean([r['seconds'] for r in chosen]),launch_mean={k:mean([r[k] for r in launch]) for k in ('time','x','vx','pitch','pitch_rate','leg_q','leg_dq')},mass_mean=mean([r['DR']['mass_factor']for r in chosen]),mu_mean=mean([r['DR']['mu']for r in chosen]),delay10ms=sum(r['DR']['D3_delay']==1 for r in chosen),lag_counts={k:{str(j):sum(r['DR']['D4lag'][k]==j for r in chosen)for j in(0,1,2)}for k in('legs','wheels')}))
v=dict(epoch=time.time(),kind='ACTUAL372_SAVED368_PUSH_STATE_DR_ASSOCIATIONS',passed=True,source=dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),facts=facts,groups=groups,conclusion='Source/bounded groups differ in per-env D0-D7 and sensor samples; observed success associations are descriptive. Next independent373 matches 40pairs D0-D7 plus common per-tick sensor noise, preserves50/100/400Hz and actual366manifold acceptance. No training345.',NN=0,SDK=0,network=0,physics=0,checkpoint_reads=0,account_writes=0)
with(P/'reports/ACTUAL372_SAVED368_PUSH_DR_ASSOCIATIONS.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,groups=groups),indent=2))
