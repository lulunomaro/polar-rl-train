# Native C MPC supervisor V1 — 独立in-process新功能

**新C核心、host C/C++接口与数值资格已完成；新ARM物件事实单列。** 直接链接sealed ASQP，不是blocked IO修复、替代传输、worker、完整C3最终enqueue或实机MPC。未执行physics/GPU/Git/agents，父goal未改。

## 交付与接口

- [公共API](<nm1_supervisor.h>)：`nm1_init`、`nm1_select`；`nm1_check_solution`为生产同用的纯证书复核，不求解/替换候选。
- [监督核](<nm1_supervisor.c>)、[const模型](<nm1_model.c>)与[模型声明](<nm1_model.h>)；直接调用旧sealed [ASQP](<../ACTIVE_BOX_QP_V3/active_box_qp.c>)，不是另一套算法。
- [源码包](<nm1_source_bundle.zip>)含4件新源文件+2件逐字旧ASQP源依赖，保留sibling布局；[构建说明](<BUILD.txt>)。
- [核心回执](<CORE_RECEIPT.json>)、[host资格](<HOST_QUALIFICATION.json>)、[ARM物件报告](<OBJECT_SUMMARY.json>)三者分开；[清单](<MANIFEST.json>)给出主件SHA，[索引](<INDEX.json>)保留所有attempt。

```c
nm1_context context;       /* caller-owned; initialize once */
nm1_workspace workspace;  /* caller-owned, per concurrent caller */
nm1_output selected;
nm1_config cfg = { clock_now_ns, clock_context, 3000 };
/* check nm1_init result; populate typed input from valid C3 + same-packet drive */
nm1_init(&context, &cfg);
nm1_select(&context, &input, &workspace, &selected);
/* Check API result, valid, clock_valid, deadline_missed and caller's final
   deadline/driver eligibility. selected.valid alone is NOT permission to emit. */
```

输入为已经产生的C3 `STATE14/REF14/MATH_TAU/GUARDED_TAU/SHAPER_V` float值和同包drive6；不把日志estimated state当新传感器。数学row6是LH/LC/LW/RH/RC/RW，未知物理前后、符号、减速比和CAN绑定仍未补造。显式epoch相等是新typed guard，不是采样/新鲜度硬件证明。

`box_valid`仅表示诊断端点可用finite f32表达，不承诺交集非空；反向端点仍走`NO_BOX`回退，只有实际accepted字段表示本模块候选提交。

Host实际sizeof：context **272B**、workspace **5896B**、output **288B**；不是ARM栈或总RAM测量。无heap/VLA/内部mutable global。输入/ctx/workspace/output必须disjoint，alias返回的重叠output不可用，调用方须inhibit。typed坏配置/上下文/非finite输入是zero-invalid扩展；与正常valid C3的独立GUARDED fallback区分。

## 监督语义

[完整映射](<SEMANTIC_MAPPING.md>)对照未修改的父[Python v2](<../../C_ACTIVE_MPC_SUPERVISOR_V1/supervisor_v2.py>)：

- N15、fixedleg8+nominal-lag9、H32与既有真实H15逐bit相同；tolerance仍float32(.002)，64全局pivots，不正则、不调参。
- 仅改变两轮common，保留MATH_TAU的yaw差；signed四象限DC先做原速度preclip，再求common交集、向内f32量化。当前点box冻结全N15，不是未来电压/能量/接触/状态约束。
- abs(yawrate)>2或abs(pitch)>.25、disabled、latched、空交集、nonfinite梯度、真实QP nonconvergence和超时均回到原C3 GUARDED六输出；无效base立即zero/invalid，不调用QP。
- **fixedleg ground模型的yaw/pitch域检查不是可信ground/flight判定。** 实际caller遇operator跳跃、预测腾空、非normal模式或contact许可未绑定时，必须显式`enabled=0`；小pitch不等于接地许可。此禁用只退出本模块MPC，最终caller仍须按实际模式/许可决定是否使用C3 fallback或inhibit。本轮未提高COM/FSM confidence cap。父R39 mini-hop属于独立Python手动timer实验，未接本MPC；未读取其GT/触地信息，也未用于本模块门槛或调参。
- 独立GUARDED float→double精确提升，不经QP workspace或失败iterate。返回selected torque6为double，避免再量化改变父Python点guard语义。
- caller double projected KKT另算，必须同时满足unchanged .002上界/可行性；固定bound坐标投影KKT0。certificate/clock fault锁存MPC路径，显式init重置；预期nonconverged/deadline不自动锁存，也不接受private iterate。
- warm和accepted只在最后deadline poll通过后提交；最后过期/clock fault则恢复全部6个GUARDED、accepted_z全零、warm不变。fallback的last_u仍按父语义更新为返回两轮平均。

## 算术与真实数值结果

