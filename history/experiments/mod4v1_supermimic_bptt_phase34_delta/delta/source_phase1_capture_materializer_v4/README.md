# Phase1 materializer V4 — PENDING_FINAL_WORKER4_PINS

当前仅为最窄 SOURCE 差异/闭包模板。最终 worker4 seal/index/root pins 尚未由父 agent 交付；没有生成 V4 entry/helper/mirror/index/seal，没有 ready 声明，也没有 prepare/preflight/stage/dispatch/native 操作。原 V3 和 good holdout V2 封件保持固定。

技能 catalog 仅 Office/ACL，与本 RL SOURCE 任务无匹配；采用 FS read/glob/grep＋stdlib/AST。此任务不读 actual reports、不使用 SSH、SDK/Torch/PT/raw/GPU、C ledger、锁或 Git。

## 待绑定接口

[derive_materializer_v4.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/derive_materializer_v4.py>) 的 `FINAL_WORKER4=None` 是 SOURCE 派生的待绑定值，不是新增 native approval gate。它只接受父 agent 最终提供的：

```python
FINAL_WORKER4 = {
    'seal': (EXACT_BYTES, 'EXACT_SHA256'),
    'root': 'EXACT_COMPLETE13_CANONICAL_ROOT',
    'index': (EXACT_BYTES, 'EXACT_SHA256'),
}
```

待最终实际字节读齐后，才核验完整 13 seal、typed V1 index＋source_version4、5 candidate 源、原17/B2/C8/adapter10/partition9/C182 和实际所有额外 source references。不猜浮动 SHA，不把文件存在当作 active 证据。若最终 schema/成员数/源闭包不同，显式报告差异，不放宽既有集合检查。

## V3 全文作为唯一派生基线

- [封存 V3 entry](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py>)：42437 bytes / `2a4213d95939216f3a91db6c1739a443907aadf33c4f615aa897eace5a915425`。
- [封存 V3 helper](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v3/static_source_helpers_v1.py>)：完整原 17 helpers，10078 bytes / `11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2`。
- V4 无新增 runtime/闭包 helper。仅 `load_sources/metadata_validate/preflight_summary/stage` 中来源、版本与 SOURCE 标签的必要传播；其余完整函数 AST 不变，stage 仅 SOURCE kind 变化。
- `normalize_B2_source_paths` 与 `verify_B2_source_closure` 的完整 AST 不变。完整原 B2 manifest 435 refs/155 Python＋4 routing JSON＋diagnostic final/4 refs，共 164 真实来源输入，先验原 raw SHA，再调用原 SOURCE API build_manifest(root=actual mirror)，只显式 source_path 根正规化。
- 保留完整 8 runtime/static-bank/deps、27 原 worker_files、完整 vendor7、独立 pre-overlay input_path/readbytes/hash 库存、冲突 retained mapping、实际 stream observations、相同真实 bootstrap、AppV6→dc4Base。
- 不硬编码镜像文件数量为旧 313；最终 SOURCE_MIRROR 必须按 V4 实际输入＋派生/回归所需文本闭包重建。隔离 mirror 测试仍禁止回读原 R。

## 原 wire、资源与假设边界

ROOT_PREFIX `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_`、`STAGE_COMPLETE_PHASE1_CAPTURE_V1.json`、typed plan/task/purpose、controller/原 parent 都不改。E3-only/N80/64或128 controls、synthetic zero6/PT0/无训练无质量结论、原 physical/DR、privateGPU EX＋finite EX/C readonly/原 waits/deadlines 保持。

父 agent 报告 V3 live failure；本任务没有读取该 actual report。`env.device` 与原 core Tensor.device 比较的表示差异仅是父提出的 SOURCE/CPU 待核假设，不冒充已发布实际 flags 类型/shape。V3 source 当前 worker126 为 `OriginalEpisodeBoundary(torch,env.device,n=80)`；若最终 worker4 只改用现有 `bridge.device`，将对完整 worker bytes 作精确一行投影、其他四 candidate 全 bytes 相同检查，但不执行 worker/SDK 或重写原 boundary。最终 CPU fixture 与 native 结果须各自保持证据层级。
