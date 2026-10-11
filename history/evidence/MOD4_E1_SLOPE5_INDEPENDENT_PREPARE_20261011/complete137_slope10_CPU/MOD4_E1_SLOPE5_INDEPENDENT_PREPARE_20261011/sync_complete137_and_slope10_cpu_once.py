"""Sync complete8degree frozen review and next10degree CPU preparation only."""
from slope_io import *
import traceback

def main():
 names={'E1_SLOPE8_137_COMPLETE_ACTUAL_COLLECTION.json':sorted(R.glob('SLOPE137_COLLECTED_[0-9]*.json'))[-1],
  'E1_SLOPE8_137_COMPLETE_ACTUAL_REVIEW.json':sorted(R.glob('SLOPE137_ACTUAL_REVIEW_[0-9]*.json'))[-1],
  'E1_SLOPE8_137_COMPLETE_SCOPE_DECISION.json':R/'SLOPE137_COMPLETE_SCOPE_DECISION.json',
  'E1_SLOPE10_CPU_COMPONENT_PREPARED.json':R/'SLOPE10_CPU_COMPONENT_PREPARED.json',
  'NEXT_E1_SLOPE10_GEOMETRY_QUERY_AND_FROZEN_WORK_ORDER.md':R/'NEXT_E1_SLOPE10_GEOMETRY_QUERY_AND_FROZEN_WORK_ORDER.md'}
 assert json.loads(names['E1_SLOPE8_137_COMPLETE_ACTUAL_REVIEW.json'].read_bytes())['review_complete']
 save('COMPLETE137_SLOPE10_CPU_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True))
 n,w=connect_both()
 try:
  with n.open_sftp() as f:
   prior=f.listdir(E+'/reports');assert all(x not in prior for x in names)
   for name,path in names.items():put(f,E+'/reports/'+name,path.read_bytes())
  row=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(__CENTRAL__)/'reports';B=Path(__BUDGET__);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE'
s=rev['slope8_137_actualray_scope'];assert s['actual_complete_review_pending'];d=json.loads((R/'E1_SLOPE8_137_COMPLETE_SCOPE_DECISION.json').read_bytes());assert d['scoped8deg_mirrored_frozen_behavior_accepted'] and not d['qualified_full_SLOPE_or_MoE']
assert json.loads(budget)['active_segment'] is None and json.loads(budget)['authorized_training_seconds']==828000
s.update(actual_complete_review_pending=False,actual_collection=str(R/'E1_SLOPE8_137_COMPLETE_ACTUAL_COLLECTION.json'),actual_complete_review=str(R/'E1_SLOPE8_137_COMPLETE_ACTUAL_REVIEW.json'),actual_complete_decision=str(R/'E1_SLOPE8_137_COMPLETE_SCOPE_DECISION.json'),scoped8deg_frozen_behavior_accepted=True,scope_candidate_frozen=True,qualified_full_SLOPE=False,no_mechanical8deg_PPO_needed_for_observed_scope=True,learning_executor_deployed=False)
rev.update(next_independent_work_order=str(R/'NEXT_E1_SLOPE10_GEOMETRY_QUERY_AND_FROZEN_WORK_ORDER.md'),slope10_next_CPU_scope=dict(component=str(R/'E1_SLOPE10_CPU_COMPONENT_PREPARED.json'),source_SHA=d['source_checkpoint']['sha256'],CPU_component_only=True,normal_query_contract_and_frozen_package_pending=True,new_frozen_job_not_published=True,learning_executor_deployed=False,new_budget_seconds=0))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE137-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();append='\n\nActual137 complete/errorfree twohostbyteexact/fullNPZ/original1e-6 actualray-input ground contract and fullraw callbacks/contactCOMlinkhardware reviewed.8deg mirrored2m ascending27/27 descending27/27 with1N support,ordinary0. Source404own24b is frozen for observed5and8deg scopes;no mechanical8degPPO/no fullSLOPE or gate graduation.136original failure retained. Nextapproved10deg CPU geometry198rays/normals prepared only;cos10=.984807753 means old8deg sample-normal>.99 cannot be blindly reused. Read NEXT_E1_SLOPE10_GEOMETRY_QUERY_AND_FROZEN_WORK_ORDER for new analyticnormal/actualinput contract then unique frozen scope,not threshold relaxation;no10degGPU/package/job/PPO yet. MasterapprovaltracksRMcanonical unchanged, healthynewworker no restart, localWASD untouched.\n'.encode()
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.COMPLETE137-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,complete137_and_next10_CPU_synced=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_GPU_PPO_or_budget_write=True,canonical_SHA=hashlib.sha256(budget).hexdigest())))
'''.replace('__CENTRAL__',repr(E)).replace('__BUDGET__',repr(B)))
  p=save('COMPLETE137_SLOPE10_CPU_METADATA_SYNCED.json',row)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE8_137_COMPLETE_AND_SLOPE10_CPU_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(row))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE137_SLOPE10_CPU_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_replay=True));raise
