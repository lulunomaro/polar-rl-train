from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;R=T/'reports';N=T/'H1_STEP270_E3_COMMAND_AUDIT_PAIR_V9_20261022';F=T/'H1_STEP270_E3_PAIR_V10_20261022'
read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['passed'] and proof['original_canonical_cost_settled']
base=N/'current_pair_closed_text/h1';hp=next(base.rglob('CLOCK_TRAINING_HEALTH.json'));health=read(hp);log=base/'job0/production_WORKER.log'
audits=[]
with log.open(encoding='utf8') as stream:
    for line in stream:
        if line.startswith('COMMAND_AUDIT '):audits.append(json.loads(line[len('COMMAND_AUDIT '):]))
row=next(x for x in audits if x['control_step']==2401);a=row['spin_command_audit']
assert a['stage']=='H1_step270_external_forward_request_audit_v1' and a['command_matches_existing_publisher'] and a['public_request_envs']==895
assert health['control_steps']==2832 and health['actual_physics_callbacks']==health['expected_physics_callbacks']==11328
assert health['unknown_task_reset_events']==health['integrity_task_reset_events']==0 and not health['nonfinite_observed'] and health['stop_reason'] is None
assert proof['models']['h1']['updates']==118 and proof['models']['h1']['Adam']==680020
put(R/'V100_H1_ACTUAL_CONTROL2401_PASSED_COMPLETE118_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,scope='read original actual worker log and final health plus qualified complete checkpoint receipt; no new GPU or raw replay',actual_command_audits=audits,actual_health=health,log=dict(path=str(log),bytes=log.stat().st_size,SHA=H(log)),health_source=dict(path=str(hp),SHA=H(hp)),complete_h1=proof['models']['h1'],actual_passed_old2401_and_completed2832=True,no_new_270mm_or_graduation_result=True,legacy_audit_field_manual_frozen_evaluation_is_inherited_label_not_this_production_mode=True,reader_path_lookup_error_preserved=dict(attempted_relative='job0/production/LEARN.log',actual_rg_error='IO error: 系统找不到指定的文件。 (os error 2)',observed_outer_shell_exit=0,actual_correct_log='job0/production_WORKER.log',no_experiment_failure_or_reexecution=True),empty_node_console_search_no_matches_exit1=True))
# Preserve the unexecuted source verbatim, then correct only future task/manifest
# metadata inherited from the earlier failed-window repair transition.
p=F/'prepare_pair_from_actual_closed_pair_CPU_once.py';old=p.read_text('utf8');history=F/'reserved_history';history.mkdir();shutil.copy2(p,history/'prepare_pair_from_actual_closed_pair_CPU_V1_UNUSED_METADATA_HISTORY.py')
s=old;needle="task.update(id=cfg['cohort_id']+'_'+key,";assert s.count(needle)==1
s=s.replace(needle,"task.update(qualified_source_fallback_after_failed_pair7=False,only_command_audit_adapter_repair=False,id=cfg['cohort_id']+'_'+key,")
needle="m=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,closed_step270_samephase_continuation=key=='h1')";assert s.count(needle)==1
s=s.replace(needle,"m=dict(oldm,source_SHA=final['SHA'],source_Adamstep=model['Adam'],files=rows,closed_step270_samephase_continuation=key=='h1',explicit_command_audit_adapter_repair=False)")
ast.parse(s);p.write_text(s,encoding='utf8')
put(R/'V100_PAIR10_UNUSED_SAMEPHASE_METADATA_CORRECTION_CPU_ACTUAL.json',dict(epoch=time.time(),only_unused_task_manifest_metadata=True,old_source_SHA=hashlib.sha256(old.encode()).hexdigest(),new_source_SHA=H(p),old_source_retained=str(history/'prepare_pair_from_actual_closed_pair_CPU_V1_UNUSED_METADATA_HISTORY.py'),no_worker_runtime_PPO_account_change=True,new_source_not_prepared_or_run=True,clear_prior_fallback_and_repair_flags_for_next_actual_samephase_source=True))
# A separate new bounded batch selects only the still-present original producer
# files. Earlier verified/deleted files are skipped; no new training disk gate.
src=(N/'relocate_actual_closed_H1_forensics_peer_TLS_bounded_once.py').read_text('utf8')
assert src.count('if free<=25*1024**3:')==1
src=src.replace('if free<=25*1024**3:','if True:  # Remaining authorized closed producer files, not a new training disk threshold.')
src=src.replace("ROOT72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_'+N.name","ROOT72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_REMAINING_V100_'+N.name")
src=src.replace("ROOT210='/mnt/mod4_linux_durable_20261013/PEER_TLS_'+N.name","ROOT210='/mnt/mod4_linux_durable_20261013/PEER_TLS_REMAINING_V100_'+N.name")
src=src.replace('PEER_FORENSICS_','REMAINING_V100_PEER_FORENSICS_')
ast.parse(src);path=N/'relocate_remaining_actual_closed_pair9_H1_peer_TLS_V100_bounded_once.py';path.open('x',encoding='utf8').write(src)
put(R/'V100_REMAINING_CLOSED_PAIR9_PEER_STORAGE_UNUSED_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),source_AST_reserved_only=True,path=str(path),SHA=H(path),requires_actual_current_complete_CPU_cost_allout=True,only_remaining_producer_files_up_to20GiB=True,skip_already_relocated_no_retransfer=True,new_target_controller=True,no_new_training_disk_threshold=True,original25GiB_admission_8GiB_full_update_savedstop_unchanged=True,passed_same_TLS_HMAC_core_reused=True,no_remote_process_yet=True))
print(json.dumps(dict(actual_control2401_passed=True,complete_updates=118,next_unused_metadata_corrected=True,new_remaining_storage_only_source_prepared=True)))
