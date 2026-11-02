# Portable Core v2 Kinematics — 独立闭链与LQR代数模块

**本包只对应冻结 r00 的闭链运动学和纯线性代数。它不是父任务当前动态 specific-force 估计器V2，也没有把旧 portable_core_v1 冒充当前仿真版本。** v1及父文件均未修改；后续动态估计器待父冻结后另作v3。

## 交付与主机结果

- [ct_kinematics.h](<ct_kinematics.h>) / [ct_kinematics.c](<ct_kinematics.c>)：C99 binary32，闭链FK、有限差分Jacobian、四编码器/轮转速/gyro双轮前向观测，以及6×14 LQR+前馈；无heap、全局可变状态或硬件/仿真/RL依赖。
- [C自测](<ctk_selftest.c>)：**2,761次断言检查 / 0失败**，不是2,761个机器人episode。两次构建及自测均成功，[最终原文](<selftest_attempt_02.log>)完整保留。
- 编译器现有完整路径供父归档：

```text
C:\MinGW\bin\gcc.exe
```

版本 **MinGW.org GCC-6.3.0-1 / 6.3.0**，target=`mingw32`，见[工具链原文](<toolchain_version.log>)。严格C99、`-Wall -Wextra -Werror -pedantic`、禁止fast-math/FMA合并，SSE2执行模型 `sizeof(float)=4 / FLT_MANT_DIG=24 / FLT_EVAL_METHOD=0`。SSE2选项仅用于当前host，不是ARM编译参数。

| 最终对独立float64参考的最大绝对误差（FD eps=1e−3） | 值 |
|---|---:|
| FK轮心位置 | 7.4505806e−8 m |
| 相对膝角 | 3.27825546e−7 rad |
| Jacobian单元素 | 3.09169292e−4（前三行m/rad，末行rad/rad） |
| 轮心相对线速度 | 1.42008066e−5 m/s |
| 相对膝角速度/轮y角速度 | 6.0800463e−5 rad/s |
| 最终前向观测 | 1.8119812e−5 m/s |
| LQR扭矩 | 1.90734863e−6 N·m |

这证明的是指定数学/fixture的C端移植及边界检查，不是闭链实物标定、ARM/WCET、传感器时序、控制稳定性或物理技能资格。

## 来源、单位与半径分离

