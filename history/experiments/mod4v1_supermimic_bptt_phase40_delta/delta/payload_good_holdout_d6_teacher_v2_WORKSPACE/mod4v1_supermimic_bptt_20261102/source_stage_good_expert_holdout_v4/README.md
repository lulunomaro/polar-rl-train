# Good-expert holdout D4：严格原 wire 身份与 published SOURCE 身份分离

**状态：`SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE`。** 本包仅交付新的 D4 源码、36 项 stdlib/FAKE 回归和不可变文本封件。源码、index、seal 的 `enabled/source_native_enabled/staged/dispatched` 全部为 False；实际 native binding、独立 seed 质量、SDK/资源准入及原生关闭仍为 UNKNOWN。没有实际调用 prepare/preflight/stage/main、parent/worker、SSH、SDK/Torch、PT/raw、GPU、C ledger、锁或 Git。

## 1. 本次最小修复与历史边界

父侧先前两次 before-stage 失败各自保留：第一次 payload 只有逻辑 source mirror、缺 flat20；第二次 NEW flat20 已通过源码映射，D3 对原计划的严格 cached 字节断言随后失败。本包没有把任何一次历史失败改记为 PASS，也没有实际重跑它们。

允许的 SOURCE 诊断表明：实际原计划 wire 与本地已发布 cached 文本完整 JSON 解码值完全相等，但字节并不相同。D4 只修正此身份混用：

| 身份 | 字节数 | SHA256 | 用途 |
|---|---:|---|---|
| [实际原 wire 的固定 SOURCE capture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json>) | 14112 | `a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1` | 未来 prepare 的严格 `ORIGINAL_PLAN_PIN`；实际 `original_plan_SHA` 的身份 |
| [cached published SOURCE reference](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json>) | 14385 | `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0` | 独立 `PUBLISHED_ORIGINAL_PLAN_PIN`；旧 mirror 原声明保持原样 |
| [父侧 wire/published SOURCE 诊断](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json>) | 1459 | `673398d112f60f084b9c945a747d0d13625e43487291549d9d4dfca0a3991b38` | 只读来源；不是本包的新远端读或实际 stage 结果 |

固定 decoded canonical SHA256：

```text
8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a
```

cached 的 273 个 CRLF 换成 LF 后恰等于该 wire；wire 无 CRLF。此处只是解释两个已固定输入的差异，生产代码**没有**换行修复、重写原件或 canonical-only 放行。严格 raw wire 长度/SHA 先过，再对同一次解码结果增加一个固定 canonical guard。相同解码值的其他序列化、CRLF 版本、末尾额外换行仍失败。原 27 项 worker-file 依赖逐项完全相同；JSON 中的模型路径只作字符串，未跟随打开。

## 2. 真正的源码差异

[D4 CLI](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/stage_good_expert_holdout_v4.py>) 为 53515 bytes，SHA256：

```text
c6be5e8acd2bd1a83f09427fb717cc1d102077cf363b67034d65d09f4e86ab0d
```

相对 [完整 sealed D3 CLI](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py>)：

- `prepare`：原一次 metadata 读取及严格长度/hash 顺序不变；固定 tuple 使用实际 wire。只把错误文字改成 wire，并插入一个固定 decoded canonical `need`。其他完整 AST 相同。
- `preflight_summary`、`stage`：仅 SOURCE kind/version 从 3 传播为 4。
- 其余 **28 个 D3 函数完整源码与 AST 相同**，没有新增 runtime helper。既有 `derive_materialized_runtime_plan`、完整 `metadata_validate`、`source_mappings`、`main`、复制/hash/fsync loop、独立原件保全、实际 stream observations 及所有资源/等待/close 逻辑均不变。
- [原 holdout parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py>) 9679 bytes / `fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff`，以及 [原 holdout runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py>) 56370 bytes / `4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f`，保持完整原字节。