[预算](<NUMERICAL_BUDGET.json>)在首C执行前注册：[freeze日志](<freeze_01.log>)。0step const导出 `f=Mstate*state9-Mref*ref8-Mv*shaperV`，**运算次序改变，不作一般bit-exact承诺**；最终f仍f32。数据payload **4068B**，不含编译对齐/目标代码。通过读取host COFF和两种ARM ELF符号实际字节，H和全部映射const bits均等于导出：[compiled-data proof](<COMPILED_DATA_PROOF.json>)。

[对照结果](<COMPARISON.json>)、[逐帧表](<FRAME_COMPARISON.csv>)：**3717帧、0预算/选择/计数/latch差异**。

| 新固定数据 | 数量 |
|---|---:|
| 既有C3已保存reply+原同包drive | 3200 |
| 独立固定seed代数tuple（非P25/robot trajectory） | 512 |
| invalid/disabled/domain/overspeed分支 | 5 |

所有实际QP调用的原H/f/box/shifted-warm/tol/pivot/预算在本cohort逐bit一致；compressed f的实测bit-diff **0**。tau/warm/last_u max error **0**，caller-double KKT重算次序差最大 **2.7000623958883807e-13**。参考方法为未改父v2重放**实际新native ASQP回答**并检查它构建的原问题和独立KKT；由于每个实际调用输入相同，未偷换问题或用oracle调H。该方法不是额外第二次solver运行；另有36个旧真实H15 cold/warm直接新调用，与旧已封status/pivots/z/upper逐bit一致。

真实分支分布：**1510 accepted、1676 domain fallback、334 nonconverged fallback、195空交集、1 invalid base、1 disabled**。334份均保留在[未收敛明细](<ALL_NONCONVERGED.json>)：295 MAX_PIVOTS、20 NO_PROGRESS、19 CYCLE，没有补成成功、改tol/cap或拿iterate控制。

[首host运行](<host_run_01.log>)共 **84531检查/0失败**（包括逐帧、36旧H、typed与时钟，不是84531个独立机器人场景）。[实际C++调用](<cpp_run_01.log>)通过。新测试二进制保留并校验PE32/i386及SHA；不是恢复旧被删除exe。

## 时间：最后poll只是已观察事实

调用者提供外部`cycle_start_ns`，可以早于C3。显式availability+monotonic u64-ns callback；所有valid-base路径最后poll，invalid-base与父源一致直接返回。PRE_QP计算余下floor微秒交给kernel；START adapter用已观测PRE_QP微秒epoch作保守种子（仍检查真实START raw ns），后续kernel poll为raw ns/1000，包含入口开销且floor可不足2us提前截止。该seed不是新START硬件读数。

[45个插点](<CLOCK_INSERTIONS.csv>)覆盖7 native阶段及9 sealed kernel阶段（kernel phase合并为其中1 native阶段），每处deadline/rollback/unavailable。真实FULL_FACTOR在 **1/120 cell**、FACE在 **121 total cells** 中断；START/VALIDATE deadline **0 factor cells**。最后poll过期恢复6输出，warm/accepted不提交。u64大于2^53及MAX边缘整数已测试。

clock错误终止时的UINT64_MAX/0 poison仅让sealed kernel退出，外层clockfault必定discard/latch；该路径kernel时间stats不当实测。正常剩余预算、raw最后时间与选中状态分开。返回后的copy/调度/driver、真实driver-rate envelope、C3最终enqueue、完整3ms/WCET均未覆盖。**valid fallback也不是新的按时发车资格**。

## ARM仅compile-only

[首build](<ARM_BUILD_01.json>)新2源×M4/M7 **4/4 objects**，严格warning-as-error：

| 候选 | supervisor对象 | const model对象 |
|---|---:|---:|
| M4 fpv4-sp-d16 hard | 13400B | 5084B |
| M7 fpv5-sp-d16 hard | 13392B | 5084B |

ELF32 LE ET_REL EM_ARM、ARMv7E-M/Thumb、VFPargs1，__ARM_FP0x6、DBL_MANT_DIG53/double8、FLT_EVAL_METHOD0。SP-hard是ABI，**不是SP-only算术**。真实未解析项包含`__aeabi_d* / __aeabi_f2d / __aeabi_d2f / __aeabi_uldivmod / __hardfp_fabs/fmin/fmax/nextafterf`、ASQP与模型符号；精确列表及SHA在[物件报告](<OBJECT_SUMMARY.json>)。未做BSP/soft-double/libm目标链接、ARM执行、FPSCR/FTZ/栈/WCET。

## 封存边界

[错误与边界记录](<ERROR_REPORT.md>)保留一次只读不存在路径查询；本模块首strict build、首run、首对照和首ARM build均实际通过，未抑制warning、未重命名/修改防护。旧blocked IO仍BLOCKED，未运行SDK或旧worker。新源与测试only在本目录；[最终验证](<VALIDATION.json>)核查924旧文件和13源引用哈希未变。该新功能不阻断其他已授权组件工作，也不扩展旧PH2/PH3/物理结论。
