"""Direct old/new whole80 pairing; original strict failures and every prefix remain."""
from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;W=D.parent
OLD=W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json'
NEW=D/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=json.loads(OLD.read_bytes());b=json.loads(NEW.read_bytes());assert a['passed'] and b['passed'] and a['source_SHA']=='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139' and b['source_SHA']=='cfcefb1c46b33d6028bf6663921fac12a58a5abfdba782e1480a18ac84de541b'
ra=json.loads(Path(a['original_report']['local_path']).read_bytes());rb=json.loads(Path(b['original_report']['local_path']).read_bytes())
differences=[]
def compare(x,y,path):
 if type(x)!=type(y):differences.append(path+'/type');return
 if isinstance(x,dict):
  if set(x)!=set(y):differences.append(path+'/keys');return
  for k in x:compare(x[k],y[k],path+'/'+k)
 elif isinstance(x,list):
  if len(x)!=len(y):differences.append(path+'/len');return
  for i,(p,q) in enumerate(zip(x,y)):compare(p,q,path+'/'+str(i))
 elif x!=y:differences.append(path)
compare(ra['initial'],rb['initial'],'initial')
assert not differences,'Original samefixture initial physical/DR/RNG mismatch retained: '+repr(differences[:20])
for k in ('cohorts','ten_wave_span_m','approach_m','after_support_margin_m','control_dt','controls','callbacks','original_doublewheel_load_threshold_N'):assert a[k]==b[k],k
per=[];outcomes={}
for group in (0,1):
 improved=[];regressed=[];passedboth=[];failedboth=[]
 for old,new in zip(a['rows'],b['rows']):
  assert old['env']==new['env'] and old['group']==new['group']
  if old['group']!=group:continue
  before=old['contact_complete'];after=new['contact_complete']
  bucket=improved if after and not before else regressed if before and not after else passedboth if before else failedboth
  bucket.append(old['env']);per.append(dict(env=old['env'],group=group,old_complete=before,new_complete=after,old_full_valid_episodes=old['all_valid_episodes'],new_full_valid_episodes=new['all_valid_episodes']))
 outcomes[str(group)]=dict(improved=improved,regressed=regressed,passed_both=passedboth,failed_both=failedboth)
report=dict(epoch=time.time(),passed=True,original_full80_review=dict(path=str(OLD),sha256=H(OLD)),new_full80_review=dict(path=str(NEW),sha256=H(NEW)),old_source_SHA=a['source_SHA'],new_source_SHA=b['source_SHA'],actual_all_initial_root_q30_physical_parameters_recipes_assignments_captured_RNG_and_queue_values_exact=True,initial_phases_firstphysics_matched=True,first_retained_prephysics_initial_different_from_legacy_disclosed=True,old_forward=a['forward_complete'],new_forward=b['forward_complete'],old_reverse=a['reverse_complete'],new_reverse=b['reverse_complete'],old_ordinary=a['ordinary'],new_ordinary=b['ordinary'],per_group=outcomes,all_moving54_full_valid_episode_prefixes=per,standing26_no_transit_requirement=True,no_relaxed_contact_route_time_query_or_health_threshold=True,birth_exposure_and_learning_effect_not_isolated_single_causal_factor=True,other_three_inherited_skill_and_scope_decision_pending=True,qualified50=False)
q=D/'reports/PHASE_FINAL_DIRECT_F516_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json';assert not q.exists();q.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(q),old=[a['forward_complete'],a['reverse_complete']],new=[b['forward_complete'],b['reverse_complete']],ordinary=b['ordinary'],initial_exact=True,outcomes=outcomes,qualified50=False)))
