# portable_fsm_detector_v1 — 新原生C保护状态机

**本包封存的是独立C99核心/API与host接口验证，另列M4/M7 compile-only物件事实；不是固件、SP算术、接触校准、动作、实时或实物资格。** 与仍BLOCKED的ASQP stdio任务无运行时依赖，未重编、重命名或恢复该IO组件。

## 1. 源与接口

- 原语义：[sealed Python](<../../FSM_DETECTOR_V1/fsm_detector.py>) SHA `8aa2eb817cc095f2b3c470d37e24bbe91ba13a5e5a77b06e75aa54e45cce0b2e`。已只读审完整源码、README、63方法场景和旧header proposal；旧包保持字节不动。
- 新API：[fd1_detector.h](<fd1_detector.h>)；实现：[fd1_detector.c](<fd1_detector.c>)。与旧未实现proposal不做字节ABI兼容承诺。
- 编译闭包必须同时携带[Config字段](<fd1_config_fields.inc>)、[默认值](<fd1_defaults.inc>)、[reason IDs](<fd1_reasons.inc>)、[reason名称](<fd1_reason_names.inc>)。运行核心不需要Python、旧包或C3。
- [映射](<SEMANTIC_MAPPING.md>)、[冻结来源](<SOURCE_FREEZE.json>)、[数值预算](<NUMERICAL_BUDGET.json>)、[69项reason registry](<REASON_REGISTRY.json>)均在首个C执行前固定。

数值使用IEEE binary64、原Python相对秒，不做f32压缩或微秒量化。C3 f32测量可提升传入，但没有增加测量精度或可信度；这也不是给既有physics/RL另设FP64准入门槛。

## 2. 核心合同

- 固定caller-owned context，配置按值复制，无heap、VLA、可变全局、CAN回调、平台定时器或发送路径；单owner持续保留同一context。
- 模式0..10、profile、phase、输入valid位、force迟滞/持续窗/重复sample不累计、时钟倒退/未来/丢失/timeout、step-height/range/不确定度以及输出规则保持Python。
- 默认jump/recovery/auto-obstacle全部关闭、binding缺省unbound；force confidence门槛仍0.8，其他拟议阈值也未调。原Python没有跳距或jump_success/step_success输出，本C包也未发明这些字段。
- `None`/缺项显式valid/present/shape位；未知force不是0N。未知wheel state=-1、可选坏force回unknown，不借用DR、truth、world pose或新增可信cue。
- q4顺序是绝对`Lhip,Lcrank,Rhip,Rcrank`，不是state14的crank-minus-hip delta。`q4_reference_valid=0`时4个数全0，而不是一条有效零姿态。
- 硬故障锁存，立即返回INHIBIT/NONE/u0/q_valid0/accepted0/no-slip0；旧contact仅作为诊断保留，不形成许可。新的reset_event+disarm+健康窗才清普通fault，reset同周期只回DISARMED。
- reason有66个原Python字符串，故旧proposal单个uint64不足；新接口用2个word，同时保留有序、去重ID列表，fault和contact reason也逐项验证。
- 指针/alias/配置/context破坏是显式C typed扩展。输出与context重叠时返回`FD1_E_ALIAS`、锁存context而不写重叠输出；调用方丢弃该输出并立即走停机分支。配置/context结构损坏需显式有效init，reset事件不越过此条件。

正常软退化不一律伪装成硬故障：已经armed后contact unknown可按原Python给LIMITED、无q4阶段、无no-slip许可；默认无支撑时ARMING从不完成。模式/参考不等于底层执行资格，现有发送/功率/freshness gate仍独立。

## 3. 最小调用（无在线actuation绑定）

```c
fd1_config cfg;
fd1_context ctx;  /* persistent, single owner */
fd1_output out;
fd1_config_default(&cfg); /* all actions disabled/unbound */
if (fd1_init(&ctx, &cfg) != FD1_OK) { /* existing inhibit path; return */ }

/* Each tick: fill aligned sensor observations, explicit presence and timestamps.
 * fd1_input_default supplies schema/shape defaults, NOT contact/force trust. */
fd1_input input;
fd1_input_default(&input);
/* input.timestamp_s = caller_relative_monotonic_seconds; etc. */
fd1_status status = fd1_step(&ctx, &input, now_s, &out);
if (status >= FD1_E_ARGUMENT || out.hard_inhibit) {
    /* existing inhibit path; return immediately; no normal fallthrough */
}
/* Inspect mode/profile only. No CAN/torque/actuation function exists here. */
```

