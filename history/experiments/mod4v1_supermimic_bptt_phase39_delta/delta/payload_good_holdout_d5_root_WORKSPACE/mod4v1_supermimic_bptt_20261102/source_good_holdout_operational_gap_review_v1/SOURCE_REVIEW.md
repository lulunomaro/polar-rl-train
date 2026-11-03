# Good holdout：只读 operational-gap SOURCE trace

**结论：`SOURCE_TRACE_COMPLETE_NOT_LAUNCH_QUALIFIED`。当前封存 V2 CLI 的实际代码路径保留 disabled plan；直接交给原 native parent 会在进入 `main()` 前失败。该结论只覆盖下述已读 SOURCE 链，不断言外部未知调用者永远保持 False。**

本轮只新增本 MD 与[配套 JSON](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_operational_gap_review_v1/SOURCE_REVIEW.json>)，不实施修复、activation、controller 或 stager。目录创建前不存在。catalog 只有 Office/ACL 匹配项，本任务无对应技能，采用 FS read/glob/grep 与 stdlib AST/hash；纯 helper CPU probes=0，stager 导入及 entry 调用=0。

## 1. enabled/staged 的完整真实链

| 位置 | 实际语义 |
|---|---|
| [V2 常量:29–30](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L29-L30>) | SOURCE 标志 False；完成回执名固定为 `STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json`。这是源码状态，不是 admission。 |
| [prepare:411–422](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L411-L422>) | 新 plan 明确 `enabled=False, staged=False, source_native_enabled=False, dispatched=False`。每 seed 的 purpose 独立。 |
| [prepare:471–478](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L471-L478>) | 序列化为 `encoded_plan`；metadata validation 不把这个字节串转换成 enabled plan。 |
| [stage:630–656](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L630-L656>) | 完整复制/hash/preservation 后，655 行原样写 `prepared['encoded_plan']` 到目标 GROUP_PLAN；没有 enabled/staged 的 True 发布点。 |
| [stage:658–667](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L658-L667>) | 回执仅 `materialized=True`，仍 `source_native_enabled=False, staged=False, dispatched=False`。`original_plan_SHA` 指原固定 V8 plan，不是新 GROUP_PLAN hash。 |
| [CLI:674–687](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py#L674-L687>) | `--stage` 就是 `prepare(...) → stage(prepared)`，没有额外转换。 |
| [原 parent:79–87](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py#L79-L87>) | 81–82 行读 GROUP_PLAN 并要求两项 `is True`，83 行才 `main()`；disabled plan 失败先于 PARENT_STARTED、EX/resource admission、SDK/worker。 |

所以：**SOURCE materialization 的完成与 native 入口可达不是同一状态。** SOURCE seal/index 的 False 应原样保存；运行时 plan 的 True 应由真实 materialization 后的窄 typed 发布路径建立，而不是新增 manual-approval bool、新账本、复制资源准入或把 False 改成成功声称。本轮没有选择或实现该发布路径。

[完整 runtime:279–345](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L279-L345>)校验角色/seed/protocol/20 aliases，但不要求 enabled/staged 为 False；故 False 不是整个 schema 的永久约束。metadata PASS 也不证明 parent 的 entry gate 已通过。

## 2. 已声明可复用发布模块：有边界，非 drop-in

在已追踪的 **20 overlay mappings + V2 CLI + 原 parent entry** 内，没有声明与 C878/S135 两独立 seed 相容的 True-plan 发布模块。此为限定链的结论，不是全仓库不存在任何外部发布程序的断言。

- [既有 reference controller:15–25](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reference_parent_actual_wait_controller_v1.py#L15-L25>)保留了完整真实 `Popen → child.wait → finally wait receipt`，但硬 pin E3/W35 root、stage 名、parent 名及 SHA；它不改 GROUP_PLAN。
- [Phase1 controller:9–18、27–38](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py#L9-L38>)同样可作为完整生命周期来源；当前 purpose/PT0/E3 parent/root/receipt 路由不适用于 holdout，且没有激活 plan。
- [原 E3/W35 stager:488–498](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_native_v1/stage_embedded_teacher_native_v1.py#L488-L498>)确实产生 `staged=True` 的旧角色回执；[其 plan:299–305](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_native_v1/stage_embedded_teacher_native_v1.py#L299-L305>)是另一 typed kind/purpose，旧 True 回执不构成新 holdout 的状态转换证据。

## 3. 每 seed 尚缺的 typed 接续（不是新字段发明）

两组分别为 `20260929 / GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260929_V1` 与 `20260930 / GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260930_V1`；不同一次性 group/root，均仅 C878/S135、N80/750，完整八角色 catalog、六 deferred、H1 不构造。

| 接续 | 现有字段/判据及当前缺口 |
|---|---|
| materialization → native plan | 目标 plan 的 `kind/group_id/GPU_UUID/seed/batch_purpose/holdout_protocol/worker_files` 必须与实际材料和 seed 相符；入口 `enabled/staged=True` 尚无本链发布点。新 GROUP_PLAN 的实际 bytes/SHA 与 stage receipt SHA 的 binding 也需明确；V2 回执没有 Phase1 的 `GROUP_PLAN_SHA256` 字段，不将 `original_plan_SHA` 冒充它。 |
| outer actual parent controller | 复用现有 `root/group_id/stage_receipt_SHA256/parent_source_SHA/controller_source_SHA` 与 `controller,parent={pid,linux_start_ticks}` 语义。只对正确 seed 的原 parent 一次 `Popen`；`actual_native_parent_Popen_calls=1`、`SDK_scene_or_skill_admission=False`。当前未提供兼容 holdout 的 typed 路由/receipt 绑定。 |
| outer wait | 真实 `Popen.wait()` 返回后才有 `actual_parent_p_wait_returned=True`、整数 `returncode`、同一 parent/controller identity、`controller_errors`、`original_parent_resource_close_wait_not_replaced=True`。RC0/文件存在/PID 消失均不是替代。原 parent 内部 child waits 与双 EX release 仍独立保留。 |
| 结果 collector | 校验实际 admission、原 `TERMINAL_ROWS` 两角色、group FINAL 的 **`rows`**、原 `PARENT_EXIT_SCOPE`、`REFERENCE_GROUP_CLOSED_SOURCE_GRADE_V1` 与独立 outer wait，按同一 group/seed/purpose/PID 绑定；保留全部错误与完整 FINAL hash/close 语义。当前没有适配 holdout 的完整 collector 路由。 |
| 两 seed 汇总 | [原 summary:170–219](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L170-L219>)仅消费两份已 externally qualified、实际 waited 的组结果；按 ascending/descending/standing 条件统计，不产生 admission/outer-wait 证明、不汇成 whole-skill90 或改进结论。 |

[原 parent:44–78](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py#L44-L78>)保留两 worker 实际 waits/finally wait-before-unlock；[原 grade:776–832](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py#L776-L832>)明确 `external_parent_wait_proof_created_here=False`。二者均不填补 outer wait。

Phase1 [collector:46–142](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_result_collector_v4/collect_capture_result.py#L46-L142>)硬 pin E3/PT0/64或128，并读 `terminal` 而非本组 `rows`；[reader:31–59、175–256](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_result_collector_v4/remote_metadata_reader.py#L31-L256>)也硬 pin Phase1 aliases/metadata/projection。可复用完整 bounded-read/cache/hash、identity、atomic-output 与 wait 分层代码，**不是改名后直接收新质量结果**。holdout 必须保留 metrics、source_cache、seed、evaluation_purpose、fresh DR、physics/feedback/actor、fast-close whole-FINAL hash；不修补 producer 判据。

## 4. 最小后续 SOURCE 范围与固定 pins

父决策只需覆盖：①真实 materialization 与 native plan 的窄 typed 状态发布；②每 seed 原 parent 的薄 outer-wait 路由；③双角色 metadata collector 路由。复用完整原模块/函数，资源、原 close/wait、teacher/cache、物理和接受条件均不变；无需大框架/dispatcher。本轮均未生成或实施。

| 已读完整模块 | bytes / SHA256 |
|---|---|
| [V2 stager](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v2/stage_good_expert_holdout_v2.py>) | 47717 / `f7638e1f24e416780d6124df5fea2492a63d5daac73984470b96a32132ca242d` |
| [holdout parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py>) | 9679 / `fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff` |
| [holdout runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py>) | 56370 / `4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f` |
| [outer controller 来源](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py>) | 3824 / `95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831` |
| [collector 来源](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_result_collector_v4/collect_capture_result.py>) | 17445 / `20462d77526c418945e97596d6c9735cb427096b1e08938324388d261be91010` |
| [bounded reader 来源](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_result_collector_v4/remote_metadata_reader.py>) | 17852 / `0e220b69dddec39197c4ff54a956ad4f6385644a8794b19ce15c5616a24702ed` |

本轮 stdlib 只读验证：V2 全9成员/root、overlay 全14成员/root、20 mappings 实际字节均匹配；共49个小来源前后 hash 一致。原[ BAC 44行 review](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_v2_parent_review_v1/SOURCE_REVIEW.md#L36-L44>)的40行已经明确同一 operational gap；其 `confirmed_source_blockers=0` 是来源修复检查范围，与本 trace 不冲突。

**本轮操作为0：** SSH、非白名单 actualreports/trace、teacher/model/PT/raw stat/open、SDK/Torch/GPU、C ledger、锁、Git、stager/parent/worker entry、旧 once/tests、activation、旧封件修改。只读原固定 V8 plan metadata；未观察实际 good-holdout launch 或新质量，不把父通报的其他窗口结果当本轮实测。
