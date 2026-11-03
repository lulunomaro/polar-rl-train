# Good-holdout V2：独立 SOURCE review

**结论：SOURCE_REPAIR_CHECKS_PASS_NOT_LAUNCH_QUALIFIED。已查范围内 confirmed source blockers = 0；不是 native、实际 materialization 或 launch 签收。** 原 [NOT_LAUNCH_READY 报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_parent_readiness_review_v1/SOURCE_REPORT.md>)（24021B / `6145d41a8184daba7014b37ef5f06eac1dd2fb8795eee53720a48f2c03a930e8`）原样保留；V2 是新来源修复。

## 固定 PIN：实际核对一致

| 对象 | bytes / SHA256 |
|---|---|
| [V2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/SOURCE_SEAL.json>) | 1874 / `efee47debc71f12b9eed123283e08e34dcec757893cbff5532056db08657d75c`；9 members |
| 封件 root | `eb8b7b9ea06bbac56132eb0a761da35780547cc35ff9f9c1fb0166838a6b7d42` |
| [V2 entry](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py>) | 47717 / `f7638e1f24e416780d6124df5fea2492a63d5daac73984470b96a32132ca242d` |
| 显式 discoverySource [固定 V8 plan](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json>)（仅 SOURCE metadata） | 14385 / `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0` |

另核对旧8成员 materializer、旧14成员 overlay 的全部 seal/root；67个 WORKSPACE-relative mirror 全匹配、限定 R/T siblings。共77个既有小来源实际 SHA 核对、54 Python AST / 19 JSON 解析；探针结束后77项重新核对不变。具体 machine checks / PIN 见[配套 JSON](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_v2_parent_review_v1/SOURCE_REVIEW.json>)。

## 修复与不变量

- 固定 V8 plan 实为 **27 = 原24 indexed sources + assets metadata 2 + supervisor**；V2 精确集合/PIN 与之相等，旧 exact26 的来源阻塞已在新V2修复。资产仅核 metadata，没有读取资产本体。额外 supervisor `9247 / 7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27` 保留为原依赖，不覆盖 active parent。
- 原25函数中 **22函数完整 AST 和函数源码逐字相同**；仅 `prepare / preflight_summary / stage` 变化，新增5个 preservation helpers。非函数差异仅 docstring + 6个 V2 provenance 常量，无其他 imports/global/resource 改动。
- [preservation 链](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L283-L369>)：overlay 前独立 originals → `origin/input_path/bytes_read/SHA` → 三个异PIN旧 E1 alias 完整移动到 retained prefix → [实际输出 stream count/SHA observed 比较](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L630-L671>)。`installed` 来自 observed，而非直接抄 baseline；它是成功交给 `outgoing.write` 的 chunk SHA/count，**不是目标文件 post-write read-back**。sidecar 上限8388608B，独立于262144B plan。
- teacher-only / own zero-update container / N80 / 每角色750 controls / 原 predicates、physics、DR、资源门、waits 均保持原 PIN；H1排除、六角色 deferred 不构造。这里证明来源/代码不变，不证明 SDK 物理执行。

## 两seed：独立完整 metadata 探针

直接调用[与原V1整函数逐字相同的 `metadata_validate`](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L526-L605>)，没有调用 stager main/prepare/preflight_summary/stage、旧once或原tests。NEW fixture 仅在本 review 目录内创建、已清理：

| seed | fixture worker_files | fixture plan bytes | 结果 |
|---|---:|---:|---|
| 20260929 | 45，包含 supervisor + 3 retained aliases | 27476 | 两角色 make_task、跨seed负例、历史seed排除 PASS |
| 20260930 | 45，同上 | 27476 | 同上 PASS |

完整 AppV6 `27769 / 3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39` 和完整 Base `22337 / dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7` 真实 stdlib import，`helper._base` 绑定实际 Base，非裁剪/stub。[原 overlay schema](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L293-L308>)要求20 aliases为**子集而非全表相等**，所以接受新增安全别名。两seed删 Base alias 都正确报 `all twenty complete holdout overlay mappings must be present once`；删 observed supervisor / 改 retained SHA 也正确失败。

**探针边界：** synthetic producer descriptors；仅内存重定位 expected `source_path` 到未创建的 own-checkpoint 路径，保留原 source/mother bytes/SHA。资产/runtime/vendor 部分是明确 synthetic markers；45/27476只是 fixture 大小，不是未来实际闭包规模。metadata FD101/102是内存占位，不是 admission。首次自有包装重复 `seed` 导致 TypeError，修正仅涉及自有 inline wrapper，第二次完整 PASS；未修改封件。

## 尚缺实际证据 / 不支持扩大声称

1. 既有18/18 receipt 属 SOURCE regression，未被本轮重跑；它及本轮探针都不证明真实 assets、完整 runtime banks/vendor7、actual producer 或 stage 成功。
2. App/SDK/MRO/pose/native binding、物理 checkpoint containment/cache、原 privateEX+finiteEX+C-readonly admission、真实 DR/predicates/close/全部 wait 尚无本轮实际证据。
3. [原 native parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py#L79-L86>)入口要求 `enabled=True, staged=True`；当前 source/materialized 状态为 False。完整每seed controller + collector + **outer actual parent p.wait** 接续仍是 gap，本轮未生成或执行这些程序。
4. 未来 CLI 的 `--source-index` 是[原20项 overlay index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json>)，**不是**[新 V2 SOURCE_INDEX](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/SOURCE_INDEX.json>)；[mirror67](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/SOURCE_MIRROR_INPUTS.json>)也不是 flat20/完整静态输入。
5. `source_native_enabled/staged/dispatched=False`、`actual_native_binding=UNKNOWN`、实际评估/收益=null；没有实际新native授权。

**操作核对：** 仅新增本 review MD/JSON；77既有来源不变。SSH / 非白名单 actualreports / trace / PT-model stat/open / raw-assets / SDK-Torch-GPU / C-budget / 锁 / Git / parent-worker / 被禁 stager entry / 旧tests / 旧sealed编辑均为0。本轮 source-only 修复通过不改变原预算、资源门和资格阈值。