只请求 CURB_PROTECTED878/SLOPE135，完整八角色 catalog 保留、其余六项 deferred、H1 不构造。未来完整静态树拷贝针对两个被选角色的原 E1 runtime/source/static-bank/dependency trees；不是宣称复制了其余六角色的物理运行树。原 required27、三处真实 E1 alias 的 retained original、完整 vendor7、资产身份、teacher-only、N80/750、原方向/standing 条件与原 physical D0–D7 均不变。原 privateGPU_EX/global_finite_EX/Creadonly、empty23500、RAM96、disk25、wait1800、ready900、deadline2400，以及实际子进程 wait/finally-before-unlock 不变。

## 3. 未来 typed publication 与 receipt 接口

prepare/preflight 始终保留四个 SOURCE False 标志。仅未来实际 stage 在全部 materials copy/hash/fsync、独立 origin/retained 与实际 observations 检查通过后，调用既有纯 helper 深拷贝计划，只将现有 `enabled/staged` 两项改成 True；完整未修改的 `metadata_validate` 再通过后，才写新 `GROUP_PLAN.json`。`source_native_enabled/dispatched` 仍 False，原 source plan 和 encoded bytes 未被原地修改。

本轮没有执行上述 stage；36 项只验证 SOURCE 与自有 in-memory FAKE publication probe。

```text
COMPLETE_NAME = STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json
stage receipt.kind = SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4
stage receipt.source_derivation_version = 4
stage receipt.materialized = True
stage receipt.source_native_enabled = False
stage receipt.staged = False
stage receipt.dispatched = False
runtime GROUP_PLAN.enabled = True
runtime GROUP_PLAN.staged = True
runtime GROUP_PLAN.source_native_enabled = False
runtime GROUP_PLAN.dispatched = False
```

沿 D3 仅有两个新计划 hash binding 字段，不新增 approval/admission/ledger/SDK gate：

```text
GROUP_PLAN_bytes  = strict int len(exact final UTF8 runtime_bytes)
GROUP_PLAN_SHA256 = SHA256(exact same runtime_bytes submitted to successful fsynced write)
original_plan_SHA = a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1
```

最后一项是原 V8 实际 wire，不是 cached SOURCE 的 54172…，也不是新 runtime GROUP_PLAN 的 hash。新计划 hash 绑定没有伪装成独立目标读回证据；未来外部 controller/collector 应对实际读取的完整有界原始字节另行核对。内置 source grade/子进程 wait/双 EX 关闭与独立外部 parent Popen.wait 证明仍是不同层。本包没有新 dispatcher/controller/collector 或资源 admission。

root 规则未引入固定 PREFIX：显式 absolute、absent、non-symlink、与输入双向不重叠；`new_root.name == group_id`，`group_id` 匹配 `[A-Za-z0-9_]+`、包含严格 seed 的十进制串且不同于原 group。每个 seed 独立 one-use root。允许 seed 仅 20260929、20260930；purpose 仍 `GOOD_EXPERT_HOLDOUT_C878_S135_SEED<seed>_V1`。

## 4. 实际封件、镜像与字段

本包实际计划成员为 **10 个文件，加 1 个独立 seal**；外部文本 SOURCE 闭包实际为 **92 项**，来自全部旧 79 项原字节、sealed D3 的 10 项加 seal、以及 wire capture/diagnosis 两项，去重后核定。没有以旧 10/79 或推测数作为新证据。权威逐项数量和 hash 见 [seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/SOURCE_SEAL.json>) 与 [SOURCE mirror](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/SOURCE_MIRROR_INPUTS.json>)。

镜像 `files` 每项仍是 `workspace_relative/bytes/SHA256`，根布局保留 WORKSPACE 下 R/T 两个兄弟工程树。旧 published 14385/54172… mirror 行完全不变；新增 capture 行独立 14112/a78…。它们不是可互换的 wire，也不是模型或 SDK payload。新版十成员与 seal 需另外携带，92 项不含本包自身。

[SOURCE index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/SOURCE_INDEX.json>) 继承旧字段并明确区分：

