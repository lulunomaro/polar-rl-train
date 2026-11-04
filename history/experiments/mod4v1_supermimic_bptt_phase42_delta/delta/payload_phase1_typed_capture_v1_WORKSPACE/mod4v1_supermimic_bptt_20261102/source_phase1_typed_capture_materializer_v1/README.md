# Typed capture materializer V1 — SOURCE only

## 交付状态

这是冻结 V4 材料器的完整派生，不是 native capture 现场凭据。最终九个自有 stdlib/AST/own-temp cases 全部通过；未运行实际 prepare、preflight、stage、父 entry、SDK、Torch 或训练。`native_enabled:false`、`exact:false`、`Gate1:UNKNOWN`、`stage2_GO:false` 保持。

- [材料器](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/stage_phase1_typed_capture_v1.py>)：48,397 bytes / `0fbaad211b341c0d5cce5a429a1832c02230b2cfdfc15fb9100576514477c00b`。
- [Source index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/SOURCE_INDEX.json>)：完整依赖/别名/函数/未来 CLI 声明。
- [显式 R/T mirror manifest](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/SOURCE_MIRROR_INPUTS.json>)：396 个去重文本 SOURCE 文件，R=395、T=1；原 R mirror 的 332 行逐项原样保留。
- [最终九例 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/SOURCE_TEST_RECEIPT_attempt4.json>)：9/9、12 个真实 task/plan 负例、六个实际受测自有源码 pins；全部旧 407 个文本 SOURCE 输入 before/after 相同。
- [全部 attempt 与修正记录](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/FAILURE_RECORD.json>)：前两次失败与后两次通过均保留，未把自有 harness/helper 问题归给 Producer。
- [完整函数差异](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/FUNCTION_DIFF.json>)、[完整文本 diff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/SOURCE_DIFF.txt>)、[Source seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/SOURCE_SEAL.json>)。

## 1. 完整 V4 派生与不变边界

原冻结材料器为 45,850 bytes / `f3059d24444c40873f2d55aeb22fd82e32284e761db96250ec985314080c6507`。保留全部 14 个 top-level functions，不取 AST 方法片段拼接 runtime。七个完整函数 AST 相同：`canonical`、`reference_path`、`normalize_B2_source_paths`、`verify_B2_source_closure`、`native_boundary`、`retain_originals`、`validate_preservation`。另外七个仅处理 typed source loader、metadata、manifest/receipt、plan schema 与 CLI 必需差异；四个嵌套 metadata guards 和 try/finally 清理顺序保持。

[共享 helpers](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/static_source_helpers_v1.py>) 全 17 个完整函数、10,078 bytes / `11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2`，与 V4 整文件相同。`tree` 对 model/raw/operational 名称的排除先于 stat/classify；没有 PT 跟随。原 physics/DR/H1/mothers/acceptance、原 parent wait/close/resource/GPU/fd/deadline 逻辑均保留；未加入审批、账本或资源准入条件。

## 2. 有限 34 与完整 baseline 是两回事

冻结 Producer 的 finite34 = original17 + producer5 + dependencies9 + bootstrap2 + ABI1。其中 **32 个 overlay + 2 个独立 baseline-authoritative bootstrap**；不是把 34 个全变成 overlay。两个 bootstrap 的来源仍是完整原 V8 input inventory，既要保持原输入路径/字节证据，也要与冻结 Source pins 相同。R discovery 副本或 T 源文件不是替换 baseline 身份的借口。最终所有 34 个 installed aliases 均做实际 bytes/SHA/AST 核对，包含 ABI 和两个 bootstrap，而非只依赖原 `validate_plan` 的 31 个 required mappings。

未来 `prepare` 仍必须取得完整原 V8 `worker_sources`、`pinned_assets`、八角色完整 runtime trees、全部原 worker_files、静态 NPY/NPZ、native vendor7 与两个原 bootstrap。155/182 个 Python closure 或 finite34 都不是静态 runtime/bank inventory 的替代品。

独立 original origin 输入路径、sorted logical digest、按实际冲突动态建立的 `worker_sources/phase1_retained_original/`、实际 stream hash/fsync/observed preservation 均保留。没有硬编码“只改三个旧 alias”。本次 own fixture 实测冲突为 1；该数字不是未来完整 input 的冲突数。

## 3. R/T Source mirror 与两个外部 patch proof

`--source-root` 是显式 R mirror 根，`--t-source-root` 是显式 T mirror 根。T 仅核对既有 `NINE_N80_PARALLEL_SOURCE_V8/n80_gpu_capacity.py`：653 bytes / `ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc`。不扫描 T tree；Windows 路径仅作冻结 provenance，缺少 mirror 输入即失败，不退回 F 盘。

新 manifest 包含 Producer 15+seal、B4 21+seal、codec 7+seal、C2 5+seal、原 B2 全 13+seal、原 C1/adapter/partition、B2 全 155 文件/435 refs/164 source inputs、C1 全 182 原源及所有 index source 引用。原 CODEC pins 指向 V3 field source 的那条路径也保留，虽然 B4 对应文件字节相同。原 B2 声明的 `root:null` 原样保留。

仅有两份外部 patch proof 获 package seal + exact relative member + raw bytes/SHA 的三重白名单：B4 `SOURCE_DIFF.patch` 8,378 bytes / `d59e5c2587e93d057c5b9c3498ddfb6b28fdeeecb15189880210de4bb3565fa3`；C2 `C1_TO_C2_SOURCE_DIFF.patch` 6,231 bytes / `fe80994ac0db9e24e89a40138b6a62d6825c1bd0c794c9b8c2183a51676b9793`。它们仅供 SOURCE read/hash/未来 Source 目录复制，**不是 runtime 依赖，也不执行 patch**；未扩大 runtime/static 或模型/operational 白名单。历史 report/PT 字符串只是 provenance，相关真实文件未读。

