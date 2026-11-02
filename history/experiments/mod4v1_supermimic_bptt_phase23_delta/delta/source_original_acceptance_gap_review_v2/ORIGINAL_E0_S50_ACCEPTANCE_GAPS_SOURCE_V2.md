# 原 E0 / SLOPE_INDEPENDENT50 接受谓词缺口复核 V2

## 结论

**本次有界 source/text 集合仍未接上这两角色的“原完整技能二元接受谓词 + 原成功分母”。两角色的谓词、二元成功率继续为 `null`；S50 原接受 cohort 也继续为 `null`。** 这不是新策略失败判定，也不是“历史上绝不存在原合同”的全局声明。本件不改原训练、评测或旧接受合同，native=0。

本次新增的关键证据是：**S50 的 `independent_expert_task_contract` 已经通过发布的纯 CPU 文本、原任务文本和原保存语句精确接通；字段名里的 contract 并不是缺失的技能 grader。** 另一个需保留的细节：E0 文件树确有旧 SCUT/平地/固定自旋数值资格器，故“完全没见过任何数值 pass 代码”也不准确；它们未接成当前 E0 原全 profile 的接受口径。

机器可复核结论见 [结构化证据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_original_acceptance_gap_review_v2/ACCEPTANCE_AUTHORITY_FINDINGS_V2.json>)；33 个明确文本输入的完整路径、行段、bytes、SHA256 见 [输入索引](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_original_acceptance_gap_review_v2/AUDIT_INPUTS_SHA256_V2.json>)。

| 角色 | 原完整 atomic predicate | 原 binary denominator / cohort | 原站立接受分组规则 | 原成功判定时机 | 本次技能率 |
|---|---|---|---|---|---|
| E0 | `null` | `null`；已有 exposure/采样单位并非成功分母 | 有原 standing 标签，接受阈值/汇总规则未接上 | 原采样窗口可定位；完整技能接受时机未接上 | `null` |
| SLOPE_INDEPENDENT50 | `null` | `null` | 自有自然指令存在；原接受 cohort/站立处理未接上 | 原 boundary/timeout 是终止事件，不是成功判定时机 | `null` |

