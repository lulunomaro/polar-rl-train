# Good holdout lifecycle routes V3 — D5 最小 typed SOURCE 传播

## 交付范围

本包仅承接父 agent 给定的 D5 FINAL，形成 **NEW V3 的固定 pins、原有 typed metadata/version 传播、SOURCE 分列库存与 8 项小回归**。没有创建新的 stager、dispatcher、trainer、审批、资源准入、质量门槛或流水线。

本会话 catalog 为 Office / Windows ACL，未匹配 RL SOURCE 审计技能；采用 FS/CLI 与获准的 Python314 `-B` stdlib。所有本地执行仅为本包 SOURCE 库存/测试/封存；没有运行 SSH、prepare/preflight/stage/main、原 metadata_validate、controller、reader、collector、SDK、Torch、GPU、模型、raw、actual reports、C 预算/锁、signal、Git 或训练。B2 仅为只读 audit SOURCE 身份，不 import/execute。

SOURCE 的 `actual_native_binding` / Gate1 为 `UNKNOWN`，actual quality 为 `null`，exact/interface/stage2 GO 为 `false`。这些测试与 seal 不是现场 SDK、完整 original prepare、真实 metadata binding、original child/outer wait 或 EX release 的通过证明。

## 1. 生产代码最小差分

以下三个文件与冻结 V2 **整文件字节相同**，其完整 identity、Popen→actual wait、except/finally、full closure、whole FINAL cache、原 grade/ERROR/close binding/质量含义均保持：

| 文件 | bytes | SHA256 |
|---|---:|---|
| [controller](<good_holdout_parent_actual_wait_controller_v1.py>) | 5170 | `4cb6994a9afa0b399598f9af012529c9cd06bf6a8ad2e91c7d34f1c8496399c0` |
| [reader](<good_holdout_remote_reader.py>) | 30182 | `714e6def3ec9e128a5f31dae1de529d25ed86a59c33112b968b9d7ff15c6a7f6` |
| [collector](<collect_good_holdout_result.py>) | 15045 | `988f4fcce7f58fe33c105e86e2f1028c9b37ded7696bba00250d02b0359d3eab` |

[contract](<good_holdout_contract.py>) 只更新 `STAGE_KIND`、四项 D5 固定 SOURCE refs 与 content root，以及已有 `validate_stage` 的严格整数版本 `5` 和版本诊断 label。所有完整函数 AST 经这一处 existing typed version/label 归一后与 V2 相同；其余 top-level assignments 相同。既有 wire 字段和 COMPLETE 名称未扩充。

```text
COMPLETE_NAME = STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json
stage kind = SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5
source_derivation_version = strict int 5
```

`ROOT_PREFIX`、新增 approval 字段或 canonical-only 放宽均不存在。root/group/seed/GPU 的原 exact gates 保留。原始两个角色 C878/S135、两个 seed20260929/20260930、N80/750、full8 catalog/6 deferred、H1 excluded，以及原 physics/DR/cache/STD/actor/质量定义保持。

## 2. 固定 D5 FINAL（只读来源）

[原 D5 封件](<../source_stage_good_expert_holdout_v5/SOURCE_SEAL.json>) 实核全 8 members 与 root；没有 import 或执行 D5。路径与四项原始 refs 见 [contract](<good_holdout_contract.py>) / [库存](<SOURCE_PINS.json>)。

| ref | bytes | SHA256 |
|---|---:|---|
| source | 53521 | `9f40b92f9cb13b74ff35dd21f152310a173333f4f68b2aeafa57a5ea4f1dbfc8` |
| index | 33514 | `1149b918c0ec9badadca6a7fef98315671fd606dfb0d3de614fdc7d0bb644848` |
| mirror | 32862 | `b3c1a0f63c175d0ec344a59c9f89f0b780e0085dde6f2f6f867b63fd91579fe5` |
| seal | 1700 | `bf9c6dcfa98e2efe47844e13f55763aadfb20915361a139c0b87e564d4f84bad` |

