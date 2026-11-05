# E0 MOD4v2：完整迁移20更新已执行，原scope出现mimic健康失败，候选不晋升

## 已实际完成

- 仅E0 / GPU0 / N20000 / T24 / 原PPO20更新，17Adam各+400（641600→642000），9,600,000优化transitions；原saved iter32023不伪改为32024。
- 全actor/critic/learnedSTD/normalizer/Adam/LR严格继承；旧v1物理/DR/history/queue/RNG只作CPU历史，新v2唯一fresh reset。source一次physical/hash/CPUdecode。原生全20k限位、gas、同一次zero=8physics2feedback、闭链准入通过。
- 新完整candidate `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SINGLE_ADMISSION3_FULL_LEARNER_MIGRATION_20261106_001831_1793895511281001300/roles/E0/production/model_mod4v2_migration_complete_U020.pt`，104429847 bytes / SHA `0fdc67c977e10fb1f7c645d12c9881ceff6d4cbcd97a63e6d2e9cee6155fe57c`。
- 原SDKclose/actual child+outer wait/原账结清/租约释放、冻结评测真实wait/intent/error检查及GPUsettle全通过；这些是执行资格，不是技能。

## 独立原E0 N80 fullDR结果

固定80env /1000controls=20秒 /seed20260928/8000physics/2000feedback，原sole reset/mean+norm/clip6/35-38-6，无optimizer或source20k历史应用。

|指标|实际值|
|---|---:|
|发生物理终止环境|80/80|
|mimic终止事件|8000|
|最大mimic误差|2.809122801 rad（原门限0.01）|
|最大闭链误差|0.001862019 m（原门限0.01）|
|body vx MAE|0.465815108 m/s|
|body vy MAE|0.166722004 m/s|
|yaw MAE|1.801129318 rad/s|
|max raw / applied action|582.992676 / 6.0|

本次mimic健康前提未保持。原完整binary/profile grader缺失仍null；不是从null推出失败，而是已存在0.01rad健康门明确触发。执行合格不等于技能合格。保留完整候选/正式6cd源，不覆盖旧母版/Registry；新registry仅候选区，没有已批准专家。不同D0、单seed不足以把原因归给训练/新表示/某个控制参数，当前尚未定位传动真实失效、SDK缓存/判据语义或策略因素。

## 后续窗口按用户改为一小时，但先处理反复重置

本20更新是首次迁移短测，不作充分训练或毕业。用户明确要求N20000约一小时后评测：后续不以20次硬停，仍原save3600/总3900/headroom300/原singlewriter预算与GPU0资源门，有效PPO时间/更新/样本量与启动/保存/关闭分报。当前先做最小原生传动/状态读数诊断，既不放宽mimic门限也不在反复约0.2秒reset上盲续训；其他8不自动启动。诊断计划还未执行，不把文本计划当新GPU活动。

## 证据与边界

[实际训练truth](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_SINGLE_A3_CLOSED_TRAINING_TRUTH.json>) / [实际冻结评测闭合](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/reports/E0_SINGLE_FROZEN_20261106_004725_1793897245545996100/CLOSED_RESULT.json>) / [独立V2候选registry](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/MOD4V2_EXPERT_MIGRATION_REGISTRY_V1.json>)。

串行新政策、此前资源/预main/原queue环境缺失和静态preparer失败、真实Native全20迁移/本次不良评测、完整报告待一次meaningful feature-only唯一annotated Git+远端核验；main只读，不为Git读weights/raw/大USDmesh或重放旧once/物理，不造验证链。Goal664 rev3 active，质量未完成。