1. 数学先经read读取 [sensor_core.py:34–59](<../../source_snapshots/r00/sensor_core.py#L34-L59>)，SHA256 `df6f462e55f9e670704c0ceaa28c29cd262b53d561886846f2bdaa0f8899e00f`；没有执行该源码。
2. pins只取指定 [model_manifest.json:120–205](<../../../traditional_control_20261101/reports/model_manifest.json#L120-L205>) 的 `neutral_skeleton_xz_m`，JSON本身223,744 bytes，SHA256 `238b5ef9986b743e0642d2f97217e225179a0050ba7d2269c24d7ffad18e7f5e`。这不是其内部声明的STEP原件SHA，本任务没有打开/复制STEP大件。采用这个指定旧manifest并不自动证明最新模型几何已完成实物复核。
3. K、tau_ff、平衡q取父 [nominal_gain_v1.json:25–140](<../../nominal_gain_v1.json#L25-L140>)；root与r00冻结副本完全同SHA `7c3e1734558ef3d805739c7d154be923c93df4fd52ff89fa22acebef9b107b94`，其kind明确是nominal DARE synthesis而非物理技能结果。
4. track按指定 **0.4376m**；两侧轮心y为±track/2。pins顺序为O/K/P/A/B/C/D/W；只保留[小型输入摘录](<selected_inputs.json>)，没有复制整个模型或A/B矩阵包。
5. **rolling_radius_m是必须传入的外参，核心不选默认半径：** 0.0625m是硬件nominal规格；0.06369999796152115m是当前USD凸包几何circumradius，两者都不是实测有效滚动半径。[原参数说明:13–15](<../../nominal_gain_v1.json#L13-L15>)、[外参接口:24–34](<ct_kinematics.h#L24-L34>)。

## FK、Jacobian与轮速约定

- x前/y左/z上；sagittal x/z二维旋转严格沿r00的 `[[cos,sin],[-sin,cos]]`，不是另换符号的二维惯用矩阵。
- 两次圆交求闭链，分支符号来自neutral pin的有向面积。输出轮心位置、relative knee、rocker/shin delta。O应在chassis原点附近，避免把该算法当成任意偏置支点的几何实现。
- Jacobian为row-major **4×2**，行是x/y/z/relative-knee，列是hip/crank。膝角差分先wrap。轮心相对速度和knee rate均由Jacobian乘两个关节速率得到。[FK与Jac:93–145](<ct_kinematics.c#L93-L145>)。
- 输入四关节顺序 **Lhip,Lcrank,Rhip,Rcrank**，是crank绝对角，而非knee-relative角；均需经BSP完成正负号、零位、输出侧单位转换。[双轮入口:146–158](<ct_kinematics.c#L146-L158>)没有world/root速度、世界pose或接触truth字段。
- 单轮观测严格为：`v_forward = r*(gyro_y + hipdot + kneedot + wheel_spin) − relative_wheel_vx − (gyro×wheel_position)_x`。调用方负责freshness/时间对齐与valid标志；该纯函数不替代上层发送硬门控。
- 无效geometry、非有限数、不可达/近奇异、差分分辨率不足或差分点出域时，结果整体清零、valid=0并返回独立错误码。两侧只在都成功后一起发布，避免“左成功、右失败”留下半包。

### f32有限差分epsilon的实测选择

独立[Python参考](<generate_vectors.py>)用float64、eps=1e−6；与冻结Python原eps=1e−5的最大J差仅6.3283e−10。下表来自52个代数fixture，**不是全构型域最优性证明**：[原始扫描](<selftest_attempt_02.log#L1-L6>)。

| f32 eps(rad) | 最大J元素绝对差 | 最大前向误差(m/s) |
|---:|---:|---:|
| 2e−3 | 1.30832195e−4 | 5.24520874e−6 |
| 1e−3 | 3.09169292e−4 | 1.8119812e−5 |
| 5e−4 | 3.61084938e−4 | 2.2649765e−5 |
| 2e−4 | 1.69479847e−3 | 1.10626221e−4 |
| 1e−4 | 2.84963846e−3 | 1.07049942e−4 |
| 1e−5 | 3.64836454e−2 | 2.0840168e−3 |

初版建议**显式配置1e−3～2e−3**并针对实际工作域扫描；后续可换解析/自动微分导出的Jacobian。不要把Python的1e−5机械搬到f32。接近奇异处，放大eps可能越过可达域，本实现返回 `CTK_FD_STENCIL` 而非吞掉错误。圆交clearance/height初值2e−6m与branch-area初值1e−9m²只是数值域守卫，**不是已批准的机械可运行域或稳定性阈值**。[边界检查:37–92](<ct_kinematics.c#L37-L92>)。

### 纯4π自转与半径错配反例

给定纯yaw `omega=(0,0,±4π)`、关节rates=0，按无平移滚动约束设置 `spin_i=−omega_z*y_i/radius`，两侧计算的前向观测均抵消为0；两种半径分别一致使用时都通过，亦验证叠加0.75m/s的代数约束。[测试:63–81](<ctk_selftest.c#L63-L81>)。

如果编码器spin按0.0625m约束构造，解算却改用0.063699998m，纯4π测试会产生左 **−0.05279064m/s**、右 **+0.05279064m/s** 的虚假前向分量（半径比例差约1.9199967%）。均值恰好抵消也不代表两轮一致性正确，说明这两个radius标签应分开。[独立刚体旋转/错配测试:82–105](<ctk_selftest.c#L82-L105>)。

## 纯6×14 LQR与前馈

[实现:159–189](<ct_kinematics.c#L159-L189>)只计算 `tau=tau_ff−K*(state−reference)`，K按row-major保存；不隐式wrap yaw、不重排执行器、不做模型辨识、求解器或稳定性声明。`schema/rows/columns`、全部K/FF/state/reference/limit及乘积/累加均校验有限值，负限值无效，0限值允许显式关掉该行。错误时扭矩、unclipped诊断与valid整体清零；输出限幅后另有saturation mask。

- state14列顺序按r00：`distance,yaw,pitch,Lhip,Lknee,Rhip,Rknee,v,yawdot,pitchdot,Lhipdot,Lkneedot,Rhipdot,Rkneedot`。平衡reference是文件q的7项接7项零速度。
- 输出保持gain JSON **原6行顺序**。JSON未自带执行器名称，本包不猜测它与v1 wheel-first HAL枚举的映射；交给父显式绑定后再接电机。
- 48个LQR fixture用了100/2/0Nm统一测试上限，**不是实物额定值**；还用独立行列basis测试证明符号/矩阵布局/前馈逻辑。
- 这不是最终控制架构选型，不代表nominal K在跳跃/强扰动/高速自转全域稳定，也不含功率/热限制或真实执行器模型。

## 复现与审计边界

```powershell
# 在本目录；只用已有host工具执行纯数学单测。
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' .\generate_vectors.py
& 'C:\MinGW\bin\gcc.exe' -std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse ct_kinematics.c ctk_selftest.c -lm -o ctk_selftest_host.exe
.\ctk_selftest_host.exe
```

没有新代理、仿真、真实CAN、板卡、SSH、烧录、RL/训练、父文件或Git修改，也没有安装或广扫编译器目录。所有源码/向量/原样日志/历史测试源保留在本目录；[错误与指标修正记录](<ERROR_REPORT.md>)、[索引](<INDEX.json>)、[复核](<VALIDATION.json>)、[主交付哈希](<MANIFEST.json>)单列。旧v1与原SPR审计主交付逐哈希复核未变。下一阶段动态specific-force移植需等待父新冻结版本，再另建v3，而不是回写本包或v1。
