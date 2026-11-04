# Typed C2 real-CPU injection fixture V1 — SOURCE ONLY

## 范围

这是一个 210 行、无 CLI/main 的独立注入 fixture；当前仅执行五项 NEW stdlib AST/compile/pins 检查。能力选择：本次 catalog 为 Office/ACL，无匹配 RL skill；采用 FS 与现有 Python314 -B stdlib。真实 Torch/CPU/SDK/native、旧套件、原 gate/worker/CLI/main 全部未执行；本封件不是实际 CPU 结果。

准确 API：

```python
run_fixture(torch_module, PhysicsActionQueue, actuation_module,
            codec_module, observer_module, field_module)
```

六个原模块/依赖全文来自固定 `SOURCE_PINS.json`：E3 原 Queue 111 行/8511/a4238c…，C2 20859/ec10b09…，codec 22318/77c007…，producer observer 16708/944c6e…，完整 FieldSnapshot 与 observer contract。父后续另行在 NEW CPU namespace 注入全模块；fixture 内只检查原文件身份/关键注入对象相等，不调用 native `verify_actuation_binding`，这些检查也不替代完整 native MRO/SDK 门。

## 待父执行的实验定义

- 自有 FakeEnv/Asset/Term；真实原 Queue、C2 hooks、typed producer、codec 和 real CPU Tensor N80。独立 64 controls × 8 ticks，仅 legs lag2/wheels lag1，不复用旧 9-pair 套件。
- 同 tick submit/apply 重复、完整 Queue state_dict/额外存储属性/各 private Generator 状态、global Python/Torch CPU RNG，与 untapped 基线按原 dtype/shape/device 和 uint8 bytes 比对。fixture 自身不修改全局 RNG/default dtype。
- 自有一次 partial reset IDs `[78,79]`，保留原 reset 行为后显式固定 synthetic lags；不是自然 termination/reset 证据。初始 synthetic episode=`2**53+7`，仅作为 int64 serde 压力值，不冒真实 episode 计数。
- 每个 control 调用原 `WindowRetention.add`（内部完整 `typed_c2_event`）并检查全部事件；仅保留 `[0,1,62,63]`，middle=`UNKNOWN_UNRETAINED`。使用原 `stored_clock`；`control_slot='UNKNOWN'` 且没有 `sim_time_us` 是此 adoption clock 的合法行为，不补字段、不冒正常 B4 100Hz 采样。
- known-group 的 12 queue fields/命令/selected target 保留 full80、原 dtype；adoption 使用 C2 已 owned clone，检查同一个 Tensor object/data_ptr/_version、metadata/内容不变。fixture 为断言而另存的 verification clones 与 producer ownership 操作分开。
- 原 Queue N79 input 先在 `_input` 失败且不改 state；C2 保存 RAISED 与原 exception identity；对应 typed adoption 再在 explicit N80 门失败。另测 codec dtype metadata 错误与 source-context setter 原异常同一对象传播。
- 逆序 hook close 成功后，调用完整 codec.materialize→Python json roundtrip，检查 int64（含大于 2**53）与 bool；保存中的 C2 owned 源在 adoption 和 serde 后保持不变。

## 有意未表出的未知

counter0 / NON_TERM_SETTER 的原 C2 event owned Tensor 数值留在原内存，转换前后保持；typed event 保留全部原 keys 与 source/shape/dtype/device、scope/raw tick，但这些 Tensor 的 `values='UNKNOWN'`。**这不是未归组 setter 数值的 JSON 全保留。** JOINT IDs 也维持 metadata-only UNKNOWN，未套 ENV_IDS_FULL 或 QUEUE role。SAME_ASSET_TERM_APPLY_CONTEXT 只证明原 source context/group，不签 DOF、gas、物理 readback 或 actuator pipeline。新 OPAQUE/source-qualified 角色属于后续明确接口目的，本包无新 role、无 observer 修改。

## SOURCE 测试与冻结

五项检查仅覆盖完整文件 pins、AST/compile/API/210 行边界、完整函数调用布局、不调用旧 suite/native gate、ownership/clock/error/serde 断言的静态存在。它们没有执行 run_fixture、真实 Tensor 操作、原 C2 hooks、Queue 方法或真实 CPU 场景。

SOURCE_RECEIPT 中真实执行数为 0，实验结果/计数/通过结论均为 null。SOURCE_PINS、SOURCE_RECEIPT、SOURCE_TEST_LOG、SOURCE_SEAL 随本包冻结；所有原封件只读，producer10/B4/Queue/C2/codec/observer 旧测试均未重跑。父新 namespace 的实际 CPU 执行与结果另收新 receipt；当前 Gate1=UNKNOWN、exact=False、Stage2=False。