| 字段 | 固定含义 |
|---|---|
| `original_group_plan` | 原 cached published SOURCE reference，14385/54172…，原声明不改 |
| `original_group_plan_wire` | 固定实际 wire capture 来源，14112/a78… |
| `original_group_plan_wire_identity` | 两 tuple、固定 canonical、literal bytes 不相等、canonical 不放宽 raw pin、旧失败不抹掉 |
| `wire_identity_diagnosis_source_only` | 上表只读诊断的 path/bytes/SHA256；不执行 |
| `typed_runtime_publication` | V4 receipt kind、两 flag publication 及新计划两 hash 字段，原 wire hash 身份显式独立 |
| `flat_source_dir_complete20_mapping` | 原完整 20 项 relative/flat_name/source_workspace_relative/bytes/SHA256，原样保留 |
| `source_mirror` | 本次实际 mirror 文件的 bytes/SHA256/files_count |

**92 项逻辑 mirror 不替代 flat20 payload。** 未来 `--source-dir` 需要实际存在的、按 flat_name 布置的 20 个固定文件；[upstream overlay index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json>) 才是 CLI `--source-index` 参数，不是新 materializer SOURCE index。`source_mappings` 完整函数未变；本包没有自动组装、stage 或部署该 payload。

## 5. NEW 36 项 stdlib/FAKE 回归

[测试报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/TEST_REPORT.json>)：36/36 PASS、errors/failures 均 0，五项 audit 全 0。原 D3/V2 测试模块没有 import/replay；[NEW 测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/test_good_holdout_v4_source.py>) 来自固定完整旧文本派生。

- 保留既有 32 个 SOURCE case：required27/25实际源码、alias 冲突保全、独立 provenance、全 materials observation、缺失/tamper/伪造 counterexample、两个独立 seed 的完整未修改 metadata_validate、只改两 flag、旧 False stage 与无 emit、原 copy/fsync/parent-close AST。
- 新增 4 个 case：固定 wire 与 published SOURCE 分离；完整解码/canonical 等价不代表 wire 身份；CRLF/额外换行/其他等价序列化仍被 raw pin 拦截；仅一个 canonical guard 的精确 prepare 差异；wire 的 required27 及两个 seed 的完整 metadata 再核对。
- 只有两个纯 identity `need` 表达式在自有 FAKE AST probe 中执行，不调用完整 prepare。完整 metadata_validate 是未裁剪的真实安全源码视图配 synthetic producer metadata，不通过小段替身伪装整体模块。
- 两个资产仅固定 metadata，不创建/stat/open；模型路径不创建、不 stat/open/hash/decode。实际 static-bank/vendor7/资产/native 质量不是本测试产物。

## 6. 复现与后续边界

以下为源码回归/只读封件核验命令，非 native 操作。封件后无需重新运行生成器或测试来消费证据；测试会重写自身测试报告，消费封件优先只读 `--verify`。

```powershell
# 未封 SOURCE 开发期才运行：NEW 测试，不是 materializer entry。
python -B source_stage_good_expert_holdout_v4/test_good_holdout_v4_source.py
# 在 R 目录消费最终封件：只读完整依赖/成员/hash/AST 核验。
python -B source_stage_good_expert_holdout_v4/build_source_manifest_v4.py --verify
```

[最窄 source deriver](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/derive_stage_good_holdout_v4.py>)、[NEW regression deriver](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/derive_regressions_v4.py>) 和 [metadata/seal builder](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v4/build_source_manifest_v4.py>) 仅在本 NEW 目录生成或核对 SOURCE，不调用 native entry。

未来实际 CLI 输入仍为 `--original-group-root/--source-dir/--source-index/--native-root/--new-root/--group-id/--gpu-uuid/--seed` 和二选一 `--preflight-only/--stage`；本轮均未执行。需要父侧另外复核完整原件/static/vendor/producer 关闭元数据、flat20、独立 controller/collector 和原准入接口。归档、收到 late source seal 或本 SOURCE PASS 都不是自动 prepare/stage/GO 触发器。

本任务不再训练好专家；A1 actual0-update fullcapture 的 embedded 原 teacher mean 仍是保持 baseline，不把 fresh WM/optimizer0 称为 SM 训练。独立 20260929/20260930 证据仍待真实评测；统计只按 direction/standing 条件报告，不合并成整个技能 90，也不声称改进或非劣性。
