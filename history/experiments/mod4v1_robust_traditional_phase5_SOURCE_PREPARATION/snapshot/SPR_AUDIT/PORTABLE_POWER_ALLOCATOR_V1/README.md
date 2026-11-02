# PORTABLE_POWER_ALLOCATOR_V1 — 独立 native 数学核

**交付：固定6轴 C99 / C++ extern-C、caller-owned 内存、保守电功率包络分配；host 数学/typed/clock 与真实 C++ 调用已验证，M4/M7 仅编译物件事实。默认真实校准与电气绑定保持 UNBOUND → invalid。** 本组件未接父 R43/R44/R45 或任何机器人 episode；当前 PH4 cutoff 排除本组件，PH5/后续 pending。

## 入口与独立闭包

- [公共 API](<pa1_allocator.h>)、[C 实现](<pa1_allocator.c>)：`pa1_calibration_default / pa1_input_default / pa1_calibration_validate / pa1_init / pa1_allocate`。无 heap/VLA/内部可变全局；context/workspace/input/options/result 与整个 callback-owned range 保持互不重叠。context/workspace 属于本次独占调用，callback/其他线程不接触它们。
- [源码包](<pa1_source_bundle.zip>)：两个运行源码 + [BUILD](<BUILD.txt>) + 原始 [模型合同](<MODEL_CONTRACT.json>) / [预算](<NUMERICAL_BUDGET.json>)；不包含玩具校准 helper、旧机器人/IO 依赖或可运行机器人程序。
- [CORE receipt](<CORE_RECEIPT.json>)、[HOST qualification](<HOST_QUALIFICATION.json>)、[OBJECT facts](<OBJECT_SUMMARY.json>) 分立。最终 [VALIDATION](<VALIDATION.json>) / [INDEX](<INDEX.json>) / [MANIFEST](<MANIFEST.json>) 提供只读 SHA 闭包。

## 模型收窄与单位

原建议若把 R 当裸绕组电阻会漏算母线路径损耗：stall 1A、1Ω、路径效率 .8，需要母线1.25W而非1W。预注册 [架构](<ARCHITECTURE.md>) 与 [合同](<MODEL_CONTRACT.json>) 因此使用 **BUS-referred `Cbus_loss_upper_W_per_A2`**，不是直接填 winding ohms；其他未覆盖损耗由 `electronics_other_upper_W` 的已证明上界覆盖。所有系数/温度/电压/电流约定、四象限与齿比/符号证据由 caller 提供，代码无硬件猜测。

对同一 load-side Nm / rad/s 坐标的六轴，包络为：

```text
I_i = abs(tau_i) / Kload_lower_i
Pplus = Σ(max(tau_i*wlo_i, tau_i*whi_i, 0)/eta_drive_lower_i
          + Cbus_loss_upper_i*I_i²) + Pelec_upper
Pcharge = Σ(max(-tau_i*wlo_i, -tau_i*whi_i, 0)*eta_regen_upper_i)
Idischarge = Pplus/Vlo; Icharge = Pcharge/Vlo
```

正功率不抵扣回生。逐轴电流、正/回生功率、两种母线电流与 signed-DC box 均约束，Vhi 同样落在校准电压域。`Kload_lower` 的绑定必须支持预算所用电流量的上述上界关系，裸名牌 Kt 或仅 iq 关系不自动证明总相电流；未覆盖的励磁/空载分量、转矩跟踪、瞬态储能、其他充电源等仍需相应域/整包络证据。缺证据保持 unbound。精确 oracle 检查的是**声明包络函数**，不是实测电池/绕组电气行为；RESERVE_INFEASIBLE 的证明也限于这个模型可行域。

## reserve 优先、搜索与故障

- caller 明确给出 τ0 reserve 与 τ1 request，均有限、处于同一 fresh signed-DC box；没有零 reserve 默认值或隐式 request clamp。独立输入始终保留。reserve 违反模型约束 → `RESERVE_INFEASIBLE`；区间舍入跨界 → `RESERVE_UNCERTIFIED`；两者均 invalid，不缩减 reserve。
- τ1 认证通过则 `s=1`、六轴请求的 binary64 bits 原样返回（含 `-0.0`）。否则沿 `τ0+s*(τ1−τ0)` **固定40次二分**，保留已认证下端。上端仅表示 NOT CERTIFIED，不表示真实物理不可行。区间同时包住精确仿射点和实际舍入 torque tuple，最终重认证后才提交。
- `valid=0` 时 s/τ6/accepted certificate 清零，保留 status/stats 与明确非接受的 reserve diagnostic。**invalid 零 payload 不可当作超速制动 box 中的零 fallback。** 上层保有独立合格 fallback 或 inhibit；输出本身无执行许可。
- structural/nonfinite/alias/stale/clock/numeric 等锁存至显式 init；普通 deadline、reserve infeasible/uncertified 和 invalid frame 不宣称永久硬件故障。若输出与源对象 alias，函数返回 alias 错误而不破坏输入，重叠输出本身不可使用；context 与输入重叠时也不为写 latch 而破坏源。
- 外部 cycle_start 可早于入口；所有源时间/valid-until 与校准有效域在 monotonic available u64 ns 时钟下检查。每次评估/逐轴、二分和最后提交 poll 均显式。最后一次超时/时钟故障仍 invalid。合作式 poll 不是抢占、MCU 时限或返回后 driver enqueue 覆盖。

