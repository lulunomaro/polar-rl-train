"""Retain136 failure and publish independent137/worker evidence in central annotations."""
from slope_io import *
import traceback

def main():
 names={'E1_SLOPE8_136_FAILED_ACTUAL_RESULT_REVIEW.json':sorted(R.glob('SLOPE136_FAILURE_ACTUAL_[0-9]*.json'))[-1],
  'E1_SLOPE8_136_FAILED_BRIDGE_BYTEEXACT.json':R/'SLOPE136_FAILED_BRIDGE_BYTEEXACT.json',
  'E1_SLOPE8_136_QUERY_INPUT_ACTUAL_DIAGNOSIS.json':R/'SLOPE136_QUERY_INPUT_ACTUAL_DIAGNOSIS.json',
  'E1_SLOPE8_137_ACTUALRAY_PREPARED.json':R/'SLOPE137_PREPARED.json',
  'E1_SLOPE8_137_ACTUALRAY_PUBLISHED.json':R/'SLOPE137_PUBLISHED.json',
  'E1_SLOPE8_137_CURRENT_ACTUAL_COLLECTION.json':sorted(R.glob('SLOPE137_COLLECTED_[0-9]*.json'))[-1],
  'E1_SLOPE8_QUERY_REVIEW_WORKER_ADMITTED.json':R/'E1_SLOPE8_QUERY_REVIEW_WORKER_ADMITTED.json',
  'NEXT_E1_SLOPE8_ACTUALRAY137_AND_INDEPENDENT_WORK_ORDER.md':R/'NEXT_E1_SLOPE8_ACTUALRAY137_AND_INDEPENDENT_WORK_ORDER.md'}
 save('SLOPE136_FAILURE_137_REPAIR_SYNC_STARTED.json',dict(epoch=time.time(),one_metadata_CAS=True,no_runtime_or_budget_mutation=True))
 n,w=connect_both()
 try:
  with n.open_sftp() as f:
   prior=f.listdir(E+'/reports');assert all(name not in prior for name in names)
   for name,path in names.items():put(f,E+'/reports/'+name,path.read_bytes())
  row=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,os
R=Path(__CENTRAL__)/'reports';B=Path(__BUDGET__);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE' and rev['slope5_independent_scope']['scoped_5deg_behavior_accepted']
pub=json.loads((R/'E1_SLOPE8_137_ACTUALRAY_PUBLISHED.json').read_bytes());assert hashlib.sha256(budget).hexdigest()==pub['actual_authority']['canonical_SHA'] and json.loads(budget)['active_segment'] is None
rev['slope8_136_frozen_scope'].update(actual_complete_review_pending=False,retained_failed_before_control=True,actual_failure=str(R/'E1_SLOPE8_136_FAILED_ACTUAL_RESULT_REVIEW.json'),actual_bridge_error_byteexact=str(R/'E1_SLOPE8_136_FAILED_BRIDGE_BYTEEXACT.json'),actual_query_input_diagnosis=str(R/'E1_SLOPE8_136_QUERY_INPUT_ACTUAL_DIAGNOSIS.json'),original_failed_raw_kept=True,not_physical_traversal_pass=True)
rev.update(next_independent_work_order=str(R/'NEXT_E1_SLOPE8_ACTUALRAY137_AND_INDEPENDENT_WORK_ORDER.md'),slope8_137_actualray_scope=dict(prepared=str(R/'E1_SLOPE8_137_ACTUALRAY_PREPARED.json'),published=str(R/'E1_SLOPE8_137_ACTUALRAY_PUBLISHED.json'),actual_collection=str(R/'E1_SLOPE8_137_CURRENT_ACTUAL_COLLECTION.json'),source_SHA=pub['jobs'][0]['artifacts']['checkpoint']['sha256'],package_SHA=pub['package']['sha256'],jobs=[x['job_id'] for x in pub['jobs']],worker_namespace='E1_SLOPE8_QUERY_REVIEW',worker_admission=str(R/'E1_SLOPE8_QUERY_REVIEW_WORKER_ADMITTED.json'),actual_complete_review_pending=True,learning_executor_deployed=False,actual_collector='collect_slope137_actual.py',actual_reviewer='review_slope137_actual.py',no_PPO_before_complete137_and_newscope_contracts=True,new_budget_seconds=0))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SLOPE137-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();append='\n\nLatest136 precontrol query assertion preserved: analytic idealfloat64 grid versus actualfloat32 worldray input; CPU independent2800rays reconstructs1.059626870e-6m nominal/input expectation difference, not saved GPUdifference. New137 binds expected height to actualray inputs with original1e-6 tolerance/8deg geometry/loopAST unchanged. Original G3 worker and children naturallyexited and sharedOSlockfree/demandtask0triggers/nonRunning proved before new E1_SLOPE8_QUERY_REVIEW namespace deployed; exact failed136 exclusion only, no baseguardbridgeJSONlock change. New137 actuallypublished, complete pending. Complete135 scoped5deg accepted and negative4pi diagnosticdecline kept. Read NEXT_E1_SLOPE8_ACTUALRAY137_AND_INDEPENDENT_WORK_ORDER, no oldonce/replay or morePPO without newcontracts, masterbudget unchanged.\n'.encode()
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.SLOPE137-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,original136_failure_preserved_and137_actual_scope_synced=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_PPO_4090_launch_or_budget_write=True,canonical_SHA=hashlib.sha256(budget).hexdigest())))
'''.replace('__CENTRAL__',repr(E)).replace('__BUDGET__',repr(B)))
  p=save('SLOPE136_FAILURE_137_REPAIR_METADATA_SYNCED.json',row)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE8_136_FAILURE_AND_137_REPAIR_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(row))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE136_FAILURE_137_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_replay=True));raise
