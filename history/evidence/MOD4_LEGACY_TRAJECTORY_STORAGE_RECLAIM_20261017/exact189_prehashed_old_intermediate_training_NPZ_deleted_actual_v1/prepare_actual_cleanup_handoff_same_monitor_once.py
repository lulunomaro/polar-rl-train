"""Document actual authorized cleanup and revise the existing monitor; no runtime dispatch."""
from pathlib import Path
import json,time,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;K=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 result=json.loads((R/'SOURCE210_HUMAN_AUTHORIZED_OLD_INTERMEDIATE_TRAJECTORY_DELETION_ACTUAL.json').read_bytes())
 assert result['passed'] and result['deleted_count']==189 and result['protected_other_files_metadata_exact_unchanged']
 disk=result['filesystem_after']['/mnt/mod4_linux_durable_20261013'];assert disk['free']>25*1024**3
 before=result['filesystem_before'];home=result['filesystem_after']['/home/egde/rl_candidates']
 summary=dict(epoch=time.time(),explicit_human_authorization='大量老旧远古训练轨迹可以删除了',actual_single4090_host='10.24.4.210',deleted_files=189,deleted_allocated_bytes=39783354368,
  Windows_D_freed_allocated_bytes=33518743552,Linux_home_freed_allocated_bytes=6264610816,
  Windows_D_actual_before=before['/mnt/mod4_linux_durable_20261013'],Windows_D_actual_after=disk,
  Linux_home_actual_before=before['/home/egde/rl_candidates'],Linux_home_actual_after=home,
  current_D_available_exceeds_original25GiB=True,no_training_admission_guard_lowered=True,
  protected_other_files=27509,all_protected_metadata_unchanged=True,
  first2_last2_S4_completed_rollouts_and_per_run_retention_first_last_kept=True,
  all_models_checkpoints_code_reports_frozen_eval_raw_failure_prefixes_and_current_tasks_kept=True,
  only_explicitly_listed_old_intermediate_raw_intentionally_deleted=True,
  no_false_claim_listed_deleted_originals_still_exist=True,no_global_FD_absence_or_backup_copy_claim=True,
  original_V1_V2_local_count_rejections_V3_V4_proc_permission_rejections_preserved=True,
  V2_inferred_nonexistent_raw148_reader_claim_corrected_in_V3_actual148_exact_paths=True,
  per_file_SHA_predelete_and_durable_delete_journal_preserved=True,
  Windows_C_system_still_readonly_no_writes_remount_or_cleanup=True,
  no_H1_worker_newnative_GO_or_PPO_started_by_cleanup=True,
  current_original_H1_rejection_terminal_not_rewritten_or_hotadded=True,
  next_H1_requires_actual_new_resource_full_source121_backend_native180_and_original_writer_handoff=True,
  current_recovery_FINAL_CPU_cost_exit_locks_not_collected_by_cleanup=True,
  E2_paid_learning_still_held_after_fixed112_1of64=True,no_new_budget_or_auto_cleanup_or_extra_monitor=True)
 save(R/'SOURCE210_39P8GB_CLEANUP_D37GB_AVAILABLE_COMPACT_ACTUAL.json',summary)
 save(B/'NEXT_STORAGE_RECLAIMED_H1_ORIGINAL_SAFE_HANDOFF_ACTUAL_WORK_ORDER.json',dict(epoch=time.time(),cleanup=summary,
  predelete_manifest=dict(path=str(R/'EXACT_OLD_INTERMEDIATE_TRAJECTORIES_PREDELETE_FULL_SHA_AND_PROTECTED_FILES_V5_ACTUAL.json'),SHA=H(R/'EXACT_OLD_INTERMEDIATE_TRAJECTORIES_PREDELETE_FULL_SHA_AND_PROTECTED_FILES_V5_ACTUAL.json')),
  apply_receipt=dict(path=str(R/'SOURCE210_HUMAN_AUTHORIZED_OLD_INTERMEDIATE_TRAJECTORY_DELETION_ACTUAL.json'),SHA=H(R/'SOURCE210_HUMAN_AUTHORIZED_OLD_INTERMEDIATE_TRAJECTORY_DELETION_ACTUAL.json')),
  previous_training_workorder=str(K/'NEXT_RECOVERY_FIRST_CPU_FIXED112_FROZEN1_E2_SOURCE_REVIEW_HOLD_ACTUAL_WORK_ORDER.json'),
  authorized_next_work=['Read actual current recovery owner/FINAL/original canonical/two real fcntl and target identity; collect only missing complete final, CPU sourcefreeze and real cost/out. Do not infer final from15:37 nominalend.',
   'Storage reason is physically resolved on existing authorized writable Windows D; do not ask for the same D authorization or expansion again. Check current actual free space and retained25GiB guard before a new H1 stage.',
   'Prepare/resume original healthy same-stage H1 fullclosed121 source3f7feb09c0034d0d902526c2f03a36e84db37d3d93b68b380a2ed844eb063a75/Adam643700, its own newsource/backend native180 full CPU and safe one-original-writer handoff; no hot-add to the consumed current H1 terminal.',
   'Do not reopen E2 paid learning without actual source/frame/reward diagnosis; preserve fixed10122/fixed1050/fixed1121of64 and all original gates/false.',
   'Record this distinct human-authorized cleanup stage once, then ordinary supplements; big old remote raw files are intentionally deleted only by this exact189-file list, historical precleanup indexes remain unchanged.'],
  Git_unique_new_stage_id='human-authorized-old-intermediate-trajectory-space-reclaim',Git_pending_until_actual_remote_main_tag_peel_all_oldtags_and_tracked_SHA=True))
 args=json.loads((K/'AUTOMATION_UPDATE_RECOVERY_FIRST_FIXED112_FROZEN1_V2_ARGS.json').read_bytes());old=args['prompt'];oldpath=B/'ORIGINAL_PRE_HUMAN_OLD_TRAJECTORY_CLEANUP_MOD4_10_PROMPT_UTF8.txt'
 with oldpath.open('xb') as f:f.write(old.encode('utf8'))
 begin=old.index('人类磁盘问题已实测答复');end=old.index('\n\n本K唯一stage',begin)
 replacement='''最新human已明确“ 大量老旧远古训练轨迹可以删除了 ”，并已按精确白名单在210单4090执行，不再是等待人类扩容/路径答复。L=C:/Users/lulu/Desktop/claude/mjcf/MOD4_LEGACY_TRAJECTORY_STORAGE_RECLAIM_20261017，先读L/NEXT_STORAGE_RECLAIMED_H1_ORIGINAL_SAFE_HANDOFF_ACTUAL_WORK_ORDER.json与reports/SOURCE210_39P8GB_CLEANUP_D37GB_AVAILABLE_COMPACT_ACTUAL.json、SOURCE210_HUMAN_AUTHORIZED_OLD_INTERMEDIATE_TRAJECTORY_DELETION_ACTUAL.json。实际删除189个10月15日及更早的中间训练NPZ，39783354368allocatedB≈39.8GB：D33518743552B/home6264610816B；Dfree从3445854208到36964507648B≈37.0GB/34.4GiB，homefree从2782736384到9047347200B。所有候选完整SHA/路径inode-size-mtime与旧S4原索引核后才删；27509个其余文件元数据前后exact，所有模型/源码/报告/冻结eval raw/失败prefix与各轮首末样本保留。S4 completed148只有raw0..147，保留0/1/146/147，删除2..145；中间retention_prefix保留每run首末。原V1/V2读者把非retentionNPZ聚合149误当rollout149而本机拒绝、原V3/V4全局proc FD权限拒绝与V2错误推断raw148均保留，新V3实际148路径集与原index逐项exact，新V5按明确旧路径/UID/inode/age/fullSHA和可读进程路径引用核，不冒全局FD无占用或备份存在。删除journal与前SHA durable保存在210 L同名root和本机报告；旧原索引是删除前历史，不改成false/pass或声称已删原件仍存在。此授权只本次精确189清单，未建立自动清理政策；不删目录/模型/最新任务/他人文件，不追删已不存在raw、不为hash重GPU。
原WindowsD数据/dev/nvme0n1p5早已授权writable/fsync mounted /mnt/mod4_linux_durable_20261013，本次实际腾出D空间，原25GiB GPUguard保持。WindowsC系统/dev/nvme0n1p3 mounted /mnt/mod4_windows_readonly_20261013/system约509.8GBfree仍只读，本授权不写C/重挂/清系统/搬原件/tmpfs冒durable。原ownMOD4总227.1GB是清理前快照，不再冒当前总量；D其他既有192.4GB不能算我们。H1当前旧contract的preGO资源拒绝行仍原false/0worker/0GO/0账，不能改旧terminal或hotadd；物理空间障碍已解决，不能继续机械等待同storagepending。积极收当前自救真正FINAL/fullCPU/实际成本/父孩子out/canonicalNone/两真实fcntl交接后，推进原批准H1同阶段完整closed121 source3f7feb09c0034d0d902526c2f03a36e84db37d3d93b68b380a2ed844eb063a75/Adam643700、完整target/source/backend、自己的新unused native180全CPU与原writer安全handoff，再按实际有限grant学习；不把cleanup或Dfree当已H1native/PPO、不能双writer或自动延旧grant。不要重复问原D授权/相同扩容问题。E2仍行为审查hold，recovery只按lateractual，不因磁盘好了说三卡全PPO。'''
 prompt=old[:begin]+replacement+old[end:]
 prompt='最新human/ownactual（2026-10-17北京时间15:38后）优先覆盖旧storagepending和全raw原件永久保留字段：已按人类明确授权完成精确189个旧中间训练轨迹清理、D现约37GB可用且原25GiB guard未改。当前cleanup没有派任何新H1/PPO，也未替自救收FINAL。L新唯一stage reserved ID human-authorized-old-intermediate-trajectory-space-reclaim，需按AGENTS一次record_experiment annotatedtrial后ordinary，以lateractualGitreceipt/HEAD/remote为准，若已record绝不重record/tag/helper。旧K唯一39bd29af...永不重record；K后普通4f22fd8e1741fb0952fe890f9c66862a027c3f2a已remote/all1367旧tag原object-peel/tracked1660核。本L所有成功/失败/读者计数与权限拒绝/精确删除清单和SHA/实际释放空间/工作单/monitor/receipt必须Git，旧false与报告不覆盖。\n\n'+prompt
 prompt=prompt.replace('最新ownactual优先（2026-10-17北京时间15:18后', '前一训练snapshot（2026-10-17北京时间15:18后',1)
 prompt=prompt.replace('人类本轮将获自救新完整firstCPU和fixed112完整1/64(+0,-1)通知，之后', '自救新完整firstCPU和fixed112完整1/64(+0,-1)已通知；本轮人类已知实际39.8GB清理/D约37GB可用，之后')
 prompt=prompt.strip().replace('\r\n','\n');args['prompt']=prompt
 path=B/'MONITOR_HUMAN_AUTHORIZED_OLD_TRAJECTORY_CLEANUP_STORAGE_RESTORED_UTF8LF_V1_20261017.txt'
 with path.open('xb') as f:f.write(prompt.encode('utf8'))
 save(B/'AUTOMATION_UPDATE_OLD_TRAJECTORY_CLEANUP_STORAGE_RESTORED_ARGS.json',args)
 print(json.dumps(dict(summary=summary,prompt_SHA=H(path),old_prompt_SHA=H(oldpath),existing_monitor_only=True)),flush=True)

if __name__=='__main__':main()
