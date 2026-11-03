# MOD4_DEPLOYMENT_PORT_V1：派生工程与未绑定接口（第一交付）

**已产出实际工程文件和窄patch，不是仅审计；当前资格仅原bytes构建来源＋新C99 host接口，不是可刷写/上机固件。**

## 两项主产物

1. [BUILD_CLOSURE_FINAL.json](<BUILD_CLOSURE_FINAL.json>)：实际Keil target的原165成员、include/defines/库/startup/link/flash/hook事实；父supplement补齐17个active缺选成员及15个music header，现原165＋新2C/2header共169文件级齐备。Windows大小写alias6个，reachable lexical text368个；条件预处理、编译器builtin/Pack和opaque库ABI仍未验证。
2. [mod4_deployment_port_stage1.zip](<mod4_deployment_port_stage1.zip>)：独立[派生Keil工程](<derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx>)、427个derived文件、2个[before](<PATCH_RECEIPT.json>)、[可逆窄diff](<PORT_NARROW.patch>)、新C99 adapter/bridge、构建来源与host-smoke源码。原selected/source_original/ZIP不写，旧原型保留。

## 实际修改

- [chassis_balance.c](<derived/StandardRobotpp-balance1/application/chassis/chassis_balance.c>)：`cnt`改持久且初始化；`ConsoleStandUp`移除未赋值的`joint_pos_l/r`读取。仅拿本周期owned/valid **raw motor-coordinate qref4**，不把零数组默认当位置、不猜model→motor映射；同时核旧工程四轴limits。
- 同一文件在Console入口先capture/gate，SendCmd入口最后poll。OFF/SAFE请求STOP，普通三模式/STAND_UP以外先不开放。旧RUN内部FC自动使能被退役，ENABLE_ONLY由明确安装的action sink处理，六轴fresh enabled-ACK齐备才RUN。
- [mod4_port_gate.h](<new_code/mod4_port_gate.h>) / [C实现](<new_code/mod4_port_gate.c>)：caller-owned context；显式startup、manual arm、反馈age/fault/session/frame、qref cookie/epoch/finite/domain、clock/expiry检查，故障需显式重新init。STOP、DISABLE为不同请求枚举，MIT0不是FD。
- [bridge接口](<new_code/mod4_port_bridge.h>) / [实现](<new_code/mod4_port_bridge.c>)：单chassis-task owner，boot无services/config/clock/packet fallback。`mdp1_bridge_install/arm/stop`以后由经审BSP/provider绑定，当前无调用者自动安装/arm。缺qref不发position。
- 派生project另命名target/output，追加新module并关闭自动flash-before-debug/TargetDll flash选项；原F407/12MHz配置、旧leg gains、旧wheel PID、库路径不改。手动/外部flash不属于这些XML开关提供的硬件隔离。

## 已执行与未执行

- [HOST_BUILD_01.json](<HOST_BUILD_01.json>)：首次严格MinGW6.3 C99 build的3个新C TU及link均0，artifact保留；[首次smoke](<attempts/host_01/smoke.log>) **40 CHECK / 0 failure**，并且只运行这一次。toy绑定/时钟/反馈完全synthetic，不是MOD4参数。host sizeof context120/frame160/decision56，不是目标ABI/stack测量。
- 检查覆盖：默认UNBOUND/无FC、人工arm、startup未ready、qref缺失/NaN/Inf/坐标/域/过期、ENABLE_ONLY→ACK→RUN、STOP≠DISABLE、motor fault/stale/future stamp、clock rollback/last-poll expiry、latch、u64极值、bridge单次消费及最后poll失败撤RUN。没有新增旧QA或重复40check。
- [初始SOURCE](<SOURCE.json>)预先锁391 payload/7,724,844B，复制原bytes；[补选appendix](<SUPPLEMENT_APPENDIX.md>)/[receipt](<SUPPLEMENT_RECEIPT.json>)记录父批准32份/13,506,260B（含2个opaque库），保持初次[17-member请求](<NEEDED_MEMBERS.json>)和[闭包](<BUILD_CLOSURE.json>)不改。新[patch receipt](<PATCH_RECEIPT.json>)证明两份原文件逐字节可逆，其余389＋32继承文件不改。
- 原uvproj/bat/hooks/库算法/目标程序未运行；完整target build/link、CPP/ARM补测、CAN/SPI/flash、PHY/FK/旧QA/Git/新agent均0。没有静态解读opaque库ABI。三段原hook run0/name空，库存在不等于兼容或硬件许可。

## 界限与下一步

- 默认NONE只阻断旧chassis motor发送入口，不等于旧硬件已停住、位置保持或全固件全部CAN来源静默。STOP/DISABLE sink仅是接口请求，实际协议/确认/失联策略未绑定。
- 绑定bit是caller承诺，不是自动实测凭证；provider必须给真实时间、六轴质量/故障/ACK、model→motor坐标和qualified stop行为。对象disjoint、single-task owner是当前API前提；此40check不是任意pointer/并发/所有误用认证。
- 旧MF9025/LK不是MOD4 DM3519；generic DM±10Nm/旧normal±7Nm不是MOD4 joint±40物理绑定。新轮型号/固件/gear/ID/方向/零位/torque-current均未猜填。model代理sensor-only站起API尚未接入，也未选新leg gain。
- 最后poll只到旧send-loop之前，不覆盖逐帧发送、原子六轴、ACK、driver-rate envelope/量化、实际held反馈、发后deadline/硬件watchdog/WCET；完整链仍待后续任务。
- 下一单独审批按[NEXT_TARGET_BUILD_PLAN](<NEXT_TARGET_BUILD_PLAN.md>)审ARMCC5.06.422/Pack/short-enum/FPU/lib ABI/条件include与隔离compile/link，再决定目标构建。当前不执行该步骤。
- [RECEIPT](<RECEIPT.json>) / [VALIDATION](<VALIDATION.json>)只封存本阶段已发生的来源/patch/新host事实；初次闭包、补选、窄patch、host每个实际日志均保留，全部执行成功，未伪造target成功。
