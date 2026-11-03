# Phase1 original-queue real-CPU fixture — SOURCE, real run pending

本包是独立新 lineage。只交父代理可执行的参数注入 fixture；本地没有 import Torch、执行真实 CPU queue、SSH、SDK/native、GPU、模型/PT/replay/rawJSONL、canonical预算、Git、stager 或 trainer 操作。既有 state/context 与 actuation 两个 seal 及其17成员只读核对。

Catalog 仅 Office / Windows ACL，无 RL 匹配；本次使用 FS/CLI、Python314 `-B` 的 AST/stdlib 轻测试。SOURCE 测试 PASS 与未来真实 Torch CPU fixture PASS 是两个独立结论；均不等于 actual SDK / Gate1。

## 父代理稳定注入接口

[real_cpu_fixture.py](<real_cpu_fixture.py>)：

```python
# 父在独立 CPU 用途中提供已加载的 real torch、已PIN原class、已PIN旧tap module。
# 本包没有 loader、Torch fallback、SDK env、远程入口或 driver。
from real_cpu_fixture import run_fixture
result = run_fixture(torch_module, PhysicsActionQueue, tap_module, n=3, seed=20261103)
```

- 支持 `n=2` 或 `n=3`，默认 N3；`torch_module` 是真实已安装 Torch，而不是 stub。
- `PhysicsActionQueue` 必须来自真正原文件。fixture 用 `inspect.getsourcefile`＋SHA256校验原 class 文件、原 method code filename、原 torch global、FIELDS/WIDTHS。调用方应按正常 file-module 方式加载原文件，保留真实 `__file__` / module 身份；只 exec 一个无来源 class 或传 FakeQueue 会失败。
- `tap_module` 是旧已封存的 [actuation_tap.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py>)，同样校验 bytes pin；本包不复制或修改旧 tap。
- 原 source 与 tap 的 bytes（包括换行）必须保持一致。SDK adapter source 只作为 API/时序参考 pin，fixture 从不构造或执行真实 SDK adapter。
- 返回一个小 receipt dict，不落盘、不保存 Tensor/PT；父自行把返回值归入其独立 CPU evidence。此处不重放刚完成的 sensor CPU。

## 确切原 API / pins

[原 queue](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_physics_queue.py>)：

```python
PhysicsActionQueue(n, device, seed, enabled=True, physics_us=2500, control_us=20000)
queue.reset(key, ids, neutral, new_scene_clock=False)
queue.submit(key, x, tick)        # 原返回 None
queue.apply(key, tick)            # 原返回 g['applied'].clone()
queue.receipt(key, tick)
queue.state_dict()               # 全 groups + 两 private generators
```

| source | SHA256 |
|---|---|
| [原 PhysicsActionQueue](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_physics_queue.py>) | `a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8` |
| [原 SDK adapter（仅参考）](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_sdk_adapter.py>) | `ecd1db05a0dfe215cdf089ccf346aea1a5c51d7974a2bcd6e486dff66b7f5494` |
| [已封存 tap](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py>) | `b9b9e288124a1ba8c031a030c00a231f4d02d2ba7efee9981141ae90b8e28828` |

固定 pins 和原 API AST 见 [SOURCE_PINS.json](<SOURCE_PINS.json>)；[source_pins.py](<source_pins.py>) 只读验3个 source 与旧17成员及两seal，不 import 原 source。

## 真实 queue + 显式 fake 脚手架的边界

真实部分：原 queue 构造、两个 private generators、reset、submit、apply、receipt、state_dict 以及旧 tap 的真实 CPU Tensor `detach().clone()` 路径（留待父真实执行）。

`FakeEnv`、`FakeActionTerm`、`FakeAsset` **均明确为 fake**，仅做原调用关联与 writer argument/return identity 测试。不是 Isaac env、articulation、真实 SDK binding 或物理 readback；不包含 actor35。

