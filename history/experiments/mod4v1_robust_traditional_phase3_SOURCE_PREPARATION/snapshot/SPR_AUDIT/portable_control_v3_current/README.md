# Portable Control v3-current — 冻结V4估计器 + 实际P25正常控制

**本包完成请求的阶段1+2数值移植。不是旧R00 C1改名，不是BSP/机器人固件；H2的nominal-K相对2D odom/τ20-cap1.8反馈明确留待下一独立版本。** 本包只输出同包FK/gyro lateral proxy诊断，没有把它接到控制器或当世界位置传感器。

## 1. 冻结来源与范围

[入口冻结](<SOURCE_FREEZE.json>)记录14个当前来源、221个旧封存source/产物/manifest快照，以及两个固定TRAIN流。主要依据：

- [sensor_core_v4.py](<../../sensor_core_v4.py>)：SHA `66a9d505690ff86c60bf78ced6308cbfaee1b6b2446b75dfb472738cf2954c66`。
- [ground_controller_v4.py](<../../ground_controller_v4.py>)：SHA `0cb7c6bfc16040d0e3d640cc2a9f4f5153ce61141741c0dcba340e8c5dd5701c`。
- [实际P25控制pack](<../../NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json>)与[冻结profile](<../../NORMAL_P25_HOLDOUT_V1/PROTOCOL.json>)。C使用实际导出的P25 K，不是nominal K；离线DARE重算仅检查来源，没有现场求DARE或调参。
- [state14勘误](<../../reports/STATE14_SCHEMA_ERRATUM.md>)是列语义权威。H2三层源/协议已读并核对SHA，但其反馈阶段没有移植或运行。

唯一旧内核依赖是[封存C2纯FK](<../portable_core_v2_kinematics/ct_kinematics.c>)与[接口](<../portable_core_v2_kinematics/ct_kinematics.h>)。没有调用旧C1 observer。rolling radius、FD epsilon、IMU offset均由调用者明确给入；fixture用几何radius=.06369999796152115、f32 eps=.001，另含.0625数值例，均非实测校准。

## 2. 代码与信号语义

| 文件 | 已实现内容 |
|---|---|
| [pc3_control.h](<pc3_control.h>) | 固定caller-owned状态、packet/estimate/控制/抽象enqueue接口，schema3 |
| [pc3_estimator.c](<pc3_estimator.c>) | V4 quaternion、origin lever correction、wheel-pivot旋转参考、vector gate、Joseph v/b KF、heading unwrap与单次age view |
| [pc3_controller.c](<pc3_controller.c>) | P25实际K、固定腿120/4 PID、yaw PI/FF、jerk/accel、leash、原speed/effort/DC数学与显式row映射 |
| [pc3_dispatch.c](<pc3_dispatch.c>) | 失效锁存、绑定/期限/反馈检查、唯一正常enqueue、callback后再次检查及pending失效 |
| [pc3_p25_data.h](<pc3_p25_data.h>) | 从P25 pack导出的只读K/eq/τ；无全局可变状态 |

输入是已在canonical BODY frame、load-side SI域的IMU/encoder数据。sensor-to-body旋转、sign/zero、reducer、电流/扭矩标定与协议均在未绑定BSP侧；这里不猜DM3519 CAN字节、ID或物理front/rear角色。

state14零基序列：

```text
0 forward-displacement gauge, 1 unwrapped heading, 2 pitch,
3 Lhip, 4 Lcrank−Lhip, 5 Rhip, 6 Rcrank−Rhip,
7 forward body vx, 8 Euler heading rate, 9 Euler pitch rate,
10 Lhipdot, 11 Lcrankdot−Lhipdot, 12 Rhipdot, 13 Rcrankdot−Rhipdot.
```

被动FK knee单独用于轮角速度关系，不写进delta列。输出row6严格为`Lhip,Lcrank,Lwheel,Rhip,Rcrank,Rwheel`；wheel-first数学视图显式取`[row2,row5,row0,row1,row3,row4]`。这不是物理front/rear、bus ID或方向的绑定证明。

## 3. 当前估计数学

