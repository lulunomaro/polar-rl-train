# B4 real Sensor/Delay CPU fixture V2：最窄输入 dtype 支持域修正

**SOURCE ONLY；V2 实际 CPU 结果为 `null`。** catalog 的 Office/ACL 无 RL fixture 匹配，本次只使用 FS 与 Python314 `-B` stdlib。父后续唯一 NEW CPU purpose 再执行注入式数值部分；本包没有 loader、CLI、launcher、runner、worker、stager 或 native consumer。

## V1 失败：仅 PARENT_REPORTED

父报告唯一 CPU job `c5c7` 已 RC1：V1 的 `fixture:276 left=a.step` **UNTAPPED baseline** → scene:140 → 原真实 Sensor.apply:36，在第一条 baseline feedback 的 `noise[due] = torch.rand(...)` 处出现 Double destination / Float source 的 indexed-assignment dtype 错误。尚未进入 tapped `b.step`；`fixture_result=null`。这不是已确认的 B4 tap / SDK 缺陷，也不声明完成64/640或其它运行分母。

child 未读取实际 report、SSH、runner；保留父信息为 `PARENT_REPORTED`。原 V1 完整封件、原报告、原 runner 和原 Sensor/Delay/B4/codec 均保持不变。

本次实读完整 [原 Sensor source](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/sensor_mild_math.py#L28-L38>)：33用 `zeros_like(value)` 保留输入 dtype，36的 `torch.rand` 只有 `device/generator`，未指定 dtype。父所见原默认 rand 为 Float；V1 自建输入却为 Double。V2恢复该原环境的 float32 输入支持域，**不设置默认 dtype、不改或 cast 原 noise、不改变原 RNG 路径**。SOURCE静态证据不是新的数值实测。

## 唯一两处 fixture body 差异

[新 cpu_fixture.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_real_sensor_cpu_fixture_v2/cpu_fixture.py#L115>)：

| 行 | V1 → V2 | 原因 |
|---|---|---|
| 115 | templates `t.float64` → `t.float32` | 输入与原 mild Sensor 的 float32 rand 支持域一致 |
| 307 | expected `'torch.float64'` → `'torch.float32'` | 同步断言真实 raw/noisy/delay source 的 dtype |

无其它 fixture body 修改。反向替换全文 bytes 精确等于冻结 V1；AST 只两个 leaf 改动，完整490行/28309 bytes 不变。完整 API、原 once 转发、默认 fixed verifier22+3+Field、six hooks、64/640正常分母、idle probes、full80 flags、K0/1/2/79/80、RAISED pending、metadata-only badIDs、missingEND、finally source/restore 均沿用原完整 AST。

fake-state、synthetic19、off-input 及 invalid-channel negative input 的四个 `float64` sites（119/120/380/390）原样保留。`int64 2**60+7` 精度 probe 不变。未增加其它源位置修正。

## 同一注入 API 和冻结依赖

```python
run_fixture(torch_module, real_sensor_class, real_delay_class, *,
            codec_module, passive_module, field_module, dependency_module)
```

父注入完整真实模块/类，开启普通 assertions（非 `-O`）；source API 与 class alias 的完整校验沿用 V1。B4 canonical modules 和 codec binding、正常 float32 default 使用父原进程既有状态，不调用 `set_default_dtype`。每个 direct `PassiveCapture.attach` 前真实默认固定 **22 functions + 3 codec classes + Field class** 验证；不传 override，不调用 native `install/preflight`。

[来源 pins](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_real_sensor_cpu_fixture_v2/SOURCE_PINS.json>) 固定 V1 7members+seal/root、B4完整21members、codec完整7members、原 math2份及只读参考6份。B4 root `6c8cc456c752a57fd9963b919e398f3c91c0c2205c15b4d1a0dbd9b605c96107`，codec root `4ceeeda60cde6f8ca6cc496b8d299e5ea3b4ff2770b707f84898f06c1b75eec8`，全部保持。原实际 CPU 程序仅作为已读 source API 参考，不执行。

为精确保留两 leaf 差异，未来函数运行时原 result kind 字符串仍是 `B4_REAL_SENSOR_DELAY_TYPED_TAP_CPU_SOFTWARE_FIXTURE_V1`；这不是复用旧 actual report。NEW source contract / pins / receipt / seal 标为 V2，父的 NEW purpose/report 应据本 V2固定 source SHA 记录来源，不靠旧 kind 当质量成功。

## 五项 NEW 窄 SOURCE 检查

[test_fixture_v2_source.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b4_real_sensor_cpu_fixture_v2/test_fixture_v2_source.py>) 只做：

1. compile-only、完整同一注入 API 与 imports；不执行 fixture。
2. 两处 literal/fullbytes 反向证明及两个 AST leaf，行数/bytes 不变。
3. 原 Sensor zeros_like / rand 无dtype 的 source pin 证据；没有 default/RNG patch，其余四个 double sites 保留。
4. 完整原功能 cases/分母/unknowns/精度契约不变，V1 failure 明确 parent-reported，V2 actual CPU=null。
5. V1完整封件、B4/codec及两原类/参考源 bytes/hash/root 不变。

没有旧6/30/12或作者11，没有 fixture/B4/codec/真实类 import 或 constructor，没有 Torch/SDK/GPU/SSH/实际 report/锁/账本/Git/stage。只写本 NEW component artifact。SOURCE封存后停止，父 actual结果另存；`exact=False / Gate1=UNKNOWN / Stage2=False`，C2 disabled。
