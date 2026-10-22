from pathlib import Path
import hashlib,json,time,tomllib,traceback
S=Path(__file__).resolve().parent;W=S.parent;R=S/'reports';T=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021';B=T/'H1_STEP270_REWARD_PATH_V1_20261022';BR=B/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    result=read(R/'HOST72_APPROVED_EXACT_CLEANUP_ACTUAL_RETURNED.json');returned=read(R/'NEW_CLEANUP_ALL_FULL_TEXT_RECEIPTS_AND_ACTUAL_PROCESS_OUT_RETURNED_ACTUAL.json');approval=read(R/'HUMAN_EXPLICIT_BOTH_CLEANUP_ACTIONS_APPROVAL_ACTUAL.json')
    assert result['passed'] and returned['passed'] and returned['actual_cleanup_process_out']
    d=read(BR/'V112_HOST72_IMMUTABLE_DUPLICATE_ACTUAL_FULL_SHA_VERIFIED_REVIEWABLE_CANDIDATES.json');p=read(BR/'V112_OLD_COMPLETE_TRAINING_PREFIX_FIRST_LATEST2_EXPANSION_PROPOSAL_NOT_AUTHORIZED_CPU_ACTUAL.json')
    expected_copies={x['path'] for g in d['groups'] for x in g['copies']};expected_prune={x['path'] for s in p['stages'] for x in s['proposed_removed_unique_originals']}
    actual_copies={x['path'] for x in result['actions'] if x['kind']=='atomic_path_preserving_full_SHA_identical_hardlink_dedup'}
    actual_prune={x['path'] for x in result['actions'] if x['kind']=='explicitly_authorized_old_complete_window_middle_raw_preupdate_pruned_irrecoverable'}
    assert actual_copies==expected_copies and actual_prune==expected_prune and not actual_copies&actual_prune
    assert len(result['actions'])==len(actual_copies)+len(actual_prune)==1614
    for row in returned['files']:
        raw=Path(row['local_path']).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
    assert len(returned['files'])==1619
    summary=dict(epoch=time.time(),passed=True,exact_human_approval=approval,
       duplicate_replacements=len(actual_copies),old_complete_stages=15,irrecoverably_pruned_middle_files=len(actual_prune),
       retained_first_latest2_files=result['retained_old_first_latest2_files'],
       actual_freed_bytes=result['observed_free_delta'],free_before=result['filesystem_free_before'],free_after=result['filesystem_free_after'],
       actual_cleanup_process_out=True,full_remote_audit_reports_returned=1619,
       no_training_pause_hotpatch_new_GO_GPU_budget_or_peer_query=True,
       actual_audit_root=result['audit_root'],old_original_INDEX_snapshots_not_current_presence_claims=True,
       cleanup_candidate_NOT_AUTHORIZED_filenames_are_historical_and_superseded_by_explicit_approval_and_actual_receipts=True,
       all_other_unique_FINAL_sources_failed_models_native_evaluation_originals_error_full_logs_kept=True,
       no_new_reward_physics_or_PPO_change=True)
    put(R/'EXACT_ACTION_READBACK_AND_AUTHORIZED_SCOPE_CPU_VERIFIED_ACTUAL.json',summary)
    put(T/'reports/NEXT_ACTUAL_HUMAN_APPROVED_OLD72_CLEANUP256GB_RETURNED_V112_WORK_ORDER.json',summary)
    note=f'''The user explicitly approved both reviewed cleanup actions on host72, after asking whether any of the 526.4GB old task data was disposable.

164 immutable duplicate inputs were full-SHA verified and atomically replaced by same-volume hard links, retaining every path and byte. For exactly15 retired complete training windows, the user extended first+latest2 paired raw/preupdate retention to the reviewed old data:1450 middle files were deliberately pruned and cannot be recovered.90 first/latest paired files, every production FINAL, unique source, failed model, formal/native evaluation original, complete error/log/cost and all producer-history records remain. Prior original INDEX files remain historical; the immutable cleanup intent and1614 action receipts disclose the actual disposition.

Observed available-space increase: {result['observed_free_delta']}bytes (256.202GB). Host72 free space changed from{result['filesystem_free_before']} to{result['filesystem_free_after']}bytes (283.908GB), a snapshot rather than a future guarantee. All1619 new remote audit reports were returned byteexact and the cleanup process was confirmed out. No training signal, hotpatch, GPU job, peer identity query or budget write occurred. The active H1 boundary/reward training continues under its original owner; no skill result is claimed.

All pre-approval proposals, explicit reply, inventory, full-SHA checks, local reader path error, executable source, immutable intent/action receipts and verification are captured. This is one new human-approved storage repair stage, separate from the already recorded reward trial. It must be recorded only once; push recovery continues existing objects.
'''
    (S/'TRIAL_NOTE.md').write_text(note,encoding='utf8')
    old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))['prompt']
    a=old.index('人类明确答“可以暂时');z=old.index('当前H1新runid=',a)
    storage=f'''V112当前空间actual优先：人类新问“旧训练任务：526.4GB 一点能清理的都没有？”，明确答“两项都做，约256.21GB（推荐）”。这是具体15个旧窗保留范围扩展与164份无损去重的明确批准，已实际执行，不再pending/重复问。S={S.as_posix()}。先读S/reports/EXACT_ACTION_READBACK_AND_AUTHORIZED_SCOPE_CPU_VERIFIED_ACTUAL.json、HUMAN_EXPLICIT_BOTH_CLEANUP_ACTIONS_APPROVAL_ACTUAL.json、HOST72_APPROVED_EXACT_CLEANUP_ACTUAL_RETURNED.json及NEW_CLEANUP_ALL_FULL_TEXT_RECEIPTS_AND_ACTUAL_PROCESS_OUT_RETURNED_ACTUAL.json。
72新fresh执行后free{result['filesystem_free_after']}bytes（283.907653632GB），原free{result['filesystem_free_before']}，实际释放{result['observed_free_delta']}bytes约256.2GB；仅此时snapshot，未来仍fresh25GiB守卫。164份重复immutable input保留每条原路径和完整字节，用完整SHA核真后同盘硬链接无损去重，mode/owner/device核同，inode/mtime/nlink变化在逐项回执。15个原passedFINAL/NODEEXIT allout完整旧训练窗按新批准仅保留首+最近2完整pair，1450中途NPZ/preupdate实际移除、90保留配套文件核在。原来“新目录”授权不自动覆盖旧窗，本次明确扩展仅清单这15窗和164副本，不能扩删其他旧任务/forensic226GB/失败/native评测/FINAL/source/error/log。
已prune不可恢复。所有旧INDEX与早期NOT_AUTHORIZED候选文件是当时历史snapshot，不改旧true/false，也不再据旧INDEX all_retained=True称这些1450路径仍存在。实际路径处置以S/actual_remote_audit_texts/FULL_EXACT_INTENT_BEFORE_ANY_REPLACEMENT_OR_UNLINK.json与1614不可变ACTION回执及COMPLETE_ACTUAL.json为准。完整1619份JSON原字节SHA回执已拉回且独立CPU逐条集合exact，cleanup自己process actualout、helper/collector consume，不能重run这批、再删同路径或重hash旧raw。执行没有当前训练signal/kill/hotpatch/新GO/GPU/预算写/未知peer身份查询；H1仍原24actualGO/PPO，E3仍deferred，资源和成本以后依原closing fresh核，不冒本次查询了新训练状态。
人类500GB问题已实际回答：72指定root是原双4090 /home/lc01/Zonglin Li/zonglin2，同盘不同目录不提供新容量；本次实际cleanup已解除旧0.8GiB余量边界，不再重复请求新路径。除这15旧窗的新明确范围，其余历史原件继续保留，未来first+latest2仍原持续授权。当前训练和未来25source/schema/reward/runtime/账与closing规则如下不变。
'''
    old=old[:a]+storage+old[z:]
    start=old.index('Git同reward唯一trial');end=old.index('same mod4-10',start)
    old=old[:start]+'''Git：原reward trial0fdb24bd67cbb0442c706de643aa7cc3b15cb989/trial-20261022-h1-step270-forward-clearance-reward-v1仍consume不重record。新的明确人类授权旧存储repair单独唯一record_experiment id=host72-approved-closed-task-retention-cleanup-v112，tag=trial-20261022-host72-approved-closed-task-retention-cleanup-v112；原1422 tagobjects/peels全部不动，新增仅此cleanup标签。所有本次只读盘点、初候选、不可恢复范围披露、明确批准、source、local missing-path错误、1619原审计JSON、真实退出/空间/验证/monitor回执全档。helper/record一旦执行就consume，若push失败只续已有objects不重record/helper/tag。最终Git actual工具回执/仓库优先，不为归档连接训练host/重PT/rawhash/GPU/改账。postGit不无限追HEAD。
'''+old[end:]
    prefix='V112_HUMAN_APPROVED_STORAGE_ACTUAL latest覆盖V111“72余量仅0.8GiB/等待新路径”预期，当前训练调度仍按V111 H1-only24及unused25；本次没有查询或改变训练。\n'
    put(R/'SAME_MONITOR_V112_CLEANUP_ACTUAL_UPDATE_ARGS.json',dict(mode='update',id='mod4-10',kind='heartbeat',name='MOD4计划与双机并行巡检',status='ACTIVE',rrule='FREQ=HOURLY;INTERVAL=1',targetThreadId='01a07a2d-9036-7531-a012-692df9f56353',prompt=prefix+old))
    print(json.dumps(dict(scope_verified=True,actual_freed_bytes=result['observed_free_delta'],free_after=result['filesystem_free_after'],full_audit_reports=1619,monitor_args_prepared=True)))
except BaseException:
    put(R/('CLEANUP_HANDOFF_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc()));raise
