# Good-expert holdout D5 — 最小 ROOT canonical metadata SOURCE 修正

**状态：`SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE`。** `enabled / staged / source_native_enabled / dispatched` 全 False，native binding UNKNOWN。本轮交付 SOURCE，不执行 prepare、主函数、实际 preflight/stage、parent/worker，也不引入消费者、dispatcher、资源代码或新评测协议。

## 1. 唯一语义修改与精确接口

[新入口](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/stage_good_expert_holdout_v5.py>) 从完整固定 D4 封件派生，53521 bytes / SHA256 `9f40b92f9cb13b74ff35dd21f152310a173333f4f68b2aeafa57a5ea4f1dbfc8`。

```diff
- canonical_rel = 'runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json'
+ canonical_rel = 'E1_CANONICAL_SOURCE_METADATA.json'
```

下一条原判断完整保留：

```python
need(canonical_rel in files and metadata(files[canonical_rel][0])[0].get('canonical') == role,
     'actual selected E1 canonical metadata differs')
```

ROOT 是 original runtime tree 的根，不是工程根或 runtime/isaac/mod4。实际 ROOT metadata 的 `canonical` 分别为 `CURB_PROTECTED878` / `SLOPE135`；`role` 字段中的 `E1_CURB` / `E1_SLOPE` 是另一语义字段，非 alias。不做路径搜索、同名回退、角色通配或降低条件。

其余变化仅模块说明、`SOURCE_DERIVATION_VERSION=5`、preflight / stage 的 SOURCE kind 与 `source_derivation_version=5`。**函数集合不变，prepare/preflight_summary/stage 三函数有精确白名单差异，其余 28 个 D4 函数完整源码与 AST 相同。** [最小 diff 与逐函数证明](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/WHITELIST_DIFF.json>) 含真实 unified diff，无新 runtime helper。

## 2. 先前 pending 条件如何关闭

[集中实际 SOURCE 诊断](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_CONCENTRATED_ACTUAL_SOURCE_INPUT_DIAGNOSTIC_V1.json>)：49207 bytes / `31e4ab2668701db00fad59ea94badf09d3e8fe8975cc8b70f35aad73f77767c0`，父已收 RC0，receipt PASS/errors[]。

- 原完整 D4 native_boundary 得到两个 actual0 producer；原完整 derive_producer_guard 两角色通过 TASK → manifest raw SHA → 精确 worker/bridge 源码 → whole-AST allstate snapshot/freeze/save/FINAL 绑定。
- 15 core SOURCE 捕获均逐一核验 bytes/SHA：两角色各 TASK/INSTALL_MANIFEST/worker/bridge 共 8，加 E3 原 vendor7 共 7。11 个 Python 文件仅完整 AST 解析；4 个 JSON 仅解码，不 follow 模型路径。
- vendor 实际名称为 `__init__.py, contract.py, geometry.py, learner.py, logging.py, networks.py, replay.py`，7-tree SHA `ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`；原 docstring-only init 与完整 AST 由父诊断保持原判据。
- receipt 另有 7 项 closed-boundary 元数据上下文；22 个原路径各物理一次读是**父诊断历史记录**，不是本地 SOURCE 核验读次数。该诊断自身不是 prepare 重放，更不是新 GPU/native/质量结果。

两份实际 ROOT 捕获分别为 [C878 ROOT](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/good_holdout_runtime_root_metadata_v2/CURB_PROTECTED878_E1_CANONICAL_SOURCE_METADATA.json>) 4814 / `671f77ddef5fbd79de8dafc54213ff754cfc70ac5a9d9611680e9c76c021cfc5` 与 [S135 ROOT](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/good_holdout_runtime_root_metadata_v2/SLOPE135_E1_CANONICAL_SOURCE_METADATA.json>) 5390 / `f9a0a42c6b1390e38013a410e454da4a9d63569d47f014c3b6f6ea4ca7615b41`。

[旧审计 MD](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_d4_input_assumption_audit_v1/SOURCE_AUDIT.md>) 与 [旧审计 JSON](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_d4_input_assumption_audit_v1/SOURCE_AUDIT.json>) 的 pending 状态是当时事实，原字节不改；新索引只记录后续诊断已关闭该 SOURCE 条件。

## 3. 小 NEW 回归，不重放旧 36

[NEW 测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/test_good_holdout_v5_source.py>) **12/12 PASS**；[receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/TEST_REPORT.json>) 五项 audit 全 0。

覆盖：D4 十封件和旧 92 pins、精确三函数/28 完整源码 AST、ROOT 两捕获、ROOT-only 选择、内层同名 decoy 不读取、inner-only 不回退、错误 ROOT 不被正确 inner 救回、缺失/小写/generic role 不当 canonical、a78/54172/8c 三重身份不变、V5 typed fields 与原 publication helper、15 captures/source 诊断边界、缓存名单 12 项含 embedded teacher reference、旧测试模块未导入/重放。

FAKE selector 只编译原 prepare 中两个 selector 语句及完整 need()，输入全在内存；**不是执行完整 prepare，也没有执行完整 metadata_validate**。原完整 metadata/helper/main/copy/fsync/preservation/guard/resource 的保持性由逐函数源码与 AST 证明，不借 FAKE 结果宣称 native 通过。

本地最初一次测试 harness 在 suite 前被自身 SOURCE-only audit 拦下 importlib 的缺省 `.pyc` 探测。只修 NEW harness 为执行完整 NEW stdlib packager 源码文本；没有读取该 pyc，没有修改 production entry。之后两个 NEW12 suite 均 PASS（最后 0.473s），最终 receipt 不计这次 harness 启动为实际 preflight 或 native 结果。

