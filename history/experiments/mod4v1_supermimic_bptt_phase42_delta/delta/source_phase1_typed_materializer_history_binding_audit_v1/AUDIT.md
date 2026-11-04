# Typed 材料器历史 B2 / active B4 reference 绑定审计

## 确定结论

确认 **1 处 history-successor 错绑**： [V1 完整阶段模块:279](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/stage_phase1_typed_capture_v1.py#L279>) 在 `verify_B2_source_closure(source_root, index)` 中，把历史诊断 handoff 的 B2 seal 与 `DEPENDENCY_SEALS['sensor']` 比较。冻结 V4 此项为 B2；typed V1 正确把 active sensor 升为 B4，却原样保留了整个历史函数 AST，因此两个正确 publication 被错误地要求相等。

完整模块、全部 `DEPENDENCY_SEALS` AST 引用及后续固定条件审查中，未找到第二处同类 selector 错绑。这不代表所有后续真实文件、inventory、环境和资源约束已通过。父会实际 Linux 失败是 **PARENT_REPORTED**；本审计未打开实际报告、未重放已消费 `_SOURCE_INPUT`。

## 两个独立 reference，不互相替换

| reference | 独立 published raw seal | 成员 / index / SourceProof |
|---|---|---|
| 历史 B2 | [原始 B2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json>)：2909 bytes；`be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a` | 13；[typed index:2915–2986](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_native_capture_v1/CAPTURE_SOURCE_INDEX.json#L2915-L2986>) 的 `original_B2_reference_seal`；`phase1_source_proof/original_B2_reference/` |
| active B4 | [B4 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json>)：3824 bytes；`81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3` | 21；[typed index:841–953](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_native_capture_v1/CAPTURE_SOURCE_INDEX.json#L841-L953>) 的 `dependency_seals.sensor`；`phase1_source_proof/sensor/` |

[历史 SOURCE handoff:12–83](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_sensor_reset_identity_diagnosis_v1/FINAL_SOURCE_HANDOFF_RECEIPT.json#L12-L83>) raw 3991 bytes / `238ef8f8ecd99383f91d3d474cbae3a409a16f9ec56e8e49f2c56e5b9b523c99`，明确声明 B2 2909 / `be538a07…`。其 13 个 member rows 与独立 published B2 完全相同；另四份 diagnosis SOURCE 引用均核对实际字节。原 B2 `content_root_sha256:null` 保留。

[V1:123–129](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/stage_phase1_typed_capture_v1.py#L123-L129>) 已有历史 B2 独立 raw literal＋完整 package13＋index listing hardpin；[V1:111–122](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/stage_phase1_typed_capture_v1.py#L111-L122>) 是正确的 active B4 package21 检查，必须继续严格保留。期望值不取自任意 handoff claim，不从 live successor 推导。

## 完整 selector 与后续条件审查

所有实际 `DEPENDENCY_SEALS` AST 用处只有同一阶段模块的 **21 Store、111 Load、112 Load、279 Load**。派生脚本中另有历史替换文本，但不是实际运行 selector。

逐段固定假设清单见 [SOURCE_AUDIT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_materializer_history_binding_audit_v1/SOURCE_AUDIT.json>) 的 `complete_remaining_fixed_assumptions`：

- 198–269：B2 路径归一化、336133 原 manifest、435 refs／155 全 Python、四份 routing JSON、31456 原 API、真实原 builder／namespace restoration。B4 API 与 B2 原 API **整文件相同** `a334766d…`，这项跨包复用没有第二处语义错绑。
- 270–289、188–195：历史 handoff＋四引用、164 dependencies、SourceProof aliases。唯一错位是 279 的 seal selector。
- 292–369：原 Admission2 closed provenance、独立 origin、动态旧字节 relocation、observed SHA、八树／assets／workers／vendor7。原实际资源与三个 source 冲突仍是父会未来证据，本审计不代证。
- 372–433：new-root／原 prefix／GPU／非重叠／64|128、原 9-to-8 catalog、完整 vendor7、baseline bootstrap、34 aliases、64MiB。原 E3 controls160 是原 catalog 定义，与新 capture64|128 分属不同字段。
- 436–530：完整 metadata guards／AppV6→Base／core／34 aliases／ROOT==HERE／六 typed deps／原 bootstrap／make_task；实际环境与 blocked-module prestate 仍是原约束。本次未执行 metadata。
- 533–578：全 stream SHA→fsync→observed retained→GROUP_PLAN→actual-root metadata→原 completion；失败消费 root；原七 CLI 参数与 mode、control bounds 全保留。
- [typed support:34–229](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/typed_source_support_v1.py#L34-L229>)：固定396显式 R/T、finite34、wire、active B4 精确 patch triple、baseline2、实际 make_task control bound；未见其它 history-successor selector。

## 本次独立字节核验（不是 loader execution）

- 全 **396** declared realSource：R395＋T1 实际字节／SHA 通过，所有已声明 Python AST 解析；旧 V1 28 members 与 seal 仍完全相同。
- 完整 B2 manifest 静态遍历 **435 refs／155 unique whole Python**；所有 hash rows 与 index 和实际 source 一致。原 C1 **182** source pins 另核。
- 独立组装并核对 **272 SourceProof aliases**，logical SHA256 `f74f7e5fa02931f155bb55930f35f835f61a28cc7941cb94058c46968a8c6324`。
- 包括32 overlay＋index 的 **305** source mapping aliases，logical SHA256 `cb8bc8d40e69ef5d8d3c5ed4cab6b24aff2cd1c945cac24fff93178c7678d21b`。这不是八树完整 baseline 或 native vendor 实测证明。
- 一次长 inline 命令在执行前被 shell-source parser 拦截，后改用可分析的 literal CLI。一次自有审计 helper 错把合法 C1 relative key 当 absolute provenance，产生 `AssertionError`；修正自有数据解析后完整 proof PASS。均未调用生产函数；详情保留于审计 JSON。

## 最小 NEW V2 边界

只修历史 B2 selector：独立固定 published B2 raw bytes/SHA＋完整13 SourceProof＋index/handoff 一致性；active B4 package21 始终严格。旧 V1、B2/B4、diagnosis handoff、Producer15、finite34、TaskABI、物理／DR／H1／mothers／acceptance、roots／CLI、17 helpers、所有未改整函数、copy/fsync、origin/observed、App/Base 与原资源 close 均保。

仅新增 4–6 个 own AST／memory selector／history-vs-active 负例；不跑旧9、不调用 whole prepare/metadata/SSH/native。先交 exact complete-function diff 与双 reference 证据供父会审核，再封 NEW V2 metadata；不动父会 final13。

本审计 actual loader／B2 builder／prepare／preflight／metadata／stage／parent／实际报告／SDK／Torch／PT／raw／C／lock／Git 均 **0**；`native_enabled:false / exact:false / Gate1:UNKNOWN / stage2_GO:false`。