这与旧合同 [E0:105–156](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json#L105-L156>)、[S50:527–582](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json#L527-L582>)一致。90% 是后加的外层目标，单独的百分数并未补出原 numerator / denominator。

## E0：有诊断原口径，也有较窄资格器，但缺全角色接受规则

1. [原保存文本复核:22–35](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/E0_REVIEW_MD__HANDOFF_FROZEN_E0V2_FULL1000_SAVED_TEXT_REVIEW.md#L22-L35>)明确原数值技能通过容差、逐 command 成功阈值未保存。12,918 个 accepted signed-2π 是**采样窗口事件**；约 68.333% 是 moving exposure，不是原技能通过率。20,000 个 reset-ended 已行动 command 仍是 incomplete；20,000 个 zero-control 行没有正面技能证据。自然 straight-zero 零曝光是 pending，不应补成成功或失败。
2. [原分类器:1–20](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/E0_CATALOG__e0_original_profile_catalog_v1.py#L1-L20>)区分 standing、signed straight、signed pure、signed transition、signed moving-world；transition 有原 12s phase bins。它是分类器，不是每组成功阈值。standing 和 straight-zero 也不是随意合并的同一接受组。
3. [原 telemetry:41–93](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/E0_METRICS__e0_long_command_domain_telemetry_v1.py#L41-L93>)按 episode/command/profile/phase 和 signed-turn 维护 live 采样，MAE 的分母是 `population_controls`；[finish:199–206](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/E0_METRICS__e0_long_command_domain_telemetry_v1.py#L199-L206>)保留 `skill_graduation=False`，未声称 transition 完整同 command 12s graduation。[保存 metadata:2854–2858](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/E0_SAVED20S__E0_V2_FULL1000_EARLY_COMMAND_INSTANCE_SAVED_TEXT_ACCEPTANCE_REVIEW_ACTUAL.json#L2854-L2858>)也明确阈值/逐 command world-success 缺口。
4. [旧 FORMALS:125–130](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/FORMALS189__EXPERT189_SAVED_FORMALS_AND_SKILL_GAPS_ACTUAL.json#L125-L130>)真实保存了世界系 along/cross `max(0.03,0.1V)`、signed-yaw `0.2rad/s`、同 command 完整 signed cycle 的旧标准。它是应保留的**局部标准证据**，却未给出 E0 standing/straight/transition/moving 全域 atomic rule、完整 command cohort 和整体毕业汇总。该文件的 formal-format pass 与 full-skill accepted 本来就分开。
5. 真实较窄数值器如下，均未当作 E0 全角色接受规则：
   - [SCUT v3:35–47](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/scut_style_gate_v3.py#L35-L47>)在继承物理/证据约束下按各旧 probe 组 `fraction >= .8` 资格确认，scope 明写 “SCUT-inspired project qualification, not an exact task port”。
   - [SCUT v2 flat:14–60](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/scut_style_gate_v2.py#L14-L60>)是旧 deterministic 15s、指定速度/physical-admission 组规则，不是当前 E0 自然 command/UID 分母。
   - [curriculum v4:129–138](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/scut_curriculum_gate_v4.py#L129-L138>)是两个固定 signed spin target、每方向至少 80% 的 yaw-rate 在 ±0.2 内，外加 physical `assess`。源码也明说独立 factual target confirmation、非中间 curriculum 挡板；没有补出 E0 moving-world/standing/transition 完整接受。
   - [world cycle metrics:1–47](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/world_cycle_metrics.py#L1-L47>)仅返回 whole-prefix/完整转圈 progress/cross 统计；[world probe:196–228](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/world_spin_probe.py#L196-L228>)明说净进度与 learning admission 分开，旧数值 Boolean diagnostic。未执行这些 probe。
6. [posttrain E0 选择器:26–35](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/assess_pair1_retention_closed_metadata_v1.py#L26-L35>)的 body MAE 三项不变差 + ordinary failure 不增是选本规则，不是原技能毕业。

## S50：原 task_contract 字段的歧义已解除

完整文本接链（未打开、stat 或 hash 任何 PT）：

- [发布的 CPU schema:247–272](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_three_variants_CPU_actual_v1/SLOPE_INDEPENDENT50_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json#L247-L272>)已逐字段发布 `known_variant_extra_schema.task_contract`。
- [原任务文本:1–17](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E1_SLOPE_INDEPENDENT50_40050_MOD4V1_SOURCE_V2/original_exact/TASK.json#L1-L17>)与上述 dict **严格相等**，15 项 CPU/text 测试之一复核此等式。
- [原 producer:35–37](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E1_SLOPE_INDEPENDENT50_40050_MOD4V1_SOURCE_V2/original_exact/producer/expert_independent_worker_v1.py#L35-L37>)直接执行 `v['independent_expert_task_contract']=task`。这是 learning/deployment TASK：kind、原 source、entry、native controls、20k env、parent/headroom、保留 STD/optimizer、axis 文字；没有 accepted Boolean 或 success denominator。
- [extra-state runtime:43–55](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/runtime/isaac/mod4/variant_extra_state_runtime_v2.py#L43-L55>)检查 contract dict 的 `kind=='SLOPE5'` 并保留 whole extras，也不是 grader。

[own canonical metadata:113–117](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/E1_CANONICAL_SOURCE_METADATA.json#L113-L117>)的 full-ramp-and-both-supports 是自有范围，extra root key 名不是原接受条件。[own axis:16–27](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/runtime/isaac/mod4/independent_expert_axis_v1.py#L16-L27>)把 family4 原 tile boundary `abs(dx)>3.5 or abs(dy)>3` 设为 timeout；没有有序跨越/接触/velocity 成功规则。

[原 ROLE_CONTRACTS:998–1011](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json#L998-L1011>)明确 `DEFAULT_TRAINING_AXIS_DESCRIPTIVE_SCREEN_NO_ORIGINAL_ACCEPTED_COHORT`。[原 S50 assessor:101–114](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_assess_pair4_v4/assess_pair4_retention_closed_metadata_v4.py#L101-L114>)保留 accepted-rule missing，不把 ordinary=0 说成技能通过。

[legacy join:614–663](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/E1_SLOPE5_SOURCE_JOIN_v1.json#L614-L663>)和 [coverage plan:200–229](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/coverage_plans/CURB_SLOPE_50HZ400N_SOURCE_COVERAGE_PLAN_v1.json#L200-L229>)连接了后续 S50 自有 scope，却没有把 S135 27/27 或更早 24b 域接受规则自动移植过来。[保存 final:78](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/SLOPE50_FINAL__FIRST_CURB_SLOPE_FINAL_MODELS_AND_EXACT_DISTINCT_INTERVAL_COST_CPU_ACTUAL.json#L78>)也明确没有从 learning 推断 frozen skill pass。

## 来源 SHA 与覆盖边界

关键文本 SHA256（其余 29 个完整 SHA 在输入索引）：

| 证据 ID | bytes | SHA256 |
|---|---:|---|
| `formals189` | 11878 | `9dc7afcd5afb0581d39f85efa2004048d0b782df7bf4496581d239cda013e351` |
| `s50_cpu_published` | 13008 | `eee6c725265ccb3f1e04bd23329a9791adf19a38e6499affc407a8b80fcb75d5` |
| `s50_original_task` | 777 | `1e702c72ce2e00853001f0d22396c7127f85507ac2b5683bc451a5141271b14a` |
| `s50_original_producer` | 7679 | `ff03f2efcc46a218324e7f068387ad005060a3de5e576b2eb11885d899f0e29c` |

- 实际读取/哈希 **33 个明确 allowlisted `.md/.json/.py` 文本**，最大单件 115,717B；不是 raw events。旧文件逐项 hash 复核，无改写。
- 初始 T 内 acceptance/contract/grader 名字发现返回 402 个路径，输出只展示前 100；并未宣称 402 个内容全读，H1/无关项不跟。没有打开工具落在范围外的 spill 文件。
- 后续收敛到原 accepted-contract reference-text、S50 exact TASK/producer、legacy join/coverage、原 role contracts、旧 posttrain 选择器、R 的现存合同/measurement gap 与 E0/S50 own metadata/entry/明确 source。T 的 `skill_contracts` 列出的只有 E3；`source_views` 列出的 8 个 redacted transport/launcher 文件不作接受权威。
- `**/*{MASTER_PLAN,master_plan,skill_grader,SKILL_GRADER,grader,GRADER}*.{md,json,py}` 在 T 内名字发现为 0，**不是全历史不存在证明**。[FORMALS 引用:143–145](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/FORMALS189__EXPERT189_SAVED_FORMALS_AND_SKILL_GAPS_ACTUAL.json#L143-L145>)中的 `MOD4_MOE_MASTER_PLAN.md` 只接到 C-task 路径，保存 bytes=47599 / SHA=`812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b`；本 scope 未访问 C，也未伪装为读过这份计划。
- `T ./*.md` 曾返回 0 而已知 root 文本存在，这是 glob 语义限制，不作不存在证据。最终只对明确路径作结论。不存在新远程穷举/资源调用。

## 独立纯标量反例与后续最小缺件

[测试脚本](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_original_acceptance_gap_review_v2/test_scalar_nonidentifiability_v2.py>)与 [CPU 结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_original_acceptance_gap_review_v2/CPU_TEST_RESULTS_V2.json>)：**15/15 PASS，0 failure / 0 error，0.008s，stdlib-only**。包括同 MAE 不同分布、standing 混入掩盖 moving、同零摔倒/同完整时间不同位移、同 boundary 事件不同经过路线、跨 reset 拼接伪造有序 span、完整 signed-turn 不等于 projected progress，以及原 null、TASK 精确接链和原 producer AST 保存语句检查。测试中的假想 `.05`/`±1.2` 仅用于非可辨识性反例，绝不是 E0/S50 新阈值。测试没有执行原模块、创建二元 grader 或输出真实技能率。

后续若继续接权威，最小缺件为：带原自有 role/profile/geometry/reference scope 的原合同正文或精确冻结 grader；其中应包含原 atomic predicate/容差、完整 denominator/cohort、standing/moving 处理、ordered/contact/phase 条件、fail/reset/censor 及判定时机。当前诊断、geometry、任务预算、原环境成功启动、母本选优和新90%目标都不替代这些字段。此源审计不挡父代理既定独立实际工作，也不改变训练/评测准入。

全部产物仅写本新目录。PT open/stat/hash、NPZ/JSONL/raw、SSH、SDK/Torch/GPU/native、C-task 读取、account/locks/Git、旧 source/合同写入均为 0。
