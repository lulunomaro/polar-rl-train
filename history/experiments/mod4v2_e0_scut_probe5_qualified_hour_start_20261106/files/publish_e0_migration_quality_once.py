"""Read only actual closed training/evaluation metadata; retain candidate, do not approve skill."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent;jp=D/'E0_MOD4V2_CLOSED20_QUALITY_V1.json';mp=D/'E0_MOD4V2_CLOSED20_QUALITY_V1.md';rp=D/'MOD4V2_EXPERT_MIGRATION_REGISTRY_V1.json';assert not any(x.exists()for x in(jp,mp,rp))
t=json.loads((D/'E0_SINGLE_A3_CLOSED_TRAINING_TRUTH.json').read_bytes());evpath=Path(json.loads((D/'E0_SINGLE_FROZEN_CLOSED_RESULT_PATH.json').read_bytes())['path']);ev=json.loads(evpath.read_bytes());m=ev['normal_metrics'];pm=ev['metadata'];f=ev['cases']['E0']['V2_FROZEN_EVAL_FINAL.json'];assert ev['closed']is ev['execution_qualified']is True and m['controls']==1000 and m['physics_callbacks']==8000 and m['feedback_samples']==2000 and ev['skill_grader']is ev['full_skill_graduation']is None
assert f['role']=='E0'and f['optimizer_updates']==0 and f['source_cache']
rows=pm['TERMINAL_ROWS.json'];assert len(rows)==1 and rows[0]['actual_waited']is True and rows[0]['semantic_qualification']['qualified']is True and all(rows[0]['semantic_qualification']['checks'].values())
health_ok=m['unique_envs_terminated']==0 and m['max_current_mimic_rad']<=.01 and m['max_current_closure_m']<=.01
choice='RETAIN_E0_CANDIDATE_PENDING_DEFINED_SKILL_CONFIRMATION_KEEP_OLD_REGISTRY'if health_ok else 'KEEP_FORMAL_E0_SOURCE_NO_V2_PROMOTION_MIMIC_HEALTH_FAILED'
r=dict(kind='MOD4V2_E0_ACTUAL_CLOSED_MIGRATION_AND_ORIGINAL_SCOPE_QUALITY_V1',training=t,evaluation=dict(closed_path=str(evpath),root=ev['root'],actual_closed_execution_qualified=True,normal_metrics=m,actual_parent_wait_and_semantic=rows,actual_parent_exit=pm['PARENT_EXIT_SCOPE.json'],actual_outer_wait=pm['OUTER_OWNER_WAIT_ACTUAL.json']),original_health_prerequisites_retained=health_ok,full_binary_profile_grader=None,full_skill_graduation=None,decision=choice,candidate_preserved=t['latest_complete_save'],old_source_and_Registry_unchanged=True,other_eight_currently_scheduled=False,no_causal_attribution_from_single_cross_D0_cohort=True,goal_complete=False,model_raw_GPU_SDK_C_operations_by_publisher=0)
jp.write_text(json.dumps(r,indent=2,allow_nan=False),encoding='utf8')
selection=json.loads((D/'SOURCE_NINE_PLAN_V1.json').read_bytes());registry=dict(kind='MOD4V2_SEPARATE_MIGRATION_CANDIDATE_REGISTRY_NOT_APPROVED_EXPERTS',approved_experts={},candidates={'E0':dict(status='EXECUTION_PASSED_RETENTION_REJECTED_MIMIC_HEALTH'if not health_ok else'PENDING_DEFINED_GRADER',checkpoint=t['latest_complete_save'],actual_iteration=t['actual_live_core']['iteration'],actual_Adam17_steps=t['actual_live_core']['Adam17_steps'],actual_LRs=t['actual_live_core']['optimizer_LRs'],original_scope_execution_qualified=True,original_health_prerequisites_retained=health_ok,full_skill_graduation=None,quality_report=str(jp))},other_experts_status='NOT_SCHEDULED_IN_CURRENT_HUMAN_SERIAL_E0_SCOPE',source_plan=str(D/'SOURCE_NINE_PLAN_V1.json'),source_mothers_unchanged=True,old_Registry_v12_unchanged=True,no_automatic_approval=True,goal_complete=False);rp.write_text(json.dumps(registry,indent=2,allow_nan=False),encoding='utf8')
mae=m['body_velocity_MAE'];mp.write_text(f'''# E0 MOD4v2：完整迁移20更新已执行，原scope出现mimic健康失败，候选不晋升

## 已实际完成

- 仅E0 / GPU0 / N20000 / T24 / 原PPO20更新，17Adam各+400（641600→642000），9,600,000优化transitions；原saved iter32023不伪改为32024。
- 全actor/critic/learnedSTD/normalizer/Adam/LR严格继承；旧v1物理/DR/history/queue/RNG只作CPU历史，新v2唯一fresh reset。source一次physical/hash/CPUdecode。原生全20k限位、gas、同一次zero=8physics2feedback、闭链准入通过。
- 新完整candidate `{t['latest_complete_save']['path']}`，{t['latest_complete_save']['bytes']} bytes / SHA `{t['latest_complete_save']['sha256']}`。
- 原SDKclose/actual child+outer wait/原账结清/租约释放、冻结评测真实wait/intent/error检查及GPUsettle全通过；这些是执行资格，不是技能。

## 独立原E0 N80 fullDR结果

固定80env /1000controls=20秒 /seed20260928/8000physics/2000feedback，原sole reset/mean+norm/clip6/35-38-6，无optimizer或source20k历史应用。

|指标|实际值|
|---|---:|
|发生物理终止环境|{m['unique_envs_terminated']}/80|
|mimic终止事件|{m['termination_events_by_reason']['mimic']}|
|最大mimic误差|{m['max_current_mimic_rad']:.9f} rad（原门限0.01）|
|最大闭链误差|{m['max_current_closure_m']:.9f} m（原门限0.01）|
|body vx MAE|{mae['body_vx_m_s']:.9f} m/s|
|body vy MAE|{mae['body_vy_m_s']:.9f} m/s|
|yaw MAE|{mae['yaw_rate_rad_s']:.9f} rad/s|
|max raw / applied action|{m['max_raw_action_abs']:.6f} / {m['max_applied_action_abs']:.1f}|

本次mimic健康前提未保持。原完整binary/profile grader缺失仍null；不是从null推出失败，而是已存在0.01rad健康门明确触发。执行合格不等于技能合格。保留完整候选/正式6cd源，不覆盖旧母版/Registry；新registry仅候选区，没有已批准专家。不同D0、单seed不足以把原因归给训练/新表示/某个控制参数，当前尚未定位传动真实失效、SDK缓存/判据语义或策略因素。

## 后续窗口按用户改为一小时，但先处理反复重置

本20更新是首次迁移短测，不作充分训练或毕业。用户明确要求N20000约一小时后评测：后续不以20次硬停，仍原save3600/总3900/headroom300/原singlewriter预算与GPU0资源门，有效PPO时间/更新/样本量与启动/保存/关闭分报。当前先做最小原生传动/状态读数诊断，既不放宽mimic门限也不在反复约0.2秒reset上盲续训；其他8不自动启动。诊断计划还未执行，不把文本计划当新GPU活动。

## 证据与边界

[实际训练truth](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_SINGLE_A3_CLOSED_TRAINING_TRUTH.json>) / [实际冻结评测闭合](<{str(evpath).replace(chr(92),'/')}>) / [独立V2候选registry](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/MOD4V2_EXPERT_MIGRATION_REGISTRY_V1.json>)。

串行新政策、此前资源/预main/原queue环境缺失和静态preparer失败、真实Native全20迁移/本次不良评测、完整报告待一次meaningful feature-only唯一annotated Git+远端核验；main只读，不为Git读weights/raw/大USDmesh或重放旧once/物理，不造验证链。Goal664 rev3 active，质量未完成。
''',encoding='utf8');print(json.dumps(dict(quality=str(jp),report=str(mp),registry=str(rp),decision=choice,execution_qualified=True,health_prerequisite=health_ok,full_skill_graduation=None,goal_complete=False),indent=2))
