# B3：精确 typed 字段快照 + 有界 control 原子保留

**交付状态：SOURCE / own stdlib-Fake-API-AST，非现场准入。** `native_enabled:false / exact:false / Gate1:UNKNOWN / stage2_go:false`。未启动 SSH、SDK、GPU、原 worker、真实 PT、训练或 runtime stager；未读取 raw JSONL/canonical/锁，未修改旧封件、物理 DR、H1、mothers、acceptance 或 C2。

技能目录已匹配：本会话 Office/ACL 没有 RL 相关项，本任务使用文件 read/glob/grep 与明确允许的 Python314 `-B` 自有 stdlib 测试。

## 核心入口

- [passive_capture.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/passive_capture.py#L643>)：`install_passive_capture(...)` 先验证冻结 typed 依赖，再执行原 B2 preflight，最后安装原六个被动 wrapper；未知 wrapper / owner / source / MRO 不放行。
- [field_snapshot.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/field_snapshot.py>)：显式 `rows / ids / mask / state`；不按首维猜字段。`tensor_snapshot_adapter(..., witness_env_ids=...)` 返回 `FieldSnapshot`，不是旧 generic callable。
- [dependency_contract.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/dependency_contract.py>) + [CODEC_SOURCE_PINS.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/CODEC_SOURCE_PINS.json>)：对冻结 565 的 17 个函数、3 个 class/module、literal constants、defaults/kwdefaults、live compiled code 与 FieldSnapshot 5 个方法做安装前绑定；无 unwrap-skip。
- [SOURCE_API_CONTRACT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/SOURCE_API_CONTRACT.json>)：22 个组件/回调的精确 class/module/function、参数、sourceSHA/line；闭包名保留真实 `<locals>`。
- [SCHEMA.md](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/SCHEMA.md>)：字段 role、clock、自然 MID/END、reset/pre/post 与异常 pending-control 的完整语义。
- [SOURCE_DIFF.md](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/SOURCE_DIFF.md>) / [SOURCE_DIFF.patch](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/SOURCE_DIFF.patch>)：仅 3 个薄生产组件的 source 审阅差分；不应用到旧封件。

## 冻结 lineage，而非把旧 API 冒名升级

继承的 [source_api.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/source_api.py>) 与 B2 逐字节相同：31,456 bytes，SHA-256 `a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62`。四个原 published reset wrappers → 实际第一 MRO descriptor 的严格验证，以及原 preflight AST 完全保留。V3 只新增外层 capture schema。

只读复核的 [B2 SOURCE_SEAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json>)：2,909 bytes，SHA `be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a`，13 个成员全一致；其 [SOURCE_API_MANIFEST.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_API_MANIFEST.json>) 的 8-role 原 source 绑定继续由 caller 提供。

绑定的 [565 typed_capture_codec.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_codec_v1/typed_capture_codec.py>)：22,318 bytes，SHA `77c007fb0b17088b54bb0c115913159c7a9bf99f50f29a0b203dea483f0d1ee4`；其 [SOURCE_SEAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_codec_v1/SOURCE_SEAL.json>)：1,427 bytes，SHA `2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219`，7 个成员全一致，root `4ceeeda60cde6f8ca6cc496b8d299e5ea3b4ff2770b707f84898f06c1b75eec8`。未复制改写该封件。

## 父调用者的薄接点；这里不新增执行 loop

caller 应先让上述两个 source 模块路径可导入，并复核封件。真实安装使用公开 `install_passive_capture`；测试 fixture 中的直接 constructor 明标 `BYPASSED_ONLY_IN_OWN_FAKE`，不是 native 用法。

```python
from field_snapshot import tensor_snapshot_adapter
from typed_capture_codec import ControlLedger
from passive_capture import install_passive_capture

# All existing inputs. The adapter does not construct arange or read GPU indices.
snapshot = tensor_snapshot_adapter(
    EXISTING_TENSOR_CLASS, EXISTING_SAME_DEVICE_WITNESS_INDEX, 80,
    witness_env_ids=EXISTING_PYTHON_WITNESS_IDS_TUPLE,
)
ledger = ControlLedger(snapshot.codec, controls=64, run_id=EXISTING_RUN_ID)
tap = install_passive_capture(
    EXISTING_ENV, EXISTING_BRIDGE, EXISTING_FEEDBACK_MODULE,
    EXISTING_B2_ROLE_API, EXISTING_BRIDGE_PIN,
    snapshot=snapshot, ledger=ledger,
)

# Insert only around the parent's one ALREADY-EXISTING step and strict boundary:
tap.begin_control(EXISTING_CONTROL_INDEX)
# [parent's existing original step remains here, exactly once]
# [parent's existing strict boundary remains here, in original order]
tap.end_control(
    post_term=ALREADY_RETURNED_ORIGINAL_TERMINATED,
    post_trunc=ALREADY_RETURNED_ORIGINAL_TRUNCATED,
    source_ref=PINNED_ORIGINAL_POST_RETURN_SOURCE_REF,
    actor35=ALREADY_EXISTING_ORIGINAL_80_BY_35_BUFFER,
)

# Outside the control loop, after successful original controls only:
owned = tap.finish()
# Optional outside-loop export only; no cast, no dtype/shape loss:
json_ready = snapshot.codec.materialize(owned)
tap.close()
```

上例不包含新 step/obs/reset/getter/RNG。若原 step 抛出，保留并传播原 exception；outside-loop 使用 `tap.report()` 取 `incomplete_current_control`，不伪造 post flags 来强行 `end_control`。metadata 函数故障仅记 observer error / UNKNOWN，不替换原回调的返回或异常对象。begin/end/finish 的 observer failure 返回 UNKNOWN 并标记失败；这些不是可继续声称有效采集的准入票据。

## 实际完成的 30 项 own 测试

[最终 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/STDLIB_FAKE_TEST_RECEIPT.json>) 与 [完整测试名/log](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/STDLIB_FAKE_TEST_LOG.txt>)：Python 3.14.3 `-B`，30/30，0 error/failure/skip；unittest 8.262s，总 8.3357034s。target_modules=[]；target import、network/process/native/signal、PT/rawJSONL open attempts 均为0。

覆盖：

- full IDs K=0/1/79/80 的原 int32 dtype 与完整长度，不被 witness index 选成8；full80 bool 非 witness 第79终止/第78截断。
- 5通道×MID/END 的自然10记录；同 tick原 cache复用；原 clean16 / 已用noise / delay queue before/after；debug rings 为0也保留科学记录。
- fake untapped/tapped 6controls 原 actor值/queues/private+global RNG/call counts 相同（90 raw/sensor/delay、6 observe、6 pack）；这是 fake 比较，不是 native bitwise。
- 64controls/640normal，中间第37控制 reset 不丢；128controls/1280normal 与 K79/K80 边界不丢，第129控制上下文失败且不调用 step。
- 原六 callback 的一次调用、入参/返回 identity、异常 identity；原 reset partial-after RAISED 完整 IDs、pending owned evidence；metadata失败不会 masquerade 为自然无 reset；duplicate 标 INCOMPLETE。
- callback内 CPU/tolist 为0；outside-loop materialize 才执行；缺 actor、错误shape、缺自然 sample 均不补造。
- freeze/sourceSHA/line/default/constants、未知 wrapper、foreign codec、used ledger、invalid witness声明等负例；失败在原 preflight/赋值/MDP调用之前。

复跑默认 stdout-only，不改 receipt：

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B run_stdlib_tests.py
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B verify_seal.py
```

## 分开记录现场证据

本封件没有真实 Torch CPU、SDK、GPU、原 worker、自然物理 reset 或 untapped actor35 bitwise 结果，所有 actual/native flags 维持 false/UNKNOWN。

PARENT_REPORTED（2026-11-04 03:35:55，未由本 child 读取报告）：父会独立 actual Torch CPU 验证的是 565 codec / synthetic ledger，报告为 [PHASE1_TYPED_CODEC_ACTUAL_REAL_CPU_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_TYPED_CODEC_ACTUAL_REAL_CPU_V1.json>)；该消息不是 B3 适配器的真实 Torch 或 SDK 证明，不改写本封件 receipt/准入 flags。B3 后续 CPU/现场 binding、真实动作/队列/RNG call counts、actor35 equality 与原资源小窗接口验证仍由父会独立完成。
