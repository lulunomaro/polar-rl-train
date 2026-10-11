"""One complete135 and new136 metadata CAS; no runtime/canonical mutation."""
from slope_io import *
from prepare_slope8_frozen136_once import ROOT,CP_SHA
import traceback

def main():
 collection=sorted(R.glob('SLOPE135_COLLECTED_[0-9]*.json'))[-1];review=sorted(R.glob('SLOPE135_SCHEMA_REVIEW_[0-9]*.json'))[-1]
 own=sorted(R.glob('SNAPSHOT_OWN_FORMAL_CPU_[0-9]*.json'))[-1];col136=sorted(R.glob('SLOPE136_COLLECTED_[0-9]*.json'))[-1]
 assert json.loads(review.read_bytes())['review_complete'] and json.loads(own.read_bytes())['canonical']['active'] is None
 schema=dict(epoch=time.time(),trial_id='SLOPE135-COLLECTOR-LEGACY-SCHEMA-REPAIR-01',
  original_collector_source_SHA=H((D/'collect_slope_snapshot135_actual.py').read_bytes()),
  error_reports=[str(p) for p in R.glob('SLOPE135_COLLECTOR_ERROR_[0-9]*.json')],
  new_collector='collect_slope135_schema_actual.py',new_collector_source_SHA=H((D/'collect_slope135_schema_actual.py').read_bytes()),
  change='Only terrain requires full_route_raw; legacy skills bind result SHA=manifest SHA=ownformal SHA and exact job/checkpoint.bin, byteexact host JSON.',
  same_original_terrain_raw_SHA_contract=True,complete135_review=str(review),no_physical_fault_or_eval_replay=True,
  original136_guard_rejection=[str(p) for p in R.glob('SLOPE136_PUBLISH_ERROR_[0-9]*.json')],
  guard_repair='Unique placeholder fixes Python syntax before any remote mutation; independent reviewed publisher performs only unfinished new136 delivery.',
  old_false_raw_cost_and_sources_preserved=True)
 sp=save('SLOPE135_COLLECTOR_SCHEMA_AND_136_GUARD_ACTUAL_REVIEW.json',schema)
 save('COMPLETE135_SLOPE136_SYNC_STARTED.json',dict(epoch=time.time(),complete_review_and_frozen_scope_annotations_only=True))
 reports={'E1_SLOPE5_135_COMPLETE_ACTUAL_COLLECTION.json':collection.read_bytes(),
  'E1_SLOPE5_135_COMPLETE_ACTUAL_REVIEW.json':review.read_bytes(),
  'E1_SLOPE5_135_COMPLETE_SCOPE_DECISION.json':(R/'SLOPE135_COMPLETE_SCOPE_DECISION.json').read_bytes(),
  'E1_SLOPE5_135_COMPLETE_OWN_CPU_ACTUAL.json':own.read_bytes(),
  'E1_SLOPE5_135_COLLECTOR_SCHEMA_AND_136_GUARD_ACTUAL_REVIEW.json':sp.read_bytes(),
  'SELECTED_E1_SLOPE8_FROZEN_SOURCE.json':(R/'SELECTED_E1_SLOPE8_FROZEN_SOURCE.json').read_bytes(),
  'E1_SLOPE8_136_FROZEN_PREPARED.json':(R/'SLOPE8_FROZEN136_PREPARED.json').read_bytes(),
  'E1_SLOPE8_136_FROZEN_PUBLISHED.json':(R/'SLOPE136_PUBLISHED.json').read_bytes(),
  'E1_SLOPE8_136_CURRENT_ACTUAL_COLLECTION.json':col136.read_bytes(),
  'NEXT_E1_SLOPE8_FROZEN_AND_INDEPENDENT_WORK_ORDER.md':(R/'NEXT_E1_SLOPE8_FROZEN_AND_INDEPENDENT_WORK_ORDER.md').read_bytes()}
 n,w=connect_both()
 try:
  with n.open_sftp() as f:
   names=f.listdir(E+'/reports');assert all(name not in names for name in reports)
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  row=linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(__CENTRAL__)/'reports';B=Path(__BUDGET__);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];s=rev['slope5_independent_scope']
assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE' and s['root']==__ROOT__ and s['actual_135_fullreview_pending']
r=json.loads((R/'E1_SLOPE5_135_COMPLETE_ACTUAL_REVIEW.json').read_bytes());d=json.loads((R/'E1_SLOPE5_135_COMPLETE_SCOPE_DECISION.json').read_bytes());pub=json.loads((R/'E1_SLOPE8_136_FROZEN_PUBLISHED.json').read_bytes())
assert r['review_complete'] and d['scoped_5degree_mirrored_traversal_accepted'] and pub['jobs'][0]['artifacts']['checkpoint']['sha256']==__CP_SHA__
assert hashlib.sha256(budget).hexdigest()==pub['actual_authority']['canonical_SHA'] and json.loads(budget)['active_segment'] is None
s.update(actual_135_fullreview_pending=False,actual_135_collection=str(R/'E1_SLOPE5_135_COMPLETE_ACTUAL_COLLECTION.json'),actual_135_complete_review=str(R/'E1_SLOPE5_135_COMPLETE_ACTUAL_REVIEW.json'),actual_135_complete_decision=str(R/'E1_SLOPE5_135_COMPLETE_SCOPE_DECISION.json'),actual_135_collector_schema_review=str(R/'E1_SLOPE5_135_COLLECTOR_SCHEMA_AND_136_GUARD_ACTUAL_REVIEW.json'),actual_collector='collect_slope135_schema_actual.py',scoped_5deg_behavior_accepted=True,scope_candidate_frozen=True,qualified_SLOPE=False,automatic_more_PPO_disallowed=True,actual_new_SDK_native_PPO_pending=False)
rev.update(active_next_expert='E1_SLOPE',next_independent_work_order=str(R/'NEXT_E1_SLOPE8_FROZEN_AND_INDEPENDENT_WORK_ORDER.md'),slope8_136_frozen_scope=dict(prepared=str(R/'E1_SLOPE8_136_FROZEN_PREPARED.json'),published=str(R/'E1_SLOPE8_136_FROZEN_PUBLISHED.json'),actual_collection=str(R/'E1_SLOPE8_136_CURRENT_ACTUAL_COLLECTION.json'),source_selection=str(R/'SELECTED_E1_SLOPE8_FROZEN_SOURCE.json'),source_SHA=__CP_SHA__,jobs=[x['job_id'] for x in pub['jobs']],actual_complete_review_pending=True,learning_executor_deployed=False,actual_collector='collect_slope136_actual.py',actual_reviewer='review_slope136_actual.py',no_more_PPO_without_newscope_contracts=True,new_budget_seconds=0))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE135-SLOPE136-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();append='\n\nActual135 all4 cases complete/errorfree/fullraw and twohost byteexact independently reviewed. Own40424b has scoped5degree mirrored ascending27/27 descending27/27 original1N contact support; stand26 no crossing requirement. Both source364 and own pass54 routes; no causal gain or wholeSLOPE qualification claim. Negative4pi7to5of8 diagnostic decline and originalstrictfalse retained; world64of64. Freeze5degree candidate and advance only approved5to8 angle: new136 frozen actually published using same135 own artifactSHA24b, noPPO/no4090 launch, actualcomplete pending. Read NEXT_E1_SLOPE8_FROZEN_AND_INDEPENDENT_WORK_ORDER. Collector legacy rawfieldKeyError and publisher prewrite literalSyntaxError preserved, noeval replay. MasterapprovaltracksRMcanonical unchanged; localWASD untouched.\n'.encode()
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.COMPLETE135-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,complete135_review_and136_frozen_scope_synced=True,master_approval_tracks_RM_canonical_bytes_preserved=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),no_PPO_4090_launch_or_budget_write=True)))
'''.replace('__CENTRAL__',repr(E)).replace('__BUDGET__',repr(B)).replace('__ROOT__',repr(ROOT)).replace('__CP_SHA__',repr(CP_SHA)))
  rp=save('COMPLETE135_SLOPE136_METADATA_SYNCED.json',row)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE5_135_COMPLETE_AND_SLOPE136_METADATA_SYNCED.json',rp.read_bytes())
  print(json.dumps(row))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE135_SLOPE136_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_replay=True));raise
