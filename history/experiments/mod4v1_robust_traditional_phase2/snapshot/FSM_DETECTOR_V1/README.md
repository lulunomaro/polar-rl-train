# FSM Detector v1 — 传感器限定的分层模式原型

**纯Python检测/FSM＋C99接口proposal。63个合成host单测通过，非机器人episode、跳阶、恢复控制、ARM、实时或实物资格。** 本包所有阈值/时间窗/目标姿态均为 `proposed_engineering_not_user_acceptance`。默认jump/recovery/自动障碍动作未绑定、关闭。

## 文件与现有结果

- [Python原型](<fsm_detector.py>)：标准库，接触proxy融合、时序/故障分级、11模式、profile/关节参考阶段；无模拟器或板卡依赖。
- [合成单测](<test_fsm_detector.py>)、[append-only执行器](<run_host_checks.py>)。
- [C99纯接口proposal](<fsm_detector_v1.h>)、[header smoke](<header_smoke.c>)：只有声明与契约，没有C FSM实现；`-fsyntax-only`通过不等于C运行时通过。
- [最终单测结果](<attempts/003/RESULT.json>)：63 methods，0失败/0error，1042次合成FSM调用，覆盖全部11状态。不是63或1042个机器人episode。
- [首次失败及源码](<attempts/001/RESULT.json>)、[原日志](<attempts/001/python_unittest.log>)、[错误/修正说明](<ERROR_REPORT.md>)完整保留；[第二轮61/61](<attempts/002/RESULT.json>)也保留，不回写成最终版本。
- 最终源码/输入约定/每轮SHA见[INDEX.json](<INDEX.json>)和[VALIDATION.json](<VALIDATION.json>)；默认值单列[PROPOSED_THRESHOLDS.json](<PROPOSED_THRESHOLDS.json>)，不是验收合同。

## 最小API

在Task根目录使用同一模块名导入；一个持久实例只由单个控制owner调用：

```python
from FSM_DETECTOR_V1.fsm_detector import (
    DetectorFSM, Config, SensorFrame, Command, ProperReference, CORE,
)
detector = DetectorFSM(Config())
t = 0.0  # 相对、单调秒；调用方对齐时钟，不用墙钟跳变
packet = SensorFrame(
    timestamp_s=t, valid_bits=CORE,
    rpy_rad3=(0., 0., 0.), omega_rad_s3=(0., 0., 0.),
    proper_acc_m_s2=(0., 0., 9.81),
    proper_reference=ProperReference.CHASSIS_ORIGIN,
    encoder_q4=(0., 0., 0., 0.), encoder_qd4=(0., 0., 0., 0.),
    command=Command(timestamp_s=t),
)
choice = detector.step(packet, now=t)
assert choice.hard_inhibit  # 默认DISARMED；这不是电机报文
```

调用参数名为`now`；更普遍的写法是`detector.step(packet, now_s)`。主packet的AHRS/omega/proper/4encoder/qd须预对齐到`timestamp_s`；不同IMU/encoder acquisition时刻由上层重新对齐或撤销valid位，本原型不偷偷消除已知0.5ms/10ms错位。force/motor/front各有独立timestamp。

`SensorFrame`是slots/frozen数据结构，未知`root_world_xyz`、`contacts`等kwargs不在schema内；dict也不是可用frame。此接口没有root/world pose、world velocity、MuJoCo contact、geom id、障碍顶面truth。

### 坐标、四关节顺序与单位

- chassis x前/y左/z上；`rpy_rad3`为AHRS roll/pitch/yaw，`omega_rad_s3`为chassis-frame角速度，不是Euler角导数。
- `encoder_q4/qd4`和所有q4参考顺序：**Lhip,Lcrank,Rhip,Rcrank**，输出侧rad/rad_s。
- 这里crank是绝对关节角；不是crank-minus-hip delta，也不是闭链被动knee。父若从nominal state14/gain取pose，要显式把delta加回hip得到crank。
- `Command`含timestamp、arm/disarm/estop、forward/yaw命令和单调`jump_event/recovery_event/reset_event`。held事件ID不会重复触发。
- 这里没有torque6、CAN、BSP回调或发送许可。`hard_inhibit=True`须使调用方走既有零/失能路径并立即返回，而非继续正常controller路径。

