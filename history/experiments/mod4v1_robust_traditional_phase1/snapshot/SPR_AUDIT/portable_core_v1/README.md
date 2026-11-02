# Portable Core v1 — 可审核 C99 / binary32 初版

## 结果与边界

- [ct_core.h](<ct_core.h>)、[ct_core.c](<ct_core.c>)：纯 C99 `float` 数学/观测/整形/门控，固定调用方存储，无 `malloc/free`、MuJoCo、RL、网络、串口或板卡驱动依赖。
- [主机 C 自测](<ct_selftest.c>)经现有 MinGW GCC 6.3.0 严格编译，**18,152 次断言检查 / 0 失败**；[最终日志](<selftest_attempt_03.log#L1-L4>)中 `sizeof(float)=4`、`FLT_MANT_DIG=24`、`FLT_EVAL_METHOD=0`。最大逐标量绝对差 **7.62939453e−6**。
- 这些是**主机代数与边界单测**，不是18,152个独立机器人场景；没有运行仿真、板卡、SSH、Git或父运行任务，没有生成主板 BIN。主机测试程序只调用数学与mock回调。
- 原 [SPR 审计](<../SPR_DEPLOYMENT_AUDIT.md>)及其索引、选中源码、旧HAL头保持只读；本轮新增与修订全部在本子目录。

## 冻结来源与数学约定

先经read读取 [r00 sensor_core.py:14–32](<../../source_snapshots/r00/sensor_core.py#L14-L32>)、[估计器:98–128](<../../source_snapshots/r00/sensor_core.py#L98-L128>)、[命令整形:130–136](<../../source_snapshots/r00/sensor_core.py#L130-L136>)；冻结版本 **9,607 bytes / SHA256 `df6f462e55f9e670704c0ceaa28c29cd262b53d561886846f2bdaa0f8899e00f`**。实现没有import/exec该文件。

接口复用原 [portable_hal_proposal.h](<../portable_hal_proposal.h>) 的snapshot/command/actuation/receipt/callback类型，不改动它；旧 `mod4_core_*` 声明仍未在本版本实现，本版本入口为 `ct_*`。

- 机体系x前/y左/z上、右手角正向；四元数 `[w,x,y,z]` 为body→world。body角速度指数增量在右侧相乘，RPY依旋转矩阵 `atan2/hypot` 提取。
- `proper_accel_body` 是包含重力对应比力的proper acceleration；静止水平输入约 `[0,0,+9.81]`。杆臂向量方向为参考原点→IMU，三个向量同处body系，`proper_origin=f_imu−alpha×r−omega×(omega×r)`；之后另以 `−G*R[2,:]` 扣重力。
- alpha按冻结式 `dt/(.06+dt)` 低通角加速度差分；轮加速度按 `.12s`、±8m/s²限制；姿态修正和velocity/bias 2×2 KF及Joseph协方差更新对应冻结实现。
- 关节输入顺序 **Lhip,Lcrank,Rhip,Rcrank**；14维输出为 `[distance,yaw,pitch,Lhip,Lknee,Rhip,Rknee,v,yawdot,pitchdot,Lhipdot,Lkneedot,Rhipdot,Rkneedot]`。
- `contact_consistency` 仅是量测一致性代理，不是实际接触/足底力/着陆真值。

## 已实现模块

| 模块 | 入口与行证 | 说明 |
|---|---|---|
| Quaternion/旋转/RPY/安装旋转 | [ct_core.c:32–94](<ct_core.c#L32-L94>) | 范数、有限值、proper旋转矩阵校验；q积分支持输入/输出别名 |
| omega/alpha杆臂 | [ct_core.c:95–102](<ct_core.c#L95-L102>) | proper仍是proper，单独去重力 |
| 连续yaw | [ct_core.c:104–118](<ct_core.c#L104-L118>) | unwrap跨±π；`max_rate*dt<π`门槛；int64圈数+wrapped残差留存多圈信息，避免逐步float累加漂移 |
| 观测核心 | [ct_core.c:148–226](<ct_core.c#L148-L226>) | 64位us相对差转dt；重复包只预测视图，不重复积分；失序/过期/无效锁存错误 |
| HAL到观测 | [ct_core.c:227–246](<ct_core.c#L227-L246>) | 明确四关节索引、IMU旋转；当前严格要求四关节与IMU采样时刻一致 |
| 命令整形 | [ct_core.c:247–270](<ct_core.c#L247-L270>) | 线速度 `j=clip(16e−8a)`、梯形速度积分；yaw双模式见下 |
| 机械功率限幅 | [ct_core.c:271–288](<ct_core.c#L271-L288>) | 六轴输出侧扭矩限幅、正功/回馈功分开预算，不相互抵消 |
| CAN纯守卫 | [ct_core.c:289–296](<ct_core.c#L289-L296>) | 配置bus+ID+DLC精确匹配、仅classic standard data frame、采样/到达/当前时间与年龄检查 |
| fail-closed输出 | [ct_core.c:300–348](<ct_core.c#L300-L348>) | 一进入即清零输出；任一异常直接返回且锁存；正常结果只在所有检查后复制 |
| 单发送者示例 | [ct_core.c:349–375](<ct_core.c#L349-L375>) | 故障先调用gate再硬return；正常enqueue仅唯一末端分支；队列失败清零/锁存/gate |

### 与冻结Python的刻意差异

1. C浮点运算为binary32，Python独立参考为float64；比较按明确容差，不声称逐bit同一ARM结果。
2. 用uint64 us时间戳，避免长运行绝对float32时间损失；更严格地检查当前时间倒退、未来采样、包有效/饱和/overrun、配置与非有限值。异常需显式reset恢复，不自动重新使能。
3. 初始proper范数接近0、非proper安装旋转、unwrap采样率导致多圈歧义都返回错误。初始化倾角仍保留冻结实现的近静止假设，不是动态姿态全域可观性证明。
4. `CT_YAW_ACCEL_ONLY`保留Python原yaw加速度限幅；`CT_YAW_JERK_LIMITED`把同一jerk状态律扩展到yaw，是新增强化。两种都有独立向量。`max_speed/max_yaw_rate`约束**目标值**，不是整车实际速度/姿态包络保证；物理包络仍由上层处理。
5. 连续yaw便利值仍是float32，大绝对角时分辨率有限；需要长运行高精度相位时保留 `ct_yaw.turns` 与 `previous_wrapped` 分量，而不是只存float总角。
6. 延迟视图只外推14维状态前7项，q/roll/gyro保留采样时刻语义，并同时输出sampled/estimated时间；不得把未外推q当成“当前精确姿态”。

## 尚未实现/待绑定

- **闭链运动学前端未移植**。`wheel_forward2`必须由真实编码器/gyro和冻结几何接口对应的运动学得到；接口没有世界root速度或接触truth字段。测试的轮速数值是人工代数fixture，不是物理验证。
- 不含LQR/MPC控制律、全FSM、障碍检测、270mm台阶策略、板上RTOS/BSP/排队硬件实现或完整电功率模型；对应父任务继续实现。
- **DM3519协议未确定，不发3508替代帧**。CAN函数只校验元数据，不decode/encode未知协议；错误Rx不得刷新last-good时间戳。发布测量使用帧私有值/原子快照，不复用共享全局Rx/Tx缓冲。
- gate配置中的已验证bits/status mask/healthy value/输出侧扭矩/timeout由真实绑定提供，函数只检查一致性；这些bits不是硬件自动识别。测试使用的healthy状态7、10ms与4Nm均为fixture，非目标硬件参数。
- `latch_output_gate`必须在真实BSP阻止/清空过期normal队列并落实全轴输出禁止。mock证明的是故障分支没有再次enqueue；它不证明实物已停扭矩。queue accepted/on-bus/applied torque三者仍分开。
- 机械功率按 `Σmax(tau*dq,0)` 与 `Σmax(-tau*dq,0)` 分别限制。**不是电功率**：堵转dq=0仍保留受扭矩限值约束的力矩，I²R/驱动损耗/静态耗电/温度/电池回馈约束需另建模。输出侧扭矩峰值/持续值应由上层选择，不能把该函数当铜损或热保护。

## 单测与复现

[Python向量生成器](<generate_vectors.py>)只依赖stdlib，独立重写所读公式，不执行冻结文件或开源脚本；[向量JSON](<python_vectors.json>)、[C fixture头](<ct_test_vectors.h>)、[来源元数据](<provenance.json>)均已保存。共有16个旋转向量、16个杆臂向量、80个观测包、14个shaper检查点。

[C自测:14–147](<ct_selftest.c#L14-L147>)还覆盖4π rad/s正转2s/反转2s、跨圈、2,000步每方向、六轴逐轴离线/陈旧/Inf、NaN、时间倒退/未来、命令过期、故障锁存、重置、队列/gate失败、别名、安装旋转、bus/ID/DLC/RTR/extended/FD检查和机械功率不净额抵消。

在本子目录使用已有工具复现（只构建/执行host代数测试）：

```powershell
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' .\generate_vectors.py
& 'C:\MinGW\bin\gcc.exe' -std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse ct_core.c ct_selftest.c -lm -o ct_selftest_host.exe
.\ct_selftest_host.exe
```

`-msse2 -mfpmath=sse`只用于本机binary32执行模型，不是ARM编译选项。当前未做ARM ABI/链接、板上WCET、ISR/RTOS并发、台架/HIL/物理技能资格测试。主机EXE不作为任何主板固件交付。

构建/自测错误与所有尝试原文见 [ERROR_REPORT.md](<ERROR_REPORT.md>)；每份源码、fixture、日志、历史失败/通过源版本与当前主机产物的bytes/SHA和入口行号见 [INDEX.json](<INDEX.json>)。仅此子目录被写入。