```text
D5 eight-member root:
5e44c1870c0dc11fbe325194a12ddafd2715c977599f601c6a136353943db608
```

D5 唯一 prepare 语义修正是将 selected E1 canonical metadata 指向 ROOT 原文件；紧随的 `canonical == role` 严格判定未变。两个 ROOT SOURCE captures 中 `canonical` 分别是 `CURB_PROTECTED878` / `SLOPE135`；泛型 `role=E1_CURB/E1_SLOPE` 不是 alias，也未用 inner metadata 替代 ROOT。

[原 D5 prepare:443–444](<../source_stage_good_expert_holdout_v5/stage_good_expert_holdout_v5.py#L443-L444>)：

```python
canonical_rel = 'E1_CANONICAL_SOURCE_METADATA.json'
need(canonical_rel in files and metadata(files[canonical_rel][0])[0].get('canonical') == role, 'actual selected E1 canonical metadata differs')
```

本包对 D4→D5 完整 31 个函数只做 AST/source 分析：其余 28 个全函数 AST 及函数 source 完全相同；prepare / preflight_summary / stage 三个函数仅接受公布的 ROOT path 与 existing SourceV5 typed labels/version 差分。未执行这些函数，也未以 AST 摘片替代运行时生产 helper。原 copy/hash/fsync/full metadata 验证、27 deps、3 retained、parent/runtime 的资源规则均保留。

## 3. 三个身份严格分离

| 身份 | bytes | SHA256 |
|---|---:|---|
| actual wire SOURCE capture | 14112 | `a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1` |
| published Windows SOURCE reference | 14385 | `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0` |
| decoded canonical | — | `8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a` |

本地验证获准 SOURCE capture 的完整 14112 bytes 与 canonical。published 原计划及现场 diagnosis 只保留精确声明，不 stat/read；父所报告的 decoded whole equality 没有在本子重演。canonical equality 不替代 strict raw wire pin。

D5 actual materialization 后的原有 receipt 语义保持：`materialized=True`、`staged/source_native_enabled/dispatched=False`；其现存 `GROUP_PLAN_bytes` 与 `GROUP_PLAN_SHA256` 绑定最终 **whole raw plan bytes**。plan 只将已有 `enabled/staged` 变为 True。SOURCE receipt 的三个 False 不代表复制失败，最终 True-plan 的 hash 也不是原 published/wire plan 的 hash。

未来 unchanged controller 仍须实际读取这些 receipt/plan/原 parent bytes，凭 exact raw plan→GPU/full20/原 parent `fc445…` 绑定，并核实际 staged SOURCE 与生命周期文件状态后才到原 Popen。此包未自动执行该路径。

## 4. honest SOURCE inventory：127 / 136 / flat20 分开

[source_pins](<source_pins.py>) 先按路径拒绝 actual reports/model/raw/budget，再做小文本全 SHA 与 Python AST；所有旧封件只读复核。固定库存见 [SOURCE_PINS](<SOURCE_PINS.json>)：

| 集合 | 本地全文 SOURCE 核验 | 仅声明、现场报告未 stat/read |
|---|---:|---:|
| 旧92（逐字段保留） | 90 | 2 |
| D5 新增35 | 31 | 4 |
| D5 external127 | **121** | **6** |

加 D5 本包 8 members+seal 得逻辑136；这是 mirror 覆盖量，不是原 flat20 payload。原 good20 aliases 的完整映射、SHA 与原 parent/runtime identity 单独验证。各 seal/mirror/good20 集合有重叠，计数不是互斥加总，也没有声明全127 fresh read 或 parent physical once 等于本地 once。

六个 actual report identities 仅按 D5 published SOURCE 声明固定：旧 GROUP_PLAN、wire identity diagnosis、source-input diagnostic、quality boundary、ROOT canonical diagnostic、inner canonical diagnostic。全部未 stat/read。精确 paths/bytes/SHA 见 [SOURCE_PINS 的声明分列](<SOURCE_PINS.json>)。

末四项仅 audit 只读引用：三个报告仍为声明；B2 SOURCE API 的完整 31456 bytes / `a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62` 做 SHA/AST，标记 `active_dependency=False`、`imported_or_executed=False`。它不是本次 active runtime dependency。

获准本地 SOURCE 捕获15 = 两精确角色的 TASK/manifest/worker/bridge 共8 + E3 vendor 七模块；完整核验 11 Python / 4 JSON，未跟随其中模型或资产路径。另核 ROOT metadata2 原始身份。父诊断状态与 physical once22 是 parent-reported 历史，不计为本地新抓取、原 guard/full metadata_validate 执行、SDK/质量证明。

旧 good14、D2 nine、D3 ten、D4 ten、V1/V2 routes 各 twelve 的 members 与 root 均只读全核；旧 D4/V2 及父报告的三次 before-stage failure 保留：logical mirror/flat20、published/actual wire、inner/ROOT canonical metadata。V1 author40、V2 author11、parent-reported independent39/1 与40/0 原历史保留，未重跑或改写。

## 5. 本版本八项 SOURCE 回归

[test_v3_d5_metadata_source](<test_v3_d5_metadata_source.py>) 是 NEW V3 专属八项，不是旧40/11 或 D5 上游12。首轮8/8通过（2.657s），最终完整 `--receipt` 结果由 [测试报告](<SOURCE_TEST_REPORT.json>) 与 [原日志](<SOURCE_TEST_LOG.txt>) 固定：

1. 三个完整 production files 字节/AST 与 V2 相同；contract 全函数/assignment 仅 existing typed5/pins 白名单。
2. 两 seed 的 synthetic D5 typed receipt 通过；旧4、bool/string version、旧kind、错误 SOURCE flags、缺 final pins 等失败关闭。
3. wire/published/canonical 三身份、whole new raw plan、GPU、full20、原 parent bytes 的 negative gates。
4. 完整 inventory/旧92+35/所有旧 seal；六报告在 stat 前阻断；末4非 active 分层。
5. D5 index/mirror 的 stale kind、bool version、wire/published 混同、canonical 放宽、inner path、alias、报告重分类/缺项/重复/错 SHA 等负例。
6. 两精确 ROOT SOURCE metadata；missing canonical、泛型 role、大小写 alias、未知值负例。
7. 完整 D4/D5 modules 的余28全函数 AST/source 与三项归一差分；不执行 producer。
8. SOURCE captures15/root2 与历史 scope；flat20/136 区分，未 import/replay 旧测试，审计全0。

审计包含 Native import、模型/raw/report/budget/lock 访问、进程/network/signal/flock 和禁止的生产入口调用。SOURCE positive fixtures 只证明 metadata contracts，实际绑定仍 UNKNOWN。未知质量不补零；producer grade、child waits、double EX、outer actual wait 与 whole cached FINAL 的独立要求均沿用，RC0/materialization/finally 不替代它们。

## 6. 冻结与复核

[seal_source](<seal_source.py>) 只创建 NEW 本包 receipt/seal，12 members（不含 seal 自身）全部 actual on-disk bytes/SHA；root 为 UTF-8 的 sorted `name TAB bytes TAB SHA256 LF` records。日志 hash 来自实际磁盘 bytes，不依赖内存换行。已有 seal 时仅只读完整比对。

SOURCE-only 本地复核命令（无需连接或启动 runtime）：

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B .\source_pins.py
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B .\seal_source.py
```

最终 [SOURCE_RECEIPT](<SOURCE_RECEIPT.json>) / [SOURCE_SEAL](<SOURCE_SEAL.json>) 供父 agent 完整核对。未来实际 preflight、stage、parent、controller 的执行只归父 caller，本子交付不会触发它们。