## 实际已运行的有界证据

[原始219 case](<CASES.json>) = 27 named + 192 固定种子独立 random；[精确 Fraction 80-step oracle](<REFERENCE.json>) 在 C 执行前生成。原 fixture 与预算两次 source revision 均未改。[canonical comparison02](<COMPARISON_02.json>)、[逐 case 表](<RUN_COMPARISON_02.csv>) 与 [原始 C 输出02](<C_RUNS_02.jsonl>)：

| 项目 | 实际结果 |
|---|---:|
| C 数值 / exact-reference 检查 | 38,508 / 0 failure |
| 逐 case 实际输入111分量 bit 校验 | 24,309 / 0 mismatch |
| valid / reserve infeasible / reserve uncertified | 209 / 7 / 3 |
| valid well-conditioned cohort | 204，s error gate 2e−9 全过 |
| 全 valid 最大保守 s-gap | 9.09547045709151e−13 |
| 最大 interior line 表示误差 | 8.369632669459584e−16 Nm |
| 全端点 s=1 | 39，六轴请求 bits 全保留 |
| 实际 tuple + 精确仿射点的声明模型/box 违规 | 0；违规容差为0 |
| native typed/alias/freshness/finite/clock | [2,290 checks / 0](<native_run_02.log>) |
| deadline / rollback / unavailable 逻辑插点 | [36 rows](<NATIVE_CLOCK_CASES_02.csv>)，全 invalid |
| 实际 C++ 调 C object | [extern-C PASS](<cpp_run_02.log>) |

[10个 invalid 原始记录](<ALL_INVALID_02.json>) 全保留：3个数学 reserve 可行但保守区间未认证的边界不升级为成功，其中原非零制动/回生 box 的 reserve 恰在 charge boundary。near-flat/退化情形不作统一真实最优 s 误差承诺；二分 bracket≤2⁻⁴⁰ 和已声明的 well-conditioned gate 不是同一命题。

host `sizeof` context/workspace/result/input = 488/672/464/608 bytes，只是 MinGW i386 布局，不是 ARM 栈或实机内存/WCET测量。[HOST_BUILD02](<HOST_BUILD_02.json>) 保留实际 argv、objects/exes SHA 与日志。

## 首轮失败仍为失败

[ERROR_REPORT](<ERROR_REPORT.md>)、[COMPARISON01](<COMPARISON_01.json>) 与 [native01](<native_run_01.log>) 记载首轮 2,290/1：`a==b` 数值相等的快捷分支先于 `s==1`，把 requested `-0.0` 返回为 reserve `+0.0`。完整219输出独立 grade 有3个 endpoint-bit gate 失败（同一 case 轴0/2/4），无模型/区间认证违规。首轮 C++ 仅编译、未执行。原源码/objects/exes/[raw01](<C_RUNS_01.jsonl>) 均留在 [首轮目录](<host_attempt_01/pa1_allocator.c>)，没有覆盖为通过。revision02 **仅**把 s==1 分支提前，测试源码/219 fixture/预算/认证公式完全不改；两轮差异在只读 [分析 receipt](<ANALYSIS_RECEIPT.json>) 中核对。

## ARM 物件事实与未绑定项

[ARM receipt](<ARM_BUILD_01.json>) 和 [OBJECT JSON](<OBJECT_SUMMARY.json>) / [CSV](<OBJECT_SUMMARY.csv>)：新 M4/M7 各1 object，23,324 / 23,084 bytes；ELF32 LE ET_REL EM_ARM、ARMv7E-M Thumb、VFP args1、HardFP use1、`__ARM_FP=0x6`、binary64 mantissa53 / double8 / FLT_EVAL0。**SP-hard ABI 不等于 SP-only arithmetic**；物件确有 AEABI double/memory 与 hardfp fabs/fmax/fmin/nextafter unresolved helpers。

没有目标 libm/helper/BSP link、ARM 数值执行、FPSCR/gradual-underflow、stack/ISR/WCET 验证。M7 fromelf 的 FP_arch8 文案是 FP ISA 标签，CPU 仍为 ARMv7E-M；denormal attribute 允许 FTZ 相关行为，物件成功不证明区间认证前提在目标上成立。

模块应位于实际 driver-rate、inversePD/D4/gain 等 torque-changing 处理之后；任何后续变换、跟踪误差、陈旧反馈或量化都需独立界限/复查。未提供实际电气/热/电池/HIL/板卡/CAN/稳定性或 C3 最终 enqueue 资格。没有额外物理、GPU、Git、agent、goal 或旧 blocked IO 行为；旧 1,151 files、26 source refs 与279 assets 的 SHA 在 seal 中重核。