## 4. 完整模块 metadata 检查

使用完整实际 AppV6（27,769 / `3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39`）、真实 Base（22,337 / `dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7`）、完整 core（37,927 / `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e`）正常 metadata import；没有 AST crop/stub，不调用构造器、main、storage、capacity、close/wait 或 task_args/admission。原 parent 9,336 / `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41` 整文件未变，仅做 AST/字节绑定。

先核对实际 supplied plan 经真实 `make_task -> validate_task`，再核对真实 64/128 task 正例与 12 个负例。原 `validate_plan` 自身不拥有 controls 边界；该边界由原 prepare 和真实 task validator 保证，不假称 plan validator 单独检查了 controls。

Source own-temp 的模块路径严格 `ROOT==HERE`；未来实际 stage 另调用完整实际 runtime 的固定 B/tasks root validator。本次未访问实际 B 目录或继承 EX fd。`full_safe_module_names` 只列实际 loaded namespaces；较宽的 `namespace_cleanup_watchlist` 单列，旧 C1 cleanup 名称不是已执行 typed C2 依赖的证明。

## 5. 九例范围与结果解释

九个 unique own cases：完整函数/helpers/parent；finite34/typed wire；显式 R/T 与缺失/坏输入/分类前排除；完整 App/Base/core/typed 模块及 64/128 task；缺失 Base/坏 alias bytes；完整 runtime ROOT/HERE；独立 origin/动态 retained old bytes；own-temp stream SHA 与 tamper；精确 patch 三重 pins 与完整 stage AST 次序/B2 null。

最终 attempt4：9/9，通过时间 0.9090480000013486 秒；审计事件为空；407 个旧文本输入 SHA 全相同。原 44/63/10 suites 未运行。own fixture 的八树、opaque NPY/NPZ、asset/vendor descriptors 只验证代码协议，**不构成实际 V8 baseline/vendor7 已复制或现场已验证的凭据**。实际 SDK binding、actor35 equality、真实 call counts 与 Gate1 仍待父会在新的资源准入小窗验证。

## 6. 未来 CLI — 本子会未执行

以下仅供父会后续新用途使用。`NEW_GROUP_ID` 必须是尚未消费的新名称，保留 `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_` 前缀；可在其后包含 `_TYPED_V1_`。原 consumed roots 不复用。Source 包的工作目录与 R/T mirror 根是独立值，不猜 Linux 安装位置。

```bash
B='/home/lc01/Zonglin Li/zonglin2'
# 以下变量由父会实际新用途填入；不是本次执行参数。
# PYTHON=/absolute/python
# M=/absolute/installed/source_phase1_typed_capture_materializer_v1
# R_SOURCE_ROOT=/absolute/explicit/R/source-mirror-root
# T_SOURCE_ROOT=/absolute/explicit/T/source-mirror-root
# NEW_GROUP_ID=MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_<NEW>_TYPED_V1_<NONCE>
# GPU_UUID=GPU-<actual-original-resource-UUID>

"$PYTHON" -B "$M/verify_source_seal_v1.py"

"$PYTHON" -B "$M/stage_phase1_typed_capture_v1.py" \
  --original-group-root "$B/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700" \
  --source-root "$R_SOURCE_ROOT" --t-source-root "$T_SOURCE_ROOT" \
  --native-root "$B/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000" \
  --new-root "$B/tasks/$NEW_GROUP_ID" --group-id "$NEW_GROUP_ID" \
  --gpu-uuid "$GPU_UUID" --controls 64 --preflight-only

# 父会另行确认新用途后，在同一尚未创建的新 root 使用原参数与 --stage，
# 或另取未消费 root；不是本子会的实际执行命令：
"$PYTHON" -B "$M/stage_phase1_typed_capture_v1.py" \
  --original-group-root "$B/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700" \
  --source-root "$R_SOURCE_ROOT" --t-source-root "$T_SOURCE_ROOT" \
  --native-root "$B/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000" \
  --new-root "$B/tasks/$NEW_GROUP_ID" --group-id "$NEW_GROUP_ID" \
  --gpu-uuid "$GPU_UUID" --controls 64 --stage
```

`--controls` 仅 64 或 128，两个 mode 二选一。原 `NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN` 保持。未来完成顺序仍是完整 metadata → 全量 copy/hash/fsync → actual stream/observed preservation → GROUP_PLAN → actual-root metadata/ROOT==HERE → 最后 completion。`STAGE_COMPLETE_PHASE1_CAPTURE_V1.json` 只有在全部成功后才写 `materialized:true`、`parent_launches:0`；它不等于 native acceptance。失败会消费该 root，并保留原失败处理。

## 7. 源码工具分工

[typed support](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/typed_source_support_v1.py>) 是小型镜像/ABI/alias/task metadata 支持；[完整派生脚本](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/derive_materializer_v1.py>)、[mirror publisher](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/build_mirror_manifest_v1.py>)、[index publisher](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/build_source_index_v1.py>) 是已完成的一次性 SOURCE 生成记录，以 exclusive-create 写 NEW 产品，封印后不重跑覆盖。后续只读 Source 包核对使用 [seal verifier](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/verify_source_seal_v1.py>)；它仅 hash/AST/JSON，不导入或执行材料器 entry。
