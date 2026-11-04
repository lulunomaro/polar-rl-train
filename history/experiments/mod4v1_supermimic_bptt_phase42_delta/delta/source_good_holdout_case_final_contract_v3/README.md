# Case-FINAL finite contract V3 — SOURCE only

状态：NEW SOURCE，`enabled=False`、`staged=False`、`dispatched=False`；真实 native binding 为 `UNKNOWN`。本组件修正独立 holdout 的完整 case-FINAL 读取上限，不含训练、实际评测或历史结果重定性。

## 精确最小变化

基线为 D6 [完整 runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py>)，56370 bytes / SHA256 `7455449db33ef539a7d8517876a36a4c291d57ebaa1c361943af2343b2370ee2`。

NEW [完整 runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/good_expert_holdout_runtime_v1.py>)，56467 bytes / SHA256 `29d29e96899575b0e1e1a805d210a04aba7cb0e50376959ff91779c13927b911`，仅：

1. [第19行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/good_expert_holdout_runtime_v1.py#L19>) 增加 `CASE_FINAL_MAX = 2097152`。
2. [close 第623行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/good_expert_holdout_runtime_v1.py#L623>) 的原 `_metadata` case-FINAL 调用增加 `maximum=CASE_FINAL_MAX`。
3. [evaluate 第710行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/good_expert_holdout_runtime_v1.py#L710>) 的原 `_metadata` case-FINAL 调用增加相同 keyword。
4. [grade 第822行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/good_expert_holdout_runtime_v1.py#L822>) 的原 `_base._metadata` case-FINAL 调用增加相同 keyword。

[完整差异证明](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/CONTRACT_DIFF.json>) 记录三函数 whitelist、其余27完整函数及2完整类的 Source/AST 不变；逆向移除上述四处变化后，全文 bytes 精确等于 D6。未替换 canonical `_metadata`、未全局扩容默认值，未裁剪任何完整函数作为运行时。

## 明确保留的合同

- canonical7a092 完整模块、原 `_metadata(path, maximum=262144)` 默认值与 max+1 / raw length / JSON dict 检查不变。其他 task-plan、worker error、close receipt、intent 读取仍走原默认上限；group 8MiB 不变。
- AppV6→dc4 Base 的完整 dependency 链、原 App pin/helper、原 `app.close()` 零参数、close 顺序、env close proof、fsync/atomic intent、全 raw bytes 的 SHA/length 绑定均不变。未知字段保留；canonical JSON 或筛选字段不能替代原 raw identity。
- 原 [完整九字段 teacher guard](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/producer_teacher_guard_v1.py>) 9635 bytes / SHA256 `a839ea0ca1a76b19bff1eaf304eafc1c16e54144fe370e40186aa8c07789028c` 原字节保留；whole-pi、Norm、STD、freeze、full-root、one-read/hash/decode、母 teacher 身份和 actual0-update 历史不变。没有重新打开母 PT。
- CURB_PROTECTED878 / SLOPE135 两角色；其余六角色 deferred，H1 不构造。seed20260929、20260930 各自独立 purpose；N80、每角色750 control、ascending/descending/standing 接受条件、physical D0–D7 / DR / reset / RNG 合同不变。
- 历史 close 错误、worker error、缺 intent、false source grade、outer RC1 仍是原失败；本组件不补历史 intent，不回填现场 PASS。

## V3 索引与封件

[NEW V3 source index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V3.json>)：21907 bytes / SHA256 `aa22260f2198ad37d6bb265c85d870203536a5dec19c6e554a556244cc5cddda`。原 V1 format kind 保留，历史 teacher revision2 保留；新增明确 case-final revision3。20 个 overlay 中仅 runtime 一 row 更新；其他19 whole rows（包括 guard、canonical alias、AppV6 和 Base）与 D6 完全相同。

本组件4成员加 [独立 SOURCE seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/SOURCE_SEAL.json>)；配套 [NEW V7 SOURCE 物化器](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/README.md>) 独立8成员加 seal。seal 后不再修改。

## 证据层级

[12项 NEW 测试及完整 own-temp receipts](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/TEST_REPORT.json>) 通过；完整 runtime / AppV6 / Base / guard 模块实际载入，不以 AST 片段或 stub 代替。仅在原 helper 明示允许的 TEST-only private pin 策略下使用 OWN FakeApp；close 返回，OWN returned marker 的去除只用于覆盖 fast-intent 分支，不是 native 非返回证明。

测试覆盖2MiB−1、精确2MiB、+1、截断、非 dict、完整未知字段、raw SHA/len、fsync-before-close、单次 close、缺失/错误 intent、durable error、第三处直接 Base reader 的 whole-data equality、两 seed 完整 metadata 和独立 outer RC1 负门。原旧测试未重放。真实 prepare/preflight/stage/dispatch、模型/SDK/GPU/SSH、真实 reports/FINAL 访问均为0。

CFF 的 NEW exact selector 与完整 packet 16MiB 测试由父 agent 交接，本组件不声明其输入或结果。以上是 SOURCE 正确性证据，不是新质量实测、native binding、跨 seed 技能通过率或现场 GO。
