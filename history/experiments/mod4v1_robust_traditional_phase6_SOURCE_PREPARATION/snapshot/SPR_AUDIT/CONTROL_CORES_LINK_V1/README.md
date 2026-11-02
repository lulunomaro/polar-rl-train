# CONTROL_CORES_LINK_V1 — 构建共存验证，不是控制/发送链

**已保存的真实host完整链接、默认调用与ARM partial结果；最终封存见[VALIDATION](<VALIDATION.json>)、[receipt](<RECEIPT.json>)和[INDEX](<INDEX.json>)。PH6 pending。** 本组件没有把CB1/FSM/MPC/driver/Power接成事务，也没有最终发送许可。

## 固定来源与预算

[实际BOM](<SOURCE_BOM.json>)只含9个唯一当前runtime TU及13个header/inc，共22个原文件。按真实源码路径编译，不从任何source ZIP再取重复C3/C2。先冻结的[architecture](<ARCHITECTURE.md>)、[budget](<BUDGET.json>)和[prepare记录](<prepare_01.log>)保留；预算没有放宽。

| runtime组 | 唯一C translation units |
|---|---|
| CB1 | [candidate](<../PC3_CANDIDATE_BUNDLE_V1/cb1_candidate.c>) |
| C3纯数学/C2 | [estimator](<../portable_control_v3_current/pc3_estimator.c>)、[P25/DC](<../portable_control_v3_current/pc3_controller.c>)、[kinematics](<../portable_core_v2_kinematics/ct_kinematics.c>) |
| native FSM | [detector](<../portable_fsm_detector_v1/fd1_detector.c>) |
| native MPC | [supervisor](<../NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c>)、[model](<../NATIVE_C_MPC_SUPERVISOR_V1/nm1_model.c>) |
| ASQP / Power | [ASQP](<../ACTIVE_BOX_QP_V3/active_box_qp.c>)、[allocator](<../PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.c>) |

没有C3 dispatch、SDK/parser/worker/transport或实际send实现。C3公共头中的dispatch声明未被调用或解析成实现。

## 实际host结果

- 9个runtime源各仅编1次新C99对象；同9对象不变地用于完整C链接和真实extern-C C++11链接。两个NEW default smoke各只运行1次，分别**37 checks/0**，没有重跑旧3200/219/93等QA。
- [C stdout](<host/run_new_default_C.stdout.log>)、[CPP stdout](<host/run_new_default_CPP.stdout.log>)：CB1 candidate_valid0/send0、FSM inhibit1/disarmed、MPC valid0、Power valid0。新smoke只调用公共API，默认clock/contact/calibration/base全部未绑定；没有伪造许可或有效控制输入。
- [新smoke body](<co1_smoke_body.h>)用caller-owned固定存储，host aggregate22448B仅为测试聚合体sizeof，不是生产最小RAM、stack测量或target占用。C++直接调用各C公共API；与C probe的29个sizeof/offsetof/enum字段一致，仍不是完整跨板ABI或所有valid-path调用验证。
- [实际runtime nm](<host/nm_runtime_globals.stdout.log>)为45个强定义，重复0；内部kernel/model peer引用闭合。系统链接前剩余仅C99数学/CRT/整数runtime。两个完整PE32 i386程序真实运行通过。
- [C exe nm U](<host/nm_executable_undefined_C.stdout.log>)与[CPP exe nm U](<host/nm_executable_undefined_CPP.stdout.log>)仍列GCC可选frame-info/Java-registration CRT元数据hooks；审计单列原名，不伪装为零U，也不是缺失核API。见[host build](<HOST_BUILD.json>)与[统一审计](<COMBINATION_AUDIT.json>)。

## 实际ARM结果

| 目标 | 新输入 | 唯一partial combine | 结果对象 | 实际未定义 |
|---|---:|---:|---:|---:|
| M4 fpv4-sp-d16 hard | 9 runtime + 1 const ABI probe | 1次，exit0 | [133360B](<cortex-m4/control_cores_partial.o>) | 36系统项 |
| M7 fpv5-sp-d16 hard | 9 runtime + 1 const ABI probe | 1次，exit0 | [131156B](<cortex-m7/control_cores_partial.o>) | 36系统项 |

- 安装armlink6.10.1的[实际help](<armlink_help.log>)先确认`--partial`。真实组合用`--partial --no_remove --no_scanlib`，不引BSP或自动RT库；[ARM exact argv/receipt](<ARM_BUILD.json>)保留26条命令及输出，全部exit0。未重复link或改变编译设置。
- 两个结果均ELF32 LE **ET_REL**/EM_ARM，不是可启动固件。9核+probe强定义保留、无重复强符号、内部peer闭合；actual undefined各16个系统数学项+20个RT/CRT项完整列于[审计](<COMBINATION_AUDIT.json>)，包括double算术、memcpy/clear、u64转换/除法等。
- ARMv7E-M Thumb、SP hard参数ABI、enum32、float24/double53/FLT_EVAL0与29个const layout字段由真实对象/宏/attributes读取。SP hard不代表只有SP算术；FSM/MPC/Power的double helpers仍需库。M7 FP_arch8文字是FP ISA标签，不把CPU变为ARMv8。
- 未链接这些libm/RT helpers、BSP/startup或运行ARM。FP环境/gradual underflow、栈、ISR、时基、WCET、driver及完整控制性能均未验证。

## 首审计失败与边界

[首审计log](<audit_attempt_01/audit_01.log>)因分类表遗漏`__hardfp__fabsf`退出1，原script/log保留。实际安装[math.h:740–741](<C:/Keil_v5/ARM/ARMCLANG/include/math.h#L740-L741>)声明`_fabsf`为old ARM name且fabsf调用它；[证据](<TOOLCHAIN_ALIAS_EVIDENCE.json>)支持只补精确libm alias。仅重读saved对象做[第二审计](<audit_02.log>)，未改任何runtime/预算/flags，未再编译、link或运行smoke；不是隐藏构建失败或未知符号当作RT。

[小source/build ZIP](<control_cores_source_bundle.zip>)保留唯一22源closure、新smoke/ABI probe、固定buildscript/BOM/budget及构建说明；不含旧fixture或旧二进制。复现细节见[BUILD](<BUILD.txt>)，错误与尝试见[ERROR_REPORT](<ERROR_REPORT.md>)。

**candidate valid、FSM profile或Power证书均不是发送许可。** 本阶段没有contact许可绑定、driver preview、量化/enclosure、actual-held协调、unique final enqueue owner、完整总周期deadline或实机资格。0physics/GPU/Git/new agents/旧QA/blockedIO/goal变更；本新组合归PH6 pending，不回填既有cutoff。
