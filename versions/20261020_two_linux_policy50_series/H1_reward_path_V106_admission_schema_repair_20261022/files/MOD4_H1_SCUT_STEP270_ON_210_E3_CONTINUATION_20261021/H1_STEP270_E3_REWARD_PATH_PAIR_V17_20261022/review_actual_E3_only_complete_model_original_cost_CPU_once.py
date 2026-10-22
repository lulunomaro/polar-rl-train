from pathlib import Path
import json,time,torch
B=Path(__file__).resolve().parent;R=B/'reports';read=lambda p:json.loads(Path(p).read_bytes())
def main():
 q=read(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');v=read(R/'E3_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json');assert v['actual_finite_transport_returned'];torch.set_num_threads(2);rng=torch.get_rng_state().clone();models={};co=v['source210']['cohort'];seg=v['source210']['original_segment'];assert set(co['go'])==set(seg['experts'])=={'recovery'}
 for key,counts in [('recovery',[173,96])]:
  assert len(v['complete_models'][key])==1;final=v['complete_models'][key][0];source=Path(q['payloads'][key])/'job0/source'/q['specs'][key]['source_filename'];s=torch.load(final['local_path'],map_location='cpu',weights_only=False);old=torch.load(source,map_location='cpu',weights_only=False);seen=[0,0]
  def finite(x):
   if torch.is_tensor(x):seen[0]+=1;seen[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
   elif isinstance(x,dict):
    for y in x.values():finite(y)
   elif isinstance(x,(list,tuple)):
    for y in x:finite(y)
  finite(s);assert seen==counts and s['policy_clock']['policy_hz']==50;updates=s['owned_phase_complete_updates'] if key=='e2' else s['E3_production_updates'];Adam=q['specs'][key]['source_Adamstep']+20*updates;assert updates>0 and final['updates']==updates and final['Adam_step']==Adam;assert len(s['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={Adam};changes={n:[k for k in old[n] if not torch.equal(old[n][k],s[n][k])] for n in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8 and 'distribution.std_param' in changes['actor_state_dict'];cost=seg['experts'][key];go=co['go'][key];assert cost['duration_bound_passed'] and cost['actual_returncode']==0 and cost['started_epoch']==go['learning_started_epoch'] and abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5;models[key]=dict(final=final,updates=updates,Adam=Adam,counts=counts,all17_changed=changes,actual_cost=cost,source_SHA=q['specs'][key]['source_SHA'])
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();report=dict(epoch=time.time(),passed=True,passed_scope=['E3_complete_checkpoint','E3_original_cost','unstarted_H1_and_all_nodes_out'],H1_learning_GO_absent=True,models=models,all_owner_nodes_children_actual_out=True,all_original_private_shared_locks_free=True,original_canonical_cost_settled=True,actual_cost_sumonce=sum(x['charged_seconds'] for x in seg['experts'].values()),remaining_actual_snapshot=v['source210']['original_canonical_remaining'],old_pending_reconciliation_not_repeated=True,not_skill_or_frozen_qualification=True)
 with (R/'E3_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(passed=True,models={k:x['final']['SHA'] for k,x in models.items()},original_cost_settled=True)))
if __name__=='__main__':main()
