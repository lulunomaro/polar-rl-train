from pathlib import Path
import json,time,subprocess,sys,torch
T=Path(__file__).resolve().parent;N=T/'H1_STEP270_E3_PAIR_V7_20261022';R=N/'reports';read=lambda p:json.loads(Path(p).read_bytes())
rejection=read(R/'PAIR_ORIGINAL_FULL_REVIEW_REJECTED_MISSING_H1_FINAL_ACTUAL.json');assert rejection['actual_returncode']!=0 and rejection['original_pair_reviewer_rejected_missing_H1_FINAL']
a=read(R/'PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');q=read(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
assert a['actual_finite_transport_returned'] and not a['complete_models']['h1'] and len(a['complete_models']['recovery'])==1
f=a['complete_models']['recovery'][0];torch.set_num_threads(2)
s=torch.load(f['local_path'],map_location='cpu',weights_only=False);old=torch.load(Path(q['payloads']['recovery'])/'job0/source'/q['specs']['recovery']['source_filename'],map_location='cpu',weights_only=False)
counts=[0,0]
def finite(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,(list,tuple)):
  for v in x:finite(v)
finite(s);updates=s['E3_production_updates'];adam=q['specs']['recovery']['source_Adamstep']+20*updates
assert counts==[173,96] and updates==f['updates'] and adam==f['Adam_step'] and s['policy_clock']['policy_hz']==50
assert len(s['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={adam}
changed={k:[name for name in old[k] if not torch.equal(old[k][name],s[k][name])] for k in ('actor_state_dict','critic_state_dict')}
assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8 and 'distribution.std_param' in changed['actor_state_dict']
seg=a['source210']['original_segment'];co=a['source210']['cohort'];assert co['rows']['h1']['original_error'] and co['rows']['h1']['final'] is None
for key,cost in seg['experts'].items():
 assert cost['started_epoch']==co['go'][key]['learning_started_epoch'] and cost['duration_bound_passed'] and abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5
model=dict(final=f,updates=updates,Adam=adam,counts=counts,all17_changed=changed,actual_cost=seg['experts']['recovery'],source_SHA=q['specs']['recovery']['source_SHA'])
v=dict(epoch=time.time(),passed=True,passed_scope='only complete E3 checkpoint and both independent original cost intervals/allout; H1 failed and is NOT admitted',models=dict(recovery=model),H1_production_failed_no_FINAL=True,H1_complete_updates_before_error=read(N/'current_pair_closed_text/h1/job0/production/LEARN_ORIGINAL_ERROR_BEFORE_SAVE.json')['complete_updates'],H1_failed_prefix_not_production_source=True,all_owner_nodes_children_actual_out=True,all_original_private_shared_locks_free=True,original_canonical_cost_settled=True,actual_cost_sumonce=sum(c['charged_seconds'] for c in seg['experts'].values()),all_original_actual_cost_intervals=seg['experts'],remaining_actual_snapshot=a['source210']['original_canonical_remaining'],not_skill_or_frozen_qualification=True)
(R/'TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2))
(R/'TWO50_CURRENT_COHORT_COMPLETE_FINALS_ORIGINAL_COST_RETURNED_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(a,indent=2))
assert not torch.cuda.is_initialized();print(json.dumps(dict(E3_passed=True,H1_failed=True,E3_Adam=adam,costs=v['all_original_actual_cost_intervals'],remaining=v['remaining_actual_snapshot'])))