1. 接受同一queue epoch的IMU/encoder packet。用BODY gyro/filtered alpha消除IMU杆臂项，FK计算轮心与轮forward速度。
2. 若选择wheel-midpoint参考，在重力候选中补`alpha×pivot + omega×(omega×pivot)`，并保留V4的forward速度传播旋转耦合项。
3. `norm confidence × vector-innovation confidence`共同控制加速度姿态校正。不是旧C1的仅模长门控。normal默认gain1.5、innovation limit1；gyro-only gain0可显式配置，vector gate仍计算。
4. v/b两状态KF保留F/Q、两轮disagreement增R和**Joseph covariance update**；对称化只消除f32反对称舍入，坏/非正协方差不静默修补。
5. quaternion得到roll/pitch/heading；heading rate由body gyro与Euler角变换，绝不把gyro_z直接冒充Euler rate。turns单独int64，state14仍f32。
6. 缓存未经age传播的sample。view仅对state14[0:7]加`age*x[7:14]`一次；重复packet不再积分/KF，额外view不污染缓存。
7. `proxy_vy_no_side_slip_raw = -(raw_omega × raw_FK_midpoint)_y`保持同包原frame，和gyro/proper/roll一样不暗转到present frame。它不是独立侧滑测量；forward gauge也不是世界x。

## 4. 显式arming与严格失效

必须reset后显式选择SUPPORTED_UPRIGHT或STATIC_GRAVITY arming。前者是调用者声明的supported-upright先验，和冻结P25 protocol一致；可处理已声明的首包unsettled finite IMU，包括zero proper norm。后者要求合理非零gravity norm，坏值硬错，不像Python通用类那样在未声明时自动fallback upright。先验不证明真的接触/姿态或任意初始位形资格。

packet finite/flags、sample≤arrival≤now、channel queue-epoch一致、mean count/weight/window、overrun/clipped/driverfault、50ms最大age、100ms最大sample gap、重复payload一致、控制100Hz pacing均检查。无效mean在重复包分支**之前**检查。

- 输出失败全零、valid=0，故障锁存，显式reset/rearm才恢复；不能拿旧good estimate悄悄继续normal enqueue。
- 异常covariance、中间溢出、unwrap模糊、clock倒退、callback后期限/packet-age/drive-age过界同样失效。
- header内数值域包含正innovation_limit、accel correction范围0..1.5与有限body-rate/gap unwrap条件；默认30rad/s是本原型的**数值不混叠假设，不是电机/实板额定值**。
- P25固定dt=.01；重复/倒退或非10ms控制tick硬错。实际BSP jitter/丢tick策略尚未绑定，不用这个软件检查宣称实机100Hz已达成。

## 5. 100Hz packet不是2kHz实机collector

本包**没有window collector**。instant packet或external-mean-window都要求非空/valid count及质量元数据；mean window还要求有效weight sum与aperture一致。代码检查这些声明的内部一致性，不证明上游真的正确采样/时间加权。

queue epoch标签不代表各通道瞬时同步：gyro/accel/rates可能是前窗均值，q是窗末值。额外aperture延迟不会被假装已经包含在D3 age；输出保留aperture/count。两TRAIN fixture的20×0.5ms元数据由已知uniform simulator frontend源码重建，不是原trace逐packet记录的硬件计数，尤其不等于真实CAN encoder 2kHz。异步实机数据需要独立有证据的frontend/BSP方案。

## 6. P25控制与envelope

实际P25 K/τ_eq/eq14均原样导出；保留：legPID120/4，yawPI .8/.5、I限15，rateFF .052、**angular-acceleration FF .08**，accel1.5/yawaccel6/jerk8，position leash1、heading leash.6，fixed-leg state symmetrization、decoupled yaw。

P25默认model prediction=0、roll gains=0、wheel pitch/velocity scales=1；本包只实现此冻结profile，不冒称支持通用Python类的所有非默认选项。command speed envelope保留其原几何radius常量与55.3557 no-load值；这不把外参rolling radius自动校准成了真实值。

