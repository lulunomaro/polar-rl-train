# Phase1 E3 passive capture：最小 SOURCE materializer V1

## 交付与当前状态

- 主入口：[stage_phase1_capture_v1.py](stage_phase1_capture_v1.py)。仅 stdlib；显式 `--preflight-only` 或 `--stage`，无进程启动功能。
- [static_source_helpers_v1.py](static_source_helpers_v1.py) 的 **17 个完整函数 AST** 与原 bound-only stager 一致；[derive_static_helpers_v1.py](derive_static_helpers_v1.py) 为窄的确定性提取器，不执行旧 stager。没有摘取函数中的部分逻辑或裁剪源模块。
- [test_materializer_stdlib_v1.py](test_materializer_stdlib_v1.py) / [TEST_REPORT.json](TEST_REPORT.json)：23 个真实文本 PIN / stdlib fake 静态树 / 完整 AST 测试；**actual prepare / actual preflight / stage / parent / native worker 调用均 0**。fake bank 是自行创建的带显式 FAKE 标记的字节，不是真实 raw/NPY/NPZ 数据。
- SOURCE manifest、输入 source mirror 清单与本目录 seal 由 [build_source_manifest_v1.py](build_source_manifest_v1.py) 产生；source-only 构建/验证不扫描实际 original/native 静态数据树，不调用本 CLI 的 `prepare`、`stage`、`main`。
- `gate1='UNKNOWN'`、`capture_interface_passed=False`、`exact=False`、`stage2_GO=False`。源码、metadata import、file materialization 和 native binding 是不同证据层；这里没有新的技能质量结果。

## 固定语义，不转换旧任务目的

唯一 purpose：`NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN`；plan kind：`PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1`。仅 E3 作为未来执行成员；保留完整 8-role catalog，另外 7 项 deferred，H1 不构造。E3/N80，`--controls 64`（默认）或 `128`，synthetic zero6、PT reads 0、train False、quality False。旧 E3 `controls=160` 定义留在原 role 元数据中；新 `capture_controls` 单列，绝不把这次有界 probe 说成原技能评测。

保留 seed 20260928、原 DR/物理/资产、one-reset/true term+trunc/原 callback 次序。真实 entry 为原 formal E3 reset53 → fall/publish55 → original compute66；桥初始化一次、teacher=None，B 后 C 安装，反向 C→B→bridge→env→完整 AppV6/Base 关闭。首个 66 可能是 same-tick cached，因此没有 clean0 / Gate1 通过推断。没有重放旧 once-CPU 脚本。

原 parent 17–44、46–78 行资源块仍与 bound-only parent 完全一致；2400 deadline / 1800 wait / ready900 / private GPU EX + finite EX / C readonly 等不移入本 CLI，也不重写。训练侧既有 3900–3600–300 / reserve 86412.86069250107 不变。没有新增 manual-review / CONFIRMED bool、C writer 或第二套锁。

## 固定来源与完整闭包

Worker 最终 13 封件：`SOURCE_SEAL.json` 2537 bytes / SHA256 `3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7`，content root `d792dce3f110fe5fdfe30ded8840da657c22c72eaac42f60093cbe814c095028`。

最终 `CAPTURE_SOURCE_INDEX.json` 57198 bytes / `234f8a3d0baf2a84338e9a0bf2170510f99d33c416654bf23b47bc3b5b5aa5ad`。完整 active mappings = 原 17 + NEW 5 + dependency 5。B sensor13、C actuation8、adapter10、partition9 的 seal 及全部成员逐字节验证；C 引用的 182 original-source PIN 也实际校验。这些都是文本源码/metadata，不是模型或 raw。

`--source-root` 指 **R 的 source-only 镜像根目录**，不是 flat27 目录。输入清单 [SOURCE_MIRROR_INPUTS.json](SOURCE_MIRROR_INPUTS.json) 逐项列出镜像必须保留的 `relative` / bytes / SHA256。固定 index 内的 Windows `F:/.../mod4v1_supermimic_bptt_20261102/...` 只作来源；程序将唯一 R marker 后的安全相对路径接到显式 source-root。越界、缺件或错 PIN 硬报错，不猜别名、不用占位模块。父外层 actual-wait controller 是另一个独立 payload，不追写进 worker 的 13 封件或本 worker index。

未来实际准备必须同时具备：

1. 完整原 V8 group（`MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700`）的真实原 plan、全部原 `worker_files`、完整 `worker_sources` / `pinned_assets`，以及八角色完整 runtime 静态树（含原 static banks / NPY / NPZ / assets / deps）；不是小截取或仅 Python 文件列表。
2. 原 Admission2 source root（`MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000`）的真实 OWNER_PLAN / OWNER_EXIT_ACTUAL / COHORT_FINAL 闭合元数据，以及 E3 完整 vendor7。vendor7 tree pin 为 `ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`，`__init__.py` 保留完整原 docstring，不造 stub。
3. 上述完整 source-only R mirror；canonical `a1_frozen_eval_runtime_v2.py` 保留 7a092 别名，NEW runtime 别名独立；完整 AppV6 → `resume_runtime_contracts_v3.py` dc4Base 必须同时在。实际 metadata import 层为完整 stdlib-safe worker/runtime/observer/core/helper/pose/App/Base/B/C APIs；原 parent、native bridge、vendor Torch modules 是完整 PIN+AST 保留层，不导入其 native 层，不做 Torch/Base stub。