## 4. 实际 SOURCE 镜像与封件

[完整追加镜像](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/SOURCE_MIRROR_INPUTS.json>) **实际 127 项**：旧 92 每条保留原字段/bytes/SHA，新增 35：

| 新增 SOURCE 类别 | 数量 |
|---|---:|
| 完整 D4 十成员及其独立 seal | 11 |
| ROOT metadata 两捕获 | 2 |
| 旧只读审计 MD/JSON | 2 |
| 集中实际 SOURCE 诊断 | 1 |
| 诊断的精确 core captures | 15 |
| 审计已有引用：原质量元数据、两份 root/inner 诊断、B2 source_api 文本 | 4 |
| **新增合计** | **35** |

最后四项是只读审计引用，不接入 active runtime/import 链；尤其 B2 source_api 只作为原 ROOT 路由引用，不执行 B2 或添加 sensor/Phase1 runtime。SOURCE 镜像不包含模型、raw、静态 bank 或 SDK；完整实际树仍由未来原 prepare 按原规则验证和复制。

本包清单为 8 个成员及独立 seal：[SOURCE_INDEX](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/SOURCE_INDEX.json>)、本说明、mirror、test receipt、diff、NEW entry、小测试和 [SOURCE packager](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/build_source_v5.py>)。实际成员/根以 [seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/SOURCE_SEAL.json>) 与只读核验输出为准。packager 只做 SOURCE derive/hash/AST/JSON/seal，无运行时 consumer、资源 admission 或 dispatcher。

mirror 是两个 sibling project 的 workspace-relative 文本布局，**不等于 flat20 overlay payload**。flat20 来源与原 source_mappings 完整保留，父另行按原映射封装。新 8 成员与 seal 单独携带；全部外部文本 127 与本包 9 项的逻辑总数为 136，尚未把 flat20 的实际别名复制当作新增依赖。

捕获 JSON 内的原 Windows SOURCE 路径仅为 provenance；packager 对唯一 `F:/RMPOLAR-RL` 前缀作显式 workspace-relative 映射并核 pin，不做 basename 猜测或搜索。该处理只用于 SOURCE 引用，**不改或规范化 original runtime wire**。

只读核验命令（仅 SOURCE packager，不是 materializer CLI）：

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/build_source_v5.py' --verify
```

## 5. 父/CFF 后续接口保持

- 新 SOURCE kinds：`SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V5`、`SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V5`、`SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5`，版本字段 5；原 wire `GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1`、`STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json` 等保持 V1。
- materializer 的 `--source-index` 仍指原 sealed good20 SOURCE 索引，而非本包 SOURCE_INDEX；原 `--source-dir` 仍为完整 flat20。没有改参数、GROUP_PLAN schema、27 dependencies、3 retained conflicts 或 sidecar。
- strict actual wire：14112 / `a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1`；cached published SOURCE：14385 / `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0`；额外 canonical：`8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a`。canonical 等价不放宽 raw-wire pin。
- 原 typed publication 不变：全实际 copy/hash/fsync、独立 origin/retained/stream 证明和完整 metadata_validate 后，仅 runtime plan 的 enabled/staged 变 True；SOURCE receipt 的 staged/source_native_enabled/dispatched 仍 False。新增绑定仍仅 GROUP_PLAN_bytes/GROUP_PLAN_SHA256；original_plan_SHA 是原 wire hash。
- 完整 canonical7a092 alias 与 AppV6→dc4Base、20 overlays、27 原依赖/3 冲突保留、两角色完整 non-denied static banks/deps、原 helper/main/guards 皆保持。完整 8-role catalog，但仅 C878/S135 两角色实际构造，其余 6 deferred，H1 冻结/不构造。
- privateGPU_EX + finiteEX / C readonly / empty23500MiB / RAM96GiB / disk25GiB / wait1800 / ready900 / deadline2400，实际 p.wait、finally close/wait-before-unlock 和独立 outer wait 保持原 AST。未添加资源或批准字段。
- D4 全部封件保持原字节；三项历史实际 before-stage 失败保持历史失败。本包测试成功不重标历史失败，也不是 native/quality PASS。父完成独立 review/CFF 最小 pins 传播后，另立新目的、新 root 的实际预检；本轮没有自动 stage/dispatch。

## 6. 原技能保持优先，质量仍未新增实测

只用 actual0-update A1 fullcapture 内 embedded 原 teacher public mean；own container 与 mother teacher 身份分开。fresh WM/optimizer0 不称训练；旧任务的 N1024/seed/目标字段只作历史 producer 上下文，不转成 holdout 参数。STD/wholepi/Norm/freeze、完整 CPU history、one bytes/hash/decode、mother-open0、物理 N80 containment 不变。

C878/S135 两独立 holdout seeds20260929/20260930、每角色 N80/750 control、原 ascending/descending/standing、接受条件、plant/D0D7/reset/term-trunc/750actor/6000physics/1500feedback 全不改。质量证据仍 conditional per-direction/standing，不合并为整个技能90，不声明质量改进/非劣，不补造 E0/S50 predicates。原技能通过率/保持始终优先。

技能 catalog 已核对：当前仅 Office/ACL，无 RL SOURCE 对应；本任务使用 FSread/glob/grep 与 Python314 -B stdlib。全程无 SSH、SDK/Torch、真实 PT/model stat/hash/decode、raw/bank、GPU、C、锁、Git、旧封件编辑或旧测试重放；SOURCE seal 后只读核验。