### 可选输入与未知值

```python
ForceProxy(timestamp_s=t,
           normal_N2=(None, None), confidence2=(0., 0.),
           provenance='nominal_model_nottruth_unvalidated')
```

未知force用None/低confidence，不填假0N。只有新鲜、非负、显式provenance且confidence达到拟议门槛的proxy才参与每轮on/off迟滞。连续窗按新sample timestamp累计：重复样本不赚dwell，长gap重置候选，过期/负/NAN/缺项退unknown。`PARTIAL`与双轮supported分开。

ForceProxy来源应是声明域和标定范围的legmotor/force模型；prototype不会证明该来源真实或校准正确。测试中的70N/0.95均为合成fixture，不是模型标定。Parent已有真实设备接口的motor torque域/传动、spring/惯性/DR不确定性另行绑定。

`MotorFeedback`可含current_A6、temperature_C6、power_W+PowerKind。阈值默认None，输出reasons明确`*_LIMITS_UNBOUND`或`*_MONITOR_UNAVAILABLE`。配置`required_motor_bits`才把对应失联提升为核心丢失计时；必需monitor的阈值也须绑定。电流取绝对值；当前power limit检查正motoring功率，负regen没有独立预算，仍需下层电源/再生保护。机械功率proxy和实测bus电功率分开，kind冲突降级，不假作电功率。

`FrontObservation`需typed kind、正observation_id、range、step_height、两个sigma及timestamp。`front_sensor_bound=False`是默认值；纯近距或UNKNOWN分类不推断台阶。可观性不足/不确定度大/过期时不自动approach或launch。同一observation_id在approach结束/超时后不自动反复尝试。

## Proper acceleration与飞行可观性

`proper_reference`必须明确：IMU_SITE、CHASSIS_ORIGIN、WHOLE_ROBOT_COM或DECLARED_OTHER_POINT。OTHER视作尚无COM模型，而不是自动把它当COM。

**ORIGIN proper norm不是freefall判据。** 从IMU补到chassis origin后，绕偏置COM/轮中心旋转飞行时origin可有非零向心/切向specific force；即使origin范数偶然0，也不自动判FLIGHT。代码不从omega/4encoder凭空推全机COM或alpha/杆臂项。

COM-freefall候选只有同时满足以下条件才参与：

1. 明确`WHOLE_ROBOT_COM`参考点；
2. `lever_com_confidence`与`com_force_model_confidence`达到拟议门槛；前者包含moving-COM的alpha×r、omega×(omega×r)、2omega×r_dot、r_ddot以及相关时序/不确定性，而非只有O→IMU平移补偿；
3. Config显式`enable_com_freefall_evidence=True`（默认False）；
4. 新鲜、可信proper低范数持续窗。高COM范数不凭空证明wheel接触。

force模型与COM模型冲突时返回UNCERTAIN/DEGRADED。没有可靠force/COM模型时返回unknown，而非读取truth。

`FLIGHT`是proxy/model支持的“轮未承载/自由落体样候选模式”，不是已证明所有机器人表面都离地：非轮碰触、外部支承、force模型误差仍可混淆；`LANDING`同样是estimated support恢复，非实际顶面/跨边缘资格。没有足够可信观测时退DEGRADED，撤掉关节阶段参考。

## 状态/分层行为

