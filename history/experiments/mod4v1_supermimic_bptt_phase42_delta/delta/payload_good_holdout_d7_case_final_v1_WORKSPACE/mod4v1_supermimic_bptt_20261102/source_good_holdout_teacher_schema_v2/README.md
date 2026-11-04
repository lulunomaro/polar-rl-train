# Good holdout teacher schema — NEW SOURCE revision V2

**SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE**。enabled / source_native_enabled / staged / dispatched 全 False；实际 native binding UNKNOWN。本目录只提供两份完整原模块的最窄派生和完整 20-alias overlay index；没有新的 actor、物理、接受条件、预算或资源执行器。

## 1. 为什么保留完整九字段

父进程已发布的 [实际 metadata 诊断 V2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2.json>) 对 CURB_PROTECTED878 和 SLOPE135 的原 FINAL 各一次读字节/hash/decode。两者的 `FINAL.teacher == FINAL.checkpoint.teacher_source` 都是完整 9-key dict。该次数属于父诊断历史，非本封件本地文件核验次数，也不是原 PT 的观察。

D5 materializer 把这份 raw teacher 经 `teacher_identity` 投影为 4 字段，导致原 good runtime 的完整对象相等断言失败。仅恢复 raw 九字段又会与原 reference guard 的 `row == mother_projection4` 冲突。这是两个活跃 metadata predicate 的 schema 冲突，不是新质量或模型失败。

原 good runtime 在第 58 行精确 pin 原 guard，因此单独换 guard 文件也会被原字节 pin 拦住。本 NEW 组件只传播必需的 guard/runtime/index 精确新 pin。

## 2. 精确改动

### 完整 guard：仅 `validate_reference_row`

[NEW 完整 guard](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/producer_teacher_guard_v1.py>) 保留原模块及其他完整函数，只把该函数的母身份 predicate 改为同时要求：

1. `type(original) is dict`；`original == producer['FINAL']['teacher']`，完整内容相等；
2. key 集合精确为原实际两个 baseline 的 9 字段，不采用 subset 比较；
3. `physical_byte_opens`、`SHA_calculations`、`decodes` 均 `type(value) is int and value == 1`；
4. `whole_bootstrap_checkpoint_retained`、`original_PPO_optimizer_preserved_not_restored_to_new_BPTT` 均 `value is True`；
5. `teacher_identity(original) == mother`：原四身份 path/SHA/bytes/frozen 严格核对仍在。

缺字段、额外字段、False、0、0.0、1.0 或 True 冒充 int1 都失败；不制造 approved flags，不补默认值，不删除原 metadata。此精确 schema 是这两个固定 baseline 已观察到的数据约束，不外推其他 producer。

原 `derive_producer_guard`、`teacher_identity`、whole source bytes/pins、TASK/manifest 读取、all-state snapshot / torch.equal-before-save 与 FINAL 的绑定、evidence 字段及 `return evidence` 全部保持。原 source2 worker/bridge 的证明没有被 fixture 或布尔常量替代。

### 完整 runtime：仅 guard tuple

[NEW 完整 runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py>) 只更新第 58 行 guard 的 `(bytes, SHA256)` literal。所有函数完整源码和 AST 与原 runtime 相同，尤其原 `checkpoint.teacher_source == FINAL.teacher == row.original_bootstrap_teacher`、母 teacher 固定身份、teacherFrozen True 和 actual0/fullcapture 要求保留。

[精确函数与 patch 证明](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/SCHEMA_DIFF.json>) 记录每个未改完整函数的字节/hash，并保留两份完整模块的文本差分。

### 完整 20-alias index

[NEW index V2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json>) 保留原 `kind=SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_C878_S135_INDEX_V1` 作为既有**格式 schema**，另以 NEW V2 文件、`teacher_schema_source_revision.revision=2` 和独立 seal 区分新 SOURCE 身份。不是复用旧 stage kind。

只有 guard/runtime 两个 overlay row 的实际 source path/bytes/SHA 改变；其余 18 个 row 以及 inherited 原 worker、provenance、原 runtime rows、assets、source_state 原值逐项保留。安装 alias 与 flat basename 仍为原 v1 名称，完整数量仍 20。旧 Source index 及其 seal 不改。

## 3. 闭包与缓存

canonical `a1_frozen_eval_runtime_v2.py` 仍为 37927 / `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e`。全文件核对未发现 guard 或 holdout runtime 的另一个固定 pin；只有通用 `_pinned_module` 及原 pose/helper/App 调用。

AppV6 → dc4 Base、原 parent `fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff`、E1 worker/factory/bridge、原一 reset、true term/trunc、D0D7、STD/wholepi/Norm/freeze/one-own-bytes/hash/decode 与 mother-open0 均不改。原 metadata_validate 的 12-module pop/restore 列表已含 guard/runtime/embedded reference；没有新热模块或 cache 补丁。

外层 good runtime source_cache 保留完整 row teacher，后续 semantic 也比较完整 row；嵌入 mean reference 内部的四身份投影彼此一致，另一处仅比较 SHA，因此未发现第三个 raw/projection 冲突。其余原 runtime、母 PT、SDK 与物理实际绑定仍待父后续流程观察。

## 4. 回归、封存和边界

八项 NEW AST/内存三 dict 测试在 [D6 TEST_REPORT](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/TEST_REPORT.json>)：只执行原完整 pure `need` / `teacher_identity`、原 runtime 的精确身份语句块、NEW guard 的精确身份语句块和单独 deepcopy 表达式。没有调用完整 validator、derive_producer_guard、prepare、metadata_validate、旧测试或 native 入口。

[本组件 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/SOURCE_SEAL.json>) 覆盖 README、SCHEMA_DIFF、完整 20 index 及两个完整模块，共 5 个成员。D6 的 SOURCE mirror/索引另 pin 此 seal，避免 index 自 pin 循环。最终只读核验由 [SOURCE packager](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/build_source_v6.py>) 执行；它仅派生文本、AST/hash/JSON 和封件，不导入或运行 materializer/worker/parent。

D5 及更早 actual preflight 失败、V1 bare-python RC127、既有 seal 和报告保留原记录。此 SOURCE PASS 不是 actual preflight、native、质量改进或 noninferiority 结果。H1 继续冻结，六角色 deferred；CURB_PROTECTED878/SLOPE135 保持原 N80、每角色 750 controls、原 ascending/descending/standing、独立 holdout seeds 20260929/20260930 和 per-direction/standing 统计含义。