原row torque峰值仍`[40,40,5.775909774436091]×2`。signed-DC函数保持[原来源:127–130](<../../../traditional_control_20261101/control_core.py#L127-L130>)的velocity预夹、stall/no-load和方向相关上下界；仅防止f32 endpoint超出原绝对峰值一ULP，不扩大任何界。

**边界分层：**P25返回的是controller torque数学；integrated cycle再作point-in-time DC guard。它不是Python physics bridge内部inverse-PD/processed-target DR/driver-rate current loop的移植，也不证明有限age反馈下每个实际电机瞬间都满足DC。BSP callback还需在实际driver cadence执行原限制。前DC controllerτ与最终guardedτ应分别诊断，不偷换名称。

## 7. single-enqueue gate

典型流程：reset+explicit arm → immutable packet/math → P25 math → original DC point-guard → explicit wheel-first view → deadline/age再检 → **唯一正常enqueue** → callback后clock/age/deadline再检。

shipping binding仍unbound。必须由调用者明确声明全部绑定、提供clock/enqueue/disable-and-invalidate；host测试只用mock，没有真实硬件binding。enqueue必须原子copy并检查deadline，disable必须清除pending旧请求。失败即hard return，无后续normal分支；callback失败/晚到可能已经尝试一次queue，所以通过invalidate清pending，不能把抽象接口当作已经证明可撤销实CAN发送。

## 8. 离线数值证据

- [固定TRAIN输入](<SOURCE_FREEZE.json>)只限R04_202、R11_k20_201各800条；另7组独立synthetic packet共1600条，合计**3200**。仅白名单raw gyro/acc/encoder/time进入估计器；logged estimated14只作离线grading，root/contact truth不进入控制。无新plant/physics/step，也未读取holdout case来选参数。
- [Python64参考](<make_reference_vectors.py>)只import已检查的pure sensor/controller模块，用`-B`防parent pycache写入；MuJoCo/physics_bridge未import。原V4重放两TRAIN的estimated14与原日志**逐项最大差0**。
- 分开冻结Python原FD1e−5、量化pins/外参/K/input后FD=.001的double参考，以及给相同estimate输入的隔离P25参考。没有把这些差别混作控制器物理误差。
- [工程数值budget](<NUMERICAL_BUDGET.json>)在第一次C replay前写定，**0超限**，不是用户ratified的物理验收门槛；没有为过test调整K、sensor gains、caps或原budget。

主要最大绝对差（相对原冻结Python64；其他诊断多为参数匹配参考）：

| 量 | max abs | 单位 |
|---|---:|---|
| forward gauge | 5.33044e−6 | m |
| unwrapped heading | 1.15092e−5 | rad |
| pitch | 1.21608e−7 | rad |
| forward vx | 6.58111e−6 | m/s |
| heading rate | 1.96498e−6 | rad/s |
| Joseph P元素 | 6.90672e−7 | 混合v/b covariance单位 |
| 同包lateral proxy | 1.57193e−6 | m/s |
| 整链controllerτ vs原Python | 2.00777e−4 | Nm |
| 隔离P25τ | 1.96974e−4 | Nm |

隔离controller的最大wheelτ差出现在yaw ramp收尾：f32累计shaper_w误差2.47574e−5rad/s，被原`.08*d(w)/.01`项放大；不是暗改FF或放松原边界。每列/每场景/worst row完整值在[NUMERICAL_COMPARISON.json](<NUMERICAL_COMPARISON.json>)、[C原输出](<C_REPLAY_01.jsonl>)与[130列参考](<REFERENCE_VECTORS.csv>)。

## 9. 构建/失效测试与ARM

strict host C99：`-O2 -Wall -Wextra -Werror -pedantic -Wvla -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse`。新[自测](<pc3_selftest.c>)最终**6509断言/0失败**，含不arming、invalid mean、coherent changed duplicate、一次age view、vector gate、covariance、时间倒退、overrun、signed DC/mapping、unique enqueue与callback后失效；[原日志](<unit_run_03.log>)。host对象大小为estimator704/controller128/packet152bytes，仅此host ABI。

[独立C99 objects + C++11 extern-C smoke](<cpp_run_01.log>)通过。当前三源的新stage ARM compile-only也**6/6成功**：

| 源 | M4/fpv4-sp-d16 hard bytes | M7/fpv5-sp-d16 hard bytes |
|---|---:|---:|
| pc3_estimator | 12616 | 12628 |
| pc3_controller | 10888 | 10852 |
| pc3_dispatch | 4592 | 4620 |

已有MDK Plus5.26/ARM Compiler6.10.1；宏binary32/EVAL_METHOD0/ARMv7E-M/SP hard VFP ABI与fromelf ET_REL属性通过。[全原命令/退出](<BUILD_RECEIPT.json>)、[object SHA/头汇总](<OBJECT_SUMMARY.json>)保留。没有host SSE带到ARM，没有BSP/库链接、BIN、ARM运行、HIL/flash/FPSCR或WCET；旧C2依赖的最终链接仍需后续单独验证。

## 10. 复现/封存

[ERROR_REPORT.md](<ERROR_REPORT.md>)保留首次GCC warning失败源/partial objects/原log与literal-edit mismatch；没有降低-Werror。first numerical reference/replay/grade成功，全部原输出保留。不要覆盖已有stream/log：

```powershell
.\pc3_selftest_host_03.exe
.\pc3_replay_host.exe REFERENCE_VECTORS.csv NEW_C_REPLAY.jsonl
```

[INDEX.json](<INDEX.json>)、[VALIDATION.json](<VALIDATION.json>)、[MANIFEST.json](<MANIFEST.json>)包括当前源/数据/失败/对象SHA与221旧快照不变复核。后续resident stdio adapter或H2 profile应开新目录，不回写本包；它们也不扩大既有PH2冻结结论。
