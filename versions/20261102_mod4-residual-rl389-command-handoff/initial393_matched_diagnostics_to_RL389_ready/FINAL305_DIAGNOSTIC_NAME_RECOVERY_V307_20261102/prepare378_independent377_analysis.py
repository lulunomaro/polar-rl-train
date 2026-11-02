"""Independent377 saved-result analysis includes first-feedback identity and D3 strata."""
from pathlib import Path
import ast
P=Path(__file__).resolve().parent
s=(P/'analyze375_actual373_matched_pairs.py').read_text('utf8').replace('373','377').replace('ACTUAL375','ACTUAL378').replace('MPC_MATCHED_DR_AIR_REQUEST_V377','MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377')
s=s.replace("p=None if not n else", "p=None if not n else")
at="v=dict(epoch=time.time(),kind='ACTUAL378_INDEPENDENT377_MATCHED_FULLDR_CONTROL_COMPARISON'"
replacement="""first=[]
for i in range(40):
 left,right=rows[i][1],rows[i+40][1]
 first.append(dict(pair=i,state_delta=float(np.max(np.abs(np.array(left['source_state14'])-right['source_state14']))),target_delta=float(np.max(np.abs(np.array(left['processed_target'])-right['processed_target'])))))
assert max(x['state_delta']for x in first)<1e-6 and max(x['target_delta']for x in first)<1e-5
memory=get('ACTUAL377_NAMED_ACTUATOR_AND_RESET_PARAMETER_MEMORY.json')
strata=[]
for delay in (0,1):
 for start in (0,40):
  chosen=[r for r in s['results'][start:start+40]if memory['D3_delay'][r['env']]==delay]
  strata.append(dict(group=s['comparisons'][start//40]['group'],D3_delay_ms=delay*10,cases=len(chosen),strict=sum(r['strict270_stable']for r in chosen),orientation=sum(bool((r['episode_terminal']or{}).get('flags',{}).get('bad_orientation'))for r in chosen),full5s=sum(r['full_window']for r in chosen)))
v=dict(epoch=time.time(),kind='ACTUAL378_INDEPENDENT377_MATCHED_FULLDR_CONTROL_COMPARISON'"""
assert at in s;s=s.replace(at,replacement)
s=s.replace("groups=s['comparisons'],pair_outcomes=cells", "groups=s['comparisons'],D3_strata=strata,first_control_pair_checks=first,pair_outcomes=cells")
ast.parse(s)
with(P/'analyze378_actual377_matched_pairs.py').open('x',encoding='utf8')as f:f.write(s)
print('prepared378_analysis: zero network/SDK/physics')