所有时间都属于调用方同一个相对单调秒域；各传感器时刻对齐由上层负责。本核心不构造时钟、采样器、窗口采集器或新观测。

## 4. 新接口的实际host结果

[新reference构造](<REFERENCE_GENERATION.json>)从原63方法生成**61个context、1042步固定输入/输出**，不是重跑旧分数补档。4个方法仅构造非法配置/类型、没有step：在[逐场景表](<SCENARIO_COMPARISON.csv>)显式标为0行，不伪造逐步匹配；C固定数组/按值配置与Python immutable tuple检查也非字节同构。

最终[host日志](<host_run_03.log#L1043-L1045>)与独立[离线比较](<COMPARISON.json>)：

|新C port项目|结果|
|---|---|
|逐步模式/profile/phase/flag/reason顺序/fault顺序/contact/source/no-slip/accepted|1042/1042，0差异|
|phase、q4、confidence、entered数值|最大误差0，所有比对数值binary64位一致|
|C replay检查|46087/0失败|
|native typed/NaN/Inf/overflow/alias/clock/latch检查|1993/0失败|
|实际C++调用C object|[extern-C smoke通过](<cpp_run_03.log>)|
|host结构大小|context1536B、output392B，仅host sizeof，不是ARM栈实测|

原`1e308`有限输入在后续轨迹减法中溢出并触发NONFINITE_TRAJECTORY_REFERENCE，未提前缩成f32 Inf、删掉场景或改阈值。可选负/NAN/None force、缺失proxy、origin非零旋转、显式COM、模型冲突均按对应场景保留unknown/故障语义。全量输入/原Python输出在[reference JSONL](<REFERENCE_FRAMES.jsonl>)；新C实际输出逐行保存在host日志，测试oracle不进入核心。

第一次host已0差异，但审查找到typed NULL-context contact诊断未显式设unknown。修订及额外invalid flag/context检查保留在[错误/修订记录](<ERROR_REPORT.md>)；最终结果不回写成第一次分数。

## 5. 新ARM物件事实（与host分开）

[物件报告](<OBJECT_SUMMARY.json>)与[实际命令](<ARM_BUILD_02.json>)：

|目标候选|新模块object大小|
|---|---:|
|Cortex-M4 / fpv4-sp-d16 / hard ABI|36880B|
|Cortex-M7 / fpv5-sp-d16 / hard ABI|36860B|

2/2新object保留且SHA复核；ELF32 little-endian ET_REL EM_ARM，ARMv7E-M/Thumb，VFP args=1。宏DBL_MANT_DIG53、double8B、FLT_EVAL_METHOD0；`__ARM_FP=0x6`是SP硬件候选，不是本模块在执行SP算术。

物件确实有`__aeabi_dadd/dmul/ddiv/dcmp*`及`__hardfp_*` libm未解析依赖；没有链接这些helper/BSP或运行目标代码。未来目标板链接/库、FPSCR/FTZ、栈、ISR、计时和WCET另绑，不阻断其他已授权工作。M7旧fromelf FP_arch标签与CPU架构分开记录。

第一次ARM严格构建因5处嵌套array initializer触发`-Werror,-Wmissing-braces`；显式补braces，不抑制warning或放宽flags。失败原日志/源码保留，首次没有object是编译exit1的正常结果，不是此前IO的exit0产物消失事件。

## 6. 封存与边界

[核心闭包回执](<CORE_RECEIPT.json>)、[host资格](<HOST_QUALIFICATION.json>)、[总验证](<VALIDATION.json>)、[INDEX](<INDEX.json>)与[MANIFEST](<MANIFEST.json>)分开报告源码/接口、host实际执行和物件事实。最终复核746旧文件未变；无旧seal/blocked IO改写、physics/GPU/Git/新agent/BSP/刷写、C3在线actuation或父goal更动。所有attempt源/日志/可执行文件保存。

即使默认缺可信contact，本包仍提供可复用的DISARMED/ARMING、unknown退化、错误分级、fault latch和严格reset保护；它没有把默认unbound动作变成实机执行许可。
