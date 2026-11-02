# Portable Spin H2 v1 — frozen positive4π pure mathematical port

**冻结H2数学已移植；本包只有estimator+H2 math valid/τ，不含完整failsafe dispatcher、BSP或actuator enqueue。** `actuation_qualified`恒0。没有借P25 profile25发送spin，没有移植R27候选或宣称启停/换向物理通过。交付属于postR16/PH3 pending，不扩PH2冻结范围。

## 来源与矩阵

[冻结记录](<SOURCE_FREEZE.json>)核对H2 [PROTOCOL](<../../SPIN_H2_K20_V1/PROTOCOL.json>)的12项源/metadata以及430份旧文件。固定TRAIN只取R11_k20_201的raw/time/request/estimated14/center_log；H2 heldout case与R27没有用于选择参数。

代码依照[spin_base](<../../spin_base_v1.py>)、[relative center](<../../spin_center_controller_v1.py>)与[torque center](<../../spin_center_torque_v2.py>)。新[只读nominal数据](<sh2_nominal_data.h>)来自[nominal gain](<../../nominal_gain_v1.json>)，不是P25。其K与P25最大元素差**8.84893522683**；离线DARE重算核对nominal K，运行时不求DARE。

固定profile：nominal K，position leash **.2**（不是P25的1），heading leash.6，legPID120/4，yawPI .8/.5/I15，rateFF .052、angular-acceleration FF .08，shaping accel1.5/yawaccel6/jerk8，原speed/effort envelope。lead=.008390087918603841、center kp20/cap1.8。

输出row6是`Lhip,Lcrank,Lwheel,Rhip,Rcrank,Rwheel`；wheel-first数学视图显式`[2,5,0,1,3,4]`，不是物理bus/front-rear/sign/gear绑定。state14依据[勘误](<../../reports/STATE14_SCHEMA_ERRATUM.md>)，delta列是crank−hip及其rate，非passive FK knee。

## 实现与边界

- [sh2_control.h](<sh2_control.h>)：固定caller-owned状态/输出、C99/C++接口，数学valid与actuation资格分离。
- [sh2_controller.c](<sh2_controller.c>)：nominal base +relative planar odom +target/lead +bounded common-wheel torque。
- [sh2_pipeline.c](<sh2_pipeline.c>)：只调用封存[C3 estimator](<../portable_control_v3_current/pc3_estimator.c>)和[C2 FK](<../portable_core_v2_kinematics/ct_kinematics.c>)。没有链接P25 controller/dispatcher。

C3配置为gyro-only **attitude** gain0、wheel-midpoint reference、显式supported-upright prior；acceleration仍进入forward v/b KF，不是所有accel数据都被忽略。先验不证明任意未知初始姿态已估计。radius、FD epsilon与IMU offset外参，fixture用chart radius=.06369999796152115/eps=.001；不是实测rolling calibration。

冻结数学：

```text
vy_proxy = -(omega_held × FK_midpoint_from_age_view_leg_angles)_y
relative_xy += dt * Rot(heading_view) * [estimated_vx, vy_proxy]
pivot_relative_xy = relative_xy + Rot(heading_view) * body_midpoint_xy
active = abs(operator_yaw)>4 AND abs(operator_forward)<.1
active rising edge -> capture target pivot
projection = (pivot_xy-target) dot direction(heading_view+heading_rate*lead)
requested common correction = clip(-20*projection, -1.8, +1.8)
```

先执行原nominal base，保留yaw differential，再按剩余wheel torque headroom夹common。torque_v2明确把velocity-center cap设0，所以`velocity_centering_m_s=0`，不是偷偷给joystick加速度修正。stop后target保留，下一active rising edge重捕；直接正反切换但active一直true时保留同target，完全遵循原源而非新增恢复策略。

**时间语义原样披露：**旧H2 center用age-view hip/crank做FK，配held sample gyro；C3原proxy用raw-epoch FK。两者在本向量集最多差**.0116329789m/s**，不是同一个量。本包忠实保留冻结H2近似，未把C3 raw proxy悄换进来；这也不宣称各通道瞬时同步。

relative XY是初始heading gauge下的估计，不是世界位置传感器。vy依赖no-side-slip，未知共模侧滑仍未独立观测。FK几何/bodygyro或两轮一致不证明无滑移/真实接触。

