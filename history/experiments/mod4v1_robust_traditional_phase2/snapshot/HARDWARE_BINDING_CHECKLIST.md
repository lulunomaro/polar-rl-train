# 双板部署绑定表：已知证据与待实测字段

当前是独立传统控制保底工程。数学内核/模型评测/ARM编译/板级链接/实车是不同证据层级，不能互代。[任务范围](<TASK_SCOPE.md>)与[SPR固件审计](<SPR_AUDIT/SPR_DEPLOYMENT_AUDIT.md>)保持有效。

## 已知而非猜测

|项|当前结论|证据性质|
|---|---|---|
|腿执行器|4×DM8009P/DM-J8009P-2EC，24V、内部9:1；仿真峰40Nm、持续20Nm|型号/工程参数，非实测热曲线|
|轮执行器|2×DM3519/DM-S3519-1EC，总rotor-to-wheel15.8:1；不是19.2032再乘15.8|当前模型合同/用户机械映射|
|轮端接口|仿真wheel-endNm/rad/s；MJCF gear1不代表机械1:1|接口语义|
|轮半径|CAD凸包最大径向.063699998m；硬件nominal.0625m|都不是实测滚动半径|
|候选板|用户保留大疆C板或达妙板两路径|最终型号未绑定|
|SPR参考板|DM02/H723VGTx chassis；DJI C/F407IGHx gimbal|参考工程，不自动成为本车选型|
|现有编译器|C:/MinGW/bin/gcc.exe(host32)；C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe(ARM6.10.1)|实际已调用版本；不是目标运行证明|

## 部署前必须明确绑定

- 实际板型/PCB版本、MCU完整型号、时钟、FPU/ABI、Flash/RAM/栈预算、RTOS/中断优先级、控制时钟和watchdog。
- 每个电机的CANbus、ID、RX/TX协议/模式、标准或扩展帧、波特率、DLC、healthbits、故障码、反馈刷新率与timeout。
- DM3519真实固件接口：电流/转矩/速度模式、编码器/转速是否rotor或wheel域、内部是否已经折算旧减速比。不得照抄SPR3508帧或重复乘齿比。
- 四关节相对CAD的正向、zerooffset、角度/速度单位、绝对角与连续圈、双编码器选择；轮轴正向、rotor/wheel映射。
- Nm↔A/协议字段的实测映射、转矩常数/效率、母线电压、连续/峰值及允许持续时间、驱动限流、零速铜损、温度模型、回馈接收/电容约束。
- IMU物理安装位置/旋转、偏置/温漂/饱和/采样与时间戳、gyro/accel/encoder窗口时序。虚拟IMU[.03,0,.04]m不是实车标定。
- 已验证外部载荷/触地代理或额外传感器；ToF/台阶估计若未装配则保持unbound，不制造自动障碍输入。
- 独立输出守卫的唯一发送者、RX快照原子性、队列接受/上总线/实际执行回执、过期normal队列清空和硬件输出门控落实。

## 软件约定（避免最危险的误接）

14state第4/6列是左右`crank−hip`，不是被动knee；四编码器顺序Lhip,Lcrank,Rhip,Rcrank；六转矩行序Lhip,Lcrank,Lwheel,Rhip,Rcrank,Rwheel。详见[schema勘误](<reports/STATE14_SCHEMA_ERRATUM.md>)，wheel-firstHAL只能显式映射。

[观测C1](<SPR_AUDIT/portable_core_v1/README.md>)对应冻结R00数学，不代表当前V4的高频窗口/innovation gate/upright先验已经移植；[FK/LQR C2](<SPR_AUDIT/portable_core_v2_kinematics/README.md>)与[QP C1](<SPR_AUDIT/portable_mpc_qp_v1/README.md>)是独立kernel证据。新版QP与ARM对象构建在各自新目录推进，完整板级链接与HIL另验。

机械功率Στdq尤其不含堵转I²R；不能把现有机械功率分预算函数当电池/温度保护。驱动门控callback的mock返回成功也不证明实物已停转矩。

绑定清楚之前，工程保留抽象HAL与可审核内核，不生成冒称可刷的板卡BIN、不执行刷写。未知项以unbound显式保留。
