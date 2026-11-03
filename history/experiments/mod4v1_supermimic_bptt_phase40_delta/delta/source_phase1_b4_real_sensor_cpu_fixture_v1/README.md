# B4 + real Sensor/Delay：注入式 CPU software fixture（SOURCE ONLY）

本包只新增 fixture、六项 stdlib metadata/AST 检查及说明/封件；child 实际 TorchCPU 结果为 `null`。未来父的唯一新 CPU purpose 才执行数值部分。没有 loader、CLI、launcher、worker、stager、native consumer 或 C2 集成。

## 1. 入口和固定依赖

入口位于 [cpu_fixture.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_real_sensor_cpu_fixture_v1/cpu_fixture.py>)：

```python
run_fixture(torch_module, real_sensor_class, real_delay_class, *,
            codec_module, passive_module, field_module, dependency_module)
```

父提供已完整载入的真实 Torch 模块、两个完整原 source 类、完整 published codec 和 B4 的三个模块。启用 assertions（普通 `python -B`，不用 `-O`）；本函数只返回 compact dict，不写报告或其它文件。父自行验证本包 seal 后调用；本包没有代替父加载模块的分支。

- 原完整 Sensor：3733 bytes，`aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8`；构造 `SensorCorruption(num_envs, device, seed, profile)`。
- 原完整 Delay：3031 bytes，`90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665`；构造 `FeedbackDelay(n, device, seed, enabled=True)`。
- 两者均使用完整 `reset(ids)`、`apply(key, raw_or_x, tick)`、`state_dict()`；fixture 以真实 class globals / file / full SHA 加完整 `source_api.pin + verify_callable` 核对 init/apply/reset/state_dict。没有 AST 裁 class 或替代数学实现。兼容原 runner 的实际 module alias，即原数学模块未注册 `sys.modules` 也不补造注册；其真实 globals、原类绑定和 `torch` 身份仍逐一检查。
- 完整 [B4 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json>)：21 members，seal `81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3`，root `6c8cc456c752a57fd9963b919e398f3c91c0c2205c15b4d1a0dbd9b605c96107`。
- 完整 [codec seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_codec_v1/SOURCE_SEAL.json>)：7 members，seal `2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219`，root `4ceeeda60cde6f8ca6cc496b8d299e5ea3b4ff2770b707f84898f06c1b75eec8`。

fixture 从传入模块真实 `__file__` 定位这两个完整封件，逐件 bytes/hash/root 验证；结束的 `finally` 再验证。这是 source 软件契约检查，不是新的资源 admission。实际部署路径由父确定；本地只读证据路径集中于 [SOURCE_PINS.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_real_sensor_cpu_fixture_v1/SOURCE_PINS.json>)，没有推测 remote 路径。

B4 的 `source_api` / `field_snapshot` / `dependency_contract` / `passive_capture` 应由同一 B4 完整目录正常导入，codec 使用 publication 的正常模块名绑定；避免旧同名模块缓存。每个独立实例先真实调用 `verify_typed_dependency(snapshot, ledger)` **默认固定 publication**（19153 bytes / `5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452`），检查 **22 functions + 3 codec classes**，另有 FieldSnapshot class；不传 override。随后才直接 `PassiveCapture(...).attach()`。

**不执行** `install_passive_capture`、`preflight`、`_preflight_impl`。inspection 显式写明 `OWN_CPU_FAKE_ENV_SOFTWARE_ONLY` 和 `native_binding_preflight_executed=False`，没有 SDK/MRO 通过声明。

## 2. 正段：唯一 64/640 normal 分母

`OWN_CPU_FAKE_ENV` 是本包显式合成的原 caller，不是 Isaac 环境。它使用真实 original Sensor/Delay CPU 对象、完整 FieldSnapshot 和 published codec/B4。N80、CPU、seed 20261103、已创建 int64 witness index8；正段每 control8 physics、MID4/END8 各五 channel（3/3/4/4/2=16）。

| 正段每条 untapped/tapped 路径 | 数量 |
|---|---:|
| controls / scene callbacks / feedback ticks | 64 / 512 / 128 |
| normal channel records / real Sensor.apply / real Delay.apply | 640 / 640 / 640 |
| terminal callbacks / tap 内 reset callbacks | 64 / 5 |
| 初始化 reset（tap 前，由 fixture 原 caller 执行） | 1 |
| full int32 reset ID K | 0、1、2、79、80 |

control37 的 full bool80 为 term row79 / trunc row78，原 int32 IDs `[78,79]` 与 pre event 原子关联。K0 已观察空 IDs 与无 callback 的 `None` 严格分开。每个 normal record 的 raw/noisy/delay-return owned8 Tensor 都与原 caller 已有 Tensor 逐值、dtype/shape/rowmap/非 alias 比较；full80 pre/post flags 与 K0/1/2/79/80 IDs 全部保持。index 内容的 codec 权威仍是 `CALLER_DECLARED_INDEX_BINDING_NOT_READBACK`，CPU oracle 的独立 index 不变检查另列。