## 失效与未交付部分

finite/初始化/alias/age/stamp/精确100Hz tick/FK/几何一致检查；pipeline还要求明确gyro-only+wheel-midpoint+supported-upright模式。fault输出全零/valid0并锁存，需要显式reset/rearm。C3的coherent packet/invalid mean/overrun/age保护保持原样，gain0不绕过这些检查。

每row绝对峰值仍原`[40,40,5.775909774436091]×2`的f32表示，center请求≤1.8，yaw differential余量保留；f32 endpoint最终夹回原峰值，不扩界。**此处τ是前driver/DC的数学请求。** 下游原signed-DC/driver-rate/power/thermal限制仍必需，本包没有把未知DM3519/CAN或P25 guard借来充作H2部署。完整failsafe dispatch和H2 stdio闭环adapter均DEFERRED。

## 数值证据

[预算](<NUMERICAL_BUDGET.json>)在第一次C结果前写定，未据结果修改gain/lead/cap或预算。

1. [纯Python64原源重放](<reference_01.log>)对固定R11的logged estimated14、raw_requested_tau与center_log，三项逐点最大差均**0**。使用日志request，不猜1s浮点触发边界。
2. 5400数据点：TRAIN800 +synthetic start/stop/reverse2600、direct-reverse1200、threshold400、age-view400。仅数学数值向量，不创建/step plant；合成启停/反向不扩大正4π物理资格。
3. [C replay](<replay_run_01.log>)全部pipeline/isolated statusOK；[比较](<NUMERICAL_COMPARISON.json>)预定budget零超限、active/target flags零差。

| 量 | 最大绝对差 | reference |
|---|---:|---|
| heading | 1.06266e−5rad | 原冻结Python64 |
| final mathτ | 2.07521e−4Nm | 原冻结Python64 |
| isolated H2τ | 2.02467e−4Nm | 相同estimate/量化参数double |
| relative XY | 2.39759e−6m | 量化参数double |
| pivot-relative XY | 2.33870e−6m | 量化参数double |
| vy proxy | 1.61209e−6m/s | 量化参数double |
| center requestedτ | 4.34629e−5Nm | 量化参数double |
| isolated centerτ | 7.18640e−6Nm | 相同estimate/量化参数double |

原Python FD1e−5与C2 f32 FD=.001、pins/input/K参数量化、纯f32算术分开标注。全部原[127列参考](<REFERENCE_H2.csv>)/[C输出](<C_H2_REPLAY_01.jsonl>)保留，非只存成功末点。yaw differential最大舍入差2.38419e−7Nm。

**range边界：**本集max forward gauge仅.53385m、relative XY norm .16621m、heading75.398rad，synthetic最长26s。不覆盖20m绝对gauge/长期ref累计精度；f32积分/大gauge相减精度风险仍需独立专项，不回写sealed C3来猜因或调参。

## 构建/对象

[新unit](<sh2_selftest.c>)**5418检查/0失败**，覆盖target激活/保持/stop/直接换向、leash.2/nomK、center cap/差动headroom、invalid mean/overrun/错误gain、finite/age/alias/fault、actuation_qualified0。[C++ extern-C](<cpp_run_01.log>)通过。

strict host C99/Wall/Wextra/Werror/pedantic/Wvla/no-fast-math，核心无heap/VLA/可变全局状态。[defined-symbol证据](<host_defined_symbols_01.log>)有sh2和pc3_estimator，没有pc3_p25/pc3_cycle，实际未链接旧P25控制器/dispatcher。

已有armclang6.10.1的新stage M4/M7 SP hard compile-only **4/4对象**成功；[命令/原log引用](<BUILD_RECEIPT.json>)和[对象SHA/ELF/宏](<OBJECT_SUMMARY.json>)保留：controller M4/M7=11536/11508bytes，pipeline=2616/2620bytes。对象长度不是linked flash/stack需求。无BSP/库链接、BIN、板、ARM runtime、FPU配置或WCET结论。

[ERROR_REPORT](<ERROR_REPORT.md>)、[INDEX](<INDEX.json>)、[VALIDATION](<VALIDATION.json>)、[MANIFEST](<MANIFEST.json>)保留尝试源/原始数据/旧430文件不变复核。所有交付只在新目录；physical start/stop/reverse、unknown-slip、dispatch、真实部署仍pending。
