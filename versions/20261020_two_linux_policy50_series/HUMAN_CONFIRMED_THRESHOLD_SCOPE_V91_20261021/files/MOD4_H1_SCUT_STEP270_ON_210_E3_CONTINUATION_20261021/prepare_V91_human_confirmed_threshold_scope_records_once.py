from pathlib import Path
import datetime, hashlib, json, time, tomllib

T = Path(__file__).resolve().parent
W = T.parent
R = T / 'reports'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def put(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def main():
    report_path = R / 'V91_HUMAN_CONFIRMED_THRESHOLD_SCOPE_AND_REUSE_ACTUAL.json'
    assert not report_path.exists()
    histories = [
        Path('C:/Users/lulu/.codex/sessions/2026/09/07/rollout-2026-09-07T12-43-21-01a07a2d-9036-7531-a012-692df9f56353.jsonl'),
        Path('C:/Users/lulu/.codex/sessions/2026/10/15/rollout-2026-10-15T21-33-55-01a07a2d-9036-7531-a012-692df9f56353_01a13fc4-f5ba-7c52-8bb5-301275e18a75.jsonl'),
    ]
    wanted = (
        '按照2.5ms 求解器最优解直接加入主训练开始测试，用4090.磨刀不误砍柴工',
        '短暂暂时的2.5ms超过2mm闭链门槛是可以接受的，通过华南虎的实验我们不是能看出来吗?为什么油降低到1ms了，还有切换时如果有记录别再搞什么45分钟实验了简直浪费时间。',
        '1微米门槛是不是太严了？你查一下历史对话因该有我们设置的最优门槛来着',
        '以后按照这个继续',
    )
    found = {}
    for path in histories:
        for n, line in enumerate(path.open(encoding='utf8'), 1):
            d = json.loads(line)
            p = d.get('payload', {})
            if d.get('type') != 'response_item' or p.get('role') != 'user':
                continue
            text = '\n'.join(x.get('text', '') for x in p.get('content', []) if isinstance(x, dict))
            if text.strip() in wanted:
                found[text.strip()] = dict(path=str(path), line=n, timestamp=d.get('timestamp'), human_text=text, human_text_UTF8_SHA=sha(text.encode('utf8')))
    assert set(found) == set(wanted), sorted(set(wanted) - set(found))
    refs = [
        W / 'MOD4_DT2500_SOLVER_REPAIR_20261007/reports/SELECTION.json',
        W / 'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/reports/AUTHORIZATION.json',
        W / 'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/ORIGINAL_TRAINING_PARAMETERS_HISTORY_RECONCILIATION_20261018.md',
        W / 'MOD4_E1_G1_ACTUAL_REVIEW_20261010/frozen_fullroute_v4.py',
        R / 'STEP270_V7_ACTUAL_FLOAT3_REJECTION_AND_RAY_EQUATION_CPU_ACTUAL.json',
        R / 'STEP270_FULL20K_V9_ALL160K_COOKED_METRIC_GEOMETRY_CPU_V2_ACTUAL.json',
        R / 'STEP270_PRODUCTION_V1_UNINSTALLED_SOURCE_AST_AND_STORAGE_CPU_ACTUAL.json',
        R / 'NEXT_ACTUAL_H1_QUERY160K_CPU_PASSED_PRODUCTION_CANDIDATE_E3_BRIDGE5_LEARNING_V90_WORK_ORDER.json',
        W / 'polar-rl-train/docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md',
    ]
    proof = json.loads(refs[5].read_bytes())
    assert proof['passed_independent_all160k_metric_geometry_CPU']
    assert proof['actual_GPU_complete_all_ownout_and_private_lease_released']
    assert proof['independent_point_triangle_distance_max_m'] < 1e-6
    report = dict(
        epoch=time.time(), kind='human_confirmed_scope_correction_and_existing_evidence_reuse',
        human_original_messages=[found[x] for x in wanted],
        scope_limited_to_two_current_chat_rollouts_not_all_conversations=True,
        history_not_archived_wholesale_or_credentials_read=False,
        physics_dt_s=.0025, solver_position_velocity=[32, 4],
        H1_policy_Hz=100, existing_E3_policy_Hz_50_not_reverted=True,
        closure_per_environment_reset_m=.002,
        single_closure_peak_not_global_abort_or_automatic_1ms_fallback=True,
        query_1um_is_specific_numerical_audit_not_universal_physical_or_graduation_limit=True,
        raw_actor_mean_existing_reference_abs_tolerance=1e-4,
        no_new_FP64_bitwise_or_extra_barycentric_admission_barrier=True,
        existing_query160k_and_native3_reused_without_GPU_repetition=True,
        H1_step270_success_contract_unchanged=True,
        nonfinite_integrity_unknown_hardware_fullsave_and_original_account_guards_retained=True,
        no_training_host_transport_GPU_or_canonical_write_this_scope_record=True,
        source_references=[dict(path=str(p), bytes=p.stat().st_size, SHA=sha(p.read_bytes())) for p in refs],
        source_policy_markdown=str(refs[-1]),
        current_H1_production_admission_still_pending=True,
    )
    # Only the four selected human messages are retained; no full chat or secret-bearing history is captured.
    report['history_not_archived_wholesale_or_credentials_read'] = True
    put(report_path, report)
    workorder = dict(
        epoch=time.time(), V91_human_scope_confirmation_overrides_ambiguous_V90_physical_1um_wording=True,
        approved_scope_report=str(report_path), policy=str(refs[-1]),
        existing_actual_state_workorder=str(refs[7]),
        no_new_GPU_or_H1_GO_or_skill_result_from_this_confirmation=True,
        H1_reuse_completed_native3_fullstate_and_V9_all160k_query_CPU=True,
        next_actual_work='Complete existing production worker/controller source SDK/RSL/PPO CPU and admission binding. After current E3 bridge5 actual complete save/CPU/cost/allout, use a new unused original-writer H1+recovery root only if H1 qualified. Do not repeat passed query/native or add unrelated audit gates.',
        E3_bridge5_closing_collector=str(T / 'E3_bridge_continuation_V5/collect_actual_recovery_bridge_final_original_cost_bounded_once.py'),
        E3_bridge5_closing_reviewer=str(T / 'E3_bridge_continuation_V5/review_actual_recovery_bridge_complete_model_original_cost_CPU_once.py'),
        E3_old_owner_creation_and_schedule_are_historical_only=True,
        all_old_false_original_errors_and_scope_fields_preserved=True,
        current_stage_ordinary_append_no_new_record_or_tag=True,
    )
    order_path = R / 'NEXT_ACTUAL_HUMAN_CONFIRMED_THRESHOLD_SCOPE_AND_H1_E3_CONTINUATION_V91_WORK_ORDER.json'
    put(order_path, workorder)
    automation_path = Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
    old = tomllib.loads(automation_path.read_text(encoding='utf8'))
    assert old['id'] == 'mod4-10' and old['status'] == 'ACTIVE'
    assert old['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
    prompt = old['prompt']
    prompt = prompt.replace('原物理米单位point-to实际authored triangle距离<=1um', '特定几何数值审计point-to实际authored triangle距离<=1um')
    prompt = prompt.replace('降低物理1um', '修改查询数值容差1um')
    prompt = prompt.replace('原query1um/COM10um/closure2mm/mimic.01', '分项query数值核验1um/COM数值核验10um/单环境closure2mm/mimic.01')
    prefix = (
        'V91人类明确确认优先：人类在查历史后答“以后按照这个继续”。先读T/reports/NEXT_ACTUAL_HUMAN_CONFIRMED_THRESHOLD_SCOPE_AND_H1_E3_CONTINUATION_V91_WORK_ORDER.json及V91_HUMAN_CONFIRMED_THRESHOLD_SCOPE_AND_REUSE_ACTUAL.json；长期规则在polar-rl-train/docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md和两处AGENTS.md。'
        '已选是2.5ms/TGS32/4，H1保持100Hz×4，E3现有明确50Hz×8不倒退。2mm是单环境closure重置，单峰不整批停训/自动1ms回退。1um仅特定查询数值核验，不是统一物理健康/安全/毕业线；原physical_threshold_m字段名仅保留历史。不得以低于Float3世界坐标ULP的机械比较拒绝真实几何，不新增FP64/逐位相等/额外barycentric等关卡。'
        '复用已完整通过native3整态及V9全部16万真实query/CPU，不重GPU/native/raw下载hash；原world434失败和所有错误保留。H1生产候选仍待原必要完整源码SDK/RSL/PPO CPU及绑定，不因确认虚构准入或270成功。原nonfinite/integrity/unknown/mimic/hardware/完整savedstop和唯一原writer费用保护不变，原270mm双轮越缘顶面接触及.5s稳定目标不变。'
        '本补充没有新H1GO、GPU、余额增加或新实际训练结果；下面V90仍是最新实际运行证据，只澄清其门槛称谓和范围。以后同阶段只ordinary追加，postGit回执仅一次补档，不重record/tag/helper或无限追HEAD。\n'
    )
    args = dict(mode='update', id=old['id'], kind=old['kind'], name=old['name'], status=old['status'], rrule=old['rrule'], targetThreadId=old['target_thread_id'], prompt=prefix + prompt)
    if 'notification_policy' in old:
        args['notificationPolicy'] = old['notification_policy']
    put(R / 'V91_EXISTING_MONITOR_UPDATE_ARGS.json', args)
    print(json.dumps(dict(scope_report=str(report_path), workorder=str(order_path), selected_human_messages=len(found), current_actual_state_unchanged=True, prepared_existing_monitor_update_only=True), ensure_ascii=False))

if __name__ == '__main__':
    main()
