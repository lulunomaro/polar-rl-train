# B2 → B3 source-only 小差分审阅

完整差分仅作为 source 审阅材料：[SOURCE_DIFF.patch](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/SOURCE_DIFF.patch>)。B2 seal 与其 13 个成员均只读核验；未应用该差分。

## 保持原样

- [source_api.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/source_api.py>)：31,456 bytes；SHA-256 `a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62`；与 B2 逐字节相同，四层原 reset + endpoint MRO/source/code 校验保留。
- [fake_runtime.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/fake_runtime.py>)：原 stdlib fixture 字节相同，不代表真实 SDK。

| 原逻辑 | B2 行 | B3 行 | AST equality |
|---|---:|---:|---|
| `stdlib_snapshot` | 20 | 22 | identical |
| `BoundedRecorder` | 57 | 37 | identical |
| `_same_callable` | 124 | 104 | identical |
| `_plain_scale` | 130 | 110 | identical |
| `_root_asset_configuration` | 139 | 119 | identical |
| `preflight` | 154 | 134 | identical |
| `_preflight_impl` | 168 | 148 | identical |
| `PassiveCapture._clock` | 309 | 595 | identical |
| `PassiveCapture._patch` | 327 | 607 | identical |
| `PassiveCapture.close` | 466 | 615 | identical |

## 生产变更，仅 3 个薄源组件

1. [field_snapshot.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/field_snapshot.py>)：替换按首维猜测的 generic snapshot；ENV_ROWS / full IDs / full bool80 使用显式入口。
2. [dependency_contract.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/dependency_contract.py>)：冻结 565 真字节绑定；17 个 codec 函数 + 5 个 FieldSnapshot 方法，class/module/sourceSHA/live code/defaults/无未知 wrapper。
3. [passive_capture.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/passive_capture.py>)：六回调原函数一次、原 return/exception identity；科学保留独立于 debug rings；父 begin/end 只传既有输入；有界 pending-owned 控制保留原异常/metadata 失败下的 IDs 与部分状态。

原 call-site 数量（feedback 的 foreign-env 与 target-env 两路互斥）：`original_feedback=2; original_sensor=1; original_delay=1; original_update=1; original_term=1; original_reset=1`。参数原样转发，无新增 sampling、step、reset、getter、RNG、CPU export、文件 IO 或信号。

default joint pos/vel、scale/order、source dtype 继续由原 source API/manifest 约束；无 zero-default 或 quaternion 顺序推断。队列、动作、物理 DR、H1、mothers、acceptance 均未变更。V3 外层 schema 独立版本；继承的 source_api revision 2 只表示原 reset-binding 语义。

## 实际测试及透明失败记录

final 30/30 见 [STDLIB_FAKE_TEST_RECEIPT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/STDLIB_FAKE_TEST_RECEIPT.json>) 与 [STDLIB_FAKE_TEST_LOG.txt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/STDLIB_FAKE_TEST_LOG.txt>)。先前新增自有测试两处误设 `max_events=0`，触发原 bounds `ValueError: Recorder bounds invalid`；仅将测试改为 `first=last=0,max_events=1`，原生产 recorder bounds 保留。
生成本 source contract 首次误用闭包 qualname，`KeyError: 'PassiveCapture.attach.feedback'`；按原 source_api 真实规则修正为 `PassiveCapture.attach.<locals>.feedback`。失败时未创建 contract，原 source_api 未动。

全部为 own FakeTensor/API/AST；target modules=[]、禁止事件计数 0。未执行 Torch CPU、SDK、GPU、原 worker 或训练。`native_enabled:false / exact:false / Gate1:UNKNOWN / stage2_go:false`。