|状态|进入或主要规则|输出概念|
|---|---|---|
|DISARMED|boot/显式disarm/合法fault reset|INHIBIT；无q4参考|
|ARMING|显式arm边沿，等新鲜核心、支撑、姿态稳定窗|INHIBIT；超时DEGRADED，需disarm/rearm|
|BALANCE|arming稳定或恢复/landing稳定后|BALANCE profile；无自主q4轨迹|
|DEGRADED|soft超限、接触unknown/partial、感知/输入退化|LIMITED profile；核心失效时INHIBIT；无q4阶段|
|RECOVERY|显式启用+绑定恢复参数，manual事件或启用auto-recovery|绑定pose的五次blend参考；支撑不确定即停阶段；超时锁存|
|STEP_APPROACH|绑定typed前方感知，显式启用approach|STEP_SLOW；未启用/绑定jump不launch|
|PRELOAD|manualjump或typed-step且显式启用/绑定|PRELOAD_RAMP；支撑丢失/不确定撤销|
|PUSH_OFF|preload持续时间到达|PUSH_EXTEND；没有观测到unload时超时降级，不用时钟假装起飞|
|FLIGHT|可信proxy持续unload或受控COM候选|绑定才有FLIGHT_POSE；未绑定INHIBIT；unknown转DEGRADED；超时锁存|
|LANDING|估计支撑恢复|LANDING_COMPLY；稳定窗后BALANCE；无支撑/unknown另处理；超时锁存|
|FAULT_LATCH|硬故障、严重超限/倒地、核心失联等|终端硬返回；INHIBIT/NONE/expected_q4=None；不跌落到正常输出|

每个周期先检查hard故障，fault reset调用也只回DISARMED，不在同周期arm/launch。reset需新的reset_event、disarm且arm=False、可信健康稳定窗；held旧reset不在日后自动清锁。正常disarm不假作估计器故障，但既有FAULT不由disarm单独清除。

时钟倒退/未来timestamp、schema/非有限核心、driver fault、硬电流/温度/功率/倒地为latch；soft age、soft电气持续窗、较小倾角/角速率超限为DEGRADED；persistent必需输入缺失有独立fault timeout。optional未知观测不假为正常。

## Jump/recovery显式绑定

默认所有自动/手动jump/recovery均False；JumpBinding/RecoveryBinding均None。prototype只在`execution_context='simulation'`或`'synthetic_fixture'`且profile/envelope已绑定时接收launch/recovery enable。auto-step launch还需显式approach enable＋front binding＋typed高度范围和uncertainty门槛。

JumpBinding包含4个阶段q4目标、joint_min/max_q4和binding_id；RecoveryBinding类似。config向量用不可变tuple。初始测量pose在拟议envelope外时不启动该轨迹；每阶段以入口encoder pose为起点，给五次smoothstep期望q4。它不是优化轨迹、完整运动学、扭矩/jerk/碰撞可行性证明或硬件动作包。

launch gating用低命令、低omega、upright、estimated双轮支撑；**低命令不等于低实际平移速度**。当前输入没有一项可直接证明站停，因此自动launch仅为显式Sim试验候选，仍需父闭环/状态估计可观性、控制器handover、制动/功率/机械域验证。程序不输出jump_success/step_success；回到BALANCE也不是跳过270mm。

## C接口与既有gate的关系

复用了[既有gate“先清输出、故障锁存并立即return”契约](<../SPR_AUDIT/portable_core_v1/ct_core.h#L128-L140>)，没有修改或替换该C包。本包C header只有proposal：opaque context的storage/alignment、status/reason位登记、ABI及native FSM函数实现仍待新C移植。host smoke只检头文件语法/数组布局声明，未link/执行这些声明。C时间提议用uint64微秒，与Python相对秒在显式adapter转换；不假设字节ABI兼容。

Python实例应持续保存latch，不要每tick重建对象；单owner，非线程安全。更低层现有CAN freshness/queue/torque/power gate仍单独保留，不由FSM profile替代。

## 复现与封存

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B .\run_host_checks.py
```

该命令每次建立新attempt目录并在执行前保存source副本/SHA，记录原样unittest与C syntax日志，无physical step、SDK、真实IO、SSH或Git。本轮最终attempt003全部通过；旧失败留在001。1e−12秒只用于相对float时间deadline比较的表示余量，不是机械容差或用户验收门槛。

当前所有数值保持proposed engineering；父闭环、正常H1/H2、270mm、完整RM、真实板、传感器校准、C runtime和WCET不在这些host合成结果的证明范围。下一CONTACT_PROXY_NOMINAL_V1另建模块，本包封存后保持字节不动。
