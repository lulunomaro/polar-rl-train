"""Sync complete138 frozen evidence and only the approved next CURB CPU repair annotation."""
from slope_io import *
import traceback

def main():
    names={'E1_SLOPE10_138_COMPLETE_ACTUAL_COLLECTION.json':sorted(R.glob('SLOPE138_COLLECTED_[0-9]*.json'))[-1],
           'E1_SLOPE10_138_COMPLETE_ACTUAL_REVIEW.json':sorted(R.glob('SLOPE138_ACTUAL_REVIEW_[0-9]*.json'))[-1],
           'E1_SLOPE10_138_COMPLETE_SCOPE_DECISION.json':R/'SLOPE138_COMPLETE_SCOPE_DECISION.json',
           'E1_SLOPE10_138_COMPLETE_DECISION_SCHEMA_ACTUAL_REVIEW.json':R/'SLOPE138_COMPLETE_DECISION_SCHEMA_ACTUAL_REVIEW.json',
           'E1_CURB20_SAVED_ENTRY_EXPOSURE_CPU_REVIEW.json':R/'CURB20_SAVED_ENTRY_EXPOSURE_CPU_REVIEW.json',
           'NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER.md':R/'NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER.md',
           'E1_SLOPE10_138_STAGE_GIT_RECORDED.json':R/'SLOPE138_NORMAL_SCOPE_STAGE_GIT_RECORDED.json'}
    assert json.loads(names['E1_SLOPE10_138_COMPLETE_ACTUAL_REVIEW.json'].read_bytes())['review_complete']
    save('COMPLETE138_CURB_ENTRY_NEXT_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True))
    n,w=connect_both()
    try:
        with n.open_sftp() as f:
            assert all(name not in f.listdir(E+'/reports') for name in names)
            for name,path in names.items():put(f,E+'/reports/'+name,path.read_bytes())
        row=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(__CENTRAL__)/'reports';B=Path(__BUDGET__);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];s=rev['slope10_138_analyticnormal_scope'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE' and s['actual_complete_review_pending']
d=json.loads((R/'E1_SLOPE10_138_COMPLETE_SCOPE_DECISION.json').read_bytes());assert d['scoped10deg_mirrored_frozen_behavior_accepted'] and not d['qualified_full_SLOPE_RM_or_MoE'] and d['next_independent_expert']=='E1_CURB'
assert json.loads(budget)['authorized_training_seconds']==828000 and json.loads(budget)['active_segment'] is None
s.update(actual_complete_review_pending=False,actual_complete_collection=str(R/'E1_SLOPE10_138_COMPLETE_ACTUAL_COLLECTION.json'),actual_complete_review=str(R/'E1_SLOPE10_138_COMPLETE_ACTUAL_REVIEW.json'),actual_complete_decision=str(R/'E1_SLOPE10_138_COMPLETE_SCOPE_DECISION.json'),scoped10deg_frozen_behavior_accepted=True,accepted_observed_slope_angles_deg=[5,8,10],scope_candidate_frozen=True,no_mechanical10deg_PPO=True,qualified_full_SLOPE_or_MoE=False,stage_Git_receipt=str(R/'E1_SLOPE10_138_STAGE_GIT_RECORDED.json'))
rev['slope10_next_CPU_scope'].update(normal_query_GPU_actual_review_pending=False,actual_complete_reference='slope10_138_analyticnormal_scope')
rev.update(active_next_expert='E1_CURB',active_next_phase='CURB20_direction_entry_CPU_contract_preparation',next_independent_work_order=str(R/'NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER.md'),curb20_direction_entry_repair_scope=dict(saved_root_exposure_CPU_audit=str(R/'E1_CURB20_SAVED_ENTRY_EXPOSURE_CPU_REVIEW.json'),work_order=str(R/'NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER.md'),source_checkpoint_SHA=d['next_CURB_warmstart_SHA'],original_CURB133_forward_regression_preserved=True,geometry_height_20mm_unchanged=True,reset_entry_axis_only_preparation=True,actual_fullfootprint_and_command_histogram_contract_pending=True,CPU_component_implementation_not_yet_deployed=True,learning_executor_deployed=False,new_frozen_job_not_published=True,new_budget_seconds=0))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE138-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();append='\n\nActual138 complete/errorfree and independent fullraw/original1e-6 height+explicitanalyticnormal reviewed.10deg ascendingdescending27/27each with1N support,ordinary0/closure.657063094mm/11declaredroute truncations exactcoverage,normalmaxerror2.3291e-8. Own40424b frozen for observed5/8/10deg scopes;no mechanical10PPO/fullSLOPEgategraduation. Next004 independentCURB20 forward direction-entry CPU contract preparation: original13326to22/27 regression kept, source1293c97 warmstart,20mm150mmgeometry/commands/rewardLRhardwareDRclockfamilyproportionsunchanged. Saved2820root grid audit has lower/upper support examples;not freshground wheelcontact or actual commandhistogram proof,causalcoverage claim unproven. Read NEXT_E1_CURB20_DIRECTION_ENTRY_REPAIR_WORK_ORDER. No newCURB implementation/executor/GPU/PPO; actualfullscope admission required,oldonce forbidden,healthyworker/WASDuntouched. MasterapprovaltracksRMcanonical unchanged,allnewreports/schemaerrors/monitorGitaftercare must be captured.\n'.encode()
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.COMPLETE138-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,complete138_and_next_CURB_entry_preparation_synced=True,active_next_expert='E1_CURB',master_approval_tracks_RM_canonical_bytes_preserved=True,no_GPU_PPO_or_budget_write=True,canonical_SHA=hashlib.sha256(budget).hexdigest())))
'''.replace('__CENTRAL__',repr(E)).replace('__BUDGET__',repr(B)))
        p=save('COMPLETE138_CURB_ENTRY_NEXT_METADATA_SYNCED.json',row)
        with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE10_138_COMPLETE_AND_CURB_ENTRY_NEXT_METADATA_SYNCED.json',p.read_bytes())
        print(json.dumps(row))
    finally:cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('COMPLETE138_CURB_ENTRY_NEXT_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_replay=True));raise
