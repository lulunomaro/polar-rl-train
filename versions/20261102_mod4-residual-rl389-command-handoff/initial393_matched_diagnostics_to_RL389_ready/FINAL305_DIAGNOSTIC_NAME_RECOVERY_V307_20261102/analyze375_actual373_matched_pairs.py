"""Independent saved373 pair and actual contact acceptance analysis; no SDK/model."""
from pathlib import Path
import hashlib,json,math,time
import numpy as np
P=Path(__file__).resolve().parent;N=P.parent/'MPC_MATCHED_DR_AIR_REQUEST_V373_20261102'
path=N/'reports/ROOT373_EVALUATION_FULL_RETURNED.json';raw=path.read_bytes();full=json.loads(raw)
s=full['result'];assert s and s['passed']and not full['wrapper_error']and s['DR_paired']and s['matched_pairs']==40
get=lambda n:next(json.loads(x['UTF8'])for x in full['full_UTF8']if x['path'].endswith(n))
audit=get('ACTUAL373_MATCHED_D0_D7_AND_NOISE_ADMISSION.json');noise=get('ACTUAL373_MATCHED_SENSOR_NOISE_FINAL.json')
assert audit['passed']and all(x['paired_exact']for x in audit['backend_readback'].values())and all(audit['memory_pair_checks'].values())
assert noise['passed']and all(v>400 for v in noise['channel_calls'].values())
manifold=get('ACTUAL373_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json');trace=get('ACTUAL373_CURRENT_STATE_MPC_CONTROL_TRACE.json')
rows=[{}for _ in range(80)]
for step in trace['rows']:
 for r in step['rows']:rows[r['env']][step['control']]=r
pairs=[];cells=dict(both_success=0,source_only=0,bounded_only=0,both_fail=0)
for i in range(40):
 a,b=s['results'][i],s['results'][i+40];aa,bb=bool(a['strict270_stable']),bool(b['strict270_stable'])
 cell='both_success'if aa and bb else'source_only'if aa else'bounded_only'if bb else'both_fail';cells[cell]+=1
 common=sorted(set(rows[i])&set(rows[i+40]));pre=[];firstchange=None
 for control in common:
  left,right=rows[i][control],rows[i+40][control]
  if left['phase']!='approach'or right['phase']!='approach':break
  pre.append(dict(control=control,state_delta=float(np.max(np.abs(np.array(left['source_state14'])-right['source_state14']))),target_delta=float(np.max(np.abs(np.array(left['processed_target'])-right['processed_target'])))))
 for control in common:
  left,right=rows[i][control],rows[i+40][control]
  if np.max(np.abs(np.array(left['processed_target'])-right['processed_target']))>.0001:
   firstchange=dict(control=control,time=(control-1)*.02,source_phase=left['phase'],bounded_phase=right['phase']);break
 pairs.append(dict(pair=i,source_env=i,bounded_env=i+40,outcome=cell,source_seconds=a['seconds'],bounded_seconds=b['seconds'],lifespan_delta=b['seconds']-a['seconds'],source_full5s=a['full_window'],bounded_full5s=b['full_window'],source_wholeclear=a['first_flight_whole_footprint_clear'],bounded_wholeclear=b['first_flight_whole_footprint_clear'],approach_controls_compared=len(pre),approach_state_maxdelta=max([r['state_delta']for r in pre]or[0]),approach_target_maxdelta=max([r['target_delta']for r in pre]or[0]),first_target_divergence=firstchange))
candidates=[]
for result in s['results']:
 if not result['strict270_stable']:continue
 env=result['env'];start=None;runs=[]
 for row in manifold['rows']:
  good=row['steady'][env]and row['active'][env]
  if good and start is None:start=row['tick']
  if not good and start is not None:runs.append((start,row['tick']-1));start=None
 if start is not None:runs.append((start,len(manifold['rows'])))
 lo,hi=max(runs,key=lambda q:q[1]-q[0]);duration=(hi-lo+1)*.0025;assert duration>=.5
 segment=manifold['rows'][lo-1:hi];forces=np.array([r['top_force_N'][env]for r in segment]);assert (forces>1).all()
 assert all(r['first_flight_wholeclear_latched'][env]and not r['ground_return'][env]and not r['edge_return'][env]for r in segment)
 candidates.append(dict(env=env,pair=env%40,group=result['kind'],stable_interval=[(lo-1)*.0025,hi*.0025],stable_duration=duration,min_top_normal_force_N2=forces.min(0).tolist(),firstflight_wholefootprint=True,no_ground_or_edge_return=True))
assert len(candidates)==s['strict_successes']
release=get('ACTUAL373_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json');closed=json.loads((N/'reports/ROOT373_ALL_SSH_CLOSED_FREE.json').read_bytes())
assert release['all_own_children_waited']and release['private_shared_EX_released']and closed['all_owned_SSH_closed']and closed['SESSION_restored']
n=cells['source_only']+cells['bounded_only'];small=min(cells['source_only'],cells['bounded_only'])
p=None if not n else min(1.,2*sum(math.comb(n,k)for k in range(small+1))/2**n)
v=dict(epoch=time.time(),kind='ACTUAL375_INDEPENDENT373_MATCHED_FULLDR_CONTROL_COMPARISON',passed=True,groups=s['comparisons'],pair_outcomes=cells,discordant_pair_exact_two_sided_p=p,paired_lifespan_mean_delta_seconds=float(np.mean([r['lifespan_delta']for r in pairs])),pairs=pairs,strict_candidates=candidates,matched_actual_parameter_admission=audit,common_sensor_noise=noise,source_receipt=dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),traditional_privileged_MPC_only=True,trained324_still0of80=True,source100Hz_fidelity_not_claimed=True,physics_PD_queue50_100_400_preserved=True,NN=0,checkpoint_reads=0,SDK=0,physics=0,network=0,account_writes=0,all_own_children_waited=True,SSH_closed_FREE=True)
with(P/'reports/ACTUAL375_373_MATCHED_CONTROL_AND_MANIFOLD_RESULTS.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,groups=s['comparisons'],pair_outcomes=cells,discordant_pair_exact_two_sided_p=p,paired_lifespan_mean_delta=v['paired_lifespan_mean_delta_seconds'],approach_state_maxdelta=max(x['approach_state_maxdelta']for x in pairs),approach_target_maxdelta=max(x['approach_target_maxdelta']for x in pairs),candidates=candidates),indent=2))
