# Codec real-CPU fixture：SOURCE-only 准备

本目录仅交付 injection-only 小函数与静态证据；本次 `run_fixture` 调用数 **0**、Torch 实例数 **0**、真实 CPU 结果 **null**。父完整阅读并另行执行自己的独立 TorchCPU purpose；此处没有 launcher、loader、CLI、worker、stager、SDK 接点或新数据 consumer。

## 唯一入口

```python
run_fixture(torch_module, codec_module) -> dict
# 父传已经加载的真实 Torch 模块，以及已经按固定 pins 核对的完整 codec 模块：
result = cpu_fixture_module.run_fixture(already_loaded_torch, already_verified_codec_module)
```

函数只导入 stdlib `json` / `random`。没有导入 Torch、动态加载 codec、读取权重或文件的路径；源码约 136 行，测试仅 AST/compile/bytes pins，没有 import 或调用本函数。父执行应保持 Python assertions 开启（不使用 `-O`）；检查失败保留原异常，不转换成 RC0 成功。

## 父执行时覆盖的合成检查

- `N80`、已有 CPU `torch.arange(8, dtype=int64)` 作为 witness index；显式 CPU `arange/zeros/full` 无随机输入，四个 semantic role 逐一核对原 dtype/shape/device、保留形状、值、owned storage 与 source 非 alias。
- witness 保留 8 行；`ENV_IDS_FULL` 原 int32 完整 `K=0/1/79/80`，K80 保留 80；bool masks 的 row79 term、row78 trunc 完整保留 80，不随 witness 裁减。
- `QUEUE_GROUP_FULL` legs `[80,4]` / wheels `[80,2]`，原 float64 全 80；typed materialization 保留 dtype，int64 `2**60+7` 经 JSON round-trip 仍为精确 Python int。
- 通过修改独立 probe 的 owned tensor，再核对 source baseline，证明非 alias；所有 capture/materialize 来源和 witness index 在函数结束时再次逐值核对。空 ID tensor 的存储指针可能同为 0，故仅非空 payload 比较底层 storage pointer；空 ID 核对独立 Tensor 对象、形状和值。
- 12 个非法 semantic / dtype / axis / shape / group / witness-count 反例仅接受 `CaptureError`；没有 fallback 或 cast。
- 64 个 synthetic controls / 640 个原结构的 MID+END 五通道 metadata records，模拟 control8tick、physics400Hz、feedback100Hz、2500us/tick 的时钟关系；均标明 `SYNTHETIC_CPU_NOT_SDK`。
- control37 合成原先已就绪的 full80 pre/post masks 与 int32 IDs `[78,79]`；按 atomic control pack 保留 `prior_termination_event_id`。其它 controls 无 callback 为 `NOT_OBSERVED + ids=None`，和另一个 observed-empty ID callback 明确区分。
- 另一个小 edge-order ledger 先记录 `RAISED` / K0 IDs / before metadata，再给 late pre；保持原字段、missing 与 prior=null，late pre 不会 retro-join。
- ledger 保持已 owned clean/payload 的 Python identity 与 tensor pointer；上游完整源码 AST 另证 `ControlLedger` 没有 `clone/index_select/capture/cpu/tolist` 调用。fixture 自身用于 source baseline 的 clone、值比较与 probe 修改是测试 oracle，不等价为 observer 新增采样。
- 在任何输入构造前取全局 Torch **CPU** RNG / Python RNG，全部检查后逐状态比较；没有 CUDA 调用、CUDA 状态查询或初始化。这里只为显式要求的 CPU fixture 读 RNG state，没有给 SDK observer 加 getstate。

## 边界与 seal

所有 tensor、clock、actor35、flags、IDs、control37 reset 都是合成输入；结果只说明 standalone codec / ledger 对这些 CPU 输入的契约表现，不是 SDK、物理、实际 episode、自然 reset、sensor fresh、原模型质量或 untapped bitwise 证明。`Gate1=UNKNOWN`、`Stage2=False`；真实 CPU 尚未执行的 SOURCE receipt 使用 null 结果，而不是用假 PASS 占位。

旧 codec 8 件、旧设计 7 件及既有 B2/V4/C1 七个 source 引用仅 bytes/hash 只读核对，全部保持原件。C2 目录/pins、actual reports、whole FINAL/trace、PT/raw、SSH、GPU、SDK、canonical/资源/EX/C 账本、Git、stage/dispatch 访问或执行均为 0。本目录 `SOURCE_PINS.json` 固定所有只读来源；`SOURCE_SEAL.json` 固定本目录源码、静态日志与 receipt。SOURCE 测试次数与父未来实际 CPU 次数分开记账。
