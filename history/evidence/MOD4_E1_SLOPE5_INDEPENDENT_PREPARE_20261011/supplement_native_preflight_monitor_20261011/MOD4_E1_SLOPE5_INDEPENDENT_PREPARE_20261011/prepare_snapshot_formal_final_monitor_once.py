from slope_io import *
own=json.loads(sorted(R.glob('SNAPSHOT_OWN_FORMAL_CPU_[0-9]*.json'))[-1].read_bytes());assert not own['pending'] and own['ready']
row=own['formal_PASSED'];h=row['health'];seg=row['unique_completed_segment'][0];seconds=seg['ended_epoch']-seg['started_epoch'];ck=own['checkpoint']
head=f'''最新2026-10-11 source404自己的SLOPE5 formal已经自然完整保存退出，旧402/404big活动及fresh活动只历史。先读中央E1_SLOPE5_SNAPSHOT_REVIEWED_FORMAL_FINAL_ACTUAL_REVIEW、OWN_FORMAL_CPU_VERIFIED、FORMAL_FINAL_CURRENT_ACTUAL、COMPLETE_PREFLIGHT_ACTUAL_REVIEW、E1_SLOPE5_135_ACTUAL_CURRENT_COLLECTION与FORMAL_CLOSEOUT_METADATA_SYNCED；本机MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011/reports最新SNAPSHOT_OWN_FORMAL_CPU/SLOPE_SNAPSHOT_ACTUAL/135collection/review实际优先。

owncheckpoint={ck['path']}，SHA{ck['sha256']}/CPU{ck['finite_tensors']}/source404/实际{own['actual_snapshot_count']}snapshot+404ownfreeze/PID{own['own_PID_receipt']['pid']}/PASSED与唯一账段已核。{row['actual_updates']}updates/{h['control_steps']}control/{row['actual_environment_steps']}envsteps/{h['actual_physics_callbacks']}callbacks exact。ordinary{h['ordinary_episode_reset_events']}/integrity{h['integrity_task_reset_events']}/unknown{h['unknown_task_reset_events']}/nonfinite{h['nonfinite_observed']}/STOP{h['stop_reason']}；closure{h['max_closure_error_m']*1000:.9f}mm/mimic{h['max_mimic_error_rad']:.9f}rad。time_out/route及unique{h['actual_truncation_reset_events']}和两coverageexact以ownhealth为准，重叠termcounts不相加unique。正式target300s实际{seconds:.12f}s含load-learn-save-exit已原parent一次结清。两真实OS锁free/active-Sactive空/父guardian孩子实际自然退出/E1_SLOPE5_independent_saved_review_ready是合法审查边界，非故障或全课程finished，不复活旧main/resume/stage/native/SDK/PPO/once，不重结尾段。

新big4updates96control1.92Msteps384callbacks CPU102完整savePASSED/289.4996802806854s原父一次结清且discard；fresh同SLOPE独立20k新进程0control0PPO完整actorcriticoptimizerstd/allD0D7/globalnamed/privateCPUCUDA/terraincommand/savedsourceepisode+1实际通过，无PPO不扣。新geometry正式来源仍完整129 source3643c97，explicitG3toSLOPE/terrainexactfalse是明确迁移而非恢复失败/PhysXexactresume；之后sameSLOPE恢复要求exact，不套首transition字段。原402snapshot列表失败220.33718371391296s/small25.113439798355103s各原父一次结清，原SDK/native/small exactSHA复用，所有false/raw/cost/schema errors保持，无预算扩展/重复clock。

135四case已由该parent自动发布，complete/errorfree/fullJSONbyteexact/fullNPZ与完整审查尚待实际结果。积极用collect_slope_snapshot135_actual.py仅读实际完成结果、review_slope135_actual.py核134同derived5°2m镜像/9m格/approach.4/两轮全部坡段200mm后支撑/80env1500control15s/20260928white3精确初始化root30q/params/recipes/assignments/6000callbacks/groundcontactintegralCOMlinkhardware原容差，旧115/129三skillexact合同完整signedcircle沿横向/dedrift/左右4pi/直线误差与原strictfalse保持。stand26不要求跨坡，原1N接触与位置分列；有效ordinary前和未完成prefix保留，resetteleport不算进度。完整135决定前不更多PPO/升8度/qualifiedSLOPE/全E1/RM/MoE部署，complete后合理独立单轴或纠正，不无限hold/只队列/同课盲训；旧complete不重发。134冻结基线上下坡各27/27只是此范围，不代新候选验收。

canonical828000s230h/六扩展各一次/新增0，当前idle余{own['canonical']['remaining_seconds']:.12f}s只快照，未来active/accounted真实尾段优先，不复制/追加/clear/重tail/加时。中央scope与actual final/135引用已同步，master/approval/tracks/RM/canonical字节保持。新修复stage trial-20261011-e1-slope5-prelearn-snapshot-rejection-preserved-and-isolated-list-repaired commit570bb3cab72e728560fe40d92e9782ba22fe9374/tagobject988ec531d19249c450d6bfe10017e75fbf5920ab已actualremote main/tag/peeled核验。阶段后big/fresh/formal/135pending/ownCPU/artifactindices/sync/monitor/Gitreceipt仍ordinarysupplement，具体actualtracked/remote最终工具优先，不凭此提示假完成。所有后来135完整/新保存报告仍Git；大weights/rawNPZ/USD/ZIP仅actualpath-size-SHA，凭据不输出不Git。pushfailed只续原objects不重record/tag/commit。

004独立SLOPE ownership保持E0/Wave/CURB不改，gate未训/硬件未标定/S8后续具体批准/93-94paused；本地WASD播放器不自动GUI按键/reset/重启或停止。原DR/reward/LR/clock/plane30+20/20/15/15/actualclearplane条件命令、healthv3/fullsignedcircles tolerances/RM003002001全保持，无pure/teacher/S7/S8/70-20-10；min(18h,.13B)与其他expert/gate原规划保护无ledgerreserve。

mod4-10 ACTIVE每2h，健康pendingDONT_NOTIFY静默，只实质阶段/真实修复/重大退化/完成/需人类动作NOTIFY，不小时/5minSSH/ping/Rich/自动加时。单课reviewready不删monitor，只有预算真正结束且actualfinal全完成才停止。

以下旧404启动提示仅历史追溯，以上自己的formal final与之后135actual优先：
'''
p=D/'MONITOR_CURRENT_FORMAL_FINAL_PROMPT.md';assert not p.exists();p.write_text(head+'\n'+(D/'MONITOR_CURRENT_SNAPSHOT_REVIEWED_PROMPT.md').read_text(encoding='utf8'),encoding='utf8')
save('SNAPSHOT_FORMAL_FINAL_MONITOR_PREPARED.json',dict(epoch=time.time(),path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes()),old_prompt_preserved=True,actual_final_priority=True))
print(json.dumps(dict(path=str(p),bytes=p.stat().st_size)))
