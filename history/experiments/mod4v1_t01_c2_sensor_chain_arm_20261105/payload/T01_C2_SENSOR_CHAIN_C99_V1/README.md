# C3估计器 → C2请求力矩：C99接线与新增源文件ARM编译

[接口](<pc2_sensor_chain.h>) / [实现](<pc2_sensor_chain.c>) / [预声明协议](<build001/protocol.json>) / [本轮实际结果](<build001/result.json>)。

## 这次接通了什么

pc2_sensor_chain_init接收已有pc3_estimator_config，显式声明SUPPORTED_UPRIGHT或STATIC_GRAVITY估计先验，并选择是否启用C2内部航向环。这个初始化不产生电机arming/enable报文，不代表自然摊卧起立。

pc2_sensor_chain_step只做两次原有调用：

1. [pc3_estimator_update](<../SPR_AUDIT/portable_control_v3_current/pc3_estimator.c>)：读取规范化pc3_packet，输出已有V4派生C估计器的状态/年龄/视图。
2. [pc2_balance_step](<../T01_C2_TORQUE_C99_V1/pc2_balance.c>)：生成所选nominal C2的外环requested load-side Nm。

组合输出保留估计和控制各自valid/时间戳。普通故障贯穿锁存，估计器armed清零，再次初始化才恢复；这只是软件状态，实际驱动失能仍需调用者执行。NULL/alias前提错误不更改对象，调用者必须检查返回码，勿只读旧valid。无driver回调、enqueue、CAN、物理enable/disable或真实反馈发布者。

**没有照搬旧pc3_cycle的外环DC预裁剪。** 原PD目标反解→D4→当前PD→有符号DC的实际执行顺序仍留给驱动，避免在C2前又多加一层裁剪。此接口不是pc3_cycle或BSP的直接替换。

## 原生新接口检查：已实际运行

- GCC C99 -O2 -Wall -Wextra -Werror -fno-fast-math，编译exit0/执行exit0。
- 两种航向配置分别128个新合成mean窗口，共256个；另有2个相同packet的held-view查询，总计258次正常控制。
- 与**同一C3估计器＋同一C2后端直接分两步调用**比较，state14和六轴力矩差均为0。此项验证接线，不是第二个独立算法oracle；前一阶段Python数学对照见[2300行结果](<../T01_C2_TORQUE_C99_V1/validation001/result.json>)，本轮未重跑它。
- 新接线层的mean错误、过期、重复控制周期、同epoch变载荷、控制输入NaN均贯穿锁存；还有显式先验失败、NULL/alias不改对象检查。共7001条断言（主要是逐元素/逐调用检查），不是7001个独立故障样本。
- 合成count=20/10ms是元数据声明，不是采集5120次物理创新。没有collector或异步通道同步实现；packet端点一致也不代表所有通道瞬时同时采样。
- host状态904B/结果368B，原生整批0.174722s含检查和进程输出，不是单步WCET或ARM性能。

## 新源文件ARM编译：6/6对象

现有[armclang.exe](<C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe>)实际编译，C99/O2/Wall/Wextra/Werror/fno-fast-math：

| 目标参数 | sensor_chain对象 | balance对象 | reference对象 |
|---|---:|---:|---:|
| cortex-m4 / Thumb / fpv4-sp-d16 / hard-float | 2068B | 8672B | 6516B |
| cortex-m7 / Thumb / fpv5-sp-d16 / hard-float | 2072B | 8668B | 6516B |

每个新对象只检查52字节ELF头：ELF32 little-endian、ET_REL=1、EM_ARM=40。表内为对象文件大小，不是Flash代码量/堆栈/WCET。M4/M7是本次接受的目标编译选项，非对真实板卡CPU的发现或绑定。

没有最终ARM链接、目标运行、实时量测、驱动/BSP/功率/内环接线或HIL；旧CTK/C3源码未修改，旧ARM证据不冒充本轮完整系统链接。所有二进制仅路径/大小/未知SHA索引，不为归档重读payload。

本轮0物理步、无旧case/holdout/新K/第四控制候选，未操作试玩或V3观看进程。T01原严格接触门、三候选计数、J200落地失败和整机缺口均保持原结论。