原文件名过滤仍在 DirEntry 分类前执行：模型后缀与 operational/raw/lock/private 等条目跳过，不为判断是否保留而 stat/open 模型。其余许可静态文件全保留，NPY/NPZ 后缀不是裁掉 static bank 的理由。PT0 路径不走 producer FINAL / checkpoint 描述符 / old A1 actual0 capture，不开 mother/PT，不把 fresh WM / optimizer0 当训练。

## 独立原 bytes inventory 与 overlay 冲突

单靠两份相等的 `baseline` / `installed` 不是原 bytes 来源证明。程序首先从实际输入扫描并读完每个许可文件，独立保留：

- 原 logical alias、真实 `input_path`、该完整内容的 `bytes_read`（一次完整 identity 内容长度，不是累计磁盘 IO 计量）、bytes、SHA256；
- 原 source root / native root、原 plan 的真实字节 SHA；
- 全部 original logical rows 的 canonical SHA256、唯一 alias、完整八 runtime / asset / worker / vendor7 包含性。

原 17 overlay 与 V8 三个 active alias 存在内容冲突时，**active alias 不动**，原输入 bytes 只改存储位置到：

```text
worker_sources/phase1_retained_original/<original logical alias>
```

记录 `source_to_retained`。相同 bytes 不重复复制；实际不同的 bytes 才有 retained alias。原 logical tree digest 在 overlay 之前计算，baseline 对应保留后的每一个实际存储 alias。未来 stage 用每一实际 stream copy 的 SHA/bytes 观测重建 `installed`，再核对独立 original inventory；不是复制 baseline 数组就声称实际已安装。vendor 与已存在的不同原 static alias 异常重叠时直接报错，避免静默覆盖原 bytes。

23 tests 含三冲突正例、同 bytes 不重复、伪造两个相等数组、缺原 inventory、错原路径/read bytes、丢保留原 bytes、错 relocation、错实际 stream hash，以及 Unicode alias 对齐原 contract 的 canonical JSON digest（sort_keys / compact separators / ensure_ascii=True）。fake vendor/static 正例不构成真实 vendor7/assets 完整性证据。

## 未来命令接口（这里没有执行）

必须用全新、尚不存在且父目录已存在的 group root，basename 与 group-id 一致，prefix 固定 `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_`。source / original / native 与 output roots 不重叠。

```bash
python3 -B stage_phase1_capture_v1.py \
  --original-group-root /ABS/ORIGINAL_V8_GROUP \
  --source-root /ABS/SOURCE_ONLY_R_MIRROR \
  --native-root /ABS/ORIGINAL_ADMISSION2_ROOT \
  --new-root /ABS/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_UNIQUE \
  --group-id MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_UNIQUE \
  --gpu-uuid GPU-EXPLICIT-HEX-UUID \
  --controls 64 \
  --preflight-only
```

`--preflight-only` 实际只做来源/PIN/完整静态树清点与完整 metadata import；不创建 new-root、不修改输入。import 用系统 tempfile 的临时 **纯源码视图**，完成后核实绝对目标再清理；fake tests 用 stdlib 的 scratch routing 限定到本 NEW 目录。无 parent/worker main、无 FD inspection/admission、无 SDK/GPU/C/锁。

将最后一个参数明确换成 `--stage` 才执行文件物化。它不调用控制器、不启动 parent、不做 resource admission。以 `xb` 独占写、逐文件 streaming hash，完成 plan / 实际 installed inventory / 再次完整 safe metadata import 后写固定 receipt：

```text
STAGE_COMPLETE_PHASE1_CAPTURE_V1.json
  purpose = NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN
  materialized = true
  parent_launches = 0
  GROUP_PLAN_bytes / GROUP_PLAN_SHA256 = actual serialized plan identity
```

这是父外层 actual-wait controller 要 pin 的确定 fileops 接口。`source_native_enabled=False` / `staged=False` / `dispatched=False` 保留为非 native 状态；controller 不靠这些含混 flag 推断物化或 actual SDK 执行。preflight summary 的 `materialized=False` / `parent_launches=0`。未来外层 parent actual Popen→wait 与 nativeGate1 是父自己的后续步骤。

中途出错仅记录 error，已创建的根按 consumed 处理，不删除或重用它；success receipt 不提前写。这里不带 dispatcher / 自动 stage / GPU / SSH / SDK / Git / C writer。

## SOURCE 复验与 seal

```text
python -B derive_static_helpers_v1.py
python -B test_materializer_stdlib_v1.py
python -B build_source_manifest_v1.py
python -B build_source_manifest_v1.py --verify
```

最后一个是只读 seal verify；其余也只处理本 NEW source 产物与被 PIN 的文本，不是实际输入 preflight。测试报告不含随机时间；seal 后不再改已封源码、测试或文档。CLI 真正的实际 inputs preflight / stage 仍留给父自己的 review 后独立动作。SOURCE seal、metadata CPU PASS、file materialized 与 native/SDK/质量通过保持分层。
