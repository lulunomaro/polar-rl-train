"""Freeze real saved budget/cost evidence, never copy or write canonical ledger."""
from pathlib import Path
import json, shutil, time
from materialize_windows20k_target_cpu_once import ref,H,fresh_json,copy_exact

P=Path(__file__).resolve().parent;W=P.parents[1]

def main():
 D=P/'admission_reference_data';assert not D.exists();D.mkdir()
 inputs={
  'BUDGET_APPLIED_7TH_ORIGINAL.json':W/'MOD4_BUDGET_RETRAIN_100H_20261011/reports/BUDGET_APPLIED.json',
  'BUDGET_APPLIED_6TH_ORIGINAL.json':W/'polar-rl-train/history/evidence/20261007-approved-plan-stage0/STAGE_S0_BUDGET_APPLIED.json',
  'LOCAL_TEMP_ALL_ATTEMPTS_COST_CLASSIFICATION_ORIGINAL.json':W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/reports/LOCAL_TEMP_ALL_ATTEMPTS_COST_CLASSIFICATION_ACTUAL.json',
  'LOCAL_CONTINUE_PARENT_EXIT_ORIGINAL.json':W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/EXIT_RECEIPT.json',
  'LOCAL_CONTINUE_DISPATCH_ORIGINAL.json':W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/DISPATCH_RECEIPT.json',
  'LOCAL_CONTINUE_SOURCE_PREPARED_ORIGINAL.json':W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/reports/LOCAL_CONTINUE_SOURCE_PREPARED.json',
  'LOCAL_CONTINUE_SOURCE_FULLSTATE_CPU_ORIGINAL.json':W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/reports/LOCAL_CONTINUE_SOURCE_FULLSTATE_CPU_VERIFIED.json',
  'LIFETIME459_OUTPUT_RESOURCE_ORIGINAL.json':W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/reports/LIFETIME459_ACTUAL_OUTPUT_AND_NEXT_RESOURCE_REFERENCE.json',
  'OLD449_BOUNDARY_RESOURCE_ORIGINAL.json':W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/reports/OLD449_FINAL_BOUNDARY_RESOURCE_ACTUAL.json',
  'WINDOWS4090_HOST_SNAPSHOT_ORIGINAL.json':W/'MOD4_4090_WINDOWS_REPAIR_20261013/reports/WINDOWS4090_HOST_ACTUAL_1791863505659275600.json',
 }
 rows=[]
 classification=json.loads(inputs['LOCAL_TEMP_ALL_ATTEMPTS_COST_CLASSIFICATION_ORIGINAL.json'].read_bytes())
 for r in classification['attempts']:
  n='LOCAL_TEMP_PARENT_EXIT_'+r['attempt']+'_ORIGINAL.json';inputs[n]=Path(r['parent_EXIT_actual_path'])
  actual=json.loads(inputs[n].read_bytes());assert actual['wall_seconds']==r['parent_wall_seconds'] and actual['child_pid']==r['child_pid']
  noPPO=r['native_SDK_fullrestore0PPO_not_charged'];kind='CPU_SDK_native_fullrestore_noPPO' if noPPO else 'failed_learning_startup' if r['failed_learning_startup_cost_retained'] else 'actual_PPO'
  rows.append(dict(unique_segment_identity='childPID_'+str(r['child_pid'])+'_creation_'+str(r['child_start']),already_accounted_original_canonical=False,no_PPO_cost_excluded=noPPO,parent_EXIT_filename=n,parent_EXIT_actual_seconds=actual['wall_seconds'],classification=kind,original_parent_source_SHA_label_preserved_not_corrected=True))
 dispatch=json.loads(inputs['LOCAL_CONTINUE_DISPATCH_ORIGINAL.json'].read_bytes());x=json.loads(inputs['LOCAL_CONTINUE_PARENT_EXIT_ORIGINAL.json'].read_bytes())
 assert x['child_pid']==dispatch['child_pid']==66112
 rows.append(dict(unique_segment_identity='childPID_66112_creation_'+str(dispatch['child_create_time']),already_accounted_original_canonical=False,no_PPO_cost_excluded=False,parent_EXIT_filename='LOCAL_CONTINUE_PARENT_EXIT_ORIGINAL.json',parent_EXIT_actual_seconds=x['wall_seconds'],classification='actual_PPO',actual_source_binding_from_dispatch_and_CPU_source_proof_not_old_EXIT_template=True,old_EXIT_source_SHA_d05c_label_preserved=True))
 total=sum(r['parent_EXIT_actual_seconds'] for r in rows if not r['no_PPO_cost_excluded']);assert abs(total-6060.857095003127)<1e-9
 source_rows=[]
 for n,p in inputs.items():copy_exact(p,D/n);source_rows.append(dict(original=ref(p),frozen_filename=n,frozen=ref(D/n)))
 seventh=json.loads((D/'BUDGET_APPLIED_7TH_ORIGINAL.json').read_bytes());sixth=json.loads((D/'BUDGET_APPLIED_6TH_ORIGINAL.json').read_bytes())
 assert seventh['authorized_after']==1188000 and seventh['extension_records']==7 and sixth['authorized_after']==seventh['authorized_before']==828000
 for r in rows:
  actual=json.loads((D/r['parent_EXIT_filename']).read_bytes());assert actual['epoch']-actual['wall_seconds']>=seventh['epoch']
 fresh_json(D/'PENDING_PARENT_COST_PORTABLE_SOURCE_INDEX.json',dict(epoch=time.time(),rows=rows,total_actual_parent_pendingcost_seconds=total,no_worker_ENDED_added=True,canonical_reconciliation_pending=True,no_canonical_write_copy_refund_or_second_authority=True,parent_source_SHA_label_bug_not_used_to_bind_actual_source=True,original_source_rows=source_rows,all_cost_intervals_inside_saved_snapshot_to_now_walltime=True))
 fresh_json(P/'reports/ACTUAL_BUDGET_COST_REFERENCE_DATA_CPU_PREPARED.json',dict(epoch=time.time(),passed=True,actual_original_saved_evidence_only=True,total_unique_parent_pendingcost_seconds=total,budget_saved_snapshot_epoch=seventh['epoch'],budget_remaining_snapshot_seconds=seventh['remaining_seconds'],saved_remaining_not_current_live=True,seventh_record_applied_total1188000_and_count7_proven=True,individual_first_five_record_values_not_invented=True,walltime_lower_bound_covers_all_localcost_do_not_subtract_twice=True,reference_data_files=[ref(p) for p in sorted(D.iterdir())],resource_actual_snapshots_not_GPU_admission_or_guard_requirements=True,no_GPU_SSH_canonicalwrite_or_source_change=True,Git_ordinary_supplement_pending_root=True))
 print('Actual saved reference inputs frozen; parent pendingcost6060.857095003127s; no canonical copied/written')
if __name__=='__main__':main()