原 queue 的 lag 抽样仍由原 reset 发生；为确定性覆盖九组合，fixture 在 baseline 与 observed **两边同样赋值 lag_steps** 为指定0/1/2。这是受控 CPU 单元测试设置，绝非实际 episode DR readback。neutral 使用 synthetic zero processed targets，也不是机器人默认 q 证据。

## 覆盖与比较

每个 legs/wheels 0/1/2 的9组合：两 control（start0/8）各8个原 physics apply tick；随后只 reset row1，再执行 start16 的8个 apply tick。核心两 control 共288个 group apply，含 partial-reset 后共432个；N2/N3 都支持。

- 独立 baseline 与 observed queue 使用同原 class/seed，每个 paired operation 后比较**全原 state_dict**（所有12字段与两 private RNG）及原实例配置属性；仅排除测试插入的 submit/apply probe 方法属性，close 后这些也还原。
- Tensor 比较使用 contiguous uint8 view 的逐 byte equality，不以浮点 `allclose` 代替 bitwise equality。
- 记录 Torch **CPU global RNG** 初始 state，并在全过程检查不变。原 queue 只使用 Torch CPU private generators；不声称覆盖无关 Python/NumPy/CUDA RNG 或系统状态。
- 原 submit 的 None、原 apply 产生的 Tensor、fake writer 的返回/参数、fake term issue/apply 返回均检查原 identity；source exception 通过 probe 捕获后要求 tap 重抛同一异常对象，baseline/observed 类型与消息相同。
- 完整检查 partial reset 的 selected episode+1、neutral/valid/issue 清理、unselected 12字段逐 byte不变及 `last_apply_tick` 全局钟保留。tap 本身不 patch reset。
- `first_transition_latency=(first_apply-issue)*2500us` 与 `held_age=(current-issue)*2500us` 分离；第二 control 尚未 due 时旧 target held age=20000us，并不变成原首 latency。
- 拥有快照检查：captured selected Tensor 不 alias queue state 或原 apply 返回；12个 pre/post Tensor 也不 alias live queue；修改 captured Tensor 后全原 state 和原返回保持逐 byte不变。
- 同 tick 相同 submit / 重复 apply 幂等；不同 command 的同 tick submit与跳 tick apply维持原断言、异常 identity、状态不变。此探测单独运行，不把重复 callback 塞进要求8个 unique tick的旧 offline validator。
- capacity=1 的 bounded overflow 仍与 baseline state/RNG相同，coverage硬 UNKNOWN；最终 method恢复、probe恢复、双次 close检查。

上述均是**未来父 real CPU run 会执行的断言**，本地仅 AST/stdlib验证，当前尚无 real CPU PASS。

## 本地轻测试 / freeze

[轻测试](<test_source_contract.py>) 验证注入签名、原API/pins、N2/N3九组合/时钟计划、compile、无Torch import/自动执行、bytewise/identity/owned/overflow/restore 断言存在、两旧封件保持不变。它不调用 `run_fixture`，也不以 FakeQueue 代替真实执行。

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B 'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_actuation_real_cpu_fixture_v1\test_source_contract.py'
```

[SOURCE_RECEIPT.json](<SOURCE_RECEIPT.json>)、[SOURCE_TEST_LOG.txt](<SOURCE_TEST_LOG.txt>) 是 SOURCE 轻测试回执；[SOURCE_SEAL.json](<SOURCE_SEAL.json>) 由 [seal_source.py](<seal_source.py>) 创建后只读验证。

当前 `real_torch_cpu_executed=false`、`original_queue_execution=PENDING_PARENT_INJECTED_TORCH_CPU_RUN`、`actual_sdk_pass=false`、`Gate1=false`、`runtime_source_binding=UNKNOWN`、`physical_readback=UNKNOWN`、`actor35=NOT_TESTED`、`exact=false`。即使未来真实 CPU 全断言通过，也只升级该独立 CPU component fixture，不升级 SDK、原任务绑定或论文 Gate1，更不推进阶段2。