actor35 是合成原返回：caller 已有 END16 加显式 synthetic19；actor 组装不再调用 feedback。正段每 control 对比 untapped/tapped 原返回值、完整原 `state_dict()`（含所有私 generator、bias/episode/noise、delay/queue/cache）及计数。仅证明本 software fixture 的 parity；没有实际 native actor 或未计算 MID19。

## 3. 独立额外段与负段（全部不计入 640）

1. **IDLE cache / partialreset / warmup**：两个独立同 seed 实例，原 tick 序列 `1,2,2,2,3`，每路径25 channel calls；phase 为 `outside_scene_update`，normal records=0。第三次同 tick changed raw 保持原 Delay cached output、noise draw count 不增；原 caller 同 tick reset rows78/79 后，两行 fresh noise 和 sample_tick/ready warmup 检查。open control 明确 incomplete，不伪造 END 或 finish。
2. **off identity**：独立 `profile=off`、delay disabled，两真实原类加 tap 全程返回输入同一对象，每路径1 channel call。
3. **真实原 apply 异常**：真实 Sensor unknown-channel `AssertionError`，真实 Delay skipped-clock `AssertionError`，均比较捕获对象就是 tracker 所见的原异常，并比较真实 partial states。每路径3 Sensor attempts / 2 Delay attempts，0 normal。
4. **RAISED reset**：明确由 `OWN_CPU_FAKE_ENV` 的原 `_reset_idx` 在真实 Sensor.reset 后、真实 Delay.reset 前抛出受控异常；同一异常对象传播、真实剩余 partial state parity、pending `INCOMPLETE`/before/after/IDs 保留。**不调用 end/finish**。这不是声称原 Sensor/Delay 自己抛这个受控异常。
5. **bad-ID metadata**：独立 `metadata_only_fake_return` 原 callback，float32 IDs 专供 metadata 负例；该 callback 不执行真实 Sensor/Delay 的 malformed-ID reset。必须保留 callback count=1 和 `OBSERVED_METADATA_FAILED`，INCOMPLETE；codec ledger 内的 NOT_OBSERVED 不是“原 callback 没发生”的声明。无 malformed-ID 原类成功断言。
6. **missing END**：独立 truncated synthetic caller 只走4 physics tick 后返回，5 MID / 0 END，missing 列表保留全五 END channel。没有补采样、回放、伪造 END clock，正段 sampler 不变。

全部 six hooks（sensor.apply、delay.apply、feedback、scene.update、termination、reset）真实 attach/close，并逐一核对原 binding 恢复。原调用 tracker 只转发一次、保存其原返回或原异常；scene/terminal/reset 的原返回 identity 同样检查。

## 4. Oracle、导出与状态边界

- observer callbacks 不增加 CPU/tolist/item、RNG draw、getstate/state_dict、SDK getter、step/reset/observation。六项 static 检查完整读 pinned callbacks，检查其原调用转发；foreign-env feedback 分支是另外的 early passthrough，不是本 env 调两次。
- fixture 自己的比较、原 `state_dict`、global Torch CPU/Python RNG 读取、oracle clone/index_select/data_ptr 均在 callback 外，是独立 CPU oracle，不计作模型或 observer 采样。真实 Tensor 仍只在父后续 purpose 构造。
- 主正段关闭并恢复六 bindings 后才调用 codec `materialize` 和 JSON roundtrip；typed original dtype / shape / witness 声明保留。独立 int64 per-env feature probe 验证 `2**60+7` 经 JSON 仍精确整数；它不是 Sensor 测量或 reset ID。
- 所有 Tensor factory 显式 `device='cpu'`。没有 CUDA 属性访问、查询或初始化；没有 Torch import。函数不改全局 RNG 或线程配置。
- B4 原 report 的 UNKNOWN 不被本 fixture 提升；software parity 结果单独返回。`MID remaining19 / full clean35 / natural clock or reset / SDK / PhysX / actual DR readback / native actor / skill` 全保持未验证。

## 5. SOURCE 验证和交付

[test_fixture_source.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_real_sensor_cpu_fixture_v1/test_fixture_source.py>) 只有六项自己的 stdlib AST/compile-only/metadata checks。未 import/调用 fixture、B4、Field、codec 或原类；未执行作者11、旧30/12、旧真实 CPU runner。没有额外 audit hook、profile、runner 或反复 QA。

机器契约见 [FIXTURE_CONTRACT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_real_sensor_cpu_fixture_v1/FIXTURE_CONTRACT.json>)。SOURCE receipt 和 seal 的实际 CPU 结果保留 `null`。父未来结果另存父报告，不写回此封件。

`exact=False` · `Gate1=UNKNOWN` · `Stage2=False` · `C2 disabled`。仅 SOURCE 交付后停止；无自动 native 或训练后续。
