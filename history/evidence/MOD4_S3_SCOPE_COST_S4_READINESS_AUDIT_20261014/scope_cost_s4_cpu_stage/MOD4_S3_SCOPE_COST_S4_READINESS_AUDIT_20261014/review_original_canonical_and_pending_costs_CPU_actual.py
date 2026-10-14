"""Accounting evidence only. Never writes a live or second budget authority."""
from pathlib import Path
import json,time,hashlib,math,collections
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
J=lambda p:json.loads(Path(p).read_bytes())
def ref(p):p=Path(p);return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p))

def main():
 collection=sorted(R.glob('ORIGINAL_PLAN_REGISTRY_CANONICAL_ACTUAL_COLLECTION_*.json'))[-1];c=J(collection)
 def pick(name):return Path(next(r['local_path'] for r in c['local_collected_files'] if Path(r['path']).name==name))
 budget=pick('TRAINING_BUDGET_10H.json');b=J(budget);before=H(budget)
 approval=J(pick('PLAN_APPROVAL.json'));revision=J(pick('MOD4_BUDGET_RETRAIN_100H_REVISION_005.json'));v5=J(pick('MOD4_BUDGET_RETRAIN_100H_005_APPROVAL.json'))
 assert approval['approved'] and 'S4' in approval['allowed_stages'] and approval['S8_authorized'] is False
 assert v5['approved'] and H(pick('MOD4_BUDGET_RETRAIN_100H_REVISION_005.json'))==v5['revision_json_sha256']
 assert H(pick('MOD4_BUDGET_RETRAIN_100H_REVISION_005.md'))==v5['revision_md_sha256']
 assert revision['original_S3_30h_plus_new_terrain75h_planning_ceiling_hours']==105
 assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['active_segment'] is None
 assert sum(x['extension_id']=='USER_ADD100H_20261011_7TH' for x in b['budget_extensions'])==1
 assert abs(b['authorized_training_seconds']-b['charged_training_seconds']-b['remaining_training_seconds'])<1e-4
 segments=sorted(b['completed_segments'],key=lambda s:s['started_epoch'])
 assert len({(s['pid'],s['kind'],s['started_epoch']) for s in segments})==len(segments)
 assert all(math.isfinite(s['started_epoch']) and s['ended_epoch']>=s['started_epoch'] for s in segments)
 assert all(l['ended_epoch']<=r['started_epoch'] for l,r in zip(segments,segments[1:]))
 seconds=lambda s:s['ended_epoch']-s['started_epoch']
 e1=[s for s in segments if s['kind'].startswith(('S3_E1_','Linux_original20k_resume_','Linux_left20k_'))]
 buckets=collections.defaultdict(list)
 for s in e1:
  k=s['kind'].lower();log=s.get('log','').lower()
  group='Wave_explicit_and_Linux_Wave_continuation' if ('wave' in k or 'wave' in log or k.startswith('linux_')) else 'CURB_explicit' if ('curb' in k or 'curb' in log) else 'SLOPE_explicit' if ('slope' in k or 'slope' in log) else 'legacy_combined_E1_not_invented_as_one_current_subexpert'
  buckets[group].append(s)
 pending=[]
 temp=W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/reports/LOCAL_TEMP_ALL_ATTEMPTS_COST_CLASSIFICATION_ACTUAL.json';t=J(temp)
 assert t['passed'] and t['canonical_reconciliation_pending']
 for s in t['attempts']:
  if s['canonical_reconciliation_pending']:
   assert s['mode']=='train'
   pending.append(dict(host='human_laptop',kind=s['attempt'],child_pid=s['child_pid'],child_creation=s['child_start'],seconds=s['parent_wall_seconds'],evidence=ref(temp),known_complete_parent_segment=True,not_charged_here=True))
 local=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/EXIT_RECEIPT.json';s=J(local)
 assert s['actual_mode']=='train' and s['canonical_reconciliation_pending']
 pending.append(dict(host='human_laptop',kind='same128_continue_second7200_v1',child_pid=s['child_pid'],started_epoch=s['epoch']-s['wall_seconds'],ended_epoch=s['epoch'],seconds=s['wall_seconds'],evidence=ref(local),known_complete_parent_segment=True,not_charged_here=True))
 root=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013/REMOTE_ACTUAL_EVIDENCE_1791898617180807000'
 paths=[root/'temporary_scope128_memory20GB_logger_ready_v12_20261013/attempts/temporary2048_train_v1/EXIT_RECEIPT.json']
 bench=W/'MOD4_4090_WINDOWS_ENV_CAPACITY_20261013/REMOTE_ACTUAL_EVIDENCE_1791901318423445600'
 paths += [bench/name/'attempts/temporary2048_train_v1/EXIT_RECEIPT.json' for name in ('capacity512_own128_expanded_benchmark_v2_20261013','capacity512_own128_expanded_benchmark_v8_20261013')]
 for p in paths:
  s=J(p);assert s['phase']=='train' and s['no_PPO'] is False and s['canonical_pending']
  duration=s['actual_parent_phase_load_learn_save_exit_seconds']
  pending.append(dict(host='Windows4090',kind=p.parts[-4],child_pid=s['child']['pid'],child_creation=s['child']['created'],started_epoch=s['epoch']-duration,ended_epoch=s['epoch'],seconds=duration,evidence=ref(p),known_complete_parent_segment=True,original_parent_passed_flag_kept=s['passed'],v2_later_PhysX_contactdrop_scope_rejection_preserved='benchmark_v2' in str(p),not_charged_here=True))
 assert len({(p['host'],p['kind'],p['child_pid']) for p in pending})==len(pending)
 for p in pending:
  start=p.get('started_epoch',p.get('child_creation'));end=p.get('ended_epoch',start+p['seconds'])
  assert not any(max(start,s['started_epoch'])<min(end,s['ended_epoch']) for s in segments),'Pending interval already overlaps canonical; match exact UID before proposing any reconciliation'
 prod=bench/'capacity512_selected_ownstate_production_v1_20261013/attempts/temporary2048_train_v1'
 started=prod/'output/WINDOWS4090_PPO_UNIQUE_COST_STARTED.json'
 assert started.is_file() and not (prod/'EXIT_RECEIPT.json').exists() and not (prod/'output/WINDOWS4090_PPO_UNIQUE_COST_ENDED.json').exists()
 report=dict(epoch=time.time(),passed_read_only_accounting_audit=True,original_collection=ref(collection),canonical_snapshot=ref(budget),snapshot_not_second_budget_authority=True,
  original_authorized_seconds=b['authorized_training_seconds'],original_charged_seconds=b['charged_training_seconds'],original_remaining_seconds=b['remaining_training_seconds'],original_remaining_hours=b['remaining_training_seconds']/3600,
  original_completed_segments=len(segments),all_segment_unique_IDs=True,all_original_intervals_nonoverlapping=True,raw_interval_sum_seconds=sum(map(seconds,segments)),original_charged_minus_interval_sum_seconds=b['charged_training_seconds']-sum(map(seconds,segments)),floating_accumulation_difference_recorded_not_rewritten=True,
  S3_E1_explicit_canonical_segment_count=len(e1),S3_E1_canonical_load_learn_save_exit_seconds=sum(map(seconds,e1)),S3_E1_canonical_hours=sum(map(seconds,e1))/3600,S3_E1_segments=e1,
  per_branch_summary={k:dict(count=len(v),seconds=sum(map(seconds,v)),hours=sum(map(seconds,v))/3600) for k,v in buckets.items()},
  includes_discard_PPO_and_failed_learning_startup_cost=True,not_pure_GPU_PPO_time_or_step_count=True,old_pre_S3_mixed_terrain_time_not_relabelled_as_S3=True,
  pending_local_Windows_known_complete_segments=pending,pending_known_complete_seconds=sum(p['seconds'] for p in pending),pending_known_complete_hours=sum(p['seconds'] for p in pending)/3600,
  unknown_interrupted_Windows512_production_tail=dict(started_evidence=ref(started),original_parent_EXIT_and_worker_ENDED_not_collected=True,full_duration_seconds=None,no_walltime_or_max3600_imputation=True,no_refund_or_double_charge=True),
  remaining179h_is_original_canonical_before_pending_reconciliation=True,no_new_canonical_transaction=True,
  approved005=dict(approval=ref(pick('MOD4_BUDGET_RETRAIN_100H_005_APPROVAL.json')),json=ref(pick('MOD4_BUDGET_RETRAIN_100H_REVISION_005.json')),md=ref(pick('MOD4_BUDGET_RETRAIN_100H_REVISION_005.md')),both_approved_SHA_exact=True,original_S3_30h_plus_added_terrain75h_planning_ceiling_hours=105,allowance_not_target_or_second_budget_reservation=True,additional_gate_switching_planning_hours=15),
  previous_only30h_statement_incomplete_and_now_corrected=True,repair_planning_protection_seconds=min(18*3600,.13*b['remaining_training_seconds']),repair_protection_is_planning_only_not_ledger_reservation=True,
  actual_two_fcntl_free=all(not x['actual_fcntl_held'] for x in c['locks']),canonical_idle=True,CPU_SDK_native_frozen_fullrestore0PPO_excluded=True,
  no_training_resume_or_GPU_or_budgetwrite_or_new_authorization=True)
 assert H(budget)==before
 out=R/'S3_E1_CANONICAL_COST_AND_005_105H_PLANNING_ACTUAL_CPU_REVIEW.json';assert not out.exists();out.write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode())
 print(json.dumps(dict(passed=True,E1_canonical_hours=report['S3_E1_canonical_hours'],pending_local_Windows_complete_hours=report['pending_known_complete_hours'],pending_interrupted_tail_unknown=True,approved_terrain_planning_hours=105,original_remaining_hours=report['original_remaining_hours'],protection_hours=report['repair_planning_protection_seconds']/3600,no_canonical_write=True)))

if __name__=='__main__':main()
