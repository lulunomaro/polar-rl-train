# V4：仅 strict typed dependency binding 的 NEW Source 修复

## 结论与边界

- NEW `source_revision=4`；唯一改变的生产组件是 [dependency_contract.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py>)。并未安装或执行原场景。
- [passive_capture.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/passive_capture.py>)、[field_snapshot.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/field_snapshot.py>)、[source_api.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/source_api.py>) 与 B3 完全同字节。6 hooks、ledger 接点、场景更新与原四层 reset/MRO 检查保持原样。
- capture 数据 schema/report kind 仍为 `PASSIVE_SENSOR_CAPTURE_V3`；独立 publisher layout/API 仍为原 publication；B2 source API lineage revision 2 保留。只有 preinstall binding receipt kind 变为 `V4_TYPED_SOURCE_BINDING_INSPECTION_V1`，附 `source_revision=4` 与原 capture schema 兼容说明。
- `native_enabled:false`、`exact:false`、`gate1:UNKNOWN`、`stage2_go:false`。没有增加批准 flags。11 项 own stdlib preinstall 测试是绑定证据，不是 tensor/numerical、MDP、actor35、Torch CPU 或 SDK 现场证据。

## 两处修复

### 固定 expected publication，而非调用者自选集合

[CODEC_SOURCE_PINS.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/CODEC_SOURCE_PINS.json>) 从 B3 原件按字节复制，仍为 19153 bytes / SHA256 `5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452`。固定长度和 SHA 写在新 guard 源码中；expected 没有从运行时 imported module 源码反推。

`verify_typed_dependency(snapshot, ledger, *, dependency_pins=None)` 的签名保留：

1. `None` 只加载固定文件，校验上述完整 bytes/SHA。
2. 显式 override 只是兼容输入：全部根/嵌套 key、value 与精确类型都必须等于固定 publication。字典顺序不构成差异；空、缺项、多项、改 HASH、换 publisher/class/function、`False/0/0.0` 混同都失败。
3. 四个 collection 还检查硬编码完整名称 keysets：3 constants、3 classes、17 codec functions、5 field methods。不是仅检查计数。
4. 即使 override 完整相同，后续检查仍使用 fresh 固定文件树，不使用调用者持有的数据。
5. 原 module/owner/descriptor/`__wrapped__`/source bytes/line/live compiled code 等检查继续运行；默认 positive 实际检查 22 functions + 3 classes，另行校验 field class。

### defaults / kwdefaults 的精确字面值类型

递归比较仅接受精确的 JSON builtin 类型，先检查 `type(actual) is type(expected)`；本比较器明确区分 `False`、`int(0)` 和 `float(0.0)`。字典只接受精确字符串 keys；任意对象、subclass、嵌套 tuple 不靠宽松 `==`、`repr`、truthiness 或 coercion 通过。

仅保留以下表示规范化：

- `fn.__defaults__ is None` → 空 tuple，再将 **外层 defaults tuple** 表示为 JSON list；default value 内部的 tuple 不转换。
- `fn.__kwdefaults__ is None` → 空 dict；没有其他 falsy 规范化。
- 原 publisher 的 `ROLES` 和 `INTEGER_DTYPES` 必须是精确 tuple，仅该 **外层 tuple** 转为 publication 的 JSON list。其余 module constants 不转换。

## 实际测试与失败记录

[NEW tests](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/test_dependency_contract_v4.py>) 仅导入 stdlib、冻结 publisher、显式 field adapter 与 FakeTensor，执行 preinstall verifier。没有导入或重跑旧 B3 30 控制测试，也没有导入 capture/worker/SDK 入口。没有调用 capture、ledger begin/end、step/reset/observe、materialize 或任何 tensor 拷贝/导出操作。

- [attempt 2 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_RECEIPT_attempt2.json>)：**11/11 PASS**，0 failures/errors，Python 3.14.3 `-B`，总 0.9001012000007904 s；[日志](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_LOG_attempt2.txt>)。
- 覆盖：完整默认/identical override、四集合 empty/missing/extra、完整树身份/HASH/类型改动、真实 published positional int0→False/0.0、published kw int80→80.0/False/0/0.0、own int0 kw helper→False/0.0、递归类型、未知 wrapper/source-line/foreign owner、对象恢复及原源码不变。
- FakeTensor `detach/clone/index_select/cpu/tolist` 操作计数为 `{}`。审计 target imports、external/native calls、raw/report opens 均为 `[]`。
- [attempt 1 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_RECEIPT_attempt1.json>) 与 [失败日志](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/STDLIB_TEST_LOG_attempt1.txt>) 保留。唯一错误为 own fixture 的 `mock.patch(__code__)` 清理：`TypeError: __code__ must be set to a code object`。只把 own test 的恢复改为显式 `try/finally`；生产修复 bytes 两次运行完全相同。[失败记录](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/FAILURE_RECORD.json>) 明确区分了两次运行。

## 原件保护、API 与封件

- [before hashes](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_BEFORE.json>)、[final test after hashes](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_AFTER_attempt2.json>)：B2 13 members + B3 18 + publisher 7 + 3 原 seals，共 **41 个原 source/seal** 全同；manifest SHA256 `34345662be0e30cfb08d2598d7e3e36c7f11c24796805ab8ae0285444ac12fbe`。
- [SOURCE API contract](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_API_CONTRACT.json>) 记录新 guard 精确源码位置/SHA/签名与版本兼容；[diff 说明](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_DIFF.md>) / [单生产文件 patch](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_DIFF.patch>)。
- [SOURCE_SEAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json>) 精确列出 21 members，连 seal 共 22 files。包含 attempt 1 失败原记录与 attempt 2 最终通过记录；不留未列入封件的输出。
- [verify_seal.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/verify_seal.py>) 默认只读核验封件及 41 原文件，不运行任何测试或场景；封件只创建一次。

父告知的旧 codec CPU/STATIC 复现仅为 `PARENT_REPORTED` 历史，本任务没有打开实际 CPU/trace 报告，也没有将其视为 V4 native 通过。最终 Source pins 交父后停止，不自动安装，不生成 worker/index/stager。
